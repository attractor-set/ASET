#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import builtins
import hashlib
import itertools
import json
from pathlib import Path
from typing import Any, Callable


class ExpressionAirgapError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ExpressionAirgapError(message)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def witness_payload_digest(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def _assert_verifier_import_airgap() -> None:
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module is not None:
            imported.add(node.module)
    require(
        not any(
            name.startswith("tools") or name.startswith("alpha4_") for name in imported
        ),
        "air-gap verifier imports repository verification or expression tooling",
    )


def load_witness_artifact(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "proof witness artifact must be an object")
    require(
        value.get("document_type") == "aset-proof-derived-recognition-witnesses",
        "unexpected proof witness document type",
    )
    require(value.get("status") == "PASS", "proof witness artifact is not admitted")
    require(
        value.get("semantic_source_dependency") == "NONE",
        "proof witness artifact depends on Seed semantic source",
    )
    boundary = value.get("materialization_boundary")
    require(isinstance(boundary, dict), "proof witness boundary missing")
    require(
        boundary.get("reads_seed_semantic_source") is False,
        "proof witness materializer read Seed semantic source",
    )
    require(
        boundary.get("reads_expression_derivers") is False,
        "proof witness materializer read expression derivation tooling",
    )
    transitions = value.get("transitions")
    observables = value.get("observables")
    require(isinstance(transitions, list), "proof witness transitions missing")
    require(len(transitions) == 6, "proof witness transition cardinality drifted")
    require(isinstance(observables, dict), "proof witness observables missing")
    require(
        set(observables) == {"UNKNOWN", "ALLOW", "BLOCK"},
        "proof witness observable alphabet drifted",
    )
    return value


def _validate_expression_ast(source: str) -> None:
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            raise ExpressionAirgapError("air-gap expression imports runtime dependency")
        if isinstance(node, ast.ImportFrom):
            require(
                node.module == "__future__"
                and all(alias.name == "annotations" for alias in node.names),
                f"air-gap expression import forbidden: {node.module}",
            )
        if isinstance(node, ast.Name) and node.id == "__builtins__":
            raise ExpressionAirgapError("air-gap expression accesses __builtins__")
        if isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            raise ExpressionAirgapError(
                f"air-gap expression private attribute forbidden: {node.attr}"
            )
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in {
                "__import__",
                "breakpoint",
                "compile",
                "delattr",
                "dir",
                "eval",
                "exec",
                "getattr",
                "globals",
                "help",
                "input",
                "locals",
                "open",
                "setattr",
                "type",
                "vars",
            }:
                raise ExpressionAirgapError(
                    f"air-gap expression dynamic capability forbidden: {node.func.id}"
                )
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            require(
                node.func.attr
                not in {
                    "open",
                    "read_text",
                    "read_bytes",
                    "write_text",
                    "write_bytes",
                    "unlink",
                    "rename",
                    "replace",
                    "mkdir",
                    "touch",
                },
                f"air-gap expression filesystem capability forbidden: {node.func.attr}",
            )
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            lowered = node.value.lower()
            require(
                not any(
                    marker in lowered
                    for marker in ("tools.", "tools/", ".tla", ".forth", ".petri")
                ),
                "air-gap expression embeds repository semantic-source locator",
            )


def _execute_python(path: Path) -> dict[str, Any]:
    source = path.read_text(encoding="utf-8")
    require(
        "release companion" in source, "generated Python companion boundary missing"
    )
    _validate_expression_ast(source)

    def denied(*args: object, **kwargs: object) -> object:
        raise ExpressionAirgapError(
            "air-gap expression attempted forbidden runtime capability"
        )

    original_import = builtins.__import__

    def guarded_import(
        name: str,
        globals: dict[str, Any] | None = None,
        locals: dict[str, Any] | None = None,
        fromlist: tuple[str, ...] = (),
        level: int = 0,
    ) -> Any:
        if name != "__future__":
            raise ImportError(f"air-gap expression import forbidden: {name}")
        return original_import(name, globals, locals, fromlist, level)

    safe_builtins = dict(vars(builtins))
    safe_builtins["__import__"] = guarded_import
    for name in (
        "breakpoint",
        "compile",
        "delattr",
        "dir",
        "eval",
        "exec",
        "getattr",
        "globals",
        "help",
        "input",
        "locals",
        "open",
        "setattr",
        "type",
        "vars",
    ):
        safe_builtins[name] = denied
    namespace: dict[str, Any] = {
        "__name__": "aset_seed_alpha4_airgap_subject",
        "__file__": str(path),
        "__builtins__": safe_builtins,
    }
    exec(compile(source, str(path), "exec"), namespace)
    return namespace


def _observe(call: Callable[[], dict[str, Any]]) -> tuple[str, Any]:
    try:
        return ("ok", call())
    except (KeyError, TypeError, ValueError):
        return ("error", None)


def _witness_variants(
    current: dict[str, Any], evidence: str | None, outcome: str
) -> list[frozenset[tuple[str, str, str, str]]]:
    if evidence is None:
        return [frozenset()]
    subject = str(current["subject"])
    authority = str(current["authority"])
    other_subject = "subject-2" if subject == "subject-1" else "subject-1"
    other_authority = "authority-2" if authority == "authority-1" else "authority-1"
    other_evidence = "evidence-2" if evidence == "evidence-1" else "evidence-1"
    other_outcome = "BLOCK" if outcome == "ALLOW" else "ALLOW"
    return [
        frozenset(),
        frozenset({(authority, subject, evidence, outcome)}),
        frozenset({(authority, other_subject, evidence, outcome)}),
        frozenset({(other_authority, subject, evidence, outcome)}),
        frozenset({(authority, subject, other_evidence, outcome)}),
        frozenset({(authority, subject, evidence, other_outcome)}),
    ]


def check_python_expression(
    expression_path: Path,
    witnesses: dict[str, Any],
) -> dict[str, Any]:
    _assert_verifier_import_airgap()
    namespace = _execute_python(expression_path)
    apply_component = namespace.get("apply_component")
    graphs = namespace.get("GRAPHS")
    require(callable(apply_component), "generated Python apply_component missing")
    require(isinstance(graphs, dict), "generated Python graph table missing")

    transitions = witnesses["transitions"]
    expected_components = {str(item["component_id"]) for item in transitions}
    require(
        set(graphs) == expected_components,
        "expression component surface differs from proof witnesses",
    )

    observables = witnesses["observables"]
    subjects = ("subject-1", "subject-2")
    authorities = ("authority-1", "authority-2")
    recognition_values = tuple(sorted(observables))
    evidence_values = ("evidence-1", "evidence-2")
    evidence_sets = (
        (),
        ("evidence-1",),
        ("evidence-2",),
        ("evidence-1", "evidence-2"),
    )
    evidence_arguments: tuple[str | None, ...] = (None, *evidence_values)

    cases = 0
    successful_realizations: dict[str, set[tuple[str, str]]] = {
        component_id: set() for component_id in expected_components
    }
    for transition in transitions:
        component_id = str(transition["component_id"])
        expected_input = str(transition["input_expression"])
        expected_output = str(transition["output_expression"])
        is_recognition_transition = component_id in {
            "ASET-COMPONENT-RECOGNIZE-ALLOW",
            "ASET-COMPONENT-RECOGNIZE-BLOCK",
        }
        for subject, authority, recognition, observed, evidence in itertools.product(
            subjects,
            authorities,
            recognition_values,
            evidence_sets,
            evidence_arguments,
        ):
            current = {
                "subject": subject,
                "authority": authority,
                "recognition": recognition,
                "evidence": tuple(observed),
            }
            variants = (
                _witness_variants(current, evidence, expected_output)
                if is_recognition_transition
                else [frozenset()]
            )
            for authority_recognition in variants:
                result = _observe(
                    lambda c=current, cid=component_id, ev=evidence, ar=authority_recognition: (
                        apply_component(
                            c,
                            cid,
                            evidence=ev,
                            authority_recognition=ar,
                        )
                    )
                )
                if result[0] == "ok":
                    require(
                        recognition == expected_input,
                        f"{component_id}: expression accepted non-admissible recognition input",
                    )
                    returned = result[1]
                    require(
                        isinstance(returned, dict),
                        f"{component_id}: invalid result type",
                    )
                    output = str(returned.get("recognition"))
                    require(
                        output == expected_output,
                        f"{component_id}: recognition result violates proof witness",
                    )
                    expected_observable = observables[expected_output]
                    actual_observable = {
                        "terminal": output in {"ALLOW", "BLOCK"},
                        "effect_permitted": output == "ALLOW",
                    }
                    require(
                        actual_observable == expected_observable,
                        f"{component_id}: observable projection violates minimality witness",
                    )
                    successful_realizations[component_id].add((subject, authority))
                cases += 1

    required_contexts = set(itertools.product(subjects, authorities))
    for component_id, realized in successful_realizations.items():
        require(
            realized == required_contexts,
            f"{component_id}: theory transition is not realizable in every bounded context",
        )

    require(cases == 1824, f"unexpected bounded proof-witness case count: {cases}")
    return {
        "relation": "PROOF_DERIVED_BOUNDED_OBSERVATIONAL_ASSURANCE",
        "assurance_basis": witnesses["assurance_basis"],
        "witness_payload_digest": witness_payload_digest(witnesses),
        "cases_checked": cases,
        "components_checked": len(expected_components),
        "semantic_source_dependency": "NONE",
        "proof_materializer_runtime_dependency": "NONE",
        "expression_deriver_dependency": "NONE",
        "expression_import_surface": "NONE",
        "expression_file_access": "NONE",
        "status": "PASS",
    }


def check_airgapped_expression(
    witness_path: Path,
    expression_path: Path,
) -> dict[str, Any]:
    witnesses = load_witness_artifact(witness_path)
    python = check_python_expression(expression_path, witnesses)
    return {
        "document_type": "aset-airgapped-expression-assurance-evidence",
        "assurance_boundary": "MATERIALIZED_PROOF_WITNESSES_VS_BLACK_BOX_EXPRESSION",
        "verifier_inputs": {
            "proof_witness_artifact": {
                "artifact_name": witness_path.name,
                "sha256": sha256(witness_path),
                "payload_digest": witness_payload_digest(witnesses),
            },
            "expression_artifact": {
                "artifact_name": expression_path.name,
                "sha256": sha256(expression_path),
            },
        },
        "runtime_dependencies": {
            "semantic_source": "NONE",
            "proof_materializer": "NONE",
            "expression_deriver": "NONE",
            "expression_import_surface": "NONE",
            "expression_file_access": "NONE",
        },
        "python": python,
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--witnesses", type=Path, required=True)
    parser.add_argument("--expression", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        evidence = check_airgapped_expression(args.witnesses, args.expression)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        cases = evidence["python"]["cases_checked"]
        print(f"ALPHA4_AIRGAP_EXPRESSION_CASES={cases}/{cases} PASS")
        print("ALPHA4_AIRGAP_SEMANTIC_SOURCE_DEPENDENCY=NONE")
        print("ALPHA4_AIRGAP_PROOF_MATERIALIZER_RUNTIME_DEPENDENCY=NONE")
        print("ALPHA4_AIRGAP_EXPRESSION_DERIVER_DEPENDENCY=NONE")
        print("ALPHA4_EXPRESSION_AIRGAP=PASS")
        return 0
    except (
        ExpressionAirgapError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        TypeError,
        UnicodeError,
        ValueError,
    ) as error:
        print(f"ALPHA4_EXPRESSION_AIRGAP_ERROR={error}")
        print("ALPHA4_EXPRESSION_AIRGAP=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

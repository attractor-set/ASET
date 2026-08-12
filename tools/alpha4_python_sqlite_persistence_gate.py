#!/usr/bin/env python3
from __future__ import annotations

import argparse
import ast
import hashlib
import importlib.util
import itertools
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable


class PythonSQLitePersistenceError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PythonSQLitePersistenceError(message)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def require_no_bytecode(root: Path) -> None:
    bytecode = [
        path
        for path in root.rglob("*")
        if path.name == "__pycache__" or path.suffix == ".pyc"
    ]
    require(not bytecode, "materialized profile tree contains Python bytecode")


def load_binding(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "persistence binding must be an object")
    require(
        value.get("document_type") == "aset-python-persistence-extension-binding",
        "unexpected persistence binding document type",
    )
    require(value.get("relation") == "PERSISTENCE_EXTENSION", "relation drifted")
    require(value.get("semantic_delta") == "NONE", "semantic delta must be NONE")
    require(
        value.get("semantic_precedence") == "NONE",
        "persistence extension cannot acquire semantic precedence",
    )
    base_expression = value.get("base_expression")
    extension = value.get("extension")
    require(isinstance(base_expression, dict), "base expression binding missing")
    require(isinstance(extension, dict), "extension binding missing")
    require(
        base_expression.get("profile") == "python",
        "base expression must be Python",
    )
    require(
        extension.get("profile") == "python-sqlite",
        "extension profile must be python-sqlite",
    )
    return value


def _literal_strings(tree: ast.AST) -> set[str]:
    return {
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    }


def check_source_boundary(path: Path, base_expression_sha256: str) -> None:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source)
    strings = _literal_strings(tree)
    require(
        not ({"UNKNOWN", "ALLOW", "BLOCK"} & strings),
        "persistence extension encodes recognition values",
    )
    require(
        not any(value.startswith("ASET-COMPONENT-") for value in strings),
        "persistence extension encodes Seed component identity",
    )
    assigned_names = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, (ast.Assign, ast.AnnAssign))
        for target in (node.targets if isinstance(node, ast.Assign) else [node.target])
        if isinstance(target, ast.Name)
    }
    require("GRAPHS" not in assigned_names, "persistence extension defines semantics")
    require(
        "_base_expression.apply_component" in source,
        "persistence extension does not delegate transition semantics to base expression",
    )
    require(
        f"BASE_EXPRESSION_SHA256 = {base_expression_sha256!r}" in source,
        "extension source does not bind exact base expression bytes",
    )


def execute_python(path: Path) -> dict[str, Any]:
    namespace: dict[str, Any] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
    return namespace


def execute_extension(path: Path) -> dict[str, Any]:
    spec = importlib.util.spec_from_file_location("aset_seed_alpha4_sqlite", path)
    require(spec is not None and spec.loader is not None, "extension cannot be loaded")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return vars(module)


def observe(call: Callable[[], dict[str, Any]]) -> tuple[str, Any]:
    try:
        return ("ok", call())
    except (KeyError, TypeError, ValueError):
        return ("error", None)


def witness_variants(
    current: dict[str, Any],
    evidence: str | None,
    outcome: str,
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


def check_base_expression_congruence(
    base_expression_path: Path,
    extension_path: Path,
) -> dict[str, Any]:
    base_expression = execute_python(base_expression_path)
    extension = execute_extension(extension_path)
    apply_component = base_expression.get("apply_component")
    graphs = base_expression.get("GRAPHS")
    store_type = extension.get("SQLiteStore")
    require(callable(apply_component), "base expression apply_component missing")
    require(isinstance(graphs, dict), "base expression graph table missing")
    require(callable(store_type), "SQLiteStore missing")

    outcomes = {
        component_id: next(
            (str(node["value"]) for node in nodes if node["op"] == "SET_RECOGNITION"),
            None,
        )
        for component_id, nodes in graphs.items()
    }
    subjects = ("subject-1", "subject-2")
    authorities = ("authority-1", "authority-2")
    recognition_values = ("UNKNOWN", "ALLOW", "BLOCK")
    evidence_values = ("evidence-1", "evidence-2")
    evidence_sets = (
        (),
        ("evidence-1",),
        ("evidence-2",),
        ("evidence-1", "evidence-2"),
    )
    evidence_arguments: tuple[str | None, ...] = (None, *evidence_values)

    cases = 0
    rollback_checks = 0
    restart_checks = 0
    restart_seen: set[str] = set()
    with tempfile.TemporaryDirectory(prefix="aset-python-sqlite-") as temp:
        database = Path(temp) / "seed.sqlite3"
        store = store_type(database)
        for component_id in sorted(graphs):
            outcome = outcomes[component_id]
            for (
                subject,
                authority,
                recognition,
                observed,
                evidence,
            ) in itertools.product(
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
                    witness_variants(current, evidence, outcome)
                    if outcome is not None
                    else [frozenset()]
                )
                for authority_recognition in variants:
                    store.initialize(current)
                    before = store.load()
                    expected = observe(
                        lambda c=current, cid=component_id, ev=evidence, ar=authority_recognition: (
                            apply_component(
                                c,
                                cid,
                                evidence=ev,
                                authority_recognition=ar,
                            )
                        )
                    )
                    actual = observe(
                        lambda cid=component_id, ev=evidence, ar=authority_recognition: (
                            store.apply_component(
                                cid,
                                evidence=ev,
                                authority_recognition=ar,
                            )
                        )
                    )
                    require(
                        actual == expected,
                        "SQLite extension differs from base expression",
                    )
                    if actual[0] == "ok":
                        if component_id not in restart_seen:
                            reopened = store_type(database)
                            require(
                                reopened.load() == actual[1],
                                "committed state did not survive restart",
                            )
                            restart_seen.add(component_id)
                            restart_checks += 1
                    else:
                        require(
                            store_type(database).load() == before,
                            "base expression rejection changed persistent state",
                        )
                        rollback_checks += 1
                    cases += 1

    require(cases == 1824, f"unexpected base expression congruence case count: {cases}")
    require(restart_checks == 6, "restart coverage must include all components")
    require(rollback_checks > 0, "rollback path was not exercised")
    return {
        "relation": "PERSISTENCE_EXTENSION_OF_EXACT_PYTHON_EXPRESSION",
        "base_expression_congruence_cases": cases,
        "restart_round_trip_components": restart_checks,
        "rollback_checks": rollback_checks,
        "semantic_delta": "NONE",
        "status": "PASS",
    }


def check_python_sqlite_persistence(profiles_root: Path) -> dict[str, Any]:
    require_no_bytecode(profiles_root)
    before_digest = tree_digest(profiles_root)
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    binding_path = profiles_root / "python-sqlite/PERSISTENCE_EXTENSION.json"
    try:
        binding = load_binding(binding_path)
        base_expression_path = profiles_root / str(binding["base_expression"]["path"])
        extension_path = profiles_root / str(binding["extension"]["path"])
        require(
            base_expression_path.is_file(),
            "bound base Python expression missing",
        )
        require(extension_path.is_file(), "Python SQLite extension missing")
        base_expression_digest = sha256(base_expression_path)
        extension_digest = sha256(extension_path)
        require(
            base_expression_digest == binding["base_expression"]["sha256"],
            "bound base Python expression bytes differ",
        )
        require(
            extension_digest == binding["extension"]["sha256"],
            "bound Python SQLite bytes differ",
        )
        check_source_boundary(extension_path, base_expression_digest)
        runtime = check_base_expression_congruence(base_expression_path, extension_path)
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode
    require_no_bytecode(profiles_root)
    after_digest = tree_digest(profiles_root)
    require(
        before_digest == after_digest, "persistence gate mutated materialized profiles"
    )
    return {
        "document_type": "aset-python-sqlite-persistence-assurance-evidence",
        "project": "Authority-Seeded Evidence Trail (ASET)",
        "relation": "PERSISTENCE_EXTENSION",
        "semantic_delta": "NONE",
        "base_expression_binding": {
            "path": str(binding["base_expression"]["path"]),
            "sha256": base_expression_digest,
        },
        "extension_binding": {
            "path": str(binding["extension"]["path"]),
            "sha256": extension_digest,
        },
        "runtime": runtime,
        "materialization_boundary": {
            "profile_tree_digest_before": before_digest,
            "profile_tree_digest_after": after_digest,
            "profile_tree_unchanged": True,
            "python_bytecode_written": False,
        },
        "not_claimed": binding["not_claimed"],
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        evidence = check_python_sqlite_persistence(args.profiles_root)
        if args.output is not None:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(evidence, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
        runtime = evidence["runtime"]
        cases = runtime["base_expression_congruence_cases"]
        restarts = runtime["restart_round_trip_components"]
        rollbacks = runtime["rollback_checks"]
        print(f"ALPHA4_PYTHON_SQLITE_BASE_EXPRESSION_CONGRUENCE={cases}/{cases} PASS")
        print(f"ALPHA4_PYTHON_SQLITE_RESTART_ROUND_TRIP={restarts}/6 PASS")
        print(f"ALPHA4_PYTHON_SQLITE_ROLLBACK_CHECKS={rollbacks} PASS")
        print("ALPHA4_PYTHON_SQLITE_SEMANTIC_DELTA=NONE")
        print("ALPHA4_PYTHON_SQLITE_PROFILE_TREE_UNCHANGED=PASS")
        print("ALPHA4_PYTHON_SQLITE_PERSISTENCE_EXTENSION=PASS")
        return 0
    except (
        ImportError,
        json.JSONDecodeError,
        KeyError,
        OSError,
        PythonSQLitePersistenceError,
        RuntimeError,
        TypeError,
        UnicodeError,
        ValueError,
    ) as error:
        print(f"ALPHA4_PYTHON_SQLITE_PERSISTENCE_ERROR={error}")
        print("ALPHA4_PYTHON_SQLITE_PERSISTENCE_EXTENSION=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

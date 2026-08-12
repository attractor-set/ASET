#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FOUNDATION = Path("theory/local-recognition/formal/RecognitionCardinality.tla")
PROOF = Path("theory/local-recognition/formal/RecognitionCardinalityProofs.tla")
ALGEBRA = Path("theory/local-recognition/formal/LocalRecognitionAlgebra.tla")
FINAL_THEOREM = "ThreeRecognitionValuesAreCardinalityMinimal"
TRANSITION_PREFIX = "Theory"


class ProofWitnessError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ProofWitnessError(message)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _quoted_values(text: str, operator: str) -> tuple[str, ...]:
    match = re.search(rf"(?m)^{re.escape(operator)}\s*==\s*\{{([^}}]+)\}}$", text)
    require(match is not None, f"missing finite set definition: {operator}")
    return tuple(re.findall(r'"([^"]+)"', match.group(1)))


def _quoted_value(text: str, operator: str) -> str:
    match = re.search(rf'(?m)^{re.escape(operator)}\s*==\s*"([^"]+)"$', text)
    require(match is not None, f"missing scalar definition: {operator}")
    return match.group(1)


def _body(text: str, operator: str) -> str:
    match = re.search(
        rf"(?ms)^{re.escape(operator)}\(r, r2\)\s*==\s*\n(.*?)(?=\n\n|\nTheoryStep)",
        text,
    )
    require(match is not None, f"missing theory relation: {operator}")
    return match.group(1)


def _camel_words(value: str) -> list[str]:
    return re.findall(r"[A-Z]+(?=[A-Z][a-z]|$)|[A-Z]?[a-z]+|[0-9]+", value)


def _expression_component(theory_operator: str) -> str:
    require(
        theory_operator.startswith(TRANSITION_PREFIX),
        "invalid theory operator prefix",
    )
    suffix = theory_operator[len(TRANSITION_PREFIX) :]
    words = _camel_words(suffix)
    require(words, f"cannot derive expression component id: {theory_operator}")
    return "ASET-COMPONENT-" + "-".join(word.upper() for word in words)


def _expression_name(theory_name: str) -> str:
    require(theory_name.startswith(TRANSITION_PREFIX), "invalid theory name prefix")
    suffix = theory_name[len(TRANSITION_PREFIX) :]
    require(
        suffix in {"Unknown", "Allow", "Block"},
        f"unsupported theory state: {theory_name}",
    )
    return suffix.upper()


def materialize_witnesses(root: Path = ROOT) -> dict[str, Any]:
    foundation_path = root / FOUNDATION
    proof_path = root / PROOF
    algebra_path = root / ALGEBRA
    for path in (foundation_path, proof_path, algebra_path):
        require(
            path.is_file(),
            f"required theory file absent: {path.relative_to(root)}",
        )

    foundation = foundation_path.read_text(encoding="utf-8")
    proof = proof_path.read_text(encoding="utf-8")
    algebra = algebra_path.read_text(encoding="utf-8")

    states = _quoted_values(foundation, "RecognitionStates")
    require(states == ("U", "A", "B"), "recognition foundation state set drifted")
    require(
        f"THEOREM {FINAL_THEOREM} ==" in proof,
        "minimality final theorem declaration absent",
    )
    require(
        "NoFaithfulTwoValueEncoding" in proof,
        "two-value impossibility proof absent",
    )
    require(
        "CanonicalThreeEncodingIsFaithful" in proof,
        "three-value witness proof absent",
    )

    theory_states = {
        "TheoryUnknown": _quoted_value(algebra, "TheoryUnknown"),
        "TheoryAllow": _quoted_value(algebra, "TheoryAllow"),
        "TheoryBlock": _quoted_value(algebra, "TheoryBlock"),
    }
    require(
        tuple(theory_states.values()) == states,
        "algebra state coding differs from foundation",
    )

    terminal_match = re.search(
        r"(?m)^Terminal\(s\)\s*==\s*s\s*\\in\s*\{([^}]+)\}$",
        foundation,
    )
    require(terminal_match is not None, "Terminal observable definition absent")
    terminal_states = set(re.findall(r'"([^"]+)"', terminal_match.group(1)))
    effect_match = re.search(
        r'(?m)^EffectPermitted\(s\)\s*==\s*s\s*=\s*"([^"]+)"$',
        foundation,
    )
    require(effect_match is not None, "EffectPermitted observable definition absent")
    effect_state = effect_match.group(1)

    recognition_rows = []
    abstract_to_expression: dict[str, str] = {}
    for theory_name, abstract in theory_states.items():
        expression = _expression_name(theory_name)
        abstract_to_expression[abstract] = expression
        recognition_rows.append(
            {
                "abstract": abstract,
                "expression": expression,
                "terminal": abstract in terminal_states,
                "effect_permitted": abstract == effect_state,
            }
        )

    relation_names = (
        "TheoryObserveUnknown",
        "TheoryRecognizeAllow",
        "TheoryRecognizeBlock",
        "TheoryPreserveUnknown",
        "TheoryPreserveAllow",
        "TheoryPreserveBlock",
    )
    transitions = []
    for operator in relation_names:
        body = _body(algebra, operator)
        source_match = re.search(r"/\\ r = (Theory(?:Unknown|Allow|Block))", body)
        target_match = re.search(r"/\\ r2 = (Theory(?:Unknown|Allow|Block))", body)
        require(
            source_match is not None and target_match is not None,
            f"relation shape drifted: {operator}",
        )
        source = theory_states[source_match.group(1)]
        target = theory_states[target_match.group(1)]
        transitions.append(
            {
                "theory_operator": operator,
                "component_id": _expression_component(operator),
                "input_abstract": source,
                "output_abstract": target,
                "input_expression": abstract_to_expression[source],
                "output_expression": abstract_to_expression[target],
            }
        )

    require(
        len({item["component_id"] for item in transitions}) == 6,
        "component witness collision",
    )
    observables = {
        row["expression"]: {
            "terminal": row["terminal"],
            "effect_permitted": row["effect_permitted"],
        }
        for row in recognition_rows
    }
    require(
        len({tuple(value.values()) for value in observables.values()}) == 3,
        "recognition observables collapsed",
    )

    return {
        "document_type": "aset-proof-derived-recognition-witnesses",
        "witness_version": 1,
        "assurance_basis": "PROOF_ANCHORED_LOCAL_RECOGNITION_THEORY",
        "semantic_source_dependency": "NONE",
        "minimality": {
            "foundation_module": FOUNDATION.as_posix(),
            "foundation_sha256": sha256(foundation_path),
            "proof_module": PROOF.as_posix(),
            "proof_sha256": sha256(proof_path),
            "final_theorem": FINAL_THEOREM,
            "mechanical_proof_required_by_release_gate": True,
        },
        "algebra": {
            "module": ALGEBRA.as_posix(),
            "sha256": sha256(algebra_path),
        },
        "recognition_states": recognition_rows,
        "observables": observables,
        "transitions": transitions,
        "materialization_boundary": {
            "reads": [FOUNDATION.as_posix(), PROOF.as_posix(), ALGEBRA.as_posix()],
            "reads_seed_semantic_source": False,
            "reads_expression_derivers": False,
            "semantic_precedence": "NONE",
        },
        "status": "PASS",
    }


def witness_digest(value: dict[str, Any]) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def write_witnesses(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        witnesses = materialize_witnesses(ROOT)
        if args.output is not None:
            output = args.output if args.output.is_absolute() else ROOT / args.output
            write_witnesses(output, witnesses)
        count = len(witnesses["transitions"])
        print(f"ALPHA4_PROOF_WITNESS_TRANSITIONS={count}/6 PASS")
        print(f"ALPHA4_PROOF_WITNESS_DIGEST={witness_digest(witnesses)}")
        print("ALPHA4_PROOF_WITNESS_SEED_DEPENDENCY=NONE")
        print("ALPHA4_PROOF_WITNESS_MATERIALIZATION=PASS")
        return 0
    except (OSError, UnicodeError, ValueError, ProofWitnessError) as error:
        print(f"ALPHA4_PROOF_WITNESS_ERROR={error}")
        print("ALPHA4_PROOF_WITNESS_MATERIALIZATION=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

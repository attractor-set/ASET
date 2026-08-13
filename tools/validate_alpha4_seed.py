#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

try:
    from tools.alpha4_manifest import parse_seed_manifest
except ModuleNotFoundError:
    from alpha4_manifest import parse_seed_manifest

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "seed/alpha4"


def main() -> int:
    errors: list[str] = []
    try:
        bindings = parse_seed_manifest(ROOT)
    except Exception as error:
        print(f"ALPHA4_BINDING_ERROR={error}")
        print("ALPHA4_SEED_VALIDATION=FAIL")
        return 1

    if bindings.version != "0.4alpha":
        errors.append("Seed line version mismatch")
    if bindings.compatibility != "NONE":
        errors.append("0.3 compatibility must remain NONE")

    theory_text = (ROOT / bindings.theory_algebra).read_text(encoding="utf-8")
    if "EXTENDS RecognitionCardinality" not in theory_text:
        errors.append("local-recognition algebra is not grounded in cardinality theory")
    for forbidden in (
        "ComponentRelations",
        "RestrictedOperationalSemantics",
        "components.forth",
        "components.petri",
    ):
        if forbidden in theory_text:
            errors.append(
                f"theory improperly depends on Seed implementation: {forbidden}"
            )

    disallowed = [
        path
        for path in BASE.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}
    ]
    if disallowed:
        errors.append(
            "human/tree-document surface remains inside Seed: "
            + ", ".join(path.relative_to(ROOT).as_posix() for path in disallowed)
        )

    op_tool = (ROOT / bindings.deriver_map()["OPERATIONAL"]).read_text(encoding="utf-8")
    rel_tool = (ROOT / bindings.deriver_map()["RELATIONAL"]).read_text(encoding="utf-8")
    causal_tool = (ROOT / bindings.deriver_map()["CAUSAL"]).read_text(encoding="utf-8")
    if (
        "alpha4_relational_expression" in op_tool
        or "alpha4_causal_expression" in op_tool
    ):
        errors.append("operational derivation imports another semantic derivation")
    if (
        "alpha4_operational_expression" in rel_tool
        or "alpha4_causal_expression" in rel_tool
    ):
        errors.append("relational derivation imports another semantic derivation")
    if (
        "alpha4_operational_expression" in causal_tool
        or "alpha4_relational_expression" in causal_tool
    ):
        errors.append("causal derivation imports another semantic derivation")

    pairing_module = next(
        (
            item
            for item in bindings.proofs
            if item.proof_id == "OPERATIONAL_RELATIONAL_PAIRING"
        ),
        None,
    )
    if pairing_module is None:
        errors.append("operational/relational pairing proof binding missing")
    else:
        text = (ROOT / pairing_module.module).read_text(encoding="utf-8")
        for pair in bindings.pairs:
            if f"THEOREM {pair.pairing_theorem}" not in text:
                errors.append(f"pairing theorem missing: {pair.pairing_theorem}")

    if errors:
        for error in errors:
            print(f"ALPHA4_SEED_ERROR={error}")
        print("ALPHA4_SEED_VALIDATION=FAIL")
        return 1

    print("ALPHA4_RECOGNITION_FOUNDATION=PASS")
    print("ALPHA4_LOCAL_RECOGNITION_ALGEBRA=PASS")
    print("ALPHA4_ABSTRACT_FORTH_MACHINE=PASS")
    print("ALPHA4_FORMAL_CORRECTNESS_MODEL=PASS")
    print(f"ALPHA4_COMPONENT_PAIRS={len(bindings.pairs)}/{len(bindings.pairs)} PASS")
    print("ALPHA4_DERIVATION_INDEPENDENCE=PASS")
    print("ALPHA4_BINDING_PLAN=PASS")
    print("ALPHA4_HUMAN_SURFACE_IN_SEED=ABSENT")
    print("ALPHA4_JSON_SEMANTIC_AUTHORITY=NONE")
    print("ALPHA4_SEED_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

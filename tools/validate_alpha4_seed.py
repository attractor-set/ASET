#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

try:
    from tools.alpha4_binding_graph import binding_graph, encode_cbor, parse_seed_bindings
    from tools.alpha4_congruence import check_source_congruence
    from tools.alpha4_operational_expression import derive_operational_graphs
    from tools.alpha4_relational_expression import derive_relational_graphs
except ModuleNotFoundError:
    from alpha4_binding_graph import binding_graph, encode_cbor, parse_seed_bindings
    from alpha4_congruence import check_source_congruence
    from alpha4_operational_expression import derive_operational_graphs
    from alpha4_relational_expression import derive_relational_graphs

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "seed/alpha4"


def main() -> int:
    errors: list[str] = []
    try:
        bindings = parse_seed_bindings(ROOT)
    except Exception as error:
        print(f"ALPHA4_BINDING_ERROR={error}")
        print("ALPHA4_SEED_VALIDATION=FAIL")
        return 1

    if bindings.version != "0.4alpha":
        errors.append("Seed line version mismatch")
    if bindings.compatibility != "NONE":
        errors.append("0.3 compatibility must remain NONE")

    disallowed = [
        path for path in BASE.rglob("*")
        if path.is_file() and path.suffix.lower() in {".json", ".md", ".txt"}
    ]
    if disallowed:
        errors.append("human/tree-document surface remains inside Seed: " + ", ".join(
            path.relative_to(ROOT).as_posix() for path in disallowed
        ))

    try:
        evidence = check_source_congruence(ROOT)
        if evidence.get("status") != "PASS":
            errors.append("source content congruence did not pass")
    except Exception as error:
        errors.append(f"source content congruence: {error}")

    try:
        operational = derive_operational_graphs(ROOT)
        relational = derive_relational_graphs(ROOT)
        if len(operational.get("components", [])) != len(bindings.pairs):
            errors.append("operational pair count mismatch")
        if len(relational.get("components", [])) != len(bindings.pairs):
            errors.append("relational pair count mismatch")
    except Exception as error:
        errors.append(f"paired source derivation: {error}")

    op_tool = (ROOT / bindings.deriver_map()["OPERATIONAL"]).read_text(encoding="utf-8")
    rel_tool = (ROOT / bindings.deriver_map()["RELATIONAL"]).read_text(encoding="utf-8")
    if "alpha4_relational_expression" in op_tool:
        errors.append("operational derivation imports relational derivation")
    if "alpha4_operational_expression" in rel_tool:
        errors.append("relational derivation imports operational derivation")

    pairing_module = next(
        (item for item in bindings.proofs if item.proof_id == "OPERATIONAL_RELATIONAL_PAIRING"),
        None,
    )
    if pairing_module is None:
        errors.append("operational/relational pairing proof binding missing")
    else:
        text = (ROOT / pairing_module.module).read_text(encoding="utf-8")
        for pair in bindings.pairs:
            if f"THEOREM {pair.pairing_theorem}" not in text:
                errors.append(f"pairing theorem missing: {pair.pairing_theorem}")

    graph = binding_graph(bindings)
    encoded = encode_cbor(graph)
    if not encoded:
        errors.append("derived binding graph encoding is empty")

    if errors:
        for error in errors:
            print(f"ALPHA4_SEED_ERROR={error}")
        print("ALPHA4_SEED_VALIDATION=FAIL")
        return 1

    print("ALPHA4_RECOGNITION_FOUNDATION=PASS")
    print(f"ALPHA4_COMPONENT_PAIRS={len(bindings.pairs)}/{len(bindings.pairs)} PASS")
    print("ALPHA4_SOURCE_CONTENT_CONGRUENCE=PASS")
    print("ALPHA4_OPERATIONAL_RELATIONAL_SOURCE_PAIRING=PASS")
    print("ALPHA4_DERIVATION_INDEPENDENCE=PASS")
    print("ALPHA4_BINDING_GRAPH=PASS")
    print("ALPHA4_HUMAN_SURFACE_IN_SEED=ABSENT")
    print("ALPHA4_JSON_SEMANTIC_AUTHORITY=NONE")
    print("ALPHA4_SEED_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

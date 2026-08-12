#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from tools.alpha4_binding_graph import SeedBindings, parse_seed_bindings
    from tools.alpha4_operational_expression import (
        derive_operational_graphs,
        semantic_projection as operational_projection,
    )
    from tools.alpha4_paired_expression import check_paired_expression
    from tools.alpha4_relational_expression import (
        derive_relational_graphs,
        semantic_projection as relational_projection,
    )
except ModuleNotFoundError:
    from alpha4_binding_graph import SeedBindings, parse_seed_bindings
    from alpha4_operational_expression import (
        derive_operational_graphs,
        semantic_projection as operational_projection,
    )
    from alpha4_paired_expression import check_paired_expression
    from alpha4_relational_expression import (
        derive_relational_graphs,
        semantic_projection as relational_projection,
    )

ROOT = Path(__file__).resolve().parents[1]


class CongruenceError(RuntimeError):
    pass


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def strip_tla_comments(text: str) -> str:
    without_blocks = re.sub(r"\(\*.*?\*\)", "", text, flags=re.DOTALL)
    return re.sub(r"(?m)\\\*.*$", "", without_blocks)


def compact_tla(text: str) -> str:
    return compact(strip_tla_comments(text))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CongruenceError(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON object required: {path}")
    return value


def check_foundation_congruence(root: Path, bindings: SeedBindings) -> dict[str, Any]:
    model_path = root / bindings.foundation_model
    proof_path = root / bindings.foundation_proof.module
    model = compact_tla(model_path.read_text(encoding="utf-8"))
    proof = compact_tla(proof_path.read_text(encoding="utf-8"))

    model_claims = (
        'RecognitionStates=={"U","A","B"}',
        'TwoValues=={"0","1"}',
        'ThreeValues=={"0","1","2"}',
        r'Terminal(s)==s\in{"A","B"}',
        'EffectPermitted(s)==s="A"',
        "Observables(s)==[terminal|->Terminal(s),effect_permitted|->EffectPermitted(s)]",
        "Faithful(f,codomain)==",
        r"f\in[RecognitionStates->codomain]",
        "Observables(x)#Observables(y)=>f[x]#f[y]",
        "CanonicalThreeEncoding==",
        'CASEs="U"->"0"[]s="A"->"1"[]OTHER->"2"',
    )
    for claim in model_claims:
        require(compact(claim) in model, f"foundation model claim missing: {claim}")

    proof_claims = (
        "THEOREMRecognitionObservablesPairwiseDistinct==",
        "THEOREMNoFaithfulTwoValueEncoding==~\\Ef:Faithful(f,TwoValues)",
        "THEOREMCanonicalThreeEncodingIsFaithful==Faithful(CanonicalThreeEncoding,ThreeValues)",
        "THEOREMThreeRecognitionValuesAreCardinalityMinimal==",
        "~\\Ef:Faithful(f,TwoValues)",
        "\\Ef:Faithful(f,ThreeValues)",
    )
    for claim in proof_claims:
        require(compact(claim) in proof, f"foundation proof claim missing: {claim}")

    return {
        "relation": bindings.relation_map()["FOUNDATION"],
        "claims_checked": len(model_claims) + len(proof_claims),
        "status": "PASS",
    }


def check_theory_congruence(root: Path, bindings: SeedBindings) -> dict[str, Any]:
    theory_path = root / bindings.theory_algebra
    correctness_path = root / bindings.correctness_model
    theory = compact_tla(theory_path.read_text(encoding="utf-8"))
    correctness = compact_tla(correctness_path.read_text(encoding="utf-8"))

    theory_claims = (
        "EXTENDSRecognitionCardinality",
        "TheoryRecognitionValues==RecognitionStates",
        'TheoryUnknown=="U"',
        'TheoryAllow=="A"',
        'TheoryBlock=="B"',
        r"TheoryObserveUnknown(r,r2)==/\r=TheoryUnknown/\r2=TheoryUnknown",
        r"TheoryRecognizeAllow(r,r2)==/\r=TheoryUnknown/\r2=TheoryAllow",
        r"TheoryRecognizeBlock(r,r2)==/\r=TheoryUnknown/\r2=TheoryBlock",
        r"TheoryPreserveUnknown(r,r2)==/\r=TheoryUnknown/\r2=TheoryUnknown",
        r"TheoryPreserveAllow(r,r2)==/\r=TheoryAllow/\r2=TheoryAllow",
        r"TheoryPreserveBlock(r,r2)==/\r=TheoryBlock/\r2=TheoryBlock",
        "TheoryTerminal(r)==Terminal(r)",
        "TheoryEffectPermitted(r)==EffectPermitted(r)",
    )
    for claim in theory_claims:
        require(compact(claim) in theory, f"theory algebra claim missing: {claim}")

    require(
        bindings.theory_coding == ("U", "UNKNOWN", "A", "ALLOW", "B", "BLOCK"),
        "theory coding differs from declared abstract implementation coding",
    )
    correctness_claims = (
        "EXTENDSFiniteSets,LocalRecognitionAlgebra",
        'CASEr="UNKNOWN"->TheoryUnknown[]r="ALLOW"->TheoryAllow[]OTHER->TheoryBlock',
        "TheoryEffectPermitted(ToTheoryRecognition(s.recognition))",
        (
            "TheoryObserveUnknown(ToTheoryRecognition(s.recognition),"
            "ToTheoryRecognition(t.recognition))"
        ),
        (
            "TheoryRecognizeAllow(ToTheoryRecognition(s.recognition),"
            "ToTheoryRecognition(t.recognition))"
        ),
        (
            "TheoryRecognizeBlock(ToTheoryRecognition(s.recognition),"
            "ToTheoryRecognition(t.recognition))"
        ),
        (
            "TheoryPreserveUnknown(ToTheoryRecognition(s.recognition),"
            "ToTheoryRecognition(t.recognition))"
        ),
        (
            "TheoryPreserveAllow(ToTheoryRecognition(s.recognition),"
            "ToTheoryRecognition(t.recognition))"
        ),
        (
            "TheoryPreserveBlock(ToTheoryRecognition(s.recognition),"
            "ToTheoryRecognition(t.recognition))"
        ),
    )
    for claim in correctness_claims:
        require(
            compact(claim) in correctness,
            f"theory-constrained correctness claim missing: {claim}",
        )

    return {
        "relation": bindings.relation_map()["THEORY"],
        "theory_model": bindings.theory_algebra,
        "abstract_machine": bindings.abstract_machine,
        "formal_reflection": bindings.formal_reflection,
        "correctness_model": bindings.correctness_model,
        "claims_checked": len(theory_claims) + len(correctness_claims) + 1,
        "status": "PASS",
    }


def check_source_pairing(root: Path, bindings: SeedBindings) -> dict[str, Any]:
    operational = derive_operational_graphs(root)
    relational = derive_relational_graphs(root)
    op_projection = operational_projection(operational)
    rel_projection = relational_projection(relational)
    expected_ids = {item.component_id for item in bindings.pairs}
    require(
        set(op_projection) == expected_ids,
        "operational component identity set differs from binding relation",
    )
    require(
        set(rel_projection) == expected_ids,
        "relational component identity set differs from binding relation",
    )
    require(
        op_projection == rel_projection,
        "operational and relational source projections are incongruent",
    )
    return {
        "relation": "OPERATIONAL_RELATIONAL_SOURCE_PROJECTION_CONGRUENCE",
        "components_checked": len(expected_ids),
        "status": "PASS",
    }


def check_source_congruence(root: Path = ROOT) -> dict[str, Any]:
    bindings = parse_seed_bindings(root)
    source_pairing = check_source_pairing(root, bindings)
    return {
        "foundation": check_foundation_congruence(root, bindings),
        "theory": check_theory_congruence(root, bindings),
        "operational_component": {
            "relation": bindings.relation_map()["OPERATIONAL"],
            "components_checked": source_pairing["components_checked"],
            "status": "PASS",
        },
        "formal_component": {
            "relation": bindings.relation_map()["RELATIONAL"],
            "components_checked": source_pairing["components_checked"],
            "status": "PASS",
        },
        "source_pairing": source_pairing,
        "status": "PASS",
    }


def parse_assembled_operators(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"(?ms)^Next\(s, t, e\) ==\s*(?P<body>.*?)(?=^=+)", text)
    require(match is not None, "assembled formal Next relation missing")
    return re.findall(r"\\/\s*([A-Za-z][A-Za-z0-9_]*)\(s, t, e\)", match.group("body"))


def check_assembled_formal_congruence(
    root: Path, release_root: Path, bindings: SeedBindings
) -> dict[str, Any]:
    expected = [item.formal_operator for item in bindings.pairs]
    actual = parse_assembled_operators(release_root / "formal/AssembledSeed.tla")
    require(actual == expected, "assembled formal relation differs from binding order")
    return {
        "relation": bindings.relation_map()["ASSEMBLED"],
        "components_checked": len(expected),
        "status": "PASS",
    }


def check_release_congruence(root: Path, release_root: Path) -> dict[str, Any]:
    bindings = parse_seed_bindings(root)
    source = check_source_congruence(root)
    return {
        "document_type": "aset-content-congruence-evidence",
        "profile_id": "ASET-CONTENT-CONGRUENCE-0.4-ALPHA",
        "primary_integrity_relation": "DECLARED_CONTENT_CONGRUENCE",
        "digest_role": bindings.digest_role,
        "source": source,
        "assembled_formal": check_assembled_formal_congruence(
            root, release_root, bindings
        ),
        "paired_expression": check_paired_expression(root, release_root),
        "status": "PASS",
    }


def write_evidence(path: Path, evidence: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def print_evidence(evidence: dict[str, Any]) -> None:
    if isinstance(evidence.get("source"), dict):
        print("ALPHA4_SOURCE_CONTENT_CONGRUENCE=PASS")
    assembled = evidence.get("assembled_formal")
    if isinstance(assembled, dict):
        count = assembled["components_checked"]
        print(f"ALPHA4_ASSEMBLED_FORMAL_CONGRUENCE={count}/{count} PASS")
    paired = evidence.get("paired_expression")
    if isinstance(paired, dict):
        components = paired["components_checked"]
        cases = paired["cases_checked"]
        print(f"ALPHA4_PAIRED_GRAPH_CONGRUENCE={components}/{components} PASS")
        print(f"ALPHA4_JIT_REFERENCE_CONGRUENCE={cases}/{cases} PASS")
        print(f"ALPHA4_THEORY_PREDICTION_OBSERVATION={cases}/{cases} PASS")
    print("ALPHA4_CONTENT_CONGRUENCE=PASS")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-root", type=Path)
    parser.add_argument("--write-evidence", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.release_root is None:
            evidence: dict[str, Any] = {
                "document_type": "aset-source-content-congruence-evidence",
                "profile_id": "ASET-CONTENT-CONGRUENCE-0.4-ALPHA",
                "source": check_source_congruence(ROOT),
                "status": "PASS",
            }
            print("ALPHA4_SOURCE_CONTENT_CONGRUENCE=PASS")
        else:
            release_root = (
                args.release_root
                if args.release_root.is_absolute()
                else ROOT / args.release_root
            )
            evidence = check_release_congruence(ROOT, release_root)
            print_evidence(evidence)
        if args.write_evidence is not None:
            target = (
                args.write_evidence
                if args.write_evidence.is_absolute()
                else ROOT / args.write_evidence
            )
            write_evidence(target, evidence)
        return 0
    except (CongruenceError, KeyError, OSError, TypeError, ValueError) as error:
        print(f"ALPHA4_CONGRUENCE_ERROR={error}")
        print("ALPHA4_CONTENT_CONGRUENCE=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

try:
    from tools.alpha4_causal_expression import (
        CausalExpressionError,
        check_causal_invariant,
        derive_causal_graphs,
    )
    from tools.alpha4_congruence import CongruenceError, check_source_congruence
    from tools.alpha4_manifest import ManifestError, parse_seed_manifest
    from tools.alpha4_operational_expression import OperationalExpressionError
    from tools.alpha4_relational_expression import RelationalExpressionError
    from tools.alpha4_triangulated_expression import (
        TriangulatedExpressionError,
        check_triangulated_expression,
        print_evidence as print_triangulated_evidence,
    )
except ModuleNotFoundError:
    from alpha4_causal_expression import (
        CausalExpressionError,
        check_causal_invariant,
        derive_causal_graphs,
    )
    from alpha4_congruence import CongruenceError, check_source_congruence
    from alpha4_manifest import ManifestError, parse_seed_manifest
    from alpha4_operational_expression import OperationalExpressionError
    from alpha4_relational_expression import RelationalExpressionError
    from alpha4_triangulated_expression import (
        TriangulatedExpressionError,
        check_triangulated_expression,
        print_evidence as print_triangulated_evidence,
    )

ROOT = Path(__file__).resolve().parents[1]


def check_assurance(root: Path = ROOT) -> dict[str, object]:
    plan = parse_seed_manifest(root)
    source = check_source_congruence(root, plan)
    causal = derive_causal_graphs(root, plan)
    causal_invariant = check_causal_invariant(causal)
    triangulated = check_triangulated_expression(root, plan=plan)
    return {
        "document_type": "aset-seed-source-assurance",
        "subject_id": plan.subject_id,
        "version": plan.version,
        "binding_plan": "EPHEMERAL_FROM_SEED_ASET",
        "semantic_precedence": plan.semantic_precedence,
        "source_congruence": source,
        "causal_invariant": causal_invariant,
        "triangulated_expression": triangulated,
        "status": "PASS",
    }


def main() -> int:
    try:
        evidence = check_assurance(ROOT)
        source = evidence["source_congruence"]
        causal = evidence["causal_invariant"]
        triangulated = evidence["triangulated_expression"]
        assert isinstance(source, dict)
        assert isinstance(causal, dict)
        assert isinstance(triangulated, dict)
        components = triangulated["components_checked"]
        transitions = causal["transitions_checked"]
        print("ALPHA4_ASSURANCE_BINDING_PLAN=EPHEMERAL_FROM_SEED_ASET")
        print("ALPHA4_SOURCE_CONTENT_CONGRUENCE=PASS")
        print(f"ALPHA4_CAUSAL_COMPONENTS={components}/{components} PASS")
        print(
            "ALPHA4_CAUSAL_RECOGNITION_TOKEN_INVARIANT="
            f"{transitions}/{transitions} PASS"
        )
        print_triangulated_evidence(triangulated)
        print("ALPHA4_ASSURANCE=PASS")
        return 0
    except (
        AssertionError,
        KeyError,
        OSError,
        TypeError,
        ValueError,
        ManifestError,
        CongruenceError,
        CausalExpressionError,
        OperationalExpressionError,
        RelationalExpressionError,
        TriangulatedExpressionError,
    ) as error:
        print(f"ALPHA4_ASSURANCE_ERROR={error}")
        print("ALPHA4_ASSURANCE=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

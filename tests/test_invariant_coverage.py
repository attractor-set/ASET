from __future__ import annotations

import json
from pathlib import Path

from tools.seed_resolution_oracle import execute_case

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_coverage_closes_exact_canonical_sets() -> None:
    model = load("seed/canonical/source/seed-model.json")
    coverage = load("seed/canonical/assurance/invariant-coverage.json")
    assert {item["id"] for item in coverage["requirements"]} == {
        item["id"] for item in model["requirements"]
    }
    assert {item["id"] for item in coverage["invariants"]} == {
        item["id"] for item in model["invariants"]
    }
    assert {item["id"] for item in coverage["operations"]} == {
        item["id"] for item in model["operations"]
    }


def test_every_normative_entry_has_three_independent_evidence_classes() -> None:
    coverage = load("seed/canonical/assurance/invariant-coverage.json")
    for group in ("requirements", "invariants"):
        for item in coverage[group]:
            assert item["formal_properties"], item["id"]
            assert item["conformance_cases"], item["id"]
            assert item["semantic_mutations"], item["id"]


def test_new_adversarial_cases_match_the_canonical_oracle() -> None:
    for case_id in ("RES-NEG-014", "RES-NEG-015", "RES-NEG-016"):
        case = load(f"seed/canonical/conformance/cases/negative/{case_id}.json")
        actual, _ = execute_case(case)
        assert actual == case["expected"]


def test_implementation_neutrality_remains_explicit() -> None:
    model = load("seed/canonical/source/seed-model.json")
    assert model["implementation_boundary"]["implementation_precedence"] == "NONE"

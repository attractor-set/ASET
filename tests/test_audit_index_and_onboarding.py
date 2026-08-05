from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_audit_index_classifies_every_static_audit_record_once() -> None:
    index = load("audit/ACTIVE_AUDIT_INDEX.json")
    active = set(index["active_controlling_records"])
    historical = set(index["historical_noncontrolling_records"])
    excluded = set(index["index_exclusions"])
    assert not active & historical
    expected = {
        path.relative_to(ROOT).as_posix()
        for path in (ROOT / "audit").rglob("*")
        if path.is_file()
    }
    assert active | historical | excluded == expected
    assert active & expected == active
    assert historical & expected == historical


def test_historical_runtime_audit_is_explicitly_noncontrolling() -> None:
    index = load("audit/ACTIVE_AUDIT_INDEX.json")
    historical = set(index["historical_noncontrolling_records"])
    assert "audit/RC12_FINAL_BLACKBOX_AUDIT.json" in historical
    assert "audit/RC12_FINAL_BLACKBOX_AUDIT.md" in historical
    assert index["active_candidate"]["implementation_precedence"] == "NONE"
    readme = (ROOT / "audit/README.md").read_text(encoding="utf-8")
    assert "historical non-controlling" in readme


def test_controlled_patch_walkthrough_is_multilingual_and_non_normative() -> None:
    documents = {
        "README.md": "docs/tutorials/CONTROLLED_PATCH_WORKFLOW.md",
        "README.ru.md": "docs/tutorials/CONTROLLED_PATCH_WORKFLOW.ru.md",
        "README.pt-BR.md": "docs/tutorials/CONTROLLED_PATCH_WORKFLOW.pt-BR.md",
    }
    for readme_name, tutorial in documents.items():
        assert tutorial in (ROOT / readme_name).read_text(encoding="utf-8")
        text = (ROOT / tutorial).read_text(encoding="utf-8")
        assert "Proposal != Resolution != Permit != Receipt" in text
        assert "Observation != Evidence != Verification != Outcome" in text
        assert "seed/canonical/source/seed-model.json" in text
        assert "implementation-conformance-protocol.json" in text


def test_cross_implementation_claim_has_explicit_admission_plan() -> None:
    roadmap = (ROOT / "ROADMAP.md").read_text(encoding="utf-8")
    relative = "docs/implementation/CROSS_IMPLEMENTATION_CONFORMANCE_PLAN.md"
    assert relative in roadmap
    plan = (ROOT / relative).read_text(encoding="utf-8")
    assert "must not" in plan
    assert "zero unexplained differential observations" in plan
    assert "external runner computes all verdicts" in plan

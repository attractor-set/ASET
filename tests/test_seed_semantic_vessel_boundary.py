from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_semantic_vessel_role_is_machine_readable_without_changing_operational_nucleus() -> None:
    status = load("REPOSITORY_STATUS.json")
    assert status["architectural_role"] == "MACHINE_INTERPRETABLE_EVOLUTION_CAPABLE_SEMANTIC_VESSEL"
    assert status["operational_nucleus"] == "LOCAL_EXACT_BINDING_RESOLUTION_RECOGNITION"
    assert status["evolution_search_boundary"] == "OUTSIDE_SEED_UNSPECIFIED_NO_RECOGNITION_AUTHORITY"


def test_evolution_search_internals_are_outside_seed_and_have_no_recognition_authority() -> None:
    text = (ROOT / "docs/architecture/EVOLUTION_BOUNDARY.md").read_text(encoding="utf-8")
    assert "ASET does not standardize `E`" in text
    assert "Seed conformance requires no disclosure of search internals" in text
    assert "candidate production does not create Authority" in text
    assert "search mechanism has no semantic precedence" in text


def test_architecture_docs_do_not_silently_enter_normative_canon_package() -> None:
    package = load("seed/canonical/CANON_PACKAGE.json")
    paths = {item["path"] for item in package["files"]}
    assert "docs/architecture/SEED_ROLE.md" not in paths
    assert "docs/architecture/EVOLUTION_BOUNDARY.md" not in paths
    assert "seed/canonical/source/seed-model.json" in paths

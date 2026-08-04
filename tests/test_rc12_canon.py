from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_rc12_canon_is_complete_and_bounded():
    model = load("seed/canonical/source/seed-model.json")
    assert model["version"] == "0.1-rc12"
    assert model["status"] == "RC12_RELEASE_CANDIDATE_READY"
    assert len(model["concepts"]) >= 20
    assert len(model["requirements"]) >= 38
    assert len(model["invariants"]) >= 29
    assert len(model["transitions"]) == 18
    assert model["runtime_profile"]["status"] == "PRODUCTION_READY_BOUNDED_PROFILE"
    assert model["canonicality"]["external_third_party_audit"] == "PENDING"


def test_rc11_migration_is_fully_classified_and_migrated():
    migration = load("seed/canonical/migration/RC11_TO_RC12_SEMANTIC_COVERAGE.json")
    assert migration["summary"] == {
        "rc11_requirements": 26,
        "rc11_transition_kinds": 18,
        "rc11_schemas": 39,
        "fully_migrated_to_rc12": 83,
        "deferred_with_explicit_disposition": 0,
        "unclassified": 0,
    }


def test_protocol_and_conformance_catalogues_are_complete():
    protocol = load("seed/canonical/protocol/protocol-profile.json")
    conformance = load("seed/canonical/conformance/conformance-profile.json")
    assert protocol["schema_count"] == 39
    assert len(protocol["schemas"]) == 39
    assert conformance["case_count"] == 55
    assert conformance["positive_count"] == 23
    assert conformance["negative_count"] == 32


def test_rc12_conformance_runner_passes_all_frozen_vectors():
    result = subprocess.run(
        [sys.executable, "tools/run_rc12_conformance.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RC12_CONFORMANCE=55/55" in result.stdout


def test_bounded_model_checker_passes():
    result = subprocess.run(
        [sys.executable, "tools/model_check_rc12.py", "--depth", "7"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "MODEL_CHECK_VERDICT=PASS" in result.stdout

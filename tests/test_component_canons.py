from __future__ import annotations

import hashlib
import json
import subprocess
import sys

import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

pytestmark = pytest.mark.legacy_extensions


def load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def run_tool(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *arguments],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def test_component_partition_is_lossless() -> None:
    migration = load("aset/shared/migration/RC11_TO_COMPONENT_CANONS.json")
    expected = {
        "requirements": 177,
        "invariants": 57,
        "artifacts": 52,
        "gates": 11,
        "schemas": 57,
    }
    for kind, count in expected.items():
        assignments = migration["assignments"][kind]
        identifiers = [item["id"] for item in assignments]
        assert len(identifiers) == count
        assert len(set(identifiers)) == count


def test_seed_bridge_requires_full_external_effect_chain() -> None:
    bridge = load("aset/shared/seed-bridge/seed-compatibility-profile.json")
    rules = {
        item["classification"]: item
        for item in bridge["classification_rules"]
    }
    assert rules["EXTERNAL_EFFECT"]["sequence"] == [
        "Decision",
        "Permit",
        "PermitUseReceipt",
        "ExecutionIntent",
        "Observation",
        "Verification",
        "Outcome",
    ]


def test_historical_seed_rc12_baseline_is_preserved_as_evidence() -> None:
    baseline = load("aset/source/seed-rc12/SEED_RC12_BASELINE.json")
    assert baseline["document_type"] == "aset-seed-rc12-byte-baseline"
    assert baseline["files_count"] == len(baseline["files"]) == 303
    assert baseline["source_archive_sha256"].startswith("sha256:")


def test_active_seed_uses_canon_package_identity() -> None:
    package = load("seed/canonical/CANON_PACKAGE.json")
    assert package["implementation_precedence"] == "NONE"
    assert package["conformance_protocol"] == "ASET-SEED-RESOLUTION-CONFORMANCE-V1"


def test_component_validator_and_generated_views() -> None:
    validation = run_tool("tools/validate_component_canons.py")
    assert validation.returncode == 0, validation.stdout + validation.stderr
    parity = run_tool("tools/generate_component_views.py", "--check")
    assert parity.returncode == 0, parity.stdout + parity.stderr


def test_component_generated_views_follow_language_policy() -> None:
    result = run_tool("tools/check_language.py")
    assert result.returncode == 0, result.stdout + result.stderr


def test_component_conformance_is_reproducible() -> None:
    result = run_tool("tools/run_component_conformance.py", "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    report = load("aset/shared/conformance/results.json")
    assert report["verdict"] == "PASS"
    assert report["cases_passed"] == report["cases_total"] == 26


def test_component_bounded_models_are_reproducible() -> None:
    result = run_tool("tools/model_check_components.py", "--check")
    assert result.returncode == 0, result.stdout + result.stderr
    report = load("aset/shared/formal/results.json")
    assert report["verdict"] == "PASS"
    assert report["models_passed"] == report["models_total"] == 8


def test_component_assurance_packages_are_self_contained() -> None:
    migration = load("aset/shared/migration/RC11_TO_COMPONENT_CANONS.json")
    assignments = {
        item["id"]: item["target"]
        for item in migration["assignments"]["requirements"]
    }
    total = 0
    for key in (
        "context",
        "core",
        "gateway",
        "master",
        "memory",
        "monade",
        "protocol",
        "system",
    ):
        base = (
            "aset/system/canonical"
            if key == "system"
            else f"aset/components/{key}/canonical"
        )
        requirements = load(f"{base}/assurance/requirements.json")
        verification = load(f"{base}/assurance/verification-cases.json")
        traceability = load(f"{base}/assurance/traceability.json")
        expected = {
            identifier
            for identifier, target in assignments.items()
            if target == key
        }
        requirement_ids = {item["ID"] for item in requirements["requirements"]}
        verification_ids = {item["RequirementID"] for item in verification["cases"]}
        traceability_ids = {
            item["DerivedRequirementID"] or item["SystemRequirementID"]
            for item in traceability["links"]
        }
        assert requirement_ids == verification_ids == traceability_ids == expected
        total += len(expected)
    assert total == 177


def test_component_blackbox_is_not_part_of_active_seed_gate() -> None:
    gate = (ROOT / "tools/repository_release_gate.py").read_text(encoding="utf-8")
    assert "tools/blackbox_component_audit.py" not in gate
    assert "tools/run_component_blackbox_adversarial.py" not in gate
    assert "tools/model_check_components.py" not in gate


def test_component_canons_are_discoverable_from_root_docs() -> None:
    for relative in ("README.md", "README.ru.md", "README.pt-BR.md", "ROADMAP.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "(aset/README.md)" in text


def test_reference_implementation_is_linked_without_precedence() -> None:
    url = "https://github.com/attractor-set/aset-python-sqlite"
    for relative in ("README.md", "README.ru.md", "README.pt-BR.md", "ROADMAP.md"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert url in text
    assert "no semantic precedence" in (ROOT / "README.md").read_text(encoding="utf-8")
    assert "не имеет семантического приоритета" in (
        ROOT / "README.ru.md"
    ).read_text(encoding="utf-8")
    assert "não possui precedência semântica" in (
        ROOT / "README.pt-BR.md"
    ).read_text(encoding="utf-8")


def test_active_component_assurance_environment_is_implementation_neutral() -> None:
    system = load("aset/system/canonical/source/system-composition-model.json")
    environment_invariant = next(
        item for item in system["invariant_assignments"] if item["id"] == "INV-ENV-001"
    )
    assert "Python" not in environment_invariant["statement"]
    assert "assurance-toolchain" in environment_invariant["statement"]

    for key in (
        "context",
        "core",
        "gateway",
        "master",
        "memory",
        "monade",
        "protocol",
        "system",
    ):
        base = (
            "aset/system/canonical"
            if key == "system"
            else f"aset/components/{key}/canonical"
        )
        verification = load(f"{base}/assurance/verification-cases.json")
        for case in verification["cases"]:
            environment = case["Environment"]
            assert "Python 3.11+" not in environment
            assert "SQLite" not in environment
            assert "PostgreSQL" not in environment
            assert "Rust" not in environment

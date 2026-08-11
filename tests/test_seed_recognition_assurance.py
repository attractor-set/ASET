import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "assurance/seed-implementation-assurance/ASSURANCE_CONFORMANCE_PROFILE.json"
MANIFEST = ROOT / "assurance/seed-implementation-assurance/GENERATED_CASES_MANIFEST.json"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_module(name: str, relative: str):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_profile_is_non_normative_and_derived_from_public_v60():
    profile = load(PROFILE)
    v60 = load(ROOT / "assurance/seed-recognition-boundary/ASSURANCE_PACKAGE.json")
    canon = load(ROOT / "seed/canonical/CANON_PACKAGE.json")
    assert profile["profile_id"] == "ASET-SEED-RECOGNITION-ASSURANCE-V1"
    assert profile["normative"] is False
    assert profile["normative_precedence"] == "NONE"
    assert profile["subject"]["v60_assurance_id"] == v60["assurance_id"]
    assert profile["subject"]["v60_assurance_package_digest"] == v60["package_digest"]
    assert profile["subject"]["seed_canon_package_digest"] == canon["package_digest"]
    assert any(
        "INVALIDATED_ALLOW versus INVALIDATED_BLOCK" in item
        for item in profile["claim_boundary"]["excluded"]
    )


def test_generated_case_set_is_deterministic_schema_valid_and_pinned():
    cases_module = load_module(
        "seed_recognition_assurance_cases",
        "tools/seed_recognition_assurance_cases.py",
    )
    cases = cases_module.generate_cases()
    errors = cases_module.validate_cases(cases)
    assert errors == []
    generated = cases_module.case_manifest(cases)
    assert generated == load(MANIFEST)
    assert generated["cases_total"] == 24
    assert generated["category_counts"] == {
        "effective-class": 1,
        "effective-conflict": 2,
        "exact-authority-binding": 1,
        "pending-payload": 4,
        "terminal-behavior": 4,
        "terminal-payload": 12,
    }


def test_case_builder_check_passes():
    completed = subprocess.run(
        [sys.executable, "tools/build_seed_recognition_assurance_cases.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "SEED_RECOGNITION_ASSURANCE_CASE_MANIFEST=PASS" in completed.stdout


def test_assurance_runner_passes_against_canonical_oracle_adapter(tmp_path):
    report = tmp_path / "assurance.json"
    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_seed_recognition_assurance.py",
            "--adapter",
            f"{sys.executable} tools/seed_resolution_oracle_adapter.py",
            "--adapter-cwd",
            str(ROOT),
            "--output",
            str(report),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "SEED_RECOGNITION_ASSURANCE_CASES=24/24" in completed.stdout
    assert "SEED_RECOGNITION_ASSURANCE_DETERMINISTIC_REPLAY=PASS" in completed.stdout
    assert "SEED_RECOGNITION_ASSURANCE_CANONICAL_PROJECTION=PASS" in completed.stdout
    assert "SEED_RECOGNITION_ASSURANCE_VERDICT=PASS" in completed.stdout
    data = load(report)
    assert data["pass"] is True
    assert data["cases_passed"] == 24
    assert data["cases_executed"] == 24
    assert data["protocol_operations_verified"] == ["describe", "execute_case", "execute_cases"]


def test_assurance_comparison_detects_collapsed_exact_projection():
    cases_module = load_module(
        "seed_recognition_assurance_cases_cmp",
        "tools/seed_recognition_assurance_cases.py",
    )
    runner = load_module(
        "run_seed_recognition_assurance_cmp",
        "tools/run_seed_recognition_assurance.py",
    )
    from tools.seed_resolution_oracle import execute_case
    case = next(
        case
        for case in cases_module.generate_cases()
        if case["case_id"] == "ASSURE-PENDING-B0-P0"
    )
    actual, final_store = execute_case(case)
    response = {
        "protocol": "ASET-SEED-RESOLUTION-CONFORMANCE-V3",
        "case_id": case["case_id"],
        "actual": actual,
        "final_store": copy.deepcopy(final_store),
    }
    response["final_store"]["requests"][0]["previous_terminal_record_digest"] = None
    row = runner.compare_case(case, response)
    assert row["pass"] is False
    assert "canonical_final_store_projection_mismatch" in row["errors"]


def test_normative_corpus_remains_separate_and_unchanged_in_size():
    profile = load(ROOT / "seed/canonical/conformance/conformance-profile.json")
    canon = load(ROOT / "seed/canonical/CANON_PACKAGE.json")
    canon_paths = {item["path"] for item in canon["files"]}
    assert profile["protocol"] == "ASET-SEED-RESOLUTION-CONFORMANCE-V3"
    assert profile["positive_count"] == 9
    assert profile["negative_count"] == 16
    assert len(profile["cases"]) == 25
    assert not any(
        path.startswith("assurance/seed-implementation-assurance/")
        for path in canon_paths
    )


def test_existing_normative_external_runner_still_passes_oracle_adapter(tmp_path):
    report = tmp_path / "normative.json"
    completed = subprocess.run(
        [
            sys.executable,
            "tools/run_external_conformance.py",
            "--canon-root",
            str(ROOT),
            "--adapter",
            f"{sys.executable} tools/seed_resolution_oracle_adapter.py",
            "--adapter-cwd",
            str(ROOT),
            "--output",
            str(report),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    assert "IMPLEMENTATION_CONFORMANCE=25/25" in completed.stdout
    assert "IMPLEMENTATION_CONFORMANCE_VERDICT=PASS" in completed.stdout

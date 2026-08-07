from __future__ import annotations

import json
from pathlib import Path

from tools.build_seed_conformance_kit import release_version

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "standards/seed-compatibility/compatibility-standard-profile-v1.json"
SCHEMA = ROOT / "standards/seed-compatibility/compatibility-standard-release.schema.json"


def test_seed_compatibility_profile_v1_pins_standard_rules() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    assert profile["profile_id"] == "ASET-SEED-COMPATIBILITY-STANDARD-V1"
    assert profile["standard_series_id"] == "ASET-SEED-COMPATIBILITY-STANDARD"
    assert profile["implementation_neutral"] is True
    assert profile["hash_algorithm"] == "SHA-256"
    assert profile["conformance_claim"]["implementation_precedence"] == "NONE"
    assert profile["conformance_claim"]["must_bind_exact_release"] is True
    assert profile["conformance_claim"]["mandatory_result"] == (
        "all mandatory conformance cases PASS"
    )
    assert profile["conformance_claim"]["verdict_authority"] == (
        "external ASET conformance runner"
    )
    assert profile["distribution"]["archive"]["compression"] == "ZIP_STORED"
    assert profile["distribution"]["archive"]["fixed_timestamp"] == (
        "1980-01-01T00:00:00Z"
    )
    assert "seed/canonical/CANON_PACKAGE.json" in profile["distribution"]["support_files"]
    assert "tools/run_external_conformance.py" in profile["distribution"]["support_files"]


def test_compatibility_release_schema_pins_exact_seed_release_identity() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    required = set(schema["required"])
    assert {
        "standard_id",
        "standard_profile_sha256",
        "release_tag",
        "release_commit",
        "canonical_package_digest",
        "conformance_protocol",
        "conformance_profile_sha256",
        "mandatory_conformance_cases",
    } <= required
    assert schema["properties"]["implementation_precedence"]["const"] == "NONE"


def test_candidate_version_does_not_impersonate_a_published_release() -> None:
    commit = "a" * 40
    assert release_version("HEAD", commit) == "candidate-aaaaaaaaaaaa"

def test_ci_and_release_gate_build_seed_compatibility_distribution() -> None:
    candidate = (ROOT / ".github/workflows/seed-ci.yml").read_text(encoding="utf-8")
    release = (ROOT / ".github/workflows/release-candidate.yml").read_text(encoding="utf-8")
    gate = (ROOT / "tools/repository_release_gate.py").read_text(encoding="utf-8")
    assert "tools/build_seed_conformance_kit.py" in candidate
    assert "tools/build_seed_conformance_kit.py" in gate
    assert "tools/repository_release_gate.py" in release
    assert "dist/seed-conformance-kit/**" in release
    assert "tools/check_seed_compatibility_profile_stability.py" in gate

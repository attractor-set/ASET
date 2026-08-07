from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "tools/registration/inpi-software-deposit-profile-v1.json"


def test_inpi_deposit_profile_v1_pins_generation_rules_not_release_contents() -> None:
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))
    assert profile["profile_id"] == "ASET-INPI-SOFTWARE-DEPOSIT-V1"
    assert profile["hash_algorithm"] == "SHA-256"
    assert profile["source"]["ordering"] == "lexicographic-path"
    assert profile["source"]["selectors"] == [
        "seed/canonical",
        "tools",
        "tests",
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
    ]
    assert profile["archive"] == {
        "compression": "ZIP_STORED",
        "create_system": 3,
        "fixed_timestamp": "1980-01-01T00:00:00Z",
        "format": "zip",
        "path_prefix_template": "ASET-Seed-{release_version}/",
        "preserve_git_mode": True,
    }


def test_release_tag_version_is_distinct_from_semantic_version() -> None:
    from tools.build_inpi_software_deposit import release_version

    assert release_version("seed-0.3.0-alpha.2", "0.3.0-alpha.1") == "0.3.0-alpha.2"
    assert release_version("HEAD", "0.3.0-alpha.1") == "0.3.0-alpha.1"

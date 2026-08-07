from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def sha256(relative: str) -> str:
    return "sha256:" + hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_supplement_2_preserves_parent_identity_and_no_assignment() -> None:
    parent = load("governance/ip/background-ip-schedule.json")
    supplement = load("governance/ip/background-ip-supplement-2.json")
    assert supplement["creator"] == parent["creator"]
    holder = supplement["current_rights_holder"]
    assert isinstance(holder, dict)
    assert holder["legal_name"] == "Dzmitry Prychyna"
    assert holder["assignment_to_legal_entity"] is False


def test_supplement_2_pins_release_and_semantic_freeze() -> None:
    supplement = load("governance/ip/background-ip-supplement-2.json")
    cutoffs = supplement["cutoffs"]
    assert isinstance(cutoffs, list) and len(cutoffs) == 1
    release = cutoffs[0]
    assert isinstance(release, dict)
    assert release["release_tag"] == "seed-0.3.0-alpha.1"
    assert release["release_tag_object_sha"] == "03eaa7c36c4cbf938e43d39ece7a3d1ef69f2d13"
    assert release["commit_sha"] == "ade1e2fe58c34ca4fa53695ea9e2ec3d08552518"
    assert release["release_is_prerelease"] is True
    assert release["semantic_freeze_tag"] == "seed-0.3.0-alpha.1-semantic-freeze"
    assert release["semantic_freeze_tag_object_sha"] == "7004dcfebf5bd9566fa70a53c7da00c36aaf069c"
    assert release["semantic_freeze_commit_sha"] == "a96689b1f1da17ac126058f5ee0175c90df3ef4f"
    assert release["canon_package_digest"] == "sha256:0f0a51e4655fac186a70445f717027e42f1adc7a722f99b2eecf4dd3a2410c8d"
    assert release["manifest_files_count"] == 417


def test_supplement_2_pins_prior_supplement_bytes() -> None:
    supplement = load("governance/ip/background-ip-supplement-2.json")
    prior = supplement["prior_supplements"]
    assert isinstance(prior, list) and len(prior) == 1
    record = prior[0]
    assert isinstance(record, dict)
    assert record["supplement_id"] == "ASET-BACKGROUND-IP-SUPPLEMENT-1"
    assert record["document_sha256"] == sha256("governance/ip/background-ip-supplement-1.json")


def test_supplement_2_assets_are_unique_and_bounded() -> None:
    supplement = load("governance/ip/background-ip-supplement-2.json")
    assets = supplement["added_assets"]
    assert isinstance(assets, list)
    identifiers = [asset["asset_id"] for asset in assets if isinstance(asset, dict)]
    assert identifiers == [f"BI-S2-{index:03d}" for index in range(1, 5)]
    assert len(identifiers) == len(set(identifiers))


def test_background_ip_supplement_2_validation_passes() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_background_ip_supplement_2.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "BACKGROUND_IP_SUPPLEMENT_2_VALIDATION=PASS" in result.stdout


def test_supplement_2_is_discoverable_and_release_gated() -> None:
    readme = (ROOT / "governance/ip/README.md").read_text(encoding="utf-8")
    gate = (ROOT / "tools/repository_release_gate.py").read_text(encoding="utf-8")
    for token in (
        "BACKGROUND_IP_SUPPLEMENT_2.md",
        "background-ip-supplement-2.json",
        "background-ip-supplement-2.schema.json",
        "validate_background_ip_supplement_2.py",
    ):
        assert token in readme or token in gate

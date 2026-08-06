from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_supplement_preserves_parent_identity_and_no_assignment() -> None:
    parent = load("governance/ip/background-ip-schedule.json")
    supplement = load("governance/ip/background-ip-supplement-1.json")
    assert supplement["creator"] == parent["creator"]
    holder = supplement["current_rights_holder"]
    assert isinstance(holder, dict)
    assert holder["legal_name"] == "Dzmitry Prychyna"
    assert holder["public_pseudonym"] == "Attractor Set"
    assert holder["assignment_to_legal_entity"] is False


def test_supplement_pins_specification_and_reference_profile() -> None:
    supplement = load("governance/ip/background-ip-supplement-1.json")
    cutoffs = supplement["cutoffs"]
    assert isinstance(cutoffs, list)
    assert len(cutoffs) == 2
    specification, reference = cutoffs
    assert isinstance(specification, dict)
    assert isinstance(reference, dict)
    assert specification["commit_sha"] == (
        "a122e2f828256501abb645b89046cc866f4466ed"
    )
    assert reference["commit_sha"] == (
        "2038f84b6b5f6a0aed3636c1685d2c1fb79a1ed1"
    )
    assert reference["canon_lock_source_ref"] == specification["commit_sha"]
    assert reference["canon_lock_required_package_digest"] == specification[
        "canon_package_digest"
    ]


def test_supplement_assets_are_unique_and_bounded() -> None:
    supplement = load("governance/ip/background-ip-supplement-1.json")
    assets = supplement["added_assets"]
    assert isinstance(assets, list)
    identifiers = [asset["asset_id"] for asset in assets if isinstance(asset, dict)]
    assert len(identifiers) == len(set(identifiers))
    assert identifiers == [f"BI-S1-{index:03d}" for index in range(1, 7)]
    exclusions = supplement["exclusions"]
    assert isinstance(exclusions, list)
    assert "FUTURE_RUST_POSTGRESQL_OR_OTHER_IMPLEMENTATIONS_NOT_PRESENT_AT_CUTOFF" in exclusions
    assert "UNMERGED_ASSURANCE_REMEDIATION_PATCHES_CREATED_AFTER_CUTOFF" in exclusions


def test_background_ip_supplement_validation_passes() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_background_ip_supplement.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "BACKGROUND_IP_SUPPLEMENT_VALIDATION=PASS" in result.stdout


def test_supplement_is_discoverable_from_ip_governance() -> None:
    text = (ROOT / "governance/ip/README.md").read_text(encoding="utf-8")
    for token in (
        "BACKGROUND_IP_SUPPLEMENT_1.md",
        "background-ip-supplement-1.json",
        "background-ip-supplement.schema.json",
    ):
        assert token in text

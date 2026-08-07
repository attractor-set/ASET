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


def test_background_ip_identity_is_explicit() -> None:
    schedule = load("governance/ip/background-ip-schedule.json")
    creator = schedule["creator"]
    holder = schedule["current_rights_holder"]
    assert isinstance(creator, dict)
    assert isinstance(holder, dict)
    assert creator["legal_name"] == "Dzmitry Prychyna"
    assert creator["public_pseudonym"] == "Attractor Set"
    assert creator["pseudonym_is_separate_legal_entity"] is False
    assert holder["legal_name"] == "Dzmitry Prychyna"
    assert holder["assignment_to_legal_entity"] is False


def test_background_ip_brazil_profile_is_bounded() -> None:
    schedule = load("governance/ip/background-ip-schedule.json")
    profile = schedule["brazil_profile"]
    declaration = schedule["independent_creation_declaration"]
    assert isinstance(profile, dict)
    assert isinstance(declaration, dict)
    assert profile["inpi_registration_required_for_protection"] is False
    assert profile["inpi_registration_status"] == "NOT_FILED"
    assert profile["future_company_assignment_required"] is True
    assert declaration["commissioned_by_current_employer"] is False
    assert declaration["current_employer_resources_used"] is False
    assert declaration["developed_outside_employment_scope"] is True


def test_background_ip_validation_passes() -> None:
    result = subprocess.run(
        [sys.executable, "tools/validate_background_ip.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "BACKGROUND_IP_VALIDATION=PASS" in result.stdout


def test_background_ip_is_discoverable_from_static_docs() -> None:
    for relative in (
        "GOVERNANCE.md",
        "CONTRIBUTING.md",
        "ROADMAP.md",
        "governance/ip/README.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "BACKGROUND_IP_SCHEDULE" in text

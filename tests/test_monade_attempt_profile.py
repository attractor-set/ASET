from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "aset/profiles/monade-attempt-evidence/canonical"


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


def test_monade_attempt_profile_is_optional_and_seed_neutral() -> None:
    profile = load("aset/profiles/monade-attempt-evidence/canonical/PROFILE.json")
    assert profile["normative_for_profile"] is True
    assert profile["normative_for_seed"] is False
    assert profile["required_for_seed_conformance"] is False
    assert profile["implementation_precedence"] == "NONE"
    assert profile["seed_boundary"]["seed_model_unchanged"] is True
    assert profile["seed_boundary"]["seed_conformance_cases_unchanged"] is True

    package = load("seed/canonical/CANON_PACKAGE.json")
    assert not any(
        item["path"].startswith("aset/profiles/")
        for item in package["files"]
    )


def test_master_consumes_only_read_only_projection() -> None:
    profile = load("aset/profiles/monade-attempt-evidence/canonical/PROFILE.json")
    integration = profile["master_integration"]
    assert integration["mode"] == "READ_ONLY_LEARNING_OBSERVATION_PROJECTION"
    assert integration["master_specification_change_required"] is False
    assert integration["projection_grants_authority"] is False


def test_profile_package_validation_and_conformance_are_reproducible() -> None:
    for command in (
        ("tools/build_monade_attempt_profile_package.py", "--check"),
        ("tools/validate_monade_attempt_profile.py",),
        ("tools/run_monade_attempt_conformance.py", "--check"),
        ("tools/model_check_monade_attempt_profile.py", "--check"),
    ):
        result = run_tool(*command)
        assert result.returncode == 0, result.stdout + result.stderr

    conformance = load(
        "aset/profiles/monade-attempt-evidence/canonical/conformance/results.json"
    )
    assert conformance["verdict"] == "PASS"
    assert conformance["cases_passed"] == conformance["cases_total"] == 12

    model = load("aset/profiles/monade-attempt-evidence/canonical/formal/results.json")
    assert model["verdict"] == "PASS"
    assert model["states"] == 18
    assert model["transitions"] == 18
    assert model["negative_terminal_states"] == 10


def test_negative_attempts_never_enter_the_canonical_graph() -> None:
    model = load("aset/profiles/monade-attempt-evidence/canonical/formal/state-space.json")
    negative = [node for node in model["nodes"] if node["negative"]]
    assert len(negative) == 10
    assert all(node["terminal"] for node in negative)
    assert all(node["canonical_state_changed"] is False for node in negative)
    assert all(node["candidate_parent_allowed"] is False for node in negative)
    sources = {transition["from"] for transition in model["transitions"]}
    assert not sources.intersection({node["id"] for node in negative})


def test_profile_changes_notify_core_only_implementations() -> None:
    workflow = (ROOT / ".github/workflows/notify-implementation-profiles.yml").read_text(
        encoding="utf-8"
    )
    assert "aset/profiles/monade-attempt-evidence/**" in workflow
    assert "aset/components/monade/canonical/**" in workflow


def test_release_gate_enforces_profile_assurance() -> None:
    gate = (ROOT / "tools/repository_release_gate.py").read_text(encoding="utf-8")
    for tool in (
        "tools/build_monade_attempt_profile_package.py",
        "tools/validate_monade_attempt_profile.py",
        "tools/run_monade_attempt_conformance.py",
        "tools/model_check_monade_attempt_profile.py",
    ):
        assert tool in gate

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_active_seed_contains_no_monade_profile() -> None:
    assert not (ROOT / "aset/profiles/monade-attempt-evidence").exists()
    package = json.loads(
        (ROOT / "seed/canonical/CANON_PACKAGE.json").read_text(encoding="utf-8")
    )
    paths = {item["path"] for item in package["files"]}
    assert not any(path.startswith("aset/") for path in paths)
    assert not any("monade" in path.lower() for path in paths)


def test_active_seed_ci_has_no_extension_assurance_dependency() -> None:
    files = (
        ".github/workflows/seed-ci.yml",
        ".github/workflows/production-assurance.yml",
        "tools/repository_release_gate.py",
        "tools/generate_repository_views.py",
    )
    forbidden = (
        "monade_attempt",
        "monade-attempt",
        "model_check_components.py",
        "run_component_conformance.py",
        "blackbox_component_audit.py",
        "run_component_blackbox_adversarial.py",
        "generate_component_views.py",
    )
    for relative in files:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{relative} contains active extension dependency {token}"


def test_only_seed_package_changes_notify_core_implementations() -> None:
    workflow = (
        ROOT / ".github/workflows/notify-implementation-profiles.yml"
    ).read_text(encoding="utf-8")
    assert "seed/canonical/CANON_PACKAGE.json" in workflow
    assert "aset/components/" not in workflow
    assert "aset/profiles/" not in workflow


def test_historical_components_are_declared_noncontrolling() -> None:
    canonicality = (ROOT / "CANONICALITY.md").read_text(encoding="utf-8")
    archive = (ROOT / "aset/README.md").read_text(encoding="utf-8")
    assert "do not expand the active Seed" in canonicality
    assert "noncontrolling migration archive" in archive
    assert "Nothing under this directory" in archive
    assert "is part of active Seed conformance" in archive

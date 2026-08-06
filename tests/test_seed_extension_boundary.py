from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict[str, object]:
    value = json.loads((ROOT / relative).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_active_seed_contains_no_extracted_component_tree() -> None:
    assert not (ROOT / "aset").exists()
    assert not (ROOT / "audit/components").exists()
    package = load("seed/canonical/CANON_PACKAGE.json")
    paths = {item["path"] for item in package["files"]}
    assert not any(path.startswith("aset/") for path in paths)
    assert not any("component" in path.lower() for path in paths)


def test_active_seed_ci_has_no_component_assurance_dependency() -> None:
    files = (
        ".github/workflows/seed-ci.yml",
        ".github/workflows/production-assurance.yml",
        "tools/repository_release_gate.py",
        "tools/generate_repository_views.py",
    )
    forbidden = (
        "model_check_components.py",
        "run_component_conformance.py",
        "blackbox_component_audit.py",
        "run_component_blackbox_adversarial.py",
        "generate_component_views.py",
        "validate_component_canons.py",
    )
    for relative in files:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for token in forbidden:
            assert token not in text, f"{relative} contains {token}"


def test_only_seed_package_changes_notify_implementations() -> None:
    workflow = (
        ROOT / ".github/workflows/notify-implementation-profiles.yml"
    ).read_text(encoding="utf-8")
    assert "seed/canonical/CANON_PACKAGE.json" in workflow
    assert "aset/components/" not in workflow
    assert "aset/profiles/" not in workflow


def test_external_registries_are_non_normative() -> None:
    extensions = load("EXTENSIONS.json")
    implementations = load("IMPLEMENTATIONS.json")
    extraction = load("EXTRACTION.json")
    assert extensions["normative"] is False
    assert implementations["normative"] is False
    assert extraction["normative_effect"] == "NONE_ON_RESOLUTION_SEMANTICS"
    for registry, key in (
        (extensions, "extensions"),
        (implementations, "implementations"),
    ):
        assert all(
            item["implementation_precedence"] == "NONE"
            for item in registry[key]
        )

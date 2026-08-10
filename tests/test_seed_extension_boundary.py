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


def test_seed_has_no_implementation_specific_notification_workflow() -> None:
    assert not (ROOT / ".github/workflows/notify-implementation-profiles.yml").exists()


def test_reference_artifacts_are_readme_only_and_non_normative() -> None:
    removed = (
        "EXTENSIONS.json",
        "EXTENSIONS.md",
        "IMPLEMENTATIONS.json",
        "IMPLEMENTATIONS.md",
        "EXTRACTION.json",
        "EXTRACTION.md",
    )
    for relative in removed:
        assert not (ROOT / relative).exists()

    references = (
        "https://github.com/attractor-set/aset-network-extension",
        "https://github.com/attractor-set/aset-python-sqlite",
    )
    for readme_name in ("README.md", "README.ru.md", "README.pt-BR.md"):
        text = (ROOT / readme_name).read_text(encoding="utf-8")
        for reference in references:
            assert text.count(reference) == 1
        assert "non-normative" in text or "ненорматив" in text or "não normativa" in text
        assert "aset-network-python-sqlite" not in text
        assert "aset-ai-extension-template" not in text
        assert "aset-ai-local-stack" not in text

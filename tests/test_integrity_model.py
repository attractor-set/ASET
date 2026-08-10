from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_active_repository_integrity_does_not_use_repository_manifest():
    assert not (ROOT / "MANIFEST.json").exists()
    assert not (ROOT / "tools/rebuild_manifest.py").exists()

    runner = (ROOT / "tools/repository_release_gate.py").read_text(encoding="utf-8")
    ci = (ROOT / ".github/workflows/seed-ci.yml").read_text(encoding="utf-8")
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")

    for text in (runner, ci, contributing):
        assert "rebuild_manifest" not in text
    assert "tools/check_repository_source_identity.py" in runner
    assert "tools/check_repository_source_identity.py" in ci


def test_canonical_release_gates_separate_identity_domains():
    gates = load("seed/canonical/assurance/repository-release-gates.json")
    by_id = {item["id"]: item for item in gates["gates"]}

    assert by_id["ASET-GATE-014"] == {
        "evidence": "python tools/check_repository_source_identity.py",
        "id": "ASET-GATE-014",
        "mandatory": True,
        "name": "git_repository_source_identity",
    }
    assert by_id["ASET-GATE-015"]["evidence"] == (
        "python tools/build_release.py --verify-determinism"
    )
    assert "repository source and release-artifact integrity" in gates["claim_boundary"]["included"]
    assert "release and manifest integrity" not in gates["claim_boundary"]["included"]


def test_repository_snapshot_is_built_from_committed_git_bytes():
    builder = (ROOT / "tools/build_release.py").read_text(encoding="utf-8")
    assert '"ls-tree", "-r", "--name-only", "-z", ref' in builder
    assert '"show", f"{ref}:{path.as_posix()}"' in builder
    assert "ROOT.rglob" not in builder
    assert "--verify-determinism" in builder


def test_historical_ip_validators_read_historical_manifest_from_git():
    for relative in (
        "tools/validate_background_ip.py",
        "tools/validate_background_ip_supplement.py",
        "tools/validate_background_ip_supplement_2.py",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "git" in text.lower()
        assert "manifest" in text.lower()

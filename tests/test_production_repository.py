from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str):
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_repository_and_runtime_claims_are_separate():
    status = load("REPOSITORY_STATUS.json")
    assert status["repository_production_readiness"] == (
        "DOCUMENTATION_AND_BOUNDED_RUNTIME_PRODUCTION_READY"
    )
    assert status["seed_runtime_production"] == (
        "PRODUCTION_READY_SINGLE_NODE_SQLITE_PROFILE"
    )
    assert status["next_seed_status"] == (
        "RC12_RELEASE_CANDIDATE_READY"
    )


def test_all_repository_gates_are_mandatory_and_unique():
    data = load(
        "seed/canonical/assurance/"
        "repository-release-gates.json"
    )
    identifiers = [gate["id"] for gate in data["gates"]]
    assert data["fail_closed"] is True
    assert len(identifiers) == 19
    assert len(identifiers) == len(set(identifiers))
    assert all(gate["mandatory"] is True for gate in data["gates"])


def test_rc11_to_rc12_register_has_no_unclassified_items():
    data = load(
        "seed/canonical/migration/"
        "RC11_TO_RC12_SEMANTIC_COVERAGE.json"
    )
    summary = data["summary"]
    assert summary["rc11_requirements"] == 26
    assert summary["rc11_transition_kinds"] == 18
    assert summary["rc11_schemas"] == 39
    assert summary["fully_migrated_to_rc12"] == 83
    assert summary["deferred_with_explicit_disposition"] == 0
    assert summary["unclassified"] == 0
    assert data["target_status"] == (
        "RC12_RELEASE_CANDIDATE_READY"
    )


def test_no_open_blocking_repository_findings():
    data = load("audit/FINDING_CLOSURE_MATRIX.json")
    assert data["open_blocking_findings"] == []


def test_expanded_rc11_is_byte_exact():
    result = subprocess.run(
        [sys.executable, "tools/materialize_rc11.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RC11_EXPANDED_BYTE_IDENTITY=PASS" in result.stdout


def test_blackbox_auditor_is_standalone():
    source = (
        ROOT / "tools/blackbox_documentation_audit.py"
    ).read_text(encoding="utf-8")
    assert "from tools" not in source
    assert "import tools" not in source


def test_expanded_rc11_git_storage_is_byte_exact():
    result = subprocess.run(
        [sys.executable, "tools/materialize_rc11.py", "--check-git"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "RC11_GIT_STORAGE_BYTE_IDENTITY=PASS" in result.stdout

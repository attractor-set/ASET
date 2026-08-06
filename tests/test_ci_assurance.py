import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_verification_registry_resolves_to_declared_gates():
    registry = load("seed/canonical/assurance/verification-registry.json")
    gates = load("seed/canonical/assurance/repository-release-gates.json")
    gate_ids = {item["id"] for item in gates["gates"]}
    assert registry["normative"] is True
    for method in registry["verification_methods"]:
        assert set(method.get("gate_ids", [])) <= gate_ids
        assert method.get("gate_ids") or method.get("external_profile_gate") is True


def test_current_change_declaration_is_bound_to_candidate_model():
    declaration = load("seed/canonical/migration/CANON_CHANGE_DECLARATION.json")
    model = ROOT / "seed/canonical/source/seed-model.json"
    digest = "sha256:" + hashlib.sha256(model.read_bytes()).hexdigest()
    assert declaration["change_class"] == "BREAKING"
    assert declaration["change_kind"] == "SEMANTIC_SIMPLIFICATION"
    assert declaration["candidate_model_sha256"] == digest
    assert (ROOT / declaration["decision_ref"]).is_file()
    assert (ROOT / declaration["supersession_ref"]).is_file()

def test_ci_workflows_have_distinct_assurance_roles():
    candidate = (ROOT / ".github/workflows/seed-ci.yml").read_text(encoding="utf-8")
    formal = (ROOT / ".github/workflows/production-assurance.yml").read_text(encoding="utf-8")
    release = (ROOT / ".github/workflows/release-candidate.yml").read_text(encoding="utf-8")
    assert "candidate-consistency" in candidate
    assert "tools/run_tlc.py" in formal
    assert "tools/check_canon_compatibility.py" not in candidate
    assert "ASET_APPROVED_REF" in release


def test_assurance_traceability_tool_passes_after_model_check(tmp_path):
    model_report = tmp_path / "model.json"
    first = subprocess.run(
        [sys.executable, "tools/model_check_seed.py", "--output", str(model_report)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert first.returncode == 0, first.stdout + first.stderr
    second = subprocess.run(
        [
            sys.executable,
            "tools/check_assurance_traceability.py",
            "--model-report",
            str(model_report),
            "--output",
            str(tmp_path / "traceability.json"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert second.returncode == 0, second.stdout + second.stderr


def test_seed_resolution_tla_uses_valid_operator_tokens():
    specification = (
        ROOT / "seed/canonical/formal/SeedResolution.tla"
    ).read_text(encoding="utf-8")
    assert "/\\\\" not in specification
    assert "Range(" not in specification
    assert 'Init ==\n  /\\ authorityBindings \\in SUBSET (Authorities \\X Bindings)' in specification
    assert '  /\\ requests = {}' in specification
    assert "Spec == Init /\\ [][Next]_vars" in specification


def test_seed_resolution_tlc_treats_terminal_states_as_intended_quiescence():
    specification = (
        ROOT / "seed/canonical/formal/SeedResolution.tla"
    ).read_text(encoding="utf-8")
    configuration = (
        ROOT / "seed/canonical/formal/SeedResolution.cfg"
    ).read_text(encoding="utf-8")
    assert (
        'TerminalUnique ==' in specification
    )
    assert "CHECK_DEADLOCK FALSE" in configuration
    assert "AuthorityBindings =" not in configuration
    assert r"authorityBindings \in SUBSET (Authorities \X Bindings)" in specification


def test_active_audit_index_tracks_active_canon_package():
    package = load("seed/canonical/CANON_PACKAGE.json")
    audit_index = load("audit/ACTIVE_AUDIT_INDEX.json")
    assert (
        audit_index["active_candidate"]["canon_package_digest"]
        == package["package_digest"]
    )

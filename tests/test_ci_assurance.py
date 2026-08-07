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
    formal = (ROOT / ".github/workflows/production-assurance.yml").read_text(
        encoding="utf-8"
    )
    release = (ROOT / ".github/workflows/release-candidate.yml").read_text(
        encoding="utf-8"
    )
    assert "candidate-consistency" in candidate
    assert "tools/check_proof_traceability.py" in candidate
    assert "tools/check_canon_tla_refinement.py" in candidate
    assert "tools/run_tlc.py" in formal
    assert "tools/run_tlaps.py" in formal
    assert "tools/check_proof_traceability.py" in formal
    assert "tools/check_canon_tla_refinement.py" in formal
    assert "tools/run_canon_tla_refinement.py" in formal
    assert "4600b24" in formal
    assert "tlaps-proof.json" in formal
    assert "tools/check_canon_compatibility.py" not in candidate
    assert "ASET_APPROVED_REF" in release
    assert "TLA2TOOLS_JAR" in release
    assert "TLAPM_BIN" in release
    assert "proof-traceability-check.json" in release
    assert "canon-tla-refinement-check.json" in release
    assert "canon-tla-refinement-proof.json" in release
    assert "tools/repository_release_gate.py" in release
    assert "tlc-model-check.json" in release
    assert "tlaps-proof.json" in release


def test_tlaps_gate_and_final_theorems_are_declared():
    registry = load("seed/canonical/assurance/verification-registry.json")
    gates = load("seed/canonical/assurance/repository-release-gates.json")
    proof = (ROOT / "seed/canonical/formal/SeedResolutionProofs.tla").read_text(
        encoding="utf-8"
    )

    method = next(
        item
        for item in registry["verification_methods"]
        if item["id"] == "ASET-VERIFY-TLAPS-UNBOUNDED"
    )
    gate = next(item for item in gates["gates"] if item["id"] == "ASET-GATE-028")

    assert method["gate_ids"] == ["ASET-GATE-028"]
    assert gate["mandatory"] is True
    assert "tools/run_tlaps.py" in gate["evidence"]

    for theorem in (
        "SpecImpliesAlwaysSeedStateSafety",
        "SpecImpliesRequestsAppendOnly",
        "SpecImpliesTerminalRecordsImmutable",
        "SpecImpliesSeedStateChangesOnlyByRecognizedTransition",
        "SpecImpliesConflictObservationPreservesSeedState",
    ):
        assert f"THEOREM {theorem} ==" in proof


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
    specification = (ROOT / "seed/canonical/formal/SeedResolution.tla").read_text(
        encoding="utf-8"
    )
    assert r"/\\" not in specification
    assert "Range(" not in specification
    assert "VARIABLES\n    requestMeta,\n    terminalMeta,\n    conflicts" in specification
    assert "RequestAuthorityBindings" in specification
    assert "TerminalAuthorityBindings" in specification
    assert "observedInputs" not in specification
    assert "invalidMaterial" not in specification
    assert "terminalBinding," not in specification
    assert "requestAuthority," not in specification
    assert "Requests == DOMAIN requestMeta" in specification
    assert "TerminalRequests == DOMAIN terminalMeta" in specification
    assert "NoRequest" not in specification
    assert "NoTerminal" not in specification
    assert r"Spec == Init /\ [][Next]_vars" in specification


def test_seed_resolution_tlc_treats_terminal_states_as_intended_quiescence():
    specification = (ROOT / "seed/canonical/formal/SeedResolution.tla").read_text(
        encoding="utf-8"
    )
    configuration = (ROOT / "seed/canonical/formal/SeedResolution.cfg").read_text(
        encoding="utf-8"
    )
    assert "TerminalUnique ==" in specification
    assert "CHECK_DEADLOCK FALSE" in configuration
    assert "RequestAuthorityBindings <- TLC_RequestAuthorityBindings" in configuration
    assert "TerminalAuthorityBindings <- TLC_TerminalAuthorityBindings" in configuration
    assert r"RequestAuthorityBindings \subseteq TerminalAuthorityBindings" in specification


def test_active_audit_index_tracks_active_canon_package():
    package = load("seed/canonical/CANON_PACKAGE.json")
    audit_index = load("audit/ACTIVE_AUDIT_INDEX.json")
    assert (
        audit_index["active_candidate"]["canon_package_digest"]
        == package["package_digest"]
    )


def test_mandatory_proof_traceability_gate_is_in_aggregate_runner():
    gates = load("seed/canonical/assurance/repository-release-gates.json")
    runner = (ROOT / "tools/repository_release_gate.py").read_text(encoding="utf-8")

    gate = next(item for item in gates["gates"] if item["id"] == "ASET-GATE-029")

    assert gate["mandatory"] is True
    assert "tools/check_proof_traceability.py" in gate["evidence"]
    assert "tools/check_proof_traceability.py" in runner
    assert "dist/proof-traceability-check.json" in runner


def test_canon_tla_refinement_relation_is_complete_and_mandatory():
    relation = load("seed/canonical/assurance/canon-tla-refinement.json")
    gates = load("seed/canonical/assurance/repository-release-gates.json")
    registry = load("seed/canonical/assurance/verification-registry.json")
    runner = (ROOT / "tools/repository_release_gate.py").read_text(encoding="utf-8")

    assert len(relation["requirement_coverage"]) == 12
    assert len(relation["invariant_coverage"]) == 12
    assert len(relation["transition_coverage"]) == 3
    assert len(relation["resolution_algebra_fields"]) == 7
    assert relation["proof"]["final_theorem"] == (
        "SeedResolutionBehaviorallyEquivalentToCanonProjection"
    )
    projection = (ROOT / "seed/canonical/formal/SeedCanonProjection.tla").read_text(encoding="utf-8")
    assert "EXTENDS SeedResolution" not in projection
    assert "INSTANCE SeedResolution" not in projection
    assert "V4 is a standalone projection" in projection

    assert len(gates["gates"]) >= 26

    gate_030 = next(item for item in gates["gates"] if item["id"] == "ASET-GATE-030")
    gate_031 = next(item for item in gates["gates"] if item["id"] == "ASET-GATE-031")
    assert gate_030["mandatory"] is True
    assert gate_031["mandatory"] is True
    assert "check_canon_tla_refinement.py" in gate_030["evidence"]
    assert "run_canon_tla_refinement.py" in gate_031["evidence"]
    assert "check_canon_tla_refinement.py" in runner
    assert "run_canon_tla_refinement.py" in runner

    method = next(
        item
        for item in registry["verification_methods"]
        if item["id"] == "ASET-VERIFY-CANON-TLA-REFINEMENT"
    )
    assert method["gate_ids"] == ["ASET-GATE-030", "ASET-GATE-031"]


def test_generated_canon_tla_projection_is_current(tmp_path):
    result = subprocess.run(
        [sys.executable, "tools/generate_canon_tla_projection.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

    result = subprocess.run(
        [
            sys.executable,
            "tools/check_canon_tla_refinement.py",
            "--output",
            str(tmp_path / "canon-tla-refinement.json"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

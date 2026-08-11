import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assurance/seed-recognition-boundary"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def digest(path: str) -> str:
    return "sha256:" + hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def test_perimeter_is_external_to_frozen_canon():
    canon = load("seed/canonical/CANON_PACKAGE.json")
    paths = {item["path"] for item in canon["files"]}
    assert not any(path.startswith("assurance/seed-recognition-boundary/") for path in paths)
    assert canon["package_digest"] == "sha256:0df0ab8ecc5a1e87a4004573a9e26b04b1301ca74f8db2606ff506d6e37b5010"
    assert digest("seed/canonical/formal/SeedResolution.tla") == "sha256:1c0ebb27ed52da289f0981dcb11b61b6a7fc5c4a030ba434ae0b1d53b286b926"


def test_publication_contains_complete_active_v60_without_legacy_history():
    package = load("assurance/seed-recognition-boundary/ASSURANCE_PACKAGE.json")
    baseline = load("assurance/seed-recognition-boundary/PUBLICATION_BASELINE.json")
    modules = list((BASE / "formal").glob("*.tla"))
    assert package["publication_baseline"] == "ASET-SEED-SEMANTIC-MINIMALITY-V60"
    assert package["active_tla_modules"] == 34
    assert package["proof_modules"] == 20
    assert package["expected_tlaps_obligations"] == 2257
    assert len(modules) == 34
    assert len(package["proof_chain"]) == 20
    assert baseline["source_v60_tlaps_obligations"] == 2257
    assert baseline["publication_policy"]["legacy_history_published"] is False
    assert not (BASE / "retired").exists()
    assert not list(BASE.glob("V*_FAILURE_ANALYSIS.md"))


def test_assurance_package_is_bound_to_frozen_seed_and_existing_canon_relation():
    package = load("assurance/seed-recognition-boundary/ASSURANCE_PACKAGE.json")
    canon = load("seed/canonical/CANON_PACKAGE.json")
    relation = load("seed/canonical/assurance/canon-tla-refinement.json")
    subject = package["subject"]
    assert package["normative"] is False
    assert package["normative_precedence"] == "NONE"
    assert subject["canon_id"] == canon["canon_id"]
    assert subject["canon_version"] == canon["canon_version"]
    assert subject["canon_package_digest"] == canon["package_digest"]
    assert subject["seed_resolution_sha256"] == digest("seed/canonical/formal/SeedResolution.tla")
    assert subject["canon_tla_refinement_sha256"] == digest("seed/canonical/assurance/canon-tla-refinement.json")
    assert relation["target_model"]["sha256"] == subject["seed_resolution_sha256"]
    assert relation["source_model"]["sha256"] == subject["seed_model_sha256"]


def test_formal_chain_directly_links_assurance_to_seed_resolution():
    forward = (BASE / "formal/CanonicalPhaseSeedToSeedRefinementProofs.tla").read_text(encoding="utf-8")
    reverse = (BASE / "formal/SeedToCanonicalPhaseSeedRefinementProofs.tla").read_text(encoding="utf-8")
    local = (BASE / "formal/CanonicalLocalReachability.tla").read_text(encoding="utf-8")
    information = (BASE / "formal/CanonicalReachableInformationBoundProofs.tla").read_text(encoding="utf-8")
    assert "Seed == INSTANCE SeedResolution" in forward
    assert "THEOREM CanonicalPhaseSeedRefinesSeedResolution ==" in forward
    assert "EXTENDS SeedResolution, TLAPS" in reverse
    assert "THEOREM SeedResolutionRefinesCanonicalPhaseSeed ==" in reverse
    assert "Canonical == INSTANCE CanonicalPhaseSeed" in local
    assert "CanonicalLocalReachabilityProofs" in information
    assert "ParametricLocalStateCardinalityProofs" in information
    assert "THEOREM CanonicalReachableInformationBound ==" in information


def test_perimeter_metadata_explains_public_non_normative_gate():
    gate = load("assurance/seed-recognition-boundary/PERIMETER_GATE.json")
    readme = (BASE / "README.md").read_text(encoding="utf-8")
    assert gate["id"] == "ASET-PERIMETER-SEED-RECOGNITION-001"
    assert gate["mandatory_repository_precondition"] is True
    assert gate["normative"] is False
    assert gate["publication_baseline"] == "ASET-SEED-SEMANTIC-MINIMALITY-V60"
    assert gate["stages"][-1]["expected_obligations"] == 2257
    assert gate["stages"][-1]["expected_known_toolchain_notices"] == 15
    assert gate["stages"][-1]["expected_unexpected_warnings"] == 0
    assert "Why another gate?" in readme
    assert "does **not** define Seed semantics" in readme
    assert "2257" in readme
    assert "Re-baselining" in readme


def test_static_perimeter_checker_and_oracle_pass(tmp_path):
    package_check = subprocess.run([sys.executable, "tools/build_seed_recognition_boundary_assurance.py", "--check"], cwd=ROOT, text=True, capture_output=True, check=False)
    assert package_check.returncode == 0, package_check.stdout + package_check.stderr
    report = tmp_path / "boundary.json"
    boundary_check = subprocess.run([sys.executable, "tools/check_seed_recognition_boundary.py", "--output", str(report)], cwd=ROOT, text=True, capture_output=True, check=False)
    assert boundary_check.returncode == 0, boundary_check.stdout + boundary_check.stderr
    data = json.loads(report.read_text(encoding="utf-8"))
    assert data["verdict"] == "PASS"
    assert data["expected_tlaps_obligations"] == 2257
    assert data["oracle"]["profiles_checked"] == 2046
    assert data["oracle"]["max_shortest_reachability_depth"] == 3
    assert data["oracle"]["rich_exact_states"] == 29


def test_perimeter_is_wired_into_repository_and_ci_assurance():
    runner = (ROOT / "tools/repository_release_gate.py").read_text(encoding="utf-8")
    candidate = (ROOT / ".github/workflows/seed-ci.yml").read_text(encoding="utf-8")
    formal = (ROOT / ".github/workflows/production-assurance.yml").read_text(encoding="utf-8")
    release = (ROOT / ".github/workflows/release-candidate.yml").read_text(encoding="utf-8")
    assert "build_seed_recognition_boundary_assurance.py" in runner
    assert "check_seed_recognition_boundary.py" in runner
    assert "run_seed_recognition_boundary_tlaps.py" in runner
    assert "build_seed_recognition_boundary_assurance.py" in candidate
    assert "check_seed_recognition_boundary.py" in candidate
    assert "run_seed_recognition_boundary_tlaps.py" in formal
    assert "seed-recognition-boundary-check.json" in formal
    assert "seed-recognition-boundary-tlaps.json" in formal
    assert "seed-recognition-boundary-check.json" in release
    assert "seed-recognition-boundary-tlaps.json" in release


def test_toolchain_notice_policy_is_exact_and_fail_closed():
    policy = load("assurance/seed-recognition-boundary/TOOLCHAIN_NOTICES.json")
    assert policy["toolchain"]["tlapm_version"] == "4600b24"
    assert policy["policy"]["unexpected_warning"] == "FAIL"
    assert policy["policy"]["missing_expected_notice"] == "FAIL"
    assert policy["policy"]["formal_source_rewrite_for_toolchain_notice"] is False
    notice = policy["notices"][0]
    assert notice["expected_total_occurrences"] == 15
    assert sum(sum(rows.values()) for rows in notice["expected_by_module"].values()) == 15


def test_reported_tlapm_warning_coordinates_are_not_source_local_positions():
    parametric = (BASE / "formal/ParametricLocalStateCardinalityProofs.tla").read_text(encoding="utf-8").splitlines()
    canonical = (BASE / "formal/CanonicalLocalReachabilityProofs.tla").read_text(encoding="utf-8").splitlines()
    assert len(parametric) == 475
    assert 1177 > len(parametric)
    assert 1209 > len(parametric)
    assert len(canonical[1061 - 1]) < 54
    assert len(canonical[1176 - 1]) < 54
    assert len(canonical[1310 - 1]) < 54


def test_tlaps_runner_classifies_exact_warning_multiset_without_rewriting_proof():
    import importlib.util

    runner_path = ROOT / "tools/run_seed_recognition_boundary_tlaps.py"
    spec = importlib.util.spec_from_file_location("seed_boundary_tlaps_runner", runner_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    policy = load("assurance/seed-recognition-boundary/TOOLCHAIN_NOTICES.json")
    expected = policy["notices"][0]["expected_by_module"]["CanonicalLocalReachabilityProofs.tla"]
    output = "\n".join(line for line, count in expected.items() for _ in range(count)) + "\n[INFO]: All 476 obligations proved.\n"
    count, unexpected_count, problems = module.classify_warnings(policy, "CanonicalLocalReachabilityProofs.tla", output)
    assert count == 9
    assert unexpected_count == 0
    assert problems == []
    clean = module.without_warning_lines(output)
    assert "WARNING:" not in clean
    assert "All 476 obligations proved." in clean
    _, extra_count, extra = module.classify_warnings(
        policy,
        "CanonicalLocalReachabilityProofs.tla",
        output + "WARNING: synthetic new warning\n",
    )
    assert extra_count == 1
    assert extra

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assurance/seed-recognition-boundary"
MANIFEST = BASE / "ASSURANCE_PACKAGE.json"

FROZEN_CANON_ID = "ASET-SEED-RESOLUTION-CANON-0.3-ALPHA1"
FROZEN_CANON_VERSION = "0.3.0-alpha.1"
FROZEN_CANON_PACKAGE_FILE_SHA256 = "sha256:610f4396348c837618904770c914d52b264dd2370b91728f8a259d99516e548b"
FROZEN_CANON_PACKAGE_DIGEST = "sha256:0df0ab8ecc5a1e87a4004573a9e26b04b1301ca74f8db2606ff506d6e37b5010"
FROZEN_SEED_MODEL_SHA256 = "sha256:1fed5dc95045a287b3e9b8b4ea011a7b977729158f3360ed9a8a7e7e6ba1b4b0"
FROZEN_SEED_RESOLUTION_SHA256 = "sha256:1c0ebb27ed52da289f0981dcb11b61b6a7fc5c4a030ba434ae0b1d53b286b926"
FROZEN_CANON_TLA_REFINEMENT_SHA256 = "sha256:22884e71f1a484a8a7b00f708188191783505a71d1b2d15ad73cca67510099a5"
FROZEN_PUBLICATION_BASELINE_SHA256 = "sha256:6144b801ccb9468ce667402d5eaf1e5eeee52d7dbd3a464a440722079694f129"

ASSURANCE_FILES = ['assurance/seed-recognition-boundary/README.md', 'assurance/seed-recognition-boundary/THEOREM_SCOPE.md', 'assurance/seed-recognition-boundary/PROVENANCE.md', 'assurance/seed-recognition-boundary/PUBLICATION_BASELINE.json', 'assurance/seed-recognition-boundary/PERIMETER_GATE.json', 'assurance/seed-recognition-boundary/TOOLCHAIN_NOTICES.json', 'assurance/seed-recognition-boundary/formal/CanonicalLocalReachability.tla', 'assurance/seed-recognition-boundary/formal/CanonicalLocalReachabilityProofs.tla', 'assurance/seed-recognition-boundary/formal/CanonicalPhaseSeed.tla', 'assurance/seed-recognition-boundary/formal/CanonicalPhaseSeedToSeedRefinementProofs.tla', 'assurance/seed-recognition-boundary/formal/CanonicalReachableInformationBound.tla', 'assurance/seed-recognition-boundary/formal/CanonicalReachableInformationBoundProofs.tla', 'assurance/seed-recognition-boundary/formal/DecisionSubjectBinding.tla', 'assurance/seed-recognition-boundary/formal/DecisionSubjectBindingProofs.tla', 'assurance/seed-recognition-boundary/formal/GenesisAnchoredRecognition.tla', 'assurance/seed-recognition-boundary/formal/GenesisAnchoredRecognitionProofs.tla', 'assurance/seed-recognition-boundary/formal/GenesisAnchoredRecognitionSeedRefinementProofs.tla', 'assurance/seed-recognition-boundary/formal/IndependentProjectionAdequacy.tla', 'assurance/seed-recognition-boundary/formal/IndependentProjectionAdequacyProofs.tla', 'assurance/seed-recognition-boundary/formal/IndependentRecognitionContract.tla', 'assurance/seed-recognition-boundary/formal/IndependentRecognitionContractProofs.tla', 'assurance/seed-recognition-boundary/formal/IndependentRecognitionToGCRLiftingProofs.tla', 'assurance/seed-recognition-boundary/formal/MachineBindability.tla', 'assurance/seed-recognition-boundary/formal/MachineBindabilityProofs.tla', 'assurance/seed-recognition-boundary/formal/MachineDecisionSubjectBindingProofs.tla', 'assurance/seed-recognition-boundary/formal/MinimalRecognitionBoundary.tla', 'assurance/seed-recognition-boundary/formal/MinimalRecognitionBoundaryProofs.tla', 'assurance/seed-recognition-boundary/formal/MinimalRecognitionBoundaryToSeedRefinementProofs.tla', 'assurance/seed-recognition-boundary/formal/ParametricLocalStateCardinality.tla', 'assurance/seed-recognition-boundary/formal/ParametricLocalStateCardinalityProofs.tla', 'assurance/seed-recognition-boundary/formal/RecognitionCardinality.tla', 'assurance/seed-recognition-boundary/formal/RecognitionCardinalityProofs.tla', 'assurance/seed-recognition-boundary/formal/RecognitionInformationLowerBounds.tla', 'assurance/seed-recognition-boundary/formal/RecognitionInformationLowerBoundsProofs.tla', 'assurance/seed-recognition-boundary/formal/RecognitionOperationalCardinality.tla', 'assurance/seed-recognition-boundary/formal/RecognitionOperationalCardinalityProofs.tla', 'assurance/seed-recognition-boundary/formal/RecognitionPayloadObservability.tla', 'assurance/seed-recognition-boundary/formal/RecognitionPayloadObservabilityProofs.tla', 'assurance/seed-recognition-boundary/formal/SeedRecognitionMinimalityProofs.tla', 'assurance/seed-recognition-boundary/formal/SeedToCanonicalPhaseSeedRefinementProofs.tla']
PROOF_CHAIN = [{'id': 'RECOGNITION_CARDINALITY', 'proof_module': 'assurance/seed-recognition-boundary/formal/RecognitionCardinalityProofs.tla', 'final_theorem': 'ThreeRecognitionValuesAreCardinalityMinimal', 'expected_obligations': 14}, {'id': 'OPERATIONAL_CARDINALITY', 'proof_module': 'assurance/seed-recognition-boundary/formal/RecognitionOperationalCardinalityProofs.tla', 'final_theorem': 'SixRetainedHistoryClassesAreMinimal', 'expected_obligations': 190}, {'id': 'MACHINE_BINDABILITY', 'proof_module': 'assurance/seed-recognition-boundary/formal/MachineBindabilityProofs.tla', 'final_theorem': 'DifferentDecisionRequiresDifferentDescriptor', 'expected_obligations': 3}, {'id': 'DECISION_SUBJECT_BINDING', 'proof_module': 'assurance/seed-recognition-boundary/formal/DecisionSubjectBindingProofs.tla', 'final_theorem': 'DifferentGenesisChangesBinding', 'expected_obligations': 10}, {'id': 'MACHINE_DECISION_SUBJECT_BINDING', 'proof_module': 'assurance/seed-recognition-boundary/formal/MachineDecisionSubjectBindingProofs.tla', 'final_theorem': 'DifferentMachineDecisionProducesDifferentExactBinding', 'expected_obligations': 10}, {'id': 'SEED_RECOGNITION_CARDINALITY', 'proof_module': 'assurance/seed-recognition-boundary/formal/SeedRecognitionMinimalityProofs.tla', 'final_theorem': 'SeedRecognitionAlgebraMeetsCardinalityLowerBound', 'expected_obligations': 13}, {'id': 'GENESIS_ANCHORED_RECOGNITION', 'proof_module': 'assurance/seed-recognition-boundary/formal/GenesisAnchoredRecognitionProofs.tla', 'final_theorem': 'SpecImpliesNewApplicationRequiresAllow', 'expected_obligations': 35}, {'id': 'GENESIS_ANCHORED_TO_SEED', 'proof_module': 'assurance/seed-recognition-boundary/formal/GenesisAnchoredRecognitionSeedRefinementProofs.tla', 'final_theorem': 'GenesisAnchoredRecognitionRefinesSeedResolution', 'expected_obligations': 49}, {'id': 'INDEPENDENT_RECOGNITION_CONTRACT', 'proof_module': 'assurance/seed-recognition-boundary/formal/IndependentRecognitionContractProofs.tla', 'final_theorem': 'NativeCrossCreatesOnlyAdmittedApplication', 'expected_obligations': 22}, {'id': 'INDEPENDENT_PROJECTION_ADEQUACY', 'proof_module': 'assurance/seed-recognition-boundary/formal/IndependentProjectionAdequacyProofs.tla', 'final_theorem': 'A9ProjectedTraceCannotRollbackAlongSuppliedStep', 'expected_obligations': 13}, {'id': 'INDEPENDENT_TO_GCR_LIFTING', 'proof_module': 'assurance/seed-recognition-boundary/formal/IndependentRecognitionToGCRLiftingProofs.tla', 'final_theorem': 'IndependentRecognitionRefinesGCR', 'expected_obligations': 101}, {'id': 'MINIMAL_RECOGNITION_BOUNDARY', 'proof_module': 'assurance/seed-recognition-boundary/formal/MinimalRecognitionBoundaryProofs.tla', 'final_theorem': 'MinStatusRejectForRejectTerminal', 'expected_obligations': 12}, {'id': 'MINIMAL_BOUNDARY_TO_SEED', 'proof_module': 'assurance/seed-recognition-boundary/formal/MinimalRecognitionBoundaryToSeedRefinementProofs.tla', 'final_theorem': 'MinimalRecognitionBoundaryRefinesSeedResolution', 'expected_obligations': 189}, {'id': 'CANONICAL_PHASE_TO_SEED', 'proof_module': 'assurance/seed-recognition-boundary/formal/CanonicalPhaseSeedToSeedRefinementProofs.tla', 'final_theorem': 'CanonicalPhaseSeedRefinesSeedResolution', 'expected_obligations': 299}, {'id': 'SEED_TO_CANONICAL_PHASE', 'proof_module': 'assurance/seed-recognition-boundary/formal/SeedToCanonicalPhaseSeedRefinementProofs.tla', 'final_theorem': 'SeedResolutionRefinesCanonicalPhaseSeed', 'expected_obligations': 370}, {'id': 'PAYLOAD_OBSERVABILITY', 'proof_module': 'assurance/seed-recognition-boundary/formal/RecognitionPayloadObservabilityProofs.tla', 'final_theorem': 'PayloadObservationSummary', 'expected_obligations': 47}, {'id': 'INFORMATION_LOWER_BOUNDS', 'proof_module': 'assurance/seed-recognition-boundary/formal/RecognitionInformationLowerBoundsProofs.tla', 'final_theorem': 'RichProfileInformationLowerBounds', 'expected_obligations': 80}, {'id': 'PARAMETRIC_EXACT_CARDINALITY', 'proof_module': 'assurance/seed-recognition-boundary/formal/ParametricLocalStateCardinalityProofs.tla', 'final_theorem': 'ParametricCardinalitySummary', 'expected_obligations': 255}, {'id': 'CANONICAL_LOCAL_REACHABILITY', 'proof_module': 'assurance/seed-recognition-boundary/formal/CanonicalLocalReachabilityProofs.tla', 'final_theorem': 'CanonicalLocalReachabilityEquivalence', 'expected_obligations': 476}, {'id': 'REACHABLE_INFORMATION_BOUND', 'proof_module': 'assurance/seed-recognition-boundary/formal/CanonicalReachableInformationBoundProofs.tla', 'final_theorem': 'CanonicalReachableInformationBound', 'expected_obligations': 69}]


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def expected() -> dict[str, object]:
    rows = [{"path": path, "sha256": digest(ROOT / path)} for path in ASSURANCE_FILES]
    package_digest = "sha256:" + hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "document_type": "aset-seed-recognition-boundary-assurance-package",
        "schema_version": 2,
        "assurance_id": "ASET-SEED-RECOGNITION-BOUNDARY-ASSURANCE-V60",
        "publication_baseline": "ASET-SEED-SEMANTIC-MINIMALITY-V60",
        "status": "PUBLIC_NON_NORMATIVE_ASSURANCE",
        "normative": False,
        "normative_precedence": "NONE",
        "subject": {
            "canon_id": FROZEN_CANON_ID,
            "canon_version": FROZEN_CANON_VERSION,
            "canon_package_path": "seed/canonical/CANON_PACKAGE.json",
            "canon_package_file_sha256": FROZEN_CANON_PACKAGE_FILE_SHA256,
            "canon_package_digest": FROZEN_CANON_PACKAGE_DIGEST,
            "seed_model_path": "seed/canonical/source/seed-model.json",
            "seed_model_sha256": FROZEN_SEED_MODEL_SHA256,
            "seed_resolution_path": "seed/canonical/formal/SeedResolution.tla",
            "seed_resolution_sha256": FROZEN_SEED_RESOLUTION_SHA256,
            "canon_tla_refinement_path": "seed/canonical/assurance/canon-tla-refinement.json",
            "canon_tla_refinement_sha256": FROZEN_CANON_TLA_REFINEMENT_SHA256,
        },
        "publication_provenance": {
            "path": "assurance/seed-recognition-boundary/PUBLICATION_BASELINE.json",
            "sha256": FROZEN_PUBLICATION_BASELINE_SHA256,
            "source_v60_package_sha256": "sha256:397ddc656cac624a0d7bcbb18c575323399eb176ffa0f68b49f93f75ef9aae1c",
            "formal_edit_policy": "COMMENTS_AND_STATUS_WORDING_ONLY",
        },
        "relation_type": "EXTERNAL_ASSURANCE_PERIMETER_BOUND_TO_FROZEN_SEED",
        "active_tla_modules": 34,
        "proof_modules": 20,
        "proof_chain": PROOF_CHAIN,
        "expected_tlaps_obligations": sum(item["expected_obligations"] for item in PROOF_CHAIN),
        "claim_boundary": {
            "included": [
                "complete active v60 recognition-cardinality and boundary assurance corpus",
                "bidirectional refinement between CanonicalPhaseSeed and the pinned SeedResolution semantics over the declared reachable scope",
                "exact parametric per-resolution canonical state cardinality",
                "constructive local reachability equality with the exact normal form",
                "representation-independent finite faithful-code cardinality lower bound",
            ],
            "excluded": [
                "universal minimality among all possible systems",
                "minimum implementation variable or column count",
                "Shannon entropy or expected code length",
                "global Seed state bit size",
                "liveness",
                "cryptographic correctness",
                "implementation refinement without a separate implementation witness",
            ],
        },
        "files": rows,
        "package_digest": package_digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    content = json.dumps(expected(), sort_keys=True, indent=2) + "\n"
    if args.check:
        ok = MANIFEST.is_file() and MANIFEST.read_text(encoding="utf-8") == content
        print("SEED_RECOGNITION_BOUNDARY_ASSURANCE_PACKAGE=" + ("PASS" if ok else "DIFFERENT"))
        return 0 if ok else 1
    MANIFEST.write_text(content, encoding="utf-8", newline="\n")
    print("SEED_RECOGNITION_BOUNDARY_ASSURANCE_PACKAGE_BUILT=PASS")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

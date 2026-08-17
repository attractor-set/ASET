#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


class ReleaseAdmissionError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseAdmissionError(message)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def load_json(path: Path, expected_type: str) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path.name}: document must be an object")
    require(
        value.get("document_type") == expected_type,
        f"{path.name}: unexpected document type",
    )
    require(value.get("status") == "PASS", f"{path.name}: evidence is not PASS")
    return value


def check_release_admission(
    witness_path: Path,
    expression_evidence_path: Path,
    persistence_evidence_path: Path,
    release_proof_evidence_path: Path,
    release_root: Path,
    profiles_root: Path,
    release_archive: Path,
    profiles_archive: Path,
) -> dict[str, Any]:
    witness = load_json(
        witness_path,
        "aset-proof-derived-recognition-witnesses",
    )
    expression = load_json(
        expression_evidence_path,
        "aset-airgapped-expression-assurance-evidence",
    )
    persistence = load_json(
        persistence_evidence_path,
        "aset-python-sqlite-persistence-assurance-evidence",
    )
    release_proof = load_json(
        release_proof_evidence_path,
        "aset-release-assembled-tlaps-evidence",
    )

    release_manifest_path = release_root / "RELEASE_MANIFEST.json"
    profile_manifest_path = profiles_root / "RELEASE_PROFILE_MANIFEST.json"
    require(release_manifest_path.is_file(), "Seed release manifest missing")
    require(profile_manifest_path.is_file(), "release profile manifest missing")
    release_manifest = json.loads(release_manifest_path.read_text(encoding="utf-8"))
    profile_manifest = json.loads(profile_manifest_path.read_text(encoding="utf-8"))

    require(
        release_manifest.get("document_type") == "aset-seed-release-materialization",
        "unexpected Seed release manifest type",
    )
    require(
        profile_manifest.get("document_type")
        == "aset-ci-release-companion-materialization",
        "unexpected release profile manifest type",
    )
    require(
        profile_manifest.get("project") == "Authority-Seeded Evidence Trail (ASET)",
        "ASET project identity mismatch",
    )
    expected_algebra = {
        "id": "ASET_ALPHA",
        "name": "Local Recognition Algebra",
    }
    require(
        release_manifest.get("semantic_algebra") == expected_algebra,
        "Seed release semantic algebra identity mismatch",
    )
    require(
        profile_manifest.get("semantic_algebra") == expected_algebra,
        "release profile semantic algebra identity mismatch",
    )

    causal_expression = release_manifest.get("causal_expression")
    triangulated_assurance = release_manifest.get("triangulated_assurance")
    congruence_assurance = release_manifest.get("congruence_assurance")
    require(isinstance(causal_expression, dict), "causal release expression missing")
    require(
        causal_expression.get("semantic_delta") == "NONE"
        and causal_expression.get("semantic_precedence") == "NONE",
        "causal assurance representation changes Seed semantics",
    )
    require(
        isinstance(triangulated_assurance, dict),
        "triangulated release assurance missing",
    )
    require(
        triangulated_assurance.get("representations")
        == ["OPERATIONAL", "RELATIONAL", "CAUSAL"],
        "triangulated release representation set mismatch",
    )
    require(
        triangulated_assurance.get("semantic_delta") == "NONE"
        and triangulated_assurance.get("semantic_precedence") == "NONE",
        "triangulated assurance changes Seed semantics",
    )
    require(
        isinstance(congruence_assurance, dict),
        "release congruence assurance missing",
    )
    triangulated_evidence = congruence_assurance.get("triangulated_expression")
    require(
        isinstance(triangulated_evidence, dict)
        and triangulated_evidence.get("status") == "PASS"
        and triangulated_evidence.get("semantic_delta") == "NONE",
        "release triangulated congruence is not admitted",
    )

    representation_id = release_manifest.get("representation_id")
    require(representation_id == "0.4alpha", "release representation mismatch")
    require(
        profile_manifest.get("representation_id") == representation_id,
        "release profile representation mismatch",
    )

    release_tree_digest = tree_digest(release_root)
    profile_tree_digest = tree_digest(profiles_root)

    release_proof_binding = release_proof.get("release_binding")
    require(
        isinstance(release_proof_binding, dict),
        "post-build formal release binding missing",
    )
    require(
        release_proof_binding.get("tree_digest") == release_tree_digest,
        "post-build formal proof is bound to a different release tree",
    )
    release_proof_assembled = release_proof_binding.get("assembled_formal")
    require(
        isinstance(release_proof_assembled, dict),
        "post-build assembled formal binding missing",
    )
    assembled_path = release_root / "formal/AssembledSeed.tla"
    require(assembled_path.is_file(), "materialized AssembledSeed.tla missing")
    require(
        release_proof_assembled.get("path") == "formal/AssembledSeed.tla"
        and release_proof_assembled.get("sha256") == sha256(assembled_path),
        "post-build formal proof used different assembled bytes",
    )
    release_proof_subject = release_proof.get("proof")
    require(isinstance(release_proof_subject, dict), "post-build proof subject missing")
    require(
        release_proof_subject.get("final_theorem")
        == "AssembledNextPreservesExactSubjectAndAuthority",
        "post-build final theorem mismatch",
    )
    require(
        isinstance(release_proof_subject.get("obligations_proved"), int)
        and release_proof_subject["obligations_proved"] > 0,
        "post-build proof obligation count missing",
    )
    require(
        release_proof.get("scope") == "POST_BUILD_DEDUCTIVE_ASSURANCE"
        and release_proof.get("semantic_delta") == "NONE"
        and release_proof.get("semantic_source_runtime_dependency") == "NONE",
        "post-build proof boundary mismatch",
    )
    require(
        profile_manifest.get("seed_release_tree_digest") == release_tree_digest,
        "profile tree is not bound to exact Seed release tree",
    )

    witness_sha = sha256(witness_path)
    profile_witness = profile_manifest.get("proof_witness_artifact")
    require(isinstance(profile_witness, dict), "profile witness binding missing")
    require(
        profile_witness.get("sha256") == witness_sha,
        "profile witness binding differs from admitted witness artifact",
    )
    expression_inputs = expression.get("verifier_inputs")
    require(isinstance(expression_inputs, dict), "air-gap verifier inputs missing")
    airgap_witness = expression_inputs.get("proof_witness_artifact")
    airgap_expression = expression_inputs.get("expression_artifact")
    require(isinstance(airgap_witness, dict), "air-gap witness input missing")
    require(isinstance(airgap_expression, dict), "air-gap expression input missing")
    require(
        airgap_witness.get("sha256") == witness_sha,
        "air-gap verifier used a different witness artifact",
    )

    python_path = profiles_root / "python/aset_seed_alpha4.py"
    require(python_path.is_file(), "generated Python expression missing")
    python_sha = sha256(python_path)
    require(
        airgap_expression.get("sha256") == python_sha,
        "air-gap verifier used different Python expression bytes",
    )
    airgap_dependencies = expression.get("runtime_dependencies")
    require(
        isinstance(airgap_dependencies, dict)
        and airgap_dependencies.get("semantic_source") == "NONE"
        and airgap_dependencies.get("proof_materializer") == "NONE"
        and airgap_dependencies.get("expression_deriver") == "NONE"
        and airgap_dependencies.get("expression_import_surface") == "NONE"
        and airgap_dependencies.get("expression_file_access") == "NONE",
        "Python air-gap runtime isolation boundary drift",
    )

    persistence_base = persistence.get("base_expression_binding")
    persistence_extension = persistence.get("extension_binding")
    require(
        isinstance(persistence_base, dict),
        "persistence base expression binding missing",
    )
    require(
        isinstance(persistence_extension, dict),
        "persistence extension binding missing",
    )
    require(
        persistence_base.get("sha256") == python_sha,
        "persistence extension is not bound to admitted Python expression",
    )
    require(
        persistence.get("semantic_delta") == "NONE",
        "persistence extension declares semantic delta",
    )

    sqlite_path = profiles_root / str(persistence_extension.get("path", ""))
    require(sqlite_path.is_file(), "Python SQLite persistence extension missing")
    sqlite_sha = sha256(sqlite_path)
    require(
        persistence_extension.get("sha256") == sqlite_sha,
        "persistence evidence extension bytes differ",
    )

    materialization_boundary = persistence.get("materialization_boundary")
    require(
        isinstance(materialization_boundary, dict),
        "persistence materialization boundary missing",
    )
    require(
        materialization_boundary.get("profile_tree_unchanged") is True,
        "persistence gate mutated materialized profile tree",
    )
    require(
        materialization_boundary.get("python_bytecode_written") is False,
        "persistence gate wrote Python bytecode into materialized profile tree",
    )
    require(
        materialization_boundary.get("profile_tree_digest_before")
        == profile_tree_digest,
        "persistence gate checked a different profile tree",
    )
    require(
        materialization_boundary.get("profile_tree_digest_after")
        == profile_tree_digest,
        "profile tree changed after persistence assurance",
    )

    runtime = persistence.get("runtime")
    require(isinstance(runtime, dict), "persistence runtime evidence missing")
    require(runtime.get("status") == "PASS", "persistence runtime is not PASS")
    require(
        runtime.get("base_expression_congruence_cases") == 1824,
        "persistence base expression congruence coverage drifted",
    )
    require(
        runtime.get("restart_round_trip_components") == 6,
        "persistence restart coverage drifted",
    )
    require(
        isinstance(runtime.get("rollback_checks"), int)
        and runtime["rollback_checks"] > 0,
        "persistence rollback path was not exercised",
    )

    require(release_archive.is_file(), "Seed release archive missing")
    require(profiles_archive.is_file(), "release profile archive missing")

    return {
        "document_type": "aset-release-admission-certificate",
        "project": "Authority-Seeded Evidence Trail (ASET)",
        "semantic_algebra": {
            "id": "ASET_ALPHA",
            "name": "Local Recognition Algebra",
        },
        "subject_id": profile_manifest.get("subject_id"),
        "version": profile_manifest.get("version"),
        "representation_id": representation_id,
        "admission_relation": (
            "POST_BUILD_FORMAL_TO_PROOF_WITNESS_TO_PYTHON_AIRGAP_"
            "TO_EXACT_SQLITE_PERSISTENCE"
        ),
        "semantic_source_runtime_dependency": "NONE",
        "expression_deriver_runtime_dependency": "NONE",
        "evidence": {
            "triangulated_assurance": {
                "representations": ["OPERATIONAL", "RELATIONAL", "CAUSAL"],
                "components_checked": triangulated_evidence["components_checked"],
                "cases_checked": triangulated_evidence["cases_checked"],
                "causal_invariant": triangulated_evidence["causal_invariant"]["status"],
                "semantic_delta": "NONE",
            },
            "post_build_formal_assurance": {
                "path": release_proof_evidence_path.name,
                "sha256": sha256(release_proof_evidence_path),
                "release_tree_digest": release_tree_digest,
                "assembled_formal_sha256": sha256(assembled_path),
                "final_theorem": release_proof_subject["final_theorem"],
                "obligations_proved": release_proof_subject["obligations_proved"],
                "semantic_delta": "NONE",
                "status": "PASS",
            },
            "proof_witness": {
                "path": witness_path.name,
                "sha256": witness_sha,
            },
            "python_airgap": {
                "path": expression_evidence_path.name,
                "sha256": sha256(expression_evidence_path),
                "expression_sha256": python_sha,
                "cases_checked": expression["python"]["cases_checked"],
                "runtime_isolation": "PASS",
            },
            "python_sqlite_persistence": {
                "path": persistence_evidence_path.name,
                "sha256": sha256(persistence_evidence_path),
                "base_expression_sha256": python_sha,
                "extension_sha256": sqlite_sha,
                "base_expression_congruence_cases": runtime[
                    "base_expression_congruence_cases"
                ],
                "restart_round_trip_components": runtime[
                    "restart_round_trip_components"
                ],
                "rollback_checks": runtime["rollback_checks"],
                "semantic_delta": "NONE",
            },
        },
        "release": {
            "tree_digest": release_tree_digest,
            "archive_sha256": sha256(release_archive),
        },
        "profiles": {
            "tree_digest": profile_tree_digest,
            "archive_sha256": sha256(profiles_archive),
            "seed_release_tree_digest": release_tree_digest,
        },
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--witnesses", type=Path, required=True)
    parser.add_argument("--expression-evidence", type=Path, required=True)
    parser.add_argument("--persistence-evidence", type=Path, required=True)
    parser.add_argument("--release-proof-evidence", type=Path, required=True)
    parser.add_argument("--release-root", type=Path, required=True)
    parser.add_argument("--profiles-root", type=Path, required=True)
    parser.add_argument("--release-archive", type=Path, required=True)
    parser.add_argument("--profiles-archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        certificate = check_release_admission(
            args.witnesses,
            args.expression_evidence,
            args.persistence_evidence,
            args.release_proof_evidence,
            args.release_root,
            args.profiles_root,
            args.release_archive,
            args.profiles_archive,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(certificate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print("ALPHA4_RELEASE_ADMISSION_PROJECT=AUTHORITY_SEEDED_EVIDENCE_TRAIL")
        print("ALPHA4_RELEASE_ADMISSION_SEMANTIC_ALGEBRA=ASET_ALPHA")
        print("ALPHA4_RELEASE_ADMISSION_TRIANGULATED_ASSURANCE=PASS")
        print("ALPHA4_RELEASE_ADMISSION_POST_BUILD_TLAPS=PASS")
        print("ALPHA4_RELEASE_ADMISSION_CAUSAL_SEMANTIC_DELTA=NONE")
        print("ALPHA4_RELEASE_ADMISSION_PYTHON_AIRGAP=PASS")
        print("ALPHA4_RELEASE_ADMISSION_PYTHON_SQLITE_BASE_EXPRESSION=EXACT")
        print("ALPHA4_RELEASE_ADMISSION_PYTHON_SQLITE_SEMANTIC_DELTA=NONE")
        print("ALPHA4_RELEASE_ADMISSION_CERTIFICATE=PASS")
        return 0
    except (
        json.JSONDecodeError,
        KeyError,
        OSError,
        ReleaseAdmissionError,
        TypeError,
        ValueError,
    ) as error:
        print(f"ALPHA4_RELEASE_ADMISSION_ERROR={error}")
        print("ALPHA4_RELEASE_ADMISSION_CERTIFICATE=FAIL")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

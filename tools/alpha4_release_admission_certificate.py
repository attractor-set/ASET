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

    release_tree_digest = tree_digest(release_root)
    profile_tree_digest = tree_digest(profiles_root)
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

    persistence_parent = persistence.get("parent_binding")
    persistence_extension = persistence.get("extension_binding")
    require(isinstance(persistence_parent, dict), "persistence parent binding missing")
    require(
        isinstance(persistence_extension, dict),
        "persistence extension binding missing",
    )
    require(
        persistence_parent.get("sha256") == python_sha,
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
        runtime.get("parent_congruence_cases") == 1824,
        "persistence parent congruence coverage drifted",
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
        "line_id": profile_manifest.get("line_id"),
        "version": profile_manifest.get("version"),
        "admission_relation": (
            "PROOF_WITNESS_TO_PYTHON_AIRGAP_TO_EXACT_SQLITE_PERSISTENCE"
        ),
        "semantic_source_runtime_dependency": "NONE",
        "expression_deriver_runtime_dependency": "NONE",
        "evidence": {
            "proof_witness": {
                "path": witness_path.name,
                "sha256": witness_sha,
            },
            "python_airgap": {
                "path": expression_evidence_path.name,
                "sha256": sha256(expression_evidence_path),
                "expression_sha256": python_sha,
                "cases_checked": expression["python"]["cases_checked"],
            },
            "python_sqlite_persistence": {
                "path": persistence_evidence_path.name,
                "sha256": sha256(persistence_evidence_path),
                "parent_sha256": python_sha,
                "extension_sha256": sqlite_sha,
                "parent_congruence_cases": runtime["parent_congruence_cases"],
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
        print("ALPHA4_RELEASE_ADMISSION_PYTHON_AIRGAP=PASS")
        print("ALPHA4_RELEASE_ADMISSION_PYTHON_SQLITE_PARENT=EXACT")
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

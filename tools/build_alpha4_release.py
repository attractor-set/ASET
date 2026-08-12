#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

try:
    from tools.alpha4_binding_graph import parse_seed_bindings, write_binding_graph
    from tools.alpha4_congruence import check_release_congruence, write_evidence
    from tools.alpha4_paired_expression import write_release_graphs
    from tools.alpha4_release_profile_congruence import (
        check_release_profile_congruence,
        write_evidence as write_release_profile_evidence,
    )
    from tools.alpha4_release_profiles import build_release_profiles
except ModuleNotFoundError:
    from alpha4_binding_graph import parse_seed_bindings, write_binding_graph
    from alpha4_congruence import check_release_congruence, write_evidence
    from alpha4_paired_expression import write_release_graphs
    from alpha4_release_profile_congruence import (
        check_release_profile_congruence,
        write_evidence as write_release_profile_evidence,
    )
    from alpha4_release_profiles import build_release_profiles

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
RELEASE_NAME = "ASET-Seed-0.4alpha"
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def source_digest(paths: list[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(set(paths)):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update((ROOT / relative).read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def tracked_state() -> str | None:
    git = shutil.which("git")
    if git is None or not (ROOT / ".git").exists():
        return None
    result = subprocess.run(
        [git, "status", "--porcelain=v1", "--untracked-files=no"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout if result.returncode == 0 else None


def write_assembled_tla(target: Path) -> None:
    bindings = parse_seed_bindings(ROOT)
    lines = [
        "------------------------- MODULE AssembledSeed -------------------------",
        "EXTENDS ComponentRelations",
        "",
        "Next(s, t, e) ==",
    ]
    lines.extend(f"  \\/ {item.formal_operator}(s, t, e)" for item in bindings.pairs)
    lines += [
        "",
        "=============================================================================",
        "",
    ]
    target.write_text("\n".join(lines), encoding="utf-8")


def build_tree(output: Path) -> dict[str, object]:
    bindings = parse_seed_bindings(ROOT)
    if output.exists():
        shutil.rmtree(output)
    (output / "source").mkdir(parents=True)
    (output / "operational").mkdir(parents=True)
    (output / "formal").mkdir(parents=True)
    (output / "binding").mkdir(parents=True)
    (output / "expression/paired").mkdir(parents=True)

    shutil.copy2(ROOT / "LICENSE", output / "LICENSE")
    shutil.copy2(ROOT / "NOTICE", output / "NOTICE")
    shutil.copy2(ROOT / "seed/alpha4/SEED.aset", output / "source/SEED.aset")
    shutil.copy2(
        ROOT / bindings.abstract_machine, output / "operational/components.forth"
    )

    theory_sources = [
        bindings.foundation_model,
        bindings.foundation_proof.module,
        bindings.theory_algebra,
    ]
    for relative in theory_sources:
        source = ROOT / relative
        shutil.copy2(source, output / "formal" / source.name)
    formal_sources = [
        bindings.correctness_model,
        "seed/alpha4/formal/ComponentCompositionProofs.tla",
        bindings.formal_reflection,
        "seed/alpha4/formal/OperationalRelationalPairingProofs.tla",
    ]
    for relative in formal_sources:
        shutil.copy2(ROOT / relative, output / "formal" / Path(relative).name)
    write_assembled_tla(output / "formal/AssembledSeed.tla")

    shutil.copy2(ROOT / "seed/alpha4/binding/graph.cddl", output / "binding/graph.cddl")
    binding_evidence = write_binding_graph(ROOT, output / "binding/graph.cbor")
    write_release_graphs(ROOT, output / "expression/paired")

    congruence = check_release_congruence(ROOT, output)
    write_evidence(output / "CONGRUENCE_EVIDENCE.json", congruence)

    source_paths = [
        "seed/alpha4/SEED.aset",
        "seed/alpha4/binding/graph.cddl",
        bindings.abstract_machine,
        *formal_sources,
        *theory_sources,
    ]
    artifacts = [
        {"path": path.relative_to(output).as_posix(), "sha256": sha256(path)}
        for path in sorted(output.rglob("*"))
        if path.is_file()
    ]
    manifest: dict[str, object] = {
        "document_type": "aset-seed-release-materialization",
        "line_id": bindings.subject_id,
        "version": bindings.version,
        "compatibility_with_0_3": bindings.compatibility,
        "source_byte_identity_digest": source_digest(source_paths),
        "architecture": {
            "theory_algebra": bindings.theory_algebra,
            "minimality_theorem": bindings.foundation_proof.final_theorem,
            "abstract_machine": "operational/components.forth",
            "formal_reflection": Path(bindings.formal_reflection).name,
            "correctness_model": Path(bindings.correctness_model).name,
            "prediction_observation_relation": bindings.relation_map()[
                "PAIRED_RUNTIME"
            ],
        },
        "binding_graph": {
            **binding_evidence,
            "path": "binding/graph.cbor",
            "schema": "binding/graph.cddl",
        },
        "integrity_policy": {
            "primary_relation": "DECLARED_CONTENT_CONGRUENCE",
            "digest_role": bindings.digest_role,
            "evidence": "CONGRUENCE_EVIDENCE.json",
            "checker": "tools/alpha4_congruence.py",
        },
        "paired_expression": {
            "operational_graph": "expression/paired/operational-graph.json",
            "relational_graph": "expression/paired/relational-graph.json",
            "jit_materialization": "EPHEMERAL_IN_MEMORY",
            "reference_materialization": "RELATIONAL_GRAPH_INTERPRETER",
            "prediction_source": "THEORY_CONSTRAINED_RELATIONAL_CORRECTNESS_MODEL",
            "observation_source": "ABSTRACT_FORTH_MACHINE_EPHEMERAL_JIT",
            "semantic_precedence": "NONE",
        },
        "formal_assurance_requirement": {
            "subjects": [
                {
                    "id": item.proof_id,
                    "module": item.module,
                    "expected_obligations": item.expected_obligations,
                    "final_theorem": item.final_theorem,
                }
                for item in bindings.all_proofs
            ],
            "runner": "tools/run_alpha4_tlaps.py",
            "required_for_release_gate": True,
        },
        "congruence_assurance": congruence,
        "artifacts": artifacts,
    }
    (output / "RELEASE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            digest.update(relative.encode("utf-8"))
            digest.update(b"\0")
            digest.update(path.read_bytes())
            digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def zip_tree(root: Path, output: Path, archive_root_name: str) -> None:
    if output.exists():
        output.unlink()
    with zipfile.ZipFile(
        output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
    ) as archive:
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            relative = f"{archive_root_name}/{path.relative_to(root).as_posix()}"
            info = zipfile.ZipInfo(relative, FIXED_ZIP_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes())


def write_inpi_hash(archive: Path) -> Path:
    target_dir = DIST / "inpi"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{archive.name}.sha256"
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    target.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    return target


def build_profiles_tree(
    output: Path,
    seed_release_tree_digest: str,
    proof_witnesses: Path,
) -> dict[str, object]:
    bindings = parse_seed_bindings(ROOT)
    if not proof_witnesses.is_file():
        raise RuntimeError("materialized proof witness artifact missing")
    build_release_profiles(ROOT, output)
    witness_target = output / "assurance/proof-witnesses.json"
    witness_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(proof_witnesses, witness_target)
    congruence = check_release_profile_congruence(ROOT, output)
    write_release_profile_evidence(output / "RELEASE_PROFILE_EVIDENCE.json", congruence)
    artifacts = [
        {"path": path.relative_to(output).as_posix(), "sha256": sha256(path)}
        for path in sorted(output.rglob("*"))
        if path.is_file()
    ]
    manifest: dict[str, object] = {
        "document_type": "aset-ci-release-companion-materialization",
        "project": "Authority-Seeded Evidence Trail (ASET)",
        "line_id": bindings.subject_id,
        "version": bindings.version,
        "seed_membership": "EXTERNAL_RELEASE_COMPANION",
        "semantic_precedence": "NONE",
        "seed_release_tree_digest": seed_release_tree_digest,
        "profiles": {
            "controlled_english": "en/Seed.md",
            "python": "python/aset_seed_alpha4.py",
            "python_sqlite": {
                "role": "PERSISTENCE_EXTENSION",
                "parent": "python",
                "semantic_delta": "NONE",
                "path": "python-sqlite/aset_seed_alpha4_sqlite.py",
                "binding": "python-sqlite/PERSISTENCE_EXTENSION.json",
                "assurance": "EXTERNAL_PERSISTENCE_PROFILE_GATE_REQUIRED",
            },
        },
        "proof_witness_artifact": {
            "path": "assurance/proof-witnesses.json",
            "sha256": sha256(witness_target),
            "role": "INDEPENDENT_PROOF_DERIVED_EXPRESSION_ORACLE",
        },
        "congruence_evidence": "RELEASE_PROFILE_EVIDENCE.json",
        "artifacts": artifacts,
    }
    (output / "RELEASE_PROFILE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest


def smoke_python(path: Path) -> None:
    namespace: dict[str, object] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), namespace)
    make_state = namespace.get("state")
    apply_component = namespace.get("apply_component")
    if not callable(make_state) or not callable(apply_component):
        raise RuntimeError("generated Python entry points missing")
    current = make_state("subject-1", "authority-1")
    current = apply_component(
        current, "ASET-COMPONENT-OBSERVE-UNKNOWN", evidence="evidence-1"
    )
    current = apply_component(
        current,
        "ASET-COMPONENT-RECOGNIZE-ALLOW",
        evidence="evidence-1",
        authority_recognition=frozenset(
            {("authority-1", "subject-1", "evidence-1", "ALLOW")}
        ),
    )
    if current["recognition"] != "ALLOW":
        raise RuntimeError("generated Python smoke check failed")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify-determinism", action="store_true")
    parser.add_argument(
        "--proof-witnesses",
        type=Path,
        default=DIST / "proof-derived-recognition-witnesses.json",
    )
    args = parser.parse_args(argv)
    proof_witnesses = (
        args.proof_witnesses
        if args.proof_witnesses.is_absolute()
        else ROOT / args.proof_witnesses
    )

    validation = subprocess.run(
        [sys.executable, "tools/validate_alpha4_seed.py"],
        cwd=ROOT,
        check=False,
    )
    if validation.returncode:
        print("ALPHA4_RELEASE_BUILD=FAIL")
        return validation.returncode

    before = tracked_state()
    release_dir = DIST / RELEASE_NAME
    manifest = build_tree(release_dir)
    congruence = manifest["congruence_assurance"]
    if not isinstance(congruence, dict) or congruence.get("status") != "PASS":
        print("ALPHA4_RELEASE_BUILD=FAIL")
        return 1
    digest = tree_digest(release_dir)

    profiles_name = f"{RELEASE_NAME}-profiles"
    profiles_dir = DIST / profiles_name
    if not proof_witnesses.is_file():
        print("ALPHA4_RELEASE_PROOF_WITNESS_INPUT=FAIL")
        print("ALPHA4_RELEASE_BUILD=FAIL")
        return 1

    profile_manifest = build_profiles_tree(profiles_dir, digest, proof_witnesses)
    profile_evidence = check_release_profile_congruence(ROOT, profiles_dir)
    if profile_evidence.get("status") != "PASS":
        print("ALPHA4_RELEASE_PROFILE_CONGRUENCE=FAIL")
        return 1
    smoke_python(profiles_dir / "python/aset_seed_alpha4.py")
    profile_digest = tree_digest(profiles_dir)

    if args.verify_determinism:
        with tempfile.TemporaryDirectory(prefix="aset-alpha4-") as tmp:
            first = Path(tmp) / "first"
            second = Path(tmp) / "second"
            first_profiles = Path(tmp) / "first-profiles"
            second_profiles = Path(tmp) / "second-profiles"
            build_tree(first)
            build_tree(second)
            first_digest = tree_digest(first)
            second_digest = tree_digest(second)
            if first_digest != second_digest:
                print("ALPHA4_RELEASE_DETERMINISM=FAIL")
                return 1
            build_profiles_tree(first_profiles, first_digest, proof_witnesses)
            build_profiles_tree(second_profiles, second_digest, proof_witnesses)
            if tree_digest(first_profiles) != tree_digest(second_profiles):
                print("ALPHA4_RELEASE_PROFILE_DETERMINISM=FAIL")
                return 1
        print("ALPHA4_RELEASE_DETERMINISM=PASS")
        print("ALPHA4_RELEASE_PROFILE_DETERMINISM=PASS")

    archive = DIST / f"{RELEASE_NAME}.zip"
    profiles_archive = DIST / f"{profiles_name}.zip"
    zip_tree(release_dir, archive, RELEASE_NAME)
    zip_tree(profiles_dir, profiles_archive, profiles_name)
    inpi_hash_file = write_inpi_hash(archive)
    after = tracked_state()
    if before is not None and after != before:
        print("ALPHA4_TRACKED_TREE_UNCHANGED=FAIL")
        return 1

    assembled = congruence["assembled_formal"]
    paired = congruence["paired_expression"]
    english = profile_evidence["english"]
    print("ALPHA4_SOURCE_CONTENT_CONGRUENCE=PASS")
    assembled_count = assembled["components_checked"]
    print(
        f"ALPHA4_ASSEMBLED_FORMAL_CONGRUENCE={assembled_count}/{assembled_count} PASS"
    )
    paired_count = paired["components_checked"]
    print(f"ALPHA4_PAIRED_GRAPH_CONGRUENCE={paired_count}/{paired_count} PASS")
    paired_cases = paired["cases_checked"]
    print(f"ALPHA4_JIT_REFERENCE_CONGRUENCE={paired_cases}/{paired_cases} PASS")
    print(f"ALPHA4_THEORY_PREDICTION_OBSERVATION={paired_cases}/{paired_cases} PASS")
    print("ALPHA4_CONTENT_CONGRUENCE=PASS")
    english_count = english["components_checked"]
    print(
        "ALPHA4_RELEASE_ENGLISH_PROFILE_CONGRUENCE="
        f"{english_count}/{english_count} PASS"
    )
    print("ALPHA4_RELEASE_PYTHON_EXPRESSION_ASSURANCE=EXTERNAL_AIRGAP_REQUIRED")
    print("ALPHA4_RELEASE_PYTHON_SQLITE_RELATION=PERSISTENCE_EXTENSION_OF_PYTHON")
    print("ALPHA4_RELEASE_PYTHON_SQLITE_SEMANTIC_DELTA=NONE")
    print("ALPHA4_RELEASE_PYTHON_SQLITE_ASSURANCE=EXTERNAL_PERSISTENCE_GATE_REQUIRED")
    print("ALPHA4_RELEASE_PROFILE_CONGRUENCE=PASS")
    print(
        f"ALPHA4_SOURCE_BYTE_IDENTITY_DIGEST={manifest['source_byte_identity_digest']}"
    )
    print(f"ALPHA4_RELEASE_TREE_DIGEST={digest}")
    print(f"ALPHA4_RELEASE_ARCHIVE={archive.relative_to(ROOT)}")
    print(f"ALPHA4_RELEASE_ARCHIVE_SHA256={sha256(archive)}")
    print(f"ALPHA4_INPI_DEPOSIT_ARTIFACT={archive.relative_to(ROOT)}")
    print("ALPHA4_INPI_DEPOSIT_ALGORITHM=SHA-256")
    print(f"ALPHA4_INPI_DEPOSIT_SHA256={sha256(archive)}")
    print(f"ALPHA4_INPI_DEPOSIT_HASH_FILE={inpi_hash_file.relative_to(ROOT)}")
    print(f"ALPHA4_RELEASE_PROFILE_TREE_DIGEST={profile_digest}")
    print(f"ALPHA4_RELEASE_PROFILE_ARCHIVE={profiles_archive.relative_to(ROOT)}")
    print(f"ALPHA4_RELEASE_PROFILE_ARCHIVE_SHA256={sha256(profiles_archive)}")
    print(
        f"ALPHA4_RELEASE_PROFILE_SEED_BINDING={profile_manifest['seed_release_tree_digest']}"
    )
    print("ALPHA4_TRACKED_TREE_UNCHANGED=PASS")
    print("ALPHA4_GENERATED_PYTHON_SMOKE=PASS")
    print("ALPHA4_EPHEMERAL_JIT_VALIDATION=PASS")
    print("ALPHA4_RELEASE_BUILD=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

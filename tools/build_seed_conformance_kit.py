#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "standards/seed-compatibility/compatibility-standard-profile-v1.json"
RELEASE_SCHEMA_PATH = (
    ROOT / "standards/seed-compatibility/compatibility-standard-release.schema.json"
)


def git(*args: str) -> bytes:
    completed = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.decode("utf-8", errors="replace").strip())
    return completed.stdout


def load_json_bytes(data: bytes) -> dict[str, Any]:
    value = json.loads(data.decode("utf-8"))
    if not isinstance(value, dict):
        raise ValueError("JSON document must be an object")
    return value


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def prefixed_sha256(data: bytes) -> str:
    return "sha256:" + sha256_bytes(data)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def git_blob(ref: str, path: str) -> bytes:
    return git("show", f"{ref}:{path}")


def git_mode_and_oid(ref: str, path: str) -> tuple[str, str]:
    raw = git("ls-tree", ref, "--", path).decode("utf-8").strip()
    if not raw:
        raise RuntimeError(f"release source file missing:{path}")
    metadata, listed = raw.split("\t", 1)
    if listed != path:
        raise RuntimeError(f"release source identity mismatch:{path}")
    mode, object_type, oid = metadata.split(" ", 2)
    if object_type != "blob":
        raise RuntimeError(f"release source is not a blob:{path}")
    return mode, oid


def is_exact_release_tag(ref: str) -> bool:
    if not ref.startswith("seed-"):
        return False
    completed = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/tags/{ref}"],
        cwd=ROOT,
        check=False,
    )
    return completed.returncode == 0


def release_version(ref: str, commit: str) -> str:
    if is_exact_release_tag(ref):
        return ref.removeprefix("seed-")
    return f"candidate-{commit[:12]}"


def verify_package(ref: str, package: dict[str, Any]) -> list[dict[str, object]]:
    rows = package.get("files")
    if not isinstance(rows, list) or not rows:
        raise RuntimeError("canonical package files are missing")
    normalized: list[dict[str, object]] = []
    digest_rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise RuntimeError("canonical package row must be an object")
        path = str(row["path"])
        expected = str(row["sha256"])
        if path in seen:
            raise RuntimeError(f"duplicate canonical package path:{path}")
        seen.add(path)
        data = git_blob(ref, path)
        actual = prefixed_sha256(data)
        if actual != expected:
            raise RuntimeError(f"canonical package file digest mismatch:{path}")
        mode, oid = git_mode_and_oid(ref, path)
        normalized.append(
            {
                "git_blob_oid": oid,
                "git_mode": mode,
                "path": path,
                "sha256": actual,
                "size_bytes": len(data),
                "source": "release-canon",
            }
        )
        digest_rows.append({"path": path, "sha256": expected})
    calculated = "sha256:" + hashlib.sha256(
        json.dumps(digest_rows, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    if calculated != package.get("package_digest"):
        raise RuntimeError("canonical package digest mismatch")
    return normalized


def standard_identity(
    ref: str,
    commit: str,
    version: str,
    package: dict[str, Any],
    profile: dict[str, Any],
) -> dict[str, Any]:
    if not is_exact_release_tag(ref):
        raise RuntimeError("compatibility standard identity requires an exact seed-* release tag")
    semantic = load_json_bytes(git_blob(ref, profile["release_binding"]["semantic_source_path"]))
    conformance_data = git_blob(ref, profile["release_binding"]["conformance_profile_path"])
    conformance = load_json_bytes(conformance_data)
    protocol = load_json_bytes(
        git_blob(ref, profile["release_binding"]["implementation_protocol_path"])
    )
    return {
        "canonical_package_digest": package["package_digest"],
        "canon_id": package["canon_id"],
        "canon_version": package["canon_version"],
        "conformance_profile_sha256": prefixed_sha256(conformance_data),
        "conformance_protocol": protocol["protocol_id"],
        "document_type": "aset-seed-compatibility-standard-release",
        "implementation_precedence": "NONE",
        "mandatory_conformance_cases": int(conformance["case_count"]),
        "normative_source": {
            "package_path": profile["release_binding"]["canonical_package_path"],
            "release_commit": commit,
            "release_tag": ref,
        },
        "release_commit": commit,
        "release_tag": ref,
        "release_version": version,
        "schema_version": 1,
        "seed_semantic_version": str(semantic["version"]),
        "standard_id": f"{profile['standard_series_id']}@{ref}",
        "standard_profile_id": profile["profile_id"],
        "standard_profile_sha256": prefixed_sha256(PROFILE_PATH.read_bytes()),
        "standard_series_id": profile["standard_series_id"],
        "verdict_authority": profile["conformance_claim"]["verdict_authority"],
    }


def validate_standard(value: dict[str, Any]) -> None:
    schema = json.loads(RELEASE_SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        rendered = "; ".join(
            f"/{'/'.join(str(part) for part in error.absolute_path)}:{error.message}"
            for error in errors
        )
        raise RuntimeError(f"compatibility standard identity schema failure:{rendered}")


def generated_readme(standard: dict[str, Any]) -> bytes:
    return (
        f"# ASET Seed {standard['release_version']} Conformance Kit\n\n"
        f"Standard: `{standard['standard_id']}`\n\n"
        f"Release target: `{standard.get('release_tag', standard.get('release_ref'))}`\n\n"
        f"Release commit: `{standard['release_commit']}`\n\n"
        f"Canonical package: `{standard['canonical_package_digest']}`\n\n"
        f"Conformance protocol: `{standard['conformance_protocol']}`\n\n"
        f"Mandatory cases: `{standard['mandatory_conformance_cases']}`\n\n"
        "The exact machine-readable canon copied from the bound release is normative. "
        "The kit is a deterministic distribution and does not amend Seed semantics.\n\n"
        "## Run an implementation\n\n"
        "Install the runner dependency and execute the implementation adapter:\n\n"
        "```text\n"
        "python -m pip install -r requirements-conformance.txt\n"
        "python tools/run_external_conformance.py --canon-root . --adapter '<adapter command>'\n"
        "```\n\n"
        "A conformance claim requires every mandatory case to PASS. The external ASET "
        "runner, not the implementation adapter, determines the verdict.\n"
    ).encode()


def archive_entries(
    ref: str,
    package_records: list[dict[str, object]],
    profile: dict[str, Any],
    standard_bytes: bytes,
) -> tuple[list[dict[str, object]], dict[str, bytes]]:
    records = list(package_records)
    blobs: dict[str, bytes] = {
        str(row["path"]): git_blob(ref, str(row["path"])) for row in package_records
    }
    existing = set(blobs)
    for path in profile["distribution"]["support_files"]:
        if path in existing:
            continue
        data = git_blob(ref, path)
        mode, oid = git_mode_and_oid(ref, path)
        blobs[path] = data
        records.append(
            {
                "git_blob_oid": oid,
                "git_mode": mode,
                "path": path,
                "sha256": prefixed_sha256(data),
                "size_bytes": len(data),
                "source": "release-support",
            }
        )
        existing.add(path)

    generated: dict[str, bytes] = {
        "STANDARD.json": standard_bytes,
        "STANDARD-PROFILE.json": PROFILE_PATH.read_bytes(),
        "STANDARD-SCHEMA.json": RELEASE_SCHEMA_PATH.read_bytes(),
        "README.md": generated_readme(json.loads(standard_bytes.decode("utf-8"))),
        "requirements-conformance.txt": (
            "\n".join(profile["runner_dependencies"]) + "\n"
        ).encode(),
    }
    expected_generated = set(profile["distribution"]["generated_entries"])
    actual_generated = set(generated) | {"KIT-MANIFEST.json"}
    if expected_generated != actual_generated:
        raise RuntimeError("compatibility profile generated-entry contract mismatch")

    for path, data in generated.items():
        records.append(
            {
                "git_mode": "100644",
                "path": path,
                "sha256": prefixed_sha256(data),
                "size_bytes": len(data),
                "source": "generated-distribution",
            }
        )
        blobs[path] = data

    records = sorted(records, key=lambda row: str(row["path"]))
    manifest = {
        "document_type": "aset-seed-conformance-kit-manifest",
        "files": records,
        "files_count": len(records),
        "schema_version": 1,
        "standard_sha256": prefixed_sha256(standard_bytes),
    }
    manifest_bytes = canonical_json(manifest)
    blobs["KIT-MANIFEST.json"] = manifest_bytes
    records.append(
        {
            "git_mode": "100644",
            "path": "KIT-MANIFEST.json",
            "sha256": prefixed_sha256(manifest_bytes),
            "size_bytes": len(manifest_bytes),
            "source": "generated-distribution",
        }
    )
    return sorted(records, key=lambda row: str(row["path"])), blobs


def build_zip(
    destination: Path,
    prefix: str,
    records: list[dict[str, object]],
    blobs: dict[str, bytes],
) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED) as archive:
        for row in records:
            path = str(row["path"])
            data = blobs[path]
            info = zipfile.ZipInfo(prefix + path, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = int(str(row["git_mode"]), 8) << 16
            archive.writestr(info, data)


def verify_zip(
    path: Path,
    prefix: str,
    records: list[dict[str, object]],
    blobs: dict[str, bytes],
) -> bool:
    names = [prefix + str(row["path"]) for row in records]
    with zipfile.ZipFile(path, "r") as archive:
        if archive.namelist() != names:
            return False
        return all(
            archive.read(prefix + str(row["path"])) == blobs[str(row["path"])]
            for row in records
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--verify-determinism", action="store_true")
    parser.add_argument("--require-release-tag", action="store_true")
    args = parser.parse_args()

    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    if profile.get("hash_algorithm") != "SHA-256":
        raise RuntimeError("unsupported compatibility profile hash algorithm")
    archive_rules = profile["distribution"]["archive"]
    if archive_rules.get("compression") != "ZIP_STORED":
        raise RuntimeError("unsupported compatibility profile compression")
    if archive_rules.get("fixed_timestamp") != "1980-01-01T00:00:00Z":
        raise RuntimeError("unsupported compatibility profile timestamp")
    if archive_rules.get("create_system") != 3:
        raise RuntimeError("unsupported compatibility profile create_system")
    if archive_rules.get("preserve_git_mode") is not True:
        raise RuntimeError("compatibility profile must preserve git mode")
    commit = git("rev-parse", f"{args.ref}^{{commit}}").decode().strip()
    exact_tag = is_exact_release_tag(args.ref)
    if args.require_release_tag and not exact_tag:
        print("SEED_COMPATIBILITY_STANDARD_RELEASE_TAG=FAIL")
        return 1

    package_path = profile["release_binding"]["canonical_package_path"]
    package = load_json_bytes(git_blob(args.ref, package_path))
    package_records = verify_package(args.ref, package)
    version = release_version(args.ref, commit)

    if exact_tag:
        standard = standard_identity(args.ref, commit, version, package, profile)
        validate_standard(standard)
        standard_bytes = canonical_json(standard)
    else:
        semantic = load_json_bytes(
            git_blob(args.ref, profile["release_binding"]["semantic_source_path"])
        )
        conformance_data = git_blob(
            args.ref, profile["release_binding"]["conformance_profile_path"]
        )
        conformance = load_json_bytes(conformance_data)
        protocol = load_json_bytes(
            git_blob(args.ref, profile["release_binding"]["implementation_protocol_path"])
        )
        standard = {
            "document_type": "aset-seed-compatibility-standard-candidate",
            "canonical_package_digest": package["package_digest"],
            "canon_id": package["canon_id"],
            "canon_version": package["canon_version"],
            "conformance_profile_sha256": prefixed_sha256(conformance_data),
            "conformance_protocol": protocol["protocol_id"],
            "implementation_precedence": "NONE",
            "mandatory_conformance_cases": int(conformance["case_count"]),
            "release_commit": commit,
            "release_ref": args.ref,
            "release_version": version,
            "seed_semantic_version": str(semantic["version"]),
            "standard_id": f"{profile['standard_series_id']}@{version}",
            "standard_profile_id": profile["profile_id"],
            "standard_profile_sha256": prefixed_sha256(PROFILE_PATH.read_bytes()),
            "standard_series_id": profile["standard_series_id"],
            "verdict_authority": profile["conformance_claim"]["verdict_authority"],
        }
        standard_bytes = canonical_json(standard)

    records, blobs = archive_entries(args.ref, package_records, profile, standard_bytes)
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    basename = f"ASET-Seed-{version}-Conformance-Kit"
    archive = output / f"{basename}.zip"
    build1 = output / f".{basename}.build-1.zip"
    build2 = output / f".{basename}.build-2.zip"
    prefix = profile["distribution"]["archive"]["path_prefix_template"].format(
        release_version=version
    )

    build_zip(build1, prefix, records, blobs)
    first = sha256_file(build1)
    if args.verify_determinism:
        build_zip(build2, prefix, records, blobs)
        second = sha256_file(build2)
        print(f"SEED_CONFORMANCE_KIT_BUILD_1_SHA256={first}")
        print(f"SEED_CONFORMANCE_KIT_BUILD_2_SHA256={second}")
        if first != second:
            print("SEED_CONFORMANCE_KIT_DETERMINISTIC_REBUILD=FAIL")
            return 1
        print("SEED_CONFORMANCE_KIT_DETERMINISTIC_REBUILD=PASS")
        build2.unlink(missing_ok=True)

    build1.replace(archive)
    if not verify_zip(archive, prefix, records, blobs):
        print("SEED_CONFORMANCE_KIT_BYTE_VERIFICATION=FAIL")
        return 1
    print("SEED_CONFORMANCE_KIT_BYTE_VERIFICATION=PASS")

    digest = sha256_file(archive)
    digest_path = output / f"{basename}.zip.sha256"
    manifest_path = output / f"{basename}.manifest.json"
    standard_path = output / f"ASET-Seed-{version}-Compatibility-Standard.json"
    digest_path.write_text(f"{digest}  {archive.name}\n", encoding="utf-8")
    standard_path.write_bytes(standard_bytes)
    manifest_path.write_text(
        json.dumps(
            {
                "archive": archive.name,
                "archive_sha256": digest,
                "document_type": "aset-seed-conformance-kit-release-manifest",
                "files": records,
                "files_count": len(records),
                "release_commit": commit,
                "release_ref": args.ref,
                "schema_version": 1,
                "standard_identity": standard_path.name,
                "standard_identity_sha256": prefixed_sha256(standard_bytes),
                "standard_profile_id": profile["profile_id"],
                "standard_profile_sha256": prefixed_sha256(PROFILE_PATH.read_bytes()),
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"SEED_COMPATIBILITY_STANDARD_PROFILE={profile['profile_id']}")
    print(f"SEED_COMPATIBILITY_RELEASE_REF={args.ref}")
    print(f"SEED_COMPATIBILITY_RELEASE_COMMIT={commit}")
    print(f"SEED_COMPATIBILITY_CANON_PACKAGE={package['package_digest']}")
    print(f"SEED_CONFORMANCE_KIT_FILES={len(records)}")
    print(f"SEED_CONFORMANCE_KIT_ARCHIVE={archive}")
    print(f"SEED_CONFORMANCE_KIT_SHA256={digest}")
    print("SEED_CONFORMANCE_KIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

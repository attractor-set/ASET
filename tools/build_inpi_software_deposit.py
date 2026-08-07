#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "tools/registration/inpi-software-deposit-profile-v1.json"


def git(*args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def load_profile() -> dict[str, Any]:
    value = json.loads(PROFILE.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("deposit profile must be an object")
    return value


def semantic_version(ref: str) -> str:
    raw = git("show", f"{ref}:seed/canonical/source/seed-model.json")
    value = json.loads(raw.decode("utf-8"))
    return str(value["version"])


def release_version(ref: str, semantic: str) -> str:
    short = ref.removeprefix("refs/tags/")
    if short.startswith("seed-") and len(short) > len("seed-"):
        return short[len("seed-") :]
    return semantic


def enumerate_files(ref: str, selectors: list[str]) -> list[dict[str, str]]:
    raw = git("ls-tree", "-r", ref, "--", *selectors).decode("utf-8")
    entries: list[dict[str, str]] = []
    for line in raw.splitlines():
        if not line.strip():
            continue
        metadata, path = line.split("\t", 1)
        mode, object_type, oid = metadata.split(" ", 2)
        if object_type == "blob":
            entries.append({"mode": mode, "oid": oid, "path": path})
    return sorted(entries, key=lambda item: item["path"])


def build_zip(
    destination: Path,
    ref: str,
    prefix: str,
    entries: list[dict[str, str]],
    collect_manifest: bool,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_STORED) as archive:
        for entry in entries:
            path = entry["path"]
            data = git("show", f"{ref}:{path}")
            info = zipfile.ZipInfo(prefix + path, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.compress_type = zipfile.ZIP_STORED
            info.external_attr = int(entry["mode"], 8) << 16
            archive.writestr(info, data)
            if collect_manifest:
                records.append(
                    {
                        "git_blob_oid": entry["oid"],
                        "git_mode": entry["mode"],
                        "path": path,
                        "sha256": sha256_bytes(data),
                        "size_bytes": len(data),
                    }
                )
    return records


def verify_archive(
    archive_path: Path, ref: str, prefix: str, entries: list[dict[str, str]]
) -> bool:
    expected_names = [prefix + item["path"] for item in entries]
    with zipfile.ZipFile(archive_path, "r") as archive:
        if archive.namelist() != expected_names:
            return False
        return all(
            archive.read(prefix + item["path"]) == git("show", f"{ref}:{item['path']}")
            for item in entries
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ref", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--verify-determinism", action="store_true")
    args = parser.parse_args()

    profile = load_profile()
    ref = args.ref
    commit = git("rev-parse", f"{ref}^{{commit}}").decode().strip()
    semantic = semantic_version(ref)
    version = release_version(ref, semantic)
    selectors = list(profile["source"]["selectors"])
    entries = enumerate_files(ref, selectors)
    if not entries:
        print("INPI_DEPOSIT_SOURCE_ENUMERATION=FAIL")
        return 1

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    basename = f"ASET-Seed-{version}-INPI-deposit"
    final_archive = output / f"{basename}.zip"
    build1 = output / f".{basename}.build-1.zip"
    build2 = output / f".{basename}.build-2.zip"
    prefix = profile["archive"]["path_prefix_template"].format(
        release_version=version, semantic_version=semantic
    )

    records = build_zip(build1, ref, prefix, entries, collect_manifest=True)
    first = sha256_file(build1)
    if args.verify_determinism:
        build_zip(build2, ref, prefix, entries, collect_manifest=False)
        second = sha256_file(build2)
        print(f"INPI_DEPOSIT_BUILD_1_SHA256={first}")
        print(f"INPI_DEPOSIT_BUILD_2_SHA256={second}")
        if first != second:
            print("INPI_DEPOSIT_DETERMINISTIC_REBUILD=FAIL")
            return 1
        print("INPI_DEPOSIT_DETERMINISTIC_REBUILD=PASS")
        build2.unlink(missing_ok=True)

    build1.replace(final_archive)
    if not verify_archive(final_archive, ref, prefix, entries):
        print("INPI_DEPOSIT_BYTE_VERIFICATION=FAIL")
        return 1
    print("INPI_DEPOSIT_BYTE_VERIFICATION=PASS")

    digest = sha256_file(final_archive)
    hash_path = output / f"{basename}.zip.sha256"
    manifest_path = output / f"ASET-Seed-{version}-INPI-source-manifest.json"
    worksheet_path = output / f"ASET-Seed-{version}-INPI-submission-worksheet.json"
    hash_path.write_text(f"{digest}  {final_archive.name}\n", encoding="utf-8")
    manifest_path.write_text(
        json.dumps(
            {
                "archive": final_archive.name,
                "archive_sha256": digest,
                "document_type": "aset-inpi-software-source-manifest",
                "files": records,
                "files_count": len(records),
                "profile_id": profile["profile_id"],
                "release_commit": commit,
                "release_ref": ref,
                "release_version": version,
                "seed_semantic_version": semantic,
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    worksheet_path.write_text(
        json.dumps(
            {
                "artifact": f"ASET Seed {version}",
                "deposit_archive": final_archive.name,
                "document_type": "aset-inpi-software-submission-worksheet",
                "hash_algorithm": profile["hash_algorithm"],
                "profile_id": profile["profile_id"],
                "release_commit": commit,
                "release_ref": ref,
                "resumo_digital_hash": digest,
                "release_version": version,
                "seed_semantic_version": semantic,
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"INPI_DEPOSIT_PROFILE={profile['profile_id']}")
    print(f"INPI_DEPOSIT_RELEASE_COMMIT={commit}")
    print(f"INPI_DEPOSIT_SOURCE_FILES={len(records)}")
    print(f"INPI_DEPOSIT_ARCHIVE={final_archive}")
    print(f"INPI_DEPOSIT_SHA256={digest}")
    print("INPI_DEPOSIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

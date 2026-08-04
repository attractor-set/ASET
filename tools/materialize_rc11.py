from __future__ import annotations

import argparse
import hashlib
import io
import shutil
import subprocess
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = (
    ROOT
    / "seed"
    / "releases"
    / "0.1-rc11"
    / "delivery"
    / "ASET-Seed-v0.1-rc11-Complete-Release-Bundle.zip"
)
EXPANDED = ROOT / "seed" / "releases" / "0.1-rc11" / "expanded"
EXPECTED_BUNDLE_SHA256 = (
    "a0a534125e27f491747dc46f080f418226798dadadee31d5d55b495e6e18ab43"
)
EXPECTED_DOCUMENTATION_SHA256 = (
    "3a2f06183790dd6ec06b1d2ad47653aa368ee9e62a1ec71f76c60cab508b5600"
)
DOCUMENTATION_NAME = "ASET-Seed-Documentation-v0.1-rc11.zip"
DOCUMENTATION_ROOT = "ASET-Seed-Documentation-v0.1-rc11/"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_members(archive: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    seen: set[str] = set()
    members: list[zipfile.ZipInfo] = []
    for info in archive.infolist():
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"unsafe ZIP path: {info.filename}")
        if info.filename in seen:
            raise ValueError(f"duplicate ZIP entry: {info.filename}")
        seen.add(info.filename)
        members.append(info)
    bad = archive.testzip()
    if bad is not None:
        raise ValueError(f"ZIP CRC failure: {bad}")
    return members


def documentation_bytes() -> bytes:
    bundle_bytes = BUNDLE.read_bytes()
    if sha256_bytes(bundle_bytes) != EXPECTED_BUNDLE_SHA256:
        raise ValueError("frozen complete bundle SHA-256 mismatch")
    with zipfile.ZipFile(io.BytesIO(bundle_bytes)) as bundle:
        safe_members(bundle)
        data = bundle.read(DOCUMENTATION_NAME)
    if sha256_bytes(data) != EXPECTED_DOCUMENTATION_SHA256:
        raise ValueError("frozen documentation archive SHA-256 mismatch")
    return data


def expected_files() -> dict[str, bytes]:
    result: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(documentation_bytes())) as archive:
        for info in safe_members(archive):
            if info.is_dir():
                continue
            if not info.filename.startswith(DOCUMENTATION_ROOT):
                raise ValueError(f"unexpected documentation root: {info.filename}")
            relative = info.filename[len(DOCUMENTATION_ROOT) :]
            if not relative:
                continue
            result[relative] = archive.read(info)
    return result


def observed_files() -> dict[str, bytes]:
    if not EXPANDED.is_dir():
        return {}
    return {
        path.relative_to(EXPANDED).as_posix(): path.read_bytes()
        for path in sorted(EXPANDED.rglob("*"))
        if path.is_file()
    }


def check() -> int:
    expected = expected_files()
    observed = observed_files()
    errors: list[str] = []

    for name in sorted(set(expected) - set(observed)):
        errors.append(f"missing:{name}")
    for name in sorted(set(observed) - set(expected)):
        errors.append(f"unexpected:{name}")
    for name in sorted(set(expected) & set(observed)):
        if expected[name] != observed[name]:
            errors.append(f"different:{name}")

    if errors:
        for error in errors:
            print(f"RC11_EXPANDED_ERROR={error}")
        return 1

    print(f"RC11_EXPANDED_FILES={len(expected)}")
    print("RC11_EXPANDED_BYTE_IDENTITY=PASS")
    return 0


def git_blob_hash(data: bytes) -> str:
    result = subprocess.run(
        ["git", "hash-object", "--stdin"],
        cwd=ROOT,
        input=data,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout.decode("ascii").strip()


def git_filtered_hash(path: Path, relative: str) -> str:
    result = subprocess.run(
        [
            "git",
            "hash-object",
            "--filters",
            f"--path={relative}",
            str(path),
        ],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace"))
    return result.stdout.decode("ascii").strip()


def check_git_storage() -> int:
    probe = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        raise RuntimeError("repository Git work tree is unavailable")

    expected = expected_files()
    errors: list[str] = []

    for name, data in sorted(expected.items()):
        path = EXPANDED / name
        if not path.is_file():
            errors.append(f"missing:{name}")
            continue
        repo_relative = path.relative_to(ROOT).as_posix()
        expected_blob = git_blob_hash(data)
        filtered_blob = git_filtered_hash(path, repo_relative)
        if expected_blob != filtered_blob:
            errors.append(f"filtered:{name}")

    if errors:
        for error in errors:
            print(f"RC11_GIT_STORAGE_ERROR={error}")
        return 1

    print(f"RC11_GIT_STORAGE_FILES={len(expected)}")
    print("RC11_GIT_STORAGE_BYTE_IDENTITY=PASS")
    return 0


def write_expanded() -> int:
    expected = expected_files()
    if EXPANDED.exists():
        shutil.rmtree(EXPANDED)
    for name, data in expected.items():
        destination = EXPANDED / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    print(f"RC11_EXPANDED_FILES={len(expected)}")
    print("RC11_EXPANDED_MATERIALIZATION=PASS")
    status = check()
    if status != 0:
        return status
    return check_git_storage()


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check-git", action="store_true")
    args = parser.parse_args()
    try:
        if args.check:
            return check()
        if args.check_git:
            return check_git_storage()
        return write_expanded()
    except Exception as error:
        print(f"RC11_EXPANDED_FATAL={error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

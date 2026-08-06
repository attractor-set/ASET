from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "MANIFEST.json"

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
}


def included(relative: Path) -> bool:
    if relative.as_posix() in {"MANIFEST.json", ".coverage"}:
        return False
    if any(part.endswith(".egg-info") for part in relative.parts):
        return False
    return not any(part in EXCLUDED_PARTS for part in relative.parts)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def build_manifest() -> dict[str, object]:
    files: list[dict[str, object]] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if not included(relative):
            continue
        files.append(
            {
                "path": relative.as_posix(),
                "sha256": "sha256:" + sha256_file(path),
                "size_bytes": path.stat().st_size,
            }
        )
    return {
        "document_type": "aset-repository-bootstrap-manifest",
        "files": files,
        "files_count": len(files),
        "manifest_scope": (
            "all repository regular files except MANIFEST.json, "
            "Git metadata, virtual environments, caches and dist"
        ),
        "package": "ASET-Seed-0.3.0-alpha.1-Minimal-Strong-Core",
        "repository_root": "ASET",
    }


def canonical_text(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
    ) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = canonical_text(build_manifest())

    if args.check:
        if not MANIFEST.is_file():
            print("MANIFEST_CHECK=MISSING")
            return 1
        actual = MANIFEST.read_text(encoding="utf-8")
        if actual != expected:
            print("MANIFEST_CHECK=DIFFERENT")
            return 1
        print("MANIFEST_CHECK=PASS")
        return 0

    MANIFEST.write_text(expected, encoding="utf-8", newline="\n")
    data = json.loads(expected)
    print(f"MANIFEST_FILES={data['files_count']}")
    print("MANIFEST_REBUILT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

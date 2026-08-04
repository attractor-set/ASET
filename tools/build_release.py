from __future__ import annotations

import hashlib
import stat
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
ARCHIVE = DIST / "ASET-Repository-Snapshot.zip"

FIXED = (1980, 1, 1, 0, 0, 0)

EXCLUDED_PARTS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
}


def included(path: Path) -> bool:
    if path.as_posix() == ".coverage":
        return False
    if any(part.endswith(".egg-info") for part in path.parts):
        return False
    return not any(part in EXCLUDED_PARTS for part in path.parts)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()

    with path.open("rb") as stream:
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)

    return digest.hexdigest()


def main() -> int:
    DIST.mkdir(parents=True, exist_ok=True)

    files = [
        path
        for path in ROOT.rglob("*")
        if path.is_file()
        and included(path.relative_to(ROOT))
    ]

    with zipfile.ZipFile(
        ARCHIVE,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for path in sorted(files):
            relative = path.relative_to(ROOT)
            info = zipfile.ZipInfo(
                str(Path("ASET") / relative),
                FIXED,
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (
                (stat.S_IFREG | 0o644) << 16
            )
            archive.writestr(info, path.read_bytes())

    digest = sha256_file(ARCHIVE)

    checksum = ARCHIVE.with_suffix(
        ARCHIVE.suffix + ".sha256"
    )

    checksum.write_text(
        f"{digest}  {ARCHIVE.name}\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"ARCHIVE={ARCHIVE}")
    print(f"SHA256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

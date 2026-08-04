from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUNDLE = (
    ROOT
    / "seed"
    / "releases"
    / "0.1-rc11"
    / "delivery"
    / "ASET-Seed-v0.1-rc11-Complete-Release-Bundle.zip"
)

EXPECTED = (
    "a0a534125e27f491747dc46f080f418226798dadadee31d5d55b495e6e18ab43"
)


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
    if not BUNDLE.is_file():
        print("FROZEN_RC11_BUNDLE=MISSING")
        return 1

    observed = sha256_file(BUNDLE)

    if observed != EXPECTED:
        print(f"FROZEN_RC11_EXPECTED={EXPECTED}")
        print(f"FROZEN_RC11_OBSERVED={observed}")
        return 1

    print("FROZEN_RC11_BUNDLE=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

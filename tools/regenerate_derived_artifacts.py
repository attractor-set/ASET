#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMMANDS = (
    ["tools/build_conformance_profile.py"],
    ["tools/build_canon_package.py"],
    ["tools/generate_repository_views.py"],
    ["tools/rebuild_manifest.py"],
)


def main() -> int:
    for args in COMMANDS:
        result = subprocess.run([sys.executable, *args], cwd=ROOT, check=False)
        if result.returncode:
            print(f"DERIVED_ARTIFACT_REGENERATION_FAILURE={args[0]}")
            return result.returncode or 1
    print("DERIVED_ARTIFACT_REGENERATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

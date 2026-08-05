from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GENERATORS = (
    "tools/generate_project_metadata.py",
    "tools/generate_editions.py",
    "tools/generate_component_views.py",
    "tools/generate_semantic_views.py",
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    for generator in GENERATORS:
        command = [sys.executable, generator]
        if args.check:
            command.append("--check")
        result = subprocess.run(command, cwd=ROOT, check=False)
        if result.returncode != 0:
            print(f"REPOSITORY_VIEW_FAILURE={generator}")
            return result.returncode or 1

    mode = "PARITY" if args.check else "GENERATION"
    print(f"REPOSITORY_VIEWS_{mode}=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

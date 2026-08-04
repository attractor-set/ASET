from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("wheel", nargs="?")
    args = parser.parse_args()

    if args.wheel:
        wheel = Path(args.wheel)
    else:
        candidates = sorted((ROOT / "dist/wheels").glob("aset_seed-*.whl"))
        if len(candidates) != 1:
            print(f"WHEEL_ERROR=expected one wheel, found {len(candidates)}")
            return 1
        wheel = candidates[0]
    if not wheel.is_file():
        print(f"WHEEL_ERROR=missing:{wheel}")
        return 1

    with zipfile.ZipFile(wheel) as archive:
        names = archive.namelist()
    schema_names = [
        name
        for name in names
        if name.startswith("aset_seed/schemas/") and name.endswith(".json")
    ]
    required = {
        "aset_seed/__init__.py",
        "aset_seed/__main__.py",
        "aset_seed/cli.py",
        "aset_seed/core.py",
        "aset_seed/runtime.py",
        "aset_seed/store.py",
        "aset_seed/proofs.py",
    }
    if not required.issubset(names) or len(schema_names) != 39:
        print(f"WHEEL_ERROR=content:schemas={len(schema_names)}")
        return 1

    with tempfile.TemporaryDirectory(prefix="aset-wheel-") as directory:
        target = Path(directory) / "site"
        install = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-deps",
                "--target",
                str(target),
                str(wheel),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if install.returncode != 0:
            print("WHEEL_ERROR=install")
            print(install.stdout, end="")
            print(install.stderr, end="", file=sys.stderr)
            return install.returncode
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(target)
        probe = subprocess.run(
            [
                sys.executable,
                "-c",
                (
                    "import importlib.resources as r; import aset_seed; "
                    "p=r.files('aset_seed').joinpath('schemas'); "
                    "assert len(list(p.glob('*.json'))) == 39; "
                    "print(aset_seed.__version__)"
                ),
            ],
            cwd=Path(directory),
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
        if probe.returncode != 0:
            print("WHEEL_ERROR=import")
            print(probe.stdout, end="")
            print(probe.stderr, end="", file=sys.stderr)
            return probe.returncode

    print(f"WHEEL={wheel}")
    print("WHEEL_SCHEMAS=39")
    print("WHEEL_INSTALL_IMPORT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

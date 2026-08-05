from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot")
    parser.add_argument("--output")
    args = parser.parse_args()
    snapshot = Path(args.snapshot)
    if not snapshot.is_absolute():
        snapshot = ROOT / snapshot
    if not snapshot.is_file():
        print("REFERENCE_ADVERSARIAL_ERROR=snapshot missing")
        return 1

    with tempfile.TemporaryDirectory(prefix="aset-ref-adversarial-") as directory:
        target = Path(directory)
        with zipfile.ZipFile(snapshot) as archive:
            archive.extractall(target)
        roots = [path for path in target.iterdir() if path.is_dir()]
        repo = roots[0] if len(roots) == 1 else target
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(repo / "src")
        result = subprocess.run(
            [sys.executable, "tools/reference_adversarial_probe.py"],
            cwd=repo,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )
    print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    report = {
        "document_type": "aset-reference-blackbox-adversarial",
        "snapshot": snapshot.name,
        "returncode": result.returncode,
        "verdict": "PASS" if result.returncode == 0 else "FAIL",
    }
    if args.output:
        output = ROOT / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())

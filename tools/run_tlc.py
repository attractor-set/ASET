#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "seed/canonical/formal"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jar", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("dist/tlc-model-check.json"))
    parser.add_argument("--workers", default="1")
    args = parser.parse_args()
    jar = args.jar.resolve()
    if not jar.is_file():
        print(f"TLC_ERROR=missing jar:{jar}")
        return 2

    command = [
        "java",
        "-XX:+UseParallelGC",
        "-cp",
        str(jar),
        "tlc2.TLC",
        "-workers",
        str(args.workers),
        "-config",
        "SeedRC12.cfg",
        "SeedRC12.tla",
    ]
    completed = subprocess.run(command, cwd=FORMAL, text=True, capture_output=True, check=False)
    output = completed.stdout + completed.stderr
    passed = completed.returncode == 0 and "No error has been found" in output
    report = {
        "document_type": "aset-tlc-model-check",
        "command": command,
        "returncode": completed.returncode,
        "no_error_marker": "No error has been found" in output,
        "verdict": "PASS" if passed else "FAIL",
        "output": output,
    }
    out = ROOT / args.output
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print("TLC_MODEL_CHECK=" + report["verdict"])
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path("tools/registration/inpi-software-deposit-profile-v1.json")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-ref", required=True)
    args = parser.parse_args()

    result = subprocess.run(
        ["git", "show", f"{args.approved_ref}:{PROFILE.as_posix()}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        print("INPI_DEPOSIT_PROFILE_PRIOR=ABSENT")
        print("INPI_DEPOSIT_PROFILE_STABILITY=PASS")
        return 0
    current = (ROOT / PROFILE).read_bytes()
    if result.stdout != current:
        print("INPI_DEPOSIT_PROFILE_STABILITY=FAIL")
        print("INPI_DEPOSIT_PROFILE_ERROR=V1 profile changed; add a new versioned profile instead")
        return 1
    print("INPI_DEPOSIT_PROFILE_PRIOR=PRESENT")
    print("INPI_DEPOSIT_PROFILE_STABILITY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

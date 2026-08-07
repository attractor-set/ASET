#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = Path("standards/seed-compatibility/compatibility-standard-profile-v1.json")
SCHEMA = Path("standards/seed-compatibility/compatibility-standard-release.schema.json")


def same_as_ref(ref: str, path: Path) -> tuple[bool, bool]:
    completed = subprocess.run(
        ["git", "show", f"{ref}:{path.as_posix()}"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode:
        return False, True
    return completed.stdout == (ROOT / path).read_bytes(), False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--approved-ref", required=True)
    args = parser.parse_args()

    prior_absent = True
    for path in (PROFILE, SCHEMA):
        same, absent = same_as_ref(args.approved_ref, path)
        if absent:
            continue
        prior_absent = False
        if not same:
            print("SEED_COMPATIBILITY_PROFILE_STABILITY=FAIL")
            print(
                "SEED_COMPATIBILITY_PROFILE_ERROR="
                "V1 compatibility profile/schema changed; add a new versioned profile instead"
            )
            return 1
    print(
        "SEED_COMPATIBILITY_PROFILE_PRIOR=" + ("ABSENT" if prior_absent else "PRESENT")
    )
    print("SEED_COMPATIBILITY_PROFILE_STABILITY=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

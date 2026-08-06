#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json

from monade_attempt_profile_common import (
    PACKAGE,
    PACKAGE_FILES,
    PROFILE,
    ROOT,
    canonical_digest,
    canonical_text,
    file_digest,
    load,
)


def expected_profile() -> dict[str, object]:
    value = load(PROFILE)
    value["canonical_digest"] = canonical_digest(value)
    return value


def expected_package() -> dict[str, object]:
    rows = [
        {"path": relative, "sha256": file_digest(ROOT / relative)}
        for relative in PACKAGE_FILES
    ]
    digest = "sha256:" + hashlib.sha256(
        json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return {
        "document_type": "aset-optional-profile-package",
        "schema_version": 1,
        "profile_id": "ASET-MONADE-ATTEMPT-EVIDENCE-V1",
        "implementation_precedence": "NONE",
        "normative_for_seed": False,
        "required_for_seed_conformance": False,
        "files": rows,
        "package_digest": digest,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    profile_text = canonical_text(expected_profile())
    if args.check:
        if PROFILE.read_text(encoding="utf-8") != profile_text:
            print("MONADE_ATTEMPT_PROFILE_IDENTITY=DIFFERENT")
            return 1
    else:
        PROFILE.write_text(profile_text, encoding="utf-8", newline="\n")

    package_text = canonical_text(expected_package())
    if args.check:
        if not PACKAGE.is_file() or PACKAGE.read_text(encoding="utf-8") != package_text:
            print("MONADE_ATTEMPT_PROFILE_PACKAGE=DIFFERENT")
            return 1
        print("MONADE_ATTEMPT_PROFILE_PACKAGE=PASS")
        return 0

    PACKAGE.write_text(package_text, encoding="utf-8", newline="\n")
    print("MONADE_ATTEMPT_PROFILE_PACKAGE_BUILT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

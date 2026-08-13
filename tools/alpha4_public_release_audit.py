#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

PROJECT = "Authority-Seeded Evidence Trail (ASET)"
SEMANTIC_ALGEBRA = {
    "id": "ASET_ALPHA",
    "name": "Local Recognition Algebra",
}
REPRESENTATION_ID = "0.4alpha"
SUBJECT_ID = "ASET-SEED-0.4-ALPHA"


class PublicReleaseAuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise PublicReleaseAuditError(message)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def check_public_release(
    root: Path,
    release_root: Path,
    profiles_root: Path,
    certificate_path: Path,
) -> dict[str, object]:
    readme = (root / "README.md").read_text(encoding="utf-8")
    citation = (root / "CITATION.cff").read_text(encoding="utf-8")

    require(
        readme.startswith("# ASET — Authority-Seeded Evidence Trail\n"),
        "README project identity mismatch",
    )
    require("**ASET Alpha**" in readme, "ASET Alpha missing from README")
    require(
        "Local Recognition Algebra" in readme,
        "Local Recognition Algebra missing from README",
    )
    require(
        "current representation identifier" in readme,
        "representation description missing from README",
    )
    require(
        'title: "ASET — Authority-Seeded Evidence Trail"' in citation,
        "CITATION project identity mismatch",
    )
    require('version: "0.4alpha"' in citation, "CITATION representation mismatch")
    require(
        'repository-code: "https://github.com/attractor-set/aset-seed"' in citation,
        "CITATION repository locator mismatch",
    )

    release = load_json(release_root / "RELEASE_MANIFEST.json")
    profiles = load_json(profiles_root / "RELEASE_PROFILE_MANIFEST.json")
    certificate = load_json(certificate_path)

    require(
        release.get("subject_id") == SUBJECT_ID, "release subject identity mismatch"
    )
    require(release.get("version") == REPRESENTATION_ID, "release version mismatch")
    require(
        release.get("representation_id") == REPRESENTATION_ID,
        "release representation identity mismatch",
    )
    require(
        release.get("semantic_algebra") == SEMANTIC_ALGEBRA,
        "release semantic algebra mismatch",
    )
    composition_manifest = release.get("composition_manifest")
    require(
        isinstance(composition_manifest, dict),
        "release composition manifest metadata missing",
    )
    require(
        composition_manifest.get("path") == "source/SEED.aset"
        and composition_manifest.get("semantic_precedence") == "NONE",
        "release composition manifest binding mismatch",
    )
    require(
        "binding_graph" not in release,
        "derived binding graph must not be part of the release contract",
    )
    causal_expression = release.get("causal_expression")
    triangulated_assurance = release.get("triangulated_assurance")
    require(isinstance(causal_expression, dict), "causal release expression missing")
    require(
        causal_expression.get("semantic_delta") == "NONE"
        and causal_expression.get("semantic_precedence") == "NONE",
        "causal release expression changes semantic precedence",
    )
    require(
        isinstance(triangulated_assurance, dict),
        "triangulated release assurance missing",
    )
    require(
        triangulated_assurance.get("representations")
        == ["OPERATIONAL", "RELATIONAL", "CAUSAL"],
        "triangulated representation set mismatch",
    )
    require(
        triangulated_assurance.get("semantic_delta") == "NONE"
        and triangulated_assurance.get("semantic_precedence") == "NONE",
        "triangulated assurance changes semantic precedence",
    )

    require(profiles.get("project") == PROJECT, "profile project identity mismatch")
    require(
        profiles.get("subject_id") == SUBJECT_ID, "profile subject identity mismatch"
    )
    require(
        profiles.get("representation_id") == REPRESENTATION_ID,
        "profile representation identity mismatch",
    )
    require(
        profiles.get("semantic_algebra") == SEMANTIC_ALGEBRA,
        "profile semantic algebra mismatch",
    )
    profile_set = profiles.get("profiles")
    require(isinstance(profile_set, dict), "profile set missing")
    python_sqlite = profile_set.get("python_sqlite")
    require(isinstance(python_sqlite, dict), "Python SQLite profile missing")
    require(
        python_sqlite.get("role") == "PERSISTENCE_EXTENSION",
        "Python SQLite role mismatch",
    )
    require(
        python_sqlite.get("base_expression") == "python",
        "Python SQLite base expression mismatch",
    )
    require(
        python_sqlite.get("semantic_delta") == "NONE",
        "Python SQLite semantic delta mismatch",
    )

    require(certificate.get("project") == PROJECT, "certificate project mismatch")
    require(
        certificate.get("semantic_algebra") == SEMANTIC_ALGEBRA,
        "certificate semantic algebra mismatch",
    )
    require(
        certificate.get("representation_id") == REPRESENTATION_ID,
        "certificate representation identity mismatch",
    )
    require(certificate.get("status") == "PASS", "release admission is not PASS")
    certificate_evidence = certificate.get("evidence")
    require(isinstance(certificate_evidence, dict), "certificate evidence missing")
    post_build = certificate_evidence.get("post_build_formal_assurance")
    require(
        isinstance(post_build, dict)
        and post_build.get("status") == "PASS"
        and post_build.get("final_theorem")
        == "AssembledNextPreservesExactSubjectAndAuthority"
        and post_build.get("semantic_delta") == "NONE",
        "post-build formal assurance missing from release admission",
    )

    return {
        "document_type": "aset-public-release-audit",
        "project": PROJECT,
        "semantic_algebra": SEMANTIC_ALGEBRA,
        "representation_id": REPRESENTATION_ID,
        "subject_id": SUBJECT_ID,
        "assurance_representations": ["OPERATIONAL", "RELATIONAL", "CAUSAL"],
        "assurance_semantic_delta": "NONE",
        "python_expression_role": "RELEASE_EXPRESSION",
        "python_sqlite_role": "PERSISTENCE_EXTENSION",
        "python_sqlite_semantic_delta": "NONE",
        "post_build_formal_assurance": "PASS",
        "release_admission": "PASS",
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-root",
        type=Path,
        default=ROOT / "dist/ASET-Seed-0.4alpha",
    )
    parser.add_argument(
        "--profiles-root",
        type=Path,
        default=ROOT / "dist/ASET-Seed-0.4alpha-profiles",
    )
    parser.add_argument(
        "--certificate",
        type=Path,
        default=ROOT / "dist/release-admission-certificate.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist/public-release-audit.json",
    )
    args = parser.parse_args(argv)

    try:
        evidence = check_public_release(
            ROOT,
            args.release_root,
            args.profiles_root,
            args.certificate,
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (OSError, ValueError, PublicReleaseAuditError) as error:
        print(f"ALPHA4_PUBLIC_RELEASE_AUDIT_ERROR={error}")
        print("ALPHA4_PUBLIC_RELEASE_AUDIT=FAIL")
        return 1

    print("ALPHA4_PUBLIC_IDENTITY=AUTHORITY_SEEDED_EVIDENCE_TRAIL")
    print("ALPHA4_PUBLIC_SEMANTIC_ALGEBRA=ASET_ALPHA")
    print(f"ALPHA4_PUBLIC_REPRESENTATION={REPRESENTATION_ID}")
    print("ALPHA4_PUBLIC_ASSURANCE_REPRESENTATIONS=OPERATIONAL,RELATIONAL,CAUSAL")
    print("ALPHA4_PUBLIC_ASSURANCE_SEMANTIC_DELTA=NONE")
    print("ALPHA4_PUBLIC_POST_BUILD_FORMAL_ASSURANCE=PASS")
    print("ALPHA4_PUBLIC_RELEASE_AUDIT=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

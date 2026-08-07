#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SUPPLEMENT = ROOT / "governance/ip/background-ip-supplement-2.json"
SCHEMA = ROOT / "governance/ip/background-ip-supplement-2.schema.json"
PARENT = ROOT / "governance/ip/background-ip-schedule.json"
PRIOR = ROOT / "governance/ip/background-ip-supplement-1.json"
EDITIONS = (
    ROOT / "BACKGROUND_IP_SUPPLEMENT_2.md",
    ROOT / "BACKGROUND_IP_SUPPLEMENT_2.ru.md",
    ROOT / "BACKGROUND_IP_SUPPLEMENT_2.pt-BR.md",
)


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(["git", *arguments], cwd=ROOT, capture_output=True, check=False)


def show(commit: str, relative: str) -> bytes:
    result = git("show", f"{commit}:{relative}")
    if result.returncode:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise ValueError(f"cannot read {commit}:{relative}: {detail}")
    return result.stdout


def validate_static() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    try:
        supplement = load(SUPPLEMENT)
        schema = load(SCHEMA)
        parent = load(PARENT)
        prior = load(PRIOR)
    except Exception as error:
        return {}, [str(error)]

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(supplement), key=lambda item: list(item.absolute_path)):
        location = "/".join(str(item) for item in error.absolute_path)
        errors.append(f"schema:{location or '<root>'}:{error.message}")

    if supplement.get("creator") != parent.get("creator"):
        errors.append("creator identity differs from parent schedule")

    holder = supplement.get("current_rights_holder")
    parent_holder = parent.get("current_rights_holder")
    if not isinstance(holder, dict) or not isinstance(parent_holder, dict):
        errors.append("rights-holder identity objects are required")
    else:
        if holder.get("legal_name") != parent_holder.get("legal_name"):
            errors.append("rights-holder legal name differs from parent schedule")
        if holder.get("assignment_to_legal_entity") is not False:
            errors.append("supplement must not claim an assignment to a legal entity")

    prior_records = supplement.get("prior_supplements")
    if not isinstance(prior_records, list) or len(prior_records) != 1 or not isinstance(prior_records[0], dict):
        errors.append("exactly one prior supplement record is required")
    else:
        record = prior_records[0]
        if record.get("supplement_id") != prior.get("supplement_id"):
            errors.append("prior supplement identifier differs")
        if record.get("supplement_version") != prior.get("supplement_version"):
            errors.append("prior supplement version differs")
        if record.get("document_sha256") != sha256_bytes(PRIOR.read_bytes()):
            errors.append("prior supplement SHA-256 differs")

    assets = supplement.get("added_assets")
    expected_ids = [f"BI-S2-{index:03d}" for index in range(1, 5)]
    if not isinstance(assets, list):
        errors.append("added_assets must be an array")
    else:
        observed_ids = [asset.get("asset_id") for asset in assets if isinstance(asset, dict)]
        if observed_ids != expected_ids:
            errors.append("asset identifiers are not the expected bounded sequence")
        if len(observed_ids) != len(set(observed_ids)):
            errors.append("duplicate supplement asset identifiers")

    expected_tokens = {
        "Dzmitry Prychyna",
        "Attractor Set",
        "seed-0.3.0-alpha.1",
        "03eaa7c36c4cbf938e43d39ece7a3d1ef69f2d13",
        "ade1e2fe58c34ca4fa53695ea9e2ec3d08552518",
        "seed-0.3.0-alpha.1-semantic-freeze",
        "a96689b1f1da17ac126058f5ee0175c90df3ef4f",
    }
    for edition in EDITIONS:
        if not edition.is_file():
            errors.append(f"missing:{edition.relative_to(ROOT)}")
            continue
        text = edition.read_text(encoding="utf-8")
        for token in expected_tokens:
            if token not in text:
                errors.append(f"missing-token:{edition.relative_to(ROOT)}:{token}")

    return supplement, errors


def validate_git(supplement: dict[str, object]) -> list[str]:
    errors: list[str] = []
    cutoffs = supplement.get("cutoffs")
    if not isinstance(cutoffs, list) or len(cutoffs) != 1 or not isinstance(cutoffs[0], dict):
        return ["cannot run Git verification on malformed release cutoff"]
    cutoff = cutoffs[0]
    commit = cutoff.get("commit_sha")
    freeze_commit = cutoff.get("semantic_freeze_commit_sha")
    if not isinstance(commit, str) or not isinstance(freeze_commit, str):
        return ["release or semantic-freeze commit is missing"]

    for value, label in ((commit, "release"), (freeze_commit, "semantic-freeze")):
        if git("cat-file", "-e", f"{value}^{{commit}}").returncode:
            errors.append(f"{label} commit is not reachable: {value}")

    if not errors:
        manifest_bytes = show(commit, str(cutoff["manifest_path"]))
        if sha256_bytes(manifest_bytes) != cutoff.get("manifest_sha256"):
            errors.append("release manifest SHA-256 differs")
        manifest = json.loads(manifest_bytes)
        if manifest.get("files_count") != cutoff.get("manifest_files_count"):
            errors.append("release manifest file count differs")

        canon_bytes = show(commit, str(cutoff["canon_package_path"]))
        if sha256_bytes(canon_bytes) != cutoff.get("canon_package_file_sha256"):
            errors.append("release canon package file SHA-256 differs")
        canon = json.loads(canon_bytes)
        if canon.get("package_digest") != cutoff.get("canon_package_digest"):
            errors.append("release canon package digest differs")

        for tag_key, object_key, commit_key, label in (
            ("release_tag", "release_tag_object_sha", "commit_sha", "release"),
            ("semantic_freeze_tag", "semantic_freeze_tag_object_sha", "semantic_freeze_commit_sha", "semantic-freeze"),
        ):
            tag = str(cutoff[tag_key])
            observed_object = git("rev-parse", f"refs/tags/{tag}")
            object_sha = observed_object.stdout.decode().strip() if observed_object.returncode == 0 else ""
            if object_sha != cutoff.get(object_key):
                errors.append(f"{label} annotated-tag object differs")
            peeled = git("rev-list", "-n", "1", tag)
            peeled_sha = peeled.stdout.decode().strip() if peeled.returncode == 0 else ""
            if peeled_sha != cutoff.get(commit_key):
                errors.append(f"{label} tag does not peel to recorded commit")

        if git("merge-base", "--is-ancestor", freeze_commit, commit).returncode:
            errors.append("semantic-freeze commit is not an ancestor of release commit")

        assets = supplement.get("added_assets")
        if isinstance(assets, list):
            for asset in assets:
                if not isinstance(asset, dict):
                    continue
                for relative in asset.get("paths", []):
                    if isinstance(relative, str) and git("cat-file", "-e", f"{commit}:{relative}").returncode:
                        errors.append(f"release asset path is absent at cutoff: {relative}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-git", action="store_true")
    args = parser.parse_args()

    supplement, errors = validate_static()
    if not errors and args.check_git:
        errors.extend(validate_git(supplement))

    if errors:
        for error in errors:
            print(f"BACKGROUND_IP_SUPPLEMENT_2_ERROR={error}")
        print("BACKGROUND_IP_SUPPLEMENT_2_VALIDATION=FAIL")
        return 1

    print("BACKGROUND_IP_SUPPLEMENT_2_SCHEMA=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_2_IDENTITY_CONTINUITY=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_2_PRIOR_SUPPLEMENT=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_2_RELEASE_CUTOFF=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_2_STATIC_DOCS=PASS")
    if args.check_git:
        print("BACKGROUND_IP_SUPPLEMENT_2_GIT_RELEASE_IDENTITY=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_2_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

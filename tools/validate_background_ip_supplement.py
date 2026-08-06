#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SUPPLEMENT = ROOT / "governance/ip/background-ip-supplement-1.json"
SCHEMA = ROOT / "governance/ip/background-ip-supplement.schema.json"
PARENT = ROOT / "governance/ip/background-ip-schedule.json"
EDITIONS = (
    ROOT / "BACKGROUND_IP_SUPPLEMENT_1.md",
    ROOT / "BACKGROUND_IP_SUPPLEMENT_1.ru.md",
    ROOT / "BACKGROUND_IP_SUPPLEMENT_1.pt-BR.md",
)


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path) -> dict[str, object]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain an object")
    return value


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git(repo: Path, *arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *arguments],
        cwd=repo,
        capture_output=True,
        check=False,
    )


def show(repo: Path, commit: str, relative: str) -> bytes:
    result = git(repo, "show", f"{commit}:{relative}")
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
    except Exception as error:
        return {}, [str(error)]

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(
        validator.iter_errors(supplement),
        key=lambda item: list(item.absolute_path),
    ):
        location = "/".join(str(item) for item in error.absolute_path)
        errors.append(f"schema:{location or '<root>'}:{error.message}")

    for edition in EDITIONS:
        if not edition.is_file():
            errors.append(f"missing:{edition.relative_to(ROOT)}")

    creator = supplement.get("creator")
    holder = supplement.get("current_rights_holder")
    parent_creator = parent.get("creator")
    parent_holder = parent.get("current_rights_holder")
    if not all(
        isinstance(value, dict)
        for value in (creator, holder, parent_creator, parent_holder)
    ):
        errors.append("creator and holder identity objects are required")
    else:
        assert isinstance(creator, dict)
        assert isinstance(holder, dict)
        assert isinstance(parent_creator, dict)
        assert isinstance(parent_holder, dict)
        if creator.get("legal_name") != parent_creator.get("legal_name"):
            errors.append("creator legal name differs from parent schedule")
        if holder.get("legal_name") != parent_holder.get("legal_name"):
            errors.append("rights-holder legal name differs from parent schedule")
        if creator.get("public_pseudonym") != "Attractor Set":
            errors.append("unexpected creator pseudonym")
        if creator.get("pseudonym_is_separate_legal_entity") is not False:
            errors.append("pseudonym must not be represented as a legal entity")
        if holder.get("assignment_to_legal_entity") is not False:
            errors.append("supplement must not claim an assignment to a legal entity")

    assets = supplement.get("added_assets")
    if not isinstance(assets, list):
        errors.append("added_assets must be an array")
    else:
        identifiers = [
            asset.get("asset_id")
            for asset in assets
            if isinstance(asset, dict)
        ]
        if len(identifiers) != len(set(identifiers)):
            errors.append("duplicate supplement asset identifiers")

    cutoffs = supplement.get("cutoffs")
    if not isinstance(cutoffs, list) or len(cutoffs) != 2:
        errors.append("exactly two repository cutoffs are required")
    else:
        aset_cutoff, reference_cutoff = cutoffs
        if isinstance(aset_cutoff, dict) and isinstance(reference_cutoff, dict):
            if reference_cutoff.get("canon_lock_source_ref") != aset_cutoff.get(
                "commit_sha"
            ):
                errors.append("reference canon lock does not identify the ASET cutoff")
            if reference_cutoff.get(
                "canon_lock_required_package_digest"
            ) != aset_cutoff.get("canon_package_digest"):
                errors.append("reference canon lock package digest differs from ASET cutoff")

    expected_tokens = {
        "Dzmitry Prychyna",
        "Attractor Set",
        "a122e2f828256501abb645b89046cc866f4466ed",
        "2038f84b6b5f6a0aed3636c1685d2c1fb79a1ed1",
    }
    for edition in EDITIONS:
        if not edition.is_file():
            continue
        text = edition.read_text(encoding="utf-8")
        for token in expected_tokens:
            if token not in text:
                errors.append(f"missing-token:{edition.relative_to(ROOT)}:{token}")

    return supplement, errors


def validate_repository_cutoff(
    repo: Path,
    cutoff: dict[str, object],
    *,
    reference: bool,
) -> list[str]:
    errors: list[str] = []
    commit = cutoff.get("commit_sha")
    if not isinstance(commit, str):
        return ["cutoff commit is missing"]
    if git(repo, "cat-file", "-e", f"{commit}^{{commit}}").returncode:
        return [f"cutoff commit is not reachable in {repo}: {commit}"]

    if not reference:
        tree = git(repo, "rev-parse", f"{commit}^{{tree}}")
        observed_tree = tree.stdout.decode().strip() if tree.returncode == 0 else ""
        if observed_tree != cutoff.get("tree_sha"):
            errors.append(
                f"ASET cutoff tree differs: observed={observed_tree}; "
                f"expected={cutoff.get('tree_sha')}"
            )

        manifest_path = cutoff.get("manifest_path")
        if isinstance(manifest_path, str):
            try:
                manifest_bytes = show(repo, commit, manifest_path)
                if sha256_bytes(manifest_bytes) != cutoff.get("manifest_sha256"):
                    errors.append("ASET cutoff manifest SHA-256 differs")
                manifest = json.loads(manifest_bytes)
                if manifest.get("files_count") != cutoff.get("manifest_files_count"):
                    errors.append("ASET cutoff manifest file count differs")
            except Exception as error:
                errors.append(str(error))

        canon_path = cutoff.get("canon_package_path")
        if isinstance(canon_path, str):
            try:
                canon_bytes = show(repo, commit, canon_path)
                if sha256_bytes(canon_bytes) != cutoff.get("canon_package_file_sha256"):
                    errors.append("ASET canon package file SHA-256 differs")
                canon = json.loads(canon_bytes)
                if canon.get("package_digest") != cutoff.get("canon_package_digest"):
                    errors.append("ASET canon package digest differs")
            except Exception as error:
                errors.append(str(error))
    else:
        for path_key, sha_key in (
            ("canon_lock_path", "canon_lock_sha256"),
            ("profile_path", "profile_sha256"),
        ):
            relative = cutoff.get(path_key)
            if not isinstance(relative, str):
                errors.append(f"missing {path_key}")
                continue
            try:
                data = show(repo, commit, relative)
            except Exception as error:
                errors.append(str(error))
                continue
            if sha256_bytes(data) != cutoff.get(sha_key):
                errors.append(f"reference {relative} SHA-256 differs")
            try:
                document = json.loads(data)
            except Exception as error:
                errors.append(f"reference {relative} JSON invalid: {error}")
                continue
            if path_key == "canon_lock_path":
                source = document.get("source")
                if not isinstance(source, dict):
                    errors.append("reference canon lock source is invalid")
                else:
                    if source.get("ref") != cutoff.get("canon_lock_source_ref"):
                        errors.append("reference canon lock source ref differs")
                if document.get("required_package_digest") != cutoff.get(
                    "canon_lock_required_package_digest"
                ):
                    errors.append("reference canon lock package digest differs")
            else:
                if document.get("profile_id") != cutoff.get("profile_id"):
                    errors.append("reference profile identifier differs")
                if document.get("normative") is not False:
                    errors.append("reference profile must remain non-normative")
                if document.get("production_ready") is not False:
                    errors.append("reference profile must remain non-production-ready")
                if document.get("implementation_precedence") != "NONE":
                    errors.append("reference profile implementation precedence differs")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-git", action="store_true")
    parser.add_argument("--reference-repo", type=Path)
    args = parser.parse_args()

    supplement, errors = validate_static()
    if not errors and args.check_git:
        cutoffs = supplement.get("cutoffs")
        if not isinstance(cutoffs, list) or len(cutoffs) != 2:
            errors.append("cannot run Git verification on malformed cutoffs")
        elif args.reference_repo is None:
            errors.append("--reference-repo is required with --check-git")
        else:
            aset_cutoff, reference_cutoff = cutoffs
            if not isinstance(aset_cutoff, dict) or not isinstance(
                reference_cutoff, dict
            ):
                errors.append("cutoff entries must be objects")
            else:
                errors.extend(
                    validate_repository_cutoff(ROOT, aset_cutoff, reference=False)
                )
                errors.extend(
                    validate_repository_cutoff(
                        args.reference_repo.resolve(),
                        reference_cutoff,
                        reference=True,
                    )
                )

    if errors:
        for error in errors:
            print(f"BACKGROUND_IP_SUPPLEMENT_ERROR={error}")
        print("BACKGROUND_IP_SUPPLEMENT_VALIDATION=FAIL")
        return 1

    print("BACKGROUND_IP_SUPPLEMENT_SCHEMA=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_IDENTITY_CONTINUITY=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_CUTOFF_RELATION=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_STATIC_DOCS=PASS")
    if args.check_git:
        print("BACKGROUND_IP_SUPPLEMENT_GIT_CUTOFFS=PASS")
    print("BACKGROUND_IP_SUPPLEMENT_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

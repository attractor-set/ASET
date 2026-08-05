from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEDULE = ROOT / "governance/ip/background-ip-schedule.json"
SCHEMA = ROOT / "governance/ip/background-ip-schedule.schema.json"
REQUIRED_EDITIONS = (
    ROOT / "BACKGROUND_IP_SCHEDULE.md",
    ROOT / "BACKGROUND_IP_SCHEDULE.ru.md",
    ROOT / "BACKGROUND_IP_SCHEDULE.pt-BR.md",
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
        raise ValueError(f"{path.relative_to(ROOT)} must contain an object")
    return value


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git(*arguments: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        capture_output=True,
        check=False,
    )


def validate_static() -> tuple[dict[str, object], list[str]]:
    errors: list[str] = []
    try:
        schedule = load(SCHEDULE)
        schema = load(SCHEMA)
    except Exception as error:
        return {}, [str(error)]

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(
        validator.iter_errors(schedule),
        key=lambda item: list(item.absolute_path),
    ):
        location = "/".join(str(item) for item in error.absolute_path)
        errors.append(f"schema:{location or '<root>'}:{error.message}")

    for edition in REQUIRED_EDITIONS:
        if not edition.is_file():
            errors.append(f"missing:{edition.relative_to(ROOT)}")

    creator = schedule.get("creator")
    holder = schedule.get("current_rights_holder")
    if not isinstance(creator, dict) or not isinstance(holder, dict):
        errors.append("creator and current_rights_holder must be objects")
    else:
        if creator.get("legal_name") != holder.get("legal_name"):
            errors.append("creator and current rights holder legal names differ")
        if creator.get("public_pseudonym") != holder.get("public_pseudonym"):
            errors.append("creator and holder pseudonyms differ")
        if creator.get("pseudonym_is_separate_legal_entity") is not False:
            errors.append("Attractor Set must not be represented as a separate legal entity")

    assets = schedule.get("assets")
    if not isinstance(assets, list):
        errors.append("assets must be an array")
    else:
        identifiers: list[str] = []
        paths: set[str] = set()
        for asset in assets:
            if not isinstance(asset, dict):
                errors.append("asset entry must be an object")
                continue
            identifier = asset.get("asset_id")
            if isinstance(identifier, str):
                identifiers.append(identifier)
            asset_paths = asset.get("paths")
            if isinstance(asset_paths, list):
                paths.update(path for path in asset_paths if isinstance(path, str))
        if len(identifiers) != len(set(identifiers)):
            errors.append("duplicate asset identifiers")
        for relative in sorted(paths):
            if not (ROOT / relative).exists():
                errors.append(f"missing-scheduled-path:{relative}")

    expected_tokens = {
        "Dzmitry Prychyna",
        "Attractor Set",
    }
    for edition in REQUIRED_EDITIONS:
        if not edition.is_file():
            continue
        text = edition.read_text(encoding="utf-8")
        for token in expected_tokens:
            if token not in text:
                errors.append(f"missing-token:{edition.relative_to(ROOT)}:{token}")

    return schedule, errors


def validate_git(schedule: dict[str, object]) -> list[str]:
    errors: list[str] = []
    repository = schedule.get("repository")
    assets = schedule.get("assets")
    if not isinstance(repository, dict) or not isinstance(assets, list):
        return ["cannot run Git verification on malformed schedule"]

    baseline = repository.get("baseline_commit_sha")
    manifest_path = repository.get("baseline_manifest_path")
    expected_manifest_sha = repository.get("baseline_manifest_sha256")
    expected_files_count = repository.get("baseline_manifest_files_count")
    if not all(
        isinstance(value, str)
        for value in (baseline, manifest_path, expected_manifest_sha)
    ) or not isinstance(expected_files_count, int):
        return ["invalid baseline identity"]

    assert isinstance(baseline, str)
    assert isinstance(manifest_path, str)
    assert isinstance(expected_manifest_sha, str)

    if git("cat-file", "-e", f"{baseline}^{{commit}}").returncode != 0:
        return [f"baseline commit is not reachable: {baseline}"]

    manifest_result = git("show", f"{baseline}:{manifest_path}")
    if manifest_result.returncode != 0:
        errors.append(f"baseline manifest is unavailable: {manifest_path}")
    else:
        observed_sha = sha256_bytes(manifest_result.stdout)
        if observed_sha != expected_manifest_sha:
            errors.append(
                "baseline manifest SHA-256 differs: "
                f"observed={observed_sha}; expected={expected_manifest_sha}"
            )
        try:
            manifest = json.loads(manifest_result.stdout)
        except Exception as error:
            errors.append(f"baseline manifest JSON invalid: {error}")
        else:
            if manifest.get("files_count") != expected_files_count:
                errors.append(
                    "baseline manifest file count differs: "
                    f"observed={manifest.get('files_count')}; "
                    f"expected={expected_files_count}"
                )

    paths = {
        path
        for asset in assets
        if isinstance(asset, dict)
        for path in asset.get("paths", [])
        if isinstance(path, str)
    }
    for relative in sorted(paths):
        if git("cat-file", "-e", f"{baseline}:{relative}").returncode != 0:
            errors.append(f"scheduled path absent from baseline:{relative}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-git", action="store_true")
    args = parser.parse_args()

    schedule, errors = validate_static()
    if not errors and args.check_git:
        errors.extend(validate_git(schedule))

    if errors:
        for error in errors:
            print(f"BACKGROUND_IP_ERROR={error}")
        print("BACKGROUND_IP_VALIDATION=FAIL")
        return 1

    print("BACKGROUND_IP_SCHEMA=PASS")
    print("BACKGROUND_IP_STATIC_DOCS=PASS")
    print("BACKGROUND_IP_ASSET_PATHS=PASS")
    if args.check_git:
        print("BACKGROUND_IP_BASELINE_GIT=PASS")
    print("BACKGROUND_IP_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

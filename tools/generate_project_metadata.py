from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "metadata/project.json"
SCHEMA = ROOT / "metadata/project.schema.json"
CODEMETA = ROOT / "codemeta.json"
REPOSITORY_METADATA = ROOT / ".github/repository-metadata.json"
GENERATED_DOCS_README = ROOT / "docs/generated/README.md"
TOPIC_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, object]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=strict_object,
    )
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def canonical_json(value: object) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        indent=2,
        allow_nan=False,
    ) + "\n"


def validate_source(source: dict[str, object]) -> None:
    schema = load_json(SCHEMA)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(
        validator.iter_errors(source),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        messages = []
        for error in errors:
            location = "/".join(str(item) for item in error.absolute_path)
            messages.append(f"{location or '<root>'}: {error.message}")
        raise ValueError("; ".join(messages))

    description = str(source["description"])
    about = source["about"]
    assert isinstance(about, dict)
    if description != about["description"]:
        raise ValueError("description and about.description must be identical")
    if not description.startswith("ASET "):
        raise ValueError("description must begin with the project name ASET")
    if str(source["expanded_name"]) not in description:
        raise ValueError("description must name Authority-Signed Evidence Trail")

    topics = about["topics"]
    assert isinstance(topics, list)
    for topic in topics:
        if not isinstance(topic, str) or not TOPIC_PATTERN.fullmatch(topic):
            raise ValueError(f"invalid GitHub topic: {topic!r}")


def codemeta(source: dict[str, object]) -> dict[str, object]:
    repository = source["repository"]
    release = source["release"]
    publisher = source["publisher"]
    about = source["about"]
    assert isinstance(repository, dict)
    assert isinstance(release, dict)
    assert isinstance(publisher, dict)
    assert isinstance(about, dict)

    organization = {
        "@type": publisher["type"],
        "name": publisher["name"],
        "url": publisher["url"],
    }
    return {
        "@context": "https://w3id.org/codemeta/3.1",
        "@id": repository["url"],
        "@type": "SoftwareSourceCode",
        "abstract": source["abstract"],
        "alternateName": source["expanded_name"],
        "author": organization,
        "codeRepository": repository["url"],
        "copyrightHolder": organization,
        "datePublished": release["date_released"],
        "description": source["description"],
        "developmentStatus": release["development_status"],
        "identifier": source["name"],
        "inLanguage": source["languages"],
        "isAccessibleForFree": True,
        "issueTracker": repository["issues"],
        "keywords": about["topics"],
        "license": "https://spdx.org/licenses/Apache-2.0.html",
        "maintainer": organization,
        "name": source["name"],
        "programmingLanguage": source["programming_languages"],
        "runtimePlatform": source["runtime_platform"],
        "url": repository["url"],
        "version": release["version"],
    }


def repository_metadata(source: dict[str, object]) -> dict[str, object]:
    repository = source["repository"]
    about = source["about"]
    assert isinstance(repository, dict)
    assert isinstance(about, dict)
    return {
        "description": about["description"],
        "repository": repository["slug"],
        "topics": about["topics"],
    }


def generated_docs_readme() -> str:
    return "\n".join(
        [
            "# Generated repository views",
            "",
            "Files under this directory are deterministic derived representations.",
            "They must not be edited manually.",
            "",
            "The generated language editions are derived from the normative machine canons.",
            "Project discovery metadata is derived from `metadata/project.json` into",
            "`codemeta.json` and `.github/repository-metadata.json`.",
            "",
            "Regenerate every derived repository view with:",
            "",
            "```text",
            "python tools/generate_repository_views.py",
            "```",
            "",
            "Check committed parity without changing files with:",
            "",
            "```text",
            "python tools/generate_repository_views.py --check",
            "```",
            "",
            "ASET Seed 0.1-rc11 remains the immutable current stable release until",
            "rc12 exact release bytes complete every mandatory gate and are separately frozen.",
            "",
        ]
    )


def expected_outputs(source: dict[str, object]) -> dict[Path, str]:
    return {
        CODEMETA: canonical_json(codemeta(source)),
        REPOSITORY_METADATA: canonical_json(repository_metadata(source)),
        GENERATED_DOCS_README: generated_docs_readme(),
    }


def generate() -> int:
    source = load_json(SOURCE)
    validate_source(source)
    outputs = expected_outputs(source)
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    print(f"PROJECT_METADATA_GENERATED={len(outputs)}")
    return 0


def check() -> int:
    source = load_json(SOURCE)
    validate_source(source)
    failures: list[str] = []
    for path, expected in expected_outputs(source).items():
        if not path.is_file():
            failures.append(f"missing:{path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            failures.append(f"different:{path.relative_to(ROOT)}")
    if failures:
        for failure in failures:
            print(f"ERROR={failure}")
        return 1
    print("PROJECT_METADATA_PARITY=PASS")
    return 0


def apply_github_about() -> int:
    source = load_json(SOURCE)
    validate_source(source)
    repository = source["repository"]
    about = source["about"]
    assert isinstance(repository, dict)
    assert isinstance(about, dict)

    gh = shutil.which("gh")
    if gh is None:
        print("ERROR=gh command not found")
        return 1

    description_command = [
        gh,
        "api",
        "--method",
        "PATCH",
        f"repos/{repository['slug']}",
        "-f",
        f"description={about['description']}",
    ]
    result = subprocess.run(description_command, cwd=ROOT, check=False)
    if result.returncode != 0:
        return result.returncode or 1

    topics_command = [
        gh,
        "api",
        "--method",
        "PUT",
        f"repos/{repository['slug']}/topics",
        "--input",
        "-",
    ]
    topics_payload = canonical_json({"names": about["topics"]})
    result = subprocess.run(
        topics_command,
        cwd=ROOT,
        input=topics_payload,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return result.returncode or 1
    print("GITHUB_ABOUT_APPLIED=PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--apply-github", action="store_true")
    args = parser.parse_args()

    if args.check and args.apply_github:
        parser.error("--check and --apply-github are mutually exclusive")
    if args.check:
        return check()
    status = generate()
    if status != 0 or not args.apply_github:
        return status
    return apply_github_about()


if __name__ == "__main__":
    raise SystemExit(main())

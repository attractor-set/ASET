from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import io
import json
import re
import stat
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

EXPECTED_ROOT = "ASET/"
EXPECTED_BUNDLE_SHA256 = (
    "a0a534125e27f491747dc46f080f418226798dadadee31d5d55b495e6e18ab43"
)
EXPECTED_DOCUMENTATION_SHA256 = (
    "3a2f06183790dd6ec06b1d2ad47653aa368ee9e62a1ec71f76c60cab508b5600"
)
DOCUMENTATION_NAME = "ASET-Seed-Documentation-v0.1-rc11.zip"
DOCUMENTATION_ROOT = "ASET-Seed-Documentation-v0.1-rc11/"
TEXT_SUFFIXES = {
    ".md",
    ".txt",
    ".json",
    ".py",
    ".toml",
    ".yml",
    ".yaml",
    ".ttl",
    ".tla",
    ".cfg",
    ".csv",
    ".cff",
    ".xml",
    ".tbx",
}
SECRET_PATTERNS = {
    "github_token": re.compile(
        r"(?:github_pat_[A-Za-z0-9_]{20,}|gh[pousr]_[A-Za-z0-9]{20,})"
    ),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "private_key": re.compile(r"BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY"),
}


@dataclass
class Check:
    id: str
    name: str
    status: str
    details: str


class Audit:
    def __init__(self) -> None:
        self.checks: list[Check] = []

    def record(self, identifier: str, name: str, passed: bool, details: str) -> None:
        self.checks.append(
            Check(
                identifier,
                name,
                "PASS" if passed else "FAIL",
                details,
            )
        )

    @property
    def passed(self) -> bool:
        return all(check.status == "PASS" for check in self.checks)


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def strict_json(data: bytes) -> object:
    return json.loads(data.decode("utf-8"), object_pairs_hook=strict_object)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_json_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def safe_zip(archive: zipfile.ZipFile) -> tuple[list[zipfile.ZipInfo], list[str]]:
    errors: list[str] = []
    seen: set[str] = set()
    members: list[zipfile.ZipInfo] = []
    for info in archive.infolist():
        path = PurePosixPath(info.filename)
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"unsafe:{info.filename}")
        if info.filename in seen:
            errors.append(f"duplicate:{info.filename}")
        seen.add(info.filename)
        members.append(info)
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            errors.append(f"symlink:{info.filename}")
    bad = archive.testzip()
    if bad is not None:
        errors.append(f"crc:{bad}")
    return members, errors


def extract_files(archive: zipfile.ZipFile) -> dict[str, bytes]:
    return {
        info.filename: archive.read(info)
        for info in archive.infolist()
        if not info.is_dir()
    }


def local_markdown_links(text: str) -> list[str]:
    result: list[str] = []
    for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
        target = target.strip().split()[0].strip("<>")
        if not target or target.startswith(("#", "http://", "https://", "mailto:")):
            continue
        result.append(target.split("#", 1)[0])
    return result


def audit_snapshot(snapshot: Path) -> dict[str, object]:
    audit = Audit()
    archive_bytes = snapshot.read_bytes()
    archive_digest = sha256(archive_bytes)

    try:
        with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
            members, zip_errors = safe_zip(archive)
            files = extract_files(archive)
    except Exception as error:
        audit.record("BB-001", "snapshot ZIP integrity", False, str(error))
        return report(audit, snapshot, archive_digest)

    audit.record(
        "BB-001",
        "snapshot ZIP integrity",
        not zip_errors,
        "ok" if not zip_errors else "; ".join(zip_errors),
    )

    names = [info.filename for info in members]
    root_ok = (
        all(name.startswith(EXPECTED_ROOT) for name in names)
        and names == sorted(names)
    )
    fixed_time_ok = all(
        info.date_time == (1980, 1, 1, 0, 0, 0)
        for info in members
        if not info.is_dir()
    )
    excluded_ok = not any(
        any(
            part
            in {
                ".git",
                ".venv",
                "dist",
                "__pycache__",
                ".pytest_cache",
                ".ruff_cache",
            }
            for part in PurePosixPath(name).parts
        )
        for name in names
    )
    audit.record(
        "BB-002",
        "deterministic archive profile",
        root_ok and fixed_time_ok and excluded_ok,
        (
            f"sorted_root={root_ok}; fixed_time={fixed_time_ok}; "
            f"excluded={excluded_ok}"
        ),
    )

    def file(relative: str) -> bytes:
        return files[EXPECTED_ROOT + relative]

    # Manifest
    try:
        manifest = strict_json(file("MANIFEST.json"))
        assert isinstance(manifest, dict)
        entries = {item["path"]: item for item in manifest["files"]}
        expected_snapshot_files = {
            name[len(EXPECTED_ROOT) :]
            for name in files
            if name != EXPECTED_ROOT + "MANIFEST.json"
        }
        manifest_ok = set(entries) == expected_snapshot_files
        mismatches: list[str] = []
        for relative, entry in entries.items():
            data = file(relative)
            if entry.get("size_bytes") != len(data):
                mismatches.append(f"size:{relative}")
            if entry.get("sha256") != "sha256:" + sha256(data):
                mismatches.append(f"sha256:{relative}")
        manifest_ok = (
            manifest_ok
            and not mismatches
            and manifest.get("files_count") == len(entries)
        )
        details = (
            f"entries={len(entries)}; "
            f"scope_exact={set(entries) == expected_snapshot_files}; "
            f"mismatches={len(mismatches)}"
        )
    except Exception as error:
        manifest_ok = False
        details = str(error)
    audit.record("BB-003", "manifest exact scope and digests", manifest_ok, details)

    # License and citation
    try:
        license_text = file("LICENSE").decode("utf-8")
        license_ok = len(license_text.encode("utf-8")) > 10000 and all(
            marker in license_text
            for marker in (
                "Apache License",
                "Version 2.0, January 2004",
                "END OF TERMS AND CONDITIONS",
                "APPENDIX: How to apply the Apache License to your work.",
            )
        )
    except Exception as error:
        license_ok = False
        license_text = str(error)
    license_size = (
        len(license_text.encode("utf-8"))
        if isinstance(license_text, str)
        else 0
    )
    audit.record(
        "BB-004",
        "full Apache-2.0 license",
        license_ok,
        f"size={license_size}",
    )

    try:
        citation = file("CITATION.cff").decode("utf-8")
        citation_ok = (
            'repository-code: "https://github.com/attractor-set/ASET"'
            in citation
            and "REPLACE_" not in citation
        )
    except Exception as error:
        citation_ok = False
        citation = str(error)
    audit.record(
        "BB-005",
        "citation repository identity",
        citation_ok,
        "expected repository-code present" if citation_ok else citation[:200],
    )

    # Status boundaries
    try:
        status = strict_json(file("REPOSITORY_STATUS.json"))
        assert isinstance(status, dict)
        status_ok = (
            status.get("repository_production_readiness")
            == "DOCUMENTATION_REPOSITORY_PRODUCTION_READY"
            and status.get("current_stable_seed_release") == "0.1-rc11"
            and status.get("seed_runtime_production") == "HOLD"
            and status.get("next_seed_status") == "BOOTSTRAP_SCAFFOLD_NOT_RELEASED"
            and status.get("external_third_party_audit") == "PENDING"
            and status.get("assurance_boundary", {}).get(
                "repository_publication_and_documentation_operations"
            )
            == "PRODUCTION_READY"
            and status.get("assurance_boundary", {}).get(
                "seed_runtime_or_deployment"
            )
            == "NOT_CLAIMED"
        )
        details = json.dumps(status.get("assurance_boundary", {}), sort_keys=True)
    except Exception as error:
        status_ok = False
        details = str(error)
    audit.record("BB-006", "readiness claim separation", status_ok, details)

    # Gates and findings
    try:
        gates = strict_json(
            file(
                "seed/canonical/assurance/"
                "repository-release-gates.json"
            )
        )
        assert isinstance(gates, dict)
        gate_items = gates.get("gates", [])
        gate_ids = [item["id"] for item in gate_items]
        gates_ok = (
            gates.get("fail_closed") is True
            and len(gate_items) >= 10
            and len(gate_ids) == len(set(gate_ids))
            and all(item.get("mandatory") is True for item in gate_items)
        )
        details = f"mandatory_gates={len(gate_items)}"
    except Exception as error:
        gates_ok = False
        details = str(error)
    audit.record("BB-007", "fail-closed release gates", gates_ok, details)

    try:
        findings = strict_json(file("audit/FINDING_CLOSURE_MATRIX.json"))
        assert isinstance(findings, dict)
        open_findings = findings.get("open_blocking_findings", [])
        findings_ok = open_findings == []
        details = f"open_blocking={len(open_findings)}"
    except Exception as error:
        findings_ok = False
        details = str(error)
    audit.record("BB-008", "zero unresolved blocking findings", findings_ok, details)

    # Frozen and expanded rc11
    try:
        bundle_data = file(
            "seed/releases/0.1-rc11/delivery/"
            "ASET-Seed-v0.1-rc11-Complete-Release-Bundle.zip"
        )
        bundle_ok = sha256(bundle_data) == EXPECTED_BUNDLE_SHA256
        with zipfile.ZipFile(io.BytesIO(bundle_data)) as bundle:
            _, nested_errors = safe_zip(bundle)
            documentation_data = bundle.read(DOCUMENTATION_NAME)
        documentation_ok = (
            not nested_errors
            and sha256(documentation_data)
            == EXPECTED_DOCUMENTATION_SHA256
        )
        with zipfile.ZipFile(io.BytesIO(documentation_data)) as docs:
            doc_members, doc_errors = safe_zip(docs)
            expected_expanded = {
                info.filename[len(DOCUMENTATION_ROOT) :]: docs.read(info)
                for info in doc_members
                if not info.is_dir() and info.filename.startswith(DOCUMENTATION_ROOT)
            }
        observed_expanded = {
            name[len(EXPECTED_ROOT + "seed/releases/0.1-rc11/expanded/") :]: data
            for name, data in files.items()
            if name.startswith(EXPECTED_ROOT + "seed/releases/0.1-rc11/expanded/")
        }
        expanded_ok = (
            not doc_errors
            and set(expected_expanded) == set(observed_expanded)
            and all(
                expected_expanded[name] == observed_expanded[name]
                for name in expected_expanded
            )
        )
        rc11_ok = bundle_ok and documentation_ok and expanded_ok
        details = (
            f"bundle={bundle_ok}; documentation={documentation_ok}; "
            f"files={len(expected_expanded)}; expanded={expanded_ok}"
        )
    except Exception as error:
        rc11_ok = False
        details = str(error)
    audit.record("BB-009", "frozen and expanded rc11 byte identity", rc11_ok, details)

    # rc11 requirements / traceability / cases
    try:
        req_data = strict_json(
            file(
                "seed/releases/0.1-rc11/expanded/requirements/"
                "requirements_register.json"
            )
        )
        assert isinstance(req_data, dict)
        req_ids = {item["id"] for item in req_data["requirements"]}
        trace_rows = list(
            csv.DictReader(
                io.StringIO(
                    file(
                        "seed/releases/0.1-rc11/expanded/"
                        "requirements/traceability_matrix.csv"
                    ).decode("utf-8-sig")
                )
            )
        )
        trace_ids = {row["requirement_id"] for row in trace_rows}
        verification_rows = list(
            csv.DictReader(
                io.StringIO(
                    file(
                        "seed/releases/0.1-rc11/expanded/"
                        "requirements/verification_cases.csv"
                    ).decode("utf-8-sig")
                )
            )
        )
        positive = strict_json(
            file(
                "seed/releases/0.1-rc11/expanded/conformance/"
                "positive-index.json"
            )
        )
        negative = strict_json(
            file(
                "seed/releases/0.1-rc11/expanded/conformance/"
                "negative-index.json"
            )
        )
        assert isinstance(positive, dict) and isinstance(negative, dict)
        case_paths = {row["path"] for row in verification_rows}
        requirement_ok = (
            req_ids == trace_ids
            and len(req_ids) == 26
            and len(verification_rows) == 55
            and len(case_paths) == 55
        )
        details = (
            f"requirements={len(req_ids)}; "
            f"traceability={len(trace_ids)}; "
            f"cases={len(verification_rows)}"
        )
    except Exception as error:
        requirement_ok = False
        details = str(error)
    audit.record(
        "BB-010",
        "rc11 requirements and traceability identity",
        requirement_ok,
        details,
    )

    # Strict JSON and Python syntax
    json_errors: list[str] = []
    for name, data in files.items():
        if name.endswith(".json"):
            try:
                strict_json(data)
            except Exception as error:
                json_errors.append(f"{name}:{error}")
    json_count = sum(1 for name in files if name.endswith(".json"))
    audit.record(
        "BB-011",
        "strict JSON corpus",
        not json_errors,
        f"json_files={json_count}; errors={len(json_errors)}",
    )

    syntax_errors: list[str] = []
    for name, data in files.items():
        if name.endswith(".py"):
            try:
                ast.parse(data.decode("utf-8"), filename=name)
            except Exception as error:
                syntax_errors.append(f"{name}:{error}")
    python_count = sum(1 for name in files if name.endswith(".py"))
    audit.record(
        "BB-012",
        "tracked Python syntax",
        not syntax_errors,
        f"python_files={python_count}; errors={len(syntax_errors)}",
    )

    # Generated editions
    try:
        model = strict_json(file("seed/canonical/source/seed-model.json"))
        assert isinstance(model, dict)
        digest = sha256(canonical_json_bytes(model))
        expected_ids = (
            {item["id"] for item in model["concepts"]}
            | {item["id"] for item in model["requirements"]}
            | {item["id"] for item in model["invariants"]}
        )
        edition_ok = True
        edition_details: list[str] = []
        policy = strict_json(file("seed/canonical/terminology/foreign-terms.json"))
        assert isinstance(policy, dict)
        for language in ("ru", "en", "pt-BR"):
            text = file(f"docs/generated/{language}/ASET_Seed_Next.md").decode("utf-8")
            present_ids = {
                identifier
                for identifier in expected_ids
                if identifier in text
            }
            language_ok = (
                model["version"] in text
                and model["status"] in text
                and f"sha256:{digest}" in text
                and present_ids == expected_ids
            )
            for rule in policy["languages"][language]:
                term = rule["forbidden"]
                pattern = re.compile(
                    rf"(?<!\w){re.escape(term)}(?!\w)",
                    re.IGNORECASE | re.UNICODE,
                )
                if pattern.search(text):
                    language_ok = False
            edition_ok = edition_ok and language_ok
            edition_details.append(
                f"{language}={language_ok}:"
                f"{len(present_ids)}/{len(expected_ids)}"
            )
        details = "; ".join(edition_details)
    except Exception as error:
        edition_ok = False
        details = str(error)
    audit.record("BB-013", "generated edition semantic parity", edition_ok, details)

    # Migration disposition
    try:
        coverage = strict_json(
            file(
                "seed/canonical/migration/"
                "RC11_TO_RC12_SEMANTIC_COVERAGE.json"
            )
        )
        assert isinstance(coverage, dict)
        summary = coverage["summary"]
        migration_ok = (
            summary["rc11_requirements"] == 26
            and summary["rc11_transition_kinds"] == 18
            and summary["rc11_schemas"] == 39
            and summary["unclassified"] == 0
            and coverage["target_status"] == "BOOTSTRAP_SCAFFOLD_NOT_RELEASED"
        )
        details = json.dumps(summary, sort_keys=True)
    except Exception as error:
        migration_ok = False
        details = str(error)
    audit.record("BB-014", "rc11-to-rc12 explicit disposition", migration_ok, details)

    # Required docs and local links
    required = {
        "README.md",
        "README.ru.md",
        "README.pt-BR.md",
        "docs/repository/PRODUCTION_READINESS.md",
        "docs/repository/RELEASE_PROCESS.md",
        "docs/repository/BLACK_BOX_AUDIT_METHOD.md",
        "docs/repository/OPERATIONS_RUNBOOK.md",
        "docs/repository/DEPENDENCY_POLICY.md",
        "audit/PDCA_HISTORY.md",
        "audit/FINDING_CLOSURE_MATRIX.json",
        "seed/canonical/decisions/ADR-001-semantic-canon-authority.md",
    }
    missing_required = sorted(
        path for path in required if EXPECTED_ROOT + path not in files
    )
    audit.record(
        "BB-015",
        "mandatory operational documentation",
        not missing_required,
        f"missing={missing_required}",
    )

    link_errors: list[str] = []
    active_markdown = [
        name
        for name in files
        if name.endswith(".md")
        and not name.startswith(EXPECTED_ROOT + "seed/releases/0.1-rc11/expanded/")
        and not name.startswith(EXPECTED_ROOT + "seed/releases/0.1-rc11/materialized/")
    ]
    for name in active_markdown:
        text = files[name].decode("utf-8")
        base = PurePosixPath(name).parent
        for target in local_markdown_links(text):
            normalized = str(PurePosixPath(base / target))
            if normalized not in files and not any(
                other.startswith(normalized.rstrip("/") + "/")
                for other in files
            ):
                link_errors.append(f"{name}->{target}")
    audit.record(
        "BB-016",
        "active documentation local links",
        not link_errors,
        f"documents={len(active_markdown)}; errors={len(link_errors)}",
    )

    # Secret scan and whitespace on active source
    secret_hits: list[str] = []
    whitespace_hits: list[str] = []
    for name, data in files.items():
        relative = name[len(EXPECTED_ROOT) :]
        suffix = PurePosixPath(name).suffix.lower()
        active = not relative.startswith(
            (
                "seed/releases/0.1-rc11/expanded/",
                "seed/releases/0.1-rc11/materialized/",
                "seed/releases/0.1-rc11/delivery/",
            )
        )
        if not active or suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                secret_hits.append(f"{relative}:{label}")
        for number, line in enumerate(text.splitlines(), start=1):
            if line.rstrip() != line:
                whitespace_hits.append(f"{relative}:{number}")
    audit.record(
        "BB-017",
        "common secret-pattern scan",
        not secret_hits,
        f"hits={len(secret_hits)}",
    )
    audit.record(
        "BB-018",
        "active-source trailing whitespace",
        not whitespace_hits,
        f"hits={len(whitespace_hits)}",
    )

    # Workflows
    try:
        seed_ci = file(".github/workflows/seed-ci.yml").decode("utf-8")
        production_ci = file(
            ".github/workflows/production-assurance.yml"
        ).decode("utf-8")
        workflows_ok = all(
            token in seed_ci
            for token in (
                "pull_request:",
                "push:",
                "blackbox_documentation_audit.py",
                "permissions:\n  contents: read",
            )
        ) and all(
            token in production_ci
            for token in (
                "production_gate.py",
                "if: always()",
                "contents: read",
            )
        )
        details = "mandatory triggers, least privileges and black-box gates present"
    except Exception as error:
        workflows_ok = False
        details = str(error)
    audit.record("BB-019", "continuous assurance workflow", workflows_ok, details)

    return report(audit, snapshot, archive_digest)


def report(audit: Audit, snapshot: Path, digest: str) -> dict[str, object]:
    passed = sum(check.status == "PASS" for check in audit.checks)
    failed = sum(check.status == "FAIL" for check in audit.checks)
    return {
        "document_type": "aset-blackbox-documentation-audit",
        "version": 1,
        "audit_boundary": "snapshot-only; no import of repository validation modules",
        "snapshot": snapshot.name,
        "snapshot_sha256": "sha256:" + digest,
        "verdict": "PASS" if audit.passed else "FAIL",
        "summary": {"passed": passed, "failed": failed, "total": len(audit.checks)},
        "checks": [asdict(check) for check in audit.checks],
    }


def markdown_report(data: dict[str, object]) -> str:
    lines = [
        "# ASET black-box documentation audit",
        "",
        f"Verdict: **{data['verdict']}**",
        "",
        f"Snapshot SHA-256: `{data['snapshot_sha256']}`",
        "",
        "| ID | Check | Status | Details |",
        "|---|---|---|---|",
    ]
    for check in data["checks"]:
        details = str(check["details"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {check['id']} | {check['name']} | "
            f"{check['status']} | {details} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()

    snapshot = Path(args.snapshot)
    if not snapshot.is_file():
        print(f"BLACKBOX_FATAL=snapshot missing: {snapshot}")
        return 1

    data = audit_snapshot(snapshot)
    text = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    md = markdown_report(data)

    if args.output_json:
        path = Path(args.output_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
    if args.output_md:
        path = Path(args.output_md)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(md, encoding="utf-8", newline="\n")

    for check in data["checks"]:
        print(f"{check['id']}={check['status']}:{check['name']}")
    print(f"BLACKBOX_PASSED={data['summary']['passed']}")
    print(f"BLACKBOX_FAILED={data['summary']['failed']}")
    print(f"BLACKBOX_DOCUMENTATION_AUDIT={data['verdict']}")
    return 0 if data["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

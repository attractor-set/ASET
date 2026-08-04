from __future__ import annotations

import argparse
import hashlib
import json
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXED = (1980, 1, 1, 0, 0, 0)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_snapshot(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {
            info.filename: archive.read(info)
            for info in archive.infolist()
            if not info.is_dir()
        }


def rebuild_manifest(files: dict[str, bytes]) -> None:
    prefix = "ASET/"
    entries = []
    for name in sorted(files):
        if name == prefix + "MANIFEST.json":
            continue
        relative = name[len(prefix) :]
        entries.append(
            {
                "path": relative,
                "sha256": "sha256:" + sha256(files[name]),
                "size_bytes": len(files[name]),
            }
        )
    manifest = {
        "document_type": "aset-repository-bootstrap-manifest",
        "files": entries,
        "files_count": len(entries),
        "manifest_scope": (
            "all repository regular files except MANIFEST.json, "
            "Git metadata, virtual environments, caches and dist"
        ),
        "package": "ASET-Seed-0.1-rc12-Production-Candidate",
        "repository_root": "ASET",
    }
    files[prefix + "MANIFEST.json"] = (
        json.dumps(
            manifest,
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )
        + "\n"
    ).encode("utf-8")


def write_snapshot(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(
        path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, FIXED)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, files[name])


def mutate_missing_required(files: dict[str, bytes]) -> None:
    del files["ASET/docs/repository/PRODUCTION_READINESS.md"]


def mutate_generated_drift(files: dict[str, bytes]) -> None:
    name = "ASET/docs/generated/en/ASET_Seed_Next.md"
    files[name] = files[name].replace(
        b"SEED-REQ-001",
        b"SEED-REQ-X01",
        1,
    )


def mutate_expanded_rc11(files: dict[str, bytes]) -> None:
    name = "ASET/seed/releases/0.1-rc11/expanded/README.md"
    files[name] += b"\nmodified frozen representation\n"


def mutate_secret(files: dict[str, bytes]) -> None:
    name = "ASET/README.md"
    token = b"gh" + b"p_" + b"0123456789abcdefghijklmnopqrstuv"
    files[name] += b"\n" + token + b"\n"


def mutate_status_overclaim(files: dict[str, bytes]) -> None:
    name = "ASET/REPOSITORY_STATUS.json"
    data = json.loads(files[name].decode("utf-8"))
    data["seed_runtime_production"] = "UNIVERSAL_DISTRIBUTED_PRODUCTION_READY"
    files[name] = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")


def mutate_open_finding(files: dict[str, bytes]) -> None:
    name = "ASET/audit/FINDING_CLOSURE_MATRIX.json"
    data = json.loads(files[name].decode("utf-8"))
    data["open_blocking_findings"] = [
        {
            "id": "ADVERSARIAL-OPEN",
            "severity": "P0",
            "status": "OPEN",
        }
    ]
    files[name] = (
        json.dumps(data, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def mutate_git_normalization_policy(files: dict[str, bytes]) -> None:
    name = "ASET/.gitattributes"
    files[name] = files[name].replace(
        b"seed/releases/** -text -diff",
        b"seed/releases/** -diff",
        1,
    )


def mutate_migration_gap(files: dict[str, bytes]) -> None:
    name = "ASET/seed/canonical/migration/RC11_TO_RC12_SEMANTIC_COVERAGE.json"
    data = json.loads(files[name].decode("utf-8"))
    data["summary"]["fully_migrated_to_rc12"] = 82
    data["summary"]["unclassified"] = 1
    files[name] = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")


def mutate_protocol_schema(files: dict[str, bytes]) -> None:
    name = "ASET/src/aset_seed/schemas/transition.schema.json"
    files[name] += b" "


def mutate_runtime_missing(files: dict[str, bytes]) -> None:
    del files["ASET/src/aset_seed/runtime.py"]


def mutate_runtime_boundary(files: dict[str, bytes]) -> None:
    name = "ASET/seed/canonical/source/seed-model.json"
    data = json.loads(files[name].decode("utf-8"))
    data["runtime_profile"]["excluded"].remove("distributed consensus")
    text = json.dumps(data, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    files[name] = text.encode("utf-8")


def mutate_formal_missing(files: dict[str, bytes]) -> None:
    del files["ASET/seed/canonical/formal/SeedRC12.tla"]


def mutate_implicit_effect(files: dict[str, bytes]) -> None:
    name = "ASET/src/aset_seed/runtime.py"
    files[name] = b"import socket\n" + files[name]


def mutate_limitations(files: dict[str, bytes]) -> None:
    name = "ASET/seed/canonical/assurance/limitations.json"
    data = json.loads(files[name].decode("utf-8"))
    data["limitations"] = [item for item in data["limitations"] if item["id"] != "LIMIT-005"]
    files[name] = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")


def mutate_gate_registry(files: dict[str, bytes]) -> None:
    name = "ASET/seed/canonical/assurance/repository-release-gates.json"
    data = json.loads(files[name].decode("utf-8"))
    data["gates"] = [item for item in data["gates"] if item["name"] != "blackbox_runtime_audit"]
    files[name] = (json.dumps(data, sort_keys=True, indent=2) + "\n").encode("utf-8")


MUTATIONS = [
    ("missing_required_document", "BB-015", mutate_missing_required),
    ("generated_edition_drift", "BB-013", mutate_generated_drift),
    ("expanded_rc11_drift", "BB-009", mutate_expanded_rc11),
    ("common_secret", "BB-017", mutate_secret),
    ("runtime_overclaim", "BB-006", mutate_status_overclaim),
    ("open_blocking_finding", "BB-008", mutate_open_finding),
    ("git_normalization_policy", "BB-020", mutate_git_normalization_policy),
    ("migration_gap", "BB-014", mutate_migration_gap),
    ("protocol_schema_drift", "BB-022", mutate_protocol_schema),
    ("runtime_missing", "BB-023", mutate_runtime_missing),
    ("runtime_boundary_overclaim", "BB-024", mutate_runtime_boundary),
    ("formal_projection_missing", "BB-025", mutate_formal_missing),
    ("implicit_effect_adapter", "BB-026", mutate_implicit_effect),
    ("limitation_erased", "BB-027", mutate_limitations),
    ("gate_registry_incomplete", "BB-028", mutate_gate_registry),
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "snapshot",
        nargs="?",
        default="dist/ASET-Repository-Snapshot.zip",
    )
    parser.add_argument(
        "--output",
        default="dist/blackbox-adversarial-results.json",
    )
    args = parser.parse_args()

    snapshot = ROOT / args.snapshot
    if not snapshot.is_file():
        print(f"ADVERSARIAL_FATAL=missing snapshot:{snapshot}")
        return 1

    baseline = load_snapshot(snapshot)
    results: list[dict[str, object]] = []
    failed = False

    with tempfile.TemporaryDirectory(prefix="aset-blackbox-") as directory:
        temporary = Path(directory)
        for name, expected_check, mutation in MUTATIONS:
            files = dict(baseline)
            mutation(files)
            rebuild_manifest(files)
            candidate = temporary / f"{name}.zip"
            report_path = temporary / f"{name}.json"
            write_snapshot(candidate, files)
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools/blackbox_documentation_audit.py"),
                    str(candidate),
                    "--output-json",
                    str(report_path),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            report = json.loads(report_path.read_text(encoding="utf-8"))
            observed_failed = {
                item["id"]
                for item in report["checks"]
                if item["status"] == "FAIL"
            }
            passed = (
                result.returncode != 0
                and report["verdict"] == "FAIL"
                and expected_check in observed_failed
            )
            if not passed:
                failed = True
            results.append(
                {
                    "mutation": name,
                    "expected_failed_check": expected_check,
                    "observed_failed_checks": sorted(observed_failed),
                    "auditor_returncode": result.returncode,
                    "status": "PASS" if passed else "FAIL",
                }
            )
            print(
                f"ADVERSARIAL_{name.upper()}="
                f"{'PASS' if passed else 'FAIL'}"
            )

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "document_type": "aset-blackbox-adversarial-results",
        "version": 1,
        "verdict": "FAIL" if failed else "PASS",
        "mutations": results,
    }
    output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"BLACKBOX_ADVERSARIAL={payload['verdict']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

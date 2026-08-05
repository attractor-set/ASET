from __future__ import annotations

import argparse
import copy
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
PREFIX = "ASET/"


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def load_snapshot(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {
            info.filename: archive.read(info)
            for info in archive.infolist()
            if not info.is_dir()
        }


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


def json_document(files: dict[str, bytes], relative: str) -> dict[str, object]:
    value = json.loads(files[PREFIX + relative].decode("utf-8"))
    assert isinstance(value, dict)
    return value


def store_json(files: dict[str, bytes], relative: str, value: object) -> None:
    files[PREFIX + relative] = (
        json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")


def rebuild_manifest(files: dict[str, bytes]) -> None:
    entries = []
    for name in sorted(files):
        if name == PREFIX + "MANIFEST.json":
            continue
        relative = name[len(PREFIX) :]
        entries.append(
            {
                "path": relative,
                "sha256": sha256(files[name]),
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
        "package": "ASET-Seed-0.1-rc12-Specification-Candidate",
        "repository_root": "ASET",
    }
    store_json(files, "MANIFEST.json", manifest)


def mutate_component_digest(files: dict[str, bytes]) -> None:
    path = "aset/components/core/canonical/source/core-model.json"
    value = json_document(files, path)
    value["canonical_digest"] = "sha256:" + "0" * 64
    store_json(files, path, value)


def mutate_partition_gap(files: dict[str, bytes]) -> None:
    path = "aset/shared/migration/RC11_TO_COMPONENT_CANONS.json"
    value = json_document(files, path)
    del value["assignments"]["requirements"][0]
    store_json(files, path, value)


def mutate_seed_byte(files: dict[str, bytes]) -> None:
    path = PREFIX + "seed/canonical/source/seed-model.json"
    files[path] += b" "


def mutate_bridge_sequence(files: dict[str, bytes]) -> None:
    path = "aset/shared/seed-bridge/seed-compatibility-profile.json"
    value = json_document(files, path)
    del value["classification_rules"][4]["sequence"][2]
    store_json(files, path, value)


def mutate_conformance_missing(files: dict[str, bytes]) -> None:
    del files[PREFIX + "aset/shared/conformance/results.json"]


def mutate_formal_missing(files: dict[str, bytes]) -> None:
    del files[PREFIX + "aset/components/core/canonical/formal/core.tla"]


def mutate_open_schema(files: dict[str, bytes]) -> None:
    path = "aset/shared/schemas/component-canon.schema.json"
    value = json_document(files, path)
    value["$defs"]["contextComponent"]["additionalProperties"] = True
    store_json(files, path, value)


def mutate_duplicate_ownership(files: dict[str, bytes]) -> None:
    path = "aset/components/context/canonical/source/context-model.json"
    value = json_document(files, path)
    value["owns"].append("ContextProjection")
    store_json(files, path, value)


def mutate_localization_collapse(files: dict[str, bytes]) -> None:
    path = "aset/components/master/canonical/source/master-model.json"
    value = json_document(files, path)
    description = value["operations"][0]["description"]
    description["ru"] = description["en"]
    description["pt-BR"] = description["en"]
    store_json(files, path, value)


def mutate_assurance_missing(files: dict[str, bytes]) -> None:
    del files[PREFIX + "aset/components/memory/canonical/assurance/threat-model.json"]


def mutate_traceability_gap(files: dict[str, bytes]) -> None:
    path = "aset/components/monade/canonical/assurance/traceability.json"
    value = json_document(files, path)
    del value["links"][0]
    store_json(files, path, value)


def mutate_asset_pointer(files: dict[str, bytes]) -> None:
    path = "aset/components/protocol/canonical/source/protocol-model.json"
    value = json_document(files, path)
    value["canon_assets"]["requirements"] = "aset/missing/requirements.json"
    store_json(files, path, value)


MUTATIONS = (
    ("component_digest", "CB-005", mutate_component_digest),
    ("partition_gap", "CB-006", mutate_partition_gap),
    ("seed_byte_drift", "CB-007", mutate_seed_byte),
    ("bridge_sequence", "CB-008", mutate_bridge_sequence),
    ("conformance_missing", "CB-010", mutate_conformance_missing),
    ("formal_missing", "CB-011", mutate_formal_missing),
    ("open_meta_schema", "CB-016", mutate_open_schema),
    ("duplicate_ownership", "CB-021", mutate_duplicate_ownership),
    ("localization_collapse", "CB-022", mutate_localization_collapse),
    ("assurance_missing", "CB-023", mutate_assurance_missing),
    ("traceability_gap", "CB-024", mutate_traceability_gap),
    ("asset_pointer", "CB-025", mutate_asset_pointer),
)


def run_audit(snapshot: Path, directory: Path, label: str) -> dict[str, object]:
    output_json = directory / f"{label}.json"
    output_md = directory / f"{label}.md"
    result = subprocess.run(
        [
            sys.executable,
            "tools/blackbox_component_audit.py",
            str(snapshot),
            "--output-json",
            str(output_json),
            "--output-md",
            str(output_md),
            "--report-only",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stdout + result.stderr)
    value = json.loads(output_json.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "snapshot",
        nargs="?",
        default="dist/ASET-Repository-Snapshot.zip",
    )
    parser.add_argument(
        "--output",
        default="dist/component-blackbox-adversarial-results.json",
    )
    args = parser.parse_args()
    snapshot = ROOT / args.snapshot
    if not snapshot.is_file():
        print(f"COMPONENT_ADVERSARIAL_FATAL=missing snapshot:{snapshot}")
        return 1
    baseline_files = load_snapshot(snapshot)
    results: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="aset-component-adversarial-") as raw_directory:
        directory = Path(raw_directory)
        baseline_report = run_audit(snapshot, directory, "baseline")
        baseline_pass = baseline_report.get("verdict") == "PASS"
        results.append(
            {
                "id": "baseline",
                "expected_check": "ALL",
                "detected": baseline_pass,
                "details": f"verdict={baseline_report.get('verdict')}",
            }
        )
        for name, expected_check, mutation in MUTATIONS:
            files = copy.deepcopy(baseline_files)
            mutation(files)
            rebuild_manifest(files)
            candidate = directory / f"{name}.zip"
            write_snapshot(candidate, files)
            report = run_audit(candidate, directory, name)
            checks = {str(item["id"]): item for item in report["checks"]}
            detected = (
                report.get("verdict") == "FAIL"
                and checks.get(expected_check, {}).get("status") == "FAIL"
            )
            results.append(
                {
                    "id": name,
                    "expected_check": expected_check,
                    "detected": detected,
                    "details": (
                        f"verdict={report.get('verdict')}; "
                        f"check={checks.get(expected_check, {}).get('status')}"
                    ),
                }
            )
    failures = [item for item in results if not item["detected"]]
    report = {
        "document_type": "aset-component-blackbox-adversarial-results",
        "schema_version": 1,
        "baseline_snapshot": args.snapshot,
        "cases_total": len(results),
        "cases_passed": len(results) - len(failures),
        "cases_failed": len(failures),
        "verdict": "PASS" if not failures else "FAIL",
        "results": results,
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"COMPONENT_ADVERSARIAL={report['cases_passed']}/{report['cases_total']}")
    print(f"COMPONENT_ADVERSARIAL_VERDICT={report['verdict']}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

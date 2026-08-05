from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import stat
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import PurePosixPath

from jsonschema import Draft202012Validator
from rdflib import Graph

EXPECTED_ROOT = "ASET/"
COMPONENT_KEYS = (
    "context",
    "core",
    "gateway",
    "master",
    "memory",
    "monade",
    "protocol",
)
EXPECTED_COUNTS = {
    "requirements": 177,
    "invariants": 57,
    "artifacts": 52,
    "gates": 11,
    "schemas": 57,
}


@dataclass(frozen=True)
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
                id=identifier,
                name=name,
                status="PASS" if passed else "FAIL",
                details=details,
            )
        )


def strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def strict_json(data: bytes) -> object:
    return json.loads(data.decode("utf-8"), object_pairs_hook=strict_object)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def canonical_digest(value: dict[str, object]) -> str:
    material = dict(value)
    material.pop("canonical_digest", None)
    return "sha256:" + hashlib.sha256(canonical_bytes(material)).hexdigest()


def sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def report(audit: Audit, snapshot: str, archive_digest: str) -> dict[str, object]:
    failures = [check for check in audit.checks if check.status == "FAIL"]
    return {
        "document_type": "aset-component-canons-blackbox-audit",
        "schema_version": 1,
        "snapshot": snapshot,
        "snapshot_sha256": archive_digest,
        "method": (
            "standalone ZIP/JSON/Schema/RDF/TBX inspection; no imports from repository tools"
        ),
        "checks_total": len(audit.checks),
        "checks_passed": len(audit.checks) - len(failures),
        "checks_failed": len(failures),
        "verdict": "PASS" if not failures else "FAIL",
        "checks": [asdict(check) for check in audit.checks],
        "findings": [
            {
                "id": f"FINDING-{check.id}",
                "severity": "HIGH" if check.id in {"CB-010", "CB-011", "CB-012"} else "MEDIUM",
                "statement": check.details,
                "source_check": check.id,
                "status": "OPEN",
            }
            for check in failures
        ],
    }


def markdown(value: dict[str, object]) -> str:
    lines = [
        "# ASET component canons — independent black-box audit",
        "",
        f"- Verdict: **{value['verdict']}**",
        f"- Checks: `{value['checks_passed']}/{value['checks_total']}` passed",
        f"- Snapshot: `{value['snapshot']}`",
        f"- SHA-256: `{value['snapshot_sha256']}`",
        "",
        "| ID | Check | Status | Details |",
        "|---|---|---|---|",
    ]
    for check in value["checks"]:
        details = str(check["details"]).replace("|", "\\|").replace("\n", " ")
        lines.append(
            f"| {check['id']} | {check['name']} | {check['status']} | {details} |"
        )
    lines.extend(["", "## Findings", ""])
    if value["findings"]:
        for finding in value["findings"]:
            lines.append(
                f"- `{finding['id']}` ({finding['severity']}): {finding['statement']}"
            )
    else:
        lines.append("No open findings.")
    return "\n".join(lines).rstrip() + "\n"


def safe_archive(data: bytes) -> tuple[dict[str, bytes], list[zipfile.ZipInfo], list[str]]:
    errors: list[str] = []
    files: dict[str, bytes] = {}
    members: list[zipfile.ZipInfo] = []
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        seen: set[str] = set()
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"unsafe path:{info.filename}")
            if info.filename in seen:
                errors.append(f"duplicate member:{info.filename}")
            seen.add(info.filename)
            mode = info.external_attr >> 16
            if stat.S_ISLNK(mode):
                errors.append(f"symlink:{info.filename}")
            members.append(info)
            if not info.is_dir():
                files[info.filename] = archive.read(info)
        bad = archive.testzip()
        if bad:
            errors.append(f"CRC failure:{bad}")
    return files, members, errors


def audit_snapshot(snapshot_path: str) -> dict[str, object]:
    audit = Audit()
    raw = open(snapshot_path, "rb").read()
    archive_digest = sha256(raw)
    try:
        files, members, errors = safe_archive(raw)
    except Exception as error:
        audit.record("CB-001", "safe deterministic snapshot", False, str(error))
        return report(audit, snapshot_path, archive_digest)

    names = [member.filename for member in members]
    deterministic = (
        not errors
        and names == sorted(names)
        and all(name.startswith(EXPECTED_ROOT) for name in names)
        and all(
            member.date_time == (1980, 1, 1, 0, 0, 0)
            for member in members
            if not member.is_dir()
        )
    )
    audit.record(
        "CB-001",
        "safe deterministic snapshot",
        deterministic,
        "ok" if deterministic else "; ".join(errors or ["archive profile differs"]),
    )

    def get(relative: str) -> bytes:
        return files[EXPECTED_ROOT + relative]

    try:
        manifest = strict_json(get("MANIFEST.json"))
        assert isinstance(manifest, dict)
        entries = {str(item["path"]): item for item in manifest["files"]}
        expected = {
            name[len(EXPECTED_ROOT) :]
            for name in files
            if name != EXPECTED_ROOT + "MANIFEST.json"
        }
        mismatches: list[str] = []
        for path, entry in entries.items():
            data = get(path)
            if entry.get("size_bytes") != len(data):
                mismatches.append(f"size:{path}")
            if entry.get("sha256") != sha256(data):
                mismatches.append(f"sha256:{path}")
        manifest_ok = (
            set(entries) == expected
            and not mismatches
            and manifest.get("files_count") == len(entries)
        )
        details = f"entries={len(entries)}; mismatches={mismatches[:5]}"
    except Exception as error:
        manifest_ok = False
        details = str(error)
    audit.record("CB-002", "exact repository manifest", manifest_ok, details)

    json_errors: list[str] = []
    json_values: dict[str, object] = {}
    for name, data in files.items():
        if not name.startswith(EXPECTED_ROOT + "aset/") or not name.endswith(".json"):
            continue
        try:
            json_values[name[len(EXPECTED_ROOT) :]] = strict_json(data)
        except Exception as error:
            json_errors.append(f"{name}:{error}")
    audit.record(
        "CB-003",
        "strict component JSON corpus",
        not json_errors,
        f"documents={len(json_values)}; errors={json_errors[:5]}",
    )

    try:
        provenance = json_values["aset/source/rc11/SOURCE_PROVENANCE.json"]
        source_model = json_values["aset/source/rc11/aset-system-model-1.5-rc11.json"]
        source_spec = json_values[
            "aset/source/rc11/aset-system-specification-1.5-rc11.json"
        ]
        assert isinstance(provenance, dict)
        assert isinstance(source_model, dict)
        assert isinstance(source_spec, dict)
        source_ok = (
            provenance.get("source_archive_sha256")
            == "sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22"
            and provenance["source_model"]["sha256"]
            == sha256(get("aset/source/rc11/aset-system-model-1.5-rc11.json"))
            and provenance["source_specification"]["sha256"]
            == sha256(get("aset/source/rc11/aset-system-specification-1.5-rc11.json"))
            and source_model.get("canonical_digest")
            == provenance["source_model"]["canonical_digest"]
            and source_spec.get("canonical_digest")
            == provenance["source_specification"]["canonical_digest"]
        )
        details = (
            f"model={source_model.get('canonical_digest')}; "
            f"spec={source_spec.get('canonical_digest')}"
        )
    except Exception as error:
        source_ok = False
        details = str(error)
    audit.record("CB-004", "exact rc11 source provenance", source_ok, details)

    component_schema_path = "aset/shared/schemas/component-canon.schema.json"
    system_schema_path = "aset/shared/schemas/system-composition-canon.schema.json"
    bridge_schema_path = "aset/shared/schemas/seed-compatibility-profile.schema.json"
    migration_schema_path = "aset/shared/schemas/rc11-component-migration.schema.json"
    validation_errors: list[str] = []
    components: dict[str, dict[str, object]] = {}
    try:
        component_schema = json_values[component_schema_path]
        assert isinstance(component_schema, dict)
        for key in COMPONENT_KEYS:
            path = f"aset/components/{key}/canonical/source/{key}-model.json"
            value = json_values[path]
            assert isinstance(value, dict)
            components[key] = value
            for error in Draft202012Validator(component_schema).iter_errors(value):
                validation_errors.append(f"{key}:{error.message}")
            if value.get("canonical_digest") != canonical_digest(value):
                validation_errors.append(f"{key}:canonical digest")
        for schema_path, value_path in (
            (system_schema_path, "aset/system/canonical/source/system-composition-model.json"),
            (bridge_schema_path, "aset/shared/seed-bridge/seed-compatibility-profile.json"),
            (migration_schema_path, "aset/shared/migration/RC11_TO_COMPONENT_CANONS.json"),
        ):
            schema = json_values[schema_path]
            value = json_values[value_path]
            assert isinstance(schema, dict) and isinstance(value, dict)
            for error in Draft202012Validator(schema).iter_errors(value):
                validation_errors.append(f"{value_path}:{error.message}")
            if value.get("canonical_digest") != canonical_digest(value):
                validation_errors.append(f"{value_path}:canonical digest")
    except Exception as error:
        validation_errors.append(str(error))
    audit.record(
        "CB-005",
        "component schemas and canonical digests",
        not validation_errors,
        f"components={len(components)}; errors={validation_errors[:5]}",
    )

    partition_errors: list[str] = []
    try:
        migration = json_values["aset/shared/migration/RC11_TO_COMPONENT_CANONS.json"]
        assert isinstance(migration, dict)
        for kind, expected_count in EXPECTED_COUNTS.items():
            assignments = migration["assignments"][kind]
            identifiers = [str(item["id"]) for item in assignments]
            if len(identifiers) != expected_count or duplicates(identifiers):
                duplicate_ids = duplicates(identifiers)
                partition_errors.append(
                    f"{kind}:{len(identifiers)}/{expected_count}; "
                    f"duplicates={duplicate_ids}"
                )
        target_counts = Counter(
            str(item["target"])
            for kind in EXPECTED_COUNTS
            for item in migration["assignments"][kind]
        )
        details = "; ".join(
            f"{kind}={len(migration['assignments'][kind])}/{count}"
            for kind, count in EXPECTED_COUNTS.items()
        ) + f"; targets={dict(sorted(target_counts.items()))}"
    except Exception as error:
        partition_errors.append(str(error))
        details = str(error)
    audit.record("CB-006", "lossless rc11 partition", not partition_errors, details)

    seed_errors: list[str] = []
    try:
        baseline = json_values["aset/source/seed-rc12/SEED_RC12_BASELINE.json"]
        assert isinstance(baseline, dict)
        for entry in baseline["files"]:
            path = str(entry["path"])
            data = get(path)
            if len(data) != entry["size_bytes"] or sha256(data) != entry["sha256"]:
                seed_errors.append(path)
    except Exception as error:
        seed_errors.append(str(error))
    audit.record(
        "CB-007",
        "Seed RC12 exact-byte non-regression",
        not seed_errors,
        f"baseline_files=303; drift={seed_errors[:5]}",
    )

    bridge_errors: list[str] = []
    try:
        bridge = json_values["aset/shared/seed-bridge/seed-compatibility-profile.json"]
        assert isinstance(bridge, dict)
        rules = {
            str(item["classification"]): item
            for item in bridge["classification_rules"]
        }
        primitive_mappings = {
            str(item["aset_artifact"]): str(item["seed_primitive"])
            for item in bridge["primitive_mappings"]
        }
        external = rules["EXTERNAL_EFFECT"]
        required_sequence = [
            "Decision",
            "Permit",
            "PermitUseReceipt",
            "ExecutionIntent",
            "Observation",
            "Verification",
            "Outcome",
        ]
        if external["sequence"] != required_sequence:
            bridge_errors.append("external-effect sequence differs")
        if primitive_mappings["CoreResolution"] != "Decision":
            bridge_errors.append("CoreResolution mapping differs")
        if primitive_mappings["GateCrossingReceipt"] != "PermitUseReceipt":
            bridge_errors.append("receipt mapping differs")
        for key, component in components.items():
            for operation in component["operations"]:
                rule = rules[operation["classification"]]
                mapping = operation["seed_mapping"]
                for field in (
                    "seed_transition_required",
                    "sequence",
                    "outcome_recognition_required",
                ):
                    if mapping[field] != rule[field]:
                        bridge_errors.append(f"{key}:{operation['id']}:{field}")
    except Exception as error:
        bridge_errors.append(str(error))
    audit.record(
        "CB-008",
        "Seed RC12 semantic bridge",
        not bridge_errors,
        f"errors={bridge_errors[:5]}",
    )

    semantic_errors: list[str] = []
    generated_docs = [
        name
        for name in files
        if name.startswith(EXPECTED_ROOT + "docs/generated/")
        and re.search(r"ASET_.*_0\.1-rc1\.md$", name)
    ]
    for key in COMPONENT_KEYS:
        for relative in (
            f"aset/components/{key}/canonical/ontology/{key}.ttl",
            f"aset/components/{key}/canonical/terminology/{key}.skos.ttl",
            f"aset/components/{key}/canonical/shapes/{key}.shacl.ttl",
        ):
            try:
                Graph().parse(data=get(relative).decode("utf-8"), format="turtle")
            except Exception as error:
                semantic_errors.append(f"{relative}:{error}")
        try:
            ET.fromstring(get(f"aset/components/{key}/canonical/terminology/{key}.tbx"))
        except Exception as error:
            semantic_errors.append(f"{key}.tbx:{error}")
    audit.record(
        "CB-009",
        "generated multilingual and semantic views",
        len(generated_docs) == 24 and not semantic_errors,
        f"docs={len(generated_docs)}/24; semantic_errors={semantic_errors[:3]}",
    )

    conformance_required = (
        "aset/shared/conformance/component-conformance-profile.json",
        "aset/shared/conformance/positive/index.json",
        "aset/shared/conformance/negative/index.json",
        "aset/shared/conformance/results.json",
        "tools/run_component_conformance.py",
    )
    conformance_missing = [
        path
        for path in conformance_required
        if EXPECTED_ROOT + path not in files
    ]
    audit.record(
        "CB-010",
        "component conformance suite",
        not conformance_missing,
        "complete" if not conformance_missing else f"missing={conformance_missing}",
    )

    formal_required = [
        f"aset/components/{key}/canonical/formal/{key}.tla"
        for key in COMPONENT_KEYS
    ] + [
        "aset/system/canonical/formal/system-composition.tla",
        "aset/shared/formal/results.json",
        "tools/model_check_components.py",
    ]
    formal_missing = [path for path in formal_required if EXPECTED_ROOT + path not in files]
    audit.record(
        "CB-011",
        "bounded component formal models",
        not formal_missing,
        "complete" if not formal_missing else f"missing={formal_missing}",
    )

    try:
        validator_text = get("tools/validate_repository.py").decode("utf-8")
        generator_text = get("tools/generate_repository_views.py").decode("utf-8")
        gate_text = get("tools/production_gate.py").decode("utf-8")
        integration_markers = (
            "tools/validate_component_canons.py" in validator_text,
            "tools/generate_repository_views.py" in validator_text,
            "tools/generate_component_views.py" in generator_text,
            "tools/run_component_conformance.py" in gate_text,
            "tools/model_check_components.py" in gate_text,
            "tools/blackbox_component_audit.py" in gate_text,
        )
        integrated = all(integration_markers)
        details = f"markers={integration_markers}"
    except Exception as error:
        integrated = False
        details = str(error)
    audit.record("CB-012", "repository gate integration", integrated, details)

    boundary_errors: list[str] = []
    try:
        required_negative_rules = {
            "core": ("plan", "execute external effect", "accept result"),
            "master": ("issue Permit", "dispatch effect", "accept own work"),
            "memory": ("issue Permit", "own Task", "self-verify claims"),
        }
        for key, fragments in required_negative_rules.items():
            text = " ".join(str(item) for item in components[key]["must_not"])
            for fragment in fragments:
                if fragment not in text:
                    boundary_errors.append(f"{key}:{fragment}")
        if "Execution" not in " ".join(components["monade"]["owns"]):
            boundary_errors.append("monade execution ownership absent")
        if "Acceptance" not in " ".join(components["monade"]["owns"]):
            boundary_errors.append("monade acceptance ownership absent")
    except Exception as error:
        boundary_errors.append(str(error))
    audit.record(
        "CB-013",
        "module ownership and negative boundaries",
        not boundary_errors,
        f"errors={boundary_errors}",
    )

    try:
        system = json_values["aset/system/canonical/source/system-composition-model.json"]
        assert isinstance(system, dict)
        component_versions = {
            str(item["component_id"]): str(item["version"])
            for item in system["components"]
        }
        compatible = (
            len(component_versions) == 7
            and system["seed_compatibility"]["version"] == "0.1-rc12"
            and all(
                re.fullmatch(r"0\.1-rc[1-9][0-9]*", version)
                for version in component_versions.values()
            )
        )
        details = f"components={component_versions}; seed=0.1-rc12"
    except Exception as error:
        compatible = False
        details = str(error)
    audit.record("CB-014", "independent version compatibility", compatible, details)

    overclaim_errors: list[str] = []
    for key, component in components.items():
        assurance = component.get("assurance", {})
        if assurance.get("implementation_conformance") != "NOT_EXECUTED_PRE_IMPLEMENTATION":
            overclaim_errors.append(f"{key}:implementation")
        if assurance.get("production_conformance") != "HOLD":
            overclaim_errors.append(f"{key}:production")
        if not assurance.get("limitations"):
            overclaim_errors.append(f"{key}:limitations")
    audit.record(
        "CB-015",
        "assurance claims remain bounded",
        not overclaim_errors,
        f"errors={overclaim_errors}",
    )

    schema_closure_errors: list[str] = []
    try:
        component_schema = json_values[component_schema_path]
        system_schema = json_values[system_schema_path]
        assert isinstance(component_schema, dict) and isinstance(system_schema, dict)
        def resolve_local(
            schema: dict[str, object],
            definition: dict[str, object],
        ) -> dict[str, object]:
            reference = definition.get("$ref")
            if isinstance(reference, str) and reference.startswith("#/$defs/"):
                return schema["$defs"][reference.rsplit("/", 1)[-1]]
            return definition

        context_item = resolve_local(
            component_schema,
            component_schema["properties"]["context_components"]["items"],
        )
        if context_item.get("additionalProperties") is not False:
            schema_closure_errors.append("component context item is open")
        for field in (
            "compatibility_matrix",
            "context_namespace",
            "seed_compatibility",
            "source_baseline",
            "state_machines",
        ):
            definition = resolve_local(system_schema, system_schema["properties"][field])
            if definition.get("additionalProperties") is not False:
                schema_closure_errors.append(f"system {field} is open")
        for field in ("gates", "invariant_assignments"):
            item = resolve_local(
                system_schema,
                system_schema["properties"][field].get("items", {}),
            )
            if item.get("additionalProperties") is not False:
                schema_closure_errors.append(f"system {field} item is open")
    except Exception as error:
        schema_closure_errors.append(str(error))
    audit.record(
        "CB-016",
        "closed component meta-schemas",
        not schema_closure_errors,
        f"errors={schema_closure_errors}",
    )

    try:
        conformance = json_values["aset/shared/conformance/results.json"]
        assert isinstance(conformance, dict)
        result_ids = [str(item["id"]) for item in conformance["results"]]
        conformance_ok = (
            conformance.get("verdict") == "PASS"
            and conformance.get("cases_total") == 26
            and conformance.get("cases_passed") == 26
            and conformance.get("cases_failed") == 0
            and len(result_ids) == len(set(result_ids)) == 26
        )
        details = (
            f"verdict={conformance.get('verdict')}; "
            f"cases={conformance.get('cases_passed')}/{conformance.get('cases_total')}"
        )
    except Exception as error:
        conformance_ok = False
        details = str(error)
    audit.record("CB-017", "component conformance results", conformance_ok, details)

    formal_errors: list[str] = []
    try:
        formal = json_values["aset/shared/formal/results.json"]
        assert isinstance(formal, dict)
        if formal.get("verdict") != "PASS" or formal.get("models_passed") != 8:
            formal_errors.append("bounded model results are not 8/8 PASS")
        hashes = []
        for relative in formal_required[:8]:
            hashes.append(sha256(get(relative)))
        if len(hashes) != len(set(hashes)):
            formal_errors.append("formal projections are byte-identical")
        for item in formal.get("models", []):
            if item.get("states", 0) < 2 or item.get("verdict") != "PASS":
                formal_errors.append(f"weak or failed model:{item.get('id')}")
    except Exception as error:
        formal_errors.append(str(error))
    audit.record(
        "CB-018",
        "independent bounded formal evidence",
        not formal_errors,
        f"errors={formal_errors}",
    )

    separation_errors: list[str] = []
    try:
        system = json_values["aset/system/canonical/source/system-composition-model.json"]
        assert isinstance(system, dict)
        gates = {str(item["id"]): item for item in system["gates"]}
        expectation = gates["GATE-EXPECT-ADMIT"]
        dispatch = gates["GATE-DISPATCH"]
        if expectation["document"] == dispatch["document"]:
            separation_errors.append("expectation and dispatch document are equal")
        if expectation["permit"] == dispatch["permit"]:
            separation_errors.append("expectation and dispatch Permit are equal")
        if expectation["external_effect"] is not False:
            separation_errors.append("expectation gate asserts external effect")
        if dispatch["external_effect"] is not True:
            separation_errors.append("dispatch gate lacks external-effect boundary")
    except Exception as error:
        separation_errors.append(str(error))
    audit.record(
        "CB-019",
        "expectation and execution separation",
        not separation_errors,
        f"errors={separation_errors}",
    )

    source_inventory_errors: list[str] = []
    try:
        requirements = json_values["aset/source/rc11/requirements-register.json"]
        conformance_source = json_values["aset/source/rc11/conformance-results.json"]
        assert isinstance(requirements, dict) and isinstance(conformance_source, dict)
        if len(requirements.get("requirements", [])) != 177:
            source_inventory_errors.append("requirement registry count differs")
        source_results = conformance_source.get("results", [])
        expected_result_ids = conformance_source.get("expected_result_ids", [])
        if (
            conformance_source.get("status") != "PASS"
            or len(source_results) != 376
            or len(expected_result_ids) != 376
            or any(not item.get("passed") for item in source_results)
        ):
            source_inventory_errors.append("source conformance evidence differs")
        migration = json_values["aset/shared/migration/RC11_TO_COMPONENT_CANONS.json"]
        assert isinstance(migration, dict)
        for item in migration["assignments"]["schemas"]:
            relative = f"aset/components/protocol/canonical/protocol/schemas/{item['id']}"
            if sha256(get(relative)) != item.get("sha256"):
                source_inventory_errors.append(f"schema drift:{item['id']}")
    except Exception as error:
        source_inventory_errors.append(str(error))
    audit.record(
        "CB-020",
        "exact source registry and schema evidence",
        not source_inventory_errors,
        f"errors={source_inventory_errors[:5]}",
    )

    ownership: dict[str, list[str]] = {}
    for key, component in components.items():
        for owned in component.get("owns", []):
            ownership.setdefault(str(owned), []).append(key)
    duplicate_ownership = {
        name: owners for name, owners in ownership.items() if len(owners) > 1
    }
    audit.record(
        "CB-021",
        "exclusive primitive ownership",
        not duplicate_ownership,
        f"duplicates={duplicate_ownership}",
    )

    localization_errors: list[str] = []
    for key, component in components.items():
        for operation in component.get("operations", []):
            descriptions = operation.get("description", {})
            if not isinstance(descriptions, dict) or len(set(descriptions.values())) < 3:
                localization_errors.append(f"{key}:{operation.get('id')}")
    audit.record(
        "CB-022",
        "distinct multilingual operation semantics",
        not localization_errors,
        f"non-distinct={localization_errors}",
    )

    assurance_missing: list[str] = []
    assurance_files = (
        "requirements.json",
        "verification-cases.json",
        "traceability.json",
        "invariants.json",
        "limitations.json",
        "threat-model.json",
    )
    for key in (*COMPONENT_KEYS, "system"):
        base = (
            "aset/system/canonical"
            if key == "system"
            else f"aset/components/{key}/canonical"
        )
        for name in assurance_files:
            relative = f"{base}/assurance/{name}"
            if EXPECTED_ROOT + relative not in files:
                assurance_missing.append(relative)
        for relative in (
            f"{base}/protocol/profile.json",
            f"{base}/conformance/binding.json",
        ):
            if EXPECTED_ROOT + relative not in files:
                assurance_missing.append(relative)
    audit.record(
        "CB-023",
        "self-contained component assurance packages",
        not assurance_missing,
        "complete" if not assurance_missing else f"missing={assurance_missing}",
    )

    traceability_errors: list[str] = []
    local_requirement_total = 0
    local_verification_total = 0
    local_traceability_total = 0
    try:
        migration = json_values["aset/shared/migration/RC11_TO_COMPONENT_CANONS.json"]
        assert isinstance(migration, dict)
        assignment_map = {
            str(item["id"]): str(item["target"])
            for item in migration["assignments"]["requirements"]
        }
        for key in (*COMPONENT_KEYS, "system"):
            base = (
                "aset/system/canonical"
                if key == "system"
                else f"aset/components/{key}/canonical"
            )
            requirements = json_values[f"{base}/assurance/requirements.json"]
            verification = json_values[f"{base}/assurance/verification-cases.json"]
            traceability = json_values[f"{base}/assurance/traceability.json"]
            assert isinstance(requirements, dict)
            assert isinstance(verification, dict)
            assert isinstance(traceability, dict)
            requirement_ids = [str(item["ID"]) for item in requirements["requirements"]]
            verification_ids = [str(item["RequirementID"]) for item in verification["cases"]]
            traceability_ids = [
                str(item["DerivedRequirementID"] or item["SystemRequirementID"])
                for item in traceability["links"]
            ]
            expected_ids = {
                identifier
                for identifier, target in assignment_map.items()
                if target == key
            }
            if set(requirement_ids) != expected_ids:
                traceability_errors.append(f"{key}:requirement partition")
            if set(verification_ids) != expected_ids:
                traceability_errors.append(f"{key}:verification partition")
            if set(traceability_ids) != expected_ids:
                traceability_errors.append(f"{key}:traceability partition")
            if len(requirement_ids) != len(set(requirement_ids)):
                traceability_errors.append(f"{key}:duplicate requirement")
            local_requirement_total += len(requirement_ids)
            local_verification_total += len(verification_ids)
            local_traceability_total += len(traceability_ids)
    except Exception as error:
        traceability_errors.append(str(error))
    totals_ok = (
        local_requirement_total
        == local_verification_total
        == local_traceability_total
        == 177
    )
    if not totals_ok:
        traceability_errors.append(
            "totals="
            f"{local_requirement_total}/{local_verification_total}/{local_traceability_total}"
        )
    audit.record(
        "CB-024",
        "local requirement-verification-traceability identity",
        not traceability_errors,
        (
            "totals="
            f"{local_requirement_total}/{local_verification_total}/"
            f"{local_traceability_total}; errors={traceability_errors}"
        ),
    )

    asset_pointer_errors: list[str] = []
    try:
        for key, component in components.items():
            assets = component.get("canon_assets")
            if not isinstance(assets, dict):
                asset_pointer_errors.append(f"{key}:canon_assets absent")
                continue
            for relative in assets.values():
                if EXPECTED_ROOT + str(relative) not in files:
                    asset_pointer_errors.append(f"{key}:missing pointer:{relative}")
        system = json_values["aset/system/canonical/source/system-composition-model.json"]
        assert isinstance(system, dict)
        assets = system.get("canon_assets")
        if not isinstance(assets, dict):
            asset_pointer_errors.append("system:canon_assets absent")
    except Exception as error:
        asset_pointer_errors.append(str(error))
    audit.record(
        "CB-025",
        "canonical asset closure",
        not asset_pointer_errors,
        f"errors={asset_pointer_errors}",
    )

    try:
        gate_text = get("tools/production_gate.py").decode("utf-8")
        adversarial_required = (
            EXPECTED_ROOT + "tools/run_component_blackbox_adversarial.py" in files
            and "tools/run_component_blackbox_adversarial.py" in gate_text
        )
        details = f"integrated={adversarial_required}"
    except Exception as error:
        adversarial_required = False
        details = str(error)
    audit.record(
        "CB-026",
        "adversarial black-box gate integration",
        adversarial_required,
        details,
    )

    discoverability_errors: list[str] = []
    for relative in ("README.md", "README.ru.md", "README.pt-BR.md", "ROADMAP.md"):
        try:
            if "(aset/README.md)" not in get(relative).decode("utf-8"):
                discoverability_errors.append(relative)
        except Exception as error:
            discoverability_errors.append(f"{relative}:{error}")
    audit.record(
        "CB-027",
        "root component-canon discoverability",
        not discoverability_errors,
        f"errors={discoverability_errors}",
    )

    return report(audit, snapshot_path, archive_digest)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot")
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--output-md", required=True)
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    result = audit_snapshot(args.snapshot)
    with open(args.output_json, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    with open(args.output_md, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(markdown(result))
    print(f"COMPONENT_BLACKBOX_CHECKS={result['checks_passed']}/{result['checks_total']}")
    print(f"COMPONENT_BLACKBOX_FINDINGS={result['checks_failed']}")
    print(f"COMPONENT_BLACKBOX_VERDICT={result['verdict']}")
    if args.report_only:
        return 0
    return 0 if result["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

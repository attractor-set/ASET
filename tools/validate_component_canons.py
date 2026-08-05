from __future__ import annotations

from collections import Counter

from component_common import (
    ASET_ROOT,
    COMPONENT_KEYS,
    ROOT,
    canonical_digest,
    component_path,
    file_digest,
    load,
    schema_errors,
)
from jsonschema import Draft202012Validator

COMPONENT_SCHEMA = ASET_ROOT / "shared/schemas/component-canon.schema.json"
SYSTEM_SCHEMA = ASET_ROOT / "shared/schemas/system-composition-canon.schema.json"
BRIDGE_SCHEMA = ASET_ROOT / "shared/schemas/seed-compatibility-profile.schema.json"
MIGRATION_SCHEMA = ASET_ROOT / "shared/schemas/rc11-component-migration.schema.json"
SYSTEM = ASET_ROOT / "system/canonical/source/system-composition-model.json"
BRIDGE = ASET_ROOT / "shared/seed-bridge/seed-compatibility-profile.json"
MIGRATION = ASET_ROOT / "shared/migration/RC11_TO_COMPONENT_CANONS.json"
PROVENANCE = ASET_ROOT / "source/rc11/SOURCE_PROVENANCE.json"
SOURCE_MODEL = ASET_ROOT / "source/rc11/aset-system-model-1.5-rc11.json"
SOURCE_SPEC = ASET_ROOT / "source/rc11/aset-system-specification-1.5-rc11.json"
SOURCE_REQUIREMENTS = ASET_ROOT / "source/rc11/requirements-register.json"

EXPECTED_COUNTS = {
    "requirements": 177,
    "invariants": 57,
    "artifacts": 52,
    "gates": 11,
    "schemas": 57,
}

ASSET_SCHEMAS = {
    "requirements": ASET_ROOT / "shared/schemas/component-requirements.schema.json",
    "verification_cases": ASET_ROOT
    / "shared/schemas/component-verification-cases.schema.json",
    "traceability": ASET_ROOT / "shared/schemas/component-traceability.schema.json",
    "invariants": ASET_ROOT / "shared/schemas/component-invariants.schema.json",
    "limitations": ASET_ROOT / "shared/schemas/component-limitations.schema.json",
    "threat_model": ASET_ROOT / "shared/schemas/component-threat-model.schema.json",
    "protocol_profile": ASET_ROOT
    / "shared/schemas/component-protocol-profile.schema.json",
    "conformance_binding": ASET_ROOT
    / "shared/schemas/component-conformance-binding.schema.json",
}
CONFORMANCE_PROFILE = ASET_ROOT / "shared/conformance/component-conformance-profile.json"


def identifiers(items: list[dict[str, object]], key: str = "id") -> list[str]:
    return [str(item[key]) for item in items]


def duplicates(values: list[str]) -> list[str]:
    counts = Counter(values)
    return sorted(value for value, count in counts.items() if count > 1)


def validate_digest(name: str, value: dict[str, object], errors: list[str]) -> None:
    observed = value.get("canonical_digest")
    expected = canonical_digest(value)
    if observed != expected:
        errors.append(f"canonical digest mismatch:{name}:{observed}:{expected}")


def validate_operation_mapping(
    component_id: str,
    operation: dict[str, object],
    rules: dict[str, dict[str, object]],
    errors: list[str],
) -> None:
    classification = str(operation["classification"])
    mapping = operation["seed_mapping"]
    assert isinstance(mapping, dict)
    rule = rules.get(classification)
    if rule is None:
        errors.append(f"unknown operation classification:{component_id}:{classification}")
        return
    for field in (
        "seed_transition_required",
        "sequence",
        "outcome_recognition_required",
    ):
        if mapping.get(field) != rule.get(field):
            errors.append(
                f"seed mapping mismatch:{component_id}:{operation['id']}:{field}"
            )


def main() -> int:
    errors: list[str] = []
    component_schema = load(COMPONENT_SCHEMA)
    system_schema = load(SYSTEM_SCHEMA)
    bridge_schema = load(BRIDGE_SCHEMA)
    migration_schema = load(MIGRATION_SCHEMA)
    bridge = load(BRIDGE)
    migration = load(MIGRATION)
    system = load(SYSTEM)
    source_model = load(SOURCE_MODEL)
    source_spec = load(SOURCE_SPEC)
    source_requirements = load(SOURCE_REQUIREMENTS)["requirements"]
    provenance = load(PROVENANCE)

    for name, schema, value in (
        ("system", system_schema, system),
        ("seed-bridge", bridge_schema, bridge),
        ("migration", migration_schema, migration),
    ):
        for error in schema_errors(schema, value):
            errors.append(f"schema:{name}:{error}")
        validate_digest(name, value, errors)

    seed_role = system.get("seed_role")
    expected_capabilities = {
        "planning",
        "long-term memory",
        "agent and workflow orchestration",
        "external-effect execution infrastructure",
        "evidence acquisition infrastructure",
        "process analytics",
    }
    if not isinstance(seed_role, dict):
        errors.append("Seed role absent")
    else:
        if seed_role.get("seed_version") != system["seed_compatibility"]["version"]:
            errors.append("Seed role version differs from compatibility bridge")
        if seed_role.get("classification") != "MINIMAL_SEMANTIC_NUCLEUS":
            errors.append("Seed role classification differs")
        if seed_role.get("implementation_neutral") is not True:
            errors.append("Seed role implementation neutrality differs")
        if set(seed_role.get("capabilities_not_provided_by_seed", [])) != expected_capabilities:
            errors.append("Seed role capability boundary differs")

    required_guarantee = (
        "Components may perform the work; Seed determines when that work acquires "
        "authoritative ASET significance."
    )
    required_limitation = (
        "Component integration alone does not establish ASET compatibility without "
        "conformance to the Seed semantic lifecycle."
    )
    if required_guarantee not in bridge["guarantees"]:
        errors.append("Seed bridge authoritative-significance guarantee absent")
    if required_limitation not in bridge["limitations"]:
        errors.append("Seed bridge integration limitation absent")

    components: dict[str, dict[str, object]] = {}
    component_ids: list[str] = []
    operation_ids: list[str] = []
    for key in COMPONENT_KEYS:
        value = load(component_path(key))
        components[key] = value
        component_ids.append(str(value["component_id"]))
        operation_ids.extend(identifiers(value["operations"]))
        for error in schema_errors(component_schema, value):
            errors.append(f"schema:{key}:{error}")
        validate_digest(key, value, errors)
        if value["version"] != "0.1-rc1":
            errors.append(f"unexpected component version:{key}")
        if not value["requirement_ids"]:
            errors.append(f"component has no requirements:{key}")

    if duplicates(component_ids):
        errors.append(f"duplicate component IDs:{duplicates(component_ids)}")
    if duplicates(operation_ids):
        errors.append(f"duplicate operation IDs:{duplicates(operation_ids)}")

    if provenance.get("source_archive_sha256") != (
        "sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22"
    ):
        errors.append("source archive identity differs")
    if provenance["source_model"]["sha256"] != file_digest(SOURCE_MODEL):
        errors.append("source model byte digest differs")
    if provenance["source_specification"]["sha256"] != file_digest(SOURCE_SPEC):
        errors.append("source specification byte digest differs")
    if source_model["canonical_digest"] != provenance["source_model"]["canonical_digest"]:
        errors.append("source model canonical identity differs")
    if source_spec["canonical_digest"] != provenance["source_specification"]["canonical_digest"]:
        errors.append("source specification canonical identity differs")

    source_sets = {
        "requirements": {str(item["ID"]) for item in source_requirements},
        "invariants": {str(item["id"]) for item in source_model["invariants"]},
        "artifacts": {str(item["id"]) for item in source_model["artifacts"]},
        "gates": {str(item["id"]) for item in source_model["gate_types"]},
        "schemas": {
            str(item["id"])
            for item in migration["assignments"]["schemas"]
        },
    }
    assignment_maps: dict[str, dict[str, str]] = {}
    for kind, expected_count in EXPECTED_COUNTS.items():
        assignments = migration["assignments"][kind]
        ids = identifiers(assignments)
        if len(ids) != expected_count or len(set(ids)) != expected_count:
            errors.append(f"migration assignment count/uniqueness:{kind}")
        if set(ids) != source_sets[kind]:
            missing = sorted(source_sets[kind] - set(ids))
            extra = sorted(set(ids) - source_sets[kind])
            errors.append(f"migration source mismatch:{kind}:missing={missing}:extra={extra}")
        assignment_maps[kind] = {str(item["id"]): str(item["target"]) for item in assignments}

    assigned_requirements = {
        str(identifier): key
        for key, component in components.items()
        for identifier in component["requirement_ids"]
    }
    system_requirements = {
        identifier: "system"
        for identifier, target in assignment_maps["requirements"].items()
        if target == "system"
    }
    if assigned_requirements | system_requirements != assignment_maps["requirements"]:
        errors.append("component requirement partition differs from migration")

    assigned_invariants = {
        str(item["id"]): key
        for key, component in components.items()
        for item in component["invariants"]
    }
    system_invariants = {
        str(item["id"]): "system"
        for item in system["invariant_assignments"]
        if item["target"] == "system"
    }
    if assigned_invariants | system_invariants != assignment_maps["invariants"]:
        errors.append("component invariant partition differs from migration")

    assigned_artifacts = {
        str(item["id"]): key
        for key, component in components.items()
        for item in component["artifacts"]
    }
    if assigned_artifacts != assignment_maps["artifacts"]:
        errors.append("component artifact partition differs from migration")

    producer_roles = {
        str(role["gate_id"]): key
        for key, component in components.items()
        for role in component["gate_roles"]
        if role["role"] == "PRODUCER"
    }
    if producer_roles != assignment_maps["gates"]:
        errors.append("gate producer partition differs from migration")
    for key, expected_role in (
        ("core", "AUTHORITY_ISSUER"),
        ("context", "CONTEXT_TARGET"),
        ("protocol", "SCHEMA_AUTHORITY"),
    ):
        count = sum(
            role["role"] == expected_role
            for role in components[key]["gate_roles"]
        )
        if count != 11:
            errors.append(f"gate role coverage:{key}:{expected_role}:{count}")

    protocol_schema_dir = ASET_ROOT / "components/protocol/canonical/protocol/schemas"
    for item in migration["assignments"]["schemas"]:
        path = protocol_schema_dir / str(item["id"])
        if not path.is_file() or file_digest(path) != item.get("sha256"):
            errors.append(f"protocol schema byte mismatch:{item['id']}")

    rules = {
        str(item["classification"]): item
        for item in bridge["classification_rules"]
    }
    for component in components.values():
        for operation in component["operations"]:
            validate_operation_mapping(str(component["component_id"]), operation, rules, errors)

    seed_model_path = ROOT / str(bridge["seed_model_path"])
    if file_digest(seed_model_path) != bridge["seed_model_sha256"]:
        errors.append("Seed model file digest differs")

    refs = {str(item["component_id"]): item for item in system["components"]}
    if set(refs) != set(component_ids):
        errors.append("system component inventory differs")
    for key, component in components.items():
        ref = refs.get(str(component["component_id"]))
        if ref is None:
            continue
        if ref["canonical_digest"] != component["canonical_digest"]:
            errors.append(f"system component digest differs:{key}")
        if ref["version"] != component["version"]:
            errors.append(f"system component version differs:{key}")

    for schema_path in [
        COMPONENT_SCHEMA,
        SYSTEM_SCHEMA,
        BRIDGE_SCHEMA,
        MIGRATION_SCHEMA,
        *ASSET_SCHEMAS.values(),
    ]:
        try:
            Draft202012Validator.check_schema(load(schema_path))
        except Exception as error:
            errors.append(f"meta-schema:{schema_path.relative_to(ROOT)}:{error}")

    conformance_profile = load(CONFORMANCE_PROFILE)
    conformance_case_ids = set(conformance_profile["required_case_ids"])
    conformance_profile_digest = str(conformance_profile["canonical_digest"])

    canon_documents: dict[str, dict[str, object]] = {
        **components,
        "system": system,
    }
    for key, document in canon_documents.items():
        assets = document.get("canon_assets")
        if not isinstance(assets, dict):
            errors.append(f"canon assets absent:{key}")
            continue
        local: dict[str, dict[str, object]] = {}
        for asset_name, schema_path in ASSET_SCHEMAS.items():
            relative = assets.get(asset_name)
            if not isinstance(relative, str):
                errors.append(f"canon asset pointer absent:{key}:{asset_name}")
                continue
            path = ROOT / relative
            if not path.is_file():
                errors.append(f"canon asset missing:{key}:{asset_name}:{relative}")
                continue
            value = load(path)
            local[asset_name] = value
            for error in schema_errors(load(schema_path), value):
                errors.append(f"asset schema:{key}:{asset_name}:{error}")
            validate_digest(f"{key}:{asset_name}", value, errors)
            expected_component_id = (
                "aset.system" if key == "system" else str(document["component_id"])
            )
            if value.get("component_id") != expected_component_id:
                errors.append(f"asset component identity differs:{key}:{asset_name}")
            if value.get("component_version") != document["version"]:
                errors.append(f"asset version differs:{key}:{asset_name}")

        expected_requirement_ids = (
            {
                identifier
                for identifier, target in assignment_maps["requirements"].items()
                if target == "system"
            }
            if key == "system"
            else {str(item) for item in document["requirement_ids"]}
        )
        requirements_value = local.get("requirements", {})
        observed_requirement_ids = {
            str(item["ID"])
            for item in requirements_value.get("requirements", [])
        }
        if observed_requirement_ids != expected_requirement_ids:
            errors.append(f"local requirements differ:{key}")

        verification_value = local.get("verification_cases", {})
        observed_verification_ids = {
            str(item["RequirementID"])
            for item in verification_value.get("cases", [])
        }
        if observed_verification_ids != expected_requirement_ids:
            errors.append(f"local verification differs:{key}")

        traceability_value = local.get("traceability", {})
        observed_traceability_ids = {
            str(item["DerivedRequirementID"] or item["SystemRequirementID"])
            for item in traceability_value.get("links", [])
        }
        if observed_traceability_ids != expected_requirement_ids:
            errors.append(f"local traceability differs:{key}")

        invariant_value = local.get("invariants", {})
        observed_invariant_ids = {
            str(item["id"])
            for item in invariant_value.get("invariants", [])
        }
        expected_invariant_ids = (
            {
                str(item["id"])
                for item in system["invariant_assignments"]
                if item["target"] == "system"
            }
            if key == "system"
            else {
                str(item["id"])
                for item in [*document["invariants"], *document["boundary_invariants"]]
            }
        )
        if observed_invariant_ids != expected_invariant_ids:
            errors.append(f"local invariants differ:{key}")

        threat_value = local.get("threat_model", {})
        if not threat_value.get("threats"):
            errors.append(f"local threat model empty:{key}")

        protocol_value = local.get("protocol_profile", {})
        seed_bridge = protocol_value.get("seed_bridge", {})
        if not isinstance(seed_bridge, dict) or seed_bridge.get("canonical_digest") != bridge[
            "canonical_digest"
        ]:
            errors.append(f"protocol Seed bridge differs:{key}")

        binding_value = local.get("conformance_binding", {})
        if binding_value.get("shared_profile_digest") != conformance_profile_digest:
            errors.append(f"conformance profile digest differs:{key}")
        applicable = set(binding_value.get("applicable_case_ids", []))
        if not applicable or not applicable <= conformance_case_ids:
            errors.append(f"conformance binding differs:{key}")

        formal_relative = assets.get("formal_profile")
        if not isinstance(formal_relative, str) or not (ROOT / formal_relative).is_file():
            errors.append(f"formal asset missing:{key}")

    if errors:
        for error in errors:
            print(f"COMPONENT_CANON_ERROR={error}")
        return 1
    print("COMPONENT_CANONS=7")
    print("COMPONENT_VERSIONS_INDEPENDENT=PASS")
    print("RC11_REQUIREMENTS_PARTITION=177/177")
    print("RC11_INVARIANTS_PARTITION=57/57")
    print("RC11_ARTIFACTS_PARTITION=52/52")
    print("RC11_GATES_PARTITION=11/11")
    print("RC11_SCHEMAS_BOUND=57/57")
    print("SEED_RC12_BRIDGE=PASS")
    print("COMPONENT_CANON_VALIDATION=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

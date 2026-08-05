from __future__ import annotations

import copy
from dataclasses import replace

import pytest

from aset_reference import (
    DeterministicConnector,
    ReferenceError,
    ReferenceMachine,
    run_critical_path,
)
from aset_reference.canonical import canonical_json, domain_digest, freeze_json


@pytest.mark.parametrize(
    ("effect_class", "terminal_status", "outcome_class"),
    [
        ("SUCCESS", "CLOSED", "SUCCESS"),
        ("FAILURE", "CLOSED", "FAILURE"),
        ("NO_EFFECT", "CLOSED", "NO_EFFECT"),
        ("UNKNOWN", "REJECTED", None),
    ],
)
def test_complete_path_for_all_effect_classes(effect_class, terminal_status, outcome_class):
    result = run_critical_path(effect_class)
    assert len(result.crossings) == 8
    assert len(result.receipts) == 8
    assert result.final_context.version == 8
    assert result.terminal_status == terminal_status
    expected_verification = "FAIL" if effect_class == "UNKNOWN" else "PASS"
    assert result.verification.payload["status"] == expected_verification
    if outcome_class is None:
        assert result.outcome is None
    else:
        assert result.outcome is not None
        assert result.outcome.payload["classification"] == outcome_class


def test_critical_path_preserves_required_separations():
    result = run_critical_path("SUCCESS")
    by_type = {artifact.artifact_type: artifact for artifact in result.artifacts}
    required = {
        "ContextProjection",
        "PlanProposal",
        "ExpectedChangePatch",
        "OperationalBinding",
        "ExecutionIntent",
        "Observation",
        "EvidenceBundle",
        "Verification",
        "AcceptanceDecision",
        "Outcome",
        "LearningObservation",
    }
    assert required <= set(by_type)
    assert by_type["Observation"].artifact_id != by_type["Verification"].artifact_id
    assert by_type["Verification"].artifact_id != by_type["Outcome"].artifact_id
    assert len({receipt.permit_id for receipt in result.receipts}) == 8


def test_gate_order_is_exact():
    result = run_critical_path("SUCCESS")
    assert [crossing.gate_id for crossing in result.crossings] == [
        "GATE-CONTEXT-PROJECT",
        "GATE-EXPECT-ADMIT",
        "GATE-EXEC-BIND",
        "GATE-DISPATCH",
        "GATE-OBSERVE",
        "GATE-EVIDENCE",
        "GATE-ACCEPT",
        "GATE-TASK-CLOSE",
    ]


def test_each_receipt_is_bound_to_immediate_predecessor():
    result = run_critical_path("SUCCESS")
    previous = None
    for receipt in result.receipts:
        assert receipt.previous_receipt_id == previous
        previous = receipt.receipt_id


def test_machine_is_single_use():
    machine = ReferenceMachine()
    machine.run("SUCCESS")
    with pytest.raises(ReferenceError, match="MACHINE_ALREADY_USED"):
        machine.run("SUCCESS")


def test_connector_replay_is_idempotent():
    machine = ReferenceMachine()
    intent = machine._artifact("ExecutionIntent", {"operation": "demo"})
    connector = DeterministicConnector()
    first = connector.execute(intent, "SUCCESS")
    second = connector.execute(intent, "SUCCESS")
    assert first == second


def test_rejects_unknown_effect_class():
    with pytest.raises(ReferenceError, match="EFFECT_CLASS_UNSUPPORTED"):
        run_critical_path("MAYBE")


def test_seed_canonicalization_rejects_floats():
    with pytest.raises(ValueError, match="FLOAT_FORBIDDEN"):
        freeze_json({"value": 1.5})


def test_seed_canonicalization_normalizes_nfc():
    composed = domain_digest("test", {"text": "é"})
    decomposed = domain_digest("test", {"text": "e\u0301"})
    assert composed == decomposed
    assert canonical_json({"text": "é"}) == canonical_json({"text": "e\u0301"})


def test_seed_canonicalization_rejects_normalized_key_collision():
    with pytest.raises(ValueError, match="NORMALIZED_KEY_COLLISION"):
        freeze_json({"é": 1, "e\u0301": 2})


def test_crossing_rejects_reused_permit():
    machine = ReferenceMachine()
    patch = machine._patch(
        "ContextProjectionPatch",
        "GATE-CONTEXT-PROJECT",
        {"CTX-MEM": {}, "CTX-TASK": {"status": "PROJECTED"}},
    )
    resolution, permit = machine.authorize(patch)
    machine.cross(patch, resolution, permit)
    with pytest.raises(ReferenceError, match="PERMIT_ALREADY_CONSUMED"):
        machine.cross(patch, resolution, permit)


def test_crossing_rejects_wrong_gate_binding():
    machine = ReferenceMachine()
    patch = machine._patch(
        "ContextProjectionPatch",
        "GATE-CONTEXT-PROJECT",
        {"CTX-MEM": {}, "CTX-TASK": {"status": "PROJECTED"}},
    )
    resolution, permit = machine.authorize(patch)
    wrong = replace(permit, gate_id="GATE-EXPECT-ADMIT")
    with pytest.raises(ReferenceError, match="PERMIT_BINDING_MISMATCH"):
        machine.cross(patch, resolution, wrong)


def test_crossing_rejects_wrong_resolution_binding():
    machine = ReferenceMachine()
    patch = machine._patch(
        "ContextProjectionPatch",
        "GATE-CONTEXT-PROJECT",
        {"CTX-MEM": {}, "CTX-TASK": {"status": "PROJECTED"}},
    )
    resolution, permit = machine.authorize(patch)
    wrong = replace(resolution, gate_id="GATE-EXPECT-ADMIT")
    with pytest.raises(ReferenceError, match="RESOLUTION_BINDING_MISMATCH"):
        machine.cross(patch, wrong, permit)


def test_crossing_rejects_wrong_write_set():
    machine = ReferenceMachine()
    patch = machine._patch(
        "ContextProjectionPatch",
        "GATE-CONTEXT-PROJECT",
        {"CTX-MEM": {}},
    )
    resolution, permit = machine.authorize(patch)
    with pytest.raises(ReferenceError, match="WRITE_SET_MISMATCH"):
        machine.cross(patch, resolution, permit)


def test_crossing_rejects_stale_context():
    machine = ReferenceMachine()
    patch = machine._patch(
        "ContextProjectionPatch",
        "GATE-CONTEXT-PROJECT",
        {"CTX-MEM": {}, "CTX-TASK": {"status": "PROJECTED"}},
    )
    resolution, permit = machine.authorize(patch)
    machine.context = type(machine.context)(
        context_id=machine.context.context_id,
        version=machine.context.version,
        sections={key: dict(value) for key, value in machine.context.sections.items()},
        root="sha256:" + "0" * 64,
    )
    with pytest.raises(ReferenceError, match="SOURCE_CONTEXT_STALE"):
        machine.cross(patch, resolution, permit)


def test_snapshot_roundtrip_is_exact():
    machine = ReferenceMachine()
    machine.run("FAILURE")
    snapshot = machine.snapshot()
    restored = ReferenceMachine.restore(snapshot)
    assert restored.snapshot() == snapshot


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ("context_root", "CONTEXT_ROOT_INVALID"),
        ("resolution_gate", "RESOLUTION_CHAIN_INVALID"),
        ("permit_patch_digest", "PERMIT_CHAIN_INVALID"),
        ("receipt_patch_digest", "RECEIPT_CHAIN_INVALID"),
        ("receipt_source_root", "RECEIPT_CHAIN_INVALID"),
        ("crossing_source_root", "CROSSING_CHAIN_INVALID"),
        ("consumed_permits", "CONSUMED_PERMIT_SET_INVALID"),
        ("last_receipt", "LAST_RECEIPT_INVALID"),
    ],
)
def test_snapshot_tampering_fails_closed(mutation, code):
    machine = ReferenceMachine()
    machine.run("SUCCESS")
    snapshot = copy.deepcopy(machine.snapshot())
    first_crossing = snapshot["crossings"][0]
    first_permit = first_crossing["permit_id"]
    first_receipt = first_crossing["receipt_id"]
    first_resolution = snapshot["permits"][first_permit]["resolution_id"]
    if mutation == "context_root":
        snapshot["context"]["root"] = "sha256:" + "0" * 64
    elif mutation == "resolution_gate":
        snapshot["resolutions"][first_resolution]["gate_id"] = "GATE-EXPECT-ADMIT"
    elif mutation == "permit_patch_digest":
        snapshot["permits"][first_permit]["patch_digest"] = "sha256:" + "0" * 64
    elif mutation == "receipt_patch_digest":
        snapshot["receipts"][first_receipt]["patch_digest"] = "sha256:" + "0" * 64
    elif mutation == "receipt_source_root":
        snapshot["receipts"][first_receipt]["source_context_root"] = "sha256:" + "0" * 64
    elif mutation == "crossing_source_root":
        snapshot["crossings"][0]["source_context_root"] = "sha256:" + "0" * 64
    elif mutation == "consumed_permits":
        snapshot["consumed_permit_ids"] = []
    elif mutation == "last_receipt":
        snapshot["last_receipt_id"] = "receipt:wrong"
    with pytest.raises(ReferenceError, match=code):
        ReferenceMachine.restore(snapshot)

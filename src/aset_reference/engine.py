"""Deterministic full semantic critical path for ASET.

This module is a non-normative executable interpretation.  It deliberately
contains no persistence, network, subprocess, clock, randomness, model call,
or production cryptographic key management.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from .canonical import domain_digest, normalized_json, plain_json
from .model import (
    Artifact,
    Context,
    CoreResolution,
    CriticalPathResult,
    EffectRecord,
    GateCrossing,
    GovernedPatch,
    Permit,
    PermitUseReceipt,
)

GATE_WRITES: dict[str, frozenset[str]] = {
    "GATE-CONTEXT-PROJECT": frozenset({"CTX-MEM", "CTX-TASK"}),
    "GATE-EXPECT-ADMIT": frozenset({"CTX-MAST", "CTX-TASK"}),
    "GATE-EXEC-BIND": frozenset({"CTX-EXEC"}),
    "GATE-DISPATCH": frozenset({"CTX-EXEC", "CTX-AUTH"}),
    "GATE-OBSERVE": frozenset({"CTX-EXEC"}),
    "GATE-EVIDENCE": frozenset({"CTX-ACCE"}),
    "GATE-ACCEPT": frozenset({"CTX-ACCE", "CTX-TASK"}),
    "GATE-TASK-CLOSE": frozenset({"CTX-ACCE", "CTX-TASK"}),
}

EFFECT_CLASSES = ("SUCCESS", "FAILURE", "NO_EFFECT", "UNKNOWN")


class ReferenceError(ValueError):
    """Fail-closed reference boundary rejection."""


class DeterministicConnector:
    """Idempotent connector with four explicit semantic effect classes."""

    def __init__(self) -> None:
        self._effects: dict[str, EffectRecord] = {}

    def execute(self, intent: Artifact, effect_class: str) -> EffectRecord:
        if effect_class not in EFFECT_CLASSES:
            raise ReferenceError("EFFECT_CLASS_UNSUPPORTED")
        key = domain_digest(
            "ASET/Reference/EffectIdempotency/v1",
            {"intent_id": intent.artifact_id, "effect_class": effect_class},
        )
        existing = self._effects.get(key)
        if existing is not None:
            return existing
        effect_id = "effect:" + domain_digest(
            "ASET/Reference/Effect/v1",
            {"intent_id": intent.artifact_id, "effect_class": effect_class},
        )[7:]
        record = EffectRecord(
            effect_id=effect_id,
            intent_id=intent.artifact_id,
            effect_class=effect_class,
            idempotency_key=key,
        )
        self._effects[key] = record
        return record


class ReferenceMachine:
    """In-memory state machine for one complete critical-path execution."""

    def __init__(self, context_id: str = "ctx:reference") -> None:
        sections = {
            "CTX-MEM": {},
            "CTX-MAST": {},
            "CTX-EXEC": {},
            "CTX-ACCE": {},
            "CTX-TASK": {"status": "NEW"},
            "CTX-AUTH": {},
        }
        root = self._context_root(context_id, 0, sections)
        self.context = Context(context_id=context_id, version=0, sections=sections, root=root)
        self.artifacts: dict[str, Artifact] = {}
        self.patches: dict[str, GovernedPatch] = {}
        self.resolutions: dict[str, CoreResolution] = {}
        self.permits: dict[str, Permit] = {}
        self.receipts: dict[str, PermitUseReceipt] = {}
        self.crossings: list[GateCrossing] = []
        self.effects: dict[str, EffectRecord] = {}
        self.consumed_permit_ids: set[str] = set()
        self.last_receipt_id: str | None = None

    @staticmethod
    def _context_root(context_id: str, version: int, sections: dict[str, Any]) -> str:
        return domain_digest(
            "ASET/Reference/Context/v1",
            {"context_id": context_id, "version": version, "sections": sections},
        )

    def _artifact(self, artifact_type: str, payload: dict[str, Any]) -> Artifact:
        material = {
            "artifact_type": artifact_type,
            "payload": normalized_json(payload),
            "source_context_root": self.context.root,
            "previous_receipt_id": self.last_receipt_id,
        }
        artifact_id = artifact_type.lower().replace("_", "-") + ":" + domain_digest(
            "ASET/Reference/ArtifactID/v1", material
        )[7:]
        artifact = Artifact(artifact_id=artifact_id, **material)
        self.artifacts[artifact_id] = artifact
        return artifact

    def _patch(
        self,
        patch_type: str,
        gate_id: str,
        writes: dict[str, dict[str, Any]],
    ) -> GovernedPatch:
        material = {
            "patch_type": patch_type,
            "gate_id": gate_id,
            "source_context_root": self.context.root,
            "writes": normalized_json(writes),
            "previous_receipt_id": self.last_receipt_id,
        }
        patch_id = patch_type.lower().replace("_", "-") + ":" + domain_digest(
            "ASET/Reference/PatchID/v1", material
        )[7:]
        patch = GovernedPatch(patch_id=patch_id, **material)
        self.patches[patch_id] = patch
        return patch

    def authorize(self, patch: GovernedPatch) -> tuple[CoreResolution, Permit]:
        if patch.source_context_root != self.context.root:
            raise ReferenceError("SOURCE_CONTEXT_STALE")
        resolution_material = {
            "gate_id": patch.gate_id,
            "patch_id": patch.patch_id,
            "patch_digest": patch.digest,
            "source_context_root": patch.source_context_root,
            "verdict": "PERMIT",
        }
        resolution_id = "resolution:" + domain_digest(
            "ASET/Reference/CoreResolutionID/v1", resolution_material
        )[7:]
        resolution = CoreResolution(resolution_id=resolution_id, **resolution_material)
        permit_material = {
            "resolution_id": resolution_id,
            "gate_id": patch.gate_id,
            "patch_id": patch.patch_id,
            "patch_digest": patch.digest,
            "source_context_root": patch.source_context_root,
        }
        permit_id = "permit:" + domain_digest(
            "ASET/Reference/PermitID/v1", permit_material
        )[7:]
        permit = Permit(permit_id=permit_id, **permit_material)
        self.resolutions[resolution_id] = resolution
        self.permits[permit_id] = permit
        return resolution, permit

    def cross(
        self,
        patch: GovernedPatch,
        resolution: CoreResolution,
        permit: Permit,
    ) -> PermitUseReceipt:
        self._validate_crossing_inputs(patch, resolution, permit)
        sections = deepcopy(plain_json(self.context.sections))
        for namespace, replacement in plain_json(patch.writes).items():
            sections[namespace] = replacement
        next_version = self.context.version + 1
        next_root = self._context_root(self.context.context_id, next_version, sections)
        receipt_material = {
            "permit_id": permit.permit_id,
            "resolution_id": resolution.resolution_id,
            "gate_id": patch.gate_id,
            "patch_id": patch.patch_id,
            "patch_digest": patch.digest,
            "source_context_root": self.context.root,
            "resulting_context_root": next_root,
            "resulting_context_version": next_version,
            "previous_receipt_id": self.last_receipt_id,
        }
        receipt_id = "receipt:" + domain_digest(
            "ASET/Reference/PermitUseReceiptID/v1", receipt_material
        )[7:]
        receipt = PermitUseReceipt(receipt_id=receipt_id, **receipt_material)
        ordinal = len(self.crossings) + 1
        crossing_material = {
            "ordinal": ordinal,
            "gate_id": patch.gate_id,
            "patch_id": patch.patch_id,
            "permit_id": permit.permit_id,
            "receipt_id": receipt_id,
            "source_context_root": self.context.root,
            "resulting_context_root": next_root,
        }
        crossing_id = "crossing:" + domain_digest(
            "ASET/Reference/GateCrossingID/v1", crossing_material
        )[7:]
        crossing = GateCrossing(crossing_id=crossing_id, **crossing_material)
        self.context = Context(
            context_id=self.context.context_id,
            version=next_version,
            sections=sections,
            root=next_root,
        )
        self.receipts[receipt_id] = receipt
        self.crossings.append(crossing)
        self.consumed_permit_ids.add(permit.permit_id)
        self.last_receipt_id = receipt_id
        return receipt

    def _validate_crossing_inputs(
        self,
        patch: GovernedPatch,
        resolution: CoreResolution,
        permit: Permit,
    ) -> None:
        if patch.gate_id not in GATE_WRITES:
            raise ReferenceError("GATE_UNKNOWN")
        if frozenset(patch.writes) != GATE_WRITES[patch.gate_id]:
            raise ReferenceError("WRITE_SET_MISMATCH")
        if permit.permit_id in self.consumed_permit_ids:
            raise ReferenceError("PERMIT_ALREADY_CONSUMED")
        if patch.source_context_root != self.context.root:
            raise ReferenceError("SOURCE_CONTEXT_STALE")
        if patch.previous_receipt_id != self.last_receipt_id:
            raise ReferenceError("PREDECESSOR_RECEIPT_MISMATCH")
        expected = (
            patch.gate_id,
            patch.patch_id,
            patch.digest,
            patch.source_context_root,
        )
        if (
            resolution.gate_id,
            resolution.patch_id,
            resolution.patch_digest,
            resolution.source_context_root,
        ) != expected:
            raise ReferenceError("RESOLUTION_BINDING_MISMATCH")
        if (
            permit.gate_id,
            permit.patch_id,
            permit.patch_digest,
            permit.source_context_root,
        ) != expected:
            raise ReferenceError("PERMIT_BINDING_MISMATCH")
        if permit.resolution_id != resolution.resolution_id:
            raise ReferenceError("PERMIT_RESOLUTION_MISMATCH")

    def governed_crossing(
        self,
        patch_type: str,
        gate_id: str,
        writes: dict[str, dict[str, Any]],
    ) -> PermitUseReceipt:
        patch = self._patch(patch_type, gate_id, writes)
        resolution, permit = self.authorize(patch)
        return self.cross(patch, resolution, permit)

    def run(self, effect_class: str = "SUCCESS") -> CriticalPathResult:
        if self.crossings:
            raise ReferenceError("MACHINE_ALREADY_USED")
        if effect_class not in EFFECT_CLASSES:
            raise ReferenceError("EFFECT_CLASS_UNSUPPORTED")

        projection = self._artifact(
            "ContextProjection",
            {"claims": ["goal:demo"], "epistemic_status": "CONTEXTUAL"},
        )
        self.governed_crossing(
            "ContextProjectionPatch",
            "GATE-CONTEXT-PROJECT",
            {
                "CTX-MEM": {"projection_id": projection.artifact_id},
                "CTX-TASK": {"status": "PROJECTED"},
            },
        )

        plan = self._artifact("PlanProposal", {"goal": "demo", "steps": ["deterministic-effect"]})
        expected = self._artifact(
            "ExpectedChangePatch",
            {
                "plan_proposal_id": plan.artifact_id,
                "expected_claim": "effect classified",
                "preserved_invariants": ["proposal-not-authority"],
            },
        )
        self.governed_crossing(
            "ExpectedChangeAdmissionPatch",
            "GATE-EXPECT-ADMIT",
            {
                "CTX-MAST": {
                    "plan_proposal_id": plan.artifact_id,
                    "expected_change_id": expected.artifact_id,
                },
                "CTX-TASK": {"status": "EXPECTATION_ADMITTED"},
            },
        )

        binding = self._artifact(
            "OperationalBinding",
            {
                "expected_change_id": expected.artifact_id,
                "actor": "reference-worker",
                "operation": "classify-effect",
                "limits": {"operations": 1},
            },
        )
        self.governed_crossing(
            "OperationalBindingPatch",
            "GATE-EXEC-BIND",
            {"CTX-EXEC": {"operational_binding_id": binding.artifact_id}},
        )

        intent = self._artifact(
            "ExecutionIntent",
            {
                "operational_binding_id": binding.artifact_id,
                "effect_class_request": effect_class,
            },
        )
        self.governed_crossing(
            "ExecutionIntentPatch",
            "GATE-DISPATCH",
            {
                "CTX-EXEC": {
                    "operational_binding_id": binding.artifact_id,
                    "execution_intent_id": intent.artifact_id,
                    "status": "DISPATCHED",
                },
                "CTX-AUTH": {"dispatch_authorized": True},
            },
        )

        connector = DeterministicConnector()
        effect = connector.execute(intent, effect_class)
        self.effects[effect.effect_id] = effect
        observation = self._artifact(
            "Observation",
            {
                "execution_intent_id": intent.artifact_id,
                "effect_id": effect.effect_id,
                "effect_class": effect.effect_class,
            },
        )
        self.governed_crossing(
            "ObservationPatch",
            "GATE-OBSERVE",
            {
                "CTX-EXEC": {
                    "execution_intent_id": intent.artifact_id,
                    "observation_id": observation.artifact_id,
                    "status": "OBSERVED",
                }
            },
        )

        evidence = self._artifact(
            "EvidenceBundle",
            {
                "observation_id": observation.artifact_id,
                "effect_class": effect.effect_class,
                "evidence_status": "COMPLETE" if effect_class != "UNKNOWN" else "INCONCLUSIVE",
            },
        )
        self.governed_crossing(
            "EvidencePatch",
            "GATE-EVIDENCE",
            {"CTX-ACCE": {"evidence_bundle_id": evidence.artifact_id}},
        )

        verification_status = "PASS" if effect_class != "UNKNOWN" else "FAIL"
        verification = self._artifact(
            "Verification",
            {
                "observation_id": observation.artifact_id,
                "evidence_bundle_id": evidence.artifact_id,
                "status": verification_status,
                "verified_effect_class": effect_class,
            },
        )
        acceptance = self._artifact(
            "AcceptanceDecision",
            {
                "verification_id": verification.artifact_id,
                "verdict": "ACCEPT" if verification_status == "PASS" else "REJECT",
            },
        )
        self.governed_crossing(
            "AcceptanceResultPatch",
            "GATE-ACCEPT",
            {
                "CTX-ACCE": {
                    "evidence_bundle_id": evidence.artifact_id,
                    "verification_id": verification.artifact_id,
                    "acceptance_decision_id": acceptance.artifact_id,
                },
                "CTX-TASK": {
                    "status": "VERIFIED" if verification_status == "PASS" else "REJECTED"
                },
            },
        )

        outcome: Artifact | None = None
        if verification_status == "PASS":
            outcome = self._artifact(
                "Outcome",
                {
                    "verification_ids": [verification.artifact_id],
                    "classification": effect_class,
                },
            )
        learning = self._artifact(
            "LearningObservation",
            {
                "verification_id": verification.artifact_id,
                "outcome_id": outcome.artifact_id if outcome else None,
            },
        )
        self.governed_crossing(
            "TaskCompletionPatch",
            "GATE-TASK-CLOSE",
            {
                "CTX-ACCE": {
                    "verification_id": verification.artifact_id,
                    "acceptance_decision_id": acceptance.artifact_id,
                    "outcome_id": outcome.artifact_id if outcome else None,
                    "learning_observation_id": learning.artifact_id,
                },
                "CTX-TASK": {
                    "status": "CLOSED" if outcome else "REJECTED",
                    "outcome_id": outcome.artifact_id if outcome else None,
                },
            },
        )

        return CriticalPathResult(
            effect_class=effect_class,
            final_context=self.context,
            outcome=outcome,
            verification=verification,
            acceptance_decision=acceptance,
            artifacts=tuple(self.artifacts.values()),
            crossings=tuple(self.crossings),
            receipts=tuple(self.receipts.values()),
        )

    def snapshot(self) -> dict[str, Any]:
        return {
            "document_type": "aset-python-reference-snapshot",
            "version": 1,
            "context": self.context.as_dict(),
            "artifacts": {key: value.as_dict() for key, value in sorted(self.artifacts.items())},
            "patches": {key: value.as_dict() for key, value in sorted(self.patches.items())},
            "resolutions": {
                key: value.as_dict() for key, value in sorted(self.resolutions.items())
            },
            "permits": {key: value.as_dict() for key, value in sorted(self.permits.items())},
            "receipts": {key: value.as_dict() for key, value in sorted(self.receipts.items())},
            "crossings": [value.as_dict() for value in self.crossings],
            "effects": {key: value.as_dict() for key, value in sorted(self.effects.items())},
            "consumed_permit_ids": sorted(self.consumed_permit_ids),
            "last_receipt_id": self.last_receipt_id,
        }

    @classmethod
    def restore(cls, source: dict[str, Any]) -> ReferenceMachine:
        data = normalized_json(source)
        if (
            data.get("document_type") != "aset-python-reference-snapshot"
            or data.get("version") != 1
        ):
            raise ReferenceError("SNAPSHOT_PROFILE_INVALID")
        context = Context(**data["context"])
        machine = cls(context.context_id)
        machine.context = context
        machine.artifacts = {
            key: Artifact(**value) for key, value in data.get("artifacts", {}).items()
        }
        machine.patches = {
            key: GovernedPatch(**value) for key, value in data.get("patches", {}).items()
        }
        machine.resolutions = {
            key: CoreResolution(**value) for key, value in data.get("resolutions", {}).items()
        }
        machine.permits = {key: Permit(**value) for key, value in data.get("permits", {}).items()}
        machine.receipts = {
            key: PermitUseReceipt(**value) for key, value in data.get("receipts", {}).items()
        }
        machine.crossings = [GateCrossing(**value) for value in data.get("crossings", [])]
        machine.effects = {
            key: EffectRecord(**value) for key, value in data.get("effects", {}).items()
        }
        machine.consumed_permit_ids = set(data.get("consumed_permit_ids", []))
        machine.last_receipt_id = data.get("last_receipt_id")
        machine._validate_snapshot()
        return machine

    def _validate_snapshot(self) -> None:
        sections = plain_json(self.context.sections)
        expected_root = self._context_root(self.context.context_id, self.context.version, sections)
        if self.context.root != expected_root:
            raise ReferenceError("CONTEXT_ROOT_INVALID")
        indexed = (
            (self.artifacts, "artifact_id"),
            (self.patches, "patch_id"),
            (self.resolutions, "resolution_id"),
            (self.permits, "permit_id"),
            (self.receipts, "receipt_id"),
            (self.effects, "effect_id"),
        )
        for mapping, attribute in indexed:
            for key, value in mapping.items():
                if key != getattr(value, attribute):
                    raise ReferenceError("SNAPSHOT_MAP_KEY_MISMATCH")
        previous_root = self._context_root(
            self.context.context_id,
            0,
            {
                "CTX-MEM": {},
                "CTX-MAST": {},
                "CTX-EXEC": {},
                "CTX-ACCE": {},
                "CTX-TASK": {"status": "NEW"},
                "CTX-AUTH": {},
            },
        )
        previous_receipt: str | None = None
        consumed: set[str] = set()
        for index, crossing in enumerate(self.crossings, start=1):
            if crossing.ordinal != index or crossing.source_context_root != previous_root:
                raise ReferenceError("CROSSING_CHAIN_INVALID")
            receipt = self.receipts.get(crossing.receipt_id)
            permit = self.permits.get(crossing.permit_id)
            patch = self.patches.get(crossing.patch_id)
            if receipt is None or permit is None or patch is None:
                raise ReferenceError("CROSSING_REFERENCE_MISSING")
            resolution = self.resolutions.get(permit.resolution_id)
            if resolution is None:
                raise ReferenceError("RESOLUTION_REFERENCE_MISSING")
            expected = (
                patch.gate_id,
                patch.patch_id,
                patch.digest,
                patch.source_context_root,
            )
            if (
                resolution.gate_id,
                resolution.patch_id,
                resolution.patch_digest,
                resolution.source_context_root,
            ) != expected:
                raise ReferenceError("RESOLUTION_CHAIN_INVALID")
            if (
                permit.gate_id,
                permit.patch_id,
                permit.patch_digest,
                permit.source_context_root,
            ) != expected or permit.resolution_id != resolution.resolution_id:
                raise ReferenceError("PERMIT_CHAIN_INVALID")
            if (
                receipt.permit_id != permit.permit_id
                or receipt.resolution_id != resolution.resolution_id
                or receipt.gate_id != patch.gate_id
                or receipt.patch_id != patch.patch_id
                or receipt.patch_digest != patch.digest
                or receipt.source_context_root != previous_root
                or receipt.resulting_context_root != crossing.resulting_context_root
                or receipt.resulting_context_version != index
                or receipt.previous_receipt_id != previous_receipt
                or patch.previous_receipt_id != previous_receipt
            ):
                raise ReferenceError("RECEIPT_CHAIN_INVALID")
            if frozenset(patch.writes) != GATE_WRITES.get(patch.gate_id):
                raise ReferenceError("WRITE_SET_MISMATCH")
            previous_root = crossing.resulting_context_root
            previous_receipt = receipt.receipt_id
            consumed.add(permit.permit_id)
        if previous_root != self.context.root or len(self.crossings) != self.context.version:
            raise ReferenceError("FINAL_CONTEXT_CHAIN_INVALID")
        if consumed != self.consumed_permit_ids:
            raise ReferenceError("CONSUMED_PERMIT_SET_INVALID")
        if previous_receipt != self.last_receipt_id:
            raise ReferenceError("LAST_RECEIPT_INVALID")


def run_critical_path(effect_class: str = "SUCCESS") -> CriticalPathResult:
    """Run one complete deterministic semantic critical-path execution."""
    return ReferenceMachine().run(effect_class)

"""Immutable values for the full ASET semantic critical-path reference."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .canonical import domain_digest, freeze_json, plain_json

JsonMap = Mapping[str, Any]


def _required_text(value: str, field: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")


def _digest(value: str, field: str) -> None:
    _required_text(value, field)
    if not value.startswith("sha256:") or len(value) != 71:
        raise ValueError(f"{field} must be a sha256 digest")


def frozen_map(value: Mapping[str, Any]) -> JsonMap:
    frozen = freeze_json(value)
    if not isinstance(frozen, Mapping):
        raise TypeError("expected JSON object")
    return frozen


@dataclass(frozen=True, slots=True)
class Context:
    context_id: str
    version: int
    sections: JsonMap
    root: str

    def __post_init__(self) -> None:
        _required_text(self.context_id, "context_id")
        if not isinstance(self.version, int) or isinstance(self.version, bool) or self.version < 0:
            raise ValueError("version must be a non-negative integer")
        object.__setattr__(self, "sections", frozen_map(self.sections))
        _digest(self.root, "root")

    def as_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "version": self.version,
            "sections": plain_json(self.sections),
            "root": self.root,
        }


@dataclass(frozen=True, slots=True)
class Artifact:
    artifact_id: str
    artifact_type: str
    payload: JsonMap
    source_context_root: str
    previous_receipt_id: str | None = None

    def __post_init__(self) -> None:
        _required_text(self.artifact_id, "artifact_id")
        _required_text(self.artifact_type, "artifact_type")
        object.__setattr__(self, "payload", frozen_map(self.payload))
        _digest(self.source_context_root, "source_context_root")
        if self.previous_receipt_id is not None:
            _required_text(self.previous_receipt_id, "previous_receipt_id")

    def as_dict(self) -> dict[str, Any]:
        return {
            "artifact_id": self.artifact_id,
            "artifact_type": self.artifact_type,
            "payload": plain_json(self.payload),
            "source_context_root": self.source_context_root,
            "previous_receipt_id": self.previous_receipt_id,
        }

    @property
    def digest(self) -> str:
        return domain_digest("ASET/Reference/Artifact/v1", self.as_dict())


@dataclass(frozen=True, slots=True)
class GovernedPatch:
    patch_id: str
    patch_type: str
    gate_id: str
    source_context_root: str
    writes: JsonMap
    previous_receipt_id: str | None

    def __post_init__(self) -> None:
        _required_text(self.patch_id, "patch_id")
        _required_text(self.patch_type, "patch_type")
        _required_text(self.gate_id, "gate_id")
        _digest(self.source_context_root, "source_context_root")
        object.__setattr__(self, "writes", frozen_map(self.writes))
        if not self.writes:
            raise ValueError("writes must not be empty")
        if self.previous_receipt_id is not None:
            _required_text(self.previous_receipt_id, "previous_receipt_id")

    def as_dict(self) -> dict[str, Any]:
        return {
            "patch_id": self.patch_id,
            "patch_type": self.patch_type,
            "gate_id": self.gate_id,
            "source_context_root": self.source_context_root,
            "writes": plain_json(self.writes),
            "previous_receipt_id": self.previous_receipt_id,
        }

    @property
    def digest(self) -> str:
        return domain_digest("ASET/Reference/GovernedPatch/v1", self.as_dict())


@dataclass(frozen=True, slots=True)
class CoreResolution:
    resolution_id: str
    gate_id: str
    patch_id: str
    patch_digest: str
    source_context_root: str
    verdict: str = "PERMIT"

    def __post_init__(self) -> None:
        _required_text(self.resolution_id, "resolution_id")
        _required_text(self.gate_id, "gate_id")
        _required_text(self.patch_id, "patch_id")
        _digest(self.patch_digest, "patch_digest")
        _digest(self.source_context_root, "source_context_root")
        if self.verdict != "PERMIT":
            raise ValueError("reference resolution verdict must be PERMIT")

    def as_dict(self) -> dict[str, Any]:
        return {
            "resolution_id": self.resolution_id,
            "gate_id": self.gate_id,
            "patch_id": self.patch_id,
            "patch_digest": self.patch_digest,
            "source_context_root": self.source_context_root,
            "verdict": self.verdict,
        }


@dataclass(frozen=True, slots=True)
class Permit:
    permit_id: str
    resolution_id: str
    gate_id: str
    patch_id: str
    patch_digest: str
    source_context_root: str

    def __post_init__(self) -> None:
        _required_text(self.permit_id, "permit_id")
        _required_text(self.resolution_id, "resolution_id")
        _required_text(self.gate_id, "gate_id")
        _required_text(self.patch_id, "patch_id")
        _digest(self.patch_digest, "patch_digest")
        _digest(self.source_context_root, "source_context_root")

    def as_dict(self) -> dict[str, Any]:
        return {
            "permit_id": self.permit_id,
            "resolution_id": self.resolution_id,
            "gate_id": self.gate_id,
            "patch_id": self.patch_id,
            "patch_digest": self.patch_digest,
            "source_context_root": self.source_context_root,
        }


@dataclass(frozen=True, slots=True)
class PermitUseReceipt:
    receipt_id: str
    permit_id: str
    resolution_id: str
    gate_id: str
    patch_id: str
    patch_digest: str
    source_context_root: str
    resulting_context_root: str
    resulting_context_version: int
    previous_receipt_id: str | None

    def __post_init__(self) -> None:
        for field, value in (
            ("receipt_id", self.receipt_id),
            ("permit_id", self.permit_id),
            ("resolution_id", self.resolution_id),
            ("gate_id", self.gate_id),
            ("patch_id", self.patch_id),
        ):
            _required_text(value, field)
        _digest(self.patch_digest, "patch_digest")
        _digest(self.source_context_root, "source_context_root")
        _digest(self.resulting_context_root, "resulting_context_root")
        if self.resulting_context_version < 1:
            raise ValueError("resulting_context_version must be positive")
        if self.previous_receipt_id is not None:
            _required_text(self.previous_receipt_id, "previous_receipt_id")

    def as_dict(self) -> dict[str, Any]:
        return {
            "receipt_id": self.receipt_id,
            "permit_id": self.permit_id,
            "resolution_id": self.resolution_id,
            "gate_id": self.gate_id,
            "patch_id": self.patch_id,
            "patch_digest": self.patch_digest,
            "source_context_root": self.source_context_root,
            "resulting_context_root": self.resulting_context_root,
            "resulting_context_version": self.resulting_context_version,
            "previous_receipt_id": self.previous_receipt_id,
        }


@dataclass(frozen=True, slots=True)
class GateCrossing:
    crossing_id: str
    ordinal: int
    gate_id: str
    patch_id: str
    permit_id: str
    receipt_id: str
    source_context_root: str
    resulting_context_root: str

    def __post_init__(self) -> None:
        for field, value in (
            ("crossing_id", self.crossing_id),
            ("gate_id", self.gate_id),
            ("patch_id", self.patch_id),
            ("permit_id", self.permit_id),
            ("receipt_id", self.receipt_id),
        ):
            _required_text(value, field)
        if self.ordinal < 1:
            raise ValueError("ordinal must be positive")
        _digest(self.source_context_root, "source_context_root")
        _digest(self.resulting_context_root, "resulting_context_root")

    def as_dict(self) -> dict[str, Any]:
        return {
            "crossing_id": self.crossing_id,
            "ordinal": self.ordinal,
            "gate_id": self.gate_id,
            "patch_id": self.patch_id,
            "permit_id": self.permit_id,
            "receipt_id": self.receipt_id,
            "source_context_root": self.source_context_root,
            "resulting_context_root": self.resulting_context_root,
        }


@dataclass(frozen=True, slots=True)
class EffectRecord:
    effect_id: str
    intent_id: str
    effect_class: str
    idempotency_key: str

    def __post_init__(self) -> None:
        for field, value in (
            ("effect_id", self.effect_id),
            ("intent_id", self.intent_id),
            ("idempotency_key", self.idempotency_key),
        ):
            _required_text(value, field)
        if self.effect_class not in {"SUCCESS", "FAILURE", "NO_EFFECT", "UNKNOWN"}:
            raise ValueError("unsupported effect_class")

    def as_dict(self) -> dict[str, Any]:
        return {
            "effect_id": self.effect_id,
            "intent_id": self.intent_id,
            "effect_class": self.effect_class,
            "idempotency_key": self.idempotency_key,
        }


@dataclass(frozen=True, slots=True)
class CriticalPathResult:
    effect_class: str
    final_context: Context
    outcome: Artifact | None
    verification: Artifact
    acceptance_decision: Artifact
    artifacts: tuple[Artifact, ...]
    crossings: tuple[GateCrossing, ...]
    receipts: tuple[PermitUseReceipt, ...]

    @property
    def terminal_status(self) -> str:
        task = plain_json(self.final_context.sections)["CTX-TASK"]
        return str(task["status"])

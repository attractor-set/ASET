"""Immutable values for the storage-free ASET reference kernel."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from .canonical import freeze_json, plain_json

JsonMap = Mapping[str, Any]


def frozen_map(value: Mapping[str, Any]) -> JsonMap:
    frozen = freeze_json(value)
    if not isinstance(frozen, Mapping):
        raise TypeError("expected JSON object")
    return frozen


@dataclass(frozen=True, slots=True)
class Context:
    context_id: str
    version: int
    state: JsonMap
    consumed_permit_ids: frozenset[str] = frozenset()
    suspended: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "state", frozen_map(self.state))

    def as_dict(self) -> dict[str, Any]:
        return {
            "context_id": self.context_id,
            "version": self.version,
            "state": plain_json(self.state),
            "consumed_permit_ids": sorted(self.consumed_permit_ids),
            "suspended": self.suspended,
        }


@dataclass(frozen=True, slots=True)
class Proposal:
    proposal_id: str
    context_id: str
    expected_context_version: int
    gate_id: str
    patch: JsonMap

    def __post_init__(self) -> None:
        object.__setattr__(self, "patch", frozen_map(self.patch))

    def as_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "context_id": self.context_id,
            "expected_context_version": self.expected_context_version,
            "gate_id": self.gate_id,
            "patch": plain_json(self.patch),
        }


@dataclass(frozen=True, slots=True)
class Permit:
    permit_id: str
    proposal_digest: str
    context_id: str
    expected_context_version: int
    gate_id: str
    required_evidence_types: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Evidence:
    evidence_id: str
    evidence_type: str
    proposal_digest: str
    payload: JsonMap

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", frozen_map(self.payload))


@dataclass(frozen=True, slots=True)
class TransitionAccepted:
    previous_context: Context
    next_context: Context
    consumed_permit_id: str
    proposal_digest: str
    transition_digest: str
    audit_record: JsonMap


@dataclass(frozen=True, slots=True)
class TransitionRejected:
    reason_code: str
    failed_requirement: str
    context_unchanged: bool = True
    permit_consumed: bool = False

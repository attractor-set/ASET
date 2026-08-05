"""Pure ASET critical-path transition semantics.

The kernel accepts immutable values and returns an immutable normative result.
It performs no persistence, network, subprocess, clock, randomness, or external effect.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .canonical import sha256_digest
from .model import (
    Context,
    Evidence,
    Permit,
    Proposal,
    TransitionAccepted,
    TransitionRejected,
    frozen_map,
)


def _reject(code: str, requirement: str) -> TransitionRejected:
    return TransitionRejected(reason_code=code, failed_requirement=requirement)


def _evidence_types(evidence: Iterable[Evidence], proposal_digest: str) -> set[str] | None:
    types: set[str] = set()
    for item in evidence:
        if item.proposal_digest != proposal_digest:
            return None
        if item.evidence_type in types:
            return None
        types.add(item.evidence_type)
    return types


def apply_transition(
    *,
    context: Context,
    proposal: Proposal,
    permit: Permit,
    evidence: tuple[Evidence, ...] = (),
) -> TransitionAccepted | TransitionRejected:
    """Evaluate one ASET context transition without performing side effects."""
    if not context.context_id or context.version < 0:
        return _reject("INVALID_CONTEXT", "ASET-SEED-REQ-001")
    if proposal.context_id != context.context_id:
        return _reject("PROPOSAL_CONTEXT_MISMATCH", "ASET-SEED-REQ-003")
    if proposal.expected_context_version != context.version:
        return _reject("STALE_CONTEXT", "ASET-SEED-REQ-003")
    if context.suspended:
        return _reject("CONTEXT_SUSPENDED", "ASET-SEED-REQ-011")
    if not proposal.proposal_id or not proposal.gate_id or not proposal.patch:
        return _reject("INVALID_PROPOSAL", "ASET-SEED-REQ-001")

    proposal_digest = sha256_digest(proposal.as_dict())
    if permit.permit_id in context.consumed_permit_ids:
        return _reject("PERMIT_ALREADY_CONSUMED", "SEED-INV-011")
    if permit.proposal_digest != proposal_digest:
        return _reject("PERMIT_PROPOSAL_MISMATCH", "ASET-SEED-REQ-005")
    if permit.context_id != context.context_id:
        return _reject("PERMIT_CONTEXT_MISMATCH", "ASET-SEED-REQ-005")
    if permit.expected_context_version != context.version:
        return _reject("PERMIT_STALE_CONTEXT", "ASET-SEED-REQ-005")
    if permit.gate_id != proposal.gate_id:
        return _reject("PERMIT_GATE_MISMATCH", "ASET-SEED-REQ-005")

    supplied_types = _evidence_types(evidence, proposal_digest)
    if supplied_types is None:
        return _reject("INVALID_EVIDENCE_BINDING", "SEED-INV-014")
    if set(permit.required_evidence_types) != supplied_types:
        return _reject("INCOMPLETE_EVIDENCE", "ASET-SEED-REQ-008")

    next_state: dict[str, Any] = dict(context.state)
    next_state.update(proposal.patch)
    next_context = Context(
        context_id=context.context_id,
        version=context.version + 1,
        state=next_state,
        consumed_permit_ids=context.consumed_permit_ids | {permit.permit_id},
        suspended=context.suspended,
    )
    transition_material = {
        "previous_context": context.as_dict(),
        "proposal": proposal.as_dict(),
        "permit_id": permit.permit_id,
        "evidence_ids": sorted(item.evidence_id for item in evidence),
        "next_context": next_context.as_dict(),
    }
    transition_digest = sha256_digest(transition_material)
    audit_record = frozen_map(
        {
            "context_id": context.context_id,
            "previous_version": context.version,
            "next_version": next_context.version,
            "proposal_id": proposal.proposal_id,
            "proposal_digest": proposal_digest,
            "permit_id": permit.permit_id,
            "gate_id": proposal.gate_id,
            "transition_digest": transition_digest,
        }
    )
    return TransitionAccepted(
        previous_context=context,
        next_context=next_context,
        consumed_permit_id=permit.permit_id,
        proposal_digest=proposal_digest,
        transition_digest=transition_digest,
        audit_record=audit_record,
    )

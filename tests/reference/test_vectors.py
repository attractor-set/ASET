from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from aset_reference import Context, Evidence, Permit, Proposal, TransitionAccepted, apply_transition
from aset_reference.canonical import sha256_digest

ROOT = Path(__file__).resolve().parents[2]


def load_base():
    data = json.loads((ROOT / "test-vectors/reference/accepted-basic.json").read_text())
    context_data = dict(data["context"])
    context_data["consumed_permit_ids"] = frozenset(context_data["consumed_permit_ids"])
    context = Context(**context_data)
    proposal = Proposal(**data["proposal"])
    digest = sha256_digest(proposal.as_dict())
    permit_data = dict(data["permit"])
    permit_data["required_evidence_types"] = tuple(permit_data["required_evidence_types"])
    permit = Permit(**permit_data, proposal_digest=digest)
    evidence = tuple(Evidence(**item, proposal_digest=digest) for item in data["evidence"])
    return data, context, proposal, permit, evidence


def test_language_neutral_acceptance_vector():
    data, context, proposal, permit, evidence = load_base()
    result = apply_transition(context=context, proposal=proposal, permit=permit, evidence=evidence)
    assert isinstance(result, TransitionAccepted)
    assert result.next_context.version == data["expected"]["next_version"]
    assert result.next_context.as_dict()["state"] == data["expected"]["next_state"]
    assert result.consumed_permit_id == data["expected"]["consumed_permit_id"]


def test_language_neutral_rejection_vectors():
    _, base_context, base_proposal, base_permit, base_evidence = load_base()
    cases = json.loads((ROOT / "test-vectors/reference/rejected-cases.json").read_text())["cases"]
    for case in cases:
        context, proposal, permit, evidence = base_context, base_proposal, base_permit, base_evidence
        if case["mutation"] == "proposal_version":
            proposal = replace(proposal, expected_context_version=case["value"])
        elif case["mutation"] == "permit_gate":
            permit = replace(permit, gate_id=case["value"])
        elif case["mutation"] == "drop_evidence":
            evidence = ()
        elif case["mutation"] == "consume_permit":
            context = replace(context, consumed_permit_ids=frozenset({permit.permit_id}))
        elif case["mutation"] == "suspend_context":
            context = replace(context, suspended=True)
        result = apply_transition(context=context, proposal=proposal, permit=permit, evidence=evidence)
        assert result.reason_code == case["reason_code"], case["case_id"]

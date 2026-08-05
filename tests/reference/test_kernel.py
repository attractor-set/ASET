from __future__ import annotations

from dataclasses import replace

from aset_reference import Context, Evidence, Permit, Proposal, TransitionAccepted, apply_transition
from aset_reference.canonical import sha256_digest


def fixture():
    context = Context(context_id="ctx:1", version=3, state={"status": "draft"})
    proposal = Proposal(
        proposal_id="proposal:1",
        context_id="ctx:1",
        expected_context_version=3,
        gate_id="gate:approve",
        patch={"status": "approved"},
    )
    digest = sha256_digest(proposal.as_dict())
    permit = Permit(
        permit_id="permit:1",
        proposal_digest=digest,
        context_id="ctx:1",
        expected_context_version=3,
        gate_id="gate:approve",
        required_evidence_types=("review",),
    )
    evidence = Evidence("evidence:1", "review", digest, {"verdict": "PASS"})
    return context, proposal, permit, evidence


def test_accepts_bound_transition_and_returns_commit_material():
    context, proposal, permit, evidence = fixture()
    result = apply_transition(context=context, proposal=proposal, permit=permit, evidence=(evidence,))
    assert isinstance(result, TransitionAccepted)
    assert result.next_context.version == 4
    assert result.next_context.state == {"status": "approved"}
    assert result.next_context.consumed_permit_ids == {"permit:1"}
    assert context.version == 3
    assert context.state == {"status": "draft"}


def test_rejects_each_binding_failure_without_consuming_permit():
    context, proposal, permit, evidence = fixture()
    cases = [
        (replace(proposal, context_id="ctx:other"), permit, (evidence,), "PROPOSAL_CONTEXT_MISMATCH"),
        (replace(proposal, expected_context_version=2), permit, (evidence,), "STALE_CONTEXT"),
        (proposal, replace(permit, proposal_digest="sha256:" + "0" * 64), (evidence,), "PERMIT_PROPOSAL_MISMATCH"),
        (proposal, replace(permit, gate_id="gate:other"), (evidence,), "PERMIT_GATE_MISMATCH"),
        (proposal, permit, (), "INCOMPLETE_EVIDENCE"),
    ]
    for candidate, candidate_permit, candidate_evidence, code in cases:
        result = apply_transition(
            context=context,
            proposal=candidate,
            permit=candidate_permit,
            evidence=candidate_evidence,
        )
        assert result.reason_code == code
        assert result.context_unchanged is True
        assert result.permit_consumed is False


def test_rejects_replay_and_suspended_context():
    context, proposal, permit, evidence = fixture()
    replay_context = replace(context, consumed_permit_ids=frozenset({permit.permit_id}))
    assert apply_transition(context=replay_context, proposal=proposal, permit=permit, evidence=(evidence,)).reason_code == "PERMIT_ALREADY_CONSUMED"
    suspended = replace(context, suspended=True)
    assert apply_transition(context=suspended, proposal=proposal, permit=permit, evidence=(evidence,)).reason_code == "CONTEXT_SUSPENDED"


def test_is_deterministic():
    args = fixture()
    first = apply_transition(context=args[0], proposal=args[1], permit=args[2], evidence=(args[3],))
    second = apply_transition(context=args[0], proposal=args[1], permit=args[2], evidence=(args[3],))
    assert first == second


def test_inputs_are_deeply_frozen_and_non_json_values_are_rejected():
    nested = {"items": [{"value": 1}]}
    context = Context(context_id="ctx:1", version=0, state=nested)
    nested["items"][0]["value"] = 9
    assert context.as_dict()["state"] == {"items": [{"value": 1}]}

    import pytest

    with pytest.raises(ValueError):
        Context(context_id="ctx:1", version=0, state={"bad": float("nan")})
    with pytest.raises(TypeError):
        Context(context_id="ctx:1", version=0, state={"bad": object()})

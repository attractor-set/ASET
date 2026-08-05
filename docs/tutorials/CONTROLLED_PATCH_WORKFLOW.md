[English](CONTROLLED_PATCH_WORKFLOW.md) · [Русский](CONTROLLED_PATCH_WORKFLOW.ru.md) · [Português do Brasil](CONTROLLED_PATCH_WORKFLOW.pt-BR.md)

# Walkthrough: a controlled patch by an AI agent

This walkthrough is non-normative. It explains one end-to-end use of the existing ASET distinctions and points to the machine canon; it does not define new document fields or transition rules.

## Scenario

An organization wants an AI agent to propose a repository patch. The patch may affect an external repository only after a specific authority decision, a one-shot permit and an atomic gate crossing. A successful command is not yet an accepted outcome.

## Sequence

1. **Proposal.** The agent produces a proposal containing the intended patch and its exact target context. A proposal expresses requested change; it carries no authority.
2. **Resolution.** The relevant authority evaluates the exact proposal under the current context and returns a permitted or prohibited resolution. The resolution is not itself a reusable credential.
3. **Permit.** A permitted resolution may ground one permit bound to the exact document digest, context, gate, crossing and actor/execution identity. The permit authorizes one immediate crossing only.
4. **Gate crossing and receipt.** The gate validates the permit and context, applies the canonical patch atomically, consumes the permit and emits a receipt. Replay of the same crossing returns the same result; the permit cannot authorize another crossing.
5. **Execution intent.** Authorization to include an expected change in context is distinct from authorization to perform an external effect. A separate execution decision and permit are required before dispatching the repository operation.
6. **Observation.** The worker reports what was observed after the attempt. An observation is not evidence and does not prove that the intended result occurred.
7. **Evidence and verification.** Admitted evidence is evaluated against explicit acceptance criteria. Verification classifies the result; verifier failure or uncertainty cannot ground a successful outcome.
8. **Outcome.** The relevant context locally recognizes an outcome only from valid verification. Other contexts retain their own authority and recognition rules.

## Why the distinctions matter

```text
Proposal != Resolution != Permit != Receipt
Intent != external effect
Observation != Evidence != Verification != Outcome
```

These separations prevent a model suggestion, an expired authorization, a command exit code or an unverified report from silently becoming authoritative state.

## Machine sources

- Seed model: [`../../seed/canonical/source/seed-model.json`](../../seed/canonical/source/seed-model.json)
- Conformance cases: [`../../seed/canonical/conformance/`](../../seed/canonical/conformance/)
- Formal projection: [`../../seed/canonical/formal/`](../../seed/canonical/formal/)
- Component system model: [`../../aset/system/canonical/source/system-composition-model.json`](../../aset/system/canonical/source/system-composition-model.json)
- External implementation protocol: [`../../seed/canonical/conformance/implementation-conformance-protocol.json`](../../seed/canonical/conformance/implementation-conformance-protocol.json)

For executable behavior, use the conformance corpus rather than translating this walkthrough into an independent implementation contract.

# ASET Seed 0.1-rc12 — machine-readable normative canon

**Version:** `0.1-rc12`

**Status:** `RC12_RELEASE_CANDIDATE_READY`

**Canonical model SHA-256:** `sha256:4e633a5cfe17872d8edadd51780c01924647a5c80e6a693f1af5d768e36e5faa`

> This document is generated automatically from the machine canon. Manual editing is prohibited.

## Assurance boundaries

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Concepts

### trust space (`TrustSpace`)

The state of one Genesis lineage with an isolated normative history.

Identifier: `seed.trust_space`

### genesis (`Genesis`)

Immutable initial material anchoring a trust-space identity.

Identifier: `seed.genesis`

### trust constitution (`Constitution`)

The canonical policy of admissible authority, procedures, and transitions.

Identifier: `seed.constitution`

### context (`Context`)

A normative namespace with immutable ContextID and local state.

Identifier: `seed.context`

### context descriptor (`ContextDescriptor`)

A protocol record of context identity, parent, address, member, and lifecycle.

Identifier: `seed.context_descriptor`

### institutional authority (`Authority`)

An active institutional power in an exact context, scope, and state.

Identifier: `seed.authority`

### authority binding (`AuthorityBinding`)

A protocol record binding an authority holder, kind, scope, epoch, and provenance.

Identifier: `seed.authority_binding`

### decision (`Decision`)

A recorded normative choice or declaration of readiness.

Identifier: `seed.decision`

### permit (`Permit`)

A bounded authorization to submit the result of a specific action.

Identifier: `seed.permit`

### execution intent (`ExecutionIntent`)

A materialized use of a permit for a specific attempt.

Identifier: `seed.execution_intent`

### permit-use receipt (`PermitUseReceipt`)

Immutable evidence that a specific permit attempt was consumed.

Identifier: `seed.permit_use_receipt`

### observation (`Observation`)

A claim about an action result or external fact bound to evidence.

Identifier: `seed.observation`

### verification (`Verification`)

Recognition that a claim passed the prescribed verification procedure.

Identifier: `seed.verification`

### outcome (`Outcome`)

The final institutional recognition of an action result.

Identifier: `seed.outcome`

### state transition (`Transition`)

An atomic candidate change to the canonical state of one context.

Identifier: `seed.transition`

### transition record (`TransitionRecord`)

An immutable record of an accepted transition, its causes, and created artifacts.

Identifier: `seed.transition_record`

### export receipt (`ExportReceipt`)

A source-local commitment transferable to another context as evidence.

Identifier: `seed.export_receipt`

### import record (`ImportRecord`)

A local record accepting foreign evidence without importing its outcome automatically.

Identifier: `seed.import_record`

### local commit (`LocalCommit`)

A pre-classified transition admissible during a network partition.

Identifier: `seed.local_commit`

### reconciliation receipt (`ReconciliationReceipt`)

A record of local-commit validation, confirmed prefix, and detected forks.

Identifier: `seed.reconciliation_receipt`

### dependency edge (`DependencyEdge`)

A typed directed relation of normative or non-normative dependency between contexts.

Identifier: `seed.dependency_edge`

### membership-withdrawal record (`MembershipWithdrawalRecord`)

An immutable record of voluntary exit or context replacement.

Identifier: `seed.membership_withdrawal_record`

### context-redefinition record (`ContextRedefinitionRecord`)

A complete record of the atomic replacement of an exact set of interdependent contexts.

Identifier: `seed.context_redefinition_record`

### correction record (`CorrectionRecord`)

An append-only record withdrawing or replacing a verification before final outcome.

Identifier: `seed.correction_record`

### state root (`StateRoot`)

A domain-separated hash of the complete canonical trust-space state.

Identifier: `seed.state_root`

### authentication proof (`Proof`)

Externally verifiable evidence bound to a principal and exact transition.

Identifier: `seed.proof`

### durable runtime store (`RuntimeStore`)

A transactional store for state and the append-only transition-attempt audit log.

Identifier: `seed.runtime_store`

## Requirements

### `ASET-SEED-REQ-001`

The public API MUST enforce strict schemas and fail closed.

Canonical modality: `MUST`

Predicate: `enforce_strict_schemas_fail_closed`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-002`

TrustSpaceID and ContextID MUST be derived from canonical Genesis material.

Canonical modality: `MUST`

Predicate: `derive_identity_from_genesis`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-003`

Every accepted transition MUST be atomic and followed by whole-state validation.

Canonical modality: `MUST`

Predicate: `commit_atomically_and_validate_state`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-004`

Active authority scopes for one context/capability MUST NOT overlap.

Canonical modality: `MUST_NOT`

Predicate: `prevent_active_scope_overlap`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-005`

Permit terms MUST bind readiness and the permit-issue decision.

Canonical modality: `MUST`

Predicate: `bind_permit_terms`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-006`

A permit success predicate MUST resolve to an active constitution rule.

Canonical modality: `MUST`

Predicate: `resolve_success_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-007`

The verification policy MUST equal the permit success predicate.

Canonical modality: `MUST`

Predicate: `match_verification_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-008`

An outcome MUST aggregate the complete effective set of PASS verifications.

Canonical modality: `MUST`

Predicate: `aggregate_complete_effective_verifications`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-009`

A correction MUST target only a verification that has not been finalized by an outcome.

Canonical modality: `MUST`

Predicate: `limit_correction_to_nonfinal_verification`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-010`

Causal parents MUST be derived from typed artifact references.

Canonical modality: `MUST`

Predicate: `derive_causal_parents`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-011`

Ordinary transitions MUST NOT be accepted in a suspended context.

Canonical modality: `MUST_NOT`

Predicate: `block_ordinary_transition_in_suspended_context`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-012`

Reconciliation MUST include all known local commits and preserve fork evidence.

Canonical modality: `MUST`

Predicate: `reconcile_complete_known_commits`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-013`

Both endpoints of a normative dependency MUST be active contexts.

Canonical modality: `MUST`

Predicate: `require_active_normative_endpoints`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-014`

Standalone withdrawal MUST be member-signed and MUST NOT leave an active normative dependant.

Canonical modality: `MUST`

Predicate: `protect_normative_dependants_on_withdrawal`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-015`

AffectedSiblingSet MUST be computed transitively from the pre-state.

Canonical modality: `MUST`

Predicate: `compute_affected_sibling_closure`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-016`

The proposal digest MUST bind the complete embedded proposal.

Canonical modality: `MUST`

Predicate: `bind_full_redefinition_proposal`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-017`

Every affected member MUST authorize the exact proposal.

Canonical modality: `MUST`

Predicate: `require_all_member_authorizations`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-018`

The parent MUST hold REDEFINE_CONTEXT authority.

Canonical modality: `MUST`

Predicate: `require_parent_redefinition_authority`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-019`

Redefinition MUST commit atomically or leave state unchanged.

Canonical modality: `MUST`

Predicate: `commit_redefinition_atomically`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-020`

Successors MUST preserve parent, alias, member, and kind while receiving a new ContextID.

Canonical modality: `MUST`

Predicate: `preserve_successor_identity_fields`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-021`

Dependencies among affected siblings MUST be remapped to successors.

Canonical modality: `MUST`

Predicate: `remap_affected_dependencies`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-022`

Governance records MUST retain the complete proposal and proof digests.

Canonical modality: `MUST`

Predicate: `retain_governance_evidence`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-023`

Authority transfer MUST use a same-context positive action trail and new-holder readiness.

Canonical modality: `MUST`

Predicate: `bind_same_context_authority_transfer`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-024`

Reference-core branch coverage MUST be at least 90 percent for release freeze.

Canonical modality: `MUST`

Predicate: `meet_branch_coverage_threshold`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-025`

Coverage and publication-QA evidence MUST be bound to exact source and document bytes.

Canonical modality: `MUST`

Predicate: `bind_assurance_to_exact_bytes`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-REQ-026`

Release freeze MUST include clean-room validation of the deterministic archive.

Canonical modality: `MUST`

Predicate: `perform_clean_room_release_validation`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-COMPONENT-BLACKBOX`

### `ASET-SEED-DOC-001`

Official language editions MUST be derived deterministically from the machine-readable canon.

Canonical modality: `MUST`

Predicate: `derive_editions_from_canon`

`verification`: `ASET-VERIFY-GENERATED-EDITION-PARITY`, `ASET-VERIFY-SEMANTIC-ID-PARITY`

### `ASET-SEED-DOC-002`

All representations MUST preserve stable semantic identifiers for requirements, invariants, and transitions.

Canonical modality: `MUST`

Predicate: `preserve_semantic_identifiers`

`verification`: `ASET-VERIFY-GENERATED-EDITION-PARITY`, `ASET-VERIFY-SEMANTIC-ID-PARITY`

## Invariants

- `SEED-INV-001` — TrustSpaceID, Root Genesis, and constitution epoch zero are immutable.
- `SEED-INV-002` — Exactly one root context has no parent, and the context tree is acyclic.
- `SEED-INV-003` — Every ContextID is derived from its parent identifier and context-Genesis digest.
- `SEED-INV-004` — The live-alias index exactly matches active contexts.
- `SEED-INV-005` — All active contexts use the current constitution epoch.
- `SEED-INV-006` — One authority key has at most one active holder, and active scopes of one capability do not overlap.
- `SEED-INV-007` — A withdrawn, superseded, or terminated context has no active authority or permits.
- `SEED-INV-008` — Every artifact-map key equals the internal artifact identifier and refers to an existing context.
- `SEED-INV-009` — Permit terms are bound exactly to the issue decision, readiness, and recognized success policy.
- `SEED-INV-010` — Verification policy equals the permit success predicate and an active constitution rule.
- `SEED-INV-011` — Permit attenuation is linear and creates no duplicated attempt budget.
- `SEED-INV-012` — Attempt indices are contiguous, receipts are durable, and the submission-id index is exact.
- `SEED-INV-013` — Every observation is bound to the exact receipt, permit, and context.
- `SEED-INV-014` — Every verification is bound to the exact observation, receipt, permit, and context.
- `SEED-INV-015` — An outcome uses the complete effective verification set of its permit.
- `SEED-INV-016` — Export, import, and local recognition preserve exact cross-context provenance.
- `SEED-INV-017` — A correction targets only a verification before final outcome.
- `SEED-INV-018` — Transition counts, local ordinals, artifact ownership, and derived causal parents are exact.
- `SEED-INV-019` — A suspended context permits local continuation only through the dedicated partition transition.
- `SEED-INV-020` — Reconciliation includes all known local commits and preserves competing-branch evidence.
- `SEED-INV-021` — Dependency edges are unique, non-self-referential, and have existing endpoints.
- `SEED-INV-022` — Both endpoints of every normative edge are active contexts.
- `SEED-INV-023` — Standalone withdrawal leaves no active normative dependant.
- `SEED-INV-024` — AffectedSiblingSet is the exact transitive closure of direct siblings.
- `SEED-INV-025` — Redefinition uses the canonical digest of the complete proposal and the exact member-authorization set.
- `SEED-INV-026` — Context replacement is atomic, preserves identity fields, and remaps dependencies exactly.
- `SEED-INV-027` — Governance records contain the complete proposal and authentication evidence.
- `SEED-INV-028` — Authority transfer has a complete action trail in the same context.
- `SEED-INV-029` — Context-internal roots and the global state root exactly match canonical state.

## Transitions

### `SEED-TX-001` — `MEMBER_CONTEXT_GENESIS`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-member-context-genesis.schema.json`
- `authorization_rule`: bootstrap predicate or CREATE_MEMBER_CONTEXT
- `created_artifacts`: `ContextDescriptor`, `AuthorityBinding`

### `SEED-TX-002` — `DECISION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-decision.schema.json`
- `authorization_rule`: self-signed readiness or capability selected by decision kind
- `created_artifacts`: `Decision`

### `SEED-TX-003` — `PERMIT_ISSUE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-issue.schema.json`
- `authorization_rule`: ISSUE_PERMIT
- `created_artifacts`: `Permit`

### `SEED-TX-004` — `PERMIT_ATTENUATE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-attenuate.schema.json`
- `authorization_rule`: active parent permit and new-delegate readiness
- `created_artifacts`: `Permit`

### `SEED-TX-005` — `PERMIT_USE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-permit-use.schema.json`
- `authorization_rule`: permit delegate and available attempt
- `created_artifacts`: `ExecutionIntent`, `PermitUseReceipt`

### `SEED-TX-006` — `OBSERVATION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-observation.schema.json`
- `authorization_rule`: presenter bound to permit-use receipt
- `created_artifacts`: `Observation`

### `SEED-TX-007` — `VERIFICATION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-verification.schema.json`
- `authorization_rule`: VERIFY
- `created_artifacts`: `Verification`

### `SEED-TX-008` — `OUTCOME`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-outcome.schema.json`
- `authorization_rule`: CONFIRM_OUTCOME
- `created_artifacts`: `Outcome`

### `SEED-TX-009` — `EXPORT`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-export.schema.json`
- `authorization_rule`: EXPORT
- `created_artifacts`: `ExportReceipt`

### `SEED-TX-010` — `IMPORT`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-import.schema.json`
- `authorization_rule`: IMPORT and local permit-use receipt
- `created_artifacts`: `ImportRecord`, `Observation`

### `SEED-TX-011` — `GUARANTEE_SUSPEND`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-guarantee-suspend.schema.json`
- `authorization_rule`: SUSPEND_GUARANTEE in parent context
- `created_artifacts`: `context guarantee status`

### `SEED-TX-012` — `PARTITION_LOCAL_TRANSITION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-partition-local-transition.schema.json`
- `authorization_rule`: constitution-classified local operation and accepted proof
- `created_artifacts`: `LocalCommit`

### `SEED-TX-013` — `RECONCILE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-reconcile.schema.json`
- `authorization_rule`: RECONCILE
- `created_artifacts`: `ReconciliationReceipt`

### `SEED-TX-014` — `MEMBERSHIP_WITHDRAW`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-membership-withdraw.schema.json`
- `authorization_rule`: member signature and no active normative dependant
- `created_artifacts`: `MembershipWithdrawalRecord`

### `SEED-TX-015` — `CONTEXT_REDEFINE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-context-redefine.schema.json`
- `authorization_rule`: parent REDEFINE_CONTEXT plus exact member authorizations
- `created_artifacts`: `ContextDescriptor`, `AuthorityBinding`, `MembershipWithdrawalRecord`, `ContextRedefinitionRecord`

### `SEED-TX-016` — `CONTEXT_TERMINATE`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-context-terminate.schema.json`
- `authorization_rule`: TERMINATE_CONTEXT plus PASS TRUST_LINEAGE_LOST verification
- `created_artifacts`: `context lifecycle changes`

### `SEED-TX-017` — `CORRECTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-correction.schema.json`
- `authorization_rule`: VERIFY
- `created_artifacts`: `CorrectionRecord`

### `SEED-TX-018` — `AUTHORITY_TRANSFER`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-authority-transfer.schema.json`
- `authorization_rule`: TRANSFER_AUTHORITY plus same-context positive action trail
- `created_artifacts`: `AuthorityBinding`

## Implementation boundary

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `programming language`, `storage backend`, `deployment topology`, `consensus protocol`, `network transport`, `cryptographic provider`, `operational user interface`

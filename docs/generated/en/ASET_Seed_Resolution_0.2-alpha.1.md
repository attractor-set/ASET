# ASET Seed 0.2 alpha — Resolution Core

**Version:** `0.2.0-alpha.1`

**Status:** `RESOLUTION_CORE_ALPHA`

**Canonical model SHA-256:** `sha256:af855b45f052ebfef144de856d71230f5b2b9a65d48fe58c24be778ace51d633`

> This edition is derived from the machine canon.

## Assurance

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Concepts

### resolution cycle (`ResolutionCycle`)

One immutably bound cycle for resolving an exact normative question.

Identifier: `seed.resolution_cycle`

### context binding (`ContextBinding`)

The exact context, state-root and policy-epoch binding within which a question is resolved.

Identifier: `seed.context_binding`

### resolution question (`ResolutionQuestion`)

A canonically digested question and its bounded resolution scope.

Identifier: `seed.resolution_question`

### resolution status (`ResolutionStatus`)

The normative status UNKNOWN, ACCEPT or DENY within one cycle.

Identifier: `seed.resolution_status`

### enforcement disposition (`EnforcementDisposition`)

The operational consequence of a decision: BLOCKED for UNKNOWN and DENY, ALLOW only for ACCEPT.

Identifier: `seed.enforcement_disposition`

### resolution authority (`ResolutionAuthority`)

An explicitly empowered subject able to narrow UNKNOWN in an exact scope and epoch.

Identifier: `seed.resolution_authority`

### escalation grant (`EscalationGrant`)

An explicit authorization to pass an unresolved question to the next Resolution Authority without automatic authority inheritance.

Identifier: `seed.escalation_grant`

### evidence reference (`EvidenceReference`)

A content-addressed reference to material used when narrowing UNKNOWN.

Identifier: `seed.evidence_reference`

### resolution record (`ResolutionRecord`)

An immutable record of opening, escalation or terminal resolution and its provenance.

Identifier: `seed.resolution_record`

### resolution chain (`ResolutionChain`)

An acyclic sequence of explicitly authorized Resolution Authorities for one question.

Identifier: `seed.resolution_chain`

## Requirements

### `ASET-SEED-REQ-001`

A new resolution cycle MUST open as UNKNOWN with BLOCKED enforcement.

Modality: `MUST`

Predicate: `open_as_unknown_blocked`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-002`

A cycle status MUST be one of UNKNOWN, ACCEPT, DENY; only ACCEPT and DENY are terminal.

Modality: `MUST`

Predicate: `use_three_status_lattice`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-003`

UNKNOWN MUST NOT authorize an external effect and MUST NOT be silently coerced to DENY.

Modality: `MUST_NOT`

Predicate: `authorize_from_unknown`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-004`

BLOCKED MUST correspond to UNKNOWN and DENY; ALLOW MAY correspond only to ACCEPT.

Modality: `MUST`

Predicate: `bind_enforcement_to_status`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-005`

Every cycle MUST bind exact context_id, state_root, question_digest, policy_epoch and scope values.

Modality: `MUST`

Predicate: `bind_exact_question_state_policy`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-006`

Narrowing UNKNOWN MUST be performed by an active Resolution Authority in the exact scope and epoch.

Modality: `MUST`

Predicate: `require_exact_resolution_authority`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-007`

A resolution or escalation MUST NOT expand the original question scope.

Modality: `MUST_NOT`

Predicate: `expand_resolution_scope`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-008`

Passing UNKNOWN to the next authority MUST have an explicit EscalationGrant; context ancestry or federation membership alone creates no authority.

Modality: `MUST`

Predicate: `require_explicit_escalation_grant`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-009`

Escalation MUST preserve resolution_id, context_id, state_root, question_digest and policy_epoch.

Modality: `MUST`

Predicate: `preserve_question_during_escalation`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-010`

The Resolution Authority chain MUST remain acyclic.

Modality: `MUST`

Predicate: `keep_resolution_chain_acyclic`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-011`

Within one cycle, ACCEPT or DENY MUST NOT change to another status; an exact replay MAY be idempotent.

Modality: `MUST_NOT`

Predicate: `mutate_terminal_status`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-012`

Reconsidering a terminal decision MUST create a new resolution_id and cycle linked to the prior record.

Modality: `MUST`

Predicate: `use_new_cycle_for_reconsideration`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-013`

Opening, escalation and terminal resolution MUST append an immutable ResolutionRecord with Authority and provenance.

Modality: `MUST`

Predicate: `append_resolution_records`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-BOUNDED-MODEL`

### `ASET-SEED-REQ-014`

Implementations MUST be checked by observable semantics and have no normative precedence over one another.

Modality: `MUST`

Predicate: `preserve_implementation_neutrality`

`verification`: `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-SPECIFICATION-TESTS`, `ASET-VERIFY-EXTERNAL-CONFORMANCE`

## Invariants

- `SEED-INV-001` — Every valid status is UNKNOWN, ACCEPT or DENY.
- `SEED-INV-002` — UNKNOWN is always paired with BLOCKED.
- `SEED-INV-003` — DENY is always paired with BLOCKED.
- `SEED-INV-004` — ALLOW is possible only with ACCEPT.
- `SEED-INV-005` — A terminal decision is immutable within one resolution_id.
- `SEED-INV-006` — Resolution Authority must match the context, scope and policy epoch.
- `SEED-INV-007` — Escalation is possible only from UNKNOWN through an explicit EscalationGrant.
- `SEED-INV-008` — Escalation preserves question identity and does not expand scope.
- `SEED-INV-009` — The Resolution Authority chain contains no repeated authority.
- `SEED-INV-010` — ResolutionRecord entries are appended monotonically and are never rewritten.
- `SEED-INV-011` — A rejected command preserves state and state root.
- `SEED-INV-012` — A new reconsideration of a terminal decision uses a new resolution_id.

## Transitions

### `SEED-TX-001` — `OPEN_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-open-resolution.schema.json`
- `authority_rule`: The opening authority must be explicit and exactly bound to context, scope and policy epoch.
- `scope_rule`: The opened scope becomes the maximum scope of this cycle.
- `created_artifacts`: `ResolutionCycle`, `ResolutionRecord`

### `SEED-TX-002` — `RESOLVE_ACCEPT`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-resolve.schema.json`
- `authority_rule`: The current Resolution Authority must match exact binding and scope.
- `scope_rule`: Decision scope must be equal to or narrower than the opened scope.
- `created_artifacts`: `ResolutionRecord`

### `SEED-TX-003` — `RESOLVE_DENY`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-resolve.schema.json`
- `authority_rule`: The current Resolution Authority must match exact binding and scope.
- `scope_rule`: Decision scope must be equal to or narrower than the opened scope.
- `created_artifacts`: `ResolutionRecord`

### `SEED-TX-004` — `ESCALATE_UNKNOWN`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-escalate-unknown.schema.json`
- `authority_rule`: An exact EscalationGrant must authorize the current and next Resolution Authorities.
- `scope_rule`: Escalated scope must not expand and exact question binding must remain unchanged.
- `created_artifacts`: `ResolutionRecord`

## Implementation boundary

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `storage engine`, `durability level`, `concurrency control`, `network topology`, `consensus protocol`, `cryptographic provider`, `key custody`, `execution engine`, `planning`, `memory`, `federation topology`, `artifact retention`

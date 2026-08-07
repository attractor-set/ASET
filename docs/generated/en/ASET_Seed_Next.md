# ASET Seed Minimal Resolution Kernel 0.3 alpha 1

**Version:** `0.3.0-alpha.1`

**Status:** `MINIMAL_STRONG_CORE_ALPHA`

**Canonical model SHA-256:** `sha256:54c46e46d4e6b5870353bb0ed229310f60583e9acd11798b655bdd837c8dba74`

> This edition is derived from the machine canon.

## Assurance

- `implementation_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `external_third_party_audit`: `PENDING`

## Concepts

### resolution binding (`ResolutionBinding`)

The exact context, state root, question, policy epoch and scope to which one resolution applies.

Identifier: `seed.resolution_binding`

### resolution request (`ResolutionRequest`)

A fresh identifier bound to one exact resolution binding and an initial locally recognized Authority.

Identifier: `seed.resolution_request`

### resolution (`Resolution`)

The derived value UNKNOWN, or the terminal value ALLOW or BLOCK.

Identifier: `seed.resolution_value`

### local Authority (`LocalAuthority`)

An Authority explicitly recognized by one Context for one exact binding and policy epoch.

Identifier: `seed.local_authority`

### Authority recognition (`AuthorityRecognition`)

A local exact-binding recognition result stating that one Authority is authorized for one ResolutionBinding; concrete grant chains, signatures and proof construction are external to Seed.

Identifier: `seed.authority_recognition`

### evidence reference (`EvidenceReference`)

An opaque content-addressed reference to non-authoritative evidence or proof material. It has no normative effect until a Seed admission boundary recognizes the fact it supports.

Identifier: `seed.evidence_reference`

### resolution record (`ResolutionRecord`)

One immutable content-addressed terminal ALLOW or BLOCK record with exact binding, a recognized Authority, and optional opaque evidence references.

Identifier: `seed.resolution_record`

### reconsideration commitment (`ReconsiderationCommitment`)

An immutable content-addressed commitment from a fresh request to a previously recognized terminal ResolutionRecord; the predecessor request or record need not remain physically retained by the implementation. Recognition may be established by current retained material or by externally validated authenticated-set/accumulator proof material.

Identifier: `seed.reconsideration_commitment`

## Requirements

### `ASET-SEED-REQ-001`

ResolutionBinding MUST contain exact context_id, state_root, question_digest, policy_epoch and scope values and a canonical binding digest.

Modality: `MUST`

Predicate: `binding_exact`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-002`

Every ResolutionRequest MUST use a fresh resolution_id and bind one exact ResolutionBinding.

Modality: `MUST`

Predicate: `request_fresh`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-003`

The derived Resolution MUST be UNKNOWN, ALLOW or BLOCK; only ALLOW and BLOCK are stored terminal values.

Modality: `MUST`

Predicate: `resolution_domain`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-004`

An exact bound effect MUST be permitted if and only if the unique valid terminal ResolutionRecord is ALLOW.

Modality: `MUST`

Predicate: `allow_only`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-005`

UNKNOWN and BLOCK MUST prohibit the effect. Missing or ambiguous valid terminal state, or failure to establish a valid terminal record, MUST resolve to UNKNOWN. Invalid or non-authoritative material MUST NOT override an otherwise unique valid terminal record.

Modality: `MUST`

Predicate: `fail_closed`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-006`

A terminal record MUST be rooted in an Authority explicitly recognized by the local Context for the exact binding and policy epoch.

Modality: `MUST`

Predicate: `local_authority`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-007`

Authority evidence or delegation material MUST NOT create or expand Authority by itself; a terminal record Authority MUST be explicitly recognized for the exact binding before the record can become valid.

Modality: `MUST`

Predicate: `authority_recognition_boundary`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-008`

Evidence, verification results, AI outputs, consensus results, remote outcomes and other external statements MUST NOT by themselves mutate Seed-owned canonical state or create ALLOW or local Authority.

Modality: `MUST`

Predicate: `inputs_non_authoritative`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-009`

At most one valid terminal record MAY exist for one resolution_id; conflicting terminal records MUST fail closed as UNKNOWN.

Modality: `MAY`

Predicate: `terminal_unique`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-010`

A terminal ResolutionRecord MUST be immutable and content-addressed; exact replay MAY be idempotent but replacement is forbidden.

Modality: `MAY`

Predicate: `record_immutable`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-011`

Reconsideration MUST create a fresh resolution_id and carry an immutable content-addressed commitment to a previously recognized terminal ResolutionRecord; the predecessor request or record need not remain physically retained.

Modality: `MUST`

Predicate: `reconsider_fresh`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-012`

Implementations and extensions MUST be checked by observable semantics and MUST have no normative precedence.

Modality: `MUST`

Predicate: `implementation_neutral`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

## Invariants

- `SEED-INV-001` — Every valid derived resolution is UNKNOWN, ALLOW or BLOCK.
- `SEED-INV-002` — Effect permission is true if and only if the unique valid terminal record is ALLOW.
- `SEED-INV-003` — UNKNOWN and BLOCK never permit an effect.
- `SEED-INV-004` — Every request and terminal record preserves one exact binding digest.
- `SEED-INV-005` — Every valid terminal record uses an Authority explicitly recognized for the exact local binding.
- `SEED-INV-006` — Authority evidence is non-authoritative until exact-binding Authority recognition succeeds; opaque proof material cannot create or expand Authority by itself.
- `SEED-INV-007` — External statements and evidence are outside Seed-owned canonical state unless accepted by a recognized Seed transition.
- `SEED-INV-008` — At most one valid terminal record exists for one resolution_id.
- `SEED-INV-009` — Conflicting valid terminal records yield UNKNOWN. Invalid or non-authoritative material cannot create ALLOW, create a conflict, or override an otherwise unique valid terminal record.
- `SEED-INV-010` — Resolution records are append-only, immutable and content-addressed.
- `SEED-INV-011` — Only recognized Seed state transitions may change Seed-owned canonical state; environment observations and observer operations do not mutate that state.
- `SEED-INV-012` — Reconsideration uses a fresh resolution_id linked by an immutable content-addressed commitment to a previously recognized terminal ResolutionRecord; predecessor object retention is not required.

## Transitions

### `SEED-TX-001` — `REGISTER_REQUEST`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-register-request.schema.json`
- `authority_rule`: The initial Authority binding must be locally rooted and exactly match the request binding.
- `binding_rule`: The request contains one canonical exact binding and a fresh resolution_id. For reconsideration, previous_terminal_record_digest must be a recognized immutable terminal-record commitment; predecessor object presence in retained storage is not required.
- `created_artifacts`: `ResolutionRequest`

### `SEED-TX-002` — `SUBMIT_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-submit-resolution.schema.json`
- `authority_rule`: The record Authority must be explicitly recognized for the exact request binding. Concrete signatures, delegation chains and proof construction are external validation mechanisms.
- `binding_rule`: The record request_digest and binding_digest must exactly match the registered request.
- `created_artifacts`: `ResolutionRecord`

### `SEED-TX-003` — `EVALUATE_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/operation.schema.json`
- `authority_rule`: Evaluation creates no Authority and accepts no external statement as a resolution.
- `binding_rule`: Evaluation observes one resolution_id without mutating Seed-owned state. It derives UNKNOWN when no unique valid terminal record is established; invalid or non-authoritative material cannot override a unique valid record.
- `created_artifacts`: `ResolutionEvaluation`

## Implementation boundary

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `policy evaluation language`, `evidence acquisition`, `orchestration semantics`, `enforcement mechanism`, `storage engine`, `durability level`, `concurrency control`, `network topology`, `consensus protocol`, `cryptographic provider`, `concrete Authority grant-chain construction and validation`, `key custody`, `federation topology`, `AI model`, `artifact retention`, `retention, pruning, archiving and compaction of superseded request/record material`, `terminal-commitment accumulator construction`, `accumulator membership/update witness retention`

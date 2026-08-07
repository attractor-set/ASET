# ASET Seed Minimal Resolution Kernel 0.3 alpha 1

**Version:** `0.3.0-alpha.1`

**Status:** `MINIMAL_STRONG_CORE_ALPHA`

**Canonical model SHA-256:** `sha256:5bbdfefe35a0adf83fd5e5dd86475a4f57ae92d4f9b9c06a7d530faf2e484396`

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

### Authority proof (`AuthorityProof`)

A locally rooted, exact-binding, acyclic and non-expanding chain of explicit Authority grants.

Identifier: `seed.authority_proof`

### evidence reference (`EvidenceReference`)

A content-addressed non-authoritative input cited as the basis of a terminal record.

Identifier: `seed.evidence_reference`

### resolution record (`ResolutionRecord`)

One immutable content-addressed terminal ALLOW or BLOCK record with exact binding and Authority proof.

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

UNKNOWN and BLOCK MUST prohibit the effect; absence, invalidity, ambiguity or verification error MUST resolve to UNKNOWN rather than ALLOW.

Modality: `MUST`

Predicate: `fail_closed`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-006`

A terminal record MUST be rooted in an Authority explicitly recognized by the local Context for the exact binding and policy epoch.

Modality: `MUST`

Predicate: `local_authority`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-007`

Every delegated Authority proof MUST be explicit, acyclic, exact-binding and non-expanding.

Modality: `MUST`

Predicate: `proof_attenuating`

`verification`: `ASET-VERIFY-DECLARATIVE-STATE-VALIDATION`, `ASET-VERIFY-PORTABLE-CASES`, `ASET-VERIFY-BOUNDED-MODEL`, `ASET-VERIFY-INVARIANT-COVERAGE`, `ASET-VERIFY-SEMANTIC-MUTATIONS`

### `ASET-SEED-REQ-008`

Evidence, verification results, AI outputs, consensus results and remote outcomes MUST NOT by themselves create ALLOW or local Authority.

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
- `SEED-INV-005` — Every valid terminal record is rooted in a local Authority binding.
- `SEED-INV-006` — Every delegated Authority proof is exact-binding, acyclic and non-expanding.
- `SEED-INV-007` — Evidence and external statements are non-authoritative inputs.
- `SEED-INV-008` — At most one valid terminal record exists for one resolution_id.
- `SEED-INV-009` — Conflicting or invalid terminal material yields UNKNOWN and never ALLOW.
- `SEED-INV-010` — Resolution records are append-only, immutable and content-addressed.
- `SEED-INV-011` — Only recognized Seed transitions may change the canonical store; an invalid or unrecognized candidate is not a Seed transition.
- `SEED-INV-012` — Reconsideration uses a fresh resolution_id linked by an immutable content-addressed commitment to a previously recognized terminal ResolutionRecord; predecessor object retention is not required.

## Transitions

### `SEED-TX-001` — `REGISTER_REQUEST`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-register-request.schema.json`
- `authority_rule`: The initial Authority binding must be locally rooted and exactly match the request binding.
- `binding_rule`: The request contains one canonical exact binding and a fresh resolution_id. For reconsideration, previous_terminal_record_digest must be a recognized immutable terminal-record commitment; predecessor object presence in retained storage is not required.
- `created_artifacts`: `ResolutionRequest`

### `SEED-TX-002` — `SUBMIT_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/payload-submit-resolution.schema.json`
- `authority_rule`: The record Authority must be the local root Authority or be justified by a valid exact-binding Authority proof.
- `binding_rule`: The record request_digest and binding_digest must exactly match the registered request.
- `created_artifacts`: `ResolutionRecord`

### `SEED-TX-003` — `EVALUATE_RESOLUTION`

- `payload_schema`: `seed/canonical/protocol/schemas/operation.schema.json`
- `authority_rule`: Evaluation creates no Authority and accepts no external statement as a resolution.
- `binding_rule`: Evaluation is performed for one registered resolution_id and fails closed on missing, invalid or conflicting terminal material.
- `created_artifacts`: `ResolutionEvaluation`

## Implementation boundary

- `normative_status`: `IMPLEMENTATION_NEUTRAL`
- `implementation_precedence`: `NONE`
- `conformance_protocol_ref`: `seed/canonical/conformance/implementation-conformance-protocol.json`
- `unspecified_by_seed`: `policy evaluation language`, `evidence acquisition`, `orchestration semantics`, `enforcement mechanism`, `storage engine`, `durability level`, `concurrency control`, `network topology`, `consensus protocol`, `cryptographic provider`, `key custody`, `federation topology`, `AI model`, `artifact retention`, `retention, pruning, archiving and compaction of superseded request/record material`, `terminal-commitment accumulator construction`, `accumulator membership/update witness retention`

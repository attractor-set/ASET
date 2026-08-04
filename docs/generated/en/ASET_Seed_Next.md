# ASET Seed — machine-readable normative canon

**Version:** `0.1-rc12-development`

**Status:** `BOOTSTRAP_SCAFFOLD_NOT_RELEASED`

**Canonical model SHA-256:** `sha256:1ebe6babe03edce9595a921e059e3e65bd55112c22ae79dd60e4fdd4a9335c5d`

> This document is generated automatically. Manual editing is prohibited.

## Status

`BOOTSTRAP_SCAFFOLD_NOT_RELEASED`

## Concepts

### context (`Context`)

A normative namespace with immutable identity and a resolvable address.

Identifier: `seed.context`

### institutional authority (`Authority`)

An active institutional power in an exact context and state.

Identifier: `seed.authority`

### decision (`Decision`)

A recorded normative choice or declaration of readiness.

Identifier: `seed.decision`

### permit (`Permit`)

A bounded authorization to submit the result of a specific action.

Identifier: `seed.permit`

### execution intent (`ExecutionIntent`)

A materialized use of a permit for a specific attempt.

Identifier: `seed.execution_intent`

### observation (`Observation`)

A claim about the result of an action or an external fact.

Identifier: `seed.observation`

### verification (`Verification`)

Recognition that a claim passed the prescribed verification procedure.

Identifier: `seed.verification`

### outcome (`Outcome`)

The final institutional recognition of an action result.

Identifier: `seed.outcome`

## Requirements

### `SEED-REQ-001`

Each transition MUST belong to exactly one context.

Canonical modality: `MUST`

Predicate: `belong_to_exactly_one_context`

### `SEED-REQ-002`

A verification MUST use a rule recognized by the active trust-space constitution.

Canonical modality: `MUST`

Predicate: `use_recognized_policy`

### `SEED-REQ-003`

An outcome MUST NOT be accepted without a valid trail from decision through verification.

Canonical modality: `MUST_NOT`

Predicate: `exist_without_valid_trail`

### `SEED-REQ-004`

A cross-context authority transfer MUST NOT be accepted without local re-recognition.

Canonical modality: `MUST_NOT`

Predicate: `cross_context_without_local_recognition`

### `SEED-DOC-REQ-001`

Each official language edition MUST be deterministically derived from the machine-readable canon.

Canonical modality: `MUST`

Predicate: `derive_from_machine_readable_canon`

### `SEED-DOC-REQ-002`

Unnecessary foreign terminology MUST NOT be used when an exact and established native term exists; protocol identifiers are exempt.

Canonical modality: `MUST_NOT`

Predicate: `use_unnecessary_foreign_term`

## Invariants

- `SEED-INV-001` — Every accepted transition belongs to exactly one context.
- `SEED-INV-002` — One authority key has at most one active holder.
- `SEED-INV-003` — A permit attempt is never consumed more than once.
- `SEED-INV-004` — Historical ancestry is not active membership.
- `SEED-INV-005` — No outcome exists without an effective verification set.

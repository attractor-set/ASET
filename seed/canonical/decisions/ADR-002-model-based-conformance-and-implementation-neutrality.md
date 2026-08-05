# ADR-002 — Model-based conformance and implementation neutrality

Status: **ACCEPTED**

## Decision

The ASET machine canon is the normative source of ASET semantics. Concrete implementations are non-normative conformance subjects. No implementation, programming language, storage engine, runner or deployment profile has semantic precedence.

Implementation conformance is evaluated as black-box observational equivalence against the canon-bound mathematical transition model, invariant set, protocol schemas and conformance corpus. The implementation adapter returns observations; an external runner determines the verdict.

Storage, durability, concurrency, recovery, consensus, networking and cryptographic-provider guarantees belong to separately identified implementation profiles. Such profiles may strengthen operational guarantees but may not weaken, merge or bypass Seed distinctions and invariants.

## Consequences

- The ASET specification repository contains no required runtime.
- The Python and SQLite stack is maintained separately as a non-normative educational profile.
- CI may consume the canon package directly from a pinned repository revision and digest.
- Candidate-canon self-consistency and compatibility with an approved canon are separate checks.
- Frozen historical releases and evidence remain immutable.

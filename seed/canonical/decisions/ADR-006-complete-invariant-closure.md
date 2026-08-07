# ADR-006 — Complete invariant closure for the minimal Seed kernel

## Status

Accepted for `0.3.0-alpha.1`.

## Context

The minimal Seed kernel reduced the normative surface to exact bindings, local
Authority, immutable terminal records, fail-closed evaluation and fresh
reconsideration. The reduction made complete machine traceability practical,
but the first formal projection mapped the twelve canonical invariants to only
six bounded properties and did not require negative semantic mutation evidence.

A foundational Seed must not contain a normative `MUST` or `MUST NOT` whose
failure cannot be detected by the release process.

## Decision

Seed publishes a normative invariant-coverage matrix that closes all of the
following sets exactly:

- twelve canonical requirements;
- twelve canonical safety invariants;
- three canonical transition kinds;
- the complete formal-property registry;
- the complete portable conformance corpus;
- the complete semantic-mutation catalogue.

Every requirement and invariant must reference at least one formal property,
one portable conformance case and one semantic mutation. Every transition must
have positive and negative conformance coverage. Orphan formal properties,
portable cases and mutations are release-blocking.

The TLA+ projection checks eleven state invariants and four temporal properties.
Exact digest identity, detailed Authority-grant validation, evaluator totality
and implementation neutrality are checked by the executable oracle and static
canon validators. This division does not give any implementation semantic
precedence.

## Consequences

The release gate now fails unless:

- requirement coverage is `12/12`;
- invariant coverage is `12/12`;
- transition coverage is `3/3`;
- all registered semantic mutations are killed;
- the bounded state explorer and TLC property catalogues match the registry;
- no normative assurance evidence is orphaned.

At the time of this decision, this closed the published bounded safety
contract. Subsequent assurance work added an unbounded TLAPS deductive safety
proof for the committed abstract TLA+ projection.

Subsequent assurance work also added a source-locked generated canonical TLA+
projection and a TLAPS theorem establishing behavioral equivalence between that
declared projection and `SeedResolution.tla`. The relation is explicitly
bounded by opaque Binding and Authority-proof abstractions. It does not prove
natural-language equivalence, concrete Binding/digest construction,
implementation refinement or correctness, concrete Authority grant-chain
construction, liveness, cryptographic primitive security or external
certification.

## Supersession note

ADR-009 supersedes the active property-count, state-boundary and Authority grant-chain wording in this historical assurance decision. The active formal property set and Authority boundary are defined by the current verification registry and formal model.

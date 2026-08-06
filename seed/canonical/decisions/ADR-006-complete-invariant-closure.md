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

This closes the published bounded safety contract. It does not claim unbounded
TLAPS proof, liveness, cryptographic security, correctness of every
implementation or external certification.

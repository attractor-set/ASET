# Cross-implementation conformance plan

## Purpose

Implementation neutrality is not established by repository separation alone. It is strengthened when independently developed implementations produce equivalent ASET observations under one pinned canon package and when the specification-owned runner determines the verdict.

The first comparison target is the non-normative Python + SQLite learning profile and an independently engineered Rust + PostgreSQL profile.

## Independence controls

The second implementation must not:

- import or execute the Python semantic core;
- translate Python control flow line by line as its primary design method;
- reuse implementation-owned expected-result code;
- determine its own conformance verdict;
- weaken or merge canonical distinctions to match local storage constraints.

It may consume only published canon artifacts, schemas, conformance cases and explanatory non-normative documentation.

## Required comparison lanes

1. **Exact canonical corpus.** Both adapters execute every case in the pinned conformance package.
2. **Deterministic replay.** Repeated execution of the same ordered cases produces identical observations and final state roots within each implementation.
3. **Differential valid sequences.** A specification-owned generator creates valid bounded transition sequences. Accepted/rejected status, normative result codes, state-change flags and canonical state roots must agree.
4. **Differential invalid sequences.** Mutations cover stale context, scope mismatch, replay, invalid ordering, malformed canonical documents and forbidden authority reuse. Both implementations must reject at the same normative boundary.
5. **Persistence-profile restart.** Each profile restarts from its own durable representation and returns the same canonical observable state as before restart.
6. **No shared-verdict path.** The external runner computes all verdicts from adapter observations and the pinned canon package.

## Comparison tuple

For every case or generated step, compare at least:

```text
case/step identity
accepted or rejected
normative result code
state_changed
canonical final-state root
created canonical artifact identifiers
causal bindings required by the protocol
```

Profile-local telemetry, database layout and operational error details are not compared unless a profile contract explicitly requires them.

## Release admission

A cross-implementation claim requires:

- two independently maintained implementation repositories;
- exact canon locks resolving to one package digest;
- complete corpus PASS for each implementation;
- zero unexplained differential observations;
- deterministic replay PASS;
- published machine-readable comparison report;
- explicit statement that agreement does not prove physical-world truth or production suitability.

Until these conditions are met, the repository may claim implementation-neutral design and external conformance protocol support, but not independent cross-implementation validation.

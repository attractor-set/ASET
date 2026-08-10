# Black-box audit method

The active black-box audit evaluates the exact repository snapshot from public
repository artifacts and deterministic commands. It does not treat historical
runtime evidence as controlling evidence for Seed 0.3.

## Active documentation boundary

`tools/blackbox_documentation_audit.py` checks the curated active documentation
surface, generated multilingual Seed editions, language navigation, the active
audit classification, implementation-neutrality claims, and prohibited legacy
runtime/readiness claims. Every file under `audit/` must be classified as
active, historical, or explicitly excluded by `ACTIVE_AUDIT_INDEX.json`.

The method document itself is part of the active documentation surface so that
the description of the gate cannot silently diverge from the gate.

## Canon and assurance boundary

The repository release gate independently requires:

- deterministic repository-view parity;
- machine-canon and canon-package validation;
- exhaustive finite-state saturation for the published finite fixture;
- semantic mutation closure;
- requirement/invariant/operation coverage;
- assurance and proof traceability;
- standalone canon-to-TLA projection parity;
- TLC model checking;
- TLAPS safety proofs;
- TLAPS canon-to-TLA behavioral-equivalence proof;
- specification tests, lint/sanity checks, exact Git source identity and deterministic
  repository-snapshot construction.

These checks establish consistency and the declared safety properties of the
exact candidate snapshot. They do not establish implementation production
readiness, cryptographic security, factual truth of external evidence, or
correctness of mechanisms intentionally outside the Seed boundary.

## Historical evidence

RC11/RC12 runtime, SQLite, HMAC, permit, outcome, membership and related audit
records are preserved as historical evidence. They are non-controlling for the
active Seed 0.3 minimal resolution-recognition semantics unless explicitly
listed as active by `ACTIVE_AUDIT_INDEX.json`.

## Failure rule

Any mandatory failing gate or unclassified active audit artifact is a blocking
finding for the candidate snapshot. A candidate may be treated as release-gate
closed only when the aggregate repository release gate passes for that exact
snapshot.

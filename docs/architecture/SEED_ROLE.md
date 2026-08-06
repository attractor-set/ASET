# ASET Seed as the semantic nucleus

## Status

This document explains the architectural role defined by the active machine canon at
`seed/canonical/source/seed-model.json`. If this explanation conflicts with the machine-readable
canon, the machine-readable canon prevails.

## Role

ASET Seed is the minimal, implementation-neutral resolution nucleus. It defines the exact
bindings, authority conditions, state lattice and invariants required to resolve a normative
question from `UNKNOWN` to `ACCEPT` or `DENY`, or to escalate it while it remains `UNKNOWN`.

Seed does not provide planning, memory, orchestration, execution, persistence, federation,
cryptographic providers or AI inference. Those capabilities may be supplied by independently
versioned extensions and implementations.

> Extensions may produce evidence and proposals; Seed determines when an exact normative
> question is locally resolved.

## Extension boundary

An extension may add domain concepts, stronger obligations, additional lifecycle states and
operational controls. It must not:

- weaken a Seed invariant;
- treat Context ancestry or federation membership as inherited authority;
- convert `UNKNOWN` to `ACCEPT`, `DENY` or an allowed effect by implication;
- treat an observation, AI output or remote result as a local resolution;
- claim semantic precedence for an implementation.

## Claim boundary

Seed establishes the validity and traceability of a resolution record. It does not establish the
truth of external observations, completeness of evidence, physical execution of an effect,
production safety, legal compliance or universal availability.

## Compatibility consequence

```text
component integration
    != ASET compatibility

component integration
    + exact Seed binding
    + portable conformance
    = possible ASET-compatible implementation
```

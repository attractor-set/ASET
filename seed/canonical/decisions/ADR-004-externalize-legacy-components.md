# ADR-004 — Externalize legacy component material

## Status

Accepted for Seed `0.2.0-alpha.2`.

## Context

The active Seed was already narrowed to the resolution core, but the repository still contained a
noncontrolling system/component corpus, component-specific assurance tools, audits, tests and
generated views. Their presence obscured the normative boundary and made the declared repository
gates inconsistent with the active Seed-only release gate.

## Decision

Remove the legacy component corpus from the active tree, preserve it by exact source revision and
release-asset digest, and maintain extension and implementation work in independently versioned
repositories.

Seed alpha 2 retains the alpha 1 resolution concepts, requirements, invariants, transitions and
conformance protocol. The release identity changes because the repository assurance package and
candidate boundary change.

## Consequences

- `extension_separation` becomes `COMPLETE`;
- no `aset/` component tree remains in the active repository;
- component-only assurance gates are removed;
- external registries remain non-normative;
- extensions pinned to alpha 1 remain semantically compatible but retain their exact original
  package binding;
- future component semantics require a separately versioned extension and explicit conformance.

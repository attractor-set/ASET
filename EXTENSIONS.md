# ASET extension registry

This registry is informational and non-normative. An entry does not expand the active Seed canon
and does not grant semantic precedence.

| Extension | Version | Exact canon | Scope | Status |
|---|---:|---|---|---|
| [ASET Network Extension](https://github.com/attractor-set/aset-network-extension) | `0.1.0-alpha.1` | `ASET-NETWORK-EXTENSION-CANON-0.1-ALPHA1` | Federation topology and target-local recognition | Published alpha |
| [ASET AI Extension Template](https://github.com/attractor-set/aset-ai-extension-template) | `0.1.0-alpha.1` | `ASET-AI-EXTENSION-TEMPLATE-CANON-0.1-ALPHA1` | Authority-bounded AI observations and proposals | Published alpha |

Both published extensions pin Seed alpha 1 exactly. Seed alpha 2 changes repository packaging and
assurance boundaries without changing the resolution algebra, so the registry records semantic
compatibility while retaining each exact upstream package identity.

Every extension must pin an exact Seed package, preserve all Seed invariants, publish its own
invariants and portable conformance cases, and remain independently versioned.

## Seed-owned conformance

A registry entry is not a conformance verdict. Published extensions MUST run
`ASET-SEED-EXTENSION-CONFORMANCE-V1` from the exact pinned Seed checkout and publish a
PASS report for all mandatory boundary roles. See
`docs/implementation/EXTENSION_CONFORMANCE.md`.

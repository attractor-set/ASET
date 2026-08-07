# Seed state minimization

## Decision

The abstract Seed safety state is normalized to three independent variables:

1. `requestMeta` — a partial function containing immutable request metadata only for registered `resolution_id` values;
2. `terminalMeta` — a partial function containing accepted terminal metadata only for terminal `resolution_id` values;
3. `conflicts` — the only retained environment observation because conflict can
   change a previously terminal derived resolution to `UNKNOWN`.

`LocalAuthorityBindings` and `AuthorityProofBindings` are immutable context
parameters, not mutable Seed state.

## Removed independent state

The formal projection no longer stores independent copies of:

- `requests` — exactly `DOMAIN requestMeta`;
- request/terminal absence sentinels — absence is represented by an identifier not being in the corresponding function domain;
- request binding, request Authority and predecessor maps — normalized into one
  request metadata cell (the initial Authority is admission evidence and need not
  be duplicated after successful local-root validation);
- terminal binding — derived from immutable request binding;
- terminal Authority/value maps — normalized into one terminal metadata cell;
- invalid-material observations — rejected material cannot become accepted
  terminal state, so the abstract resolution state stutters;
- non-authoritative inputs — they have no canonical state slot and therefore
  stutter by construction.

This is a representation strengthening, not a move of guarantees into a
cryptographic accumulator. No Merkle/MMR/hash algorithm is introduced into
Seed.

## Why this is stronger

The old projection represented several impossible or undesirable disagreement
states and then proved invariants excluding them. The normalized projection also
uses partial functions instead of mixed sentinel-or-record values, so each
metadata function is homogeneous whenever it is defined. The normalized projection does
not represent those disagreements at all. In particular an accepted terminal
record cannot carry a binding different from its registered request because no
independent terminal-binding state exists.

The externally visible protocol remains unchanged. Invalid records, digest
mismatches and Authority-proof failures are rejected at the protocol/conformance
boundary before they can enter the accepted abstract state.

## Formal boundary

The minimized model keeps explicit proofs for fail-closed resolution,
Authority soundness, fresh reconsideration, terminal immutability, append-only
request identity and recognized-transition state changes. It additionally makes
two boundary properties explicit:

- invalid material is a semantic stutter in the accepted abstract state;
- non-authoritative input is a semantic stutter and has no retained state slot.

Concrete cryptography, terminal-commitment accumulators, persistence and
implementation refinement remain separate profiles.

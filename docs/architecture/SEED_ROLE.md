# Role of ASET Seed

ASET Seed is a **minimal machine-interpretable semantic vessel**.

This is an architectural description, not a new protocol object. The active operational nucleus remains the minimal local resolution-recognition core defined by the exact machine-readable canon. No state field, operation, requirement or invariant is added by this document.

## Semantic vessel

Seed provides a public form in which normative meaning can remain:

- **machine-readable** — represented by explicit machine-processable artifacts rather than prose alone;
- **machine-interpretable** — relations, identities, bindings and validity conditions are explicit enough for deterministic processing and conformance evaluation;
- **independently implementable** — no language, runtime, storage engine or vendor implementation has semantic precedence;
- **independently verifiable** — implementations and extensions can be checked against public immutable semantics and conformance evidence;
- **extension-capable** — richer semantics may be layered over Seed while preserving the Seed boundary;
- **evolution-capable** — independently produced candidate forms may return to the same public verification and recognition boundary without their production mechanism becoming Authority.

The vessel carries semantic relations; it does not prescribe the content that must fill them.

## Operational nucleus

The active Seed resolution algebra remains:

```text
UNKNOWN | ALLOW | BLOCK
```

Seed owns only the state necessary to remember admitted requests and accepted terminal resolutions. It does not own the world that supplies evidence, conflict observations, policy results, cryptographic proofs, candidate generation or search.

## Seed-owned state

- immutable request metadata for registered `resolution_id` values;
- immutable terminal metadata for accepted terminal `ALLOW`/`BLOCK` values.

## Environment and observers

Conflict is environment state because additional distinct valid terminal material for an already accepted terminal resolution changes the derived resolution to `UNKNOWN`. Conflict observation is not admissible before an accepted terminal record exists.
`EVALUATE_RESOLUTION` is a pure observer and never mutates Seed-owned state.

Invalid, malformed or non-authoritative material has no Seed state slot. It may fail admission or be ignored by the resolution algebra, but it cannot create Authority, `ALLOW` or a conflict by mere presence.

## Authority boundary

Seed consumes one exact-binding Authority-recognition relation for both request registration and terminal submission. How recognition is established—signature, certificate, delegation mechanism, hardware root, external verifier or another mechanism—is a profile concern. Opaque evidence references are not Authority by themselves.

The same separation applies to evolution: generation, mutation, search, selection, evaluation or synthesis may produce candidate material, but none of those activities creates Authority or recognition merely by producing a candidate.

## Evolution boundary

ASET specifies the public boundary through which independently discovered candidate forms can become machine-verifiable claims and, where applicable, locally recognized effects. It deliberately does not prescribe the mechanism that discovers those candidates.

The formal search boundary is described in [`EVOLUTION_BOUNDARY.md`](EVOLUTION_BOUNDARY.md). Search internals are not required for Seed conformance; observable claims and evidence at the public boundary are.

## Outside Seed

Policy evaluation, evidence acquisition, workflow, federation, storage, retention/compaction, cryptographic accumulators, signature schemes, effect enforcement, candidate generation, evolutionary search, mutation operators, fitness functions, role synthesis and selection strategy are extension, implementation or strategy concerns.

Reconsideration refers to a recognized immutable terminal commitment. The predecessor object need not remain physically retained.

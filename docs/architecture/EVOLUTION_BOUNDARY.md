# ASET evolution boundary

## Status

Architectural, non-normative explanation of the public search/recognition boundary. It does not amend the active Seed canon, add Seed state, add operations, or define a required evolution algorithm.

## Purpose

ASET permits semantic forms to evolve without making one search mechanism part of the standard. The public specification defines **what must be observable at the boundary**; it does not define **how a candidate is found**.

This separation makes independent search possible while preserving implementation neutrality and local Authority.

## Abstract search problem

Let:

- `R_n` be a currently recognized artifact, state projection or semantic realization relevant to an external system;
- `T` be a public target contract, extension canon, Direction or other machine-readable constraint set external to Seed;
- `E` be any external search substrate;
- `C` be a candidate semantic form;
- `W` be evidence produced or collected for the candidate.

An external substrate may implement any function of the form:

```text
E(R_n, T, ...) -> (C, W)
```

ASET does not standardize `E`. `E` may be deterministic or stochastic, human or machine driven, local or distributed, public or private, evolutionary or non-evolutionary.

The independently solvable problem is:

```text
find any E and candidate C such that

    C can be represented under the claimed public semantic contract,
    relevant claims about C can be independently checked from public observables/evidence,
    and any requested effect can be reduced to an exact Seed ResolutionBinding
    under the target Context's own Authority-recognition relation.
```

The search space is therefore the set of candidate semantic realizations that admit a public projection to verifiable claims. ASET gives no privileged coordinates, mutation grammar, fitness function or traversal algorithm for that space.

## Non-implication rules

The following implications are invalid:

```text
ProducedBy(E, C)       -/-> Recognized(C)
SelectedBy(E, C)       -/-> Recognized(C)
HighFitness(E, C)      -/-> Recognized(C)
VerifiedUnder(T, C, W) -/-> SeedALLOW(C)
```

Verification evidence may inform an Authority decision, but evidence does not create Authority and a search substrate does not recognize its own output merely by producing it.

Only the active Seed rules determine whether an exact bound resolution is `UNKNOWN`, `ALLOW` or `BLOCK`; only `ALLOW` permits the bound effect.

## Public/private symmetry

Seed conformance requires no disclosure of search internals. A producer may disclose its search mechanism, publish only its boundary protocol, or keep the search mechanism private. These choices do not change Seed semantics.

What remains public and independently checkable is the claimed semantic contract, exact bindings, required evidence surface, observable conformance behavior and resulting Seed resolution.

This is deliberate:

> ASET standardizes how independently discovered forms can be represented, checked and locally recognized; it does not prescribe how those forms are discovered.

## Compatibility condition

An evolution mechanism is compatible with the ASET boundary when all of the following hold:

1. candidate production does not mutate Seed-owned state directly;
2. candidate production does not create Authority;
3. candidate selection does not imply recognition;
4. claims crossing into Seed use the public exact-binding protocol required by the active release;
5. implementation or extension conformance remains independently checkable without trusting the search mechanism;
6. the search mechanism has no semantic precedence over the machine-readable canon.

No stronger claim about the search mechanism is required by Seed itself.

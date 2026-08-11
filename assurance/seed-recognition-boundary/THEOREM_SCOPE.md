# Theorem scope — Seed recognition-boundary assurance

This document describes the public v60 assurance scope. It is explanatory and
non-normative; theorem statements in `formal/` and the frozen Seed canon remain
the machine-checkable sources.

## Mechanically proved layers

| Layer | Final theorem | Obligations |
|---|---|---:|
| Recognition cardinality | `ThreeRecognitionValuesAreCardinalityMinimal` | 14 |
| Operational/history cardinality | `SixRetainedHistoryClassesAreMinimal` | 190 |
| Machine bindability | `DifferentDecisionRequiresDifferentDescriptor` | 3 |
| Decision-subject binding | `DifferentGenesisChangesBinding` | 10 |
| Machine decision-subject binding | `DifferentMachineDecisionProducesDifferentExactBinding` | 10 |
| Seed recognition cardinality | `SeedRecognitionAlgebraMeetsCardinalityLowerBound` | 13 |
| Genesis-anchored recognition | `SpecImpliesNewApplicationRequiresAllow` | 35 |
| Genesis-anchored -> Seed | `GenesisAnchoredRecognitionRefinesSeedResolution` | 49 |
| Independent recognition contract | `NativeCrossCreatesOnlyAdmittedApplication` | 22 |
| Independent projection adequacy | `A9ProjectedTraceCannotRollbackAlongSuppliedStep` | 13 |
| Independent -> GCR lifting | `IndependentRecognitionRefinesGCR` | 101 |
| Minimal recognition boundary | `MinStatusRejectForRejectTerminal` | 12 |
| Minimal boundary -> Seed | `MinimalRecognitionBoundaryRefinesSeedResolution` | 189 |
| Canonical phase -> Seed | `CanonicalPhaseSeedRefinesSeedResolution` | 299 |
| Seed -> canonical phase | `SeedResolutionRefinesCanonicalPhaseSeed` | 370 |
| Payload observability | `PayloadObservationSummary` | 47 |
| Information lower bounds | `RichProfileInformationLowerBounds` | 80 |
| Parametric exact cardinality | `ParametricCardinalitySummary` | 255 |
| Canonical local reachability | `CanonicalLocalReachabilityEquivalence` | 476 |
| Reachable finite-code bound | `CanonicalReachableInformationBound` | 69 |
| **Total** |  | **2257** |

## Exact local result

For the finite canonical-link parameterization, the exact reachable
per-resolution state count is:

```text
1 + |B_rec|*|P| + 4*|RAB|*|P|
```

The normal-form state set is exactly the constructively reachable local state
set, and every state is reachable within at most three non-stuttering local
steps.

Any finite faithful encoding of that exact reachable local semantics needs at
least the same number of distinct code states.

## Scope restrictions

The proof does not claim:

- universal minimality of Seed among all possible semantic systems;
- minimum source-code variables, database columns or implementation objects;
- Shannon entropy, entropy rate or expected code length;
- a bit-size for the complete/global Seed state;
- arbitrary machine-to-Seed refinement without a domain-specific conformance
  witness;
- cryptographic security, liveness or truth of external evidence.

`MachineBindability` is a conditional deterministic factorization lemma. It does
not prove that every arbitrary recognizer has a finite, computable or canonical
decision-sufficient descriptor.

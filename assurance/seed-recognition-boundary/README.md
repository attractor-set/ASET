# Seed recognition-boundary assurance

Status: **public, non-normative assurance**. Publication baseline: **v60**.

This package is an external protective perimeter around the semantic-frozen
ASET Seed. It publishes the complete active v60 proof corpus: 34 TLA+ modules,
20 TLAPS proof modules and an expected full proof total of **2257 obligations**.
Historical failed proof attempts, retired models, version-by-version audit logs
and iteration-specific tools are intentionally not part of the published
assurance package.

The package does **not** define Seed semantics and is intentionally excluded
from `seed/canonical/CANON_PACKAGE.json`.

## Why another gate?

The Seed is frozen, but later repository work can still weaken the formal
connection to it, introduce hidden recognition distinctions, or collapse
recognition distinctions required by reachable Seed behaviour. The perimeter
therefore protects an already-defined subject instead of adding a new
normative rule.

The dependency direction is one-way:

```text
machine-readable canon
        |
        | existing canon -> TLA proof
        v
seed/canonical/formal/SeedResolution.tla
        |
        | public v60 assurance corpus
        v
recognition quotient / boundary / canonical normal form
        |
        | exact reachability + cardinality + finite-code bound
        v
repository protective perimeter
```

Nothing in this package is imported back into the normative canon. Changing
assurance material cannot silently redefine the Seed. Conversely, changing the
frozen Seed invalidates the subject binding and fails the perimeter closed.

## Published v60 corpus

The publication keeps every active v60 TLA+ model and proof module. Publication
normalization removes only historical/internal wording in comments. A pinned
`PUBLICATION_BASELINE.json` records both the original v60 file hashes and a
comment-stripped hash for every module; the gate requires the published modules
to remain identical to the proved v60 corpus after comments are removed.

See:

- [`THEOREM_SCOPE.md`](THEOREM_SCOPE.md) for the exact claim boundary;
- [`PROVENANCE.md`](PROVENANCE.md) for publication normalization and identity;
- [`ASSURANCE_PACKAGE.json`](ASSURANCE_PACKAGE.json) for machine-readable subject
  binding and proof-module obligation counts;
- [`PERIMETER_GATE.json`](PERIMETER_GATE.json) for the mandatory repository
  precondition.

## Mechanical result

The complete published corpus replays **2257/2257 TLAPS obligations** with the
pinned TLAPM identity. It includes the complete active chain from recognition
cardinality and binding lemmas through independent/minimal recognition
boundaries, bidirectional `CanonicalPhaseSeed <-> SeedResolution` refinement,
payload observability, exact parametric cardinality, canonical local
reachability and the finite faithful-code lower bound.

The terminal composed result is scoped to exact reachable **per-resolution
recognition semantics**. In particular, under the declared finite canonical
link assumptions:

```text
|ReachableLocalStates|
  = 1 + |B_rec|*|P| + 4*|RAB|*|P|
```

and every finite faithful code space for those exact reachable states needs at
least that many distinguishable code states. For a fixed-width binary code this
gives the ordinary arithmetic corollary `2^k >= N`.

## What is not claimed

This assurance does not establish universal minimality among all possible
systems, minimum implementation variable/column count, Shannon entropy,
expected code length, global Seed-state bit size, arbitrary implementation
refinement, liveness, cryptographic correctness, concrete Authority evidence or
factual truth of external evidence.

## Protective perimeter

Repository assurance executes three stages:

1. `python tools/build_seed_recognition_boundary_assurance.py --check` — package
   and publication-baseline parity;
2. `python tools/check_seed_recognition_boundary.py` — frozen subject binding,
   proof topology, publication-normalization identity and bounded executable
   falsification oracle;
3. `python tools/run_seed_recognition_boundary_tlaps.py --tlapm <tlapm>` — full
   **20-module / 2257-obligation** mechanical replay.

The release runner treats the perimeter as a mandatory repository precondition.
It deliberately has no `ASET-GATE-*` identifier because the frozen canonical
gate registry is itself normative Seed material.

## Proof-output hygiene

The pinned TLAPM build emits a small, deterministic set of generated-pattern
notices while replaying the unchanged v60 proof corpus. They are not source
locations in the published proofs: two reported line numbers exceed the full
length of `ParametricLocalStateCardinalityProofs.tla`, and the reported
character offset for the three `CanonicalLocalReachabilityProofs.tla`
coordinates exceeds the length of those source lines.

`TOOLCHAIN_NOTICES.json` therefore pins the exact notice multiset for TLAPM
`4600b24`. The TLAPS runner suppresses those raw notice lines and emits a
classified summary instead. The policy is fail-closed: a new warning, a changed
coordinate/message, or a missing expected notice fails the perimeter. This
avoids rewriting an already-proved formal program merely to accommodate
toolchain-generated pattern diagnostics.

The expected clean summary is:

```text
SEED_RECOGNITION_BOUNDARY_TLAPM_KNOWN_NOTICES=15
SEED_RECOGNITION_BOUNDARY_TLAPM_UNEXPECTED_WARNINGS=0
```

## Re-baselining

A failure caused by a changed canonical package or `SeedResolution.tla` must
not be fixed by merely updating hashes. A new baseline requires an explicit
Seed/assurance decision, regenerated provenance, complete mechanical replay and
review of the claim boundary.

# ASET Seed as the Semantic Nucleus

## Status

This document explains the architectural role defined normatively by `seed_role` in `aset/system/canonical/source/system-composition-model.json`. If this explanation conflicts with the machine-readable composition canon or with ASET Seed, the machine-readable canon prevails.

## Role

ASET Seed is the minimal, implementation-neutral semantic nucleus of ASET. It defines the authority-bound concepts, validity conditions, invariants and transition semantics required for ASET-compatible systems.

Seed is not a reduced product edition of the full ASET stack. It is the common normative basis from which different complete systems and implementation profiles may grow.

> Components may perform the work; Seed determines when that work acquires authoritative ASET significance.

## Composition boundary

A complete ASET system may use independently developed internal or external components for planning, memory, orchestration, execution control, evidence acquisition, storage, user interaction and analytics. These components do not become normative merely because they are integrated.

A transition that claims authoritative ASET significance must conform to Seed semantics. This includes:

- authorization of a meaningful state change;
- authoritative recording of its execution;
- verification of an observation or claimed result;
- recognition of a result as an Outcome;
- any other transition represented as changing canonical ASET state.

Local computation that makes no authoritative claim may remain outside the Seed transition lifecycle.

## Extension boundary

Component canons and implementation profiles may:

- refine Seed concepts for a specific domain;
- impose stricter authorization or evidence requirements;
- add controls, lifecycle states and implementation safeguards;
- use independent technologies and storage models;
- integrate external systems through declared adapters.

They must not weaken, merge or bypass Seed distinctions and invariants. In particular, an extension must not silently equate identity with Authority, Decision with Permit, Observation with Verification, or Verification with Outcome.

## Claim boundary

Seed establishes normative validity and traceability for authoritative transitions. It does not by itself establish:

- factual truth of observations;
- completeness of evidence;
- correctness of external source data;
- physical execution of an external effect;
- universal safety or legal compliance.

Those claims require appropriate evidence, verification procedures, authorities and implementation profiles.

## Capabilities not provided by Seed

Seed defines how relevant outputs acquire authoritative significance, but it does not itself provide complete infrastructure for:

- planning;
- long-term memory;
- agent and workflow orchestration;
- external-effect execution;
- evidence acquisition;
- process analytics.

ASET components or compatible external systems may provide these capabilities.

## Compatibility consequence

A collection of integrated components is not automatically an ASET-compatible system. Compatibility requires declared mappings and conformance of authoritative transitions to the Seed semantic lifecycle.

```text
component integration
    != ASET compatibility

component integration
    + declared Seed mappings
    + Seed conformance
    = possible ASET-compatible implementation
```

The canonical machine-readable definition remains the `seed_role` object in the System Composition canon.

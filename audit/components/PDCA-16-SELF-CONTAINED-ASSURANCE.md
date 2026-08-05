# PDCA-16 — self-contained component assurance

## PLAN

Make every independently versioned component canon auditable without consulting the monolithic rc11 registries for its local assurance slice.

Success criteria:

- local requirements, verification cases and traceability remain an exact 177/177/177 partition;
- each component and the system canon include local invariants, limitations, threat model, protocol profile and conformance binding;
- canonical assets are explicitly linked from each canon;
- no schema, runtime or Seed duplication;
- the cycle ends with an independent black-box audit.

## DO

- Materialized local assurance packages for Context, Core, Model Gateway, Master, Memory, Monade, Protocol and System Composition.
- Added closed schemas for component requirements, verification cases, traceability, invariants, limitations, threat models, protocol profiles and conformance bindings.
- Added `canon_assets` to every component and system canon.
- Retained the exact rc11 source once under `aset/source/rc11/`; local packages are deterministic partitions rather than rewritten claims.
- Reused the shared component toolchain instead of introducing eight validator stacks.

## CHECK

- Requirement partition: 177/177.
- Verification partition: 177/177.
- Traceability partition: 177/177.
- Component conformance: 26/26 PASS.
- Bounded component models: 8/8 PASS.
- Seed RC12 exact-byte baseline: unchanged.

## ACT — terminal black-box audit

The terminal PDCA-16 black-box audit validates the self-contained assurance packages, local traceability identity and canonical asset closure. Its output is stored as `PDCA-16-BLACKBOX.json` and `PDCA-16-BLACKBOX.md` and forms the input to the adversarial closure cycle.

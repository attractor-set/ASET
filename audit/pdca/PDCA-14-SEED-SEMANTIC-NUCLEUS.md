# PDCA-14 — Seed semantic nucleus

## Plan

Clarify the architectural role of ASET Seed without changing Seed 0.1-rc12 canonical bytes or bounded runtime behavior.

Required properties:

- define Seed as the minimal, implementation-neutral semantic nucleus of ASET;
- allow complete ASET systems to compose independent internal or external components;
- require Seed conformance only for transitions that claim authoritative ASET significance;
- allow stricter component refinements while forbidding weakening, merging or bypassing Seed distinctions and invariants;
- preserve the boundary between normative validity and factual truth;
- state explicitly which application capabilities Seed does not itself provide.

## Do

- Added the normative `seed_role` object to `aset/system/canonical/source/system-composition-model.json`.
- Closed the new object in `system-composition-canon.schema.json`.
- Strengthened the Seed compatibility bridge with an authoritative-significance guarantee and an integration-alone limitation.
- Updated all protocol-profile bindings to the refreshed Seed bridge digest.
- Extended generated System Composition views in Russian, English and Brazilian Portuguese.
- Added `docs/architecture/SEED_ROLE.md` and concise curated explanations to the repository READMEs and component-canon index.
- Strengthened component validation and the existing independent-version black-box check without changing the black-box check count.

## Check

Verified in the patch-construction environment:

- repository generated-view parity: `PASS`;
- foreign-term policy: `PASS`;
- component-canon schema and digest validation: `PASS`;
- bounded component model checking: `8/8 PASS`;
- complete unit-test suite: `87/87 PASS`;
- deterministic release snapshot: `PASS`;
- component black-box audit: `27/27 PASS`;
- component adversarial mutation rejection: `13/13 PASS`;
- documentation black-box audit: `33/33 PASS`;
- manifest parity and repository diff checks: `PASS`.

The exact project production gate remains mandatory before merge. The patch-construction environment does not contain the pinned `pyshacl` and Ruff dependencies used by the project virtual environment.

## Act

The role of Seed is now explicit at the System Composition level:

> Components may perform the work; Seed determines when that work acquires authoritative ASET significance.

This cycle does not add planning, memory, orchestration, execution, evidence-acquisition or analytics mechanisms to Seed. Future component canons and implementation profiles may provide them, but authoritative transitions remain bound to Seed semantics.

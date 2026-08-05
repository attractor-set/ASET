# PDCA-18 — release identity and multilingual closure

## PLAN

Close only the defects discovered after PDCA-17: stale release identity after the final canon edits, generated pt-BR foreign-term violations, and small Python hygiene issues in the new shared component toolchain. Do not change Seed RC12 bytes or component semantics.

Success criteria:

- generated EN, RU and pt-BR component views are derived from the canonical models and pass the repository language policy;
- component and Seed partitions, digests, conformance and bounded formal evidence remain unchanged in meaning;
- the exact rc11 source archive remains bound to SHA-256 `4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22`;
- all available repository, runtime, coverage, wheel and component regression checks pass;
- the manifest and final snapshot are rebuilt only after every repository edit;
- the final action is a fresh independent black-box and adversarial audit of the rebuilt snapshot, with no later repository mutation.

## DO

- Moved pt-BR foreign-term normalization into `tools/generate_component_views.py`, so generated views are corrected from the canonical generation path rather than edited by hand.
- Added a regression test requiring all generated component views to pass `tools/check_language.py`.
- Removed only unused imports, an unused loop binding and overlong lines introduced by the component toolchain.
- Preserved the shared validator/generator/conformance/model-check architecture; no per-component toolchain copies were added.
- Prepared the release identity for a final rebuild after this cycle record.

## CHECK

The pre-terminal regression produced:

- generated Seed editions parity: PASS;
- generated semantic views parity: PASS;
- generated component views parity: PASS;
- multilingual foreign-term policy: PASS;
- Seed RC12 canon validation: PASS;
- component canon validation: 7 canons, independent `0.1-rc1` versions, requirements 177/177, invariants 57/57, artifacts 52/52, gates 11/11, schemas 57/57, Seed bridge PASS;
- Seed conformance: 55/55 PASS;
- component conformance: 26/26 PASS;
- Seed bounded model: 281 states and 832 transitions, PASS;
- component bounded models: 8/8 PASS;
- Seed branch coverage: 730/806 branches, 90.570720%, PASS;
- full pytest regression: 55/55 PASS;
- wheel content/install/import: PASS with 39 runtime schemas;
- exact expanded rc11 bytes and Git storage: 174/174 PASS;
- independent RDF parse and implemented SHACL-subset constraints: PASS for Seed and all seven component vocabularies;
- manual AST/static audit of all new Python files: no unused imports, syntax errors, trailing whitespace or lines over 100 characters.

Execution boundary: the exact repository commands using pinned `ruff==0.15.22` and `pyshacl==0.40.0` were not executable in this container because those modules are absent. They are not reported as PASS. The terminal delivery summary records them as environment-unavailable controls, while CI remains the authoritative place for their exact execution.

## ACT — terminal black-box audit

After rebuilding `MANIFEST.json` and the deterministic repository snapshot, run standalone component, documentation and runtime black-box audits plus component, runtime and full-repository adversarial harnesses. Their reports are written only under excluded `dist/`; no repository content is changed after the snapshot audit.

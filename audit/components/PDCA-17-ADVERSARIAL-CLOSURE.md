# PDCA-17 — adversarial closure and final regression

## PLAN

Close the component-canon extraction without adding new semantics. Make the specification line discoverable from the repository root, require the adversarial component audit in the production gate and repeat all available Seed and component regressions.

Success criteria:

- root documentation links to the component canon index in EN, RU and pt-BR;
- the production gate invokes both the standalone component black-box audit and its adversarial harness;
- all 13 adversarial cases detect their target mutation;
- component validation, generated parity, conformance and bounded models remain green;
- Seed exact bytes and runtime tests remain unchanged;
- the final action is an independent full-project black-box audit with no later repository mutation.

## DO

- Added concise root-level navigation and bounded assurance claims.
- Added black-box controls for adversarial gate integration and multilingual discoverability.
- Added regression tests for both controls.
- Kept the shared toolchain and existing component boundaries unchanged.

## CHECK

The final regression commands and their outputs are recorded in the delivery summary. Exact pinned Ruff/pySHACL production validation remains dependent on the repository's declared CI environment and is not replaced by a weaker local claim.

## ACT — terminal black-box audit

The authoritative terminal report is emitted to `dist/final-component-blackbox.json` and `dist/final-component-blackbox.md`. No repository content is changed after that audit.

# ASET engineering instructions

These instructions apply to the entire repository. More specific instructions may narrow them but must not weaken normative, frozen-release, or assurance boundaries.

## Think before coding

- State assumptions, ambiguities, and trade-offs before implementation.
- Stop and ask when an ambiguity changes semantics, security, compatibility, or release identity.
- Prefer the simplest interpretation that satisfies the explicit requirement; do not silently add scope.
- Define measurable success criteria before changing code.

## Simplicity first

- Add only code required by the current goal.
- Do not introduce speculative abstractions, adapters, configuration, services, or extension points.
- Prefer one clear implementation over a framework for hypothetical implementations.
- Refactor code introduced by the current change when a smaller design provides the same verified behavior.

## Surgical changes

- Every changed line must trace to the requested behavior, a failing test, or an audit finding.
- Do not reformat, rename, or clean adjacent code without a direct need.
- Preserve existing style and public behavior unless the task explicitly changes them.
- Remove only imports, variables, functions, and files made obsolete by the current change.
- Never modify `seed/releases/0.1-rc11/`; it is an immutable frozen release.

## Goal-driven execution

For each non-trivial change, use this form:

1. state the intended behavior and assumptions;
2. add or identify a reproducing test or machine check;
3. make the smallest implementation change;
4. run focused tests;
5. run regression and release checks;
6. perform a full black-box audit of the built snapshot.

A task is not complete because code was written. It is complete only when stated success criteria are machine-verifiable and pass.

## PDCA requirement

Multi-step work must use Deming cycles. Each cycle records Plan, Do, Check, and Act. The final step of every cycle is a black-box analysis of the built project, independent of internal success claims. Findings from that analysis define the next cycle.

Regular refactoring is required only when it strengthens or simplifies the model without widening scope. Refactoring must preserve regression results and be recorded in `audit/REFACTORING_LOG.md`.

## ASET Seed boundaries

- The current stable release is immutable ASET Seed 0.1-rc11 until a separately identified rc12 release is frozen.
- The specification repository makes no embedded runtime production claim.
- Implementation-profile guarantees are external to the Seed canon and must be claimed and tested separately.
- The default proof verifier rejects all proofs.
- Do not add implicit network, subprocess, tool, or physical-effect execution to the Seed runtime.
- Do not claim distributed consensus, multi-primary safety, physical-world truth, deployment key management, universal formal proof, or external certification.
- External third-party audit remains `PENDING` until exact release bytes receive an externally published audit.

## Required verification

A release-candidate change must pass all mandatory gates in `seed/canonical/assurance/repository-release-gates.json`, including:

- canonical and generated-view parity;
- frozen rc11 working-tree and Git-stored byte identity;
- 55-vector semantic conformance and 252 branch guards;
- bounded formal model checking;
- unit, integration, security, and concurrency tests;
- Ruff and real PySHACL validation;
- installable wheel verification;
- deterministic snapshot construction;
- documentation, runtime, and adversarial black-box audits.

Failure of any mandatory gate blocks commit, merge, or release promotion.

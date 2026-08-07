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
- Refactor only when the smaller design preserves the verified behavior and stated boundary.

## Surgical changes

- Every changed line must trace to requested behavior, a failing check, or an audit finding.
- Do not reformat, rename, or clean adjacent code without a direct need.
- Preserve public behavior unless the task explicitly changes it.
- Never modify `seed/releases/0.1-rc11/`; it is immutable historical release evidence.
- Never move or rewrite an existing protected semantic-freeze tag.

## Goal-driven execution

For each non-trivial change:

1. state intended behavior and assumptions;
2. add or identify a reproducing test or machine check;
3. make the smallest implementation change;
4. run focused checks;
5. run regression and release checks;
6. inspect the built snapshot independently of internal success claims.

A task is complete only when its success criteria are machine-verifiable and pass.

## PDCA requirement

Multi-step work uses Deming cycles: Plan, Do, Check, Act. Findings from the Check step define the next cycle. Refactoring must not widen scope or weaken verified boundaries.

## ASET Seed boundaries

- The active Seed source is `seed/canonical/` at version `0.3.0-alpha.1`.
- The semantic baseline is frozen by `seed-0.3.0-alpha.1-semantic-freeze`.
- Frozen Seed semantics change only through an explicitly versioned future Seed revision.
- Demonstrated defect fixes, assurance strengthening, and non-semantic documentation or metadata cleanup may proceed without redefining Seed semantics.
- New capabilities belong in external extensions or implementations and have no semantic precedence over the Seed canon.
- The repository makes no embedded production-runtime claim.
- Concrete cryptographic providers, Authority grant-chain validation, storage, durability, networking, consensus, orchestration, evidence acquisition, AI models, and external effects remain outside Seed semantics unless a future canon revision states otherwise.
- External third-party audit remains `PENDING` while the canon declares it so.

## Required verification

The authoritative release-gate list is `seed/canonical/assurance/repository-release-gates.json`.

Do not duplicate historical gate counts in engineering instructions. Run the gates declared by the current canon and tooling, including generated-view parity, canon/package validation, frozen-release integrity, finite-state checks, tests and static analysis, manifest/snapshot integrity, traceability, documentation audit, compatibility classification, invariant mutation/coverage, TLC, TLAPS, and canon-to-TLA refinement.

Failure of a mandatory gate blocks merge or release promotion. Never weaken a gate merely to make a change pass.

# Refactoring log

## Reference critical path

- Introduced a new storage-free `aset_reference` package rather than refactoring the frozen or active SQLite Seed runtime.
- Kept the kernel as one explicit validation pipeline and one immutable value model; no repositories, adapters, dependency injection, configuration, or plugin abstractions were introduced.
- Separated deterministic canonicalization from transition semantics because both are independently testable normative concerns.

## Repository metadata generation

- Introduced one strict `metadata/project.json` source instead of duplicating the About description and topics across CodeMeta, scripts and CI.
- Added one thin orchestration command over the existing generators rather than replacing their independent, testable responsibilities.
- Kept multilingual explanatory README text static; only deterministic repository-discovery and machine-derived views are generated.
- Kept GitHub repository mutation outside ordinary CI and exposed it as an explicit administrator-authorized operation.
## Seed semantic nucleus

- Added one closed `seed_role` object to the existing System Composition canon instead of introducing a parallel architecture registry.
- Kept Seed implementation-neutral and left planning, memory, orchestration, execution infrastructure, evidence acquisition and analytics outside its provided capabilities.
- Reused the existing Seed compatibility bridge and generated-view pipeline rather than creating a new integration framework.
- Strengthened the existing component black-box check instead of increasing the audit surface with a redundant check identifier.

## Assurance-toolchain neutrality and reference implementation discovery

- Rephrased the active System Composition environment invariant so that it binds an externally committed assurance-toolchain and dependency closure without prescribing Python or any implementation runtime.
- Replaced Python-specific environment descriptions in active component and system verification cases with implementation-neutral assurance-toolchain descriptions; frozen rc11 source evidence remains unchanged.
- Linked the separate non-normative [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite) reference implementation from all curated root README editions and the roadmap without granting it semantic precedence.

## Seed final semantic cleanup

- Unified request and terminal admission under one `RecognizedAuthorityBindings` relation to match the single wire AuthorityBinding semantics.
- Restricted conflict observation to already accepted terminal resolutions, eliminating impossible pre-terminal conflict states.
- Distinguished accepted terminal uniqueness from external valid conflict material through `AcceptedTerminalUnique` and `ConflictSound`.
- Reclassified the machine-canon catalogue as three operations: two state transitions and one observer, with `SEED-OP-*` identifiers.
- Advanced the standalone canon-to-TLA projection to V5 and updated the active audit methodology and evidence line.

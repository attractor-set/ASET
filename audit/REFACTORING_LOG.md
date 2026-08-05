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

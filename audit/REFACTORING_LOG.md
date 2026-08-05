# Refactoring log

## Reference critical path

- Introduced a new storage-free `aset_reference` package rather than refactoring the frozen or active SQLite Seed runtime.
- Kept the kernel as one explicit validation pipeline and one immutable value model; no repositories, adapters, dependency injection, configuration, or plugin abstractions were introduced.
- Separated deterministic canonicalization from transition semantics because both are independently testable normative concerns.

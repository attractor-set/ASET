# Implementation neutrality and model-based conformance

[English](IMPLEMENTATION_NEUTRALITY.md)

ASET is defined by its machine-readable canon, normative schemas, invariants, transition semantics and conformance corpus. It is not defined by Python, SQLite, PostgreSQL, Rust, a consensus protocol or any other implementation technology.

A concrete implementation exposes the language-neutral `ASET-IMPLEMENTATION-CONFORMANCE-V1` adapter. The external conformance runner consumes the canon from an independently identified commit or release package, executes each case as a black box and compares the observable result with the model-bound expectation.

The specification repository therefore proves and publishes semantics. Separate implementation repositories demonstrate operational realizations and profile-specific guarantees.

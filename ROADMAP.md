# Roadmap

1. Freeze the minimal `UNKNOWN -> ACCEPT | DENY` resolution algebra and exact binding rules.
2. Validate the new protocol through two independent implementations.
3. Move Context, Federation, Core, Monade, Master and AI-system semantics into separately versioned extension-template repositories.
4. Update `aset-python-sqlite` to the new black-box protocol without treating it as an oracle.
5. Build an independent Rust/PostgreSQL implementation and use differential results only to expose ambiguity.
6. Complete an external semantic and formal audit before Seed 1.0.

## Supporting records

- Historical component canons pending extraction: [`aset/README.md`](aset/README.md)
- Cross-implementation admission plan: [`docs/implementation/CROSS_IMPLEMENTATION_CONFORMANCE_PLAN.md`](docs/implementation/CROSS_IMPLEMENTATION_CONFORMANCE_PLAN.md)
- Non-normative implementation: [`aset-python-sqlite`](https://github.com/attractor-set/aset-python-sqlite)
- Background-IP provenance: [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md)

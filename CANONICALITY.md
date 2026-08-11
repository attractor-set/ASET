# Canonicality

The normative source is `seed/canonical/source/seed-model.json` together with the exact files listed in `seed/canonical/CANON_PACKAGE.json`.

The Seed resolution algebra is `UNKNOWN | ALLOW | BLOCK`. `UNKNOWN` is derived when no unique valid terminal record exists. Only a valid exact-binding locally authorized `ALLOW` record permits the bound effect. `BLOCK`, absence, invalidity and conflict are fail-closed.

Generated language editions, formal projections and executable oracles are controlled representations of the machine canon. No implementation, extension, storage engine, policy language or cryptographic provider has semantic precedence.

## Architectural meaning and operational canon

ASET describes Seed architecturally as a machine-interpretable semantic vessel because the public form can be independently implemented, verified, extended and reused as the boundary for later candidate semantics. This architectural description does **not** enlarge the active Seed state machine.

The exact files in `seed/canonical/CANON_PACKAGE.json` remain the sole normative source for Seed operational semantics and conformance. Architecture documents such as `docs/architecture/SEED_ROLE.md` and `docs/architecture/EVOLUTION_BOUNDARY.md` explain the role and open search boundary of Seed; they cannot add a state field, operation, validity rule, Authority source or recognition path unless such a change is separately incorporated into a new immutable canon package.

In particular, candidate-generation and evolutionary-search mechanisms have no semantic precedence and need not be disclosed for Seed conformance. Their outputs acquire no Authority merely because they were produced, selected or verified.

# ASET Seed 0.2 alpha resolution core

Status: `RESOLUTION_CORE_ALPHA`

The active Seed is the implementation-neutral normative core for narrowing an exact unresolved question:

```text
UNKNOWN -> ACCEPT | DENY
```

`UNKNOWN` and `DENY` are operationally `BLOCKED`. Only `ACCEPT` may produce `ALLOW`. An unresolved question may remain `UNKNOWN` while it moves to a next explicitly authorized Resolution Authority. Context ancestry or federation membership alone creates no authority.

## Active canon

1. `source/seed-model.json` — normative machine model;
2. `protocol/` — minimal resolution wire schemas;
3. `conformance/` — portable black-box cases;
4. `CANON_PACKAGE.json` — exact package identity;
5. `formal/SeedResolution.tla` — bounded assurance projection;
6. generated multilingual editions — derived views.

## Scope boundary

Seed does not define execution, Permit consumption, attempt journals, planning, memory, federation topology, consensus, storage, cryptographic providers or artifact retention. Those belong to extensions and implementations.

The migration from the predecessor lifecycle canon is intentionally breaking and is documented in `migration/RC12_TO_RESOLUTION_CORE.md`.

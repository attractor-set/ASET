# Canonicality

The normative source is `seed/canonical/source/seed-model.json` together with the exact files listed in `seed/canonical/CANON_PACKAGE.json`.

The Seed resolution algebra is `UNKNOWN | ALLOW | BLOCK`. `UNKNOWN` is derived when no unique valid terminal record exists. Only a valid exact-binding locally authorized `ALLOW` record permits the bound effect. `BLOCK`, absence, invalidity and conflict are fail-closed.

Generated language editions, formal projections and executable oracles are controlled representations of the machine canon. No implementation, extension, storage engine, policy language or cryptographic provider has semantic precedence.

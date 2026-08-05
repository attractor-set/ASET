# ASET component canons

ASET Seed is the minimal, implementation-neutral semantic nucleus of ASET. This directory defines independently versioned component canons that may grow around that nucleus while remaining explicitly bound to Seed transition semantics.

The component canons decompose the exact ASET 1.5-rc11 monolithic machine specification into System Composition, Context, Core, Monade, Memory, Master, Model Gateway and Protocol profiles above ASET Seed 0.1-rc12.

Component line: `0.1-rc1`.

- `system/`: composition and compatibility matrix;
- `components/context/`: namespace, immutable components and atomic patch semantics;
- `components/core/`: resolution, Permit and gate crossing;
- `components/monade/`: Task, execution and independent acceptance;
- `components/memory/`: provenance-preserving memory and mutation;
- `components/master/`: planning, ExpectedChangePatch and advisory attractor analysis;
- `components/gateway/`: provider request rendering;
- `components/protocol/`: closed schemas, canonicalization and signatures;
- `shared/seed-bridge/`: explicit mapping to Seed 0.1-rc12;
- `shared/migration/`: exact partition coverage of the rc11 monolith.

The component canons do not modify or supersede Seed. No implementation or production conformance is claimed.

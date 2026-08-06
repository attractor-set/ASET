# Historical ASET extension migration archive

The active normative ASET Seed exists only under [`seed/canonical/`](../seed/canonical/).
This `aset/` tree is a **noncontrolling migration archive** retained temporarily so the
pre-split rc11/rc12 decomposition can be extracted into separately versioned extension-template
repositories without losing byte identity, traceability, or authorship evidence.

Nothing under this directory:

- expands the active Seed;
- is part of active Seed conformance;
- is executed by the active Seed release gate;
- has semantic precedence over `seed/canonical/`;
- makes Monade, Master, Core, Memory, Context, Protocol, Gateway, or System Composition part of Seed.

The archived component line contains historical decomposition material for:

- `system/`;
- `components/context/`;
- `components/core/`;
- `components/monade/`;
- `components/memory/`;
- `components/master/`;
- `components/gateway/`;
- `components/protocol/`;
- `shared/seed-bridge/`;
- `shared/migration/`.

The previously added in-repository Monade Attempt Evidence Profile has been removed. Any future
Monade specification, including attempt and negative-result evidence, belongs in an external
extension-template repository pinned to an exact Seed package digest.

Historical archive checks may be run manually and must not be interpreted as Seed release gates.

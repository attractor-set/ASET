# Formal-model status

`SeedBootstrap.tla` is a wiring scaffold only.

It is not the complete ASET Seed transition semantics and must not
be cited as a proof of rc11 or rc12 correctness.

Before a formal gate may report PASS:

- the complete transition relation must be modeled;
- safety and liveness properties must be mapped to requirement IDs;
- the TLA+ toolchain must be pinned by digest;
- expected counterexamples must be included;
- TLC and/or Apalache outputs must be retained as evidence.

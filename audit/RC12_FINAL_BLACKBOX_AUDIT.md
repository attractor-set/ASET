# ASET Seed 0.1-rc12 final pre-freeze black-box declaration

## Boundary

The final audit treats the deterministic repository snapshot as an external consumer would. It does not trust internal reports as evidence of their own correctness. It independently checks archive structure, manifest hashes, mandatory documentation, frozen rc11 byte identity, machine-canon completeness, canonical/runtime schema identity, claim boundaries, formal projection presence, executable runtime behavior, and controlled adversarial mutations.

## Required results

- documentation black-box audit: 32/32;
- runtime black-box audit: 18/18;
- documentation adversarial mutations: 15/15 rejected;
- runtime adversarial mutations: 9/9 detected;
- semantic regression: 55/55 vectors;
- branch guards: 252/252;
- bounded model: 281 reachable states and 832 explored transitions;
- unit/integration/security tests: 45/45 or greater after final repository validation;
- semantic-core branch coverage: at least 90%;
- open blocking findings: zero.

## Assurance conclusion

A candidate satisfying every mandatory gate is technically ready for the separate exact-byte freeze cycle for `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1`. This conclusion excludes distributed consensus, multi-primary operation, automatic external effects, physical-world truth, deployment key management, unbounded formal proof, and external certification.

Owner freeze approval, exact-byte clean-room materialization, protected tag creation, and tag-bound postchecks are not performed by this declaration. External third-party audit remains pending. Machine reports generated from the final snapshot are controlling; this declaration cannot override a failing report.

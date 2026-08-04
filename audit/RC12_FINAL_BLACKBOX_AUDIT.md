# ASET Seed 0.1-rc12 final black-box audit declaration

## Boundary

The final audit treats the deterministic repository snapshot as an external consumer would. It does not trust internal validation reports as proof of their own correctness. It independently checks archive structure, hashes, mandatory documentation, rc11 byte identity, machine-canon completeness, protocol/runtime schema identity, claim boundaries, formal projection presence, executable runtime behavior, and adversarial rejection.

## Required results

- documentation audit: 28/28 mandatory checks;
- runtime audit: 8/8 behavioral checks;
- adversarial audit: 15/15 controlled corruptions rejected;
- semantic regression: 55/55 vectors;
- branch guards: 252/252;
- bounded model: 281 reachable states and 832 explored transitions;
- unit/integration/security tests: 30/30;
- semantic-core branch coverage: 730/806, 90.570720%.

## Assurance conclusion

A result satisfying every mandatory gate is production-ready only for `ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1`. This conclusion excludes distributed consensus, multi-primary operation, automatic external effects, physical-world truth, deployment key management, universal formal proof, and external certification. External third-party audit remains pending.

Machine reports generated from the final snapshot are the controlling evidence; this declaration does not override a failing report.

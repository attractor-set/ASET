# PDCA-12 — final pre-freeze assurance

## Plan

Close the four findings emitted by the PDCA-11 black-box analysis without expanding Seed semantics. Success requires:

- stable rejection of invalid trust-space identifiers;
- one strict stored-state guard on every retrieval/execution path;
- exact 23-gate repository validation;
- direct and adversarial proof that HMAC authorization binds exact transition content;
- full regression and snapshot-only black-box audits;
- zero open P0/P1 findings.

## Do

- validated the exact `ts:<64 lowercase hexadecimal>` identifier before database access;
- reused `_decode_stored_state` from `get_state`, idempotent `initialize`, `apply`, health, and backup;
- updated strict repository validation and gate-count tests;
- added modified-after-proof HMAC regression, public CLI black-box coverage, and verifier mutation detection;
- strengthened backup black-box verification to reopen, health-check, and validate restored state;
- added a machine-readable technical freeze-entry record that keeps owner approval and exact-byte freeze explicitly pending;
- refactored duplicate boundary logic into small existing helpers rather than adding another abstraction layer.

## Check — complete project black-box audit

The final deterministic snapshot is checked independently for archive safety, manifest identity, canon completeness, rc11 byte preservation, generated-language parity, proof-profile safety, release boundaries, hostile runtime behavior, and controlled implementation mutations.

Required final results:

- machine canon: 27 concepts, 40 requirements, 37 invariants, 18 transitions, 39 schemas, 55 bindings;
- migration: 83/83, zero deferred and zero unclassified;
- semantic conformance: 55/55;
- branch guards: 252/252;
- bounded model: 281 states and 832 transitions;
- tests: 45/45 or greater after final repository checks;
- documentation black-box: 32/32;
- runtime black-box: 18/18;
- documentation adversarial mutations: 15/15 rejected;
- runtime adversarial mutations: 9/9 detected;
- open blocking findings: zero.

## Act

When every mandatory gate passes on the exact merge commit, classify rc12 as `READY_FOR_EXACT_BYTE_FREEZE`. Do not create the stable tag yet: owner approval, clean-room exact-byte materialization, final release envelope, and tag-bound postchecks remain the separate freeze cycle.

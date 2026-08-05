# Python full critical-path reference — PDCA record

Each cycle ends with a black-box observation that determines the next cycle.
The record concerns the non-normative deterministic semantic reference only.

## Cycle 1 — baseline truthfulness

**Plan:** test the pre-existing reducer against the System Composition path.
**Do:** exercised failure evidence, canonicalization, permit identity and artifact inventory.
**Check:** the reducer covered one generic mutation, not the full critical path.
**Act / terminal black-box:** classified the old implementation as partial and removed false traceability.
Next cycle: implement the smallest complete eight-gate path.

## Cycle 2 — complete causal path

**Plan:** add only the mandatory artifacts and gates.
**Do:** implemented projection, expectation, binding, dispatch, observation, evidence,
verification, acceptance, task closure and conditional Outcome.
**Check:** all four effect classes reached explicit terminal states.
**Act / terminal black-box:** confirmed the chain but found duplicate ad-hoc canonicalization.
Next cycle: reuse Seed canonical semantics.

## Cycle 3 — canonical identity

**Plan:** make cross-language bytes authoritative.
**Do:** reused Seed NFC, integer-only, domain-separated, length-framed canonicalization.
**Check:** floats and normalized-key collisions fail closed; equivalent Unicode is identical.
**Act / terminal black-box:** canonical probes passed and exposed the need for durable causal evidence.
Next cycle: add exact receipts and restore validation.

## Cycle 4 — authority and receipt chain

**Plan:** bind Resolution, Permit, receipt and patch to one source Context.
**Do:** added one-shot permits, exact write-sets, immediate-predecessor receipts and Context roots.
**Check:** stale, wrong-gate, wrong-patch and replay cases fail closed.
**Act / terminal black-box:** mutation of restored state exposed missing whole-chain validation.
Next cycle: validate snapshots as a causal graph.

## Cycle 5 — recovery model

**Plan:** make snapshot restoration reject structurally plausible tampering.
**Do:** validated map identities, crossing order, roots, resolutions, permits, receipts,
consumed sets, write-sets and terminal Context identity.
**Check:** exact round-trip succeeds and hostile mutations fail.
**Act / terminal black-box:** restore audit passed and showed that pytest alone was insufficient evidence.
Next cycle: independent conformance and bounded model tools.

## Cycle 6 — independent assurance

**Plan:** move critical claims out of unit-test-only evidence.
**Do:** added a 26-case conformance runner and four-class bounded model check.
**Check:** 32 governed crossings and all terminal conditions were verified.
**Act / terminal black-box:** source audit passed and identified release-snapshot isolation as the next boundary.
Next cycle: execute black-box checks from the immutable archive.

## Cycle 7 — release black-box and adversarial sensitivity

**Plan:** verify only public files from the deterministic release snapshot.
**Do:** added 10 independent black-box checks and 10 snapshot mutations.
**Check:** the audit detects removed bindings, write-set changes and causal-chain corruption.
**Act / terminal black-box:** release audit passed and found CI did not yet make these controls mandatory.
Next cycle: integrate fail-closed CI and production gate.

## Cycle 8 — simplification and CI closure

**Plan:** remove obsolete reducer files and avoid a second infrastructure stack.
**Do:** kept one storage-free package, one deterministic connector, one conformance runner,
one model checker and two black-box tools; integrated them into CI and wheel verification.
**Check:** focused, repository, wheel and release gates run from the same source tree.
**Act / terminal black-box:** final immutable-snapshot audit and adversarial audit are the release evidence.
No additional semantic scope was added.

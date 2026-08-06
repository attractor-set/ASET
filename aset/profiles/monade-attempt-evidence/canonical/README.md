# Monade Attempt Evidence Profile

`ASET-MONADE-ATTEMPT-EVIDENCE-V1` is an optional normative component profile. It preserves execution attempts, negative dispositions and verification evidence without admitting rejected candidates into the canonical Context graph.

The profile is **not normative for ASET Seed** and is **not required for Seed implementation conformance**. A core-only implementation may ignore it and remain Seed-conformant.

## Boundary

- Monade owns attempt execution, evidence collection, verification disposition and append-only attempt records.
- A rejected or quarantined attempt never changes canonical Context and never becomes a canonical parent.
- `ACCEPTED_FOR_RECOGNITION` is not an Outcome; recognition remains a separate authority-controlled gate.
- Master may consume a read-only `LearningObservation` projection. The projection grants no Permit, authority, verification or recognition power.
- Retry creates a new attempt and references the prior attempt.

## Evidence path

Large artifacts may remain outside the record. The record carries content-addressed digests and implementation-defined locations.

# ASET Memory 0.1-rc1

Preserves provenance, episodes, and memory projections without turning retrieval into authority or a verified fact.

- `component_id`: `aset.memory`
- `version`: `0.1-rc1`
- `status`: `COMPONENT_CANON_CANDIDATE`
- `canonical_digest`: `sha256:fe4c5a7e6ad4dfe7dc43ee988fc82b1214f034b2a9e81c5fe07b3abfab3d9d67`

## Source boundary

- `ASET`: `1.5-rc11`
- `archive_sha256`: `sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22`
- `model_digest`: `sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94`
- `specification_digest`: `sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6`

## Ownership

- `ContextProjection`
- `MemoryCandidate`
- `MemoryItem`
- `MemoryReceipt`
- `RawEvent`

## Forbidden responsibilities

- issue Permit
- own Task
- self-verify claims

## Operations and Seed mapping

### `MEM-PROJECT` — ProjectMemory

Produce a scoped provenance-preserving memory projection without promoting epistemic status.

- `classification`: `LOCAL_NON_GOVERNED_COMPUTATION`
- `seed_transition_required`: `False`
- `seed_sequence`: `none`
- `outcome_recognition_required`: `False`

### `MEM-MUTATE` — MutateMemory

Apply an authorized memory lifecycle mutation and emit a receipt.

- `classification`: `GOVERNED_CONTEXT_MUTATION`
- `seed_transition_required`: `True`
- `seed_sequence`: `Decision → Permit → PermitUseReceipt`
- `outcome_recognition_required`: `False`

## Requirements

Count: `20`

`MEM-001`, `MEM-002`, `MEM-003`, `MEM-004`, `MEM-005`, `MEM-006`, `MEM-007`, `MEM-008`, `MEM-009`, `MEM-010`, `MEM-011`, `MEM-012`, `MEM-013`, `MEM-014`, `MEM-015`, `MEM-016`, `MEM-017`, `MEM-018`, `MEM-019`, `MEM-020`

## Invariants

- `INV-MEM-001` — Memory и operational Context различны.
- `MEM-BND-001` — Memory retrieval is advisory and does not establish authority or verification.

## Assurance boundaries

- `MEMORY-LIM-001` (`HIGH`) — This component canon is a normative decomposition; no independent component implementation has yet demonstrated semantic conformance. Required evidence: Independent implementation, component conformance execution, and fault-injection evidence.
- `MEMORY-LIM-002` (`MEDIUM`) — The extraction preserves rc11 semantics but the new component release bytes have not received an external third-party audit. Required evidence: External exact-byte audit of the component release.

## Machine-readable canon assets

- `conformance_binding`: `aset/components/memory/canonical/conformance/binding.json`
- `formal_profile`: `aset/components/memory/canonical/formal/memory.tla`
- `invariants`: `aset/components/memory/canonical/assurance/invariants.json`
- `limitations`: `aset/components/memory/canonical/assurance/limitations.json`
- `protocol_profile`: `aset/components/memory/canonical/protocol/profile.json`
- `requirements`: `aset/components/memory/canonical/assurance/requirements.json`
- `threat_model`: `aset/components/memory/canonical/assurance/threat-model.json`
- `traceability`: `aset/components/memory/canonical/assurance/traceability.json`
- `verification_cases`: `aset/components/memory/canonical/assurance/verification-cases.json`

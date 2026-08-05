# ASET Protocol 0.1-rc1

Define schemas fechados, canonicalização, assinaturas e contratos wire portáveis.

- `component_id`: `aset.protocol`
- `version`: `0.1-rc1`
- `status`: `COMPONENT_CANON_CANDIDATE`
- `canonical_digest`: `sha256:ec4ec84b6aa045946f9383b0601ad919718d2253454f36b3e0a8f59afa192662`

## Limite de origem

- `ASET`: `1.5-rc11`
- `archive_sha256`: `sha256:4fd358e3c395547bdfb8f5a3e7d71ad377d25428923eba4c4889d5e686fece22`
- `model_digest`: `sha256:cd569fafe4e241cda24527384776dc0637379529a36ffe2870cb318f3c830b94`
- `specification_digest`: `sha256:b843060044f7dc887c001a1130a8a38bec49745fbdfa9a5e66934eecdfd7eeb6`

## Propriedade

- `CanonicalEnvelope`
- `ErrorEnvelope`
- `SchemaRegistry`
- `SignatureProfile`

## Responsabilidades proibidas

- accept work
- contain module business logic
- issue Permit

## Operações e mapeamento para o Seed

### `PROTO-VALIDATE` — ValidateArtifact

Valida o documento normativo por um schema fechado antes de sua admissão.

- `classification`: `LOCAL_NON_GOVERNED_COMPUTATION`
- `seed_transition_required`: `False`
- `seed_sequence`: `none`
- `outcome_recognition_required`: `False`

### `PROTO-CANON` — CanonicalizeArtifact

Produz bytes canônicos e digest sem executar lógica de negócio.

- `classification`: `LOCAL_NON_GOVERNED_COMPUTATION`
- `seed_transition_required`: `False`
- `seed_sequence`: `none`
- `outcome_recognition_required`: `False`

## Requisitos

Count: `22`

`MRS-001`, `MRS-002`, `MRS-003`, `MRS-004`, `MRS-005`, `MRS-006`, `MRS-007`, `MRS-008`, `MRS-009`, `MRS-010`, `PRO-001`, `PRO-002`, `PRO-003`, `PRO-004`, `PRO-005`, `PRO-006`, `PRO-007`, `PRO-008`, `PRO-009`, `PRO-010`, `PRO-011`, `PRO-012`

## Invariantes

- `INV-CORPUS-001` — The positive conformance corpus forms an end-to-end digest-linked signed artifact graph; unresolved or substituted internal references are prohibited.
- `INV-CORPUS-002` — Each one-shot Permit in the positive corpus resolves to one exact signed CoreResolution that binds the exact Submission and Permit digest.
- `INV-CRYPTO-001` — ASET-JCS-1 canonical bytes, SHA-256 digests and Ed25519 signatures are verified against reproducible positive and negative vectors.
- `INV-CRYPTO-002` — Signed normative JSON values prohibit non-integer numbers unless a future version defines and tests a complete cross-language numeric canonicalization profile.
- `INV-CRYPTO-003` — ASET-JCS-1 permits only I-JSON safe integers and sorts NFC-normalized object keys by unsigned UTF-8 bytes using published cross-language edge vectors.
- `INV-ID-001` — Every stable ID in the normative machine model is globally unique; conflicting duplicate identities are prohibited.
- `INV-ID-002` — Every primary identity in requirements, ADR, verification, model, diagram, conformance, oracle, document and key registries is unique in its declared registry.
- `INV-JSON-001` — Every normative JSON input rejects duplicate raw member names before semantic parsing, schema validation, digesting or signature verification.
- `INV-SCHEMA-001` — Every normative JSON artifact is validated by a closed-world schema with unknown properties rejected.
- `INV-SCHEMA-002` — All 11 gates have distinct submission, Permit and patch schemas; a document valid for one role is invalid for every incompatible role.
- `INV-SCHEMA-003` — The externally signed fixação da versão profile binds the path, schema $id, byte SHA-256 and canonical digest of every mandatory normative JSON Schema before any schema is used.
- `PROTO-BND-001` — Protocol validation and canonicalization contain no module business logic and issue no Permit.

## Limites de assurance

- `PROTOCOL-LIM-001` (`HIGH`) — This component canon is a normative decomposition; no independent component implementation has yet demonstrated semantic conformance. Required evidence: Independent implementation, component conformance execution, and fault-injection evidence.
- `PROTOCOL-LIM-002` (`MEDIUM`) — The extraction preserves rc11 semantics but the new component release bytes have not received an external third-party audit. Required evidence: External exact-byte audit of the component release.

## Ativos do cânone legíveis por máquina

- `conformance_binding`: `aset/components/protocol/canonical/conformance/binding.json`
- `formal_profile`: `aset/components/protocol/canonical/formal/protocol.tla`
- `invariants`: `aset/components/protocol/canonical/assurance/invariants.json`
- `limitations`: `aset/components/protocol/canonical/assurance/limitations.json`
- `protocol_profile`: `aset/components/protocol/canonical/protocol/profile.json`
- `requirements`: `aset/components/protocol/canonical/assurance/requirements.json`
- `threat_model`: `aset/components/protocol/canonical/assurance/threat-model.json`
- `traceability`: `aset/components/protocol/canonical/assurance/traceability.json`
- `verification_cases`: `aset/components/protocol/canonical/assurance/verification-cases.json`

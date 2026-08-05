# ASET Background IP Schedule

**Document status:** Public evidentiary inventory
**Schedule version:** 1.0
**Effective date:** 2026-08-05
**Jurisdiction profile:** Brazil (`BR`)
**Repository:** `https://github.com/attractor-set/ASET`
**Baseline commit:** `f22c67569374550418818bbbdf1a59e96264113d`
**Baseline manifest:** `MANIFEST.json`
**Baseline manifest SHA-256:** `sha256:e127ae646d5bc7368ac1e42d6a657b5d2bbf6e2f99590d9345dfb00f704c585a`

Languages: English · [Русский](BACKGROUND_IP_SCHEDULE.ru.md) · [Português do Brasil](BACKGROUND_IP_SCHEDULE.pt-BR.md)

## 1. Purpose and legal character

This Schedule identifies ASET intellectual assets that existed before later employment,
investment, university, grant-funded, contractor or commercial-development arrangements.
It establishes a reproducible public boundary between pre-existing ASET assets and any
foreground intellectual property created under a later written agreement.

This Schedule is an evidentiary inventory. It is not an assignment, software registration,
trademark registration, legal opinion or adjudication of ownership. A transaction-specific
agreement prevails where applicable.

## 2. Creator, public pseudonym and current rights holder

- **Creator and current claimed holder of economic rights:** Dzmitry Prychyna.
- **Public pseudonym and project identity:** Attractor Set.
- **Legal-status boundary:** Attractor Set is a pseudonym used by Dzmitry Prychyna. It is not
  identified by this Schedule as a separate legal entity or a separate rights holder.
- **Future company boundary:** No future company, laboratory, university or investor receives
  rights in the Background IP merely through participation, funding or use. Any transfer must
  be made by an express written instrument.

## 3. Independent-creation declaration

Dzmitry Prychyna declares, to the best of his knowledge, that the scheduled assets were:

- conceived and developed on his own initiative;
- developed outside the scope of his employment duties and without being commissioned,
  directed, financed or supervised by his current employer;
- developed with his own computer, accounts, storage, tools, time and other resources;
- developed without unauthorized use of third-party source code, data, credentials,
  infrastructure, confidential technical information, trade secrets or business secrets;
- not produced as a client deliverable, commissioned research project, scholarship, internship
  or statutory-service obligation.

This declaration records provenance. Confidential supporting evidence must be retained outside
the public repository.

## 4. Reproducible baseline

The exact technical boundary is the Git commit and baseline manifest identified above. The
baseline commit is the primary identity. `MANIFEST.json` at that commit records the repository
files and SHA-256 values existing before this Schedule was added.

Files created after the baseline commit are not automatically Background IP under this version.
They require an amended Schedule or a separate written classification.

## 5. Background IP inventory

### BI-001 — ASET Seed

ASET Seed specifications, machine canon, terminology, schemas, formal models, conformance
cases, frozen releases, generated editions, bounded runtime and associated assurance materials.

Primary paths: `seed/`, `src/aset_seed/`, `docs/generated/`, `docs/runtime/`.

### BI-002 — Full ASET system and component canons

The preserved full ASET source models, System Composition, Context, Core, Monade, Memory,
Master, Model Gateway and Protocol canons, shared bridges and component assurance packages.

Primary paths: `aset/source/`, `aset/system/`, `aset/components/`, `aset/shared/`.

### BI-003 — Reference implementations and executable tooling

The Python semantic critical-path reference, bounded runtime implementation, command-line
interfaces and supporting executable tools existing at the baseline.

Primary paths: `src/aset_reference/`, `src/aset_seed/`, `tools/`.

### BI-004 — Assurance, conformance and formal-verification assets

Authored test vectors, tests, model-checking projections, validation tools, release gates,
deterministic-build logic, black-box audits, adversarial suites and traceability mechanisms.

Primary paths: `tests/`, `test-vectors/`, `audit/`, `tools/`, and component assurance directories.

### BI-005 — Documentation and original authored expression

Architecture descriptions, specifications, diagrams, examples, governance documents,
terminology and the original selection and arrangement of repository materials.

Primary paths: `docs/` and the active root Markdown documentation.

### BI-006 — Project identity and release metadata

ASET repository identity, release naming, project metadata, manifests, citations and release
status records existing at the baseline.

Primary paths: `metadata/`, `codemeta.json`, `CITATION.cff`, `MANIFEST.json`,
`REPOSITORY_STATUS.json`.

### BI-007 — ASET names and associated project goodwill

The ASET name, component names, release identifiers and the Attractor Set public project
identity, subject to applicable trademark law and any future registration. This entry does not
claim exclusivity in generic, descriptive or third-party terms.

### BI-008 — ASET-specific technical know-how

Pre-existing know-how concerning canonical accountability semantics, authority-bound state
transitions, conformance design, recovery, replay, composition profiles and PostgreSQL/Rust
implementation strategy. Abstract ideas are not claimed as copyrighted expression merely by
being listed here; confidential know-how must be protected through access controls and written
agreements.

## 6. Exclusions

This Schedule does not claim ownership of:

- third-party software, standards, publications, trademarks or external projects;
- independently created contributions not assigned or licensed to Dzmitry Prychyna;
- generic ideas, methods or procedures to the extent they are not protected expression;
- foreground intellectual property created under a later written agreement;
- personal data, signatures, employment contracts or confidential evidence kept outside Git;
- work created after the baseline unless separately classified.

The Apache License 2.0 remains unchanged. Public licensing grants permissions; it does not by
itself transfer authorship or ownership of the underlying Background IP.

## 7. Brazilian profile

For Brazil, this Schedule distinguishes the author (`autor`) from the holder of economic rights
(`titular dos direitos patrimoniais`). On the effective date both are declared to be Dzmitry
Prychyna; Attractor Set is his pseudonym.

The public inventory is intended to support, but not replace:

- optional software registration before the Brazilian National Institute of Industrial Property
  (`INPI`);
- a future written assignment to a Brazilian company;
- an annex identifying pre-existing intellectual property in an `Acordo de Parceria para PD&I`;
- separate contractual treatment of foreground intellectual property, publications,
  confidentiality, licensing and commercialization.

Relevant frameworks include Lei nº 9.609/1998, Lei nº 9.610/1998, Lei nº 10.973/2004 and
Decreto nº 9.283/2018. Legal review is required before a specific investment, assignment,
university partnership or commercialization agreement.

See [`BACKGROUND_IP_SCHEDULE.pt-BR.md`](BACKGROUND_IP_SCHEDULE.pt-BR.md) for the Brazilian
Portuguese edition and [`governance/ip/README.md`](governance/ip/README.md) for machine-readable
and operational details.

## 8. Future company, laboratory and university projects

Every later agreement involving ASET should:

1. incorporate this Schedule and its exact baseline commit by reference;
2. state that the Background IP remains with Dzmitry Prychyna unless expressly assigned;
3. define project foreground IP separately;
4. define publication, confidentiality, licensing and commercialization rights;
5. identify contributions and their authors or rightsholders;
6. avoid any implied assignment of the Background IP;
7. require an amended Schedule when new assets are intentionally reclassified as Background IP.

## 9. Amendments and preservation

An amendment must use a new version, preserve earlier versions, identify its cutoff commit and
manifest, describe additions or reclassifications, and pass the repository production gate.
Earlier versions must not be silently rewritten.

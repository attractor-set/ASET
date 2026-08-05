# Governance

ASET uses owner-led, specification-first governance with protected `main` and protected release tags.

## Normative change process

A normative change requires:

1. a machine-readable proposal;
2. semantic-difference classification;
3. schema and constraint updates;
4. executable conformance cases where semantics change;
5. regenerated official editions;
6. deterministic snapshot construction;
7. black-box documentation audit;
8. independent review for a release candidate;
9. a new immutable release.

Every mandatory release gate is fail-closed. Missing evidence is failure, not waiver.

Frozen release bytes are never rewritten. Experimental work belongs outside frozen release directories.

## Creator and public project identity

ASET was independently created by **Dzmitry Prychyna**, who uses **Attractor Set** as a public pseudonym and project identity. Attractor Set is not represented as a separate legal entity.

The machine-readable project metadata must preserve this distinction:

- creator and current claimed rights holder: Dzmitry Prychyna;
- alternate public name: Attractor Set;
- repository and publication identity: `attractor-set/ASET`.

## Background intellectual property

The public boundary of intellectual assets existing before later employment, investment, university, grant-funded or commercial arrangements is maintained in:

- [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md);
- [`BACKGROUND_IP_SCHEDULE.ru.md`](BACKGROUND_IP_SCHEDULE.ru.md);
- [`BACKGROUND_IP_SCHEDULE.pt-BR.md`](BACKGROUND_IP_SCHEDULE.pt-BR.md);
- [`governance/ip/background-ip-schedule.json`](governance/ip/background-ip-schedule.json).

The Schedule is an evidentiary inventory. It does not replace an assignment, INPI registration, trademark registration or transaction-specific legal review. The Apache 2.0 licence remains unchanged.

## Contributions and foreground IP

A contribution is not automatically reclassified as the creator's Background IP. Contributions remain subject to their applicable copyright and the repository licence unless an express written instrument provides otherwise.

A university, grant, employment, contractor or commercial project must define separately:

- pre-existing Background IP;
- project foreground intellectual property;
- contributor and institutional rights;
- publication and confidentiality rules;
- licensing, commercialization and transfer rights.

## Brazil-specific partnership boundary

For a Brazilian `Acordo de Parceria para PD&I` or equivalent instrument, the Background IP Schedule should be incorporated as an annex identifying `Propriedade Intelectual Preexistente`. The agreement and its work plan must separately define ownership and exploitation of project results.

No future company, university, laboratory, funder or investor receives the scheduled rights without an express written assignment or licence.

## Schedule amendments

A Background IP Schedule amendment requires a new version, a new cutoff commit and manifest identity, preservation of prior versions, an explicit change record and a passing production gate. Earlier Schedule versions must not be silently rewritten.

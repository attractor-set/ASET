# ASET intellectual-property provenance

This directory contains the machine-readable public inventory supporting the root
Background IP Schedule.

## Files

- `background-ip-schedule.json` — canonical machine-readable inventory for Schedule 1.0.
- `background-ip-schedule.schema.json` — strict JSON Schema.
- [`../../BACKGROUND_IP_SUPPLEMENT_1.md`](../../BACKGROUND_IP_SUPPLEMENT_1.md), [`../../BACKGROUND_IP_SUPPLEMENT_1.ru.md`](../../BACKGROUND_IP_SUPPLEMENT_1.ru.md) and [`../../BACKGROUND_IP_SUPPLEMENT_1.pt-BR.md`](../../BACKGROUND_IP_SUPPLEMENT_1.pt-BR.md) — public human-readable Supplement 1 editions.
- `background-ip-supplement-1.json` — canonical machine-readable projection of Supplement 1.
- `background-ip-supplement.schema.json` — strict Supplement 1 JSON Schema.
- [`../../BACKGROUND_IP_SUPPLEMENT_2.md`](../../BACKGROUND_IP_SUPPLEMENT_2.md), [`../../BACKGROUND_IP_SUPPLEMENT_2.ru.md`](../../BACKGROUND_IP_SUPPLEMENT_2.ru.md) and [`../../BACKGROUND_IP_SUPPLEMENT_2.pt-BR.md`](../../BACKGROUND_IP_SUPPLEMENT_2.pt-BR.md) — public human-readable Supplement 2 editions tied to `seed-0.3.0-alpha.1`.
- `background-ip-supplement-2.json` — canonical machine-readable projection of Supplement 2.
- `background-ip-supplement-2.schema.json` — strict Supplement 2 JSON Schema.

The English, Russian and Brazilian Portuguese Schedule editions are maintained as static
human-readable governance documents. The JSON inventory is the canonical technical projection
for identifiers, baseline hashes, asset classes and declared ownership status.

## Identity boundary

- Legal name and current claimed rights holder: `Dzmitry Prychyna`.
- Public pseudonym and project identity: `Attractor Set`.
- `Attractor Set` is not represented as a separate legal entity.

## Verification

Run repository validation:

```text
python tools/validate_background_ip.py
python tools/validate_background_ip_supplement.py
python tools/validate_background_ip_supplement_2.py
```

In a Git checkout that contains the baseline commit, also run:

```text
python tools/validate_background_ip.py --check-git
python tools/validate_background_ip_supplement.py --check-git --reference-repo /path/to/aset-python-sqlite
python tools/validate_background_ip_supplement_2.py --check-git
```

The Git check verifies baseline-commit reachability, the historical `MANIFEST.json` digest and
presence of every scheduled repository path at the baseline.

## Confidential records

Do not commit identity documents, CPF, addresses, signatures, employment contracts, invoices,
private source archives, legal opinions or assignment instruments. Those records belong in a
controlled confidential annex referenced by contract, not in the public repository.

## Brazil

For Brazilian transactions, use `BACKGROUND_IP_SCHEDULE.pt-BR.md` as the working language
version and attach it to the relevant agreement. It does not replace:

- INPI registration of a sufficiently stable software version;
- a written assignment to a future company;
- an `Acordo de Parceria para PD&I` and its work plan;
- a separate foreground-IP, publication, confidentiality and commercialization clause.

## Background IP Supplement 2

The released ASET Seed 0.3.0-alpha.1 state is recorded by the append-only Background IP Supplement 2 evidence set:

- `BACKGROUND_IP_SUPPLEMENT_2.md`
- `BACKGROUND_IP_SUPPLEMENT_2.pt-BR.md`
- `BACKGROUND_IP_SUPPLEMENT_2.ru.md`
- `background-ip-supplement-2.json`
- `background-ip-supplement-2.schema.json`
- `validate_background_ip_supplement_2.py`

Supplement 2 extends the evidentiary provenance chain without rewriting the Background IP Schedule or Supplement 1.


# ASET intellectual-property provenance

This directory contains the machine-readable public inventory supporting the root
Background IP Schedule.

## Files

- `background-ip-schedule.json` — canonical machine-readable inventory for Schedule 1.0.
- `background-ip-schedule.schema.json` — strict JSON Schema.

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
```

In a Git checkout that contains the baseline commit, also run:

```text
python tools/validate_background_ip.py --check-git
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

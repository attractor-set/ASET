# Contributing

Contributions are accepted through reviewed pull requests.

Before submitting:

```text
python tools/generate_repository_views.py
python tools/generate_repository_views.py --check
python tools/validate_repository.py
python -m pytest -q
```

Normative changes must include:

- stable identifiers;
- machine-readable semantics;
- updated constraints;
- positive and negative examples;
- all three language forms;
- a semantic-change explanation.

Do not edit generated views, including `docs/generated/`, `codemeta.json` and `.github/repository-metadata.json`, manually.
Do not modify files below a frozen release directory.

## Intellectual-property provenance

The pre-existing ASET boundary is recorded in [`BACKGROUND_IP_SCHEDULE.md`](BACKGROUND_IP_SCHEDULE.md). New contributions are not automatically added to that Background IP inventory.

A contributor must have the right to submit the contribution and must not include employer, client or third-party confidential material. Contributions are accepted under the repository's Apache 2.0 licence unless a separate written agreement applies. Project-specific ownership, assignment or university foreground-IP terms must be handled outside the pull request and referenced explicitly.

Do not commit personal identifiers, signatures, employment contracts, private assignment instruments or confidential evidence.

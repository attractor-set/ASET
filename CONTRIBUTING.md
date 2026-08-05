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

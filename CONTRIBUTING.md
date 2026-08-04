# Contributing

Contributions are accepted through reviewed pull requests.

Before submitting:

```text
python tools/generate_editions.py --check
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

Do not edit files below `docs/generated/` manually.
Do not modify files below a frozen release directory.

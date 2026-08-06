# Generated repository views

Files under this directory are deterministic derived representations.
They must not be edited manually.

The generated language editions are derived from the normative machine canons.
Project discovery metadata is derived from `metadata/project.json` into
`codemeta.json` and `.github/repository-metadata.json`.

Regenerate every derived repository view with:

```text
python tools/generate_repository_views.py
```

Check committed parity without changing files with:

```text
python tools/generate_repository_views.py --check
```

ASET Seed 0.2 alpha 2 is the active resolution-core candidate.
Historical Seed files remain immutable migration evidence; legacy component material is externalized.

# ASET Seed Compatibility Standard

ASET Seed releases can be declared immutable, versioned compatibility standards for implementation conformance.

The standard does not give any implementation semantic precedence. Its normative behavior is the exact machine-readable canon identified by a Seed release tag, release commit and `CANON_PACKAGE.json` package digest. The compatibility layer binds that immutable canon to the official implementation-conformance protocol and mandatory conformance cases.

The first declared compatibility baseline is `seed-0.3.0-alpha.2`. Its semantic baseline remains `0.3.0-alpha.1`; the alpha.2 release incorporates a conformance erratum without changing Seed semantics.

## Exact release identity

A compatibility-standard release is identified by all of the following:

- `standard_series_id`;
- exact Seed release tag;
- exact release commit;
- Seed semantic version;
- canon ID and canon version;
- canonical package digest;
- conformance protocol ID;
- conformance-profile digest;
- mandatory case count.

Changing any bound release identity creates a different compatibility target. Existing release tags and compatibility identities are never moved or rewritten.

## Conformance claim

An implementation may claim conformance to one exact ASET Seed Compatibility Standard release only when an external ASET conformance runner verifies every mandatory case for that release. The implementation adapter does not determine its own PASS/FAIL verdict and has `implementation_precedence=NONE`.

Implementation versioning is independent from Seed release versioning.

## Conformance Kit

`tools/build_seed_conformance_kit.py` builds a deterministic release-bound kit containing:

- every file listed by the release's exact `CANON_PACKAGE.json`;
- the ASET external implementation-conformance runner;
- the Seed resolution oracle as a reference assurance artifact;
- generated immutable release identity (`STANDARD.json`);
- a deterministic kit manifest and usage README.

Distribution metadata does not replace or amend the Seed canon. The exact release canon remains normative.

For a published release tag:

```text
python tools/build_seed_conformance_kit.py \
  --ref seed-0.3.0-alpha.2 \
  --output-dir dist/seed-compatibility \
  --verify-determinism \
  --require-release-tag
```

The resulting ZIP, SHA-256 file, manifest and compatibility-standard identity are suitable as GitHub Release assets and as a stable CI input for independent implementations.

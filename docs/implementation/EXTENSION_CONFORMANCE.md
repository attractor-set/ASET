# External extension conformance

ASET Seed owns `ASET-SEED-EXTENSION-CONFORMANCE-V1`. A separately versioned
extension does not become conformant merely by naming a Seed version in its README or
by comparing two local metadata files.

An extension repository MUST:

1. pin the exact Seed canon identifier, version, package-file digest, package-internal
   digest, and immutable repository ref in `upstream/ASET_SEED_BINDING.json`;
2. include that binding and `upstream/SEED_EXTENSION_CONFORMANCE.json` in its canon
   package;
3. map every Seed boundary role to a content-addressed portable extension case;
4. expose the `describe`, `execute_case`, and `execute_cases` adapter operations;
5. run the Seed-owned external verifier from the pinned Seed checkout.

The verifier checks package integrity, exact upstream identity, deterministic replay, the
extension's own expected result, and the normalized Seed boundary result. The mandatory
roles cover unresolved input, local ACCEPT, local DENY, rejection of a pre-resolution boundary bypass, enforcement mismatch, exact-binding mismatch, and non-local authority.

Example from an extension checkout:

```bash
python .upstream/aset/tools/run_external_extension_conformance.py \
  --canon-root .upstream/aset \
  --extension-root . \
  --adapter "python tools/seed_extension_adapter.py" \
  --output dist/seed-extension-conformance.json
```

A PASS is bounded evidence for the listed boundary roles. It is not a proof of complete
extension semantics, production security, external truth, or unbounded formal refinement.

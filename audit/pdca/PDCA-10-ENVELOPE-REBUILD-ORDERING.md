# PDCA-10 — Release-envelope rebuild ordering correction

## Plan / black-box input

The mandatory Ruff gate correctly rejected the initial rc12 candidate. The first corrective cycle then changed four runtime source files and rebuilt `MANIFEST.json`, but it did not regenerate the rc12 release envelope before running the production gate. From the gate boundary the candidate therefore appeared internally inconsistent: the envelope still contained the pre-lint runtime digests while the runtime source had changed.

Success criteria:

1. preserve the exact frozen rc11 subtree;
2. accept only the known dirty candidate scope;
3. require the pinned Ruff gate to pass before any release metadata is rebuilt;
4. rebuild the rc12 envelope after every source mutation that it hashes;
5. rebuild the repository manifest after the envelope and audit records;
6. pass the complete production gate, whose final steps are documentation, runtime, and adversarial black-box audits;
7. create no commit unless every gate passes.

## Do

- Kept the seven lint corrections from PDCA-09 unchanged.
- Added this corrective record and `RC12-AUD-014`.
- Regenerated `seed/canonical/release/RC12_RELEASE_CANDIDATE.json` from the corrected runtime bytes.
- Regenerated `MANIFEST.json` only after the release envelope and audit records were final.
- Made the resume script idempotent for both the pre-PDCA-10 and partially applied PDCA-10 dirty states.

## Check

Required order:

```text
source correction
→ Ruff PASS
→ release envelope build
→ release envelope check
→ repository manifest build
→ repository manifest check
→ complete production gate
→ final documentation black-box audit
→ final runtime black-box audit
→ adversarial black-box audit
```

The complete production gate remains authoritative. A passing local envelope or manifest check alone is not a release result.

## Act / next-cycle input

Release metadata generation order is now an explicit invariant of the corrective workflow. Any later source mutation that changes a release-envelope input must invalidate and regenerate the envelope before the manifest is rebuilt. The final black-box reports from the complete production gate become the next PDCA input.

# Publication provenance

The public assurance corpus is derived from the completed v60 semantic
minimality/falsification program whose full TLAPS regression proved
**2257/2257 obligations**.

Publication removes legacy material that is not needed to reproduce the final
result:

- failed proof-attempt analyses from earlier iterations;
- version-by-version preflight reports;
- retired/experimental models;
- iteration-specific adversarial helper scripts.

All 34 active TLA+ modules are retained. Publication edits inside those modules
are restricted to comments/status wording. `PUBLICATION_BASELINE.json` records:

- source-v60 SHA-256 for every active module;
- published SHA-256;
- a comment-stripped SHA-256 that must be identical between the source v60 and
  the published module.

This makes the cleanup auditable while keeping the public files readable.
The formal gate then replays all 20 proof modules rather than relying on the
normalization check as proof evidence.

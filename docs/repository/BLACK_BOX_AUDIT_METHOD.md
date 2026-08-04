
# Black-box documentation audit method

The black-box auditor receives only the built repository snapshot and external expected anchors. It does not import repository validation modules and does not trust generated internal pass reports.

The audit independently checks:

- ZIP path safety, duplicate entries and CRC;
- exact manifest scope, file sizes and SHA-256 digests;
- full Apache-2.0 license and citation URL;
- public repository status and assurance boundaries;
- frozen rc11 bundle identity;
- byte-exact rc11 expanded tree materialization;
- strict JSON parsing with duplicate-member rejection;
- generated language edition status, version, canonical digest and semantic-ID parity;
- foreign-term policy;
- rc11 requirements, verification and traceability set identity;
- Python syntax of tracked tools and tests;
- local Markdown-link resolution;
- common secret and private-key patterns;
- mandatory production-readiness documents and release gates;
- absence of unresolved blocking audit findings.

The auditor emits machine-readable JSON and a concise Markdown report. Any mandatory failure produces a nonzero result. A separate adversarial runner mutates the snapshot while rebuilding its manifest and verifies that the auditor rejects required-document removal, generated-edition drift, frozen rc11 drift, secret insertion, runtime overclaim, and an open blocking finding.

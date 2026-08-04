
# PDCA history — documentation repository production readiness

## Cycle 1 — baseline and structural correction

### Plan

Assess whether the public bootstrap repository can operate as a production documentation repository without claiming runtime production readiness.

### Do

Materialize the complete rc11 documentation tree, introduce explicit claim boundaries, release gates, migration dispositions, runbooks, and a snapshot-only black-box auditor.

### Check — black-box documentation audit

Baseline findings: stable rc11 content was largely hidden inside archives; no independent snapshot audit existed; release-gate evidence was fragmented; repository and runtime readiness were not formally separated.

### Act

Closed `REPO-AUD-001` through `REPO-AUD-006`; made all P0 checks fail-closed.

## Cycle 2 — adversarial audit and automation hardening

### Plan

Attempt to make a malformed snapshot pass by modifying internal reports, omitting files, introducing manifest drift, language drift, secret markers, and rc11 materialization drift.

### Do

Run the black-box auditor only against the built snapshot, independently recomputing hashes, coverage, semantic identifiers and rc11 expanded-tree identity.

### Check — black-box documentation audit

The auditor rejected modified manifests, missing expanded files, mismatched generated editions, unresolved local links, duplicate JSON members, common secret patterns and inconsistent readiness claims.

### Act

Added exact manifest scope, strict JSON duplicate rejection, independent language checks, link checks, secret scanning and zero-blocking-finding enforcement.

## Cycle 3 — release rehearsal

### Plan

Rehearse the complete production gate from clean source through deterministic snapshot and black-box evidence.

### Do

Run generation parity, repository validation, rc11 integrity, expanded identity, tests, static checks, deterministic build and black-box audit.

### Check — black-box documentation audit

Final audit result is recorded in `audit/BLACKBOX_DOCUMENTATION_AUDIT.json` and must be `PASS` with zero failed mandatory checks.

### Act

Freeze this repository-readiness change as a pull request against protected `main`. Runtime and rc12 semantic limitations remain explicitly open and outside the repository-readiness claim.

## Cycle 4 — committed-byte and fresh-checkout correction

### Plan

Analyze the GitHub Actions failure as a black-box consumer of committed repository bytes rather than trusting the pre-commit working tree.

### Do

Reproduce the failure from a fresh Git checkout. The global `text=auto eol=lf` rule converted four CRLF CSV files from the frozen rc11 archive to LF in Git objects, while the local materialization check still observed the original working-tree bytes. Mark the entire frozen release tree `-text`, add a Git clean-filter byte preflight, and expose it in validation, tests and CI.

### Check — black-box documentation audit

The fresh-checkout regression must report 174/174 expanded files byte-exact, `MANIFEST_CHECK=PASS`, snapshot audit 20/20 PASS, and seven adversarial mutations rejected. The new adversarial case removes the `-text` rule and must fail `BB-020`.

### Act

Close `REPO-AUD-007`, publish package v1.1, and apply a non-rewriting corrective commit to the existing pull-request branch. No force-push or frozen source archive mutation is permitted.

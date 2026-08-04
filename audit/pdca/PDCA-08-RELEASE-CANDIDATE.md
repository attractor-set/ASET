# PDCA-08 — deterministic rc12 release candidate

## Plan

Bind the complete canon, protocol schemas, runtime source, bounded claim, and mandatory gates into one deterministic candidate. A merge is allowed only after real SHACL, Ruff, wheel installation, regression, model, and black-box gates pass in the target environment.

## Do

Added the rc12 release envelope, deterministic manifest and snapshot construction, wheel build and isolated install verification, published dependency pins, least-privilege CI, production-gate orchestration, deployment checklist, threat model, and exact audit evidence outputs.

## Check

Local environment-independent checks passed: canon 27/40/37/18, migration 83/83, schemas 39/39, conformance 55/55, branch guards 252/252, model 281/832, tests 30/30, and core branch coverage 90.570720%. Real PySHACL and Ruff remain mandatory apply/CI gates when their packages are available.

## Act

Classified the result as `RC12_RELEASE_CANDIDATE_READY`, not as a frozen stable release or external certification. The apply script refuses to commit unless all nineteen gates pass against the exact target repository.

## Final black-box analysis and audit for the next cycle

The final snapshot-only documentation audit, runtime audit, and adversarial audit must all pass after the last manifest rebuild. Their machine reports are release evidence. Any failed check opens the next PDCA cycle; a clean result permits the protected-branch pull request and subsequent independent third-party audit.

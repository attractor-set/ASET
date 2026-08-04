# ASET Seed 0.1-rc11

Complete pre-freeze candidate package for the ASET Seed constitutional reference monitor.

## Execute

```bash
python conformance/run_conformance.py
python audit/run_independent_reaudit.py
python audit/run_blackbox_audit.py
python tests/run_branch_suite.py
```

Coverage evidence is in `validation/coverage.json` and is bound to exact source/test/schema/case hashes by `validation/coverage_bindings.json`. Production status is HOLD; external third-party audit is pending.

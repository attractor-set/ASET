
# ASET Seed 0.1-rc11

Status: immutable frozen historical release; independent final audit `PASS_WITH_LIMITATIONS`; production runtime `HOLD`.

## Representations

- `delivery/` — complete immutable release bundle and checksum;
- `materialized/` — principal publication and audit files extracted for convenience;
- `expanded/` — byte-exact expansion of `ASET-Seed-Documentation-v0.1-rc11.zip`, verified by `tools/materialize_rc11.py --check`.

The expanded tree improves reviewability but does not create a new release. Any byte mismatch against the frozen documentation archive is a release-integrity failure.

Start with [`expanded/docs/ASET_SEED_SPECIFICATION.md`](expanded/docs/ASET_SEED_SPECIFICATION.md).

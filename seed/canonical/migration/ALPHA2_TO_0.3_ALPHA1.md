# Migration from Seed 0.2 alpha 2 to Seed 0.3 alpha 1

This migration is intentionally breaking.

| 0.2 concept | 0.3 concept |
|---|---|
| `status = UNKNOWN` and `enforcement = BLOCKED` | derived `resolution = UNKNOWN` |
| `status = ACCEPT` and `enforcement = ALLOW` | terminal `resolution = ALLOW` |
| `status = DENY` and `enforcement = BLOCKED` | terminal `resolution = BLOCK` |
| mutable current Authority and escalation chain | exact-binding Authority recognition plus optional opaque evidence references |
| open/escalate/resolve workflow state | append-only request and terminal-record store |

A 0.2 implementation cannot claim 0.3 conformance by renaming fields. It must implement the 0.3 exact-binding, local exact-binding Authority recognition, terminal uniqueness and fail-closed evaluation rules.

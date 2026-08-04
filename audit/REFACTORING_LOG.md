# rc12 refactoring log

The refactoring rule for rc12 was surgical: preserve audited semantics, remove only complexity introduced by the new candidate, and bind every change to a regression check.

| Refactoring | Reason | Verification |
|---|---|---|
| Reused the audited rc11 semantic engine instead of rewriting transition logic | Minimize semantic drift and implementation surface | 55/55 conformance vectors and 252/252 branch guards |
| Added public `validate_transition` instead of calling a private schema helper from the store | Reduce cross-module coupling | runtime integration tests and static API check |
| Returned the existing state from the initialization transaction | Remove a nested database connection and preserve one serialization boundary | idempotent initialization regression |
| Centralized strict JSON loading and canonical output | Avoid duplicate parsers and inconsistent duplicate-key behavior | duplicate-member and CLI tests |
| Kept proof verification behind one small protocol | Default fail-closed behavior without speculative plugin architecture | reject-all, HMAC success, and wrong-proof tests |
| Used one SQLite store and one hash-chained attempt ledger | Avoid a second datastore or message broker | reopen, concurrency, chain, and backup tests |
| Refused backup overwrite and validated copied database integrity | Turn ambiguous operator behavior into fail-closed behavior | backup regression tests |
| Enforced private POSIX modes for local secrets, databases, and backups | Prevent silent local disclosure in the bounded deployment profile | CLI security tests |
| Cross-checked audit result columns, revision count, and persisted state root | Prevent tampering with redundant audit fields or detaching the ledger from current state | audit tampering and revision-binding tests |
| Excluded build, coverage, cache, and packaging artifacts from release scope | Keep snapshots reproducible | deterministic manifest and black-box archive checks |
| Reduced the build backend to pinned setuptools and corrected CI tool pins | Remove an unnecessary build dependency and prevent an impossible install gate | package metadata check and target CI install |
| Centralized stable runtime rejections in `_rejection` | Remove repeated result dictionaries without changing admission semantics | hostile boundary unit and black-box tests |
| Reused `_decode_stored_state` across read, initialize, execute, health, and backup | One validation rule is easier to audit than five divergent paths | corrupt-state regression and mutation tests |
| Kept the proof boundary to reject-all plus one exact-content HMAC profile | Remove unsafe and redundant authorization surface | modified-after-proof regression and black-box mutation |
| Reused health as the backup admission gate | Avoid a second partial backup-validation implementation | corrupt-state backup rejection and restored-backup health |

No frozen rc11 file is changed by these refactorings.

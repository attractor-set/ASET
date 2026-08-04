# Partition and reconciliation

Guarantee suspension is branch-local. A suspended branch may record only preclassified local commits. Reconciliation validates commit IDs, parents, operation class, signer and proof; requires every known commit; accepts at most a valid prefix; and preserves competing descendants as persistent fork evidence.

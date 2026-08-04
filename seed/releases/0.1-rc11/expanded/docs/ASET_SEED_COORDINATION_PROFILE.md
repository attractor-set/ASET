# Coordination profile

Partitioned branches are classified by Constitution as `MONOTONE_LOCAL`, `INVARIANT_CONFLUENT` or `COORDINATION_REQUIRED`. Unknown classes fail closed. Ordinary transitions are forbidden in a `SUSPENDED` Context; only `PARTITION_LOCAL_TRANSITION` rechecks the declared class and proof. Reconciliation begins from the last confirmed export root, preserves fork evidence and requires completeness with respect to every known local commit.

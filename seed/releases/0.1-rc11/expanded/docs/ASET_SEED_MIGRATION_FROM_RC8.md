# Migration to rc11

rc11 preserves rc8/rc9 authority, Permit, evidence, partition and causal semantics while replacing mutable-Amendment plebiscite governance. The incomplete rc10 draft introduced withdrawal/redefinition but used destructive pending withdrawals. rc11 removes that intermediate state.

Migration mapping:

- `AMENDMENT` and vote receipts: removed.
- `CUT` and recursive pruning: removed.
- proposal-bound pending withdrawal: removed.
- member consent: inline authorization inside atomic `CONTEXT_REDEFINE`.
- voluntary exit: standalone `MEMBERSHIP_WITHDRAW`.
- root Constitution change: new Genesis only.

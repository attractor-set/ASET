# Terminal commitment accumulation

ASET Seed intentionally separates **semantic recognition** from **historical retention**.

A reconsideration request carries `previous_terminal_record_digest`. The digest identifies an immutable terminal-resolution fact. Seed requires that the commitment be recognized, but it does not require the predecessor request or record to remain in the active store.

## Bounded hot buffer + authenticated accumulator

A scalable implementation may maintain:

- `B`: a hot buffer containing at most `N` recent terminal-record digests;
- `A`: profile-specific authenticated accumulator state;
- external proof material sufficient to establish membership of compacted commitments when needed.

Conceptually:

```text
new terminal ResolutionRecord
          |
          v
   record_digest = c
          |
          v
      append to B
          |
     |B| reaches N
          |
          v
 compact completed block
          |
          v
      A' = Add(A, block)
      B' = empty
```

Recognition of `previous_terminal_record_digest = c` is then established either because `c` is still in the hot buffer/current retained records, or because the selected accumulator profile verifies a witness for `c` against `A`.

## Why the accumulator is not normative Seed

Different authenticated structures make different trade-offs:

- a balanced Merkle structure commonly gives `O(log n)` membership proofs;
- an MMR supports append-oriented histories while retaining a logarithmic frontier;
- some accumulators can expose constant-size commitments/witnesses but rely on stronger cryptographic assumptions;
- recursive proof systems can move more state and computation outside the kernel.

Hard-coding one of these would make a cryptographic/storage choice normative. Seed instead exposes one semantic boundary: **recognized terminal commitment**.

## About the `N + 1` bound

`N` hot commitments plus one root is an attractive implementation target, but it is not true for every Merkle-style construction without additional external state. A root alone generally does not contain enough information to reconstruct arbitrary future membership proofs or, for some append constructions, to update the root efficiently.

A profile may still achieve an `N + 1` kernel-retained digest bound if required frontier/history/witness material is external and the kernel can validate the supplied update or membership proof. Otherwise the retained accumulator frontier may be `O(log n)`.

Therefore the portable claim is:

```text
Seed semantic history retention: not required
hot state: bounded by profile
accumulator retained state: O(1) or O(log n), depending on profile
membership proof: supplied/maintained outside Seed
```

This preserves the minimal Seed role while allowing long-lived deployments to avoid linear growth of canonical state.

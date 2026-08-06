# PDCA-17 — Seed invariant closure

## Plan

Close every normative requirement, safety invariant and transition of the
minimal Seed kernel without adding workflow, enforcement, federation or storage
semantics.

## Do

The candidate now contains a normative coverage matrix, a 15-property bounded
formal projection, four exact executable/static properties, three additional
adversarial vectors and thirteen semantic mutations.

## Check

The release evidence must report:

```text
requirements = 12/12
invariants = 12/12
transitions = 3/3
semantic mutations killed = 13/13
semantic mutation survivors = 0
```

TLC remains an independent mandatory release gate. Unbounded TLAPS proof is not
claimed by this cycle.

## Act

The safety surface is closed. Further work may strengthen proof, test diversity
or documentation, but must not add new Seed semantics without a separately
classified canon change.

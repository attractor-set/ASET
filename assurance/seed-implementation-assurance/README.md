# Seed implementation recognition assurance

This directory defines a **non-normative, v60-derived black-box assurance profile** for implementations of the frozen ASET Seed.

It does not add requirements to the canonical Seed compatibility standard and it does not change the frozen 25-case normative conformance corpus. A conforming implementation remains defined by the canonical conformance material under `seed/canonical/conformance/`.

The purpose of this additional profile is different: it uses the public v60 recognition-boundary proof as a source of adversarial witness dimensions and checks that an external implementation adapter does not silently collapse Seed-visible recognition distinctions.

The dependency direction is:

```text
frozen Seed canon
    -> public v60 assurance
        -> implementation recognition assurance
            -> external implementation adapter
```

There is no reverse dependency into the frozen canon or into the v60 formal corpus.

## Why this is separate from normative conformance

The normative conformance corpus is intentionally frozen. Retrofitting v60-derived cases into that corpus would silently strengthen the standard after freeze.

Instead, implementations may report two independent results:

```text
IMPLEMENTATION_CONFORMANCE_VERDICT=PASS
SEED_RECOGNITION_ASSURANCE_VERDICT=PASS
```

The first is normative compatibility evidence. The second is additional public assurance evidence.

## Existing adapter protocol is reused

The runner deliberately reuses `ASET-SEED-RESOLUTION-CONFORMANCE-V3` and its three process operations:

- `describe`
- `execute_case`
- `execute_cases`

No internal storage representation is prescribed. The implementation adapter is the witness that projects implementation state into the canonical protocol `final_store` shape.

The generated cases are deterministic and pinned by `GENERATED_CASES_MANIFEST.json`.

## What is checked

The rich witness profile exercises:

- two exact bindings;
- two previous terminal commitments;
- three recognized authority-binding pairs;
- both terminal decisions;
- terminal replay and rewrite behavior;
- exact authority-binding rejection;
- the effective conflict class.

This detects common semantic drift such as dropping a previous commitment, losing terminal authority provenance in the adapter projection, conflating bindings while pending, collapsing ALLOW and BLOCK, or permitting a terminal rewrite.

## Important boundary: conflict provenance

The formal v60 model contains an environment-level `ObserveConflict` action and distinguishes retained-history phases `INVALIDATED_ALLOW` and `INVALIDATED_BLOCK`.

The frozen external implementation protocol does **not** expose `ObserveConflict`. Therefore this profile checks only the protocol-observable effective conflict result (`UNKNOWN`, fail closed). It does not claim that the existing black-box protocol can witness the full invalidated provenance distinction.

A future extension/projection assurance protocol may expose an explicit abstract projection witness for that stronger purpose. It should remain a separate non-normative layer rather than modifying the frozen Seed protocol.

## Usage

First verify that the generated case set has not drifted:

```bash
python tools/build_seed_recognition_assurance_cases.py --check
```

Then run the implementation adapter:

```bash
python tools/run_seed_recognition_assurance.py \
  --adapter "python path/to/seed_adapter.py" \
  --adapter-cwd path/to/implementation \
  --output dist/seed-recognition-assurance.json
```

A successful run reports the generated case total, deterministic replay, exact canonical projection preservation, and:

```text
SEED_RECOGNITION_ASSURANCE_VERDICT=PASS
```

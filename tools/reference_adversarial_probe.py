from __future__ import annotations

import copy

from aset_reference import ReferenceError, ReferenceMachine


def main() -> int:
    machine = ReferenceMachine()
    machine.run("SUCCESS")
    original = machine.snapshot()
    first = original["crossings"][0]
    first_permit = first["permit_id"]
    first_receipt = first["receipt_id"]
    first_resolution = original["permits"][first_permit]["resolution_id"]
    first_patch = first["patch_id"]

    mutations = {
        "CONTEXT_ROOT": lambda item: item["context"].__setitem__("root", "sha256:" + "0" * 64),
        "RESOLUTION_GATE": lambda item: item["resolutions"][first_resolution].__setitem__(
            "gate_id", "GATE-EXPECT-ADMIT"
        ),
        "PERMIT_PATCH_DIGEST": lambda item: item["permits"][first_permit].__setitem__(
            "patch_digest", "sha256:" + "0" * 64
        ),
        "RECEIPT_PATCH_DIGEST": lambda item: item["receipts"][first_receipt].__setitem__(
            "patch_digest", "sha256:" + "0" * 64
        ),
        "RECEIPT_SOURCE_ROOT": lambda item: item["receipts"][first_receipt].__setitem__(
            "source_context_root", "sha256:" + "0" * 64
        ),
        "CROSSING_SOURCE_ROOT": lambda item: item["crossings"][0].__setitem__(
            "source_context_root", "sha256:" + "0" * 64
        ),
        "CONSUMED_SET": lambda item: item.__setitem__("consumed_permit_ids", []),
        "LAST_RECEIPT": lambda item: item.__setitem__("last_receipt_id", "receipt:wrong"),
        "WRITE_SET": lambda item: item["patches"][first_patch]["writes"].pop("CTX-TASK"),
        "MAP_KEY": lambda item: item["permits"].__setitem__(
            "permit:wrong", item["permits"].pop(first_permit)
        ),
    }

    detected = 0
    for name, mutate in mutations.items():
        candidate = copy.deepcopy(original)
        mutate(candidate)
        try:
            ReferenceMachine.restore(candidate)
        except (ReferenceError, ValueError, KeyError):
            print(f"REFERENCE_ADVERSARIAL_{name}=PASS")
            detected += 1
        else:
            print(f"REFERENCE_ADVERSARIAL_{name}=FAIL")
    print(f"REFERENCE_ADVERSARIAL={detected}/{len(mutations)}")
    print("REFERENCE_ADVERSARIAL_VERDICT=" + ("PASS" if detected == len(mutations) else "FAIL"))
    return 0 if detected == len(mutations) else 1


if __name__ == "__main__":
    raise SystemExit(main())

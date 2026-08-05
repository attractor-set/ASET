from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from aset_reference import ReferenceError, ReferenceMachine, run_critical_path
from aset_reference.canonical import domain_digest, freeze_json

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    checks: list[dict[str, str]] = []

    def check(name: str, condition: bool) -> None:
        if not condition:
            raise AssertionError(name)
        checks.append({"id": name, "status": "PASS"})

    results = {
        effect: run_critical_path(effect)
        for effect in ("SUCCESS", "FAILURE", "NO_EFFECT", "UNKNOWN")
    }
    check("REF-CONF-001", results["SUCCESS"].terminal_status == "CLOSED")
    check("REF-CONF-002", results["FAILURE"].terminal_status == "CLOSED")
    check("REF-CONF-003", results["NO_EFFECT"].terminal_status == "CLOSED")
    check("REF-CONF-004", results["UNKNOWN"].terminal_status == "REJECTED")
    check("REF-CONF-005", all(len(result.crossings) == 8 for result in results.values()))
    check("REF-CONF-006", all(len(result.receipts) == 8 for result in results.values()))
    check("REF-CONF-007", results["SUCCESS"].outcome is not None)
    check("REF-CONF-008", results["FAILURE"].outcome is not None)
    check("REF-CONF-009", results["NO_EFFECT"].outcome is not None)
    check("REF-CONF-010", results["UNKNOWN"].outcome is None)
    check("REF-CONF-011", results["UNKNOWN"].verification.payload["status"] == "FAIL")
    check("REF-CONF-012", len({item.permit_id for item in results["SUCCESS"].receipts}) == 8)
    check(
        "REF-CONF-013",
        [item.gate_id for item in results["SUCCESS"].crossings]
        == [
            "GATE-CONTEXT-PROJECT",
            "GATE-EXPECT-ADMIT",
            "GATE-EXEC-BIND",
            "GATE-DISPATCH",
            "GATE-OBSERVE",
            "GATE-EVIDENCE",
            "GATE-ACCEPT",
            "GATE-TASK-CLOSE",
        ],
    )
    previous = None
    for receipt in results["SUCCESS"].receipts:
        if receipt.previous_receipt_id != previous:
            raise AssertionError("REF-CONF-014")
        previous = receipt.receipt_id
    check("REF-CONF-014", True)
    check(
        "REF-CONF-015",
        domain_digest("nfc", {"x": "é"}) == domain_digest("nfc", {"x": "e\u0301"}),
    )
    try:
        freeze_json({"x": 1.5})
    except ValueError:
        check("REF-CONF-016", True)
    else:
        check("REF-CONF-016", False)
    try:
        freeze_json({"é": 1, "e\u0301": 2})
    except ValueError:
        check("REF-CONF-017", True)
    else:
        check("REF-CONF-017", False)

    machine = ReferenceMachine()
    patch = machine._patch(
        "ContextProjectionPatch",
        "GATE-CONTEXT-PROJECT",
        {"CTX-MEM": {}, "CTX-TASK": {"status": "PROJECTED"}},
    )
    resolution, permit = machine.authorize(patch)
    machine.cross(patch, resolution, permit)
    try:
        machine.cross(patch, resolution, permit)
    except ReferenceError as exc:
        check("REF-CONF-018", str(exc) == "PERMIT_ALREADY_CONSUMED")
    else:
        check("REF-CONF-018", False)

    restored_source = ReferenceMachine()
    restored_source.run("SUCCESS")
    snapshot = restored_source.snapshot()
    check("REF-CONF-019", ReferenceMachine.restore(snapshot).snapshot() == snapshot)

    mutations = (
        ("REF-CONF-020", "context", "root"),
        ("REF-CONF-021", "resolution", "gate_id"),
        ("REF-CONF-022", "permit", "patch_digest"),
        ("REF-CONF-023", "receipt", "patch_digest"),
        ("REF-CONF-024", "crossing", "source_context_root"),
        ("REF-CONF-025", "top", "consumed_permit_ids"),
        ("REF-CONF-026", "top", "last_receipt_id"),
    )
    first = snapshot["crossings"][0]
    for case_id, target, field in mutations:
        candidate = copy.deepcopy(snapshot)
        if target == "context":
            candidate["context"][field] = "sha256:" + "0" * 64
        elif target == "resolution":
            permit_id = first["permit_id"]
            resolution_id = candidate["permits"][permit_id]["resolution_id"]
            candidate["resolutions"][resolution_id][field] = "GATE-EXPECT-ADMIT"
        elif target == "permit":
            candidate["permits"][first["permit_id"]][field] = "sha256:" + "0" * 64
        elif target == "receipt":
            candidate["receipts"][first["receipt_id"]][field] = "sha256:" + "0" * 64
        elif target == "crossing":
            candidate["crossings"][0][field] = "sha256:" + "0" * 64
        elif field == "consumed_permit_ids":
            candidate[field] = []
        else:
            candidate[field] = "receipt:wrong"
        try:
            ReferenceMachine.restore(candidate)
        except ReferenceError:
            check(case_id, True)
        else:
            check(case_id, False)

    report = {
        "document_type": "aset-reference-conformance-results",
        "version": 1,
        "checks": checks,
        "checks_passed": len(checks),
        "checks_total": 26,
        "verdict": "PASS" if len(checks) == 26 else "FAIL",
    }
    if args.output:
        path = ROOT / args.output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"REFERENCE_CONFORMANCE={len(checks)}/26")
    print(f"REFERENCE_CONFORMANCE_VERDICT={report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

import json
from pathlib import Path

from aset_reference import ReferenceMachine
from aset_reference.canonical import canonical_json

ROOT = Path(__file__).resolve().parents[2]
VECTOR = ROOT / "test-vectors/reference/full-critical-path-success.json"


def test_portable_success_vector():
    expected = json.loads(VECTOR.read_text(encoding="utf-8"))
    machine = ReferenceMachine()
    result = machine.run("SUCCESS")
    snapshot = machine.snapshot()
    assert result.final_context.root == expected["expected_final_context_root"]
    assert result.outcome is not None
    assert result.outcome.artifact_id == expected["expected_outcome_id"]
    assert [item.receipt_id for item in result.receipts] == expected["expected_receipt_ids"]
    assert canonical_json(snapshot).hex() == expected["snapshot_canonical_hex"]

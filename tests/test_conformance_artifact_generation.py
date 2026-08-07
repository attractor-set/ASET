from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

from tools.seed_resolution_oracle import execute_case
from tools.validate_seed_canon import validate_postconditions

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "seed/canonical/conformance/cases/positive/RES-POS-007.json"


def load_case() -> dict[str, object]:
    value = json.loads(CASE.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_res_pos_007_idempotent_replay_postcondition_matches_final_store() -> None:
    case = load_case()
    actual, final_store = execute_case(case)
    assert actual["code"] == "IDEMPOTENT_REPLAY"
    assert actual["state_changed"] is False
    errors: list[str] = []
    validate_postconditions(errors, "RES-POS-007", case, final_store)
    assert errors == []


def test_postcondition_guard_detects_the_published_res_pos_007_defect() -> None:
    case = copy.deepcopy(load_case())
    case["postconditions"][0]["equals"] = (
        "sha256:036914e827dcd520081da16232f409942e0f768d343b44e03079f2f73f749ae8"
    )
    _, final_store = execute_case(case)
    errors: list[str] = []
    validate_postconditions(errors, "RES-POS-007", case, final_store)
    assert errors == [
        "case_postcondition:RES-POS-007:/records/0/record_digest:value_mismatch"
    ]


def test_conformance_profile_is_generated_from_case_files() -> None:
    result = subprocess.run(
        [sys.executable, "tools/build_conformance_profile.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "CONFORMANCE_PROFILE_PARITY=PASS" in result.stdout

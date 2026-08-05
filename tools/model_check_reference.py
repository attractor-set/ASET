from __future__ import annotations

import argparse
import json
from pathlib import Path

from aset_reference import EFFECT_CLASSES, GATE_WRITES, run_critical_path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    terminal: dict[str, str] = {}
    crossings = 0
    for effect_class in EFFECT_CLASSES:
        result = run_critical_path(effect_class)
        if len(result.crossings) != len(GATE_WRITES):
            raise AssertionError(effect_class)
        if result.final_context.version != len(GATE_WRITES):
            raise AssertionError(effect_class)
        if result.outcome is not None and result.verification.payload["status"] != "PASS":
            raise AssertionError("OUTCOME_WITHOUT_PASS_VERIFICATION")
        if effect_class == "UNKNOWN" and result.outcome is not None:
            raise AssertionError("UNKNOWN_OUTCOME_FORBIDDEN")
        terminal[effect_class] = result.terminal_status
        crossings += len(result.crossings)

    report = {
        "document_type": "aset-reference-bounded-model-check",
        "version": 1,
        "effect_classes": len(EFFECT_CLASSES),
        "crossings": crossings,
        "terminal_states": terminal,
        "verdict": "PASS",
    }
    if args.output:
        path = ROOT / args.output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(f"REFERENCE_MODEL_EFFECT_CLASSES={len(EFFECT_CLASSES)}")
    print(f"REFERENCE_MODEL_CROSSINGS={crossings}")
    print("REFERENCE_MODEL_CHECK=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

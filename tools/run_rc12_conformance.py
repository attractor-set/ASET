from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from aset_seed import core  # noqa: E402

PROFILE = ROOT / "seed/canonical/conformance/conformance-profile.json"


def strict_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict_object)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    profile = load(PROFILE)
    rows = []
    for item in profile["cases"]:
        path = ROOT / item["path"]
        case = load(path)
        ok, actual, expected = core.validate_case(copy.deepcopy(case))
        rows.append(
            {
                "case_id": case["case_id"],
                "path": item["path"],
                "pass": bool(ok),
                "actual": actual,
                "expected": expected,
            }
        )
    report = {
        "document_type": "aset-seed-rc12-conformance-results",
        "implementation_version": core.IMPLEMENTATION_VERSION,
        "wire_version": core.VERSION,
        "seed_semantics_id": core.SEED_SEMANTICS_ID,
        "cases_total": len(rows),
        "cases_passed": sum(row["pass"] for row in rows),
        "pass": all(row["pass"] for row in rows),
        "results": rows,
    }
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    print(f"RC12_CONFORMANCE={report['cases_passed']}/{report['cases_total']}")
    print(f"RC12_CONFORMANCE_VERDICT={'PASS' if report['pass'] else 'FAIL'}")
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

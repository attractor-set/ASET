#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from typing import Any

try:
    from tools.seed_resolution_oracle import execute_case
except ModuleNotFoundError:
    from seed_resolution_oracle import execute_case

PROTOCOL = "ASET-SEED-RESOLUTION-CONFORMANCE-V3"


def result(case: dict[str, Any]) -> dict[str, Any]:
    actual, final_store = execute_case(case)
    return {
        "protocol": PROTOCOL,
        "case_id": case["case_id"],
        "actual": actual,
        "final_store": final_store,
    }


def main() -> int:
    request = json.loads(sys.stdin.read())
    if request.get("protocol") != PROTOCOL:
        raise ValueError("unsupported protocol")
    operation = request.get("operation")
    if operation == "describe":
        response = {
            "protocol": PROTOCOL,
            "implementation": {
                "profile_id": "ASET-CANONICAL-ORACLE-TEST-ADAPTER-V1",
                "normative": False,
            },
            "supported_operations": ["describe", "execute_case", "execute_cases"],
        }
    elif operation == "execute_case":
        response = result(request["case"])
    elif operation == "execute_cases":
        response = {
            "protocol": PROTOCOL,
            "results": [result(case) for case in request["cases"]],
        }
    else:
        raise ValueError("unsupported operation")
    sys.stdout.write(json.dumps(response, sort_keys=True, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

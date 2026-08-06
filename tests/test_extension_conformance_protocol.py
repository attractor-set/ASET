from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]


def load(relative: str) -> dict[str, object]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def test_extension_protocol_and_schemas_validate() -> None:
    protocol = load("seed/canonical/conformance/extension-conformance-protocol.json")
    schema = load("seed/canonical/schemas/extension-conformance-protocol.schema.json")
    Draft202012Validator.check_schema(schema)
    Draft202012Validator(schema).validate(protocol)
    assert protocol["implementation_precedence"] == "NONE"
    assert len(protocol["boundary_roles"]) == 7


def test_canon_package_contains_extension_protocol() -> None:
    package = load("seed/canonical/CANON_PACKAGE.json")
    assert package["extension_conformance_protocol"] == (
        "ASET-SEED-EXTENSION-CONFORMANCE-V1"
    )
    paths = {item["path"] for item in package["files"]}
    assert "seed/canonical/conformance/extension-conformance-protocol.json" in paths
    assert "seed/canonical/schemas/extension-seed-binding.schema.json" in paths


def test_external_extension_runner_has_cli() -> None:
    result = subprocess.run(
        [sys.executable, "tools/run_external_extension_conformance.py", "--help"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr

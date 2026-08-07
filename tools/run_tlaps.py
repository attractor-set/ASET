#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_TLAPM_VERSION = "4600b24"
EXPECTED_TLAPM_COMMIT = "4600b24c6d95a25ff081ad37b63b2a01c29d43a5"

DEFAULT_MODULE = Path("seed/canonical/formal/SeedResolutionProofs.tla")
DEFAULT_MODEL = Path("seed/canonical/formal/SeedResolution.tla")

FINAL_THEOREMS = (
    "SpecImpliesAlwaysSeedStateSafety",
    "SpecImpliesRequestsAppendOnly",
    "SpecImpliesTerminalRecordsImmutable",
    "SpecImpliesCanonicalStateChangesOnlyByRecognizedTransition",
    "SpecImpliesInvalidMaterialStutter",
    "SpecImpliesNonAuthoritativeInputsStutter",
)


def resolve(path: Path) -> Path:
    if path.is_absolute():
        return path
    return ROOT / path


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_report(
    output_path: Path,
    report: dict[str, object],
) -> None:
    output = resolve(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tlapm", type=Path, required=True)
    parser.add_argument(
        "--module",
        type=Path,
        default=DEFAULT_MODULE,
    )
    parser.add_argument(
        "--model",
        type=Path,
        default=DEFAULT_MODEL,
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/tlaps-proof.json"),
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=900,
    )
    args = parser.parse_args()

    tlapm = resolve(args.tlapm)
    module = resolve(args.module)
    model = resolve(args.model)

    errors: list[str] = []

    if not tlapm.is_file():
        errors.append(f"missing TLAPM executable: {tlapm}")
    elif not os.access(tlapm, os.X_OK):
        errors.append(f"TLAPM is not executable: {tlapm}")

    if not module.is_file():
        errors.append(f"missing proof module: {module}")

    if not model.is_file():
        errors.append(f"missing formal model: {model}")

    proof_text = module.read_text(encoding="utf-8") if module.is_file() else ""

    if "EXTENDS SeedResolution, TLAPS" not in proof_text:
        errors.append("proof module does not import SeedResolution and TLAPS")

    for theorem in FINAL_THEOREMS:
        pattern = rf"^THEOREM {re.escape(theorem)} ==\s*$"
        if (
            re.search(
                pattern,
                proof_text,
                flags=re.MULTILINE,
            )
            is None
        ):
            errors.append(f"missing final theorem: {theorem}")

    version_output = ""

    if tlapm.is_file() and os.access(tlapm, os.X_OK):
        try:
            version_result = subprocess.run(
                [str(tlapm), "--version"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=30,
                check=False,
            )
            version_output = version_result.stdout.strip()

            if version_result.returncode != 0:
                errors.append(f"tlapm --version returned {version_result.returncode}")

            if version_output != EXPECTED_TLAPM_VERSION:
                errors.append(f"unexpected TLAPM version: {version_output!r}")
        except subprocess.TimeoutExpired:
            errors.append("tlapm --version timed out")

    print("TLAPS_PROOF=START")
    print(f"TLAPM_COMMIT={EXPECTED_TLAPM_COMMIT}")
    print(f"TLAPM_VERSION={version_output}")
    print(f"TLAPS_MODULE={args.module.as_posix()}")
    print(f"TLAPS_MODEL={args.model.as_posix()}")

    for theorem in FINAL_THEOREMS:
        print(f"TLAPS_FINAL_THEOREM={theorem}")

    output_text = ""
    returncode: int | None = None
    timed_out = False

    if not errors:
        shutil.rmtree(
            ROOT / ".tlacache",
            ignore_errors=True,
        )

        try:
            result = subprocess.run(
                [str(tlapm), str(module)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=args.timeout_seconds,
                check=False,
            )
            output_text = result.stdout
            returncode = result.returncode
        except subprocess.TimeoutExpired as exc:
            timed_out = True
            captured = exc.stdout or ""

            if isinstance(captured, bytes):
                captured = captured.decode(
                    "utf-8",
                    errors="replace",
                )

            output_text = captured
            errors.append("TLAPS proof timed out")

    if output_text:
        print(
            output_text,
            end="" if output_text.endswith("\n") else "\n",
        )

    matches = re.findall(
        r"All ([0-9]+) obligations? proved\.",
        output_text,
    )
    obligations = int(matches[-1]) if matches else None

    forbidden_markers = (
        "obligations failed",
        "unproved obligations",
        "backend errors",
        "Zenon error",
        "Proof.Parser",
        "[ERROR]",
    )

    if returncode != 0:
        errors.append(f"TLAPM returned {returncode}")

    if obligations is None:
        errors.append("TLAPM success summary was not found")

    for marker in forbidden_markers:
        if marker in output_text:
            errors.append(f"TLAPM output contains {marker!r}")

    verdict = "PASS" if not errors else "FAIL"

    report: dict[str, object] = {
        "document_type": "aset-tlaps-proof-report",
        "schema_version": 1,
        "tlapm_commit": EXPECTED_TLAPM_COMMIT,
        "tlapm_version": version_output,
        "module": args.module.as_posix(),
        "module_sha256": ("sha256:" + sha256(module) if module.is_file() else None),
        "model": args.model.as_posix(),
        "model_sha256": ("sha256:" + sha256(model) if model.is_file() else None),
        "final_theorems": list(FINAL_THEOREMS),
        "obligations_proved": obligations,
        "returncode": returncode,
        "timed_out": timed_out,
        "errors": errors,
        "verdict": verdict,
    }

    write_report(args.output, report)

    if obligations is not None:
        print(f"TLAPS_OBLIGATIONS={obligations}")

    print(f"TLAPS_VERDICT={verdict}")

    for error in errors:
        print(f"TLAPS_ERROR={error}")

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TLAPM_VERSION = "4600b24"
EXPECTED_TLAPM_COMMIT = "4600b24c6d95a25ff081ad37b63b2a01c29d43a5"
RELATION_PATH = ROOT / "seed/canonical/assurance/canon-tla-refinement.json"
PROJECTION_PATH = ROOT / "seed/canonical/formal/SeedCanonProjection.tla"
PROOF_PATH = ROOT / "seed/canonical/formal/SeedCanonRefinementProofs.tla"
CHECKER_PATH = ROOT / "tools/check_canon_tla_refinement.py"
FINAL_THEOREM = "SeedResolutionBehaviorallyEquivalentToCanonProjection"


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tlapm", type=Path, required=True)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("dist/canon-tla-refinement-proof.json"),
    )
    parser.add_argument("--timeout-seconds", type=int, default=900)
    args = parser.parse_args()

    errors: list[str] = []
    tlapm = resolve(args.tlapm)

    if not tlapm.is_file():
        errors.append(f"missing TLAPM executable: {tlapm}")
    elif not os.access(tlapm, os.X_OK):
        errors.append(f"TLAPM is not executable: {tlapm}")

    checker = subprocess.run(
        [sys.executable, str(CHECKER_PATH)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if checker.returncode:
        errors.append("canon-to-TLA refinement integrity check failed")

    proof_text = PROOF_PATH.read_text(encoding="utf-8") if PROOF_PATH.is_file() else ""
    if "EXTENDS SeedResolution, TLAPS" not in proof_text:
        errors.append(
            "refinement proof module does not import SeedResolution and TLAPS"
        )
    if (
        re.search(
            r"^Canon\s*==\s*INSTANCE\s+SeedCanonProjection\s*$",
            proof_text,
            flags=re.MULTILINE,
        )
        is None
    ):
        errors.append(
            "refinement proof module does not explicitly instantiate "
            "standalone SeedCanonProjection"
        )
    if (
        re.search(
            rf"^THEOREM {FINAL_THEOREM} ==\s*$",
            proof_text,
            flags=re.MULTILINE,
        )
        is None
    ):
        errors.append(f"missing final theorem: {FINAL_THEOREM}")

    version_output = ""
    if tlapm.is_file() and os.access(tlapm, os.X_OK):
        try:
            result = subprocess.run(
                [str(tlapm), "--version"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=30,
                check=False,
            )
            version_output = result.stdout.strip()
            if result.returncode:
                errors.append(f"tlapm --version returned {result.returncode}")
            if version_output != EXPECTED_TLAPM_VERSION:
                errors.append(f"unexpected TLAPM version: {version_output!r}")
        except subprocess.TimeoutExpired:
            errors.append("tlapm --version timed out")

    print("CANON_TLA_REFINEMENT_PROOF=START")
    print(f"TLAPM_COMMIT={EXPECTED_TLAPM_COMMIT}")
    print(f"TLAPM_VERSION={version_output}")
    print("CANON_TLA_PROJECTION=seed/canonical/formal/SeedCanonProjection.tla")
    print("CANON_TLA_PROOF_MODULE=seed/canonical/formal/SeedCanonRefinementProofs.tla")
    print(f"CANON_TLA_FINAL_THEOREM={FINAL_THEOREM}")

    output_text = ""
    returncode: int | None = None
    timed_out = False

    if not errors:
        shutil.rmtree(ROOT / ".tlacache", ignore_errors=True)
        try:
            result = subprocess.run(
                [str(tlapm), str(PROOF_PATH)],
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
                captured = captured.decode("utf-8", errors="replace")
            output_text = captured
            errors.append("canon-to-TLA refinement proof timed out")

    if output_text:
        print(output_text, end="" if output_text.endswith("\n") else "\n")

    matches = re.findall(r"All ([0-9]+) obligations? proved\.", output_text)
    obligations = int(matches[-1]) if matches else None

    if returncode != 0:
        errors.append(f"TLAPM returned {returncode}")
    if obligations is None:
        errors.append("TLAPM success summary was not found")

    for marker in (
        "obligations failed",
        "unproved obligations",
        "backend errors",
        "Zenon error",
        "Proof.Parser",
        "[ERROR]",
    ):
        if marker in output_text:
            errors.append(f"TLAPM output contains {marker!r}")

    verdict = "PASS" if not errors else "FAIL"
    relation = json.loads(RELATION_PATH.read_text(encoding="utf-8"))
    report = {
        "document_type": "aset-canon-tla-refinement-proof-report",
        "schema_version": 1,
        "relation": "seed/canonical/assurance/canon-tla-refinement.json",
        "source_model_sha256": relation["source_model"]["sha256"],
        "target_model_sha256": relation["target_model"]["sha256"],
        "projection_sha256": digest(PROJECTION_PATH),
        "proof_module_sha256": digest(PROOF_PATH),
        "tlapm_commit": EXPECTED_TLAPM_COMMIT,
        "tlapm_version": version_output,
        "final_theorem": FINAL_THEOREM,
        "obligations_proved": obligations,
        "returncode": returncode,
        "timed_out": timed_out,
        "errors": errors,
        "verdict": verdict,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    if obligations is not None:
        print(f"CANON_TLA_REFINEMENT_OBLIGATIONS={obligations}")
    print("CANON_TLA_REFINEMENT_VERDICT=" + verdict)
    for error in errors:
        print("CANON_TLA_REFINEMENT_ERROR=" + error)

    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

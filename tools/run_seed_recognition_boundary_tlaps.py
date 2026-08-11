#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assurance/seed-recognition-boundary"
MANIFEST = BASE / "ASSURANCE_PACKAGE.json"
TOOLCHAIN_NOTICES = BASE / "TOOLCHAIN_NOTICES.json"
SEED_TLA = ROOT / "seed/canonical/formal/SeedResolution.tla"
CHECKER = ROOT / "tools/check_seed_recognition_boundary.py"
BUILDER = ROOT / "tools/build_seed_recognition_boundary_assurance.py"
EXPECTED_TLAPM_VERSION = "4600b24"
EXPECTED_TLAPM_COMMIT = "4600b24c6d95a25ff081ad37b63b2a01c29d43a5"
EXPECTED_TOTAL = 2257


def resolve(path: Path) -> Path:
    return path if path.is_absolute() else ROOT / path


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def warning_lines(output_text: str) -> list[str]:
    return [line.strip() for line in output_text.splitlines() if line.strip().startswith("WARNING:")]


def expected_warning_counter(policy: dict[str, object], module: str) -> Counter[str]:
    counter: Counter[str] = Counter()
    for notice in policy.get("notices", []):
        expected_by_module = notice.get("expected_by_module", {})
        for line, count in expected_by_module.get(module, {}).items():
            counter[line] += int(count)
    return counter


def classify_warnings(policy: dict[str, object], module: str, output_text: str) -> tuple[int, int, list[str]]:
    observed = Counter(warning_lines(output_text))
    expected = expected_warning_counter(policy, module)
    problems: list[str] = []
    missing = expected - observed
    unexpected = observed - expected
    if missing:
        problems.append("missing pinned TLAPM notice(s): " + repr(dict(missing)))
    if unexpected:
        problems.append("unexpected TLAPM warning(s): " + repr(dict(unexpected)))
    return sum(observed.values()), sum(unexpected.values()), problems


def without_warning_lines(output_text: str) -> str:
    lines = [line for line in output_text.splitlines() if not line.strip().startswith("WARNING:")]
    if not lines:
        return ""
    return "\n".join(lines) + ("\n" if output_text.endswith("\n") else "")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tlapm", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("dist/seed-recognition-boundary-tlaps.json"))
    parser.add_argument("--timeout-seconds", type=int, default=900)
    args = parser.parse_args()
    errors: list[str] = []
    tlapm = resolve(args.tlapm)
    if not tlapm.is_file(): errors.append(f"missing TLAPM executable: {tlapm}")
    elif not os.access(tlapm, os.X_OK): errors.append(f"TLAPM is not executable: {tlapm}")

    for command, label in (
        ([sys.executable, str(BUILDER), "--check"], "assurance package parity"),
        ([sys.executable, str(CHECKER)], "subject/publication/oracle integrity"),
    ):
        result = subprocess.run(command, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        if result.returncode: errors.append(f"{label} failed")

    version_output = ""
    if tlapm.is_file() and os.access(tlapm, os.X_OK):
        try:
            result = subprocess.run([str(tlapm), "--version"], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30, check=False)
            version_output = result.stdout.strip()
            if result.returncode: errors.append(f"tlapm --version returned {result.returncode}")
            if version_output != EXPECTED_TLAPM_VERSION: errors.append(f"unexpected TLAPM version: {version_output!r}")
        except subprocess.TimeoutExpired:
            errors.append("tlapm --version timed out")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    toolchain_policy = json.loads(TOOLCHAIN_NOTICES.read_text(encoding="utf-8"))
    if toolchain_policy["toolchain"]["tlapm_version"] != EXPECTED_TLAPM_VERSION:
        errors.append("toolchain notice policy TLAPM version mismatch")
    if toolchain_policy["toolchain"]["tlapm_commit"] != EXPECTED_TLAPM_COMMIT:
        errors.append("toolchain notice policy TLAPM commit mismatch")
    proof_chain = manifest["proof_chain"]
    formal_dir = BASE / "formal"
    print("SEED_RECOGNITION_BOUNDARY_TLAPS=START")
    print(f"TLAPM_COMMIT={EXPECTED_TLAPM_COMMIT}")
    print(f"TLAPM_VERSION={version_output}")
    print(f"SEED_RESOLUTION_SHA256={digest(SEED_TLA)}")
    print(f"ASSURANCE_PACKAGE_DIGEST={manifest['package_digest']}")
    print(f"PUBLICATION_BASELINE={manifest['publication_baseline']}")

    module_reports: list[dict[str, object]] = []
    total = 0
    known_notice_total = 0
    unexpected_warning_total = 0
    if not errors:
        with tempfile.TemporaryDirectory(prefix="aset-seed-recognition-assurance-") as raw:
            stage = Path(raw)
            shutil.copy2(SEED_TLA, stage / "SeedResolution.tla")
            for src in formal_dir.glob("*.tla"):
                shutil.copy2(src, stage / src.name)
            for item in proof_chain:
                module = Path(item["proof_module"]).name
                expected = int(item["expected_obligations"])
                theorem = item["final_theorem"]
                module_text = (stage / module).read_text(encoding="utf-8")
                if re.search(rf"^THEOREM\s+{re.escape(theorem)}\s*==", module_text, flags=re.MULTILINE) is None:
                    errors.append(f"missing final theorem {theorem} in {module}"); break
                print(f"SEED_RECOGNITION_BOUNDARY_MODULE={module}:START")
                shutil.rmtree(stage / ".tlacache", ignore_errors=True)
                try:
                    result = subprocess.run([str(tlapm), module], cwd=stage, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=args.timeout_seconds, check=False)
                    output_text = result.stdout; returncode = result.returncode; timed_out = False
                except subprocess.TimeoutExpired as exc:
                    captured = exc.stdout or ""
                    if isinstance(captured, bytes): captured = captured.decode("utf-8", errors="replace")
                    output_text = captured; returncode = None; timed_out = True
                observed_warning_count, module_unexpected_count, warning_errors = classify_warnings(toolchain_policy, module, output_text)
                if not warning_errors:
                    known_notice_total += observed_warning_count
                else:
                    unexpected_warning_total += module_unexpected_count
                clean_output = without_warning_lines(output_text)
                if clean_output:
                    print(clean_output, end="" if clean_output.endswith("\n") else "\n")
                if observed_warning_count:
                    print(f"SEED_RECOGNITION_BOUNDARY_TLAPM_KNOWN_NOTICE_COUNT={module}:{observed_warning_count if not warning_errors else 0}")
                matches = re.findall(r"All ([0-9]+) obligations? proved\.", output_text)
                obligations = int(matches[-1]) if matches else None
                module_errors: list[str] = list(warning_errors)
                if timed_out: module_errors.append("TLAPS timeout")
                if returncode != 0: module_errors.append(f"TLAPM returned {returncode}")
                if obligations is None: module_errors.append("TLAPM success summary was not found")
                elif obligations != expected: module_errors.append(f"obligation count drift: expected {expected}, got {obligations}")
                for marker in ("obligations failed", "unproved obligations", "backend errors", "Zenon error", "Proof.Parser", "[ERROR]"):
                    if marker in output_text: module_errors.append(f"TLAPM output contains {marker!r}")
                module_reports.append({
                    "id": item["id"], "module": module, "module_sha256": digest(formal_dir / module),
                    "final_theorem": theorem, "expected_obligations": expected,
                    "obligations_proved": obligations, "returncode": returncode,
                    "timed_out": timed_out, "known_toolchain_notices": observed_warning_count if not warning_errors else 0,
                    "warning_errors": warning_errors, "errors": module_errors,
                    "verdict": "PASS" if not module_errors else "FAIL",
                })
                if module_errors:
                    errors.extend(f"{module}: {message}" for message in module_errors)
                    print(f"SEED_RECOGNITION_BOUNDARY_MODULE={module}:FAIL"); break
                total += obligations or 0
                print(f"SEED_RECOGNITION_BOUNDARY_MODULE={module}:PASS")
                print(f"SEED_RECOGNITION_BOUNDARY_OBLIGATIONS={module}:{obligations}")

    expected_total = int(manifest["expected_tlaps_obligations"])
    expected_notice_total = sum(
        int(notice["expected_total_occurrences"]) for notice in toolchain_policy.get("notices", [])
    )
    if expected_total != EXPECTED_TOTAL: errors.append(f"manifest expected total drift: {expected_total}")
    if not errors and total != EXPECTED_TOTAL: errors.append(f"total obligation drift: expected {EXPECTED_TOTAL}, got {total}")
    if not errors and known_notice_total != expected_notice_total:
        errors.append(f"known TLAPM notice total drift: expected {expected_notice_total}, got {known_notice_total}")
    verdict = "PASS" if not errors else "FAIL"
    report = {
        "document_type": "aset-seed-recognition-boundary-tlaps-report", "schema_version": 2,
        "assurance_id": manifest["assurance_id"], "publication_baseline": manifest["publication_baseline"],
        "assurance_package_digest": manifest["package_digest"], "seed_resolution_sha256": digest(SEED_TLA),
        "tlapm_commit": EXPECTED_TLAPM_COMMIT, "tlapm_version": version_output,
        "modules": module_reports, "expected_total_obligations": EXPECTED_TOTAL,
        "obligations_proved": total, "known_toolchain_notices": known_notice_total,
        "unexpected_warnings": unexpected_warning_total, "errors": errors, "verdict": verdict,
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"SEED_RECOGNITION_BOUNDARY_TLAPM_KNOWN_NOTICES={known_notice_total}")
    print(f"SEED_RECOGNITION_BOUNDARY_TLAPM_UNEXPECTED_WARNINGS={unexpected_warning_total}")
    print(f"SEED_RECOGNITION_BOUNDARY_TLAPS_TOTAL={total}")
    print("SEED_RECOGNITION_BOUNDARY_TLAPS_VERDICT=" + verdict)
    for error in errors: print("SEED_RECOGNITION_BOUNDARY_TLAPS_ERROR=" + error)
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())

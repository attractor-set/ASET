#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

from seed_recognition_boundary_oracle import run_exhaustive_audit

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "assurance/seed-recognition-boundary"
MANIFEST = BASE / "ASSURANCE_PACKAGE.json"
PUBLICATION_BASELINE = BASE / "PUBLICATION_BASELINE.json"
TOOLCHAIN_NOTICES = BASE / "TOOLCHAIN_NOTICES.json"
CANON_PACKAGE = ROOT / "seed/canonical/CANON_PACKAGE.json"
SEED_MODEL = ROOT / "seed/canonical/source/seed-model.json"
SEED_TLA = ROOT / "seed/canonical/formal/SeedResolution.tla"
CANON_RELATION = ROOT / "seed/canonical/assurance/canon-tla-refinement.json"
FROZEN_PUBLICATION_BASELINE_SHA256 = "sha256:6144b801ccb9468ce667402d5eaf1e5eeee52d7dbd3a464a440722079694f129"


def strict(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON member: {key}")
        result[key] = value
    return result


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=strict)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def theorem_names(path: Path) -> set[str]:
    return set(re.findall(r"^THEOREM\s+([A-Za-z][A-Za-z0-9_]*)\s*==", path.read_text(encoding="utf-8"), flags=re.MULTILINE))


def strip_tla_comments(text: str) -> str:
    out: list[str] = []
    i = 0
    block = 0
    in_string = False
    while i < len(text):
        if block:
            if text.startswith("(*", i):
                block += 1; i += 2; continue
            if text.startswith("*)", i):
                block -= 1; i += 2; continue
            if text[i] == "\n": out.append("\n")
            i += 1; continue
        if in_string:
            ch = text[i]; out.append(ch)
            if ch == "\\" and i + 1 < len(text):
                i += 1; out.append(text[i])
            elif ch == '"': in_string = False
            i += 1; continue
        if text.startswith("(*", i):
            block = 1; i += 2; continue
        if text.startswith("\\*", i):
            j = text.find("\n", i)
            if j < 0: break
            out.append("\n"); i = j + 1; continue
        ch = text[i]
        if ch == '"': in_string = True
        out.append(ch); i += 1
    if block:
        raise ValueError("unterminated TLA comment")
    return "".join(out)


def normalized_tla_digest(path: Path) -> str:
    stripped = strip_tla_comments(path.read_text(encoding="utf-8"))
    canonical = "\n".join(line.rstrip() for line in stripped.splitlines()).strip() + "\n"
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dist/seed-recognition-boundary-check.json"))
    args = parser.parse_args()
    errors: list[str] = []

    manifest = load(MANIFEST)
    baseline = load(PUBLICATION_BASELINE)
    toolchain_notices = load(TOOLCHAIN_NOTICES)
    canon_package = load(CANON_PACKAGE)
    seed_model = load(SEED_MODEL)
    canon_relation = load(CANON_RELATION)
    subject = manifest["subject"]

    if manifest.get("normative") is not False or manifest.get("normative_precedence") != "NONE":
        errors.append("assurance package must remain non-normative with no normative precedence")
    if manifest.get("expected_tlaps_obligations") != 2257:
        errors.append("expected TLAPS total is not the frozen v60 total 2257")
    if manifest.get("active_tla_modules") != 34 or manifest.get("proof_modules") != 20:
        errors.append("active v60 module-count drift")
    if digest(PUBLICATION_BASELINE) != FROZEN_PUBLICATION_BASELINE_SHA256:
        errors.append("publication baseline identity mismatch")
    if baseline.get("source_v60_tlaps_obligations") != 2257:
        errors.append("publication baseline TLAPS total mismatch")
    if toolchain_notices.get("toolchain", {}).get("tlapm_version") != "4600b24":
        errors.append("toolchain notice TLAPM version mismatch")
    if toolchain_notices.get("toolchain", {}).get("tlapm_commit") != "4600b24c6d95a25ff081ad37b63b2a01c29d43a5":
        errors.append("toolchain notice TLAPM commit mismatch")
    notice_total = sum(int(item.get("expected_total_occurrences", 0)) for item in toolchain_notices.get("notices", []))
    if notice_total != 15:
        errors.append(f"toolchain notice count drift: {notice_total}")
    parametric_lines = (BASE / "formal/ParametricLocalStateCardinalityProofs.tla").read_text(encoding="utf-8").splitlines()
    canonical_lines = (BASE / "formal/CanonicalLocalReachabilityProofs.tla").read_text(encoding="utf-8").splitlines()
    if len(parametric_lines) >= 1177:
        errors.append("toolchain notice provenance assumption drift: parametric source unexpectedly reaches reported warning lines")
    for line_no in (1061, 1176, 1310):
        if len(canonical_lines[line_no - 1]) >= 54:
            errors.append(f"toolchain notice provenance assumption drift at CanonicalLocalReachabilityProofs.tla:{line_no}")

    if subject["canon_id"] != canon_package["canon_id"] or subject["canon_version"] != canon_package["canon_version"]:
        errors.append("canon identity mismatch")
    if subject["canon_package_file_sha256"] != digest(CANON_PACKAGE):
        errors.append("canon package file digest mismatch")
    if subject["canon_package_digest"] != canon_package["package_digest"]:
        errors.append("canon package semantic digest mismatch")
    if subject["seed_model_sha256"] != digest(SEED_MODEL):
        errors.append("machine-readable Seed model digest mismatch")
    if subject["seed_resolution_sha256"] != digest(SEED_TLA):
        errors.append("SeedResolution.tla digest mismatch")
    if subject["canon_tla_refinement_sha256"] != digest(CANON_RELATION):
        errors.append("canon-to-TLA relation digest mismatch")
    if canon_relation["target_model"]["sha256"] != subject["seed_resolution_sha256"]:
        errors.append("canon-to-TLA target is not the pinned SeedResolution")
    if canon_relation["source_model"]["sha256"] != subject["seed_model_sha256"]:
        errors.append("canon-to-TLA source is not the pinned machine Seed model")

    published = {p.name: p for p in (BASE / "formal").glob("*.tla")}
    if len(published) != 34:
        errors.append(f"published active TLA module count is {len(published)}, expected 34")
    baseline_rows = {row["module"]: row for row in baseline["formal_modules"]}
    if set(published) != set(baseline_rows):
        errors.append("published formal module set differs from v60 publication baseline")
    else:
        for name, path in published.items():
            if normalized_tla_digest(path) != baseline_rows[name]["comment_stripped_sha256"]:
                errors.append(f"non-comment formal drift from v60 baseline: {name}")

    rows = manifest["files"]
    if any(digest(ROOT / row["path"]) != row["sha256"] for row in rows):
        errors.append("assurance-package file hash mismatch")
    expected_package_digest = "sha256:" + hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()
    if manifest["package_digest"] != expected_package_digest:
        errors.append("assurance package digest mismatch")

    forward = (BASE / "formal/CanonicalPhaseSeedToSeedRefinementProofs.tla").read_text(encoding="utf-8")
    reverse = (BASE / "formal/SeedToCanonicalPhaseSeedRefinementProofs.tla").read_text(encoding="utf-8")
    local = (BASE / "formal/CanonicalLocalReachability.tla").read_text(encoding="utf-8")
    info = (BASE / "formal/CanonicalReachableInformationBoundProofs.tla").read_text(encoding="utf-8")
    if re.search(r"^Seed\s*==\s*INSTANCE\s+SeedResolution\s*$", forward, re.MULTILINE) is None:
        errors.append("forward canonical refinement does not instantiate SeedResolution")
    if "EXTENDS SeedResolution, TLAPS" not in reverse:
        errors.append("reverse canonical refinement does not directly import SeedResolution")
    if re.search(r"^Canonical\s*==\s*INSTANCE\s+CanonicalPhaseSeed\s*$", local, re.MULTILINE) is None:
        errors.append("reachability model does not instantiate CanonicalPhaseSeed")
    if "CanonicalLocalReachabilityProofs" not in info or "ParametricLocalStateCardinalityProofs" not in info:
        errors.append("composed information-bound proof topology mismatch")

    obligation_total = 0
    for item in manifest["proof_chain"]:
        proof_path = ROOT / item["proof_module"]
        if item["final_theorem"] not in theorem_names(proof_path):
            errors.append(f"missing final theorem {item['final_theorem']} in {item['proof_module']}")
        obligation_total += int(item["expected_obligations"])
    if obligation_total != 2257:
        errors.append(f"proof-chain obligation total is {obligation_total}, expected 2257")

    oracle_report: dict[str, Any] | None = None
    try:
        oracle_report = run_exhaustive_audit()
        if oracle_report["profiles_checked"] != 2046: errors.append("unexpected executable oracle profile count")
        if oracle_report["max_shortest_reachability_depth"] != 3: errors.append("unexpected executable oracle reachability depth")
        if oracle_report["rich_exact_states"] != 29: errors.append("rich witness state count drift")
    except (AssertionError, ValueError) as exc:
        errors.append(f"executable boundary oracle failed: {exc}")

    report = {
        "document_type": "aset-seed-recognition-boundary-check",
        "schema_version": 2,
        "assurance_id": manifest["assurance_id"],
        "publication_baseline": manifest["publication_baseline"],
        "assurance_package_digest": manifest["package_digest"],
        "canon_package_digest": canon_package["package_digest"],
        "seed_resolution_sha256": digest(SEED_TLA),
        "canon_tla_refinement_sha256": digest(CANON_RELATION),
        "expected_tlaps_obligations": manifest["expected_tlaps_obligations"],
        "publication_baseline_sha256": digest(PUBLICATION_BASELINE),
        "toolchain_notice_policy_sha256": digest(TOOLCHAIN_NOTICES),
        "expected_known_toolchain_notices": notice_total,
        "oracle": oracle_report,
        "errors": errors,
        "verdict": "PASS" if not errors else "FAIL",
    }
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8", newline="\n")
    print("SEED_RECOGNITION_BOUNDARY_SUBJECT_BINDING=" + ("PASS" if not errors else "FAIL"))
    print("SEED_RECOGNITION_BOUNDARY_PUBLICATION_IDENTITY=" + ("PASS" if not errors else "FAIL"))
    if oracle_report is not None:
        print(f"SEED_RECOGNITION_BOUNDARY_PROFILES={oracle_report['profiles_checked']}")
        print(f"SEED_RECOGNITION_BOUNDARY_MAX_DEPTH={oracle_report['max_shortest_reachability_depth']}")
    print("SEED_RECOGNITION_BOUNDARY_CHECK=" + report["verdict"])
    for error in errors: print("SEED_RECOGNITION_BOUNDARY_ERROR=" + error)
    return 0 if not errors else 1

if __name__ == "__main__":
    raise SystemExit(main())

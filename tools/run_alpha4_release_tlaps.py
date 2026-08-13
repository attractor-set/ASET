#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FINAL_THEOREM = "AssembledNextPreservesExactSubjectAndAuthority"
VERIFIER_MODULE = "AssembledSeedReleaseProofs"


class ReleaseTLAPSError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ReleaseTLAPSError(message)


def default_tlapm() -> str:
    configured = os.environ.get("TLAPM_BIN")
    if configured:
        return configured
    return str(ROOT / ".tooling" / "tlapm" / "bin" / "tlapm")


def sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def parse_obligation_count(text: str) -> int | None:
    matches = re.findall(r"All\s+(\d+)\s+obligations?\s+proved\.", text)
    return int(matches[-1]) if matches else None


def verifier_source() -> str:
    return "\n".join(
        [
            "---------------- MODULE AssembledSeedReleaseProofs ----------------",
            "EXTENDS AssembledSeed, TLAPS",
            "",
            f"THEOREM {FINAL_THEOREM} ==",
            "  \\A s, t, e : Next(s, t, e) =>",
            "    /\\ t.subject = s.subject",
            "    /\\ t.authority = s.authority",
            "PROOF",
            "  BY DEF Next,",
            "         ObserveUnknown,",
            "         RecognizeAllow,",
            "         RecognizeBlock,",
            "         PreserveUnknown,",
            "         PreserveAllow,",
            "         PreserveBlock,",
            "         StateType",
            "",
            "======================================"
            "=======================================",
            "",
        ]
    )


def load_release_manifest(release_root: Path) -> dict[str, Any]:
    path = release_root / "RELEASE_MANIFEST.json"
    require(path.is_file(), "release manifest missing")
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), "release manifest must be an object")
    require(
        value.get("document_type") == "aset-seed-release-materialization",
        "unexpected release manifest type",
    )
    congruence = value.get("congruence_assurance")
    require(isinstance(congruence, dict), "release congruence assurance missing")
    assembled = congruence.get("assembled_formal")
    require(isinstance(assembled, dict), "assembled formal congruence missing")
    require(
        assembled.get("status") == "PASS",
        "assembled formal congruence is not PASS",
    )
    require(
        assembled.get("components_checked") == 6,
        "assembled formal component coverage mismatch",
    )
    return value


def check_release_tlaps(release_root: Path, tlapm: str) -> dict[str, Any]:
    release_root = release_root.resolve()
    formal_root = release_root / "formal"
    assembled = formal_root / "AssembledSeed.tla"
    require(release_root.is_dir(), "release root missing")
    require(formal_root.is_dir(), "release formal directory missing")
    require(assembled.is_file(), "materialized AssembledSeed.tla missing")
    load_release_manifest(release_root)
    release_tree_digest = tree_digest(release_root)

    source = verifier_source()
    with tempfile.TemporaryDirectory(prefix="aset-seed-release-tlaps-") as temp_dir:
        verification_root = Path(temp_dir)
        verifier = verification_root / f"{VERIFIER_MODULE}.tla"
        verifier.write_text(source, encoding="utf-8")
        try:
            result = subprocess.run(
                [tlapm, "-I", str(formal_root), str(verifier)],
                cwd=verification_root,
                check=False,
                capture_output=True,
                text=True,
            )
        except OSError as error:
            raise ReleaseTLAPSError(f"TLAPM invocation failed: {error}") from error

    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    combined = result.stdout + "\n" + result.stderr
    obligations = parse_obligation_count(combined)
    require(result.returncode == 0, f"TLAPM returned {result.returncode}")
    require(
        obligations is not None and obligations > 0,
        "proved obligation count missing",
    )
    require(
        tree_digest(release_root) == release_tree_digest,
        "materialized release tree changed during TLAPS verification",
    )

    return {
        "document_type": "aset-release-assembled-tlaps-evidence",
        "schema_version": 1,
        "scope": "POST_BUILD_DEDUCTIVE_ASSURANCE",
        "semantic_delta": "NONE",
        "semantic_precedence": "NONE",
        "semantic_source_runtime_dependency": "NONE",
        "release_binding": {
            "tree_digest": release_tree_digest,
            "assembled_formal": {
                "path": "formal/AssembledSeed.tla",
                "sha256": sha256(assembled),
            },
        },
        "proof": {
            "module": VERIFIER_MODULE,
            "module_materialization": "EPHEMERAL_VERIFIER_ONLY",
            "module_sha256": "sha256:"
            + hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "final_theorem": FINAL_THEOREM,
            "obligations_proved": obligations,
        },
        "status": "PASS",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--release-root",
        type=Path,
        default=ROOT / "dist/ASET-Seed-0.4alpha",
    )
    parser.add_argument("--tlapm", default=default_tlapm())
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dist/release-assembled-tlaps-evidence.json",
    )
    args = parser.parse_args(argv)

    try:
        evidence = check_release_tlaps(args.release_root, args.tlapm)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(evidence, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    except (json.JSONDecodeError, OSError, ReleaseTLAPSError, ValueError) as error:
        print(f"ALPHA4_RELEASE_TLAPS_ERROR={error}")
        print("ALPHA4_RELEASE_TLAPS=FAIL")
        return 1

    proof = evidence["proof"]
    binding = evidence["release_binding"]
    assembled = binding["assembled_formal"]
    print("ALPHA4_RELEASE_TLAPS_SCOPE=POST_BUILD_DEDUCTIVE_ASSURANCE")
    print(f"ALPHA4_RELEASE_TLAPS_FINAL_THEOREM={proof['final_theorem']}")
    print(f"ALPHA4_RELEASE_TLAPS_OBLIGATIONS={proof['obligations_proved']} PASS")
    print(f"ALPHA4_RELEASE_TLAPS_ASSEMBLED_SHA256={assembled['sha256']}")
    print(f"ALPHA4_RELEASE_TLAPS_TREE_DIGEST={binding['tree_digest']}")
    print("ALPHA4_RELEASE_TLAPS_SEMANTIC_DELTA=NONE")
    print("ALPHA4_RELEASE_TLAPS_SEMANTIC_SOURCE_DEPENDENCY=NONE")
    print("ALPHA4_RELEASE_TLAPS=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

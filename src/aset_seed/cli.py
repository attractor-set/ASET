
from __future__ import annotations

import argparse
import json
import os
from collections.abc import Sequence
from dataclasses import asdict
from pathlib import Path

from .jsonio import StrictJsonError, load_strict
from .proofs import HmacSha256ProofVerifier, RejectAllProofVerifier
from .runtime import DurableSeedRuntime


def _load_verifier(path: Path | None):
    if path is None:
        return RejectAllProofVerifier()
    if os.name == "posix" and path.stat().st_mode & 0o077:
        raise StrictJsonError("proof-secret file must not be group/world accessible")
    data = load_strict(path, max_bytes=1024 * 1024)
    if not isinstance(data, dict):
        raise StrictJsonError("proof-secret document must be an object")
    if data.get("document_type") != "aset-seed-hmac-secret-map":
        raise StrictJsonError("unsupported proof-secret document type")
    if data.get("profile") != "HMAC_SHA256_V1":
        raise StrictJsonError("unsupported proof profile")
    secrets = data.get("secrets")
    if not isinstance(secrets, dict):
        raise StrictJsonError("secrets must be an object")
    return HmacSha256ProofVerifier.from_base64(secrets)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aset-seed")
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--proof-secrets", type=Path)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init = subparsers.add_parser("init")
    init.add_argument("genesis", type=Path)

    apply = subparsers.add_parser("apply")
    apply.add_argument("trust_space_id")
    apply.add_argument("transition", type=Path)

    state = subparsers.add_parser("state")
    state.add_argument("trust_space_id")

    validate = subparsers.add_parser("validate")
    validate.add_argument("trust_space_id")

    backup = subparsers.add_parser("backup")
    backup.add_argument("destination", type=Path)

    subparsers.add_parser("health")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        verifier = _load_verifier(args.proof_secrets)
        runtime = DurableSeedRuntime(args.db, proof_verifier=verifier)
        if args.command == "init":
            state = runtime.initialize(load_strict(args.genesis))
            print(
                json.dumps(
                    {
                        "trust_space_id": state["trust_space_id"],
                        "state_root": state["current_state_root"],
                    },
                    sort_keys=True,
                )
            )
        elif args.command == "apply":
            result = runtime.apply(args.trust_space_id, load_strict(args.transition))
            print(json.dumps(result, sort_keys=True))
            return 0 if result["accepted"] else 2
        elif args.command == "state":
            print(
                json.dumps(
                    runtime.get_state(args.trust_space_id),
                    ensure_ascii=False,
                    sort_keys=True,
                    indent=2,
                )
            )
        elif args.command == "validate":
            runtime.validate(args.trust_space_id)
            print("STATE_VALIDATION=PASS")
        elif args.command == "backup":
            runtime.backup(args.destination)
            print(f"BACKUP={args.destination}")
        elif args.command == "health":
            status = asdict(runtime.health())
            print(json.dumps(status, sort_keys=True))
            healthy = (
                status["database_integrity"] == "ok"
                and status["audit_chain"] == "PASS"
            )
            return 0 if healthy else 1
    except Exception as error:
        print(f"ASET_SEED_ERROR={type(error).__name__}:{error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

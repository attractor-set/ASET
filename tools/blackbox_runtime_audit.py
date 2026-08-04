from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import hmac
import json
import os
import sqlite3
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

EXPECTED_ROOT = "ASET/"


@dataclass
class Check:
    id: str
    name: str
    status: str
    details: str


def canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def domain_digest(domain: str, value: object) -> str:
    payload = canonical_bytes(value)
    framed = domain.encode("ascii") + b"\x00" + len(payload).to_bytes(8, "big") + payload
    return "sha256:" + hashlib.sha256(framed).hexdigest()


def proof_material(transition: dict) -> bytes:
    material = copy.deepcopy(transition)
    material.pop("transition_id", None)
    authn = material.get("authn")
    if isinstance(authn, dict):
        authn.pop("proof_digest", None)
    return canonical_bytes(material)


def sign_transition(transition: dict, secret: bytes) -> dict:
    signed = copy.deepcopy(transition)
    signed["authn"]["proof_digest"] = "sha256:" + hmac.new(
        secret, proof_material(signed), hashlib.sha256
    ).hexdigest()
    material = copy.deepcopy(signed)
    material.pop("transition_id", None)
    signed["transition_id"] = "tx:" + domain_digest("ASET/Transition/v1", material)[7:]
    return signed


def safe_extract(snapshot: Path, destination: Path) -> Path:
    with zipfile.ZipFile(snapshot) as archive:
        names = set()
        for info in archive.infolist():
            pure = PurePosixPath(info.filename)
            if pure.is_absolute() or ".." in pure.parts or info.filename in names:
                raise ValueError(f"unsafe ZIP member: {info.filename}")
            names.add(info.filename)
        archive.extractall(destination)
    root = destination / "ASET"
    if not root.is_dir():
        raise ValueError("snapshot root ASET/ is missing")
    return root


def run_cli(root: Path, arguments: list[str]) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")
    return subprocess.run(
        [sys.executable, "-m", "aset_seed", *arguments],
        cwd=root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def record(checks: list[Check], identifier: str, name: str, passed: bool, details: str) -> None:
    checks.append(Check(identifier, name, "PASS" if passed else "FAIL", details))


def audit(snapshot: Path) -> dict[str, object]:
    checks: list[Check] = []
    with tempfile.TemporaryDirectory(prefix="aset-runtime-blackbox-") as directory:
        root = safe_extract(snapshot, Path(directory))
        case_path = root / "seed/releases/0.1-rc11/expanded/machine/examples/positive/POS-001.json"
        case = json.loads(case_path.read_text(encoding="utf-8"))
        work = Path(directory) / "runtime"
        work.mkdir()
        genesis = work / "genesis.json"
        unsigned = work / "unsigned.json"
        signed = work / "signed.json"
        secrets = work / "secrets.json"
        database = work / "seed.db"
        backup = work / "backup.db"
        secret = b"blackbox-runtime-secret-material-32-bytes"
        genesis.write_text(json.dumps(case["initial_genesis"], sort_keys=True) + "\n")
        unsigned.write_text(json.dumps(case["candidate"], sort_keys=True) + "\n")
        signed_transition = sign_transition(case["candidate"], secret)
        signed.write_text(json.dumps(signed_transition, sort_keys=True) + "\n")
        secrets.write_text(
            json.dumps(
                {
                    "document_type": "aset-seed-hmac-secret-map",
                    "profile": "HMAC_SHA256_V1",
                    "secrets": {
                        "principal:bootstrap": base64.b64encode(secret).decode("ascii")
                    },
                },
                sort_keys=True,
            )
            + "\n"
        )
        if os.name == "posix":
            os.chmod(secrets, 0o600)

        init = run_cli(root, ["--db", str(database), "init", str(genesis)])
        try:
            init_data = json.loads(init.stdout)
        except Exception:
            init_data = {}
        trust_space_id = init_data.get("trust_space_id", "")
        record(
            checks,
            "RT-BB-001",
            "initialize durable trust space",
            init.returncode == 0 and trust_space_id.startswith("ts:"),
            (init.stdout + init.stderr).strip()[:500],
        )

        rejected = run_cli(
            root,
            [
                "--db",
                str(database),
                "--proof-secrets",
                str(secrets),
                "apply",
                trust_space_id,
                str(unsigned),
            ],
        )
        try:
            rejected_data = json.loads(rejected.stdout)
        except Exception:
            rejected_data = {}
        record(
            checks,
            "RT-BB-002",
            "invalid proof fails closed",
            rejected.returncode == 2
            and rejected_data.get("code") == "PROOF_REJECTED"
            and rejected_data.get("state_changed") is False,
            (rejected.stdout + rejected.stderr).strip()[:500],
        )

        accepted = run_cli(
            root,
            [
                "--db",
                str(database),
                "--proof-secrets",
                str(secrets),
                "apply",
                trust_space_id,
                str(signed),
            ],
        )
        try:
            accepted_data = json.loads(accepted.stdout)
        except Exception:
            accepted_data = {}
        record(
            checks,
            "RT-BB-003",
            "valid proof commits transition",
            accepted.returncode == 0
            and accepted_data.get("accepted") is True
            and accepted_data.get("state_changed") is True,
            (accepted.stdout + accepted.stderr).strip()[:500],
        )

        replay = run_cli(
            root,
            [
                "--db",
                str(database),
                "--proof-secrets",
                str(secrets),
                "apply",
                trust_space_id,
                str(signed),
            ],
        )
        try:
            replay_data = json.loads(replay.stdout)
        except Exception:
            replay_data = {}
        record(
            checks,
            "RT-BB-004",
            "exact replay is idempotent",
            replay.returncode == 0
            and replay_data.get("accepted") is True
            and replay_data.get("state_changed") is False
            and replay_data.get("code") == "IDEMPOTENT_REPLAY",
            (replay.stdout + replay.stderr).strip()[:500],
        )

        validate = run_cli(root, ["--db", str(database), "validate", trust_space_id])
        record(
            checks,
            "RT-BB-005",
            "persisted state validates after process reopen",
            validate.returncode == 0 and "STATE_VALIDATION=PASS" in validate.stdout,
            (validate.stdout + validate.stderr).strip()[:500],
        )

        health = run_cli(root, ["--db", str(database), "health"])
        try:
            health_data = json.loads(health.stdout)
        except Exception:
            health_data = {}
        record(
            checks,
            "RT-BB-006",
            "database and audit-chain health",
            health.returncode == 0
            and health_data.get("database_integrity") == "ok"
            and health_data.get("audit_chain") == "PASS"
            and health_data.get("proof_profile") == "REJECT_ALL",
            (health.stdout + health.stderr).strip()[:500],
        )

        backup_result = run_cli(root, ["--db", str(database), "backup", str(backup)])
        backup_ok = False
        if backup_result.returncode == 0 and backup.is_file():
            connection = sqlite3.connect(backup)
            try:
                backup_ok = connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
            finally:
                connection.close()
        record(
            checks,
            "RT-BB-007",
            "consistent SQLite backup",
            backup_ok,
            (backup_result.stdout + backup_result.stderr).strip()[:500],
        )

        connection = sqlite3.connect(database)
        try:
            connection.execute(
                "UPDATE transition_attempts SET entry_hash=? "
                "WHERE sequence=(SELECT MIN(sequence) FROM transition_attempts)",
                ("sha256:" + "f" * 64,),
            )
            connection.commit()
        finally:
            connection.close()
        tampered = run_cli(root, ["--db", str(database), "health"])
        try:
            tampered_data = json.loads(tampered.stdout)
        except Exception:
            tampered_data = {}
        record(
            checks,
            "RT-BB-008",
            "audit tampering is detected",
            tampered.returncode != 0 and tampered_data.get("audit_chain") == "FAIL",
            (tampered.stdout + tampered.stderr).strip()[:500],
        )

    passed = sum(item.status == "PASS" for item in checks)
    return {
        "document_type": "aset-seed-runtime-blackbox-audit",
        "version": 1,
        "audit_boundary": "built snapshot and public CLI only",
        "snapshot": snapshot.name,
        "verdict": "PASS" if passed == len(checks) else "FAIL",
        "summary": {"passed": passed, "failed": len(checks) - passed, "total": len(checks)},
        "checks": [asdict(item) for item in checks],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md")
    args = parser.parse_args()
    snapshot = Path(args.snapshot)
    if not snapshot.is_file():
        print(f"RUNTIME_BLACKBOX_FATAL=snapshot missing:{snapshot}")
        return 1
    report = audit(snapshot)
    if args.output_json:
        path = Path(args.output_json)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    if args.output_md:
        lines = [
            "# ASET Seed runtime black-box audit",
            "",
            f"Verdict: **{report['verdict']}**",
            "",
            "| ID | Check | Status | Details |",
            "|---|---|---|---|",
        ]
        for item in report["checks"]:
            details = str(item["details"]).replace("|", "\\|").replace("\n", " ")
            lines.append(f"| {item['id']} | {item['name']} | {item['status']} | {details} |")
        Path(args.output_md).write_text("\n".join(lines) + "\n", encoding="utf-8")
    for item in report["checks"]:
        print(f"{item['id']}={item['status']}:{item['name']}")
    print(f"RUNTIME_BLACKBOX_PASSED={report['summary']['passed']}")
    print(f"RUNTIME_BLACKBOX_FAILED={report['summary']['failed']}")
    print(f"RUNTIME_BLACKBOX_AUDIT={report['verdict']}")
    return 0 if report["verdict"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

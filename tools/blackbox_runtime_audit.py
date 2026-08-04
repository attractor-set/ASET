from __future__ import annotations

import argparse
import base64
import copy
import hashlib
import hmac
import json
import os
import shutil
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


def run_embedded(
    root: Path,
    code: str,
    arguments: list[str],
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")
    return subprocess.run(
        [sys.executable, "-c", code, *arguments],
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
        modified_after_proof = work / "modified-after-proof.json"
        secrets = work / "secrets.json"
        database = work / "seed.db"
        backup = work / "backup.db"
        secret = b"blackbox-runtime-secret-material-32-bytes"
        genesis.write_text(json.dumps(case["initial_genesis"], sort_keys=True) + "\n")
        unsigned.write_text(json.dumps(case["candidate"], sort_keys=True) + "\n")
        signed_transition = sign_transition(case["candidate"], secret)
        signed.write_text(json.dumps(signed_transition, sort_keys=True) + "\n")
        modified_transition = copy.deepcopy(signed_transition)
        modified_transition["payload"]["local_alias"] = "modified-after-proof"
        modified_material = copy.deepcopy(modified_transition)
        modified_material.pop("transition_id", None)
        modified_transition["transition_id"] = (
            "tx:" + domain_digest("ASET/Transition/v1", modified_material)[7:]
        )
        modified_after_proof.write_text(
            json.dumps(modified_transition, sort_keys=True) + "\n"
        )
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

        modified_proof = run_cli(
            root,
            [
                "--db",
                str(database),
                "--proof-secrets",
                str(secrets),
                "apply",
                trust_space_id,
                str(modified_after_proof),
            ],
        )
        try:
            modified_proof_data = json.loads(modified_proof.stdout)
        except Exception:
            modified_proof_data = {}
        record(
            checks,
            "RT-BB-018",
            "HMAC proof is bound to exact transition content",
            modified_proof.returncode == 2
            and modified_proof_data.get("code") == "PROOF_REJECTED"
            and modified_proof_data.get("state_changed") is False,
            (modified_proof.stdout + modified_proof.stderr).strip()[:500],
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
            and health_data.get("state_validation") == "PASS"
            and health_data.get("audit_chain") == "PASS"
            and health_data.get("proof_profile") == "REJECT_ALL",
            (health.stdout + health.stderr).strip()[:500],
        )

        backup_result = run_cli(root, ["--db", str(database), "backup", str(backup)])
        backup_health = run_cli(root, ["--db", str(backup), "health"])
        backup_validate = run_cli(
            root,
            ["--db", str(backup), "validate", trust_space_id],
        )
        try:
            backup_health_data = json.loads(backup_health.stdout)
        except Exception:
            backup_health_data = {}
        backup_ok = (
            backup_result.returncode == 0
            and backup.is_file()
            and backup_health.returncode == 0
            and backup_health_data.get("database_integrity") == "ok"
            and backup_health_data.get("state_validation") == "PASS"
            and backup_health_data.get("audit_chain") == "PASS"
            and backup_validate.returncode == 0
            and "STATE_VALIDATION=PASS" in backup_validate.stdout
        )
        record(
            checks,
            "RT-BB-007",
            "consistent semantic SQLite backup",
            backup_ok,
            (
                backup_result.stdout
                + backup_result.stderr
                + backup_health.stdout
                + backup_health.stderr
                + backup_validate.stdout
                + backup_validate.stderr
            ).strip()[:500],
        )

        corrupt_database = work / "corrupt-state.db"
        shutil.copy2(backup, corrupt_database)
        connection = sqlite3.connect(corrupt_database)
        try:
            row = connection.execute(
                "SELECT trust_space_id, state_json FROM trust_spaces LIMIT 1"
            ).fetchone()
            corrupt_state = json.loads(row[1])
            corrupt_state.pop("contexts")
            connection.execute(
                "UPDATE trust_spaces SET state_json=? WHERE trust_space_id=?",
                (json.dumps(corrupt_state, sort_keys=True), row[0]),
            )
            connection.commit()
        finally:
            connection.close()
        corrupt_health = run_cli(root, ["--db", str(corrupt_database), "health"])
        try:
            corrupt_health_data = json.loads(corrupt_health.stdout)
        except Exception:
            corrupt_health_data = {}
        record(
            checks,
            "RT-BB-009",
            "logical state corruption fails health",
            corrupt_health.returncode != 0
            and corrupt_health_data.get("database_integrity") == "ok"
            and corrupt_health_data.get("state_validation") == "FAIL",
            (corrupt_health.stdout + corrupt_health.stderr).strip()[:500],
        )

        invalid_backup = work / "invalid-backup.db"
        corrupt_backup = run_cli(
            root,
            ["--db", str(corrupt_database), "backup", str(invalid_backup)],
        )
        record(
            checks,
            "RT-BB-010",
            "backup rejects logically invalid state",
            corrupt_backup.returncode != 0 and not invalid_backup.exists(),
            (corrupt_backup.stdout + corrupt_backup.stderr).strip()[:500],
        )

        if os.name == "posix":
            symlink_database = work / "symlink.db"
            symlink_database.symlink_to(backup)
            symlink_result = run_cli(root, ["--db", str(symlink_database), "health"])
            symlink_ok = (
                symlink_result.returncode != 0
                and "symbolic link" in (symlink_result.stdout + symlink_result.stderr)
            )
            symlink_details = (
                symlink_result.stdout + symlink_result.stderr
            ).strip()[:500]
        else:
            symlink_ok = True
            symlink_details = "not applicable outside POSIX profile"
        record(
            checks,
            "RT-BB-011",
            "database symlink is rejected",
            symlink_ok,
            symlink_details,
        )

        embedded_database = work / "embedded.db"
        embedded_code = r'''
import json
import sqlite3
import sys
from pathlib import Path

from aset_seed.proofs import RejectAllProofVerifier
from aset_seed.runtime import DurableSeedRuntime, MAX_TRANSITION_BYTES

case = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
database = Path(sys.argv[1])
runtime = DurableSeedRuntime(database, proof_verifier=RejectAllProofVerifier())
state = runtime.initialize(case["initial_genesis"])
space = state["trust_space_id"]
malformed = runtime.apply(space, {"not_json": {"a", "b"}})
oversized = dict(case["candidate"])
oversized["oversized_untrusted_input"] = "x" * (MAX_TRANSITION_BYTES + 1)
oversized_result = runtime.apply(space, oversized)

class RaisingVerifier:
    profile_id = "TEST_RAISING_VERIFIER"

    def verify(self, transition):
        raise RuntimeError("secret diagnostic must not escape")

raising = DurableSeedRuntime(database, proof_verifier=RaisingVerifier())
verifier_result = raising.apply(space, case["candidate"])
unknown = runtime.apply("ts:" + "0" * 64, {})
invalid_identifier = runtime.apply({"not": "an identifier"}, {})
connection = sqlite3.connect(database)
try:
    rows = connection.execute(
        "SELECT transition_json, code FROM transition_attempts ORDER BY sequence"
    ).fetchall()
finally:
    connection.close()
print(json.dumps({
    "malformed": malformed,
    "oversized": oversized_result,
    "verifier": verifier_result,
    "unknown": unknown,
    "invalid_identifier": invalid_identifier,
    "attempts": len(rows),
    "first_record": json.loads(rows[0][0]) if rows else {},
    "codes": [row[1] for row in rows],
    "audit_chain": raising.verify_audit_chain(space),
}, sort_keys=True))
'''
        embedded = run_embedded(
            root,
            embedded_code,
            [str(embedded_database), str(case_path)],
        )
        try:
            embedded_data = json.loads(embedded.stdout)
        except Exception:
            embedded_data = {}
        record(
            checks,
            "RT-BB-012",
            "malformed embedded input is rejected stably",
            embedded.returncode == 0
            and embedded_data.get("malformed", {}).get("code")
            == "INPUT_NOT_JSON_VALUE",
            (embedded.stdout + embedded.stderr).strip()[:500],
        )
        record(
            checks,
            "RT-BB-013",
            "oversized transition is audited by digest",
            embedded.returncode == 0
            and embedded_data.get("oversized", {}).get("code")
            == "TRANSITION_TOO_LARGE"
            and embedded_data.get("first_record", {}).get("document_type")
            == "aset-seed-oversized-transition-reference"
            and embedded_data.get("attempts") == 2,
            (embedded.stdout + embedded.stderr).strip()[:500],
        )
        record(
            checks,
            "RT-BB-014",
            "proof-verifier exception is isolated and audited",
            embedded.returncode == 0
            and embedded_data.get("verifier", {}).get("code")
            == "PROOF_VERIFIER_ERROR"
            and embedded_data.get("audit_chain") is True
            and "PROOF_VERIFIER_ERROR" in embedded_data.get("codes", []),
            (embedded.stdout + embedded.stderr).strip()[:500],
        )
        record(
            checks,
            "RT-BB-015",
            "unknown trust space has stable boundary rejection",
            embedded.returncode == 0
            and embedded_data.get("unknown", {}).get("code")
            == "TRUST_SPACE_UNKNOWN",
            (embedded.stdout + embedded.stderr).strip()[:500],
        )
        record(
            checks,
            "RT-BB-016",
            "invalid trust-space identifier has stable boundary rejection",
            embedded.returncode == 0
            and embedded_data.get("invalid_identifier", {}).get("code")
            == "TRUST_SPACE_ID_INVALID",
            (embedded.stdout + embedded.stderr).strip()[:500],
        )

        corrupt_guard_code = r'''
import json
import sqlite3
import sys
from pathlib import Path

from aset_seed.proofs import RejectAllProofVerifier
from aset_seed.runtime import DurableSeedRuntime

case = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
database = Path(sys.argv[1])
runtime = DurableSeedRuntime(database, proof_verifier=RejectAllProofVerifier())
connection = sqlite3.connect(database)
try:
    space = connection.execute(
        "SELECT trust_space_id FROM trust_spaces LIMIT 1"
    ).fetchone()[0]
finally:
    connection.close()

def capture(call):
    try:
        call()
    except Exception as error:
        return type(error).__name__
    return "NO_ERROR"

get_state_error = capture(lambda: runtime.get_state(space))
initialize_error = capture(lambda: runtime.initialize(case["initial_genesis"]))
apply_result = runtime.apply(space, case["candidate"])
connection = sqlite3.connect(database)
try:
    attempts = connection.execute(
        "SELECT COUNT(*) FROM transition_attempts WHERE trust_space_id=?",
        (space,),
    ).fetchone()[0]
finally:
    connection.close()
print(json.dumps({
    "get_state_error": get_state_error,
    "initialize_error": initialize_error,
    "apply": apply_result,
    "attempts": attempts,
    "audit_chain": runtime.verify_audit_chain(space),
}, sort_keys=True))
'''
        corrupt_guard = run_embedded(
            root,
            corrupt_guard_code,
            [str(corrupt_database), str(case_path)],
        )
        try:
            corrupt_guard_data = json.loads(corrupt_guard.stdout)
        except Exception:
            corrupt_guard_data = {}
        record(
            checks,
            "RT-BB-017",
            "corrupted stored state cannot be returned, initialized, or executed",
            corrupt_guard.returncode == 0
            and corrupt_guard_data.get("get_state_error") == "StoreError"
            and corrupt_guard_data.get("initialize_error") == "StoreError"
            and corrupt_guard_data.get("apply", {}).get("code")
            == "STORED_STATE_INVALID"
            and corrupt_guard_data.get("attempts") == 5
            and corrupt_guard_data.get("audit_chain") is True,
            (corrupt_guard.stdout + corrupt_guard.stderr).strip()[:500],
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
        "audit_boundary": "built snapshot; public CLI and embedded API",
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

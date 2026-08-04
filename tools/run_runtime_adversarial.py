from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
FIXED = (1980, 1, 1, 0, 0, 0)
CASE = "seed/releases/0.1-rc11/expanded/machine/examples/positive/POS-001.json"


def load_snapshot(path: Path) -> dict[str, bytes]:
    with zipfile.ZipFile(path) as archive:
        return {
            info.filename: archive.read(info)
            for info in archive.infolist()
            if not info.is_dir()
        }


def write_snapshot(path: Path, files: dict[str, bytes]) -> None:
    with zipfile.ZipFile(
        path,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=9,
    ) as archive:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, FIXED)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, files[name])


def safe_extract(snapshot: Path, destination: Path) -> Path:
    with zipfile.ZipFile(snapshot) as archive:
        seen: set[str] = set()
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts or info.filename in seen:
                raise ValueError(f"unsafe ZIP member:{info.filename}")
            seen.add(info.filename)
        archive.extractall(destination)
    root = destination / "ASET"
    if not root.is_dir():
        raise ValueError("snapshot root missing")
    return root


def replace_once(files: dict[str, bytes], name: str, old: bytes, new: bytes) -> None:
    data = files[name]
    if data.count(old) != 1:
        raise ValueError(f"mutation anchor is not unique:{name}")
    files[name] = data.replace(old, new, 1)


def mutate_state_health(files: dict[str, bytes]) -> None:
    replace_once(
        files,
        "ASET/src/aset_seed/runtime.py",
        b"        state_ok = self._validate_stored_states()\n",
        b"        state_ok = True\n",
    )


def mutate_backup_validation(files: dict[str, bytes]) -> None:
    old = (
        b"    def backup(self, destination: Path) -> None:\n"
        b"        status = self.health()\n"
        b"        if (\n"
        b'            status.database_integrity != "ok"\n'
        b'            or status.state_validation != "PASS"\n'
        b'            or status.audit_chain != "PASS"\n'
        b"        ):\n"
        b'            raise StoreError("backup refused because runtime health validation failed")\n'
        b"        self.store.backup(destination)\n"
    )
    new = (
        b"    def backup(self, destination: Path) -> None:\n"
        b"        self.store.backup(destination)\n"
    )
    replace_once(files, "ASET/src/aset_seed/runtime.py", old, new)


def mutate_symlink_guard(files: dict[str, bytes]) -> None:
    name = "ASET/src/aset_seed/store.py"
    replace_once(
        files,
        name,
        b"    status = path.lstat()\n",
        b"    status = path.stat()\n",
    )
    replace_once(
        files,
        name,
        (
            b"        if self.path.is_symlink():\n"
            b'            raise StoreError("database file must not be a symbolic link")\n'
        ),
        b"",
    )
    replace_once(
        files,
        name,
        (
            b"    if stat.S_ISLNK(status.st_mode):\n"
            b'        raise StoreError(f"{label} must not be a symbolic link")\n'
        ),
        b"",
    )
    replace_once(
        files,
        name,
        (
            b"    if not stat.S_ISREG(status.st_mode):\n"
            b'        raise StoreError(f"{label} must be a regular file")\n'
        ),
        b"",
    )
    replace_once(
        files,
        name,
        (
            b"    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR | "
            b'getattr(os, "O_NOFOLLOW", 0)\n'
        ),
        b"    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR\n",
    )


def mutate_malformed_boundary(files: dict[str, bytes]) -> None:
    old = (
        b"        except (TypeError, ValueError, UnicodeError):\n"
        b"            # A non-JSON Python object is not a transition document and cannot be\n"
        b"            # represented safely in the normative transition audit chain.\n"
        b'            return _rejection("INPUT_NOT_JSON_VALUE")\n'
    )
    new = (
        b"        except (TypeError, ValueError, UnicodeError):\n"
        b"            raise\n"
    )
    replace_once(files, "ASET/src/aset_seed/runtime.py", old, new)


def mutate_oversized_audit(files: dict[str, bytes]) -> None:
    replace_once(
        files,
        "ASET/src/aset_seed/runtime.py",
        b'''            if len(serialized) > MAX_TRANSITION_BYTES:
                audit_transition = {
                    "document_type": "aset-seed-oversized-transition-reference",
                    "transition_id": (
                        transition.get("transition_id", "MISSING")
                        if isinstance(transition, dict)
                        else "MISSING"
                    ),
                    "sha256": "sha256:" + hashlib.sha256(serialized).hexdigest(),
                    "size_bytes": len(serialized),
                }
                result = _rejection("TRANSITION_TOO_LARGE")
''',
        b'''            if len(serialized) > MAX_TRANSITION_BYTES:
                return _rejection("TRANSITION_TOO_LARGE")
''',
    )


def mutate_verifier_isolation(files: dict[str, bytes]) -> None:
    replace_once(
        files,
        "ASET/src/aset_seed/runtime.py",
        b'''                        except Exception:
                            result = _rejection("PROOF_VERIFIER_ERROR")
''',
        b'''                        except Exception:
                            raise
''',
    )


def mutate_trust_space_identifier_guard(files: dict[str, bytes]) -> None:
    replace_once(
        files,
        "ASET/src/aset_seed/runtime.py",
        b'''        if not self._trust_space_id_is_valid(trust_space_id):
            return _rejection("TRUST_SPACE_ID_INVALID")
''',
        b"",
    )


def mutate_stored_state_execution_guard(files: dict[str, bytes]) -> None:
    replace_once(
        files,
        "ASET/src/aset_seed/runtime.py",
        b'''                try:
                    state = self._decode_stored_state(row)
                except StoreError:
                    result = _rejection("STORED_STATE_INVALID")
                else:
''',
        b'''                state = json.loads(row["state_json"])
                if True:
''',
    )


def mutate_hmac_content_binding(files: dict[str, bytes]) -> None:
    replace_once(
        files,
        "ASET/src/aset_seed/proofs.py",
        b"        return hmac.compare_digest(expected, claimed)\n",
        b"        return claimed.startswith(\"sha256:\")\n",
    )


MUTATIONS = [
    ("state_health_removed", "RT-BB-009", mutate_state_health),
    ("backup_validation_removed", "RT-BB-010", mutate_backup_validation),
    ("symlink_guard_removed", "RT-BB-011", mutate_symlink_guard),
    ("malformed_boundary_removed", "RT-BB-012", mutate_malformed_boundary),
    ("oversized_audit_removed", "RT-BB-013", mutate_oversized_audit),
    ("verifier_isolation_removed", "RT-BB-014", mutate_verifier_isolation),
    (
        "trust_space_identifier_guard_removed",
        "RT-BB-016",
        mutate_trust_space_identifier_guard,
    ),
    (
        "stored_state_execution_guard_removed",
        "RT-BB-017",
        mutate_stored_state_execution_guard,
    ),
    ("hmac_content_binding_removed", "RT-BB-018", mutate_hmac_content_binding),
]

PROBE = r'''
import json
import os
import sqlite3
import sys
from pathlib import Path

from aset_seed.core import compute_transition_id
from aset_seed.proofs import (
    HmacSha256ProofVerifier,
    RejectAllProofVerifier,
    sign_transition_hmac,
)
from aset_seed.runtime import DurableSeedRuntime, MAX_TRANSITION_BYTES

mode = sys.argv[1]
root = Path(sys.argv[2])
work = Path(sys.argv[3])
case = json.loads((root / sys.argv[4]).read_text(encoding="utf-8"))
database = work / "seed.db"
runtime = DurableSeedRuntime(database, proof_verifier=RejectAllProofVerifier())
state = runtime.initialize(case["initial_genesis"])
space = state["trust_space_id"]
secure = False
details = ""

if mode in {
    "state_health_removed",
    "backup_validation_removed",
    "stored_state_execution_guard_removed",
}:
    connection = sqlite3.connect(database)
    try:
        persisted = json.loads(connection.execute(
            "SELECT state_json FROM trust_spaces LIMIT 1"
        ).fetchone()[0])
        persisted.pop("contexts")
        connection.execute(
            "UPDATE trust_spaces SET state_json=?",
            (json.dumps(persisted, sort_keys=True),),
        )
        connection.commit()
    finally:
        connection.close()

if mode == "state_health_removed":
    status = runtime.health()
    secure = status.state_validation == "FAIL"
    details = status.state_validation
elif mode == "backup_validation_removed":
    destination = work / "backup.db"
    try:
        runtime.backup(destination)
    except Exception:
        secure = not destination.exists()
    else:
        secure = False
    details = f"backup_exists={destination.exists()}"
elif mode == "symlink_guard_removed":
    if os.name != "posix":
        secure = True
        details = "not applicable"
    else:
        link = work / "link.db"
        link.symlink_to(database)
        try:
            DurableSeedRuntime(link)
        except Exception:
            secure = True
        else:
            secure = False
        details = f"accepted={not secure}"
elif mode == "malformed_boundary_removed":
    try:
        result = runtime.apply(space, {"not_json": {"a", "b"}})
    except Exception as error:
        secure = False
        details = type(error).__name__
    else:
        secure = result.get("code") == "INPUT_NOT_JSON_VALUE"
        details = result.get("code", "")
elif mode == "oversized_audit_removed":
    transition = dict(case["candidate"])
    transition["oversized_untrusted_input"] = "x" * (MAX_TRANSITION_BYTES + 1)
    result = runtime.apply(space, transition)
    connection = sqlite3.connect(database)
    try:
        count = connection.execute("SELECT COUNT(*) FROM transition_attempts").fetchone()[0]
    finally:
        connection.close()
    secure = result.get("code") == "TRANSITION_TOO_LARGE" and count == 1
    details = f"code={result.get('code')}; attempts={count}"
elif mode == "verifier_isolation_removed":
    class RaisingVerifier:
        profile_id = "TEST_RAISING_VERIFIER"
        def verify(self, transition):
            raise RuntimeError("boom")
    raising = DurableSeedRuntime(database, proof_verifier=RaisingVerifier())
    try:
        result = raising.apply(space, case["candidate"])
    except Exception as error:
        secure = False
        details = type(error).__name__
    else:
        connection = sqlite3.connect(database)
        try:
            count = connection.execute("SELECT COUNT(*) FROM transition_attempts").fetchone()[0]
        finally:
            connection.close()
        secure = result.get("code") == "PROOF_VERIFIER_ERROR" and count == 1
        details = f"code={result.get('code')}; attempts={count}"
elif mode == "trust_space_identifier_guard_removed":
    try:
        result = runtime.apply({"not": "an identifier"}, {})
    except Exception as error:
        secure = False
        details = type(error).__name__
    else:
        secure = result.get("code") == "TRUST_SPACE_ID_INVALID"
        details = result.get("code", "")
elif mode == "stored_state_execution_guard_removed":
    try:
        result = runtime.apply(space, case["candidate"])
    except Exception as error:
        secure = False
        details = type(error).__name__
    else:
        secure = result.get("code") == "STORED_STATE_INVALID"
        details = result.get("code", "")
elif mode == "hmac_content_binding_removed":
    secret = b"runtime-adversarial-hmac-secret-32-bytes"
    hmac_runtime = DurableSeedRuntime(
        database,
        proof_verifier=HmacSha256ProofVerifier({"principal:bootstrap": secret}),
    )
    signed = sign_transition_hmac(case["candidate"], secret)
    signed["payload"]["local_alias"] = "modified-after-proof"
    signed["transition_id"] = compute_transition_id(signed)
    result = hmac_runtime.apply(space, signed)
    secure = result.get("code") == "PROOF_REJECTED"
    details = result.get("code", "")

print(json.dumps({"secure": secure, "details": details}, sort_keys=True))
'''


def run_probe(root: Path, mode: str, work: Path) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(root / "src")
    return subprocess.run(
        [sys.executable, "-c", PROBE, mode, str(root), str(work), CASE],
        cwd=root,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "snapshot",
        nargs="?",
        default="dist/ASET-Repository-Snapshot.zip",
    )
    parser.add_argument(
        "--output",
        default="dist/runtime-adversarial-results.json",
    )
    args = parser.parse_args()

    snapshot = ROOT / args.snapshot
    if not snapshot.is_file():
        print(f"RUNTIME_ADVERSARIAL_FATAL=missing snapshot:{snapshot}")
        return 1

    baseline = load_snapshot(snapshot)
    results: list[dict[str, object]] = []
    failed = False

    with tempfile.TemporaryDirectory(prefix="aset-runtime-adversarial-") as directory:
        temporary = Path(directory)
        for name, expected_check, mutation in MUTATIONS:
            files = dict(baseline)
            mutation(files)
            candidate = temporary / f"{name}.zip"
            write_snapshot(candidate, files)
            extracted = temporary / f"extract-{name}"
            root = safe_extract(candidate, extracted)
            work = temporary / f"work-{name}"
            work.mkdir()
            result = run_probe(root, name, work)
            try:
                probe = json.loads(result.stdout)
            except Exception:
                probe = {"secure": True, "details": result.stderr[:300]}
            # A successful mutation test requires the black-box security property
            # to become false after the targeted implementation mutation.
            passed = result.returncode == 0 and probe.get("secure") is False
            failed = failed or not passed
            results.append(
                {
                    "mutation": name,
                    "expected_failed_check": expected_check,
                    "probe_returncode": result.returncode,
                    "observed": probe,
                    "status": "PASS" if passed else "FAIL",
                }
            )
            print(
                f"RUNTIME_ADVERSARIAL_{name.upper()}="
                f"{'PASS' if passed else 'FAIL'}"
            )

    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "document_type": "aset-seed-runtime-adversarial-results",
        "version": 1,
        "verdict": "FAIL" if failed else "PASS",
        "mutations": results,
    }
    output.write_text(
        json.dumps(payload, sort_keys=True, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print(f"RUNTIME_BLACKBOX_ADVERSARIAL={payload['verdict']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())

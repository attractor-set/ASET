from __future__ import annotations

import copy
import json
import os
import sqlite3
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from aset_seed import DurableSeedRuntime, HmacSha256ProofVerifier, RejectAllProofVerifier
from aset_seed.jsonio import StrictJsonError, loads_strict
from aset_seed.proofs import sign_transition_hmac
from aset_seed.store import StoreError

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "seed/releases/0.1-rc11/expanded/machine/examples/positive/POS-001.json"
SECRET = b"rc12-test-secret-material-32-bytes!!"


def case():
    return json.loads(CASE.read_text(encoding="utf-8"))


def signed_candidate():
    return sign_transition_hmac(case()["candidate"], SECRET)


def verifier():
    return HmacSha256ProofVerifier({"principal:bootstrap": SECRET})


def test_default_runtime_fails_closed_on_proof(tmp_path):
    data = case()
    runtime = DurableSeedRuntime(tmp_path / "seed.db", proof_verifier=RejectAllProofVerifier())
    state = runtime.initialize(data["initial_genesis"])
    before = state["current_state_root"]
    result = runtime.apply(state["trust_space_id"], data["candidate"])
    assert result == {
        "accepted": False,
        "code": "PROOF_REJECTED",
        "state_changed": False,
        "artifacts": [],
    }
    assert runtime.get_state(state["trust_space_id"])["current_state_root"] == before
    assert runtime.verify_audit_chain(state["trust_space_id"])


def test_hmac_transition_commits_state_and_audit_atomically(tmp_path):
    data = case()
    runtime = DurableSeedRuntime(tmp_path / "seed.db", proof_verifier=verifier())
    state = runtime.initialize(data["initial_genesis"])
    result = runtime.apply(state["trust_space_id"], signed_candidate())
    assert result["accepted"] is True
    assert result["state_changed"] is True
    after = runtime.get_state(state["trust_space_id"])
    assert after["current_state_root"] != state["current_state_root"]
    runtime.validate(state["trust_space_id"])
    assert runtime.verify_audit_chain(state["trust_space_id"])
    health = runtime.health()
    assert health.database_integrity == "ok"
    assert health.audit_chain == "PASS"


def test_wrong_hmac_is_rejected_without_state_change(tmp_path):
    data = case()
    runtime = DurableSeedRuntime(tmp_path / "seed.db", proof_verifier=verifier())
    state = runtime.initialize(data["initial_genesis"])
    transition = copy.deepcopy(data["candidate"])
    transition["authn"]["proof_digest"] = "sha256:" + "0" * 64
    result = runtime.apply(state["trust_space_id"], transition)
    assert result["code"] == "PROOF_REJECTED"
    assert (
        runtime.get_state(state["trust_space_id"])["current_state_root"]
        == state["current_state_root"]
    )


def test_reopen_and_backup_preserve_integrity(tmp_path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    state = runtime.initialize(data["initial_genesis"])
    runtime.apply(state["trust_space_id"], signed_candidate())
    expected = runtime.get_state(state["trust_space_id"])["current_state_root"]

    reopened = DurableSeedRuntime(database, proof_verifier=verifier())
    assert reopened.get_state(state["trust_space_id"])["current_state_root"] == expected
    assert reopened.verify_audit_chain(state["trust_space_id"])

    backup = tmp_path / "backup.db"
    reopened.backup(backup)
    connection = sqlite3.connect(backup)
    try:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        profile = connection.execute(
            "SELECT value FROM metadata WHERE key='profile_id'"
        ).fetchone()[0]
        assert profile == "ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1"
    finally:
        connection.close()


def test_concurrent_replay_is_serialized(tmp_path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier(), busy_timeout_ms=20000)
    state = runtime.initialize(data["initial_genesis"])
    transition = signed_candidate()

    def apply_once(_):
        worker = DurableSeedRuntime(database, proof_verifier=verifier(), busy_timeout_ms=20000)
        return worker.apply(state["trust_space_id"], transition)

    with ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(apply_once, range(6)))
    assert sum(result["state_changed"] for result in results) == 1
    assert all(result["accepted"] for result in results)
    assert runtime.verify_audit_chain(state["trust_space_id"])


def test_strict_json_rejects_duplicate_members():
    with pytest.raises(StrictJsonError):
        loads_strict('{"x":1,"x":2}')


def test_store_profile_mismatch_is_rejected(tmp_path):
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    runtime.initialize(case()["initial_genesis"])
    connection = sqlite3.connect(database)
    try:
        connection.execute("UPDATE metadata SET value='wrong' WHERE key='profile_id'")
        connection.commit()
    finally:
        connection.close()
    with pytest.raises(StoreError):
        DurableSeedRuntime(database, proof_verifier=verifier())


def test_initialize_is_idempotent_without_nested_connection(tmp_path):
    data = case()
    runtime = DurableSeedRuntime(tmp_path / "seed.db", proof_verifier=verifier())
    first = runtime.initialize(data["initial_genesis"])
    second = runtime.initialize(data["initial_genesis"])
    assert second == first


def test_backup_refuses_to_overwrite_existing_file(tmp_path):
    runtime = DurableSeedRuntime(tmp_path / "seed.db", proof_verifier=verifier())
    runtime.initialize(case()["initial_genesis"])
    backup = tmp_path / "backup.db"
    backup.write_text("do not overwrite", encoding="utf-8")
    with pytest.raises(StoreError):
        runtime.backup(backup)
    assert backup.read_text(encoding="utf-8") == "do not overwrite"


def test_audit_chain_rejects_redundant_column_tampering(tmp_path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    state = runtime.initialize(data["initial_genesis"])
    runtime.apply(state["trust_space_id"], signed_candidate())
    connection = sqlite3.connect(database)
    try:
        connection.execute("UPDATE transition_attempts SET accepted=0")
        connection.commit()
    finally:
        connection.close()
    assert not runtime.verify_audit_chain(state["trust_space_id"])


def test_audit_chain_is_bound_to_current_state_revision(tmp_path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    state = runtime.initialize(data["initial_genesis"])
    runtime.apply(state["trust_space_id"], signed_candidate())
    connection = sqlite3.connect(database)
    try:
        connection.execute("UPDATE trust_spaces SET revision=0")
        connection.commit()
    finally:
        connection.close()
    assert not runtime.verify_audit_chain(state["trust_space_id"])


def test_existing_database_must_be_private_on_posix(tmp_path):
    if os.name != "posix":
        pytest.skip("POSIX permission profile only")
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    runtime.initialize(case()["initial_genesis"])
    os.chmod(database, 0o644)
    with pytest.raises(StoreError):
        DurableSeedRuntime(database, proof_verifier=verifier())

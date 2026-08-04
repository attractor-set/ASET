from __future__ import annotations

import copy
import json
import os
import sqlite3
from pathlib import Path

import pytest

from aset_seed.proofs import (
    HmacSha256ProofVerifier,
    RejectAllProofVerifier,
    sign_transition_hmac,
)
from aset_seed.runtime import MAX_TRANSITION_BYTES, DurableSeedRuntime
from aset_seed.store import StoreError

ROOT = Path(__file__).resolve().parents[1]
CASE = ROOT / "seed/releases/0.1-rc11/expanded/machine/examples/positive/POS-001.json"
SECRET = b"rc12-prefreeze-hardening-secret!!"


def case() -> dict:
    return json.loads(CASE.read_text(encoding="utf-8"))


def verifier() -> HmacSha256ProofVerifier:
    return HmacSha256ProofVerifier({"principal:bootstrap": SECRET})


def attempt_count(database: Path) -> int:
    connection = sqlite3.connect(database)
    try:
        return connection.execute("SELECT COUNT(*) FROM transition_attempts").fetchone()[0]
    finally:
        connection.close()


def test_health_fails_on_schema_invalid_persisted_state(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    state = runtime.initialize(data["initial_genesis"])

    connection = sqlite3.connect(database)
    try:
        persisted = json.loads(
            connection.execute(
                "SELECT state_json FROM trust_spaces WHERE trust_space_id=?",
                (state["trust_space_id"],),
            ).fetchone()[0]
        )
        persisted.pop("contexts")
        connection.execute(
            "UPDATE trust_spaces SET state_json=? WHERE trust_space_id=?",
            (json.dumps(persisted, sort_keys=True), state["trust_space_id"]),
        )
        connection.commit()
    finally:
        connection.close()

    status = runtime.health()
    assert status.database_integrity == "ok"
    assert status.state_validation == "FAIL"


def test_health_fails_on_stored_root_mismatch(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    runtime.initialize(data["initial_genesis"])

    connection = sqlite3.connect(database)
    try:
        connection.execute(
            "UPDATE trust_spaces SET state_root=?",
            ("sha256:" + "f" * 64,),
        )
        connection.commit()
    finally:
        connection.close()

    assert runtime.health().state_validation == "FAIL"


def test_oversized_transition_is_rejected_and_audited_by_digest(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=RejectAllProofVerifier())
    state = runtime.initialize(data["initial_genesis"])
    transition = copy.deepcopy(data["candidate"])
    transition["oversized_untrusted_input"] = "x" * (MAX_TRANSITION_BYTES + 1)

    result = runtime.apply(state["trust_space_id"], transition)

    assert result["code"] == "TRANSITION_TOO_LARGE"
    assert attempt_count(database) == 1
    connection = sqlite3.connect(database)
    try:
        recorded = json.loads(
            connection.execute("SELECT transition_json FROM transition_attempts").fetchone()[0]
        )
    finally:
        connection.close()
    assert recorded["document_type"] == "aset-seed-oversized-transition-reference"
    assert recorded["size_bytes"] > MAX_TRANSITION_BYTES
    assert recorded["sha256"].startswith("sha256:")
    assert runtime.verify_audit_chain(state["trust_space_id"])


def test_non_json_embedded_input_returns_stable_boundary_rejection(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=RejectAllProofVerifier())
    state = runtime.initialize(data["initial_genesis"])

    result = runtime.apply(state["trust_space_id"], {"not_json": {"a", "b"}})

    assert result == {
        "accepted": False,
        "code": "INPUT_NOT_JSON_VALUE",
        "state_changed": False,
        "artifacts": [],
    }
    assert attempt_count(database) == 0


def test_unknown_trust_space_returns_stable_boundary_rejection(tmp_path: Path):
    runtime = DurableSeedRuntime(tmp_path / "seed.db")
    result = runtime.apply("ts:" + "0" * 64, {})
    assert result == {
        "accepted": False,
        "code": "TRUST_SPACE_UNKNOWN",
        "state_changed": False,
        "artifacts": [],
    }


def test_invalid_trust_space_identifier_returns_stable_boundary_rejection(
    tmp_path: Path,
):
    runtime = DurableSeedRuntime(tmp_path / "seed.db")
    result = runtime.apply({"not": "an identifier"}, {})
    assert result == {
        "accepted": False,
        "code": "TRUST_SPACE_ID_INVALID",
        "state_changed": False,
        "artifacts": [],
    }


class RaisingVerifier:
    profile_id = "TEST_RAISING_VERIFIER"

    def verify(self, transition: dict) -> bool:
        raise RuntimeError("secret diagnostic must not escape")


def test_proof_verifier_exception_is_stable_and_audited(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=RaisingVerifier())
    state = runtime.initialize(data["initial_genesis"])

    result = runtime.apply(state["trust_space_id"], data["candidate"])

    assert result == {
        "accepted": False,
        "code": "PROOF_VERIFIER_ERROR",
        "state_changed": False,
        "artifacts": [],
    }
    assert attempt_count(database) == 1
    assert runtime.verify_audit_chain(state["trust_space_id"])


def test_hmac_proof_is_bound_to_exact_transition_content(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    state = runtime.initialize(data["initial_genesis"])
    transition = sign_transition_hmac(data["candidate"], SECRET)
    transition["payload"]["local_alias"] = "modified-after-proof"
    transition["transition_id"] = data["candidate"]["transition_id"]

    result = runtime.apply(state["trust_space_id"], transition)

    assert result["code"] == "PROOF_REJECTED"
    assert result["state_changed"] is False
    assert runtime.get_state(state["trust_space_id"])["current_state_root"] == state[
        "current_state_root"
    ]


def test_backup_rejects_logically_invalid_state(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    runtime.initialize(data["initial_genesis"])

    connection = sqlite3.connect(database)
    try:
        persisted = json.loads(
            connection.execute("SELECT state_json FROM trust_spaces").fetchone()[0]
        )
        persisted.pop("contexts")
        connection.execute(
            "UPDATE trust_spaces SET state_json=?",
            (json.dumps(persisted, sort_keys=True),),
        )
        connection.commit()
    finally:
        connection.close()

    destination = tmp_path / "invalid-backup.db"
    with pytest.raises(StoreError, match="health validation"):
        runtime.backup(destination)
    assert not destination.exists()


def test_corrupted_stored_state_is_not_returned_or_executed(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    state = runtime.initialize(data["initial_genesis"])

    connection = sqlite3.connect(database)
    try:
        persisted = json.loads(
            connection.execute("SELECT state_json FROM trust_spaces").fetchone()[0]
        )
        persisted.pop("contexts")
        connection.execute(
            "UPDATE trust_spaces SET state_json=?",
            (json.dumps(persisted, sort_keys=True),),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(StoreError, match="stored state validation failed"):
        runtime.get_state(state["trust_space_id"])

    result = runtime.apply(state["trust_space_id"], data["candidate"])
    assert result["code"] == "STORED_STATE_INVALID"
    assert attempt_count(database) == 1
    assert runtime.verify_audit_chain(state["trust_space_id"])


def test_idempotent_initialize_rejects_corrupted_stored_state(tmp_path: Path):
    data = case()
    database = tmp_path / "seed.db"
    runtime = DurableSeedRuntime(database, proof_verifier=verifier())
    runtime.initialize(data["initial_genesis"])
    connection = sqlite3.connect(database)
    try:
        connection.execute(
            "UPDATE trust_spaces SET state_json='{}'",
        )
        connection.commit()
    finally:
        connection.close()
    with pytest.raises(StoreError, match="stored state validation failed"):
        runtime.initialize(data["initial_genesis"])


def test_existing_database_symlink_is_rejected(tmp_path: Path):
    if os.name != "posix":
        pytest.skip("POSIX symlink profile only")
    target = tmp_path / "target.db"
    runtime = DurableSeedRuntime(target)
    runtime.initialize(case()["initial_genesis"])
    link = tmp_path / "link.db"
    link.symlink_to(target)
    with pytest.raises(StoreError, match="symbolic link"):
        DurableSeedRuntime(link)


def test_runtime_dependency_is_exactly_pinned():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'dependencies = ["jsonschema==4.26.0"]' in pyproject


def test_pinned_preverified_profile_is_not_in_production_canon():
    model = json.loads(
        (ROOT / "seed/canonical/source/seed-model.json").read_text(encoding="utf-8")
    )
    protocol = json.loads(
        (ROOT / "seed/canonical/protocol/protocol-profile.json").read_text(
            encoding="utf-8"
        )
    )
    assert model["runtime_profile"]["proof_boundary"]["provided_profiles"] == [
        "HMAC_SHA256_V1"
    ]
    assert "PINNED_PREVERIFIED_DIGEST_V1" not in protocol["proof_profiles"]


from __future__ import annotations

import copy
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from . import core
from .jsonio import dumps_canonical
from .proofs import ProofVerifier, RejectAllProofVerifier
from .store import PROFILE_ID, SqliteStore, StoreError

MAX_TRANSITION_BYTES = 8 * 1024 * 1024
ZERO_HASH = "sha256:" + "0" * 64


@dataclass(frozen=True)
class RuntimeStatus:
    profile_id: str
    implementation_version: str
    wire_version: str
    seed_semantics_id: str
    proof_profile: str
    database_integrity: str
    audit_chain: str


class DurableSeedRuntime:
    def __init__(
        self,
        database: Path,
        *,
        proof_verifier: ProofVerifier | None = None,
        busy_timeout_ms: int = 5000,
    ) -> None:
        self.store = SqliteStore(database, busy_timeout_ms=busy_timeout_ms)
        self.proof_verifier = proof_verifier or RejectAllProofVerifier()

    @staticmethod
    def _now() -> str:
        return datetime.now(UTC).isoformat(timespec="microseconds").replace("+00:00", "Z")

    def initialize(self, genesis: dict[str, Any]) -> dict[str, Any]:
        state = core.initialize_state(copy.deepcopy(genesis))
        trust_space_id = state["trust_space_id"]
        state_json = dumps_canonical(state)
        now = self._now()
        with self.store.transaction() as connection:
            existing = connection.execute(
                "SELECT state_json, state_root FROM trust_spaces WHERE trust_space_id=?",
                (trust_space_id,),
            ).fetchone()
            if existing is not None:
                if existing["state_root"] != state["current_state_root"]:
                    raise StoreError("trust space already exists with a different root")
                return json.loads(existing["state_json"])
            connection.execute(
                """
                INSERT INTO trust_spaces(
                    trust_space_id, state_json, state_root, revision, created_at, updated_at
                ) VALUES (?, ?, ?, 0, ?, ?)
                """,
                (trust_space_id, state_json, state["current_state_root"], now, now),
            )
        return state

    def get_state(self, trust_space_id: str) -> dict[str, Any]:
        connection = self.store.connect()
        try:
            row = connection.execute(
                "SELECT state_json FROM trust_spaces WHERE trust_space_id=?",
                (trust_space_id,),
            ).fetchone()
        finally:
            connection.close()
        if row is None:
            raise StoreError("trust space is unknown")
        return json.loads(row["state_json"])

    def _last_audit_hash(self, connection, trust_space_id: str) -> str:
        row = connection.execute(
            """
            SELECT entry_hash FROM transition_attempts
            WHERE trust_space_id=? ORDER BY sequence DESC LIMIT 1
            """,
            (trust_space_id,),
        ).fetchone()
        return ZERO_HASH if row is None else row["entry_hash"]

    def _record_attempt(
        self,
        connection,
        *,
        trust_space_id: str,
        transition: dict[str, Any],
        result: dict[str, Any],
        before_root: str,
        after_root: str,
        created_at: str,
    ) -> None:
        transition_json = dumps_canonical(transition)
        result_record = {
            "accepted": bool(result["accepted"]),
            "code": str(result["code"]),
            "state_changed": bool(result["state_changed"]),
            "artifacts": list(result.get("artifacts", [])),
        }
        result_json = dumps_canonical(result_record)
        previous = self._last_audit_hash(connection, trust_space_id)
        entry_material = {
            "trust_space_id": trust_space_id,
            "transition_id": transition.get("transition_id", "MISSING"),
            "transition_json": transition_json,
            "result_json": result_json,
            "before_state_root": before_root,
            "after_state_root": after_root,
            "proof_profile": self.proof_verifier.profile_id,
            "previous_entry_hash": previous,
            "created_at": created_at,
        }
        entry_hash = core.domain_digest("ASET/RuntimeAuditEntry/v1", entry_material)
        connection.execute(
            """
            INSERT INTO transition_attempts(
                trust_space_id, transition_id, transition_json, result_json,
                before_state_root, after_state_root, accepted, state_changed,
                code, proof_profile, previous_entry_hash, entry_hash, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trust_space_id,
                transition.get("transition_id", "MISSING"),
                transition_json,
                result_json,
                before_root,
                after_root,
                int(bool(result["accepted"])),
                int(bool(result["state_changed"])),
                result["code"],
                self.proof_verifier.profile_id,
                previous,
                entry_hash,
                created_at,
            ),
        )

    def apply(self, trust_space_id: str, transition: dict[str, Any]) -> dict[str, Any]:
        serialized = dumps_canonical(transition).encode("utf-8")
        if len(serialized) > MAX_TRANSITION_BYTES:
            return {
                "accepted": False,
                "code": "TRANSITION_TOO_LARGE",
                "state_changed": False,
                "artifacts": [],
            }
        now = self._now()
        with self.store.transaction() as connection:
            row = connection.execute(
                "SELECT state_json, state_root, revision FROM trust_spaces WHERE trust_space_id=?",
                (trust_space_id,),
            ).fetchone()
            if row is None:
                raise StoreError("trust space is unknown")
            state = json.loads(row["state_json"])
            before_root = row["state_root"]
            try:
                core.validate_transition(transition)
            except core.SeedError as error:
                result = {
                    "accepted": False,
                    "code": error.code,
                    "state_changed": False,
                    "artifacts": [],
                }
            else:
                if not self.proof_verifier.verify(transition):
                    result = {
                        "accepted": False,
                        "code": "PROOF_REJECTED",
                        "state_changed": False,
                        "artifacts": [],
                    }
                else:
                    result = core.apply_transition(state, copy.deepcopy(transition))
            after_root = before_root
            if result["accepted"] and result["state_changed"]:
                new_state = result["state"]
                after_root = new_state["current_state_root"]
                connection.execute(
                    """
                    UPDATE trust_spaces
                    SET state_json=?, state_root=?, revision=?, updated_at=?
                    WHERE trust_space_id=? AND revision=?
                    """,
                    (
                        dumps_canonical(new_state),
                        after_root,
                        row["revision"] + 1,
                        now,
                        trust_space_id,
                        row["revision"],
                    ),
                )
                result = {key: value for key, value in result.items() if key != "state"}
            else:
                result = {key: value for key, value in result.items() if key != "state"}
            self._record_attempt(
                connection,
                trust_space_id=trust_space_id,
                transition=transition,
                result=result,
                before_root=before_root,
                after_root=after_root,
                created_at=now,
            )
        return result

    def validate(self, trust_space_id: str) -> None:
        core.validate_state(self.get_state(trust_space_id))

    def verify_audit_chain(self, trust_space_id: str) -> bool:
        connection = self.store.connect()
        try:
            rows = connection.execute(
                """
                SELECT * FROM transition_attempts
                WHERE trust_space_id=? ORDER BY sequence
                """,
                (trust_space_id,),
            ).fetchall()
        finally:
            connection.close()
        previous = ZERO_HASH
        changed_count = 0
        last_after_root: str | None = None
        for row in rows:
            if row["previous_entry_hash"] != previous:
                return False
            try:
                result = json.loads(row["result_json"])
            except json.JSONDecodeError:
                return False
            if (
                bool(row["accepted"]) != bool(result.get("accepted"))
                or bool(row["state_changed"]) != bool(result.get("state_changed"))
                or row["code"] != result.get("code")
            ):
                return False
            material = {
                "trust_space_id": row["trust_space_id"],
                "transition_id": row["transition_id"],
                "transition_json": row["transition_json"],
                "result_json": row["result_json"],
                "before_state_root": row["before_state_root"],
                "after_state_root": row["after_state_root"],
                "proof_profile": row["proof_profile"],
                "previous_entry_hash": row["previous_entry_hash"],
                "created_at": row["created_at"],
            }
            expected = core.domain_digest("ASET/RuntimeAuditEntry/v1", material)
            if expected != row["entry_hash"]:
                return False
            changed_count += int(bool(row["state_changed"]))
            last_after_root = row["after_state_root"]
            previous = row["entry_hash"]

        connection = self.store.connect()
        try:
            state_row = connection.execute(
                "SELECT state_root, revision FROM trust_spaces WHERE trust_space_id=?",
                (trust_space_id,),
            ).fetchone()
        finally:
            connection.close()
        if state_row is None:
            return False
        if changed_count != state_row["revision"]:
            return False
        return last_after_root is None or last_after_root == state_row["state_root"]

    def health(self) -> RuntimeStatus:
        connection = self.store.connect()
        try:
            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            spaces = [
                row[0]
                for row in connection.execute(
                    "SELECT trust_space_id FROM trust_spaces"
                )
            ]
        finally:
            connection.close()
        audit_ok = all(self.verify_audit_chain(space) for space in spaces)
        return RuntimeStatus(
            profile_id=PROFILE_ID,
            implementation_version=core.IMPLEMENTATION_VERSION,
            wire_version=core.VERSION,
            seed_semantics_id=core.SEED_SEMANTICS_ID,
            proof_profile=self.proof_verifier.profile_id,
            database_integrity=str(integrity),
            audit_chain="PASS" if audit_ok else "FAIL",
        )

    def backup(self, destination: Path) -> None:
        self.store.backup(destination)

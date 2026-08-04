from __future__ import annotations

import contextlib
import os
import sqlite3
import stat
from collections.abc import Iterator
from pathlib import Path

SCHEMA_VERSION = "1"
PROFILE_ID = "ASET-SEED-RUNTIME-SQLITE-SINGLE-NODE-V1"


class StoreError(RuntimeError):
    pass


def _reserve_private_file(path: Path) -> None:
    flags = os.O_CREAT | os.O_EXCL | os.O_RDWR
    descriptor = os.open(path, flags, 0o600)
    os.close(descriptor)


def _require_private_posix_file(path: Path, label: str) -> None:
    if os.name != "posix":
        return
    mode = stat.S_IMODE(path.stat().st_mode)
    if mode & 0o077:
        raise StoreError(f"{label} must not be group/world accessible")


class SqliteStore:
    def __init__(self, path: Path, *, busy_timeout_ms: int = 5000) -> None:
        if busy_timeout_ms <= 0:
            raise ValueError("busy_timeout_ms must be positive")
        self.path = Path(path)
        self.busy_timeout_ms = busy_timeout_ms
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            _reserve_private_file(self.path)
        _require_private_posix_file(self.path, "database file")
        self._initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            self.path,
            timeout=self.busy_timeout_ms / 1000,
            isolation_level=None,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys=ON")
        connection.execute(f"PRAGMA busy_timeout={self.busy_timeout_ms}")
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA synchronous=FULL")
        return connection

    @contextlib.contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        connection = self.connect()
        try:
            connection.execute("BEGIN IMMEDIATE")
            yield connection
            connection.execute("COMMIT")
        except BaseException:
            with contextlib.suppress(sqlite3.Error):
                connection.execute("ROLLBACK")
            raise
        finally:
            connection.close()

    def _initialize(self) -> None:
        connection = self.connect()
        try:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS trust_spaces (
                    trust_space_id TEXT PRIMARY KEY,
                    state_json TEXT NOT NULL,
                    state_root TEXT NOT NULL,
                    revision INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS transition_attempts (
                    sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                    trust_space_id TEXT NOT NULL,
                    transition_id TEXT NOT NULL,
                    transition_json TEXT NOT NULL,
                    result_json TEXT NOT NULL,
                    before_state_root TEXT NOT NULL,
                    after_state_root TEXT NOT NULL,
                    accepted INTEGER NOT NULL CHECK (accepted IN (0, 1)),
                    state_changed INTEGER NOT NULL CHECK (state_changed IN (0, 1)),
                    code TEXT NOT NULL,
                    proof_profile TEXT NOT NULL,
                    previous_entry_hash TEXT NOT NULL,
                    entry_hash TEXT NOT NULL UNIQUE,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (trust_space_id) REFERENCES trust_spaces(trust_space_id)
                );
                CREATE INDEX IF NOT EXISTS idx_transition_attempts_space_sequence
                    ON transition_attempts(trust_space_id, sequence);
                CREATE INDEX IF NOT EXISTS idx_transition_attempts_transition
                    ON transition_attempts(trust_space_id, transition_id);
                """
            )
            expected = {"schema_version": SCHEMA_VERSION, "profile_id": PROFILE_ID}
            for key, value in expected.items():
                row = connection.execute(
                    "SELECT value FROM metadata WHERE key=?",
                    (key,),
                ).fetchone()
                if row is None:
                    connection.execute(
                        "INSERT INTO metadata(key, value) VALUES (?, ?)",
                        (key, value),
                    )
                elif row["value"] != value:
                    raise StoreError(f"database metadata mismatch for {key}")
        finally:
            connection.close()

    def backup(self, destination: Path) -> None:
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)
        try:
            _reserve_private_file(destination)
        except FileExistsError as error:
            raise StoreError("backup destination already exists") from error

        source = self.connect()
        target = sqlite3.connect(destination)
        succeeded = False
        try:
            source.backup(target)
            integrity = target.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise StoreError(f"backup integrity check failed: {integrity}")
            succeeded = True
        finally:
            target.close()
            source.close()
            if not succeeded:
                with contextlib.suppress(OSError):
                    destination.unlink()
        _require_private_posix_file(destination, "backup file")

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from aset_seed.cli import _load_verifier
from aset_seed.jsonio import StrictJsonError


def test_proof_secret_file_must_be_private_on_posix(tmp_path: Path):
    if os.name != "posix":
        pytest.skip("POSIX permission profile only")
    path = tmp_path / "secrets.json"
    path.write_text(
        json.dumps(
            {
                "document_type": "aset-seed-hmac-secret-map",
                "profile": "HMAC_SHA256_V1",
                "secrets": {},
            }
        ),
        encoding="utf-8",
    )
    os.chmod(path, 0o644)
    with pytest.raises(StrictJsonError):
        _load_verifier(path)
    os.chmod(path, 0o600)
    verifier = _load_verifier(path)
    assert verifier.profile_id == "HMAC_SHA256_V1"


def test_proof_secret_values_must_decode_to_32_bytes(tmp_path: Path):
    path = tmp_path / "secrets.json"
    path.write_text(
        json.dumps(
            {
                "document_type": "aset-seed-hmac-secret-map",
                "profile": "HMAC_SHA256_V1",
                "secrets": {"principal:test": "c2hvcnQ="},
            }
        ),
        encoding="utf-8",
    )
    if os.name == "posix":
        os.chmod(path, 0o600)
    with pytest.raises(ValueError):
        _load_verifier(path)


from __future__ import annotations

import base64
import copy
import hashlib
import hmac
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from .core import canonical_bytes, compute_transition_id


class ProofVerifier(Protocol):
    profile_id: str

    def verify(self, transition: dict) -> bool:
        """Return True only when the transition proof is accepted."""


@dataclass(frozen=True)
class RejectAllProofVerifier:
    profile_id: str = "REJECT_ALL"

    def verify(self, transition: dict) -> bool:
        return False


def proof_material(transition: dict) -> bytes:
    material = copy.deepcopy(transition)
    material.pop("transition_id", None)
    authn = material.get("authn")
    if isinstance(authn, dict):
        authn.pop("proof_digest", None)
    return canonical_bytes(material)


@dataclass(frozen=True)
class HmacSha256ProofVerifier:
    secrets: Mapping[str, bytes]
    profile_id: str = "HMAC_SHA256_V1"

    @classmethod
    def from_base64(cls, secrets: Mapping[str, str]) -> HmacSha256ProofVerifier:
        decoded: dict[str, bytes] = {}
        for principal, encoded in secrets.items():
            if not isinstance(principal, str) or not principal:
                raise ValueError("proof principal identifiers must be non-empty strings")
            secret = base64.b64decode(encoded, validate=True)
            if len(secret) < 32:
                raise ValueError("HMAC secrets must contain at least 32 bytes")
            decoded[principal] = secret
        return cls(decoded)

    def verify(self, transition: dict) -> bool:
        authn = transition.get("authn")
        if not isinstance(authn, dict):
            return False
        principal = authn.get("signer_principal_id")
        claimed = authn.get("proof_digest")
        if not isinstance(principal, str) or not isinstance(claimed, str):
            return False
        secret = self.secrets.get(principal)
        if secret is None or len(secret) < 32:
            return False
        expected = "sha256:" + hmac.new(
            secret,
            proof_material(transition),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, claimed)


def sign_transition_hmac(transition: dict, secret: bytes) -> dict:
    if len(secret) < 32:
        raise ValueError("HMAC secret must contain at least 32 bytes")
    signed = copy.deepcopy(transition)
    authn = signed.setdefault("authn", {})
    authn["proof_digest"] = "sha256:" + hmac.new(
        secret,
        proof_material(signed),
        hashlib.sha256,
    ).hexdigest()
    signed["transition_id"] = compute_transition_id(signed)
    return signed

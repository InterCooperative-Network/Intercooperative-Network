from __future__ import annotations

import base64
import hashlib
import json
from typing import Any, Tuple

from nacl import signing
from nacl.exceptions import BadSignatureError


def canonicalize_json(obj: Any) -> bytes:
    """Return deterministic JSON bytes: sorted keys, no spaces, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def compute_hash(data: Any, prev_hash: str | None) -> Tuple[str, str]:
    """
    Compute payload hash and row hash.
    - payload_hash = sha256(canonicalize_json(data))
    - row_hash = sha256(prev_hash || payload_hash) where prev_hash may be empty string
    Returns (payload_hash, row_hash)
    """
    payload_bytes = canonicalize_json(data)
    payload_hash = sha256_hex(payload_bytes)
    prev = (prev_hash or "").encode("utf-8")
    row_hash = sha256_hex(prev + payload_hash.encode("utf-8"))
    return payload_hash, row_hash


def generate_keypair() -> Tuple[str, str]:
    """Generate an Ed25519 keypair. Returns (public_key_b64, private_key_b64)."""
    sk = signing.SigningKey.generate()
    pk = sk.verify_key
    return (
        base64.b64encode(bytes(pk)).decode("ascii"),
        base64.b64encode(bytes(sk)).decode("ascii"),
    )


def sign_data(data: Any, private_key_b64: str) -> str:
    """Sign canonicalized data with Ed25519 private key (base64). Returns signature base64."""
    sk = signing.SigningKey(base64.b64decode(private_key_b64))
    signed = sk.sign(canonicalize_json(data))
    return base64.b64encode(signed.signature).decode("ascii")


def verify_signature(data: Any, signature_b64: str, public_key_b64: str) -> bool:
    """Verify Ed25519 signature (base64) over canonicalized data using public key (base64)."""
    vk = signing.VerifyKey(base64.b64decode(public_key_b64))
    try:
        vk.verify(canonicalize_json(data), base64.b64decode(signature_b64))
        return True
    except BadSignatureError:
        return False


def merkle_root(leaves: list[str]) -> str:
    """Compute a simple binary Merkle root from hex-encoded leaf hashes.
    If odd number of nodes at a level, promote the last one.
    Returns hex string; empty string for no leaves.
    """
    if not leaves:
        return ""
    level = leaves[:]
    while len(level) > 1:
        next_level: list[str] = []
        for i in range(0, len(level), 2):
            if i + 1 < len(level):
                combined = (level[i] + level[i + 1]).encode("utf-8")
                next_level.append(sha256_hex(combined))
            else:
                next_level.append(level[i])
        level = next_level
    return level[0]



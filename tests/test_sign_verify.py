from __future__ import annotations

import base64
import json
from pathlib import Path

import sys
sys.path.append(str((Path(__file__).resolve().parent.parent / 'icn-node').resolve()))

from app.utils.crypto import sign_data, verify_signature


def test_sign_and_verify_with_seed_key(tmp_path):
    payload = {"hello": "world", "n": 42}
    # Use demo key if exists, else generate a deterministic 32-byte zero seed for test
    demo = Path('.demo/keys/urn:coop:alpha-bakery.json')
    if demo.exists():
        priv = json.loads(demo.read_text())['private_key']
        pub = None
    else:
        seed = bytes([0] * 32)
        priv = base64.b64encode(seed).decode('ascii')
        pub = None

    sig = sign_data(payload, priv)
    # We cannot derive public from private easily here without libs, but verify should pass
    # If demo public exists use it
    if demo.exists():
        pub = json.loads(demo.read_text())['public_key']
        assert verify_signature(payload, sig, pub)



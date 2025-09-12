from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
from typing import Any

from nacl import signing
from nacl.exceptions import BadSignatureError


def canonicalize(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def load_private_key_for_org(org: str) -> bytes:
    key_file = Path(f".demo/keys/{org}.json")
    if not key_file.exists():
        raise SystemExit(f"Missing key file: {key_file}. Run make demo-up to seed.")
    data = json.loads(key_file.read_text())
    pk_b64 = data.get("private_key")
    if not pk_b64:
        raise SystemExit(f"No private_key in {key_file}")
    return base64.b64decode(pk_b64)


def sign_bytes(body: bytes, private_key_raw: bytes) -> str:
    # Accept 32-byte seed or 64-byte secret key
    if len(private_key_raw) == 32:
        sk = signing.SigningKey(private_key_raw)
    elif len(private_key_raw) == 64:
        sk = signing.SigningKey(private_key_raw[:32])
    else:
        raise SystemExit("Private key must be 32-byte seed or 64-byte secret key")
    sig = sk.sign(body).signature
    return base64.b64encode(sig).decode("ascii")


def main() -> None:
    p = argparse.ArgumentParser(description="Canonical JSON signer for ICN demo")
    p.add_argument("--file", "-i", type=str, help="Path to JSON file (or omit to read stdin)")
    p.add_argument("--org", "-o", type=str, required=True, help="Org URN for key lookup, e.g. urn:coop:alpha-bakery")
    p.add_argument("--headers", action="store_true", help="Print copyable headers and canonical body")
    p.add_argument("--verify", action="store_true", help="Verify signature using .demo public key and print OK/FAIL")
    args = p.parse_args()

    if args.file:
        payload = json.loads(Path(args.file).read_text())
    else:
        payload = json.loads(sys.stdin.read())  # type: ignore[name-defined]

    body = canonicalize(payload)
    priv = load_private_key_for_org(args.org)
    signature = sign_bytes(body, priv)
    if args.headers:
        print(f"X-Key-Id: {args.org}")
        print(f"X-Signature: {signature}")
        print()
        print(body.decode("utf-8"))
    else:
        print(signature)

    if args.verify:
        key_file = Path(f".demo/keys/{args.org}.json")
        pub_b64 = json.loads(key_file.read_text()).get("public_key", "")
        if not pub_b64:
            print("VERIFY: SKIPPED (no public_key)")
        else:
            vk = signing.VerifyKey(base64.b64decode(pub_b64))
            try:
                vk.verify(body, base64.b64decode(signature))
                print("VERIFY: OK")
            except BadSignatureError:
                print("VERIFY: FAIL")


if __name__ == "__main__":
    main()



import json
from pathlib import Path
import time

import httpx

from app.utils.crypto import sign_data


BASE = "http://localhost:8000"


def load_keys():
    data = json.loads((Path(__file__).resolve().parents[1] / "icn-node" / "demo_keys.json").read_text())
    return data


def create_invoice(priv_key: str, from_urn: str, to_urn: str, idem: str):
    payload = {
        "from_org": from_urn,
        "to_org": to_urn,
        "lines": [{"sku": "bread", "qty": 250, "unit": "loaf", "unit_price": 3.0}],
        "total": 750.0,
        "terms": {"due_net_days": 30},
        "signatures": [],
    }
    sig = sign_data(payload, priv_key)
    r = httpx.post(
        f"{BASE}/invoices",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-Key-Id": from_urn,
            "X-Signature": sig,
            "Idempotency-Key": idem,
        },
        timeout=10.0,
    )
    print("Invoice:", r.status_code, r.json())
    return r.json().get("id")


def attest_invoice(priv_key: str, attestor_urn: str, invoice_id: int):
    payload = {
        "subject_type": "invoice",
        "subject_id": str(invoice_id),
        "claims": [{"claim": "quantity_verified", "value": {"received": 250, "expected": 250}, "confidence": 1.0}],
        "weight": 1.0,
    }
    sig = sign_data(payload, priv_key)
    r = httpx.post(
        f"{BASE}/attestations",
        json=payload,
        headers={
            "Content-Type": "application/json",
            "X-Key-Id": attestor_urn,
            "X-Signature": sig,
        },
        timeout=10.0,
    )
    print("Attestation:", r.status_code, r.json())


def trust(from_urn: str, to_urn: str):
    r = httpx.get(f"{BASE}/trust/score", params={"from_org": from_urn, "to_org": to_urn, "include_factors": True}, timeout=10.0)
    print("Trust:", r.status_code, r.json())


def checkpoint(today: str):
    r = httpx.post(f"{BASE}/checkpoints/generate", params={"date": today}, json={}, timeout=10.0)
    print("Checkpoint gen:", r.status_code, r.json())
    v = httpx.get(f"{BASE}/checkpoints/{today}/verify", timeout=10.0)
    print("Checkpoint verify:", v.status_code, v.json())


def audit():
    r = httpx.get(f"{BASE}/debug/audit-log", timeout=10.0)
    print("Audit chain:", r.status_code, r.json())


if __name__ == "__main__":
    keys = load_keys()
    sunrise = keys["urn:coop:sunrise-bakery"]["private_key"]
    valley = keys["urn:coop:valley-food"]["private_key"]

    inv1 = create_invoice(sunrise, "urn:coop:sunrise-bakery", "urn:coop:river-housing", "demo-inv-001")
    inv2 = create_invoice(sunrise, "urn:coop:sunrise-bakery", "urn:coop:river-housing", "demo-inv-002")
    attest_invoice(valley, "urn:coop:valley-food", inv1)
    trust("urn:coop:sunrise-bakery", "urn:coop:river-housing")
    today = time.strftime("%Y-%m-%d")
    checkpoint(today)
    audit()



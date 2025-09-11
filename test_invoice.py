import json
from pathlib import Path
import sys

import httpx

# Ensure we can import the app package from icn-node
sys.path.insert(0, str((Path(__file__).parent / "icn-node").resolve()))
from app.utils.crypto import sign_data  # noqa: E402


def load_demo_keys():
    p = Path(__file__).parent / "icn-node" / "demo_keys.json"
    data = json.loads(p.read_text())
    return data["urn:coop:sunrise-bakery"]["private_key"], "urn:coop:sunrise-bakery"


def post_invoice(idempotency_key: str):
    priv, urn = load_demo_keys()
    invoice_data = {
        "from_org": urn,
        "to_org": "urn:coop:river-housing",
        "lines": [{"sku": "bread", "qty": 250, "unit": "loaf", "unit_price": 3.00}],
        "total": 750.00,
        "terms": {"due_net_days": 30},
        "signatures": [],
    }
    signature = sign_data(invoice_data, priv)
    resp = httpx.post(
        "http://localhost:8000/invoices",
        json=invoice_data,
        headers={
            "X-Key-Id": urn,
            "X-Signature": signature,
            "Idempotency-Key": idempotency_key,
            "Content-Type": "application/json",
        },
        timeout=10.0,
    )
    print("Status:", resp.status_code)
    print("Response:", resp.json())


def show_audit():
    r = httpx.get("http://localhost:8000/debug/audit-log", timeout=10.0)
    print("Audit Log:", r.json())


if __name__ == "__main__":
    post_invoice("test-invoice-001")
    post_invoice("test-invoice-002")
    show_audit()



from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.request import urlopen, Request
import ssl


BASE = os.environ.get("DEMO_BASE_URL", "http://localhost:8000")
OUT_DIR = Path(".demo/exports/quickbooks")


def fetch_invoices() -> list[dict[str, Any]]:
    ctx = ssl.create_default_context()
    req = Request(f"{BASE}/invoices")
    with urlopen(req, context=ctx) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("items", [])


def map_to_qb(invoices: list[dict[str, Any]]) -> dict[str, Any]:
    entries = []
    for i in invoices:
        total = float(i.get("total", 0))
        if total <= 0:
            continue
        doc_no = f"inv-{str(i['id']).zfill(6)}"
        entry = {
            "doc_no": doc_no,
            "date": "2025-01-01",  # deterministic for demo
            "lines": [
                {"account": "Accounts Receivable", "entity": str(i.get("to_org_id")), "debit": round(total, 2), "currency": "USD"},
                {"account": "Sales", "entity": str(i.get("from_org_id")), "credit": round(total, 2), "currency": "USD"},
            ],
            "memo": "ICN export demo",
        }
        entries.append(entry)
    return {"journal_entries": entries}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    invoices = fetch_invoices()
    qb = map_to_qb(invoices)
    out_path = OUT_DIR / "journal.json"
    out_path.write_text(json.dumps(qb, indent=2))
    print(str(out_path))


if __name__ == "__main__":
    main()



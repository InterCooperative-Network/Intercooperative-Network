from __future__ import annotations

import csv
import json
import os
import subprocess
from pathlib import Path


BASE = os.environ.get("DEMO_BASE_URL", "http://localhost:8000")


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def run_httpie(url: str, org: str, body: dict, idem: str) -> None:
    payload_path = Path(".demo/tmp_payload.json")
    payload_path.parent.mkdir(parents=True, exist_ok=True)
    payload_path.write_text(json.dumps(body))
    sig = subprocess.check_output(["python3", "tools/sign.py", "-i", str(payload_path), "-o", org], text=True).strip()
    cmd = [
        "http",
        "POST",
        url,
        "Content-Type:application/json",
        f"Idempotency-Key:{idem}",
        f"X-Key-Id:{org}",
        f"X-Signature:{sig}",
    ]
    print("$", " ".join(cmd), "<", str(payload_path))
    subprocess.run(cmd + ["<", str(payload_path)], check=True)


def main() -> None:
    csv_path = Path("examples/interops/invoices.csv")
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            body = {
                "from_org": row["from_org"],
                "to_org": row["to_org"],
                "lines": [
                    {
                        "sku": row["sku"],
                        "qty": float(row["qty"]),
                        "unit": row["unit"],
                        "unit_price": float(row["unit_price"]),
                    }
                ],
                "total": float(row["total"]),
                "terms": {"due_net_days": int(row["due_net_days"])},
                "signatures": [],
            }
            org = row["from_org"]
            run_httpie(f"{BASE}/invoices", org, body, f"csv-{idx}")


if __name__ == "__main__":
    main()



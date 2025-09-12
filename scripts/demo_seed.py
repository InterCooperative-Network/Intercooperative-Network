from __future__ import annotations

import asyncio
import base64
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import os

import sqlalchemy
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import sys
sys.path.append(str((Path(__file__).resolve().parent.parent / 'icn-node').resolve()))

from app.db import AsyncSessionFactory
from app.models import AuditLog, Invoice, Org
from app.utils.crypto import generate_keypair, compute_hash


DEMO_DIR = Path('.demo')
KEYS_DIR = DEMO_DIR / 'keys'
ENV_FILE = Path('.env.demo')


ORG_URNS = [
    'urn:coop:alpha-bakery',
    'urn:coop:beta-housing',
    'urn:coop:gamma-audit',
]


def ensure_dirs() -> None:
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
    DEMO_DIR.mkdir(parents=True, exist_ok=True)


async def upsert_orgs(session: AsyncSession) -> None:
    for urn in ORG_URNS:
        existing = (await session.execute(select(Org).where(Org.urn == urn))).scalar_one_or_none()
        if existing:
            # Ensure key file exists for convenience
            kf = KEYS_DIR / f"{urn}.json"
            if not kf.exists():
                with open(kf, 'w') as f:
                    json.dump({"public_key": existing.public_key, "private_key": ""}, f, indent=2)
            continue
        pub, priv = generate_keypair()
        session.add(Org(urn=urn, name=urn.split(':')[-1].replace('-', ' ').title(), public_key=pub, org_metadata={"demo": True}))
        await session.flush()
        with open(KEYS_DIR / f"{urn}.json", 'w') as f:
            json.dump({"public_key": pub, "private_key": priv}, f, indent=2)
    await session.commit()


async def current_prev_hash(session: AsyncSession) -> str | None:
    last = (await session.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(1))).scalar_one_or_none()
    return last.row_hash if last else None


async def seed_invoices_attestations(session: AsyncSession) -> dict[str, Any]:
    # Org IDs
    orgs = {o.urn: o for o in (await session.execute(select(Org))).scalars().all()}
    alpha = orgs[ORG_URNS[0]]
    beta = orgs[ORG_URNS[1]]
    gamma = orgs[ORG_URNS[2]]

    # Invoice A: alpha -> beta
    prev_hash = await current_prev_hash(session)
    invoice_a_payload = {
        "from_org": alpha.urn,
        "to_org": beta.urn,
        "lines": [{"sku": "bread", "qty": 200, "unit": "loaf", "unit_price": 3.0}],
        "total": 600.0,
        "terms": {"due_net_days": 30},
        "status": "proposed",
        "status_history": [{"status": "proposed", "by": alpha.urn}],
        "signatures": [],
    }
    payload_hash, row_hash = compute_hash(invoice_a_payload, prev_hash)
    inv_a = Invoice(
        idempotency_key="demo-inv-a",
        from_org_id=alpha.id,
        to_org_id=beta.id,
        lines=invoice_a_payload["lines"],
        total=invoice_a_payload["total"],
        terms=invoice_a_payload["terms"],
        status="proposed",
        status_history=invoice_a_payload["status_history"],
        signatures=[],
        prev_hash=prev_hash,
        row_hash=row_hash,
    )
    session.add(inv_a)
    await session.flush()
    session.add(AuditLog(prev_hash=prev_hash, row_hash=row_hash, op_type="create", entity_type="invoice", entity_id=str(inv_a.id), payload_hash=payload_hash, signature=None))

    # Invoice B: beta -> alpha (to later dispute)
    prev_hash = await current_prev_hash(session)
    invoice_b_payload = {
        "from_org": beta.urn,
        "to_org": alpha.urn,
        "lines": [{"sku": "repair", "qty": 1, "unit": "job", "unit_price": 400.0}],
        "total": 400.0,
        "terms": {"due_net_days": 15},
        "status": "proposed",
        "status_history": [{"status": "proposed", "by": beta.urn}],
        "signatures": [],
    }
    payload_hash_b, row_hash_b = compute_hash(invoice_b_payload, prev_hash)
    inv_b = Invoice(
        idempotency_key="demo-inv-b",
        from_org_id=beta.id,
        to_org_id=alpha.id,
        lines=invoice_b_payload["lines"],
        total=invoice_b_payload["total"],
        terms=invoice_b_payload["terms"],
        status="proposed",
        status_history=invoice_b_payload["status_history"],
        signatures=[],
        prev_hash=prev_hash,
        row_hash=row_hash_b,
    )
    session.add(inv_b)
    await session.flush()
    session.add(AuditLog(prev_hash=prev_hash, row_hash=row_hash_b, op_type="create", entity_type="invoice", entity_id=str(inv_b.id), payload_hash=payload_hash_b, signature=None))

    await session.commit()
    return {"invoice_a_id": inv_a.id, "invoice_b_id": inv_b.id}


def write_env_and_headers(base_url: str = "http://localhost:8000") -> None:
    lines = [f"DEMO_BASE_URL={base_url}"]
    for urn in ORG_URNS:
        key_path = KEYS_DIR / f"{urn}.json"
        if not key_path.exists():
            continue
        obj = json.loads(key_path.read_text())
        lines.append(f"{urn.replace(':','_').upper()}_PRIVATE_KEY={obj.get('private_key','')}")
        lines.append(f"{urn.replace(':','_').upper()}_PUBLIC_KEY={obj.get('public_key','')}")
    ENV_FILE.write_text("\n".join(lines) + "\n")


def print_httpie_commands(ids: dict[str, Any]) -> None:
    base = "http://localhost:8000"
    alpha, beta, gamma = ORG_URNS
    print("\n# Ready-to-run HTTPie commands (copy/paste):\n")
    print(f"http {base}/health\n")
    print("# 1) Create invoice alpha -> beta")
    print(f"http POST {base}/invoices X-Key-Id:{alpha} X-Signature:$(python3 tools/sign.py -i examples/httpie/payloads/invoice_alpha_to_beta.json -o {alpha}) Idempotency-Key:inv-a < examples/httpie/payloads/invoice_alpha_to_beta.json\n")
    print("# 2) Accept invoice as beta")
    print(f"http POST {base}/invoices/{ids['invoice_a_id']}/accept X-Key-Id:{beta} X-Signature:$(python3 tools/sign.py -i examples/httpie/payloads/empty.json -o {beta}) < examples/httpie/payloads/empty.json\n")
    print("# 3) Dispute invoice B as alpha")
    print(f"http POST {base}/invoices/{ids['invoice_b_id']}/dispute X-Key-Id:{alpha} X-Signature:$(python3 tools/sign.py -i examples/httpie/payloads/dispute.json -o {alpha}) < examples/httpie/payloads/dispute.json\n")
    print("# 4) Third-party attestation by gamma on invoice A")
    print(f"http POST {base}/attestations X-Key-Id:{gamma} X-Signature:$(python3 tools/sign.py -i examples/httpie/payloads/attestation_on_a.json -o {gamma}) < examples/httpie/payloads/attestation_on_a.json\n")
    print("# 5) Trust score with factors")
    print(f"http {base}/trust/score from_org=={alpha} to_org=={beta} include_factors==true\n")
    print("# 6) Generate and verify checkpoint")
    print("DATE=$(date -u +%F); http POST " + base + "/checkpoints/generate date==$DATE; http " + base + "/checkpoints/$DATE/verify\n")


async def main() -> None:
    ensure_dirs()
    async with AsyncSessionFactory() as session:
        await upsert_orgs(session)
        ids = await seed_invoices_attestations(session)
    write_env_and_headers()
    print_httpie_commands(ids)


if __name__ == "__main__":
    asyncio.run(main())



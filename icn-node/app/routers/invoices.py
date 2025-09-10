from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import AuditLog, Invoice, Org
from ..utils.crypto import compute_hash, canonicalize_json


router = APIRouter(prefix="/invoices", tags=["invoices"])


class InvoiceCreate(BaseModel):
    from_org: str
    to_org: str
    lines: list[dict]
    total: float
    terms: dict = Field(default_factory=dict)
    story: Optional[str] = None
    signatures: list[dict] = Field(default_factory=list)


@router.post("")
async def create_invoice(
    request: Request,
    payload: InvoiceCreate,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    session: AsyncSession = Depends(get_session),
):
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header required")

    # Verify signature against request.state.canonical_body using org public key
    org: Org = getattr(request.state, "org", None)
    if not org:
        raise HTTPException(status_code=401, detail="Signature verification required")

    # Idempotency check
    existing = (
        await session.execute(select(Invoice).where(Invoice.idempotency_key == idempotency_key))
    ).scalar_one_or_none()
    if existing:
        return {"id": existing.id, "idempotent": True}

    # Resolve orgs by urn
    from_org = (
        await session.execute(select(Org).where(Org.urn == payload.from_org))
    ).scalar_one_or_none()
    to_org = (
        await session.execute(select(Org).where(Org.urn == payload.to_org))
    ).scalar_one_or_none()
    if not from_org or not to_org:
        raise HTTPException(status_code=400, detail="Unknown from_org or to_org")

    # Compute prev_hash from last AuditLog
    last = (await session.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(1))).scalar_one_or_none()
    prev_hash = last.row_hash if last else None

    invoice_dict: dict[str, Any] = {
        "from_org": payload.from_org,
        "to_org": payload.to_org,
        "lines": payload.lines,
        "total": payload.total,
        "terms": payload.terms,
        "status": "proposed",
        "status_history": [
            {"status": "proposed", "by": org.urn}
        ],
        "signatures": payload.signatures,
    }

    payload_hash, row_hash = compute_hash(invoice_dict, prev_hash)

    inv = Invoice(
        idempotency_key=idempotency_key,
        from_org_id=from_org.id,
        to_org_id=to_org.id,
        lines=payload.lines,
        total=payload.total,
        terms=payload.terms,
        status="proposed",
        status_history=invoice_dict["status_history"],
        signatures=payload.signatures,
        prev_hash=prev_hash,
        row_hash=row_hash,
    )

    session.add(inv)
    await session.flush()

    audit = AuditLog(
        prev_hash=prev_hash,
        row_hash=row_hash,
        op_type="create",
        entity_type="invoice",
        entity_id=str(inv.id),
        payload_hash=payload_hash,
        signature=getattr(request.state, "signature_b64", None),
    )
    session.add(audit)
    await session.commit()

    return {"id": inv.id, "row_hash": row_hash}


@router.get("")
async def list_invoices(
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    res = await session.execute(select(Invoice).order_by(Invoice.id.desc()).limit(limit).offset(offset))
    items = [
        {
            "id": i.id,
            "from_org_id": i.from_org_id,
            "to_org_id": i.to_org_id,
            "total": i.total,
            "status": i.status,
            "row_hash": i.row_hash,
        }
        for i in res.scalars().all()
    ]
    return {"items": items, "limit": limit, "offset": offset}


@router.get("/{invoice_id}")
async def get_invoice(invoice_id: int, session: AsyncSession = Depends(get_session)):
    inv = (await session.execute(select(Invoice).where(Invoice.id == invoice_id))).scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return {
        "id": inv.id,
        "from_org_id": inv.from_org_id,
        "to_org_id": inv.to_org_id,
        "lines": inv.lines,
        "total": inv.total,
        "terms": inv.terms,
        "status": inv.status,
        "status_history": inv.status_history,
        "signatures": inv.signatures,
        "prev_hash": inv.prev_hash,
        "row_hash": inv.row_hash,
        "created_at": inv.created_at,
    }



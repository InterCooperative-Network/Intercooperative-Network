from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import AuditLog, Attestation, Org
from ..utils.crypto import compute_hash


router = APIRouter(prefix="/attestations", tags=["attestations"])


class Claim(BaseModel):
    claim: str
    value: Any
    confidence: float = 1.0


class AttestationCreate(BaseModel):
    subject_type: str = Field(pattern=r"^(invoice)$")
    subject_id: str
    claims: list[Claim] = Field(default_factory=list)
    weight: float = 1.0


@router.post("")
async def create_attestation(
    request: Request,
    payload: AttestationCreate,
    session: AsyncSession = Depends(get_session),
):
    org: Org = getattr(request.state, "org", None)
    if not org:
        raise HTTPException(status_code=401, detail="Signature verification required")

    # Compute prev hash from audit log
    last = (await session.execute(select(AuditLog).order_by(AuditLog.id.desc()).limit(1))).scalar_one_or_none()
    prev_hash = last.row_hash if last else None

    attestation_payload = {
        "subject_type": payload.subject_type,
        "subject_id": payload.subject_id,
        "attestor_org": org.urn,
        "claims": [c.model_dump() for c in payload.claims],
        "weight": payload.weight,
    }
    payload_hash, row_hash = compute_hash(attestation_payload, prev_hash)

    att = Attestation(
        subject_type=payload.subject_type,
        subject_id=payload.subject_id,
        attestor_org_id=org.id,
        claims=[c.model_dump() for c in payload.claims],
        weight=payload.weight,
        signature=getattr(request.state, "signature_b64", None) or "",
    )
    session.add(att)
    await session.flush()

    audit = AuditLog(
        prev_hash=prev_hash,
        row_hash=row_hash,
        op_type="create",
        entity_type="attestation",
        entity_id=str(att.id),
        payload_hash=payload_hash,
        signature=getattr(request.state, "signature_b64", None),
    )
    session.add(audit)
    await session.commit()

    return {"id": att.id, "row_hash": row_hash}


@router.get("")
async def list_attestations(
    subject_id: Optional[str] = Query(default=None),
    limit: int = 50,
    offset: int = 0,
    session: AsyncSession = Depends(get_session),
):
    stmt = select(Attestation).order_by(Attestation.id.desc()).limit(limit).offset(offset)
    if subject_id:
        stmt = select(Attestation).where(Attestation.subject_id == subject_id).order_by(Attestation.id.desc()).limit(limit).offset(offset)
    res = await session.execute(stmt)
    items = [
        {
            "id": a.id,
            "subject_type": a.subject_type,
            "subject_id": a.subject_id,
            "attestor_org_id": a.attestor_org_id,
            "claims": a.claims,
            "weight": a.weight,
            "created_at": a.created_at,
        }
        for a in res.scalars().all()
    ]
    return {"items": items, "limit": limit, "offset": offset}



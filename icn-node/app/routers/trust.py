from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Attestation, Invoice, Org


router = APIRouter(prefix="/trust", tags=["trust"])


def time_decay(ts: datetime, half_life_days: int = 180) -> float:
    """Half-life decay so recent interactions count more.

    Using an exponential decay: w = 0.5 ** (days / half_life)
    """
    now = datetime.now(timezone.utc)
    days = (now - (ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc))).days
    return 0.5 ** (days / half_life_days)


@router.get("/score")
async def trust_score(
    from_org: str = Query(...),
    to_org: str = Query(...),
    include_factors: bool = Query(False),
    session: AsyncSession = Depends(get_session),
):
    a = (await session.execute(select(Org).where(Org.urn == from_org))).scalar_one_or_none()
    b = (await session.execute(select(Org).where(Org.urn == to_org))).scalar_one_or_none()
    if not a or not b:
        raise HTTPException(status_code=400, detail="Unknown org(s)")

    # Direct factor: sum of totals, weighted by time decay and simple status weight
    invs = (
        await session.execute(
            select(Invoice).where(and_(Invoice.from_org_id == a.id, Invoice.to_org_id == b.id))
        )
    ).scalars().all()
    if not invs:
        direct = 0.0
    else:
        weight_for_status = {"settled": 1.0, "accepted": 0.7, "proposed": 0.4, "disputed": 0.1}
        direct_numer = sum(i.total * time_decay(i.created_at) * weight_for_status.get(i.status, 0.3) for i in invs)
        direct_denom = sum(i.total for i in invs) or 1.0
        direct = min(1.0, max(0.0, direct_numer / direct_denom))

    # Attestation factor: average confidence across attestations on those invoices
    att = (
        await session.execute(
            select(Attestation).where(
                and_(Attestation.subject_type == "invoice", Attestation.subject_id.in_([str(i.id) for i in invs]))
            )
        )
    ).scalars().all()
    if not att:
        attest = 0.0
    else:
        vals = []
        for arow in att:
            confidences = [float(c.get("confidence", 1.0)) for c in arow.claims if isinstance(c, dict)]
            vals.append((sum(confidences) / max(1, len(confidences))) * time_decay(arow.created_at) * arow.weight)
        attest = min(1.0, sum(vals) / max(1, len(vals)))

    disputes = 0.0
    network = 0.0

    score = 0.4 * direct + 0.2 * attest + 0.2 * (1 - disputes) + 0.2 * network
    confidence = "low" if len(invs) + len(att) < 2 else ("medium" if len(invs) + len(att) < 5 else "high")
    result = {"score": round(score, 4), "confidence": confidence}
    if include_factors:
        result["factors"] = {"direct": round(direct, 4), "attestations": round(attest, 4), "disputes": disputes, "network": network}
    return result



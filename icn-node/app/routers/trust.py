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

    # Disputes factor: recent disputes lower trust. Treat any invoice with status disputed as 0.3 value
    disputed_count = sum(1 for i in invs if i.status == "disputed")
    disputes_value = 0.3 if disputed_count > 0 else 1.0

    # Compose weighted score with explainability
    weights = {
        "payment_history_decay": 0.4,
        "third_party_attestations": 0.3,
        "disputes_recent": 0.3,
    }
    factors = {
        "payment_history_decay": max(0.0, min(1.0, direct)),
        "third_party_attestations": max(0.0, min(1.0, attest)),
        "disputes_recent": max(0.0, min(1.0, disputes_value if disputed_count == 0 else 0.3)),
    }
    score = (
        weights["payment_history_decay"] * factors["payment_history_decay"]
        + weights["third_party_attestations"] * factors["third_party_attestations"]
        + weights["disputes_recent"] * factors["disputes_recent"]
    )

    # Confidence as a 0..1 in addition to string for backward compat
    samples = len(invs) + len(att)
    confidence_f = 0.25 if samples < 2 else (0.6 if samples < 5 else 0.85)
    confidence_label = "low" if confidence_f < 0.4 else ("medium" if confidence_f < 0.8 else "high")

    result = {"score": round(score * 100), "confidence": round(confidence_f, 2)}
    if include_factors:
        result["factors"] = [
            {"factor": k, "value": round(factors[k], 2), "weight": weights[k]} for k in [
                "payment_history_decay", "third_party_attestations", "disputes_recent"
            ]
        ]
        result["explanation"] = "Time-weighted history plus attestations, minus recent disputes"
    return result



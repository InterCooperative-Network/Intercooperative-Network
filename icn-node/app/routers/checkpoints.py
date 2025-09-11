from __future__ import annotations

from datetime import date as Date, datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import AuditLog, Checkpoint
from ..utils.crypto import merkle_root, sha256_hex


router = APIRouter(prefix="/checkpoints", tags=["checkpoints"])


def _leaf_from_audit(a: AuditLog) -> str:
    """Deterministic leaf (PRD §11):
    sha256(prev_hash || row_hash || op_type || entity_type || entity_id || payload_hash || timestamp)
    """
    prev = (a.prev_hash or "")
    row = a.row_hash or ""
    ts = a.timestamp.isoformat()
    s = f"{prev}|{row}|{a.op_type}|{a.entity_type}|{a.entity_id}|{a.payload_hash}|{ts}"
    return sha256_hex(s.encode("utf-8"))


@router.post("/generate")
async def generate_checkpoint(
    date: str = Query(..., description="YYYY-MM-DD"),
    session: AsyncSession = Depends(get_session),
):
    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    # Fetch day's audit entries in order
    start = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    end = datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)
    rows = (
        await session.execute(
            select(AuditLog).where(and_(AuditLog.timestamp >= start, AuditLog.timestamp <= end)).order_by(AuditLog.id.asc())
        )
    ).scalars().all()
    leaves = [_leaf_from_audit(a) for a in rows]
    root = merkle_root(leaves)

    # Link to previous checkpoint
    last_cp = (
        await session.execute(select(Checkpoint).order_by(Checkpoint.id.desc()).limit(1))
    ).scalar_one_or_none()
    prev_cp_hash = last_cp.merkle_root if last_cp else None

    cp = Checkpoint(
        date=d,
        node_id="local-node",  # TODO: configurable node identifier
        operations_count=len(rows),
        merkle_root=root or "",
        prev_checkpoint_hash=prev_cp_hash,
        signature="",  # TODO: sign with node operational key when available
    )
    session.add(cp)
    await session.commit()
    return {"date": date, "operations_count": len(rows), "merkle_root": root}


@router.get("/{date}/verify")
async def verify_checkpoint(
    date: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        d = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    cp = (
        await session.execute(select(Checkpoint).where(Checkpoint.date == d).limit(1))
    ).scalar_one_or_none()
    if not cp:
        raise HTTPException(status_code=404, detail="Checkpoint not found")

    start = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
    end = datetime(d.year, d.month, d.day, 23, 59, 59, tzinfo=timezone.utc)
    rows = (
        await session.execute(
            select(AuditLog).where(and_(AuditLog.timestamp >= start, AuditLog.timestamp <= end)).order_by(AuditLog.id.asc())
        )
    ).scalars().all()
    leaves = [_leaf_from_audit(a) for a in rows]
    root = merkle_root(leaves)
    ok = (root or "") == (cp.merkle_root or "")
    return {"ok": ok, "merkle_root": cp.merkle_root, "count": len(rows)}



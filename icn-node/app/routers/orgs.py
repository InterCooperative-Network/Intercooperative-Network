from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_session
from ..models import Org


router = APIRouter(prefix="/orgs", tags=["orgs"])


def to_public_org_dict(org: Org) -> dict:
    return {
        "org_id": org.urn,
        "display_name": org.name,
        "pubkey": org.public_key,
    }


@router.get("")
async def list_orgs(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(Org).order_by(Org.id.asc()))
    items = [to_public_org_dict(o) for o in res.scalars().all()]
    return {"items": items}


@router.get("/{org_id}")
async def get_org(org_id: str, session: AsyncSession = Depends(get_session)):
    org = (await session.execute(select(Org).where(Org.urn == org_id))).scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Org not found")
    return {
        "org_id": org.urn,
        "display_name": org.name,
        "pubkey": org.public_key,
        "metadata": org.org_metadata,
        "created_at": org.created_at,
    }



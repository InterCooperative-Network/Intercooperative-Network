
"""
FastAPI application entry point for the ICN Node (Weekend MVP).

Responsibilities
- Registers the signature verification middleware for POST/PATCH writes
- Wires core routers: invoices, attestations, trust, checkpoints
- Exposes a debug endpoint for verifying audit-chain continuity

Notes
- Signature middleware enforces `X-Key-Id` (org URN) and `X-Signature` (Ed25519)
- `POST /checkpoints/generate` is exempted for local demo convenience
"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="ICN Node", version="0.1.0")

# CORS for local demo UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "ok", "node": "icn-mvp"}

# Wiring
from .middleware.signatures import SignatureVerificationMiddleware
from .routers.invoices import router as invoices_router
from .routers.attestations import router as attestations_router
from .routers.trust import router as trust_router
from .routers.checkpoints import router as checkpoints_router
from .db import get_session
from .models import AuditLog, Invoice, Attestation
from .utils.crypto import canonicalize_json

app.add_middleware(SignatureVerificationMiddleware)
app.include_router(invoices_router)
app.include_router(attestations_router)
app.include_router(trust_router)
app.include_router(checkpoints_router)

@app.get("/env/demo")
async def env_demo():
    """Expose base URL hint for the web viewer and scripts."""
    return {"base_url": "http://localhost:8000"}


@app.get("/debug/audit-log")
async def debug_audit_log(session: AsyncSession = Depends(get_session)):
    res = await session.execute(select(AuditLog).order_by(AuditLog.id.asc()))
    items = res.scalars().all()
    chain_ok = True
    prev = None
    for a in items:
        if a.prev_hash != (prev.row_hash if prev else None):
            chain_ok = False
            break
        prev = a
    last_rows = []
    # Build last 5 entries with small payload preview when possible
    tail = items[-5:]
    for a in tail:
        preview = None
        if a.entity_type == "invoice":
            inv = (
                await session.execute(select(Invoice).where(Invoice.id == int(a.entity_id)))
            ).scalar_one_or_none()
            if inv:
                payload = {
                    "from_org_id": inv.from_org_id,
                    "to_org_id": inv.to_org_id,
                    "total": inv.total,
                    "status": inv.status,
                }
                preview = canonicalize_json(payload).decode("utf-8")[:100]
        elif a.entity_type == "attestation":
            att = (
                await session.execute(select(Attestation).where(Attestation.id == int(a.entity_id)))
            ).scalar_one_or_none()
            if att:
                payload = {
                    "subject_type": att.subject_type,
                    "subject_id": att.subject_id,
                    "weight": att.weight,
                }
                preview = canonicalize_json(payload).decode("utf-8")[:100]
        last_rows.append({
            "ts": a.timestamp.isoformat(),
            "row_hash": a.row_hash,
            "op": a.op_type,
            "entity": f"{a.entity_type}:{a.entity_id}",
            "payload_preview": preview,
        })
    continuity = None
    if items:
        continuity = f"{items[0].prev_hash or ''} -> ... -> {items[-1].row_hash}"
    return {
        "count": len(items),
        "chain_ok": chain_ok,
        "head": items[-1].row_hash if items else None,
        "last_rows": last_rows,
        "continuity": continuity,
    }

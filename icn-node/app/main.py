
from fastapi import FastAPI, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI(title="ICN Node", version="0.1.0")

@app.get("/health")
async def health():
    return {"status": "ok", "node": "icn-mvp"}

# Wiring
from .middleware.signatures import SignatureVerificationMiddleware
from .routers.invoices import router as invoices_router
from .db import get_session
from .models import AuditLog

app.add_middleware(SignatureVerificationMiddleware)
app.include_router(invoices_router)


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
    return {
        "count": len(items),
        "chain_ok": chain_ok,
        "head": items[-1].row_hash if items else None,
    }

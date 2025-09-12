from __future__ import annotations

import json
from typing import Callable

from fastapi import HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware

from ..utils.crypto import canonicalize_json, verify_signature
from ..models import Org
from ..db import AsyncSessionFactory
from sqlalchemy import select


class SignatureVerificationMiddleware(BaseHTTPMiddleware):
    """
    Verify Ed25519 signatures on JSON write requests.

    Security model
    - Each org has a public key (seeded for the demo) stored in the DB
    - Writers sign the canonicalized JSON body; the server verifies before processing
    - Valid requests get `request.state.org` (the signer org) attached for handlers

    Headers
    - `X-Key-Id`: org URN (e.g., `urn:coop:sunrise-bakery`)
    - `X-Signature`: base64-encoded Ed25519 signature over the JSON body

    Exemptions
    - Some dev endpoints (health, docs, debug, checkpoint generation) are exempt to
      simplify local demos while keeping the default secure-by-default posture.
    """

    def __init__(self, app, exempt_paths: set[str] | None = None):
        super().__init__(app)
        self.exempt_paths = exempt_paths or {"/health", "/docs", "/openapi.json", "/debug/audit-log", "/checkpoints/generate"}

    async def dispatch(self, request: Request, call_next: Callable):
        if request.method in {"POST", "PATCH"} and request.url.path not in self.exempt_paths:
            content_type = request.headers.get("content-type", "").lower()
            if "application/json" not in content_type:
                raise HTTPException(status_code=415, detail="Content-Type must be application/json")

            key_id = request.headers.get("X-Key-Id")
            signature_b64 = request.headers.get("X-Signature")
            if not key_id or not signature_b64:
                raise HTTPException(status_code=401, detail="Missing signature headers")

            body_bytes = await request.body()
            # Re-inject body for downstream handlers
            request._body = body_bytes  # type: ignore[attr-defined]
            try:
                body_obj = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON body")

            # Lookup org by urn
            async with AsyncSessionFactory() as session:
                org = (
                    await session.execute(select(Org).where(Org.urn == key_id))
                ).scalar_one_or_none()
            if not org:
                raise HTTPException(status_code=401, detail="Unknown X-Key-Id")

            # Verify signature over canonicalized JSON using org's public key
            if not verify_signature(body_obj, signature_b64, org.public_key):
                raise HTTPException(status_code=401, detail="Invalid signature")

            # Attach state and canonical bytes for reuse.
            request.state.org = org
            request.state.canonical_body = canonicalize_json(body_obj)
            request.state.signature_b64 = signature_b64

        response = await call_next(request)
        return response



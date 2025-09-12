# ICN Node (Service README)

This package hosts the FastAPI service for the ICN Node.

## Architecture (Weekend MVP)

- `app/main.py`: FastAPI app wiring and debug endpoints
- `app/middleware/signatures.py`: Ed25519 signature verification for JSON writes
- `app/routers/`: HTTP APIs (invoices, attestations, trust, checkpoints)
- `app/models.py`: SQLAlchemy ORM models
- `app/db.py`: Async SQLAlchemy engine/session
- `app/utils/crypto.py`: Canonical JSON, signing/verify, hashing, Merkle
- `app/seed.py`: Demo orgs with Ed25519 keypairs (writes `demo_keys.json`)

## Local run

```bash
docker-compose up -d
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

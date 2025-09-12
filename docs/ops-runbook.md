# Operations Runbook (Local/Dev)

## Bring up services
- docker-compose up -d (Postgres on 5433)
- python -m venv venv && source venv/bin/activate
- pip install -r icn-node/requirements.txt
- alembic upgrade head
- python -m app.seed
- uvicorn app.main:app --reload

## Common checks
- GET /health
- GET /debug/audit-log (chain_ok should be true)
- POST /checkpoints/generate?date=YYYY-MM-DD and then verify

## Logs
- uvicorn.log (top-level)

## Troubleshooting
- Port conflicts: update docker-compose.yml port or stop local Postgres
- Alembic errors: ensure alembic.ini has sqlalchemy.url pointing to 5433
- Signature errors: print canonical JSON on client and server for diff

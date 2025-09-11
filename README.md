# ICN Node - Weekend MVP

Minimal implementation of the Intercooperative Network per PRD v0.3.

## Quick Start

```bash
# 1. Start PostgreSQL
cd icn-node && docker-compose up -d

# 2. Create/upgrade schema
source venv/bin/activate || python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head

# 3. Seed demo organizations (saves keys to icn-node/demo_keys.json)
python -m app.seed

# 4. Start the API
uvicorn app.main:app --reload

# 5. Test with demo script (new terminal)
cd .. && python test_invoice.py
```

## Core Capabilities (PRD → Implementation)

| PRD Section | Feature | Status | Endpoint |
|------------|---------|--------|----------|
| 6. System Architecture | Signed writes | ✅ | All POST/PATCH |
| 6. Data Schemas | Invoices | ✅ | `POST /invoices` |
| 6. Data Schemas | Attestations | ✅ | `POST /attestations` |
| 6. Trust Graph | Trust scoring | ✅ | `GET /trust/score` |
| 11. Reliability | Checkpoints | ✅ | `POST /checkpoints/generate` |
| 5. Domain Model | Audit chain | ✅ | `GET /debug/audit-log` |

## API Examples

### 1) Create Invoice (Signed)

```bash
# Prepare a signature using icn-node/demo_keys.json (example shown via Python) and export to $SIG
SIG=$(python3 - <<'PY'
import json
from pathlib import Path
from app.utils.crypto import sign_data
priv=json.loads(Path('icn-node/demo_keys.json').read_text())['urn:coop:sunrise-bakery']['private_key']
payload={
  "from_org":"urn:coop:sunrise-bakery",
  "to_org":"urn:coop:river-housing",
  "lines":[{"sku":"bread","qty":250,"unit":"loaf","unit_price":3.00}],
  "total":750.00,
  "terms":{"due_net_days":30},
  "signatures":[]
}
print(sign_data(payload, priv))
PY
)

curl -X POST http://localhost:8000/invoices \
  -H "Content-Type: application/json" \
  -H "X-Key-Id: urn:coop:sunrise-bakery" \
  -H "X-Signature: $SIG" \
  -H "Idempotency-Key: inv-001" \
  -d '{
    "from_org": "urn:coop:sunrise-bakery",
    "to_org": "urn:coop:river-housing",
    "lines": [{"sku": "bread", "qty": 250, "unit": "loaf", "unit_price": 3.00}],
    "total": 750.00,
    "terms": {"due_net_days": 30},
    "signatures": []
  }'
```

### 2) Attest to Invoice

```bash
SIG=$(python3 - <<'PY'
import json
from pathlib import Path
from app.utils.crypto import sign_data
priv=json.loads(Path('icn-node/demo_keys.json').read_text())['urn:coop:valley-food']['private_key']
payload={
  "subject_type":"invoice",
  "subject_id":"1",
  "claims":[{"claim":"quantity_verified","value":{"received":250,"expected":250},"confidence":1.0}],
  "weight":1.0
}
print(sign_data(payload, priv))
PY
)

curl -X POST http://localhost:8000/attestations \
  -H "Content-Type: application/json" \
  -H "X-Key-Id: urn:coop:valley-food" \
  -H "X-Signature: $SIG" \
  -d '{
    "subject_type": "invoice",
    "subject_id": "1",
    "claims": [{
      "claim": "quantity_verified",
      "value": {"received": 250, "expected": 250},
      "confidence": 1.0
    }],
    "weight": 1.0
  }'
```

### 3) Query Trust Score

```bash
curl "http://localhost:8000/trust/score?from_org=urn:coop:sunrise-bakery&to_org=urn:coop:river-housing&include_factors=true"
```

### 4) Generate Daily Checkpoint

```bash
DATE=$(date -u +%F)
curl -X POST "http://localhost:8000/checkpoints/generate?date=${DATE}" -H 'Content-Type: application/json' -d '{}'
curl "http://localhost:8000/checkpoints/${DATE}/verify"
```

### 5) Verify Audit Chain

```bash
curl http://localhost:8000/debug/audit-log
```

## What's Implemented

- ✅ Ed25519 signed operations
- ✅ Hash-chained audit log
- ✅ Idempotent invoice creation
- ✅ Attestations with weighted claims
- ✅ Time-decayed trust scoring
- ✅ Daily Merkle checkpoints
- ✅ Signature verification middleware

## What's Next (Post-MVP)

- [ ] CSV import/export
- [ ] Disputes and resolution
- [ ] Settlement suggestions
- [ ] Web UI
- [ ] Relay federation
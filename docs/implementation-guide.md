# ICN Implementation Guide (Weekend MVP)

This guide explains how the MVP maps the PRD to concrete code, with rationale and extension points.

## 1. Integrity Model

- All write operations are signed (Ed25519) over canonical JSON (`app/utils/crypto.py`).
- The database stores an append-only chain via `prev_hash` → `row_hash` (payload hash chained).
- A daily checkpoint computes a Merkle root over the day’s audit entries and stores it (`checkpoints`).

Why this design?
- Boring, verifiable primitives that are easy to reason about and validate offline (PRD §6/§11).

## 2. Canonical JSON & Signatures

- Canonicalization sorts keys and removes whitespace to ensure deterministic bytes before signing.
- Clients include `X-Key-Id` (org URN) and `X-Signature` (base64) on writes; middleware verifies before handlers.

Extension: support delegated keys and scoped capabilities (PRD v0.3 Key Hierarchy).

## 3. Data Model (ORM)

- `Org`: URN + public key, minimal metadata.
- `Invoice`: denormalized JSON fields for speed; status history captured as JSON.
- `Attestation`: claims as JSON array with optional confidences; weighted contributions to trust.
- `AuditLog`: op metadata + hashes, forms the linear chain.
- `Checkpoint`: daily digest of audit entries.

Future: normalize financial tables; add `Dispute` and attachments with evidence hashes.

## 4. Trust Score (Stub)

- Factors (PRD §6/§16):
  - Direct trades: time-decayed value and simple status weights
  - Attestations: average confidence, time-decayed, weighted
  - Disputes, network testimony: set to 0 in MVP

This is intentionally simple and explainable; extend later with path-based testimony.

## 5. Endpoints Overview

- `POST /invoices`: create idempotent invoice and append to audit chain.
- `POST /attestations`: attach attestations to invoices with audit logging.
- `GET /trust/score`: return score with factors.
- `POST /checkpoints/generate`: produce daily Merkle root (dev-exempt from signatures).
- `GET /checkpoints/{date}/verify`: recompute and compare root.
- `GET /debug/audit-log`: verify linear chain continuity.

## 6. Running Locally

See project `README.md` for Quick Start and `examples/full_demo.py` for a scripted walkthrough.

## 7. Next Steps

- Tests: unit (canonicalization, signatures, Merkle); integration (invoice→attestation→trust; checkpoint verify)
- CSV adapters and email-to-invoice draft
- Disputes and settlement suggestions
- Web UI and relay mirroring

## 8. Security Notes

- Ed25519 signature verification fails fast; invalid requests are rejected with 401.
- Rate limits and anomaly flags are planned (PRD §11); keep signatures mandatory for writes.
- Checkpoints can be published to mirrors for offline verification.

---

For details, browse:
- `app/middleware/signatures.py` – signature enforcement
- `app/utils/crypto.py` – canonical JSON and hashing
- `app/routers/*` – endpoints and flows
- `app/models.py` – schema definitions

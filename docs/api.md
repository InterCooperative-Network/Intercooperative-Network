# ICN API (Weekend MVP)

Base URL: http://localhost:8000

## Auth

- Signed writes: headers `X-Key-Id` (org URN) and `X-Signature` (Ed25519 over canonical JSON)
- Content-Type: application/json for all POST/PATCH

## Invoices

POST /invoices
- Headers: Idempotency-Key, X-Key-Id, X-Signature
- Body: {from_org, to_org, lines[], total, terms{}, signatures[]}
- 200: {id, row_hash}

GET /invoices
- Query: limit, offset
- 200: {items: [...]} 

GET /invoices/{id}
- 200: invoice record

## Attestations

POST /attestations
- Headers: X-Key-Id, X-Signature
- Body: {subject_type:"invoice", subject_id, claims[], weight}
- 200: {id, row_hash}

GET /attestations?subject_id=...
- 200: {items: [...]}

## Trust

GET /trust/score?from_org=...&to_org=...&include_factors=true
- 200: {score, confidence, factors}

## Checkpoints

POST /checkpoints/generate?date=YYYY-MM-DD
- Dev-exempt from signatures
- 200: {date, operations_count, merkle_root}

GET /checkpoints/{date}/verify
- 200: {ok, merkle_root, count}

GET /checkpoints/artifacts/{date}
- 200: {date, merkle_root, count, head_hash, prev_head_hash}

## Orgs

GET /orgs
- 200: {items: [{org_id, display_name, pubkey}]}

GET /orgs/{org_id}
- 200: {org_id, display_name, pubkey, metadata, created_at}

## Debug

GET /debug/audit-log
- 200: {count, chain_ok, head, last_rows, continuity}

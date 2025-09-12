# Security Model (MVP)

## Signed Writes
- Every write requires Ed25519 signature over canonical JSON
- Prevents tampering and forgery in transit

## Audit Chain
- Each write computes payload_hash and row_hash chained to prev_hash
- Detects deletion or mutation of historical rows

## Checkpoints
- Daily Merkle root over audit entries
- Enables offline verification and mirror checks

## Key Management (Demo)
- Demo keys generated via seed script and stored locally (demo_keys.json)
- Production should use secure storage and rotation ceremonies (PRD v0.3)

ICN 5-Minute Demo Script

Narrative: "Integrity-first rails for inter-coop trade"

1) Press play
   - Run `make demo-up`
   - This brings up Postgres, applies migrations, seeds 3 orgs and keys, and prints ready-to-run commands

2) Create an invoice (alpha → beta)
   - Shows signed write and idempotency
   - Copy/paste from printed HTTPie output or run `examples/httpie/10_create_invoice_alpha_to_beta.sh`

3) Accept the invoice (beta)
   - Demonstrates multi-party workflow and append-only audit

4) Post third-party attestation (gamma)
   - External validator contributes signal

5) Dispute another invoice (alpha) and see impact on trust
   - Query `GET /trust/score?include_factors=true` to see factor breakdown

6) Generate daily checkpoint and verify
   - Demonstrates merkle root over audit rows and continuity
   - Shows artifact written to `.demo/checkpoints/<DATE>.json` and mirror verification (`make mirror-verify DATE=<DATE>`)

7) Open the mini web viewer
- Bonus: export for finance
  - Run `make export-qb` to produce QuickBooks-style journal JSON
- Bonus: browse org directory
  - `http :8000/orgs` to list seeded orgs and pubkeys
   - `make web` then open the localhost URL
   - Use the five buttons to repeat the flow and copy curl commands

Talking points
- Signed writes over canonical JSON
- Append-only audit chain with continuity
- Daily checkpoints (Merkle) for receipt-like verifiability
- Deterministic seeds and timestamps for reproducibility
- CSV import: we meet you where you are



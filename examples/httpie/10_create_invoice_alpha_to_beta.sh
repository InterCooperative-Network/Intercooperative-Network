#!/usr/bin/env bash
set -euo pipefail

BASE=${DEMO_BASE_URL:-http://localhost:8000}
ORG=urn:coop:alpha-bakery
BODY=examples/httpie/payloads/invoice_alpha_to_beta.json
SIG=$(python3 tools/sign.py -i "$BODY" -o "$ORG")

http POST "$BASE/invoices" \
  Content-Type:application/json \
  Idempotency-Key:demo-inv-a \
  X-Key-Id:"$ORG" \
  X-Signature:"$SIG" \
  < "$BODY"
echo "OK: create invoice A"



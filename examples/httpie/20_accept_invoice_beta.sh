#!/usr/bin/env bash
set -euo pipefail

BASE=${DEMO_BASE_URL:-http://localhost:8000}
ORG=urn:coop:beta-housing
INVOICE_ID=${1:-1}
BODY=examples/httpie/payloads/empty.json
SIG=$(python3 tools/sign.py -i "$BODY" -o "$ORG")
http POST "$BASE/invoices/$INVOICE_ID/accept" \
  Content-Type:application/json \
  X-Key-Id:"$ORG" \
  X-Signature:"$SIG" \
  < "$BODY"
echo "OK: accept invoice $INVOICE_ID"



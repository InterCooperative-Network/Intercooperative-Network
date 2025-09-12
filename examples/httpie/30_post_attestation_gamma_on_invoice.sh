#!/usr/bin/env bash
set -euo pipefail

BASE=${DEMO_BASE_URL:-http://localhost:8000}
ORG=urn:coop:gamma-audit
BODY=examples/httpie/payloads/attestation_on_a.json
SIG=$(python3 tools/sign.py -i "$BODY" -o "$ORG")
http POST "$BASE/attestations" \
  Content-Type:application/json \
  X-Key-Id:"$ORG" \
  X-Signature:"$SIG" \
  < "$BODY"
echo "OK: attestation"



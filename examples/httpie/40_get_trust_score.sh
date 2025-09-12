#!/usr/bin/env bash
set -euo pipefail

BASE=${DEMO_BASE_URL:-http://localhost:8000}
http "$BASE/trust/score?from_org=urn:coop:alpha-bakery&to_org=urn:coop:beta-housing&include_factors=true"
echo "OK: trust score"



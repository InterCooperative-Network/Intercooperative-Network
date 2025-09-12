#!/usr/bin/env bash
set -euo pipefail

BASE=${DEMO_BASE_URL:-http://localhost:8000}
http "$BASE/orgs"
echo "OK: orgs"



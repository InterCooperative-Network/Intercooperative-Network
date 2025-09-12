#!/usr/bin/env bash
set -euo pipefail

BASE=${DEMO_BASE_URL:-http://localhost:8000}
DATE=$(date -u +%F)
http POST "$BASE/checkpoints/generate" date==$DATE > /dev/null
http "$BASE/checkpoints/$DATE/verify"
echo "OK: checkpoint $DATE"



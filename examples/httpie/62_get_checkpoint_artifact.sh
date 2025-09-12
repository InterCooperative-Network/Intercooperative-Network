#!/usr/bin/env bash
set -euo pipefail

BASE=${DEMO_BASE_URL:-http://localhost:8000}
DATE=${1:-$(date -u +%F)}
http "$BASE/checkpoints/artifacts/$DATE"
echo "OK: artifact $DATE"



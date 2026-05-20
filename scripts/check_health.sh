#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"

curl -fsS "${BASE_URL}/v1/health"
echo
curl -fsS "${BASE_URL}/v1/health/db"
echo


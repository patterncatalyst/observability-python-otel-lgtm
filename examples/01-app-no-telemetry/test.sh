#!/usr/bin/env bash
# scripts/test-template.sh — copy per example; smoke-tests one demo against a
# running stack. Exits non-zero on failure so the aggregator can gate on it.
set -euo pipefail
API="${API:-http://localhost:8080}"
resp="$(curl -sf -X POST "$API/compute" -H 'content-type: application/json' -d '{"n": 100}')"
echo "$resp"
echo "$resp" | grep -q '"result": 5050' || { echo "FAIL: expected result 5050 for n=100"; exit 1; }
echo "PASS"

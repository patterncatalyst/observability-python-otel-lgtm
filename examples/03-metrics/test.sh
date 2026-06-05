#!/usr/bin/env bash
set -euo pipefail
for i in $(seq 1 20); do
  curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
    -d '{"customer_id":"t","sku":"WIDGET-001","quantity":1}' || true
done
echo "ok: load sent (RED metrics should appear in Mimir)"

#!/usr/bin/env bash
set -euo pipefail
resp="$(curl -sS -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"t","sku":"WIDGET-001","quantity":1}')"
echo "$resp" | grep -q '"status":"confirmed"' || { echo "order not confirmed: $resp"; exit 1; }
sleep 2
echo "ok: order confirmed; shipping/notification spans should share the trace"

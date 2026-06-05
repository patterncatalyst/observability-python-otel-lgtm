#!/usr/bin/env bash
set -euo pipefail
curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"t","sku":"WIDGET-001","quantity":1}' || true
sleep 2
logs="$(podman logs --tail 20 order 2>/dev/null || true)"
echo "$logs" | grep -q 'trace_id' || { echo "no trace_id in logs"; exit 1; }
echo "ok: logs carry trace_id"

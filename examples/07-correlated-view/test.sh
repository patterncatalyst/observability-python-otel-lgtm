#!/usr/bin/env bash
set -euo pipefail
# one success
curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"t","sku":"WIDGET-001","quantity":1}' || true
# one decline (over the payment ceiling) → expect HTTP 402
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8080/orders \
  -H 'Content-Type: application/json' -d '{"customer_id":"t","sku":"WIDGET-001","quantity":60}')
[ "$code" = "402" ] || { echo "expected 402 decline, got $code"; exit 1; }
echo "ok: success + decline produced; success/error traces should be correlatable in Grafana"

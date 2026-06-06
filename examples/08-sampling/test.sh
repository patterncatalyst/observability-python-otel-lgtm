#!/usr/bin/env bash
set -euo pipefail
curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"t","sku":"WIDGET-001","quantity":1}' || true
code=$(curl -s -o /dev/null -w '%{http_code}' -X POST http://localhost:8080/orders \
  -H 'Content-Type: application/json' -d '{"customer_id":"t","sku":"WIDGET-001","quantity":60}')
[ "$code" = "402" ] || { echo "expected 402 decline, got $code"; exit 1; }
echo "ok: traffic produced; verify in Tempo that errors + /orders survive and healthy traffic is sampled to ~5%"

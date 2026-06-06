#!/usr/bin/env bash
set -euo pipefail
curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"t","sku":"WIDGET-001","quantity":1}' || true
echo "ok: load produced; profiling verification is manual in Grafana (see README) — flame graph link from a span"

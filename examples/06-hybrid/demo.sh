#!/usr/bin/env bash
# Demo 6 — the hybrid: auto-instrumentation for breadth, custom spans for depth,
# both in one trace. Same code as everything else, fully instrumented.
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=false
export PROPAGATE_KAFKA_CONTEXT=true
echo "Bringing up the services, fully instrumented (auto + custom)..."
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

oid=$(curl -sS -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"cust-1","sku":"WIDGET-001","quantity":1}' | sed -n 's/.*"order_id":"\([^"]*\)".*/\1/p')
echo "placed order $oid"
curl -sS -X POST http://localhost:8081/graphql -H 'Content-Type: application/json' \
  -d "{\"query\":\"{ order(orderId: \\\"$oid\\\") { status reviews { rating } } }\"}" >/dev/null && echo "ran a GraphQL read"

cat <<'MSG'

Open Grafana > Explore > Tempo and open the latest order trace. In ONE tree you
see both layers:
  • auto    — POST /orders, the inventory/payment gRPC spans, the asyncpg queries
  • custom  — the shipping/notification consumer spans under the Kafka hop, and
              the review.resolve_* spans under the GraphQL query

Compare it to Demo 2 (custom layer off): there the consumers floated into their
own traces and GraphQL was one blind span. The difference IS the hybrid layer.
Look for any operation showing two near-identical spans — that would be
double-instrumentation, which this repo avoids by propagating Kafka by hand and
leaving automatic Kafka instrumentation off.
MSG

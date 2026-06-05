#!/usr/bin/env bash
# Demo 2 — zero-code auto-instrumentation. Turn the SDK on and the synchronous
# hops are traced for free. The async Kafka hop is deliberately left un-propagated
# here so you can see the trace break at the message boundary (Demo 5 fixes it).
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=false
export PROPAGATE_KAFKA_CONTEXT=false
echo "Bringing up the services with telemetry ENABLED (Kafka propagation off)..."
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

curl -sS -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"cust-1","sku":"WIDGET-001","quantity":1}'; echo

cat <<'MSG'

Open Grafana > Explore > Tempo and find the most recent trace.
You get ONE trace spanning the order REST handler, both gRPC calls (inventory,
payment), and every Postgres query — with no tracing code in the services. That
is auto-instrumentation: FastAPI + gRPC + asyncpg, wired by obs.otel.setup().

But notice the shipping and notification work shows up as SEPARATE, parented-to-
nothing traces. Context did not cross the Kafka boundary. Demo 5 closes that gap.
MSG

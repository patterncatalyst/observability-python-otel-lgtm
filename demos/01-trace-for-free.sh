#!/usr/bin/env bash
# Demo 1 — A trace for free: one request across REST, gRPC, and Postgres
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/lib/_demo.sh"

demo_title 1 "A trace for free — one request across REST, gRPC, and Postgres"
require_tools curl jq || exit 0
require_stack || exit 0

demo_intro "There is not one line of tracing code in the order handler. The \
OpenTelemetry SDK plus the auto-instrumentation for FastAPI, gRPC, and asyncpg \
produce a full distributed trace on their own. We'll place a single order — \
which fans out over gRPC to inventory and payment and writes to Postgres — and \
then open the trace in Tempo and read it top to bottom."

section "Step 1 — Place one order"
say "A POST to the order service reserves stock (gRPC → inventory), authorises \
payment (gRPC → payment), writes the order row, and publishes an event. Watch \
the response come back with an order id and a status."
run "curl -sS -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"demo\",\"sku\":\"WIDGET-001\",\"quantity\":1}' | jq ."

section "Step 2 — Open the trace in Tempo"
watch "one trace whose root is the order service's POST /orders span, with \
child spans for the two gRPC calls (inventory Reserve, payment Authorize) and \
the asyncpg INSERTs nested underneath — none of which we wrote by hand."
browser "$GRAFANA_URL/explore" "Pick the Tempo data source, click Search, and \
open the most recent POST /orders trace. Expand the span tree: order → gRPC \
Reserve → gRPC Authorize → the database writes. Point out the service \
boundaries and the per-span timings."

say "Every one of those spans came from auto-instrumentation reading the \
libraries the service already uses. The handler just does its job; the SDK \
turns the request into a trace and ships it to the Collector over OTLP."

demo_end "A full distributed trace across REST, gRPC, and Postgres — with zero \
tracing code in the application. Next: the one place auto-instrumentation \
can't follow on its own — the jump across Kafka."

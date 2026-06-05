#!/usr/bin/env bash
# Demo 7 — the correlated view. Drive a realistic mix of traffic, then follow one
# request across traces, logs, and metrics in Grafana.
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=false
export PROPAGATE_KAFKA_CONTEXT=true
echo "Bringing up the services, fully instrumented..."
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

echo "Driving a mix of successful orders and a few that trip the payment ceiling..."
for i in $(seq 1 30); do
  curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
    -d '{"customer_id":"load","sku":"WIDGET-001","quantity":1}' || true
done
# a handful of declines (quantity * unit price > payment ceiling) → error traces
for i in $(seq 1 3); do
  curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
    -d '{"customer_id":"big","sku":"WIDGET-001","quantity":60}' || true
done

cat <<'MSG'

Now walk the four moves in Grafana (http://localhost:3000):

  1. Tempo — Explore > Tempo, service.name=order, open a trace. Read it top-down:
     the request's path across services, with a duration on each hop. Open a
     FAILED one: the Authorize span is the error, decline reason on the span.
  2. Span > logs — on a span, "Logs for this span" jumps to exactly that service's
     log lines for this trace (Loki, by trace_id).
  3. Metric > trace — open the order latency panel (Mimir); click an exemplar dot
     on a p99 bump to land on the slow trace behind it.
  4. Serde cost — compare a gRPC client span to its server span: the gap is wire +
     (de)serialization, and message-size attributes show the payload size.

One trace_id ties all of it together. That movement between signals is the point.
MSG

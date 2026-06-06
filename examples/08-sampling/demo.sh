#!/usr/bin/env bash
# Demo 8 — tail sampling: keep errors + slow + /orders, sample the healthy rest.
# Requires the tail-sampling Collector config to be mounted (see the chapter):
#   stack/compose.yaml: ./otelcol/config.tail-sampling.yaml:/otel-lgtm/otelcol-config.yaml:Z
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=false
export PROPAGATE_KAFKA_CONTEXT=true
echo "Bringing up the stack (ensure the tail-sampling config is mounted)..."
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

echo "Driving a mix: healthy orders, a few declines (errors), and lots of health reads..."
for i in $(seq 1 50); do
  curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
    -d '{"customer_id":"load","sku":"WIDGET-001","quantity":1}' || true
done
for i in $(seq 1 5); do          # over the payment ceiling -> error traces
  curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
    -d '{"customer_id":"big","sku":"WIDGET-001","quantity":60}' || true
done
for i in $(seq 1 80); do curl -sf -o /dev/null http://localhost:8080/health || true; done  # healthy, non-critical

cat <<'MSG'

In Tempo (http://localhost:3000):
  • every /orders trace is kept            (critical-routes policy)
  • every error trace (the declines)       (status_code policy)
  • the GET /health traffic is mostly gone — only the ~5% baseline survives
Watch the lgtm container's memory during load: it rises with in-flight traces and
settles as the 30s decision windows close — that curve is the cost of tail sampling.
MSG

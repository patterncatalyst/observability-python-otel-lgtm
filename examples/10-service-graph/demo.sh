#!/usr/bin/env bash
# Example 10 — the live service graph (Tempo metrics-generator → Grafana node graph).
# Requires Tempo's metrics-generator enabled with service-graphs + span-metrics,
# remote-writing to the bundled store (see _docs/12-service-graph.md). The Grafana
# service map is already provisioned in stack/grafana/datasources.yaml.
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=false
export PROPAGATE_KAFKA_CONTEXT=true   # so the Kafka hop shows up as edges
echo "Bringing up the stack..."
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

echo "Driving steady load so every edge carries traffic..."
for i in $(seq 1 200); do
  curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
    -d '{"customer_id":"load","sku":"WIDGET-001","quantity":1}' || true
  if [ $((i % 20)) -eq 0 ]; then
    curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
      -d '{"customer_id":"big","sku":"WIDGET-001","quantity":60}' || true   # a decline, to move the error rate
  fi
done

cat <<'MSG'

In Grafana (http://localhost:3000):
  • Tempo data source → Service Graph (or the Node Graph in Explore)
  • watch the topology: order → inventory/payment (gRPC), order → kafka →
    shipping/notification, order → postgres — with live rate/error/latency
  • the periodic declines make the payment edge's error rate move
If no graph appears, Tempo's metrics-generator isn't enabled or isn't
remote-writing to the store the service map points at — see _docs/12-service-graph.md.
MSG

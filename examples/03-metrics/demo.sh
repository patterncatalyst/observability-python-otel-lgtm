#!/usr/bin/env bash
# Demo 3 — metrics. Drive load and watch RED (rate, errors, duration) metrics,
# with exemplars that jump from a latency spike straight to an example trace.
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"; STACK="$ROOT/stack"
export OTEL_SDK_DISABLED=false
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

echo "Driving load at the REST edge..."
if command -v hey >/dev/null; then
  "$ROOT/tools/load/hey-orders.sh" 500 20
else
  echo "(hey not installed — sending a small burst with curl instead)"
  for i in $(seq 1 50); do
    curl -sf -o /dev/null -X POST http://localhost:8080/orders \
      -H 'Content-Type: application/json' \
      -d '{"customer_id":"load","sku":"WIDGET-001","quantity":1}' || true
  done
fi

cat <<'MSG'

Open Grafana > Explore (Mimir/Prometheus). Look at request rate and latency for
service.name="order". Turn on exemplars: the dots on the latency graph link to
the actual traces behind the slow requests.
MSG

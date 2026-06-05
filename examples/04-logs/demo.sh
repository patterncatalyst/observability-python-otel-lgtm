#!/usr/bin/env bash
# Demo 4 — logs correlated to traces. Every log line is JSON stamped with the
# active trace_id/span_id, so Loki and Tempo link both ways.
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=false
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

curl -sS -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"cust-1","sku":"WIDGET-001","quantity":1}'; echo
echo; echo "Recent order-service logs (note the trace_id on each line):"
podman logs --tail 5 order || true

cat <<'MSG'

Open Grafana > Explore > Loki. Filter {service_name="order"} and expand a line:
the trace_id field has a "View trace" link straight into Tempo. From a trace span
you can pivot the other way into its logs.
MSG

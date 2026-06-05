#!/usr/bin/env bash
# Demo 1 — the services with the OTel SDK switched OFF. The baseline pain: requests
# succeed, but the system is opaque. Nothing lands in Grafana.
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=true
echo "Bringing up the services with telemetry DISABLED..."
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

echo "Placing an order — it will succeed:"
curl -sS -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"cust-1","sku":"WIDGET-001","quantity":1}'; echo

cat <<'MSG'

Now open Grafana at http://localhost:3000 and look at Explore > Tempo.
There are no traces. Six services just collaborated across REST, gRPC, Kafka,
and Postgres to fulfil that order and you cannot see any of it. That opacity is
the problem the rest of the talk removes.
MSG

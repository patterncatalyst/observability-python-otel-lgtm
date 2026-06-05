#!/usr/bin/env bash
# Demo 5 — custom instrumentation across Kafka. Turn propagation back on and the
# async consumers rejoin the originating trace. One trace, end to end.
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=false
export PROPAGATE_KAFKA_CONTEXT=true
echo "Bringing up the mesh with Kafka context propagation ON..."
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

curl -sS -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
  -d '{"customer_id":"cust-1","sku":"WIDGET-001","quantity":1}'; echo

cat <<'MSG'

Open Grafana > Explore > Tempo and find the latest order trace. Compare it to
Demo 2: the shipping and notification consumer spans are now CHILDREN of the same
trace. The only difference is that the producer injects the trace context into
the Kafka message headers and the consumers extract it (obs.kafka_propagation).
That is the whole trick to tracing across an asynchronous boundary.
MSG

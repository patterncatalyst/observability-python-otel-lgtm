#!/usr/bin/env bash
# Demo 9 — continuous profiling (the fourth signal), via Pyroscope.
# SKETCH, not a settled recipe — see the chapter's verification note. To enable:
#   1. Use an otel-lgtm tag that bundles Pyroscope (recent 0.11+; 0.8.1 may not).
#   2. Add a profiles pipeline to stack/otelcol/config.yaml (chapter shows it).
#   3. Add `pyroscope-io` to services/common (the obs.profiling hook soft-imports it).
set -euo pipefail
STACK="$(git rev-parse --show-toplevel)/stack"
export OTEL_SDK_DISABLED=false
export PROPAGATE_KAFKA_CONTEXT=true
export PYROSCOPE_ADDRESS="${PYROSCOPE_ADDRESS:-http://lgtm:4040}"   # turns on obs.profiling
echo "Bringing up the stack with profiling enabled (PYROSCOPE_ADDRESS=$PYROSCOPE_ADDRESS)..."
( cd "$STACK" && podman compose up --build -d )
for i in $(seq 1 60); do curl -sf http://localhost:8080/health >/dev/null 2>&1 && break; sleep 2; done

echo "Driving load so there is CPU to profile..."
for i in $(seq 1 100); do
  curl -sf -o /dev/null -X POST http://localhost:8080/orders -H 'Content-Type: application/json' \
    -d '{"customer_id":"prof","sku":"WIDGET-001","quantity":1}' || true
done

cat <<'MSG'

In Grafana (http://localhost:3000):
  • open a slow /orders trace in Tempo
  • use "Profiles for this span" (Tempo datasource tracesToProfiles) to open the
    Pyroscope flame graph for that service + time window
  • read down from the widest frame to the function that spent the CPU
If the link or flame graph is empty, re-check the three enable steps at the top of
this script — profiling is the least-settled signal in this stack.
MSG

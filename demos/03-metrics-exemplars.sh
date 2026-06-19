#!/usr/bin/env bash
# Demo 3 — Metrics & exemplars: RED from the same traffic, then jump to a trace
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/lib/_demo.sh"

demo_title 3 "Metrics and exemplars — from a chart straight to a trace"
require_tools curl || exit 0
require_stack || exit 0

demo_intro "A trace is one request; a metric is the shape of all of them. The \
same auto-instrumentation that drew the trace also emits RED metrics — request \
Rate, Error ratio, and Duration — with no extra code. And an exemplar ties a \
single point on a latency histogram back to the actual trace that produced it. \
We'll send a burst of traffic, mostly healthy with a few declines, then read \
the curves in Grafana and click our way from a chart to a trace."

section "Step 1 — Send a burst of traffic"
say "Forty healthy orders so the rate and latency have shape:"
run "for i in \$(seq 1 40); do curl -sf -o /dev/null -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"load\",\"sku\":\"WIDGET-001\",\"quantity\":1}'; done; echo 'sent 40'"
say "Then five that decline at payment (quantity 60 is over the ceiling), so \
the error line has something to show — these come back HTTP 402:"
run "for i in \$(seq 1 5); do curl -sf -o /dev/null -w '%{http_code} ' -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"big\",\"sku\":\"WIDGET-001\",\"quantity\":60}'; done; echo"

section "Step 2 — Read the RED metrics, then click an exemplar"
watch "the request-rate curve climb with the burst, the 4xx ratio tick up from \
the five declines, and the p50/p95/p99 latency bands. Then find an exemplar \
dot on the duration histogram and click it — it opens the exact trace behind \
that data point."
browser "$GRAFANA_URL/explore" "Pick the Prometheus/Mimir data source and \
graph the order service's request rate and duration (or open the metrics \
dashboard). Hover the latency panel, click an exemplar dot, and follow it into \
Tempo — the chart just handed you a real trace."

say "None of those metrics were written by hand — they're the transport-level \
RED the instrumentation emits. The exemplar is the thread from the aggregate \
back to one request, which is what makes 'p99 is bad' immediately actionable."

demo_end "RED for free, and a one-click path from a slow point on a chart to \
the trace that caused it. Next: the third signal — logs that carry the same \
trace_id."

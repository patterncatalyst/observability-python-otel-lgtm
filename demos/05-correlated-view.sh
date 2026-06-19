#!/usr/bin/env bash
# Demo 5 — The correlated view: one request, read across traces, logs, metrics
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/lib/_demo.sh"

demo_title 5 "One request, three signals — the correlated view"
require_tools curl || exit 0
require_stack || exit 0

demo_intro "This is the payoff of Part 1. Start from a single interesting \
request — an order that gets declined at payment — and read it as a trace, as \
logs, and as a point in the metrics, pivoting on one screen without ever \
copy-pasting an id. The trace_id is what makes the three signals one story."

section "Step 1 — Cause one interesting request"
say "An order for sixty units is over the payment ceiling, so it declines with \
HTTP 402 — a clean, deterministic 'something went wrong' to investigate."
run "curl -sS -o /dev/null -w 'declined: HTTP %{http_code}\\n' -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"big\",\"sku\":\"WIDGET-001\",\"quantity\":60}'"

section "Step 2 — Read it three ways"
watch "in the trace, the payment Authorize span carrying the decline; one click \
to its logs; and the same 402 showing up in the error line of the metrics, \
with the exemplar pointing right back to this trace."
browser "$GRAFANA_URL/explore" "Open the declined order's trace in Tempo. Walk \
it: the Authorize span shows not-authorized → 'Logs for this span' shows the \
decline line in Loki → switch to the metrics and show this 402 in the 4xx \
ratio, exemplar linking back. Three signals, one request, no manual joining."

say "Nothing here was correlated by hand. One trace_id flows through the span, \
the log record, and the metric exemplar, so Grafana can walk you between them. \
That's the whole reason to adopt all three signals together rather than one at \
a time."

demo_end "From a single 402 to the span, the log, and the metric that explain \
it — on one screen. Next: keeping all of this affordable at volume — sampling."

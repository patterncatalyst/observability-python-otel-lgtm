#!/usr/bin/env bash
# Demo 4 — Correlated logs: every line carries its trace_id, both ways
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/lib/_demo.sh"

demo_title 4 "Correlated logs — every line carries its trace_id"
require_tools curl || exit 0
require_stack || exit 0

demo_intro "A log line on its own tells you what happened, not which request it \
belonged to. Our logs are JSON, stamped with the active trace_id, and exported \
over OTLP to Loki — so a line in Loki links to its trace in Tempo, and a span \
in Tempo links back to its logs. We'll place one order and walk that link in \
both directions."

section "Step 1 — Place an order"
say "One order, so we have a fresh trace_id to follow through the logs."
run "curl -sS -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"demo\",\"sku\":\"WIDGET-001\",\"quantity\":1}' -w '\\n'"

section "Step 2 — From a log line to its trace"
watch "the JSON log line for this order, with a trace_id field. Loki turns \
that into a clickable link straight to the trace in Tempo."
browser "$GRAFANA_URL/explore" "Pick Loki, query {service_name=\"order\"}, and \
open the newest line. Show the structured JSON — message plus trace_id — then \
click the trace_id derived field to jump into the trace in Tempo."

section "Step 3 — …and back again"
watch "the reverse pivot: from a span in Tempo, 'Logs for this span' filters \
Loki to exactly that request's lines."
browser "$GRAFANA_URL/explore" "In the trace you just opened, use 'Logs for \
this span' to drop back into Loki, now filtered to this one trace. Two signals, \
one id, joined both ways."

say "The trace_id is the join key. obs.logging stamps it onto the stdout JSON \
for the console, and the OTLP log records Loki receives carry it automatically \
from the active span — same id, two places."

demo_end "Logs stopped being a separate haystack: every line knows its trace, \
and every span knows its logs. Next: all three signals on one screen."

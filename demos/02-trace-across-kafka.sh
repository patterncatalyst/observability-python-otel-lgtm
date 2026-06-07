#!/usr/bin/env bash
# Demo 2 — The trace breaks at Kafka, and the fix: context across the async hop
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/lib/_demo.sh"

demo_title 2 "The trace breaks at Kafka — and the fix"
require_tools curl podman || exit 0
require_stack || exit 0

demo_intro "Auto-instrumentation follows in-process calls, but a message queue \
is a gap: the producer publishes now, a consumer handles it later, in a \
different process. Out of the box the order service's trace stops at the \
publish. We'll prove that by turning context propagation OFF, then turn it \
back ON and watch shipping and notification rejoin the very same trace."

_recreate() {  # $1 = true|false  — restart the producer + consumers with the flag
    run_soft "(cd \"$STACK_DIR\" && PROPAGATE_KAFKA_CONTEXT=$1 podman compose up -d --force-recreate order shipping notification)"
    printf '%b' "  ${DIM}  waiting for the order service to go healthy${NC}"
    for _ in $(seq 1 30); do curl -sf -o /dev/null --max-time 2 "$ORDER_URL/health" && break; printf '.'; sleep 2; done
    echo; good "ready"
}

section "Step 1 — Turn propagation OFF and place an order"
say "PROPAGATE_KAFKA_CONTEXT=false makes the producer publish the event with \
no trace context in the message headers. We recreate just the producer and the \
two consumers — a few seconds — then place one order."
_recreate false
run "curl -sS -o /dev/null -w 'placed: HTTP %{http_code}\\n' -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"demo\",\"sku\":\"WIDGET-001\",\"quantity\":1}'"

watch "the order trace ENDS at the 'publish order.placed' span. Shipping and \
notification still run — but they show up as their own separate traces, with \
no causal link back to the order that triggered them."
browser "$GRAFANA_URL/explore" "Tempo → Search → open the latest POST /orders \
trace. Note it stops at the Kafka publish. Then search for shipping / \
notification spans and show they're orphaned in their own traces."

section "Step 2 — Turn propagation ON and place another"
say "PROPAGATE_KAFKA_CONTEXT=true switches on obs.kafka_propagation: the \
producer injects the W3C traceparent into the Kafka message headers, and each \
consumer extracts it and continues the trace. Same code path, one env flip."
_recreate true
run "curl -sS -o /dev/null -w 'placed: HTTP %{http_code}\\n' -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"demo\",\"sku\":\"WIDGET-001\",\"quantity\":1}'"

watch "now the trace continues THROUGH the publish into \
shipping.handle_order_placed and the notification consumer — one connected \
trace across the async boundary, spanning two extra processes and a broker."
browser "$GRAFANA_URL/explore" "Tempo → open the newest POST /orders trace. \
Expand past the publish span: shipping and notification are now child spans of \
the same trace. That's the fix, live."

demo_end "Auto-instrumentation got us everything up to the broker; carrying \
W3C context through the Kafka headers by hand carried the trace across it. \
Next: metrics, and the exemplar that jumps from a chart straight to a trace."

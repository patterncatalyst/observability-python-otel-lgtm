#!/usr/bin/env bash
# Demo 6 — Tail sampling: keep errors, slow, and /orders; drop the healthy rest
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/lib/_demo.sh"

demo_title 6 "Tail sampling — keep what matters, drop the rest"
require_tools curl || exit 0
require_stack || exit 0

demo_intro "At real traffic you can't keep every trace. The app exports 100% \
and the Collector decides what survives: with the tail-sampling config it keeps \
every error, every request over a second, and every /orders call, and samples \
the healthy remainder down to a baseline. We'll drive a mix and confirm in \
Tempo that the interesting traces are all there while most of the healthy noise \
is gone."

# Soft check: is the tail-sampling config the one mounted?
if grep -q 'config.tail-sampling.yaml' "$STACK_DIR/compose.yaml" 2>/dev/null; then
    good "tail-sampling Collector config appears to be mounted"
else
    note "This demo needs the tail-sampling Collector config mounted. It's a one-line"
    printf '%b\n' "    swap in stack/compose.yaml (see _docs/10-sampling.md), then: podman compose up -d --force-recreate lgtm"
    caution "Continuing anyway — without it, every trace is kept and the contrast won't show."
fi

section "Step 1 — Drive a representative mix"
say "Fifty healthy orders, five declines (errors), and a hundred health reads \
(healthy, non-critical — the traffic tail sampling should mostly drop):"
run "for i in \$(seq 1 50); do curl -sf -o /dev/null -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"load\",\"sku\":\"WIDGET-001\",\"quantity\":1}'; done; \
for i in \$(seq 1 5); do curl -sf -o /dev/null -X POST \"\$ORDER_URL/orders\" -H 'Content-Type: application/json' -d '{\"customer_id\":\"big\",\"sku\":\"WIDGET-001\",\"quantity\":60}'; done; \
for i in \$(seq 1 100); do curl -sf -o /dev/null \"\$ORDER_URL/health\"; done; echo 'mix sent'"

section "Step 2 — See what survived"
watch "in Tempo: every /orders trace present, every error (the declines) \
present, and the GET /health flood largely gone — only the ~5% probabilistic \
baseline survives. Then glance at the lgtm container's memory: it rises with \
in-flight traces and settles as the decision windows close. That curve is the \
cost of the intelligence."
browser "$GRAFANA_URL/explore" "Tempo → Search. Filter to errors and show they \
were all kept; filter to /orders and show those were all kept; then search the \
healthy GET /health traffic and show how little of it made it through."

say "The services never changed — sampling is entirely a Collector config. \
You decide what's worth keeping by how a trace turned out, not blindly up \
front, and you pay for it in Collector memory rather than storage."

demo_end "Errors, slow requests, and critical routes kept; healthy noise \
sampled away; the app none the wiser. Next: the fourth signal — profiling."

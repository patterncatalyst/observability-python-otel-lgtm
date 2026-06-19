#!/usr/bin/env bash
# Demo 8 — The live service graph: the whole system, lighting up in real time
HERE="$(cd "$(dirname "$0")" && pwd)"; source "$HERE/lib/_demo.sh"

demo_title 8 "The live service graph — what's going on right now"
require_tools curl || exit 0
require_stack || exit 0

demo_intro "The operational view: an animated map of the services with live \
request and error rates on every hop. The Kiali-style 'what's happening right \
now' picture — but built straight from the traces, with no service mesh, no \
sidecars, and no Kubernetes. Tempo's metrics-generator turns span-to-span \
relationships into a service graph, and Grafana renders it as a node graph. \
We'll run steady load and watch the topology come alive."

section "Step 1 — Put the system under steady load"
say "A continuous stream of orders so every edge — REST in, gRPC to inventory \
and payment, the Kafka hop to shipping and notification, and the database \
writes — carries live traffic while we watch."
load_start 400

section "Step 2 — Open the live service graph"
watch "the node graph drawing itself from the traffic: order at the edge, gRPC \
to inventory and payment, the Kafka hop out to shipping and notification, and \
Postgres underneath — each node and edge labelled with request rate, error \
rate, and latency, updating as the load runs."
browser "$GRAFANA_URL/explore" "Pick the Tempo data source and open the Service \
Graph (or the Node Graph in Explore). Walk the topology and point at the live \
RED on each edge. Cause a few declines in another terminal and watch the \
payment edge's error rate move."

say "This is the same correlation idea, one level up: instead of one trace, the \
shape of all of them. And it's pure OpenTelemetry — derived from the spans the \
services already emit, which is why it needs none of the mesh machinery a tool \
like Kiali assumes."

demo_end "The whole system, live, from the traces alone — the operational \
companion to the per-request views. That's the set: one request made legible, \
all four signals, and the live map of the lot."

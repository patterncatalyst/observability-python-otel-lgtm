---
title: "The live service graph"
order: 12
part: "The pipeline"
description: "An animated map of the whole system with request and error rates on every hop — the Kiali-style 'what's happening right now' view, built straight from the traces with no service mesh, no sidecars, and no Kubernetes."
duration: 11 minutes
---

Every view so far has started from one request. This one starts from all of
them at once. The live service graph is the operational picture — a topology of
the services with request rate, error rate, and latency on every edge, updating
as traffic flows. If you have reached for Kiali to get this, the surprise here
is that you do not need a service mesh, sidecars, or Kubernetes to have it: the
graph is derived from the traces the services already emit.

{% include excalidraw.html file="fig-13-service-graph" alt="A node graph with order at the edge, gRPC edges to inventory and payment labelled with request and error rates, a Kafka hop out to shipping and notification, and a database edge to postgres; a caption notes it is built by Tempo's metrics-generator from span relationships with no service mesh, sidecars, or Kubernetes." caption="Figure 12.1 — The live service graph: request rate, error rate, and latency on every edge, derived from traces" %}

## Where the graph comes from

Tempo runs a **metrics-generator** that watches spans go by and emits two
families of metrics from them. The `service-graphs` processor pairs each
client/server (and producer/consumer) span with its partner and counts the
edges between services — that is the topology and the per-edge request and error
rates. The `span-metrics` processor emits RED metrics per span name — the
per-node rates and latencies. Both are written to the same Prometheus-compatible
store the rest of your metrics live in (the bundled Mimir), and Grafana renders
them as a node graph.

The important property is *how* it reads the topology. It does not sniff the
network or read a mesh's config; it inspects spans for OpenTelemetry semantic
conventions — direct calls via client/server span kinds, messaging hops via
producer/consumer span kinds, and database calls via `db.*` attributes. That is
exactly the shape this system already produces: REST and gRPC give it the
order → inventory and order → payment edges, the Kafka hop gives it
order → shipping and order → notification (because §7 set the producer and
consumer span kinds the processor keys on), and asyncpg gives it the edge to
Postgres. The graph is a free consequence of having instrumented the services —
no new agent, no mesh.

## Turning it on

Two pieces have to line up. First, Tempo's metrics-generator must be enabled and
told which processors to run, writing to the metrics store:

```yaml
# Tempo overrides — enable the generator for the service graph
overrides:
  defaults:
    metrics_generator:
      processors: [service-graphs, span-metrics]
metrics_generator:
  storage:
    remote_write:
      - url: http://localhost:9090/api/v1/write   # the bundled metrics store
```

Second, Grafana's Tempo data source needs its **service map** pointed at that
store, which is the one committed piece of this in the repo
(`stack/grafana/datasources.yaml`):

```yaml
jsonData:
  serviceMap:
    datasourceUid: prometheus
```

With both in place, the Tempo data source grows a **Service Graph** tab, and
Explore can draw the node graph for any time window.

## Build, run, observe

```bash
cd examples/10-service-graph && ./demo.sh
```

The demo puts the system under steady load and leaves it running. Open Grafana,
pick the Tempo data source, and open the Service Graph (or the Node Graph in
Explore). Watch the topology draw itself: `order` at the edge, gRPC to inventory
and payment, the Kafka hop to shipping and notification, Postgres underneath —
each node and edge carrying live rate, error, and latency. Cause a few declines
and watch the payment edge's error rate move.

## Cross-check

Drive load, then confirm the graph shows every edge you expect — including the
Kafka hop, which only appears if producer/consumer context propagation is on
(Demo 2's `PROPAGATE_KAFKA_CONTEXT`). A missing shipping or notification edge is
the same broken-async-link from §7, seen from above. If no graph appears at all,
the metrics-generator isn't enabled or isn't remote-writing to the store the
service map points at.

## What you learned

- The service graph is the operational, all-requests-at-once view: live RED on
  every node and edge of the topology.
- It is built by Tempo's metrics-generator from the spans you already emit —
  client/server, producer/consumer, and `db.*` — so it needs no service mesh,
  no sidecars, and no Kubernetes, unlike a mesh console such as Kiali.
- Enabling it is two bits of config: the generator's processors plus remote
  write, and the Grafana service-map pointing at the metrics store.

That is the whole system, live, from the traces alone — the operational
companion to the per-request correlation the rest of the talk builds.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm the bundled Tempo enables the metrics-generator with the
`service-graphs` and `span-metrics` processors and remote-writes to the bundled
store, that the Grafana service map resolves against it, and that the Kafka hop
shows up as producer/consumer edges. The Tempo generator config above is shown
as the shape to apply; only the Grafana service-map setting is committed, to
avoid baking a version-sensitive Tempo override into the default stack.*

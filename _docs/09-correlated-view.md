---
title: "Reading it in Grafana: the correlated view"
order: 9
part: "The three signals"
description: "Open Grafana and follow one request across all three signals — read a trace as a business flow, jump from a span to its logs, and from a latency spike to the trace behind it."
duration: 16 minutes
---

You have produced traces, metrics, and logs, and stamped all three with one shared
identity. This chapter is the payoff: opening Grafana and actually *using* that
correlation. It is the part that answers the questions that send most people
looking for observability in the first place — where did the time go, which
service failed, and what did that service log at the moment it did — none of which
a wall of disconnected log lines can tell you.

The driver is `examples/07-correlated-view/`, which sends a realistic mix of
traffic: mostly successful orders, plus a few large enough to trip the payment
ceiling so there are error traces to find. Run it, then follow the four moves
below in Grafana at `http://localhost:3000`.

{% include excalidraw.html file="fig-11-correlation-graph" alt="A trace in Tempo links to its logs in Loki by trace_id and to its metrics in Mimir by exemplar; arrows show the pivots between the three signals." caption="Figure 9.1 — One trace_id makes traces, logs, and metrics one view" %}

## 1. The trace, read as a business flow

In **Explore → Tempo**, search for `service.name = order` over the last fifteen
minutes and open a recent trace. Read it top down and it is not a pile of spans —
it is the request's path through your system, in order, with a duration on each
step: `POST /orders` at the root, then the `Reserve` call into inventory, the
`Authorize` call into payment, the `INSERT` into Postgres, the `order.placed`
publish, and — with propagation on — the shipping and notification consumers
hanging beneath it. That top-to-bottom read is the distributed business flow that
no single service's logs can give you, because no single service ever saw the
whole thing.

Now open one of the failed orders. The error is not a guess: the `Authorize` span
is marked error, with the decline reason sitting right on it as an attribute, and
the spans that would have followed (the publish, the consumers) simply are not
there because the request stopped. You have located the failing hop and its reason
without opening a single log file.

## 2. From a span to its logs

On any span, use **Logs for this span**. Grafana follows the span's `trace_id`
into Loki and lands you on exactly the JSON lines that service emitted while that
span was open — no grep, no guessing the right five-minute window, no scrolling
past other requests' noise. This is the pivot the logging stamp from Chapter 6 was
built for: the `trace_id` field on every line is what Loki's derived-field
configuration turns into this link.

## 3. From a metric spike to a trace

Open the order service's latency panel in **Mimir/Prometheus**. When p99 bumps,
you want the request behind the bump, not a hunch — and the exemplar dots on the
histogram are exactly that: each is a sampled `trace_id` captured when a slow
measurement was recorded inside a span. Click one and you are in Tempo on a real
slow request from that moment. This is the aggregate-to-concrete direction:
metrics tell you *something* is slow, the exemplar tells you *which one* so you can
read why.

## 4. The serialization cost, made visible

The pain that sends teams here is often invisible cost between services — time
spent on the wire and in serializing and deserializing payloads. It is on the
trace already: look at a gRPC client span and the matching server span beneath it.
The client span is wall-clock from the caller's side; the server span is the work
inside the callee; the gap between them is network plus (de)serialization, and the
message-size attributes on the spans tell you how big the payload was. You are
reading the serde cost of a call directly off the trace, per request, instead of
inferring it from aggregate dashboards.

## Why the pivots work

All four moves rely on one thing: a single `trace_id` flowing through every hop —
carried automatically across HTTP and gRPC, carried by hand across Kafka (Chapter
7). Logs carry that id as a field, so Loki can link to Tempo; metrics carry it as
an exemplar, so a histogram bucket can link to Tempo. The shared identity is the
entire reason any of these pivots is one click rather than an afternoon. Three
signals from one SDK with one resource is not tidiness for its own sake — it is
what makes the movement between them possible.

## Build, run, observe

```bash
cd examples/07-correlated-view && ./demo.sh
```

It drives the traffic mix, then prints the click-path for the four moves above so
you can follow along live.

## Cross-check

Take the `order_id` from one REST response and find it in three places: as an
attribute on its trace in Tempo, in the order service's logs for that trace in
Loki, and in the `orders` table in Postgres. One identifier, three stores,
agreeing — when they do, your correlation is wired correctly end to end.

## What you learned

- A trace read top down is your distributed system's business flow, with the
  timing and the failing hop in plain sight.
- `trace_id` is the join key: it makes span → logs and metric → trace single
  clicks, via Loki derived fields and metric exemplars.
- The value of the three signals is not any one of them — it is the movement
  between them, which only the shared identity makes cheap.

That closes the three signals. The next part moves the costly decisions —
sampling, and what to keep at volume — out of the application and into the
Collector.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm the span-to-logs link resolves in this build of the
otel-lgtm image, exemplars are enabled on the metric panels, and the gRPC
message-size attributes are present. The exact "Logs for this span" affordance
depends on the bundled Grafana/Tempo/Loki versions.*

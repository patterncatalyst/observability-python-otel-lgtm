---
title: "Observability fundamentals"
order: 2
part: "Foundations"
description: "The three signals and the OpenTelemetry data path — and why a shared trace context is the whole point."
duration: 15 minutes
---

You can bolt a metrics library onto a service, or adopt a structured-logging
format, or add a tracer, and end up with three tools that know nothing about
each other. This chapter is about the model that makes them one system instead
of three: what each signal is for, how OpenTelemetry moves them, and the shared
identifier that lets you pivot between them.

{% raw %}{% include excalidraw.html file="fig-02-otel-data-path" alt="A Python service with the OpenTelemetry SDK emits traces, metrics, and logs over OTLP to the Collector, whose receivers, processors, and exporters route each signal to Tempo, Mimir, and Loki, all viewed in Grafana." caption="Figure 2.1 — One SDK, one Collector, three backends, one UI" %}{% endraw %}

## Three signals, three questions

The three signals answer different questions about the same system, and their
strength is in combination.

A **trace** answers *where did the time go, and what happened along the way*. It
is a tree of spans — one span per unit of work — each with a start, a duration,
and attributes. Every span in a trace shares one `trace_id`; each span has its
own `span_id` and points at its parent. For our demo, one trace should span the
HTTP request, both gRPC calls, the Postgres writes, the Kafka publish, and the
shipping and notification consumers that react to it.

A **metric** answers *how much, how often, how slow — in aggregate*. Metrics are
cheap numbers aggregated over time: request rate, error rate, duration
percentiles. They are what alerts fire on, because they are small enough to keep
for everything, always.

A **log** answers *what exactly happened at this instant*. A log line is a
timestamped record, ideally structured. Logs carry the detail a metric averages
away and a span does not have room for.

Their costs differ as much as their jobs, which is why the pipeline later treats
them differently. Metrics are cheap enough to keep for everything, all the time —
a fixed set of numbers per series regardless of traffic. Traces are richer and
grow with every request, so at volume they are usually sampled rather than kept
whole. Logs are the most voluminous of the three and the easiest to let sprawl,
so they earn their keep only where the detail is worth the storage. Holding that
asymmetry in mind now makes the sampling decisions in the last part read as
economics rather than arbitrary knobs.

The trap is treating them as three products. The metric tells you error rate
just spiked; the trace shows you which hop is failing; the log line tells you the
exact exception. That hand-off only works if all three carry the same
identifiers — which is what OpenTelemetry gives you.

## The OpenTelemetry data path

OpenTelemetry separates *producing* telemetry from *shipping* it. In your
process, the **SDK** creates spans, records measurements, and emits log records,
all described by a shared **resource** (the `service.name`, version, and
environment that say who produced this). The SDK exports over **OTLP**, the
OpenTelemetry wire protocol, to a **Collector**.

The Collector is the decision point, and Figure 2.1 shows its three internal
stages. **Receivers** accept OTLP (here on HTTP port 4318). **Processors** act on
the stream in order — a `memory_limiter` so a telemetry flood cannot take the
Collector down, a `batch` processor to ship efficiently, and later a sampler.
**Exporters** route each signal onward: traces to Tempo, metrics to Mimir, logs
to Loki. Grafana reads all three and, because they share identifiers, links them.

Putting the Collector in the path — rather than exporting straight from the app
to each backend — is what lets sampling, batching, redaction, and routing be
configured in one place, owned by whoever runs the platform, without touching
application code. The application emits everything; the Collector decides what
survives.

## Why the shared context is the point

The reason this is one system and not three is **context propagation**. When a
span is active, the SDK can stamp its `trace_id` and `span_id` onto the log
records emitted in the same breath, and attach a sampled exemplar — a pointer
back to a representative trace — onto a metric. That is what turns "error rate is
up" into "click here for the trace, and here are its logs."

The hard part, and the part most material skips, is keeping that context alive
across a boundary that is not a function call. When the order service publishes
`order.placed` to Kafka, the shipping and notification consumers run in different
processes with no shared call stack. Unless the trace context travels *with the
message*, each consumer starts a brand-new trace and the chain breaks in the middle. Carrying it across that hop
is the job of the custom-instrumentation chapter; for now, hold onto the idea
that a single `trace_id` flowing through every hop is the foundation everything
else is built on.

## What you learned

- Traces, metrics, and logs answer *where*, *how much*, and *what exactly* — and
  are worth far more together than apart.
- OpenTelemetry splits producing telemetry (the SDK) from shipping it (OTLP to
  the Collector), and the Collector's receivers, processors, and exporters are
  where routing and sampling decisions live.
- A shared `trace_id`, propagated across every hop, is what makes cross-signal
  correlation possible — and async boundaries like Kafka are where it is easy to
  lose.

The next chapter introduces the service we will make observable, and walks its
code closely enough that you could write it yourself.

---

*Verification status: <span class="status status--unverified">unverified</span>.
The concepts are stable; the specific exporter/endpoint wiring shown is
confirmed against the stack's Collector config in the demo chapters.*

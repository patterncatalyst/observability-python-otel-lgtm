---
title: "Metrics: the aggregate view"
order: 5
part: "The three signals"
description: "The same SDK emits RED metrics — rate, errors, duration — and exemplars stitch a point on a latency graph to the exact trace behind it."
duration: 14 minutes
---

Traces answer "what happened in this one request?" Metrics answer "what is
happening across all of them?" — and you need both, because you cannot keep a
trace for every request forever, but you can keep cheap aggregate counters and
histograms indefinitely. This chapter turns on metrics for the mesh and, more
importantly, shows how a metric links back to a trace through **exemplars**, so
the aggregate view and the single-request view are one click apart.

The code is in `examples/03-metrics/`; the metric pipeline lives in the same
`obs.otel.setup()` you already met.

## RED, and where the numbers come from

The useful default for a request-driven service is the RED method: **R**ate (how
many requests per second), **E**rrors (how many are failing), and **D**uration
(how long they take, as a distribution). Between them they answer "is it busy, is
it broken, is it slow?" — the three questions an on-call engineer asks first.

You get most of RED without writing any metric code, because the same
auto-instrumentation that produced spans also produces metrics. The HTTP and gRPC
instrumentors emit request counts and server-duration histograms, labelled by
route, method, and status code. Rate is the derivative of the count; errors are
the count filtered to 5xx (or gRPC non-OK); duration is the histogram. The order
service's `POST /orders` latency and throughput are already being recorded.

## How the code works

**The meter provider — already built.** In `obs.otel.setup`, metrics are wired
beside traces:

```python
reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=f"{cfg.endpoint}/v1/metrics")
)
meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
metrics.set_meter_provider(meter_provider)
```

The reader is *periodic*: metrics are not pushed per event like spans, they are
read from in-memory aggregations on a fixed interval and exported in a batch.
That is the fundamental difference between a metric and a span — a span is one
event, a metric is a running aggregate the SDK keeps and samples. The same
`Resource` is attached, so a metric carries the same `service.name` as the spans
from that service and they line up in Grafana.

**A custom metric, when the auto ones are not enough.** The auto metrics cover
transport-level RED, but domain questions — "how many orders were declined for
payment?" — need a counter you define. `obs.otel.meter()` returns the configured
meter; a service creates an instrument once and records to it:

```python
declines = otel.meter().create_counter("orders.payment_declined")
# ... when payment returns not-authorized:
declines.add(1, {"reason": auth.decline_reason})
```

A `Counter` is the right instrument because the value only ever goes up and you
care about the rate of increase; the attribute (`reason`) becomes a label you can
group by. (The repo keeps the application code lean and leans on the auto
metrics; this is the shape to reach for when you add a business metric.)

**Exemplars — the link back to a trace.** An exemplar is a sample trace id the
SDK attaches to a metric data point when that measurement was recorded inside an
active span. Because our duration histogram is recorded while the request span is
current, each bucket can carry an example `trace_id`. Grafana renders these as
dots on the latency graph; clicking one opens that trace in Tempo. This is the
payoff of emitting both signals from one SDK with one resource: "p99 spiked at
14:32" stops being a dead end and becomes "here is a request that was actually
slow."

## Build, run, observe

```bash
cd examples/03-metrics && ./demo.sh
```

The script drives load at the REST edge (with `hey` if installed, or a curl
burst otherwise). In Grafana > Explore, query the order service's request rate
and duration; some of the load deliberately trips the payment ceiling so the
error line is non-zero. Turn on exemplars on the latency panel and follow a dot
into its trace.

## Cross-check

The numbers should agree across signals. Pick a one-minute window: the request
count the metric reports for `POST /orders` should match the number of order
traces in Tempo for the same window, and the error-rate line should match the
share of those traces marked error. When the aggregate and the individual views
disagree, one of them is misconfigured — agreement is a cheap correctness check
you can run any time.

## What you learned

- RED — rate, errors, duration — is the default question set, and the HTTP/gRPC
  auto-instrumentation emits most of it for free.
- Metrics are periodic aggregates, not per-event records; the `MeterProvider`
  and a `PeriodicExportingMetricReader` own that pipeline.
- A custom `Counter` covers domain questions the transport metrics cannot, and
  **exemplars** link a metric data point straight to a representative trace.

Next, *Logs* adds the third signal and stamps every line with the `trace_id`, so
a log and its trace find each other.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm RED metrics for the order service appear in Mimir, the
error line tracks the payment-declined load, and exemplars resolve to real
traces. The exact metric instrument names are illustrative until confirmed.*

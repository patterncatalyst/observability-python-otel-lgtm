---
title: "Auto-instrumentation: traces for free"
order: 4
part: "The three signals"
description: "One setup() call turns on FastAPI, gRPC, and asyncpg instrumentation, and a single order becomes one trace across the synchronous hops — then breaks at Kafka."
duration: 16 minutes
---

In the last chapter the services ran with telemetry off and Grafana was empty. Here
we change exactly one thing — switch the SDK on — and a single `POST /orders`
turns into one connected trace across the order service, both gRPC dependencies,
and every Postgres query, without adding a line of tracing to any handler. The
new idea is **auto-instrumentation**: libraries instrument themselves once you
ask them to, and context propagates across HTTP and gRPC for free. The chapter
ends by showing the one boundary that ride does *not* cross.

The code is in `examples/02-auto-instrumentation/` and the shared `obs` library
under `services/common/`. The run script builds the stack, places an order, and
points you at the trace.

{% include excalidraw.html file="fig-04-instrumentation-layers" alt="Three layers: application code at the top with no telemetry calls; an auto-instrumentation layer wrapping FastAPI, gRPC, and asyncpg; and the OpenTelemetry SDK below exporting OTLP to the Collector." caption="Figure 4.1 — Auto-instrumentation sits between your code and the libraries it already uses" %}

## What "auto" actually means

There are two ways to turn on auto-instrumentation, and it is worth knowing both.
The zero-code way is the `opentelemetry-instrument` launcher: you run
`opentelemetry-instrument python -m yourapp` and it monkey-patches supported
libraries at import time, reading configuration entirely from `OTEL_*`
environment variables. Nothing in your source changes at all.

The programmatic way — the one this repo uses — calls the same instrumentors from
code at startup. We prefer it here because it keeps the configuration visible in
one reviewable place (`obs.otel.setup`) and lets a service instrument its own app
object, which FastAPI needs. Either way, the *application* code stays free of
tracing calls; the difference is only where the "turn it on" lives.

What both share is the mechanism that makes a trace cross a process boundary:
**context propagation**. The instrumented HTTP client and gRPC client write the
active span's identity into a `traceparent` header (the W3C Trace Context
standard); the instrumented server on the other side reads it and makes its work
a child of that span. That is why a trace can start in the order service and
continue inside inventory, in a different process, with nobody writing
propagation code.

## How the code works

The whole mechanism is in `services/common/obs/otel.py`. Walk `setup()` top to
bottom.

**The resource — who is emitting this.** Every span, metric, and log is tagged
with a `Resource`, built from three attributes:

```python
resource = Resource.create({
    "service.name": cfg.service_name,
    "service.version": cfg.service_version,
    "deployment.environment": cfg.environment,
})
```

`service.name` is the single most important attribute in the whole system: it is
what makes Grafana able to say "this span happened in `payment`, that one in
`order`." Without it every span is anonymous. We pass it explicitly
(`otel.setup("order")`) so it is never left to a guessed default.

**The three providers — one per signal.** A provider is the SDK object that owns
a signal and knows how to export it. Traces get a `TracerProvider` with a
`BatchSpanProcessor` wrapping an OTLP/HTTP span exporter; metrics get a
`MeterProvider` with a `PeriodicExportingMetricReader`; logs get a
`LoggerProvider` with a batching processor. Each exporter points at the same
Collector base URL, and the SDK appends the signal-specific path
(`/v1/traces`, `/v1/metrics`, `/v1/logs`):

```python
tracer_provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{cfg.endpoint}/v1/traces"))
)
```

The *Batch* processor matters: it buffers spans and ships them in the background
on their own thread, so exporting telemetry never sits on your request's critical
path. If it were a simple processor, every span would flush synchronously and you
would have made the service slower by observing it.

**The propagator.** Setting the global propagator to W3C Trace Context is what
lets the injected `traceparent` be understood on both ends. The SDK defaults to
this, and the instrumentors use whatever is set globally — so all the gRPC and
HTTP hops agree on the same header format.

**Turning the libraries on.** `_enable_auto_instrumentation()` calls the
instrumentors for the synchronous hops:

```python
AsyncPGInstrumentor().instrument()
GrpcAioInstrumentorClient().instrument()
GrpcAioInstrumentorServer().instrument()
```

Each `instrument()` call patches its library process-wide: every asyncpg query
now opens a span, every gRPC client call injects context and every gRPC server
call extracts it. FastAPI is the exception — it instruments a specific app
object, so services call `otel.instrument_fastapi(app)` once the app exists. The
imports are wrapped in `try/except` so a service that does not use a given
library (notification has no database) still starts cleanly.

**The off switch.** The first thing `setup()` checks is `OTEL_SDK_DISABLED`. When
it is true — the baseline demo — `setup()` returns immediately with no-op
tracer/meter, which is exactly how Chapter 3 produced a working but invisible
system. One environment variable is the whole difference between Demo 1 and Demo
2 running the same code.

## Build, run, observe

```bash
cd examples/02-auto-instrumentation && ./demo.sh
```

Place an order, open Grafana > Explore > Tempo, and open the newest trace. You
will see a single tree: the `POST /orders` server span, child client spans for
the inventory and payment gRPC calls, server spans inside those services, and
asyncpg spans for each query — all correlated, none of it written by hand.

## The boundary where it stops

Look for the shipping and notification work and you will not find it under that
trace. The demo runs with `PROPAGATE_KAFKA_CONTEXT=false`, and the consumer spans
show up as their own separate, parentless traces. Auto-instrumentation propagated
context across HTTP and gRPC because those protocols have a natural header slot
and the instrumented client filled it in. A Kafka message has no one filling in a
`traceparent` for you, so the chain breaks at the broker. Closing that gap is
custom work — the subject of Chapter 7.

## What you learned

- `obs.otel.setup()` builds a resource, three signal providers with OTLP/HTTP
  exporters, and a W3C propagator — the standard SDK bootstrap.
- Auto-instrumentation (programmatic here, or the `opentelemetry-instrument`
  launcher) traces FastAPI, gRPC, and asyncpg with no application code.
- Context crosses HTTP and gRPC via the `traceparent` header automatically; it
  does **not** cross Kafka, which is where the next signals and Chapter 7 come in.

Next, *Metrics* adds the aggregate view — rates, errors, and latency — and links a
slow point on a graph back to the exact trace behind it.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm one trace spans order -> inventory/payment gRPC ->
Postgres in Tempo, the resource carries the right `service.name` per service, and
that with propagation off the consumer spans form separate traces. Exact OTel
instrumentation package versions are pinned but unverified against a 3.14 runtime.*

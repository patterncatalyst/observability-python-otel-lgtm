---
title: "Continuous profiling: the fourth signal"
order: 11
part: "The pipeline"
description: "Traces localise a slow span; profiling shows which functions inside it burned the CPU. The newest signal, bundled in the same stack — and the least settled on the Python side."
duration: 12 minutes
---

The correlated view from Part 2's predecessor can take you to a single slow span:
`Authorize` took 820 ms on the payment service, on this one trace. The question it
cannot answer is *where* — which function inside that service spent the 820 ms.
Traces, metrics, and logs all stop at the boundary of the process; none of them
sees the call stack. Continuous profiling is the signal that does, and Grafana now
calls it the fourth pillar alongside the other three. This chapter is the honest
state of it: the backend is already in the box, and the Python client side is the
newest, least-settled part of the whole stack.

{% include excalidraw.html file="fig-12-profiling" alt="A slow Authorize span in Tempo links by service and time window to a CPU flame graph in Pyroscope, where nested frames show serve → Authorize → serialize (55%) and db.execute (30%); the profile reveals which functions inside the slow span spent the CPU." caption="Figure 11.1 — The trace says which span was slow; the profile says which functions inside it spent the CPU" %}

## What profiling adds

A profiler samples the call stack of a running process many times a second and
aggregates the samples into a flame graph: the wider a frame, the more CPU time
(or allocated memory) was spent in that function and everything it called.
*Continuous* profiling does this always, in production, at an overhead low enough
to leave on — typically a couple of percent — rather than the heavyweight,
attach-when-it's-already-broken profilers you may have reached for before.

The reason it belongs next to traces is the join. A trace tells you a span was
slow; the profile for that service over that span's time window tells you the
slow span's CPU went 55% into `serialize_money` and 30% into a database call. The
trace localises *which* work was slow across services; the profile localises
*what* was slow inside one. That pairing — span to flame graph — is the payoff,
and it is why the diagram links the two by service plus time window rather than by
a shared id.

## The backend is already here

The good news for this stack: the `grafana/otel-lgtm` image bundles Grafana
Pyroscope as the profiles store, with a Collector profiles pipeline feeding it —
the same shape as traces, metrics, and logs. You do not stand up a new backend;
profiles ride the OTLP path you already run.

Two caveats specific to this repo, both real:

- **The pinned image may predate it.** This stack pins `grafana/otel-lgtm:0.8.1`;
  Pyroscope was added to the image over its 0.x life and recent tags are 0.11+.
  Confirm your tag includes Pyroscope, and bump the pin if not. This is tracked as
  an open item in `_plans/reconciliation-plan.md`.
- **Our Collector config overrides the image's.** Because the stack mounts its own
  `otelcol/config.yaml` over the image default, it replaces the bundled pipelines —
  including the profiles one. Enabling profiling means adding a profiles pipeline
  back to the mounted config:

  ```yaml
  # in stack/otelcol/config.yaml
  exporters:
    otlphttp/pyroscope:
      endpoint: http://localhost:4040
      tls: { insecure: true }
  service:
    pipelines:
      profiles:
        receivers: [otlp]
        exporters: [otlphttp/pyroscope]
  ```

  Receiving OTLP profiles needs the Collector's `service.profilesSupport` feature
  gate, which the contrib build in the image carries.

## The Python side is the unsettled part

Where logs, metrics, and traces have stable SDKs, profiling does not yet. There
are two routes, and the chapter is deliberate about which is which:

- **The OpenTelemetry profiling signal (OTLP profiles)** is the standards-track
  answer, but it is experimental — the spec is young and the Python SDK support is
  nascent. It is the right long-term path and the wrong thing to pin a talk on.
- **The Grafana Pyroscope SDK** (`pyroscope-io`) is the pragmatic path today: it
  samples in-process and pushes to Pyroscope. `obs/profiling.py` wires it as an
  optional hook, gated on an env var and guarded by a soft import so a service
  without the dependency still starts:

  ```python
  def setup_profiling(service_name: str) -> None:
      addr = os.getenv("PYROSCOPE_ADDRESS")
      if not addr:
          return
      try:
          import pyroscope
      except ImportError:
          return
      pyroscope.configure(application_name=service_name, server_address=addr,
                          tags={"service_name": service_name})
  ```

  There is also an **OpenTelemetry eBPF profiler** that needs no in-process SDK,
  but its own docs warn of breaking changes and call it development-and-test only,
  so it stays a footnote here.

The span-to-profile link is the last piece, configured on Grafana's Tempo
datasource as `tracesToProfiles`, pointing at a Pyroscope datasource and matching
on `service_name` over the span's time range — the same correlation pattern as
trace-to-logs, one signal over.

## Build, run, observe

```bash
cd examples/09-profiling && ./demo.sh
```

With profiling enabled and the pipeline in place, drive load, open a slow
`/orders` trace in Tempo, and use *Profiles for this span* to land in the flame
graph for that service and window. Read down from the widest frame to the hotspot.

## What you learned

- Profiling is the fourth signal: where CPU and memory go *inside* a process,
  sampled continuously at low overhead — the view traces, metrics, and logs cannot
  give because they stop at the process boundary.
- The backend ships in the same `otel-lgtm` image; profiles ride the OTLP path,
  provided the mounted Collector config carries a profiles pipeline.
- The Python client side is the least settled: prefer the Pyroscope SDK today,
  watch the OTLP profiles signal for the standards-track future.

That closes the arc: one request, instrumented for free, deepened by hand where it
matters, sampled sanely at the pipeline, and now legible all the way down to the
function that spent the time — across four signals joined by one trace.

---

*Verification status: <span class="status status--unverified">unverified</span>,
and more so than any other chapter. A real run must confirm the pinned image
includes Pyroscope (or bump it), that the added profiles pipeline is accepted by
the image's Collector build, that the Pyroscope Python SDK version configures and
pushes as shown, and that Grafana's `tracesToProfiles` links a span to its flame
graph. Treat the profiling path as a sketch to validate, not a settled recipe.*

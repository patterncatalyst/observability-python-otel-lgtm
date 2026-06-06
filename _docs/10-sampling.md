---
title: "Sampling: keeping what matters"
order: 10
part: "The pipeline"
description: "At volume you cannot keep every trace. Decide what survives in the Collector, after the trace is complete — keep the errors, the slow ones, and the routes that matter, and sample the rest."
duration: 14 minutes
---

The three signals are wired and correlated. The problem the last part leaves you
with is cost: a trace is the expensive signal, and at real traffic you cannot
afford to store all of them. This chapter is about deciding what to keep — and,
just as importantly, *where* that decision is made. The answer this stack uses is
the OpenTelemetry Collector, after the fact, which is what lets you keep the
traces you will actually want without keeping the ones you never will.

{% include excalidraw.html file="fig-09-sampling-location" alt="Head sampling decides at the SDK before a trace exists (cheap but blind); tail sampling sends all spans to the Collector, which buffers the whole trace and then keeps errors, slow, and critical routes while dropping most healthy traffic (costs RAM, keeps what matters)." caption="Figure 10.1 — Head sampling is cheap and blind; tail sampling costs memory and keeps what matters" %}

## Head versus tail

There are two places to drop a trace, and the difference is everything.

**Head sampling** decides at the start, in the SDK, before the request has run.
It is cheap — you never pay to build, export, or store the spans you drop — but it
is blind: at the moment you decide, you do not yet know whether this request will
error, time out, or sail through in two milliseconds. A head sampler keeping 5%
keeps 5% of your errors too, which is exactly backwards from what you want.

**Tail sampling** decides at the end, in the Collector, once every span of the
trace has arrived. Now the decision can be informed: keep it *because* it errored,
*because* it was slow, *because* it hit a route you care about. The cost is that
the Collector must hold each in-progress trace in memory until it is sure the
trace is complete, then apply the rules. You pay in Collector RAM for the
intelligence head sampling cannot have. For most teams that trade is worth it,
and it is the one this stack makes.

This is why the SDK in `obs.otel.setup` installs no sampler: every service exports
100% of its spans. The application is deliberately not in the sampling business —
it emits everything, and the Collector decides what survives. That separation is
the point: you can change the whole sampling policy without redeploying a single
service.

## How the config works

The tail-sampling policy lives in `stack/otelcol/config.tail-sampling.yaml`, in a
`tail_sampling` processor on the traces pipeline:

```yaml
tail_sampling:
  decision_wait: 30s
  num_traces: 50000
  policies:
    - { name: errors-policy, type: status_code, status_code: { status_codes: [ERROR] } }
    - { name: slow-policy,    type: latency,     latency: { threshold_ms: 1000 } }
    - { name: critical-routes, type: string_attribute,
        string_attribute: { key: http.target, values: [/orders] } }
    - { name: probabilistic-baseline, type: probabilistic,
        probabilistic: { sampling_percentage: 5 } }
```

Read the knobs as the cost dials they are. `decision_wait: 30s` is how long the
Collector holds a trace waiting for trailing spans before it decides — long enough
that a slow request completes, short enough that memory turns over. `num_traces:
50000` caps how many traces are buffered at once; past it, new traces are dropped
rather than letting the Collector run out of memory. The policies are evaluated as
an OR: a trace is kept if it matches *any* of them, so every error is kept, every
request over a second is kept, every `/orders` call is kept, and of everything
left, a 5% baseline is kept so the healthy path is not invisible. The
`memory_limiter` ahead of it is raised to 1024 MiB precisely because buffering
costs more than the pass-through base config does.

The pipeline wiring puts the processor in the traces path only:

```yaml
traces:
  receivers: [otlp]
  processors: [memory_limiter, resource, tail_sampling, batch]
  exporters: [otlphttp/tempo]
```

Metrics and logs have no sampler — sampling is a trace concern, because metrics
are already aggregates and logs are correlated to the traces you kept.

## Build, run, observe

The base stack runs the pass-through `config.yaml`. To switch on tail sampling,
point the `lgtm` service at the sampling config and restart it:

```bash
# in stack/compose.yaml, swap the mounted Collector config:
#   - ./otelcol/config.tail-sampling.yaml:/otel-lgtm/otelcol-config.yaml:Z
podman compose up -d --force-recreate lgtm
cd examples/08-sampling && ./demo.sh
```

The demo drives a mix — healthy orders, a few declines (errors), and a slow
request or two — then you look in Tempo. Every error trace and every `/orders`
trace is present; the bulk of the healthy GET traffic is gone, kept only at the
5% baseline. Watch the Collector's memory while `hey` runs: it rises with
in-flight traces and settles as `decision_wait` windows close. That curve is the
cost you are paying for the intelligence.

## Cross-check

Drive load, then confirm three things in Tempo: an error you caused is always
findable; a `/orders` trace is always findable; and the count of healthy,
non-critical traces is roughly 5% of what you sent. If errors are missing, the
status-code policy is not seeing your spans' error status; if memory climbs
without bound, `num_traces` or `decision_wait` is too high for your traffic.

## What you learned

- Head sampling is cheap and blind; tail sampling costs Collector memory and buys
  the ability to keep a trace *because* of how it turned out.
- The services export 100% and own no sampling policy, so what you keep is a
  Collector config change, not a redeploy.
- Keep errors, slow, and critical routes unconditionally; sample the healthy
  remainder. The cost is RAM proportional to in-flight traces times `decision_wait`.

Next, *Continuous profiling* adds the fourth signal — where CPU and memory go
inside a service — and links a flame graph back to the span that paid for it.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm the `tail_sampling` policies behave as described against
the contrib Collector in the otel-lgtm image, that error status survives the
gRPC/HTTP→OTLP path so the status-code policy fires, and that `/orders` arrives as
`http.target` (newer HTTP semconv may name it `url.path` — adjust the policy key
if so).*

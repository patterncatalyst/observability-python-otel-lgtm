# Demo 9 — continuous profiling (the fourth signal)

Where the CPU goes *inside* a slow span. Profiles ride the same stack via the
bundled Pyroscope; the span→flame-graph link is Grafana's `tracesToProfiles`.

**This is the least-settled signal.** It is a sketch to validate, not a settled
recipe. Enabling it takes three steps (see `demo.sh` header): a Pyroscope-bundling
`otel-lgtm` tag, a `profiles` pipeline in the Collector config, and the
`pyroscope-io` package so `obs.profiling` can push. The OpenTelemetry profiling
signal (OTLP profiles) is the standards-track future but still experimental.

```bash
./demo.sh
```

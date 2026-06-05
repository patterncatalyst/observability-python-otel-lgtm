# Demo 3 — metrics (RED + exemplars)

With telemetry on, drive a few hundred orders and watch the rate/error/duration
metrics the SDK emits. Exemplars tie a point on the latency histogram to a real
trace, so "why was p99 slow at 14:32?" is one click, not a query-writing
exercise.

```bash
./demo.sh
```

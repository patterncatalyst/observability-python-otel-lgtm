# Demo 7 — the correlated view

Drive a realistic mix of traffic — mostly successful orders plus a few that trip
the payment ceiling — then follow one request across all three signals in Grafana:
read the trace as a business flow, pivot from a span to its logs, and from a
latency exemplar back to a trace. The serialization cost between services is
readable straight off the gRPC client/server span pair.

```bash
./demo.sh
```

Everything pivots on one `trace_id` flowing through every hop. The chapter walks
the four moves step by step.

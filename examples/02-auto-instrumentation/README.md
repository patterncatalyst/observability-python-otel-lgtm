# Demo 2 — auto-instrumentation (traces for free)

Same code as Demo 1, SDK on. One `obs.otel.setup()` call turns on
auto-instrumentation for FastAPI, gRPC, and asyncpg, so a single order request
becomes one trace across REST -> gRPC (inventory) -> gRPC (payment) -> Postgres,
with zero tracing code in the handlers.

```bash
./demo.sh
```

This demo intentionally leaves `PROPAGATE_KAFKA_CONTEXT=false`, so the Kafka hop
breaks the trace — shipping and notification appear as disconnected traces. That
sets up Demo 5, where one helper carries the context across the message boundary.

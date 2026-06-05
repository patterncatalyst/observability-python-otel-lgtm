# Demo 1 — the services, no telemetry

Bring the six example services up with the OpenTelemetry SDK disabled
(`OTEL_SDK_DISABLED=true`) and place an order. It works: stock is reserved,
payment authorized, the order persisted, the `order.placed` event published, and
shipping and notification react. But Grafana is empty — you have no idea any of
that happened, how long it took, or where it would fail under load.

```bash
./demo.sh
```

This is the starting point. Every later demo adds one layer of visibility on top
of this exact same code.

# Demo 5 — custom spans across the Kafka hop

The climax. Auto-instrumentation got us one trace across the synchronous hops in
Demo 2, but the trace broke at Kafka. Here `PROPAGATE_KAFKA_CONTEXT=true` turns on
the two-line bridge: the order service injects the active trace context into the
message headers, and the shipping and notification consumers extract it and open
their processing spans with it as the parent.

```bash
./demo.sh
```

Result: a single trace from the REST call all the way through the asynchronous
consumers — exactly what you could not see in Demo 1.

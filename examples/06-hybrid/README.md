# Demo 6 — auto, custom, and hybrid

The same system, fully instrumented, so one trace shows both layers at once: the
breadth auto-instrumentation gives for free (HTTP, gRPC, Postgres spans) and the
depth the custom spans add where auto is blind (the Kafka continuation, the
GraphQL resolver tree).

```bash
./demo.sh
```

Hold this trace next to Demo 2's (auto only): the gap between them — the rejoined
consumers and the opened-up resolvers — is exactly what the hybrid layer buys, and
the chapter walks through what each layer costs.

# Demo 8 — tail sampling

Keep the traces you will want (errors, slow requests, `/orders`) and sample the
healthy remainder, deciding in the Collector after each trace completes. Requires
the tail-sampling config mounted in place of the base one (the chapter shows the
one-line swap).

```bash
./demo.sh
```

The services export 100%; the policy is entirely in `stack/otelcol/config.tail-sampling.yaml`,
so changing what you keep never touches application code.

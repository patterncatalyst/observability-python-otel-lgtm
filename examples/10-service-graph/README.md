# Example 10 — the live service graph

The operational view: the service topology with live request, error, and latency
on every edge, built from the traces by Tempo's metrics-generator — no service
mesh, no sidecars, no Kubernetes.

```bash
./demo.sh
```

Requires Tempo's metrics-generator enabled (`service-graphs` + `span-metrics`,
remote-writing to the bundled store); the Grafana service map is already
provisioned. See `_docs/12-service-graph.md` for the one-time enablement.

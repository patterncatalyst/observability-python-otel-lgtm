# Diagram catalogue

One spec, two consumers. `scripts/diagrams.py` emits each figure as a themed
`<name>.svg` (embedded in the chapters) and a matching `<name>.excalidraw`
(editable source). `scripts/render_pngs.sh` rasterises the same SVGs to
`deck/png/<name>.png` for the slide deck, so the book and the deck share one set.

Regenerate everything:

```bash
python3 scripts/diagrams.py     # SVG + .excalidraw  → assets/diagrams/
scripts/render_pngs.sh          # PNG                → deck/png/
```

| File | Figure | Used by |
|---|---|---|
| `fig-02-otel-data-path` | 2.1 — One SDK, one Collector, three backends | Fundamentals chapter; deck §2 |
| `fig-03-app-topology` | 3.1 — The async round trip | The demo app chapter; deck §3 |
| `fig-04-instrumentation-layers` | 4.1 — Auto vs. custom vs. hybrid | Hybrid chapter (r2.0); deck |
| `fig-07-context-propagation` | 7.1 — traceparent across the Kafka hop | Custom spans chapter (r1.0); deck |
| `fig-09-sampling-location` | 9.1 — Head vs. tail decision point | Sampling chapter (r2.0); deck |
| `fig-11-correlation-graph` | 11.1 — trace_id + exemplars | Correlated-view chapter (r2.0); deck |

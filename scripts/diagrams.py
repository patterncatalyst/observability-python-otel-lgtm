#!/usr/bin/env python3
"""Shared diagram set for the talk + the site.

One spec per PRD figure. Each emit() writes a themed <name>.svg (embedded in the
Jekyll chapters) and a matching <name>.excalidraw (editable source) into
assets/diagrams/. The same SVGs are rasterised to PNG for the slide deck by
scripts/render_pngs.sh, so the book and the deck share one set of figures.

Run:  python3 scripts/diagrams.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
import generate_diagram as g

g.OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "diagrams")


# ── Fig 2.1 — The three signals and the OTel data path ──────────────────────
def fig_02_otel_data_path():
    g.emit("fig-02-otel-data-path", 900, 360,
        bands=[
            {"x": 250, "y": 70, "w": 220, "h": 250, "label": "OTel Collector", "fill": "#f7f7f7"},
            {"x": 520, "y": 70, "w": 170, "h": 250, "label": "LGTM backends", "fill": "#fafafa"},
        ],
        nodes=[
            {"x": 30,  "y": 150, "w": 180, "h": 90, "style": "accent",
             "lines": ["Python service", "OTel SDK", "traces · metrics · logs"]},
            {"x": 265, "y": 100, "w": 190, "h": 50, "style": "sub",
             "lines": ["receivers", "OTLP/HTTP :4318"]},
            {"x": 265, "y": 165, "w": 190, "h": 50, "style": "sub",
             "lines": ["processors", "memory_limiter · batch"]},
            {"x": 265, "y": 230, "w": 190, "h": 50, "style": "sub",
             "lines": ["exporters", "route per signal"]},
            {"x": 535, "y": 100, "w": 140, "h": 48, "style": "box", "lines": ["Tempo", "traces"]},
            {"x": 535, "y": 168, "w": 140, "h": 48, "style": "box", "lines": ["Mimir", "metrics"]},
            {"x": 535, "y": 236, "w": 140, "h": 48, "style": "box", "lines": ["Loki", "logs"]},
            {"x": 740, "y": 150, "w": 140, "h": 90, "style": "ink",
             "lines": ["Grafana", "one correlated UI"]},
        ],
        edges=[
            {"x1": 210, "y1": 195, "x2": 265, "y2": 190, "label": "OTLP", "amber": True},
            {"x1": 455, "y1": 124, "x2": 535, "y2": 124},
            {"x1": 455, "y1": 192, "x2": 535, "y2": 192},
            {"x1": 455, "y1": 255, "x2": 535, "y2": 260},
            {"x1": 675, "y1": 124, "x2": 740, "y2": 175},
            {"x1": 675, "y1": 192, "x2": 740, "y2": 195},
            {"x1": 675, "y1": 260, "x2": 740, "y2": 215},
        ],
        notes=[{"x": 450, "y": 40, "text": "One SDK emits all three signals; the Collector decides what survives; Grafana ties them back together.",
                "anchor": "middle", "size": 12}])


# ── Fig 3.1 — Demo app topology and the async round trip ────────────────────
def fig_03_service_topology():
    g.emit("fig-03-service-topology", 960, 440,
        bands=[
            {"x": 170, "y": 50, "w": 770, "h": 240, "label": "compose network", "fill": "#f7f7f7"},
            {"x": 170, "y": 330, "w": 770, "h": 80, "label": "Postgres · meshdb", "fill": "#fdecec"},
        ],
        nodes=[
            {"x": 20,  "y": 150, "w": 130, "h": 70, "style": "sub", "lines": ["Client", "curl / Postman"]},
            {"x": 190, "y": 150, "w": 150, "h": 70, "style": "accent", "lines": ["order", "REST :8080"]},
            {"x": 410, "y": 80,  "w": 150, "h": 60, "style": "box", "lines": ["inventory", "gRPC :50051"]},
            {"x": 410, "y": 170, "w": 150, "h": 60, "style": "box", "lines": ["payment", "gRPC :50052"]},
            {"x": 620, "y": 150, "w": 150, "h": 70, "style": "box", "lines": ["Kafka", "order.placed"]},
            {"x": 800, "y": 90,  "w": 140, "h": 56, "style": "box", "lines": ["shipping", "consumer"]},
            {"x": 800, "y": 184, "w": 140, "h": 56, "style": "box", "lines": ["notification", "consumer"]},
            {"x": 20,  "y": 340, "w": 150, "h": 60, "style": "accent", "lines": ["review", "GraphQL :8081"]},
        ],
        edges=[
            {"x1": 150, "y1": 185, "x2": 190, "y2": 185, "label": "POST /orders", "amber": True},
            {"x1": 340, "y1": 175, "x2": 410, "y2": 110, "label": "Reserve"},
            {"x1": 340, "y1": 190, "x2": 410, "y2": 200, "label": "Authorize", "ly": 10},
            {"x1": 560, "y1": 185, "x2": 620, "y2": 185, "label": "publish", "amber": True},
            {"x1": 770, "y1": 175, "x2": 800, "y2": 118, "label": "consume"},
            {"x1": 770, "y1": 195, "x2": 800, "y2": 210, "label": "consume", "ly": 12},
            {"x1": 95,  "y1": 220, "x2": 95,  "y2": 340, "label": "GraphQL", "amber": True, "lx": -34},
            # data-store connections (thin/dashed down into the Postgres band)
            {"x1": 265, "y1": 220, "x2": 265, "y2": 330, "dashed": True},
            {"x1": 485, "y1": 230, "x2": 485, "y2": 330, "dashed": True},
            {"x1": 700, "y1": 220, "x2": 700, "y2": 330, "dashed": True, "lx": 700},
            {"x1": 870, "y1": 240, "x2": 870, "y2": 330, "dashed": True},
            {"x1": 95,  "y1": 400, "x2": 170, "y2": 370, "dashed": True},
        ],
        notes=[{"x": 450, "y": 36, "text": "One POST /orders crosses REST, two gRPC calls, Kafka, and Postgres; review serves a GraphQL read path. The trace must follow all of it.",
                "anchor": "middle", "size": 12}])


# ── Fig 4.1 — Instrumentation layering: auto vs custom vs hybrid ─────────────
def fig_04_instrumentation_layers():
    g.emit("fig-04-instrumentation-layers", 900, 340,
        nodes=[
            {"x": 30,  "y": 90, "w": 250, "h": 180, "style": "box",
             "lines": ["Auto", "opentelemetry-instrument", "framework + library spans", "zero code change"]},
            {"x": 325, "y": 90, "w": 250, "h": 180, "style": "box",
             "lines": ["Custom", "manual API", "your business spans", "attributes you choose"]},
            {"x": 620, "y": 90, "w": 250, "h": 180, "style": "accent",
             "lines": ["Hybrid", "auto + custom together", "real-world default", "mind the duplicate span"]},
        ],
        edges=[
            {"x1": 280, "y1": 180, "x2": 325, "y2": 180},
            {"x1": 575, "y1": 180, "x2": 620, "y2": 180, "amber": True},
        ],
        notes=[
            {"x": 155, "y": 60, "text": "breadth, for free", "anchor": "middle", "size": 12},
            {"x": 450, "y": 60, "text": "depth, where it matters", "anchor": "middle", "size": 12},
            {"x": 745, "y": 60, "text": "both", "anchor": "middle", "size": 12, "bold": True},
        ])


# ── Fig 7.1 — Context propagation across the async (Kafka) boundary ─────────
def fig_07_context_propagation():
    g.emit("fig-07-context-propagation", 900, 360,
        bands=[
            {"x": 20, "y": 250, "w": 860, "h": 90, "label": "one trace_id, every hop", "fill": "#fdecec"},
        ],
        nodes=[
            {"x": 30,  "y": 80, "w": 150, "h": 70, "style": "accent", "lines": ["FastAPI", "root span"]},
            {"x": 240, "y": 80, "w": 170, "h": 70, "style": "box", "lines": ["Kafka message", "headers carry", "traceparent"]},
            {"x": 470, "y": 80, "w": 150, "h": 70, "style": "accent", "lines": ["Consumer", "child span"]},
            {"x": 700, "y": 80, "w": 150, "h": 70, "style": "box", "lines": ["Postgres", "child span"]},
            {"x": 105, "y": 270, "w": 120, "h": 50, "style": "sub", "lines": ["span A"]},
            {"x": 290, "y": 270, "w": 120, "h": 50, "style": "ghost", "lines": ["inject ctx"]},
            {"x": 475, "y": 270, "w": 120, "h": 50, "style": "sub", "lines": ["span B"]},
            {"x": 700, "y": 270, "w": 120, "h": 50, "style": "sub", "lines": ["span C"]},
        ],
        edges=[
            {"x1": 180, "y1": 115, "x2": 240, "y2": 115, "label": "inject", "amber": True},
            {"x1": 410, "y1": 115, "x2": 470, "y2": 115, "label": "extract", "amber": True},
            {"x1": 620, "y1": 115, "x2": 700, "y2": 115, "label": "child of B"},
            {"x1": 165, "y1": 150, "x2": 165, "y2": 270, "dashed": True},
            {"x1": 350, "y1": 150, "x2": 350, "y2": 270, "dashed": True},
            {"x1": 535, "y1": 150, "x2": 535, "y2": 270, "dashed": True},
            {"x1": 760, "y1": 150, "x2": 760, "y2": 270, "dashed": True},
        ],
        notes=[{"x": 450, "y": 50, "text": "traceparent rides in the Kafka message headers, so the work after the hop joins the originating trace.",
                "anchor": "middle", "size": 12}])


# ── Fig 9.1 — Where the sampling decision is made (head vs tail) ─────────────
def fig_09_sampling_location():
    g.emit("fig-09-sampling-location", 900, 360,
        bands=[
            {"x": 20,  "y": 70, "w": 250, "h": 250, "label": "head sampling", "fill": "#fafafa"},
            {"x": 470, "y": 70, "w": 410, "h": 250, "label": "tail sampling", "fill": "#fdecec"},
        ],
        nodes=[
            {"x": 50,  "y": 120, "w": 190, "h": 70, "style": "accent", "lines": ["SDK", "decides up front"]},
            {"x": 50,  "y": 220, "w": 190, "h": 70, "style": "ghost", "lines": ["dropped before", "the trace exists"]},
            {"x": 300, "y": 150, "w": 130, "h": 60, "style": "sub", "lines": ["all spans", "sent"]},
            {"x": 500, "y": 150, "w": 170, "h": 70, "style": "box", "lines": ["Collector", "buffers full trace"]},
            {"x": 710, "y": 110, "w": 150, "h": 55, "style": "accent", "lines": ["keep errors", "+ slow + critical"]},
            {"x": 710, "y": 195, "w": 150, "h": 55, "style": "ghost", "lines": ["drop most", "healthy traces"]},
        ],
        edges=[
            {"x1": 145, "y1": 190, "x2": 145, "y2": 220, "label": "no", "lx": 120, "amber": True},
            {"x1": 240, "y1": 145, "x2": 300, "y2": 175, "label": "yes"},
            {"x1": 430, "y1": 180, "x2": 500, "y2": 185, "label": "100%"},
            {"x1": 670, "y1": 175, "x2": 710, "y2": 140, "amber": True},
            {"x1": 670, "y1": 195, "x2": 710, "y2": 218},
        ],
        notes=[
            {"x": 145, "y": 50, "text": "cheap, blind", "anchor": "middle", "size": 12},
            {"x": 675, "y": 50, "text": "costs RAM, keeps what matters", "anchor": "middle", "size": 12},
        ])


# ── Fig 11.1 — The correlation graph (trace_id + exemplars) ─────────────────
def fig_11_correlation_graph():
    g.emit("fig-11-correlation-graph", 900, 360,
        nodes=[
            {"x": 360, "y": 40,  "w": 180, "h": 70, "style": "ink", "lines": ["trace_id", "the shared key"]},
            {"x": 80,  "y": 200, "w": 170, "h": 70, "style": "box", "lines": ["Trace", "Tempo"]},
            {"x": 365, "y": 230, "w": 170, "h": 70, "style": "box", "lines": ["Logs", "Loki"]},
            {"x": 650, "y": 200, "w": 170, "h": 70, "style": "box", "lines": ["Metrics", "Mimir · exemplars"]},
        ],
        edges=[
            {"x1": 400, "y1": 110, "x2": 200, "y2": 200, "label": "span_id", "amber": True},
            {"x1": 450, "y1": 110, "x2": 450, "y2": 230, "label": "trace_id in log line", "amber": True, "lx": 560},
            {"x1": 500, "y1": 110, "x2": 720, "y2": 200, "label": "exemplar → trace", "amber": True, "ly": 150},
            {"x1": 250, "y1": 250, "x2": 365, "y2": 262, "label": "pivot", "bidir": True},
            {"x1": 535, "y1": 262, "x2": 650, "y2": 250, "label": "pivot", "bidir": True},
        ],
        notes=[{"x": 450, "y": 330, "text": "Follow one request: trace → its logs → its metrics, all linked by the same trace_id.",
                "anchor": "middle", "size": 12}])


FIGURES = [
    fig_02_otel_data_path,
    fig_03_service_topology,
    fig_04_instrumentation_layers,
    fig_07_context_propagation,
    fig_09_sampling_location,
    fig_11_correlation_graph,
]

if __name__ == "__main__":
    os.makedirs(g.OUT, exist_ok=True)
    for fn in FIGURES:
        fn()
        print("emitted:", fn.__name__)
    print("done →", os.path.abspath(g.OUT))

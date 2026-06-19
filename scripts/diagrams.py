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
            {"x": 170, "y": 330, "w": 770, "h": 80, "label": "Postgres · appdb", "fill": "#fdecec"},
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


# ── Fig 6.1 — Logs stamped with the trace: the ids are the join key ──────────
def fig_06_log_correlation():
    g.emit("fig-06-log-correlation", 860, 320,
        nodes=[
            {"x": 30,  "y": 120, "w": 180, "h": 80, "style": "accent",
             "lines": ["request span", "trace_id = abc…"]},
            {"x": 290, "y": 120, "w": 230, "h": 80, "style": "box",
             "lines": ["log line (JSON)", "{ msg, trace_id: abc… }"]},
            {"x": 600, "y": 66,  "w": 150, "h": 66, "style": "box", "lines": ["Loki", "logs, by trace_id"]},
            {"x": 600, "y": 210, "w": 150, "h": 66, "style": "box", "lines": ["Tempo", "traces, by trace_id"]},
        ],
        edges=[
            {"x1": 210, "y1": 160, "x2": 290, "y2": 160, "label": "stamps the ids", "amber": True, "ly": -10},
            {"x1": 520, "y1": 145, "x2": 600, "y2": 105, "label": "OTLP → Collector"},
            {"x1": 675, "y1": 132, "x2": 675, "y2": 210, "label": "trace_id", "amber": True, "bidir": True},
        ],
        notes=[{"x": 430, "y": 34,
                "text": "Stamp each log with the active trace_id; the line in Loki and the trace in Tempo then point at each other.",
                "anchor": "middle", "size": 12}])


# ── Fig 5.1 — Metrics and exemplars: one request, two shapes ─────────────────
def fig_05_metrics_exemplars():
    g.emit("fig-05-metrics-exemplars", 920, 340,
        nodes=[
            {"x": 40,  "y": 135, "w": 160, "h": 90, "style": "accent",
             "lines": ["incoming requests", "POST /orders"]},
            {"x": 300, "y": 70,  "w": 220, "h": 72, "style": "box",
             "lines": ["one span per request", "per-event"]},
            {"x": 600, "y": 74,  "w": 150, "h": 64, "style": "box", "lines": ["Tempo", "traces"]},
            {"x": 300, "y": 210, "w": 220, "h": 84, "style": "box",
             "lines": ["duration histogram", "periodic aggregate · p50·p95·p99"]},
            {"x": 600, "y": 218, "w": 150, "h": 64, "style": "box", "lines": ["Mimir", "rate · errors · p99"]},
        ],
        edges=[
            {"x1": 200, "y1": 160, "x2": 300, "y2": 106, "label": "record a span"},
            {"x1": 200, "y1": 200, "x2": 300, "y2": 252, "label": "+ record duration", "ly": 10},
            {"x1": 520, "y1": 106, "x2": 600, "y2": 106},
            {"x1": 520, "y1": 252, "x2": 600, "y2": 250},
            {"x1": 410, "y1": 210, "x2": 410, "y2": 142, "label": "exemplar → trace_id", "amber": True, "lx": 70},
        ],
        notes=[{"x": 460, "y": 32,
                "text": "One request, two shapes: a per-event span and a periodic aggregate. The exemplar links a histogram bucket back to a real trace.",
                "anchor": "middle", "size": 12}])


# ── Fig 1.1 — The running stack: what `podman compose up` brings up ──────────
def fig_01_running_stack():
    g.emit("fig-01-running-stack", 960, 390,
        bands=[
            {"x": 20,  "y": 50, "w": 920, "h": 320, "label": "compose network", "fill": "#f7f7f7"},
            {"x": 540, "y": 80, "w": 400, "h": 240, "label": "grafana/otel-lgtm · one image", "fill": "#fafafa"},
        ],
        nodes=[
            {"x": 50,  "y": 105, "w": 200, "h": 95, "style": "accent",
             "lines": ["six services", "REST · gRPC · GraphQL · Kafka", "host :8080 / :8081"]},
            {"x": 300, "y": 215, "w": 150, "h": 55, "style": "box", "lines": ["Kafka", "order.placed"]},
            {"x": 300, "y": 295, "w": 150, "h": 55, "style": "box", "lines": ["Postgres", "appdb"]},
            {"x": 565, "y": 110, "w": 160, "h": 70, "style": "sub",
             "lines": ["OTel Collector", "OTLP/HTTP in :4318"]},
            {"x": 770, "y": 110, "w": 150, "h": 70, "style": "box",
             "lines": ["Tempo · Mimir · Loki", "traces · metrics · logs"]},
            {"x": 650, "y": 240, "w": 200, "h": 60, "style": "ink",
             "lines": ["Grafana", ":3000 — one UI for all three"]},
        ],
        edges=[
            {"x1": 250, "y1": 145, "x2": 565, "y2": 145, "label": "OTLP/HTTP :4318", "amber": True},
            {"x1": 160, "y1": 200, "x2": 310, "y2": 230, "label": "events"},
            {"x1": 135, "y1": 200, "x2": 305, "y2": 305, "label": "SQL", "dashed": True, "lx": -10},
            {"x1": 725, "y1": 145, "x2": 770, "y2": 145, "amber": True},
            {"x1": 845, "y1": 180, "x2": 800, "y2": 240, "label": "query"},
        ],
        notes=[{"x": 480, "y": 32,
                "text": "What `podman compose up` brings up: the services, Postgres and Kafka, and the bundled otel-lgtm backend (Collector → stores → Grafana).",
                "anchor": "middle", "size": 12}])


# ── Fig 12.1 — The live service graph: trace-derived topology with RED on edges ─
def fig_13_service_graph():
    g.emit("fig-13-service-graph", 900, 430,
        nodes=[
            {"x": 60,  "y": 150, "w": 150, "h": 62, "style": "accent", "lines": ["order", "/orders · REST"]},
            {"x": 60,  "y": 330, "w": 150, "h": 48, "style": "sub",    "lines": ["postgres"]},
            {"x": 360, "y": 70,  "w": 150, "h": 52, "style": "box",    "lines": ["inventory", "gRPC"]},
            {"x": 360, "y": 158, "w": 150, "h": 52, "style": "box",    "lines": ["payment", "gRPC"]},
            {"x": 360, "y": 246, "w": 150, "h": 52, "style": "sub",    "lines": ["kafka", "order.placed"]},
            {"x": 620, "y": 212, "w": 150, "h": 50, "style": "box",    "lines": ["shipping"]},
            {"x": 620, "y": 288, "w": 150, "h": 50, "style": "box",    "lines": ["notification"]},
        ],
        edges=[
            {"x1": 210, "y1": 172, "x2": 360, "y2": 96,  "label": "45 rps · 0% err", "amber": True, "ly": -10},
            {"x1": 210, "y1": 184, "x2": 360, "y2": 184, "label": "45 rps · 2% err", "amber": True, "ly": -10},
            {"x1": 210, "y1": 198, "x2": 360, "y2": 272, "label": "publish"},
            {"x1": 510, "y1": 272, "x2": 620, "y2": 237, "label": "consume"},
            {"x1": 510, "y1": 282, "x2": 620, "y2": 313, "label": "consume"},
            {"x1": 135, "y1": 212, "x2": 135, "y2": 330, "label": "db writes", "dashed": True, "lx": 30},
        ],
        notes=[
            {"x": 450, "y": 32,
             "text": "The live service graph — request rate, error rate, and latency on every edge",
             "anchor": "middle", "size": 13},
            {"x": 450, "y": 410,
             "text": "Built by Tempo's metrics-generator from span relationships — no service mesh, no sidecars, no Kubernetes.",
             "anchor": "middle", "size": 12},
        ])


# ── Fig 11.1 — Continuous profiling: the span → flame-graph link ─────────────
def fig_12_profiling():
    g.emit("fig-12-profiling", 900, 360,
        nodes=[
            {"x": 40,  "y": 150, "w": 210, "h": 84, "style": "accent",
             "lines": ["span: Authorize", "820 ms — but where?", "(Tempo)"]},
            # flame graph: nested frames, the hotspot highlighted
            {"x": 520, "y": 120, "w": 330, "h": 28, "style": "box",  "lines": ["serve (request)"]},
            {"x": 520, "y": 150, "w": 280, "h": 28, "style": "box",  "lines": ["Authorize"]},
            {"x": 520, "y": 180, "w": 180, "h": 28, "style": "accent","lines": ["serialize 55%"]},
            {"x": 700, "y": 180, "w": 100, "h": 28, "style": "sub",  "lines": ["db.execute 30%"]},
        ],
        edges=[
            {"x1": 250, "y1": 188, "x2": 520, "y2": 160,
             "label": "Traces → Profiles · same service + time window", "amber": True, "ly": -12},
        ],
        notes=[
            {"x": 690, "y": 104, "text": "CPU flame graph (Pyroscope)", "anchor": "middle", "size": 12},
            {"x": 450, "y": 320,
             "text": "Traces localise the slow span; the profile shows which functions burned the CPU inside it.",
             "anchor": "middle", "size": 12},
        ])


# ── Fig 0.1 — The arc: three parts, one trace_id, ending in one correlated view ─
def fig_00_arc():
    g.emit("fig-00-arc", 940, 300,
        bands=[
            {"x": 20, "y": 210, "w": 900, "h": 70,
             "label": "one trace_id — end to end through every hop", "fill": "#fdecec"},
        ],
        nodes=[
            {"x": 40,  "y": 80, "w": 220, "h": 95, "style": "accent",
             "lines": ["Foundations", "the stack + the services", "§0–§3"]},
            {"x": 330, "y": 80, "w": 300, "h": 95, "style": "box",
             "lines": ["The three signals", "traces · metrics · logs", "→ one correlated view  ·  §4–§9"]},
            {"x": 700, "y": 80, "w": 220, "h": 95, "style": "box",
             "lines": ["The pipeline", "sampling · profiling", "keep it affordable"]},
        ],
        edges=[
            {"x1": 260, "y1": 127, "x2": 330, "y2": 127, "amber": True},
            {"x1": 630, "y1": 127, "x2": 700, "y2": 127, "amber": True},
            {"x1": 150, "y1": 175, "x2": 150, "y2": 210, "dashed": True},
            {"x1": 480, "y1": 175, "x2": 480, "y2": 210, "dashed": True},
            {"x1": 810, "y1": 175, "x2": 810, "y2": 210, "dashed": True},
        ],
        notes=[{"x": 470, "y": 45,
                "text": "Build it in three parts; the same trace_id threads through all of them, ending in one correlated view.",
                "anchor": "middle", "size": 12}])


FIGURES = [
    fig_00_arc,
    fig_01_running_stack,
    fig_02_otel_data_path,
    fig_03_service_topology,
    fig_04_instrumentation_layers,
    fig_05_metrics_exemplars,
    fig_06_log_correlation,
    fig_07_context_propagation,
    fig_09_sampling_location,
    fig_11_correlation_graph,
    fig_12_profiling,
    fig_13_service_graph,
]

if __name__ == "__main__":
    os.makedirs(g.OUT, exist_ok=True)
    for fn in FIGURES:
        fn()
        print("emitted:", fn.__name__)
    print("done →", os.path.abspath(g.OUT))

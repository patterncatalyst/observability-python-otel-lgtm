---
title: "Iteration plan"
order: 1
description: "The roadmap from the PRD's milestones to shipped iterations."
render_with_liquid: false
---

# Iteration plan

This project is built in iterations, packaged as `observability-python-otel-lgtm-rNN.x.tar.gz`,
with the slide deck as `otel-lgtm-python-rNN.x.pptx`. The PRD is the scope
authority; this page tracks the order of build.

## r0.1 — Foundation (this iteration)

- [x] Repository skeleton: Jekyll site (layouts, includes, CSS), GitHub Pages workflow.
- [x] House style unified on Red Hat red across the site, the shared diagrams, and the deck.
- [x] Shared diagram pipeline: one spec → SVG + Excalidraw (`scripts/diagrams.py`) → PNG for the deck (`scripts/render_pngs.sh`).
- [x] All six figures drafted (Figs 2.1, 3.1, 4.1, 7.1, 9.1, 11.1).
- [x] The shared stack: compose (LGTM + Postgres + Kafka + api + worker), base + tail-sampling Collector configs, Grafana datasource provisioning, DB schema.
- [x] The demo app: FastAPI front door, Kafka worker, Postgres round trip, Poetry packaging, UBI multi-stage Containerfile.
- [x] Demo 1 (app, no telemetry) as a runnable example with a driver and a smoke test.
- [x] Chapters for Part 0 — Foundations: Outline, Prerequisites, Fundamentals, The demo app.
- [x] Slide deck through §3, embedding the shared figures.
- [x] Plans: this roadmap and the reconciliation plan.

## r1.0 — The three signals

- [ ] §4 Auto-instrumentation + Demo 2 (traces for free in Tempo). Resolve the Python 3.14 wheel question first.
- [ ] §5 Metrics → Mimir + Demo 3 (RED + a custom business metric, a Grafana panel).
- [ ] §6 Logs → Loki + Demo 4 (structured logs, trace_id/span_id injection, log↔trace pivot).
- [ ] §7 Custom instrumentation + Demo 5 (manual spans; trace context across both Kafka hops). Uses Fig 7.1.
- [ ] Deck sections for §4–§7.

## r2.0 — The pipeline

- [ ] §8 The hybrid approach + Demo 6 (duplicate-span / suppression gotcha). Uses Fig 4.1.
- [ ] §9 The Collector & sampling + Demo 7 (head vs. tail; swap Collector config). Uses Fig 9.1.
- [ ] §10 Continuous profiling + Demo 8 (optional; flame graph, span↔profile).
- [ ] §11 The correlated view + Demo 9 (one trace → logs → metrics via exemplars). Uses Fig 11.1.
- [ ] §12 Anti-patterns & production notes; §N Where to go next.
- [ ] Deck sections for §8–§N.

## r3.0 — Hardening for delivery

- [ ] `scripts/test-all-examples.sh` green from a cold start on Fedora and macOS.
- [ ] Cross-platform verification; promote demo rows to verified in the reconciliation plan.
- [ ] Timed rehearsal of both delivery profiles (90-min core, ~3-hr workshop).
- [ ] Recorded demo fallbacks captured.
- [ ] Editorial pass; set the github_username and baseurl; publish the repo and Pages site.

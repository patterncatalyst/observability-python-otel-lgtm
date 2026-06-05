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

## r1.1 — The three signals (this iteration)

*Supersedes the earlier r1.0 working cuts (never committed): r1.1 folds in §8–§9,
Demos 6–7, the professional-audience rewrite, the prerequisites install table, and
unpublishing the internal plans from the site.*

**Architecture pivot.** r1.x replaced the single FastAPI+worker app with a
set of six example services (order, inventory, payment, shipping,
notification, review) so the trace can be examined across REST, gRPC, GraphQL,
Kafka, and Postgres in one request. The service names are borrowed from a separate
[data-mesh reference project](https://github.com/patterncatalyst/datamesh-reference-arch-python),
but this is plainly a set of services on Podman compose — an OpenTelemetry talk,
not a data mesh and not Kubernetes. The r0.1 `app/` and its example were removed.

- [x] Scrubbed all eBPF/Rust/Aya/Fedora-KVM/bpftool/bcc template language from
  the site scaffold (index, includes, layout favicon, CSS, diagram engine).
- [x] Shared protos at the repo top level (`proto/shop/...`) for the gRPC hops,
  compiled by `scripts/gen-protos.sh`.
- [x] Shared `obs` library (`services/common/`): OTel bootstrap, Kafka context
  propagation, asyncpg pool, trace-stamped JSON logging.
- [x] Six services under `services/` + one parameterized `services/Containerfile`.
- [x] Rewrote the stack: compose with the six services + LGTM + Postgres + Kafka
  + Kafka-UI; multi-domain schema; sampling config retargeted to `/orders`.
- [x] Tooling: curl scripts, a Postman collection, `hey` (REST) and `ghz` (gRPC)
  load drivers.
- [x] §3 rewritten for the example services; §4 Auto-instrumentation, §5 Metrics,
  §6 Logs, §7 Custom spans across Kafka, §8 Auto vs custom vs hybrid, and §9
  Reading it in Grafana (the correlated view) written under "The three signals."
- [x] Demos 1–7 as runnable examples (no-telemetry baseline; auto-instrumentation
  with the Kafka break; metrics; logs; spans across Kafka with the fix; the
  hybrid; the correlated-view walkthrough).
- [x] Prerequisites chapter carries a Fedora 44 + macOS install table; the PRD and
  plans are unpublished from the site (internal tracking only).
- [x] New `fig-03-service-topology`; deck built as
  `presentations/otel-lgtm-python-r1.1.pptx`.

## r2.0 — The pipeline

The hybrid approach and the correlated view moved forward into the r1.1 "three
signals" part (§8 and §9). The pipeline part is now the Collector-side concerns.

- [ ] §10 The Collector & sampling + Demo 8 (head vs. tail; swap Collector config; what it costs to keep). Uses Fig 9.1.
- [ ] §11 Continuous profiling + Demo 9 (optional; flame graph, span↔profile).
- [ ] §12 Anti-patterns & production notes; §N Where to go next.
- [ ] Deck sections for §8–§N.

## r3.0 — Hardening for delivery

- [ ] `scripts/test-all-examples.sh` green from a cold start on Fedora and macOS.
- [ ] Cross-platform verification; promote demo rows to verified in the reconciliation plan.
- [ ] Timed rehearsal of both delivery profiles (90-min core, ~3-hr workshop).
- [ ] Recorded demo fallbacks captured.
- [ ] Editorial pass; set the github_username and baseurl; publish the repo and Pages site.

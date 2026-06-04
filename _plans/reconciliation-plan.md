---
title: "Reconciliation plan"
order: 2
description: "Per-claim verification log. Everything is unverified until a real run confirms it."
render_with_liquid: false
---

# Reconciliation plan

Nothing here runs in the authoring environment (no Podman, no network), so every
demo and version claim is **unverified** until a real `podman compose up` + test
run confirms it on each target platform (current Fedora; current macOS with a
fresh Podman machine). This page is the record of intended vs. delivered.

## Demos

| # | Chapter | Status | What a real run must confirm |
|---|---|---|---|
| 1 | The demo app | unverified | Cold `podman compose up --build`; API healthy; `POST /compute {n:100}` → `result 5050`; a `jobs` row written; image builds on the chosen UBI Python base. |
| 2 | Auto-instrumentation | not started | `opentelemetry-instrument` produces FastAPI/Kafka/Postgres spans in Tempo with no code change — on Python 3.14 or a documented fallback. |
| 3 | Metrics | not started | RED metrics + one custom metric reach Mimir; a Grafana panel renders them. |
| 4 | Logs | not started | Structured logs with trace_id/span_id reach Loki; the log↔trace pivot works via the provisioned derived field. |
| 5 | Custom spans across Kafka | not started | traceparent injected/extracted on both Kafka hops; worker + Postgres + reply spans join the originating trace. |
| 6 | Hybrid | not started | Auto + custom together; the duplicate-span / suppression gotcha reproduces and the fix removes it. |
| 7 | Sampling | not started | Head vs. tail Collector configs both run; tail keeps errors + slow + `/compute`; memory stays bounded under `hey`. |
| 8 | Profiling | not started | Continuous profiling backend pinned; a flame graph renders; span↔profile link works. |
| 9 | Correlated view | not started | One request followed trace → logs → metrics via exemplars in a single Grafana view. |

## Versions to pin and re-verify against upstream before delivery

| Component | Pinned here | To confirm |
|---|---|---|
| Grafana otel-lgtm | `0.8.1` | tag still published; bundled Collector includes `tail_sampling` (contrib). |
| Postgres | `16-alpine` | — |
| Kafka (apache/kafka) | `3.8.0` | KRaft single-broker config still valid. |
| Python runtime | target 3.14; range `>=3.12,<3.15` | **UBI Python 3.14 image tag exists**; auto-instrumentation wheels published for 3.14. |
| UBI base image | `ubi9/python-312:latest` (ARG `PYTHON_BASE`) | swap to the 3.14 tag once confirmed. |
| Poetry | `1.8.5` | — |
| FastAPI / uvicorn | `0.115.6` / `0.34.0` | — |
| aiokafka / asyncpg | `0.12.0` / `0.30.0` | wheels for the chosen Python. |

## Open questions carried from the PRD

- Python 3.14 auto-instrumentation wheel availability (gates Demo 2's runtime).
- Profiling backend choice (dedicated Pyroscope-style vs. native OTel profiling signal).
- Exemplar support configured as Demo 9 needs in the pinned Mimir/Grafana.
- One Kafka broker (current choice) vs. a small cluster.
- Ship a Postman collection, or are `curl` + `hey` enough.

## Iteration log

- **r0.1** — Foundation scaffolded: site, shared stack, demo app, Demo 1, Figs 2/3/4/7/9/11, chapters §0–§3, deck through §3. All demos unverified; no real run in the loop.

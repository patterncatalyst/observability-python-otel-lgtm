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

## Architecture pivot (r1.0)

r1.0 replaced the single FastAPI+worker app with a six-service data-mesh-style
application (order, inventory, payment, shipping, notification, review) spanning
REST, gRPC, GraphQL, Kafka, and Postgres, mirroring the
[data-mesh reference architecture](https://github.com/patterncatalyst/datamesh-reference-arch-python)
but on Podman compose rather than Kubernetes. Decisions taken, all unverified:

- **One database (`meshdb`), all domains.** A laptop simplification; production
  would isolate a store per domain. Stated in `stack/db/init/01-schema.sql`.
- **Shared `obs` library as a Poetry path dependency** (`obs = {path="../common"}`),
  installed alongside each service in the shared `services/Containerfile`.
- **`PROPAGATE_KAFKA_CONTEXT` toggle** gates the manual Kafka propagation so Demo
  2 shows the trace breaking at the broker and Demo 5 shows it fixed.
- **`OTEL_SDK_DISABLED` defaults to false** in compose (`${OTEL_SDK_DISABLED:-false}`);
  Demo 1 overrides it true for the no-telemetry baseline.

## Demos

| # | Chapter | Status | What a real run must confirm |
|---|---|---|---|
| 1 | The demo mesh | unverified | Cold `podman compose up --build`; all six service images build on the UBI Python base; protos compile into each image; `POST /orders` → `confirmed`; a shipment row + notification log appear. |
| 2 | Auto-instrumentation | unverified | With `PROPAGATE_KAFKA_CONTEXT=false`, one trace spans order → inventory/payment gRPC → Postgres in Tempo with no app code; consumers form separate traces. On Python 3.14 or a documented fallback. |
| 3 | Metrics | unverified | RED metrics for the order service reach Mimir; the error line tracks payment-declined load; exemplars resolve to real traces. |
| 4 | Logs | unverified | Order logs are JSON with a populated `trace_id` during a request; value matches the trace; Loki derived field links to Tempo. |
| 5 | Custom spans across Kafka | unverified | With propagation on, shipping + notification spans share the order's trace and parent to its publish span; GraphQL resolver spans nest under the request. aiokafka header round-trip of `traceparent` is the highest risk. |
| 6 | Hybrid | not started | Auto + custom together; the duplicate-span / suppression gotcha reproduces and the fix removes it. |
| 7 | Sampling | not started | Head vs. tail Collector configs both run; tail keeps errors + slow + `/orders`; memory stays bounded under `hey`. |
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
| grpcio | `1.68.0` | wheels for the chosen Python; matches grpcio-tools used to compile protos. |
| strawberry-graphql | `0.248.0` | GraphQLRouter API stable on this version. |
| opentelemetry-api / -sdk | `1.30.0` | exporter + instrumentation versions move together. |
| opentelemetry-exporter-otlp-proto-http | `1.30.0` | OTLP/HTTP log exporter import path (`_log_exporter`) still valid. |
| opentelemetry-instrumentation-{fastapi,grpc,asyncpg} | `0.51b0` | the `0.NNbM` line tracks the `1.NN` core; **published for Python 3.14**. |

## Open questions carried from the PRD

- Python 3.14 auto-instrumentation wheel availability (gates Demo 2's runtime).
- Profiling backend choice (dedicated Pyroscope-style vs. native OTel profiling signal).
- Exemplar support configured as Demo 9 needs in the pinned Mimir/Grafana.
- One Kafka broker (current choice) vs. a small cluster.
- Ship a Postman collection, or are `curl` + `hey` enough.

## Iteration log

- **r0.1** — Foundation scaffolded: site, shared stack, demo app, Demo 1, Figs 2/3/4/7/9/11, chapters §0–§3, deck through §3. All demos unverified; no real run in the loop.

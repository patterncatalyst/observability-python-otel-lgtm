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

## Architecture pivot (r1.x)

The r1.x line replaced the single FastAPI+worker app with a set of six example services
(order, inventory, payment, shipping, notification, review) spanning REST, gRPC,
GraphQL, Kafka, and Postgres on Podman compose. The service names are borrowed
from a separate data-mesh reference project; this is not a data mesh. Decisions taken, all unverified:

- **One database (`appdb`), all domains.** A laptop simplification; production
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
| 1 | The example services | unverified | Cold `podman compose up --build`; all six service images build on the UBI Python base; protos compile into each image; `POST /orders` → `confirmed`; a shipment row + notification log appear. |
| 2 | Auto-instrumentation | unverified | With `PROPAGATE_KAFKA_CONTEXT=false`, one trace spans order → inventory/payment gRPC → Postgres in Tempo with no app code; consumers form separate traces. On Python 3.14 or a documented fallback. |
| 3 | Metrics | unverified | RED metrics for the order service reach Mimir; the error line tracks payment-declined load; exemplars resolve to real traces. |
| 4 | Logs | unverified | Order logs are JSON with a populated `trace_id` during a request; value matches the trace; Loki derived field links to Tempo. |
| 5 | Custom spans across Kafka | unverified | With propagation on, shipping + notification spans share the order's trace and parent to its publish span; GraphQL resolver spans nest under the request. aiokafka header round-trip of `traceparent` is the highest risk. |
| 6 | Auto vs custom vs hybrid | unverified | Fully-instrumented trace shows both auto and custom spans in one tree; no operation is double-instrumented; metric pipeline carries no unbounded labels. |
| 7 | Correlated view (Grafana) | unverified | Span→logs link resolves by `trace_id`; metric exemplars open a trace; gRPC client/server span pair exposes serde cost + message-size attributes; one `order_id` agrees across trace, logs, and Postgres. |
| 8 | Sampling | not started | Head vs. tail Collector configs both run; tail keeps errors + slow + `/orders`; memory stays bounded under `hey`. |
| 9 | Profiling | not started | Continuous profiling backend pinned; a flame graph renders; span↔profile link works. |

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
| opentelemetry-instrumentation-{fastapi,grpc,asyncpg} | `0.51b0` | the `0.NNbM` line tracks the `1.NN` core; **confirm wheels published for Python 3.14** (the open question below). |

## Open questions carried from the PRD

- Python 3.14 auto-instrumentation wheel availability (gates Demo 2's runtime).
- Profiling backend choice (dedicated Pyroscope-style vs. native OTel profiling signal).
- Exemplar support configured as Demo 7 needs in the pinned Mimir/Grafana.

## Resolved

- Postman collection — **shipped** (`tools/postman/`), alongside `curl` + `hey` + `ghz`.
- Single Kafka broker (KRaft) — **kept**; a cluster is out of scope for a laptop demo.

## Iteration log

- **r0.1** — Foundation scaffolded: site, shared stack, the original FastAPI+worker app, Demo 1, Figs 2/3/4/7/9/11, chapters §0–§3, deck through §3. All demos unverified; no real run in the loop.
- **r1.1** — Architecture pivot to six example services across REST/gRPC/GraphQL/Kafka/Postgres; shared `proto/shop` contracts and the `obs` library; rewritten stack and tooling (curl/Postman/hey/ghz); chapters §3–§9 (the full three-signals arc, incl. §8 auto/custom/hybrid and §9 the Grafana correlated view); Demos 1–7; professional-audience rewrite; Fedora 44 + macOS prerequisites table; plans unpublished from the site. Still unverified; no real run in the loop.

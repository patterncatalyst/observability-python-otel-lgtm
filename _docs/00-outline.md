---
title: "Outline"
order: 0
part: "Foundations"
description: "What this talk covers, the running example, and the two ways to deliver it."
duration: 3 minutes
---

Every distributed system eventually puts the same three questions to whoever is
on call: where did the time go, which service actually failed, and what did it log
at the moment it did. Across service boundaries, logs alone answer none of them
well — and that gap, not a shortage of log lines, is what this talk closes. You
take a realistic set of Python services and make one request's whole journey
legible: a single trace you can read end to end, with metrics and logs that link
back to it.

The running example is a small set of services — order, inventory, payment, shipping,
notification, review — where one `POST /orders` fans out across REST at the edge, gRPC
between services, an asynchronous Kafka event, Postgres underneath, and a GraphQL
read path. Over the talk that system grows traces, metrics, and logs from a
single OpenTelemetry SDK, all correlated in a self-hosted Grafana stack, with an
OpenTelemetry Collector in the path making the sampling and routing decisions.

Everything runs locally under Podman. There are no paid accounts and no managed
cloud on the path — the whole backend is the open-source Grafana **LGTM** stack:
**L**oki for logs, **G**rafana to view them, **T**empo for traces, and
**M**imir for metrics.

## The arc

{% include excalidraw.html file="fig-00-arc" alt="A three-part roadmap: Foundations, then the three signals converging into one correlated view, then the pipeline; a single trace_id threads through all three." caption="Figure 0.1 — The arc: three parts, one trace_id, ending in one correlated view" %}

| Part | Theme | Chapters |
|---|---|---|
| **Foundations** | the stack, the signals, the services | Outline, Prerequisites, Fundamentals, The services |
| **The three signals** | traces, metrics, logs — and correlation | Auto-instrumentation, Metrics, Logs, Custom spans across Kafka, Auto vs custom vs hybrid, Reading it in Grafana |
| **The pipeline** | the Collector and what to keep | Sampling, Profiling |

## Two ways to deliver it

The same materials run as a 90-minute core talk or a half-day workshop. The core
path is the foundations, the four headline demos (auto-instrumentation, logs to
traces, custom spans across the Kafka hop, and the correlated view), and the
sampling discussion. The full workshop runs every demo live, including metrics,
the hybrid pattern, and continuous profiling, with one break in the middle.

What this talk is *not*: it does not teach Python, FastAPI, Kafka, or Postgres
fundamentals; it does not deploy any of this to Kubernetes; and it does not
compare commercial observability vendors. The backend is self-hosted and
vendor-neutral, so mapping any of it to a managed service later is yours to do.

The next chapter covers what you need installed to follow along.

---

*Verification status: <span class="status status--unverified">unverified</span>.
The duration estimates are targets to confirm in a timed rehearsal.*

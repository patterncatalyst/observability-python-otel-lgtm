---
title: "Prerequisites and the running stack"
order: 1
part: "Foundations"
description: "What to install, and a tour of the live LGTM stack before any code is instrumented."
duration: 8 minutes
---

Before instrumenting anything, you need the tools installed and the backend
running. This chapter pins the versions the demos assume and tours the stack so
that when telemetry starts flowing, you already know where it lands.

## What you need installed

The demos target **Python 3.14** with **Poetry** for dependency management, and
they run on **Podman** with `podman compose` — not Docker. Podman is rootless by
default and is the engine on the platforms this talk targets (current Fedora and
current macOS via the Podman machine). On macOS, give the Podman machine at
least 4 GB of memory; the full stack uses roughly 3 GB across all its services.

<div class="callout callout--warn">
  <p class="callout__title">Python 3.14 and auto-instrumentation</p>
  <p>The talk's narrative targets Python 3.14. Whether the OpenTelemetry
  auto-instrumentation wheels are published for a brand-new CPython is a thing to
  confirm against upstream right before delivery — it is the single biggest
  readiness risk here. The app's dependency range stays open to 3.12+ so the
  demo installs on whatever supported CPython the current Red Hat UBI image
  ships while that 3.14 image tag is confirmed.</p>
</div>

## The stack, before any telemetry

The backend is one image — `grafana/otel-lgtm` — that bundles Grafana, Tempo,
Mimir (Prometheus-compatible), Loki, *and* an OpenTelemetry Collector. Bundling
it keeps the demo to a single `podman compose up`, but the architecture it
stands for is the real one: applications send to a Collector, and the Collector
routes each signal to its backend. We mount our own Collector config into the
image precisely so that sampling and routing stay first-class, swappable things
rather than hidden defaults.

Everything for the stack lives under `stack/`. Bring it up with:

```bash
cd stack && podman compose up --build
```

Once it is healthy, these are the addresses worth knowing. From the host you
reach services on `localhost` and the host-side port; from *inside* the compose
network, services reach each other by service name on the container-internal
port — a distinction that is the most common source of "can't reach the
Collector" confusion.

| Service | From the host | Inside the network | Purpose |
|---|---|---|---|
| Grafana | `http://localhost:3000` | `http://lgtm:3000` | the one UI for all three signals |
| OTLP/HTTP | `http://localhost:4318` | `http://lgtm:4318` | where telemetry is sent |
| OTLP/gRPC | `localhost:4317` | `lgtm:4317` | the gRPC alternative |
| Tempo | `http://localhost:3200` | `http://lgtm:3200` | trace storage and query |
| Mimir | `http://localhost:9090` | `http://lgtm:9090` | metric storage and query |
| Loki | `http://localhost:3100` | `http://lgtm:3100` | log storage and query |
| API | `http://localhost:8080` | `http://api:8080` | the demo service |

## A house-style choice: OTLP over HTTP

Telemetry can leave the SDK over OTLP/gRPC (port 4317) or OTLP/HTTP (port 4318).
This talk defaults to **HTTP on 4318**. It is easier to debug — a plain `curl`
can post to it — more firewall-friendly, and for a development workload the
performance difference is negligible. The gRPC endpoint stays exposed, so
switching is a one-line change to `OTEL_EXPORTER_OTLP_PROTOCOL` and the endpoint
port. Wherever you see an endpoint in the chapters that follow, it is the
path-less form `http://lgtm:4318`, which the SDK completes per signal.

## Cross-check

Confirm the backend is actually up before moving on, rather than trusting that
the containers started:

```bash
curl -sf http://localhost:3000/api/health   # Grafana: expect {"database":"ok",...}
curl -sf http://localhost:4318/v1/traces -X POST -H 'content-type: application/json' -d '{}'
```

The first confirms Grafana is serving. The second posts an empty payload to the
Collector's trace endpoint; an HTTP response (even a complaint about the empty
body) proves the OTLP receiver is listening on 4318.

## What you learned

- The demos run on Podman with `podman compose`, target Python 3.14 with Poetry,
  and use the bundled `grafana/otel-lgtm` backend with a Collector in the path.
- Host access is `localhost` + host port; in-network access is service-name +
  container port — the two are not interchangeable.
- This talk sends OTLP over HTTP on 4318 by default, with gRPC a one-line switch.

The next chapter steps back from the wiring to the ideas: what the three signals
are, and why one shared trace context is what makes them worth more together
than apart.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm the pinned image tags resolve, the health checks pass on
both target platforms, and the chosen UBI Python base image tag (3.14 vs. a
supported fallback) before the prerequisites are stated as final.*

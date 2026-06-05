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

Almost nothing has to be installed by hand. The backend — Grafana, Tempo, Mimir,
Loki, the Collector, Postgres, and Kafka — arrives as container images the first
time you run `podman compose up`, and the gRPC stubs are compiled inside each
service image, so there is no `protoc` toolchain to set up. What you do need is a
container engine and a way to drive traffic at the services.

| Tool | What it's for | Fedora 44 | macOS (Homebrew) |
|---|---|---|---|
| **Podman + compose** | the container engine the whole stack runs on (rootless; not Docker) | `sudo dnf install podman podman-compose` | `brew install podman podman-compose`, then `podman machine init --memory 6144 && podman machine start` |
| **git** | clone the repo | `sudo dnf install git` | preinstalled, or `brew install git` |
| **curl** | drive the REST and GraphQL edges from a shell | preinstalled | preinstalled |
| **Python 3.14 + Poetry** | *optional* — only to run or develop a service outside its container | `sudo dnf install python3.14 pipx && pipx install poetry` | `brew install python@3.14 pipx && pipx install poetry` |
| **hey** | *optional* — HTTP load on the REST edge (the metrics chapter) | `sudo dnf install golang && go install github.com/rakyll/hey@latest` | `brew install hey` |
| **ghz** | *optional* — load straight at a gRPC service | `sudo dnf install golang && go install github.com/bojand/ghz/cmd/ghz@latest` | `brew install ghz` |
| **Postman** | *optional* — a GUI alternative to the curl scripts | `flatpak install flathub com.getpostman.Postman` | `brew install --cask postman` |

On macOS the engine is the Podman machine, a small Linux VM; the `--memory 6144`
above gives it the ~3.5 GB the full stack needs with headroom. On Fedora, Podman
runs natively and rootless. The `go install` binaries land in `~/go/bin`, so add
that to your `PATH` if it isn't already.

<div class="callout callout--warn">
  <p class="callout__title">Python 3.14 and auto-instrumentation</p>
  <p>The talk's narrative targets Python 3.14. Whether the OpenTelemetry
  auto-instrumentation wheels are published for a brand-new CPython is a thing to
  confirm against upstream right before delivery — it is the single biggest
  readiness risk here. Each service's dependency range stays open to 3.12+ so the
  images install on whatever supported CPython the current Red Hat UBI base
  ships while that 3.14 tag is confirmed.</p>
</div>

## The stack, before any telemetry

{% raw %}{% include excalidraw.html file="fig-01-running-stack" alt="The compose network: six services send OTLP/HTTP on 4318 to the bundled otel-lgtm Collector, which feeds Tempo, Mimir, and Loki behind one Grafana UI; the services also talk to Kafka and Postgres." caption="Figure 1.1 — One podman compose up: the services, Kafka and Postgres, and the bundled otel-lgtm backend" %}{% endraw %}

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
| Order (REST) | `http://localhost:8080` | `http://order:8080` | external edge: place/read orders |
| Review (GraphQL) | `http://localhost:8081/graphql` | `http://review:8081` | external read edge |
| Kafka UI | `http://localhost:8090` | — | inspect topics and the `order.placed` event |

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

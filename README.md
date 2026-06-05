# 🔭 Observability for Python with OpenTelemetry & the Grafana LGTM Stack

A demo-driven talk and companion tutorial. You instrument a realistic set of
Python services — **order, inventory, payment, shipping, notification, review** —
where one `POST /orders` fans out across **REST**, **gRPC**, **GraphQL**,
**Kafka**, and **Postgres**, with **OpenTelemetry**, then ship traces, metrics,
and logs into a self-hosted **Grafana LGTM** stack (**L**oki, **G**rafana,
**T**empo, **M**imir) and correlate all three signals across one request. The
services use familiar e-commerce domain names purely as a convenient, realistic
shape to instrument — the point is the observability, not the domain.

Everything runs locally with a single `podman compose up`. No SaaS, no
API keys, no cloud account, and no Kubernetes — just the OSS stack on your
laptop. This is an OpenTelemetry talk, not a Kubernetes one.

---

## What's in here

This repository is four deliverables that share one source of truth:

| Path | What it is |
|------|------------|
| [`_docs/`](_docs/) | The **tutorial site** chapters (Jekyll). Numbered, part-grouped, served as a static site. |
| [`deck/`](deck/) | The **slide deck tooling** — `deck.js` source + the `pptxgenjs` design system, shared assets, and diagram PNGs. |
| [`presentations/`](presentations/) | The **built decks** (`.pptx`), one per talk/cut — committed deliverables built from `deck/`. |
| [`proto/`](proto/) | The **shared gRPC contracts** (`proto/shop/...`), at the top level so every service compiles one copy of the truth. |
| [`services/`](services/) | The **six domain services** plus the shared `obs` library (`services/common/`) and one parameterized `Containerfile`. |
| [`stack/`](stack/) | The **observability stack** — `compose.yaml` for Grafana LGTM, the OTel Collector, Postgres, and Kafka, plus the six services. |
| [`tools/`](tools/) | **curl** scripts, a **Postman** collection, and **hey**/**ghz** load drivers to exercise the running services. |
| [`examples/`](examples/) | One thin **runnable demo** per chapter; each drives the shared stack. |
| [`assets/diagrams/`](assets/diagrams/) | The **shared diagrams** — `.svg` + `.excalidraw`, generated from `scripts/diagrams.py`. |

**The site and the deck share the same diagrams.** `scripts/diagrams.py` emits
each figure once as SVG (embedded in the site) and as an editable `.excalidraw`
source; `scripts/render_pngs.sh` rasterizes the same SVGs to PNG for the deck.
One spec → identical figures in the book and the slides.

---

## Quick start

### Run the stack and the services

```bash
# from the repo root
cd stack
podman compose up --build -d   # Grafana LGTM + Collector + Postgres + Kafka + 6 services
```

Then open:

- **Grafana** — <http://localhost:3000> (anonymous admin, no login)
- **Order API (REST)** — <http://localhost:8080/health>
- **Review API (GraphQL)** — <http://localhost:8081/graphql>
- **Kafka UI** — <http://localhost:8090>

Place an order — one request that fans out across REST, gRPC, Kafka, and Postgres:

```bash
curl -s -X POST http://localhost:8080/orders \
  -H 'content-type: application/json' \
  -d '{"customer_id": "cust-42", "sku": "WIDGET-001", "quantity": 1}'
# => {"order_id": "...", "status": "confirmed", "amount_cents": 1999}
```

More ways to drive it — curl scripts, a Postman collection, and `hey`/`ghz` load
generators — are in [`tools/`](tools/). Tear down:

```bash
podman compose down -v
```

Each chapter has a matching driver under `examples/NN-*/` with `demo.sh` and a
`test.sh` assertion.

### Build the slide deck

```bash
cd deck
export NODE_PATH=$(npm root -g)
node deck.js                  # → ../presentations/otel-lgtm-python.pptx
```

Built decks land in [`presentations/`](presentations/) and are committed. See
that folder's README for adding a second deck (e.g. a workshop cut).

### Serve the tutorial site locally

```bash
bundle install
bundle exec jekyll serve --baseurl ""
# => http://127.0.0.1:4000
```

### Regenerate the diagrams

```bash
python scripts/diagrams.py        # → assets/diagrams/*.svg + *.excalidraw
bash scripts/render_pngs.sh       # → deck/png/*.png  (needs LibreOffice)
```

---

## The example services

One `POST /orders` fans out across five protocols and six services, which is what
makes it a good observability teaching example — trace context has to survive
gRPC calls, an asynchronous Kafka hop, and database round trips, not just an
in-process call:

```
client ──REST──▶ order ──gRPC──▶ inventory  (reserve stock)
                   │   ──gRPC──▶ payment    (authorize)
                   │   ──SQL──▶  Postgres    (persist)
                   └─produce──▶ Kafka (order.placed)
                                   ├──▶ shipping     (consume → shipment)
                                   └──▶ notification (consume → notify)
client ──GraphQL──▶ review  (read orders + reviews)
```

The order service reserves stock and authorizes payment over gRPC, persists the
order, and publishes `order.placed`; shipping and notification consume it
asynchronously; review serves a GraphQL read path. gRPC and Postgres are
auto-instrumented, so those spans join the request's trace for free — the one hop
that needs explicit context propagation is Kafka, which is the climax of the
talk. The gRPC contracts are shared protos under [`proto/`](proto/); the shared
`obs` library under `services/common/` carries all the instrumentation. See
[`_docs/03-demo-app.md`](_docs/03-demo-app.md) for the call-by-call walkthrough.

---

## Requirements

- **Podman** + **podman compose** (the stack is Podman-first, rootless, UBI-based — no Docker required)
- **Python 3.14** target for the services; each `pyproject.toml` allows `>=3.12,<3.15` so the images build on a current UBI Python while the 3.14 tag is confirmed
- **Node.js** (for building the deck)
- **Ruby + Bundler** (only to serve the site locally; GitHub Pages builds it for you)

---

## Shipping changes

Every push (to any branch) triggers the Actions workflow, which builds the site;
pushes to `main` also deploy it to Pages. The going-forward loop is stage →
commit → push → watch the run:

```bash
scripts/ship.sh "what changed in this commit"
```

That stages everything, commits, pushes, and attaches to the resulting Actions
run with `gh run watch`. (It's just a wrapper over `git add -A && git commit &&
git push && gh run watch` — run those by hand if you prefer.)

---

## Before you publish

A couple of placeholders need real values:

- `_config.yml` → `github_username` (currently `your-username`) and, if this is
  a project Pages site, confirm `baseurl: "/observability-python-otel-lgtm"`.
- Confirm the **Python 3.14** UBI image tag and that the OpenTelemetry
  auto-instrumentation wheels are available for 3.14 (the single biggest unknown).

---

## License

[Apache 2.0](LICENSE).

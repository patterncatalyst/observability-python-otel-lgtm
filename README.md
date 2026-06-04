# 🔭 Observability for Python with OpenTelemetry & the Grafana LGTM Stack

A demo-driven talk and companion tutorial. You instrument a realistic Python
service — **FastAPI → Kafka → worker → Postgres → Kafka → FastAPI** — with
**OpenTelemetry**, then ship traces, metrics, and logs into a self-hosted
**Grafana LGTM** stack (**L**oki, **G**rafana, **T**empo, **M**imir) and
correlate all three signals across one request.

Everything runs locally with a single `podman compose up`. No SaaS, no
API keys, no cloud account — just the OSS stack on your laptop.

> **Status: foundation iteration (r0.1).** Sections 0–3, the demo app, the
> stack, and all six shared diagrams are authored. Demos 2–9 and the
> three-signals / pipeline deep-dives land in later iterations — see
> [`_plans/iteration-plan.md`](_plans/iteration-plan.md). Every demo currently
> ships marked **`unverified`**: authored against the target versions but not
> yet executed end-to-end in this environment (no container runtime here).
> See [`_plans/reconciliation-plan.md`](_plans/reconciliation-plan.md).

---

## What's in here

This repository is four deliverables that share one source of truth:

| Path | What it is |
|------|------------|
| [`_docs/`](_docs/) | The **tutorial site** chapters (Jekyll). Numbered, part-grouped, served as a static site. |
| [`deck/`](deck/) | The **slide deck** — a 1.5–3 hr presentation built with `pptxgenjs`. |
| [`app/`](app/) | The **demo application** — shared FastAPI + worker source, packaged with Poetry, containerized on UBI. |
| [`stack/`](stack/) | The **observability stack** — `compose.yaml` for Grafana LGTM, the OTel Collector, Postgres, and Kafka. |
| [`examples/`](examples/) | One thin **runnable demo** per chapter; each drives the shared stack. |
| [`assets/diagrams/`](assets/diagrams/) | The **shared diagrams** — `.svg` + `.excalidraw`, generated from `scripts/diagrams.py`. |

**The site and the deck share the same diagrams.** `scripts/diagrams.py` emits
each figure once as SVG (embedded in the site) and as an editable `.excalidraw`
source; `scripts/render_pngs.sh` rasterizes the same SVGs to PNG for the deck.
One spec → identical figures in the book and the slides.

---

## Quick start

### Run the stack and the demo app

```bash
# from the repo root
cd stack
podman compose up -d          # Grafana LGTM + Collector + Postgres + Kafka + app
```

Then open:

- **Grafana** — <http://localhost:3000> (anonymous admin, no login)
- **Demo API** — <http://localhost:8080/health>
- **Kafka UI** — <http://localhost:8085>

Drive a request through the whole async round trip:

```bash
curl -s -X POST http://localhost:8080/compute \
  -H 'content-type: application/json' \
  -d '{"n": 100}'
# => {"request_id": "...", "n": 100, "result": 5050}
```

Tear down:

```bash
podman compose down -v
```

Each chapter has a matching driver under `examples/NN-*/` with `demo.sh`
(`up` / `drive` / `down` / `clean`) and a `test.sh` assertion.

### Build the slide deck

```bash
cd deck
export NODE_PATH=$(npm root -g)
node deck.js                  # writes the .pptx
```

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

## The demo application

A single request makes a full asynchronous round trip, which is what makes it a
good observability teaching example — context has to propagate across a message
broker, not just an in-process call:

```
client ──HTTP──▶ FastAPI ──produce──▶ Kafka (requests)
                                            │
                                            ▼
                              worker ──query──▶ Postgres
                                            │
                  FastAPI ◀──Kafka (replies)─┘
   client ◀──HTTP── (correlated by request_id)
```

The API holds each caller's request open against a `Future` keyed by
`request_id`, publishes to the `requests` topic, and resolves the future when
the matching reply arrives on the `replies` topic. The worker does the actual
compute (a triangular number, scaled by a multiplier it reads from Postgres),
records the job, and publishes the reply. See
[`_docs/03-demo-app.md`](_docs/03-demo-app.md) for the call-by-call walkthrough.

---

## Requirements

- **Podman** + **podman compose** (the stack is Podman-first, rootless, UBI-based — no Docker required)
- **Python 3.14** target for the app (the env here is 3.12; `pyproject.toml` allows `>=3.12,<3.15` so it installs on the current UBI Python image while the 3.14 image tag is confirmed — tracked as an open question in the reconciliation plan)
- **Node.js** (for building the deck)
- **Ruby + Bundler** (only to serve the site locally; GitHub Pages builds it for you)

---

## Before you publish

A couple of placeholders need real values:

- `_config.yml` → `github_username` (currently `your-username`) and, if this is
  a project Pages site, confirm `baseurl: "/observability-python-otel-lgtm"`.
- Confirm the **Python 3.14** UBI image tag and that the OpenTelemetry
  auto-instrumentation wheels are available for 3.14 (the single biggest
  unknown — see PRD §12 and the reconciliation plan).

---

## License

[Apache 2.0](LICENSE).

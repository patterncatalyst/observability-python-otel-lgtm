# Product Requirements Document — Observability for Python with OpenTelemetry and the Grafana LGTM Stack

> A live, demo-driven technical presentation (1.5–3 hours). This PRD reuses the
> tutorial-PRD structure but is written for a **talk with live demos**: "reader"
> means "attendee," and each demo is treated as a runnable example that stays
> `unverified` until it has actually run end-to-end on the target platform.

---

## 1. Summary

**One sentence:** A hands-on talk that takes a working Python/FastAPI service —
one that makes an async round trip through Kafka and Postgres — and shows, live,
how to make it observable with OpenTelemetry traces, metrics, and logs,
correlated across the whole chain and feeding a self-hosted Grafana stack.

**One paragraph:** The topic is instrumenting a realistic Python workload with
OpenTelemetry and seeing it correlated in Grafana. The workload is a small but
complete async chain: a FastAPI service accepts a request, publishes it to a
Kafka topic, a separate Python consumer processes it — reading from and writing
to Postgres — and publishes a result back onto a reply topic, which the FastAPI
service consumes and returns to the caller. Attendees arrive comfortable with
Python and HTTP services but with only a vague mental model of "observability" —
they may have bolted on a metrics library or a logging format before, but they
haven't seen traces, metrics, and logs emitted from one SDK, tied together by a
shared trace context that survives the hop across Kafka, and routed through a
vendor-neutral Collector. They leave able to stand up the same stack locally with
Podman, follow a single request as one trace across every hop of the chain, pivot
from that trace to its logs and metrics, choose between auto-, custom-, and hybrid
instrumentation deliberately, and reason about head vs. tail sampling. This talk
exists because most OTel material is either a five-line "hello span" snippet or
vendor-specific SaaS marketing; very little walks a complete, container-native,
rootless, UBI-based Python service — with a real async message boundary in the
middle — through all three signals on an entirely self-hosted open-source
backend. (Continuous profiling is included as an optional extension, §10.)

---

## 2. Problem statement

### Who is the reader?

The primary attendee is a **mid-to-senior Python backend or platform engineer**
who ships HTTP services and is on the hook for them in production. They know
FastAPI (or Flask/Django) and async Python, can read a docker/podman compose
file, and have used Grafana to *look at* dashboards someone else built. They do
**not** have a working model of OpenTelemetry's architecture, have never
configured a Collector, and treat tracing, metrics, and logging as three
unrelated tools. Their motivation is usually a recent incident: a latency
regression or an intermittent failure they couldn't explain because the three
signals lived in three disconnected systems with no shared identifiers.

### What's their pain today?

Without this talk, an engineer who wants end-to-end observability has to
assemble it from a dozen partial sources: the OTel docs (excellent reference,
poor narrative), one blog post per signal, vendor quickstarts that assume you'll
send data to *their* SaaS, and Grafana docs that assume the data is already
arriving. The result is cargo-culting — people copy a working `tracer` snippet
without understanding context propagation, never correlate logs to traces,
emit metrics with unbounded-cardinality labels, and discover sampling only after
their backend bill (or memory) explodes. Cross-signal correlation, async context
propagation across a Kafka boundary, and sampling strategy are exactly the parts
the scattered sources skip.

### Why now?

OpenTelemetry's metrics and logs signals are stable and the SDK story is mature
enough that "traces, metrics, and logs from one SDK" is finally a realistic ask rather
than an aspiration. The Grafana LGTM stack is fully open-source and runs locally
under Podman, so the entire demo is reproducible with no paid accounts. Python
3.14 is current, which raises a real, timely question the audience will hit —
whether the auto-instrumentation libraries have caught up to a brand-new CPython
(flagged in §9/§12 as something to verify before delivery).

---

## 3. Goals and non-goals

### Goals (what success looks like)

- An attendee who finishes can stand up the full LGTM + demo-app stack locally
  with `podman compose up` and see traces, metrics, logs, and profiles in
  Grafana without consulting other resources.
- An attendee understands *why* a shared trace context is what makes
  cross-signal correlation possible — not just which decorator to copy.
- An attendee can articulate the difference between auto-, custom-, and hybrid
  instrumentation and choose deliberately for a given service.
- An attendee can explain head vs. tail sampling, where each decision is made in
  the pipeline, and the trade-off each makes.
- Every live demo builds and runs end-to-end on the target platforms (§9) with
  no manual fixups, from a cold `podman compose up`.
- The talk fits a 90-minute "core" delivery and a ~3-hour "full workshop"
  delivery from the same materials, by adding/removing demos (see §5).

### Non-goals (what this is NOT)

- This does NOT teach Python, FastAPI, Kafka, or Postgres fundamentals (assumed
  prerequisites).
- This does NOT cover Kubernetes deployment of the Collector or the LGTM stack
  (out of scope; everything runs in local Podman — a natural follow-on).
- This does NOT compare commercial observability vendors or managed backends
  (vendor-neutral; the whole point is self-hosted OSS — attendees can map to a
  SaaS themselves).
- This does NOT do a deep dive on OTel internals (exporters, processors,
  resource detection) beyond what the demos require.
- This does NOT cover front-end / browser / mobile (RUM) instrumentation.

---

## 4. Audience details

### Primary audience

Mid-to-senior Python backend/platform engineers on Linux (Fedora/RHEL) or macOS,
running containers with Podman, who own services in production and want a
self-hosted, vendor-neutral observability story for them.

### Secondary audience

SREs and platform engineers who operate the backend rather than write the app —
they get the Collector, sampling, and dashboard-provisioning material and can
treat the app instrumentation as context. Also tech leads evaluating OTel
adoption who want a concrete sense of the effort and the payoff. Served
gracefully by keeping the Collector/sampling/dashboard segments self-contained so
they stand on their own without the app-coding detail.

### Audience NOT served

Complete beginners with no container or HTTP-service experience; Windows users
not on WSL2 (Podman machine assumed); anyone looking for a managed-SaaS
quickstart or a language other than Python.

---

## 5. Scope and section outline

Two delivery profiles come out of one set of materials:

- **Core (~90 min):** §0, §2, §3, §4, §6, §7, §11, §N — concepts plus four live
  demos (auto-instrumentation, logs↔traces correlation, custom spans + Kafka
  propagation, the correlated view). Sampling, profiling, and the hybrid pattern
  are *discussed* but not demoed.
- **Full workshop (~3 hr):** every section, every demo run live, with one ~10-min
  break after §6 or §7.

`[C]` marks core-path sections; `[X]` marks extended-only.

### Sections

| §  | Title                                          | Purpose                                                                 | Est. duration |
|----|------------------------------------------------|-------------------------------------------------------------------------|---------------|
| 0  | Outline `[C]`                                  | Attendee's map of what's ahead; set the two delivery profiles           | 3 min         |
| 1  | Prerequisites & the running stack `[C]`        | What's installed (Python 3.14, Poetry, Podman); tour the live LGTM stack | 8 min        |
| 2  | Observability fundamentals `[C]`               | The three signals (traces, metrics, logs) + OTel architecture (SDK → Collector → backends); the "why" | 15 min |
| 3  | The demo app & how it's built `[C]`            | FastAPI → Kafka req topic → consumer → Postgres → reply topic → back; UBI multi-stage; `podman compose up` (Demo 1) | 12 min |
| 4  | Auto-instrumentation: zero-code `[C]`          | `opentelemetry-instrument`; traces appear in Tempo for free (Demo 2)    | 18 min        |
| 5  | Metrics → Mimir `[C]`                          | RED method, a custom business metric, a Grafana dashboard panel (Demo 3) | 16 min       |
| 6  | Logs → Loki `[C]`                              | Structured logs, trace_id/span_id injection, log↔trace pivot (Demo 4)   | 14 min        |
| 7  | Custom instrumentation `[C]`                   | Manual spans/attributes; **context propagation across both Kafka hops** (Demo 5)  | 20 min        |
| 8  | The hybrid approach `[X]`                      | Auto + custom together; the duplicate-span / suppression gotcha (Demo 6) | 10 min       |
| 9  | The Collector & sampling `[C]`                 | Head vs. tail sampling, where each decides, config both (Demo 7)        | 20 min        |
| 10 | Continuous profiling & tuning `[X]` (optional) | Flame graphs, span↔profile correlation, one tuning change (Demo 8)      | 15 min        |
| 11 | The correlated view `[C]`                      | One Grafana view: follow one request as a trace → its logs → its metrics via exemplars (Demo 9)| 12 min |
| 12 | Anti-patterns & production notes `[X]`         | Cardinality, PII in spans, sampling regret, over-instrumentation        | 8 min         |
| N  | Where to go next `[C]`                         | Collector on Kubernetes, OTel profiling signal, OTTL transforms, SaaS export | 5 min     |

**Total estimated duration (full workshop):** ~176 min of content; with one
~10-min break, lands at roughly 3 hours. The 90-min core path is the eight `[C]`
sections with demo time trimmed.

### Optional appendices or follow-ons

- **The OTel profiling signal** vs. a dedicated profiling backend — once the
  native profiling signal matures, revisit §10 to emit profiles through the same
  Collector pipeline as the three core signals.
- **Collector deployment patterns** — agent vs. gateway, the Collector on
  Kubernetes / OpenShift, OTTL transforms. Deferred; out of local-Podman scope.
- **Exporting to a managed backend** — swapping the OTLP exporter target so the
  same instrumentation feeds a SaaS instead of self-hosted Grafana. A one-line
  config change worth showing as proof of vendor-neutrality.

---

## 6. Runnable examples

### Will this tutorial have runnable code examples?

- [x] Yes

All demos are live; nothing is staged screenshots. Each demo is a self-contained
example directory with a run script and README, in the lgtm-tutorial example
shape.

### If yes, what languages or tools?

| Component | Detail |
|-----------|--------|
| Language / runtime | Python **3.14** |
| Dependency / build | **Poetry** (lockfile committed; `poetry install` in the build stage) |
| Web framework | **FastAPI** (+ Uvicorn) |
| Async messaging | **Kafka** (request topic + reply topic; FastAPI produces the request and consumes the reply, a separate consumer service does the work) |
| Database | **Postgres** |
| Instrumentation | OpenTelemetry Python SDK + `opentelemetry-instrumentation` (auto), manual API for custom spans/metrics |
| Pipeline | OpenTelemetry **Collector** (OTLP/gRPC in; routes to each backend) |
| Backends | **Grafana** + **Tempo** (traces) + **Mimir** (metrics) + **Loki** (logs) + a profiling backend (Pyroscope-style) |
| Containers | **Podman + podman compose**; **Red Hat UBI** base images; **multi-stage** builds, rootless |
| Load / test | **hey** (load), **curl** (smoke), **Postman** collection (manual exploration) |

Runtime/version notes to pin and re-verify before delivery (see §12): exact
Python 3.14.x patch; auto-instrumentation wheel availability for 3.14; pinned
Collector, Tempo, Mimir, Loki, Grafana, and profiling-backend versions; UBI
image tag.

Service dependencies: Postgres and Kafka run as compose services. No special
hardware. No paid accounts.

### Demos (the runnable set)

| # | Section | What it shows |
|---|---------|----------------|
| 1 | §3  | Cold `podman compose up` → POST to the FastAPI endpoint with curl; the request rides Kafka to the consumer, hits Postgres, comes back as the HTTP response. **No telemetry yet** |
| 2 | §4  | Relaunch under `opentelemetry-instrument`; FastAPI, Kafka, and Postgres spans auto-appear in Tempo, zero code change |
| 3 | §5  | RED metrics + one custom business metric → Mimir; build a Grafana panel live |
| 4 | §6  | Structured JSON logs with `trace_id`/`span_id` injected; pivot Loki log → Tempo trace and back |
| 5 | §7  | Manual spans + attributes around business logic; propagate trace context **across both Kafka hops** (request and reply) so the consumer, Postgres, and reply spans all join the one originating trace |
| 6 | §8  | Hybrid: keep auto, add custom spans; show the duplicate-span / suppression gotcha and how to avoid it |
| 7 | §9  | Two Collector configs — head (probabilistic) vs. tail (keep errors + slow traces); drive with `hey`; compare what each keeps |
| 8 | §10 | *(optional)* Enable continuous profiling; load a hot path; read the flame graph; make one tuning change; show the delta |
| 9 | §11 | One Grafana view following a single request as one trace, linked to its logs and metrics via exemplars (and its profile, if §10 ran) |

### Test strategy for examples

- [x] Per-example test scripts under `scripts/` using `curl`/`hey` against each
  service (see `scripts/test-template.sh`); a Postman collection ships alongside
  for manual exploration but is not the automated gate.
- [x] Aggregator `scripts/test-all-examples.sh` brings up the stack, runs each
  example's test in sequence, and tears down.
- [ ] CI integration via GitHub Actions — desirable once examples are stable;
  deferred until after first live delivery.
- [ ] Manual verification only — not acceptable here; live demos must be scripted.

The reconciliation plan tracks every demo's verification state — `unverified`
until a real `podman compose up` + test-script run confirms it on each target
platform.

---

## 7. Diagrams

### Will this tutorial use diagrams?

- [x] Yes, paired SVG + Excalidraw source (via `scripts/generate_diagram.py`)

### Anticipated diagrams

- **Fig 2.x** — The three signals and the OTel data path: app + SDK → Collector
  (receivers/processors/exporters) → Tempo / Mimir / Loki → Grafana (profiling
  backend optional). The "how the pieces fit" anchor for §2.
- **Fig 3.x** — Demo app topology and the async round trip: client → FastAPI →
  Kafka request topic → consumer service → Postgres → Kafka reply topic →
  FastAPI → client.
- **Fig 4.x** — Instrumentation layering: auto vs. custom vs. hybrid, and what
  each contributes.
- **Fig 7.x** — Context propagation across the async boundary: how `traceparent`
  rides on each Kafka message so the consumer, Postgres, and reply spans all join
  the originating request's trace.
- **Fig 9.x** — Where the sampling decision is made: head (at/near the SDK,
  before the data exists) vs. tail (at the Collector, after the full trace
  arrives).
- **Fig 11.x** — The correlation graph: trace_id and exemplars as the links that
  connect a span to its logs and metrics (and its profile, if §10 ran).

---

## 8. Success metrics

### Verification metrics (you control these)

- All nine demos pass `scripts/test-all-examples.sh` from a cold start on the
  target platforms (§9).
- Reconciliation plan shows all demo rows as `verified`.
- §1 prerequisites tested on a fresh VM of each target platform (clean Fedora;
  clean macOS with a fresh Podman machine).
- The full deck plus demos fits inside 3 hours with one break in a rehearsal
  run; the core path fits 90 minutes in a rehearsal run.
- Each demo has a recorded fallback (asciinema/screen capture) in case live
  fails (see §10 risks).

### Adoption metrics (harder to control)

- Post-talk: attendees who later stand up the repo themselves (repo stars/clones
  as a weak proxy).
- CFP acceptance and re-invites; session feedback scores where the venue
  collects them. Slow, noisy signals — not a basis for in-flight decisions.

---

## 9. Constraints and dependencies

### Technical constraints

- Containers run on **Podman + podman compose**, not Docker.
- Base images are **Red Hat UBI**; every container file uses a **multi-stage
  build** (build stage with Poetry + toolchain; slim runtime stage).
- Everything runs **rootless**.
- Primary platforms: **Fedora (current)** and **current macOS** (Podman machine).
- No example may require a paid service, account, or anything behind a paywall —
  the entire backend is self-hosted OSS.
- Python **3.14**; Poetry for dependency management; OTLP as the wire protocol
  (gRPC by default, with a note on HTTP).
- The whole stack must come up from a single `podman compose up` and be
  reachable on documented loopback ports.

### Editorial constraints

- Vendor-neutral: no comparisons to commercial observability products; map-to-SaaS
  left to the attendee.
- "You" for the attendee; passive or third-person otherwise; no "we" voice.
- Commands are copy-pasteable as single lines; prompts/prefixes show *where* a
  command runs (host vs. container).
- Image and package references are fully qualified.
- Diagrams are SVG (scale on hi-DPI), paired with editable Excalidraw source.
- Code shown in slides is the real, runnable code from the example dirs — no
  stubs that diverge from what runs.

### Dependencies

- UBI image availability and tag stability on the Red Hat registry.
- A Podman version whose `podman compose` supports the compose features used.
- OpenTelemetry Python SDK + auto-instrumentation packages **with working wheels
  for Python 3.14** (the key risk — see §10/§12).
- OpenTelemetry Collector version with the `tail_sampling` processor.
- Tempo, Mimir, Loki, Grafana, and the profiling backend — all pinned.
- Kafka and Postgres container images.

If auto-instrumentation lags Python 3.14, the fallback is to pin the demo to the
latest fully-supported 3.x for the auto-instrumentation demo while keeping custom
instrumentation on 3.14 — decided after the readiness check in §12.

---

## 10. Risks and mitigations

| Risk                                                          | Impact | Likelihood | Mitigation                                                                 |
|---------------------------------------------------------------|--------|------------|----------------------------------------------------------------------------|
| Python 3.14 auto-instrumentation wheels not yet available     | High   | Medium     | Verify early (§12); fall back to a supported runtime for Demo 2 if needed; pin versions in the reconciliation plan |
| Live demo fails on stage (network, cold cache, timing)        | High   | Medium     | Pre-warm the stack before the session; recorded fallback per demo; idempotent run scripts |
| Tail-sampling Collector memory blows up under `hey` load      | Medium | Medium     | Bound decision wait + max traces in config; keep demo load modest; show the knob as a teaching point |
| Example runs on Fedora but not macOS (Podman machine quirks)  | Medium | Medium     | Cross-platform verify before marking demos `verified`; document Podman-machine resource minimums in §1 |
| Talk runs long; attendees don't finish                        | High   | Medium     | Two delivery profiles (§5); core path front-loads value; sectioned so partial reads work |
| Talk too shallow; misses the "why" of correlation/propagation | Medium | Low        | §2, §7, §11 carry the conceptual load; each demo includes a "how it works" walkthrough |
| Profiling backend / OTel profiling signal in flux             | Medium | Medium     | Treat §10 as extended/optional; pin the profiling backend; note the native signal as a follow-on |
| Upstream LGTM or Collector config changes mid-prep            | Medium | Medium     | Pin all versions; re-verify against upstream right before delivery; log in reconciliation plan |

---

## 11. Timeline and milestones

| Milestone                                      | Est. effort | Done? |
|------------------------------------------------|-------------|-------|
| PRD reviewed and approved                      | 1–2 hours   | [ ]   |
| Skeleton scaffolded and config'd               | 30 min      | [ ]   |
| §1 prerequisites + compose stack drafted       | 3–5 hours   | [ ]   |
| Demo 1 (app up, no telemetry) working          | 3–6 hours   | [ ]   |
| Demo 2 (auto-instrumentation) working          | 2–4 hours   | [ ]   |
| Python 3.14 instrumentation readiness verified | 1–2 hours   | [ ]   |
| Demos 3–4 (metrics, logs+correlation) working  | 4–8 hours   | [ ]   |
| Demo 5 (custom spans + Kafka propagation)      | 4–6 hours   | [ ]   |
| Demos 6–7 (hybrid, sampling) working           | 4–8 hours   | [ ]   |
| Demos 8–9 (profiling, correlated view)         | 4–8 hours   | [ ]   |
| All sections drafted (zero-draft)              | 8–12 hours  | [ ]   |
| All demos passing `test-all-examples.sh`       | 4–6 hours   | [ ]   |
| Cross-platform verification (Fedora + macOS)   | 3–5 hours   | [ ]   |
| Diagrams drafted (Figs 2/3/4/7/9/11)           | 3–5 hours   | [ ]   |
| Slide deck assembled from sections             | 6–10 hours  | [ ]   |
| Rehearsal: time both delivery profiles         | 3–4 hours   | [ ]   |
| Editorial pass for tone and voice              | 4–8 hours   | [ ]   |
| Reconciliation plan reflects reality           | 1–2 hours   | [ ]   |
| Recorded demo fallbacks captured               | 2–3 hours   | [ ]   |
| Public delivery / publish repo                 | —           | [ ]   |

**Hard deadline (if any):** TODO — set to the target CFP/conference date.

**Realistic launch target:** TODO — pick once the conference date is fixed.

---

## 12. Open questions

- Are OpenTelemetry auto-instrumentation wheels available and working for Python
  **3.14** today? (Determines whether Demo 2 runs on 3.14 or a fallback runtime.)
  Verify against upstream before drafting Demo 2.
- Profiles: use a dedicated profiling backend (Pyroscope-style) now, or wait on
  the **native OTel profiling signal**? What's its current maturity, and can it
  route through the same Collector pipeline? (Affects §10 and the §11 correlated
  view.)
- Which **exact versions** of Tempo, Mimir, Loki, Grafana, the Collector, and the
  profiling backend to pin — and do their current configs match what the demos
  assume?
- For exemplars (metrics→trace links), is the chosen Mimir/Grafana version's
  exemplar support configured the way Demo 9 needs?
- One Kafka broker for the demo, or is a small cluster worth the compose weight?
- Postman collection: ship it, or is `curl` + `hey` enough and Postman just adds
  maintenance?

---

## 13. Decision log

| Date | Decision | Rationale |
|------|----------|-----------|
| TODO | Podman + podman compose over Docker | Default on target platforms; rootless; matches the audience's likely RHEL/Fedora reality |
| TODO | Red Hat UBI base images, multi-stage builds | Production-representative base; multi-stage keeps the runtime image slim and free of build tooling |
| TODO | Poetry for dependency management | Lockfile reproducibility; clean separation of build vs. runtime stages |
| TODO | Self-hosted Grafana LGTM stack (no SaaS) | Vendor-neutral; fully reproducible with no paid accounts; the whole pedagogical point |
| TODO | OTel Collector in the path (not direct-to-backend export) | Lets sampling, batching, and routing be taught as first-class; mirrors real deployments |
| TODO | Tail sampling demonstrated at the Collector | Keeps errors and slow traces regardless of volume — the realistic production choice |
| TODO | Async request/reply over Kafka (request topic + reply topic) | Propagating trace context across two message hops and back is the correlation story scattered sources skip; the round trip is what "return it to the caller" requires |
| TODO | Local Podman compose, no Kubernetes | Keep the focus on Python + OTel; everyone can run the whole chain locally without cluster complexity |
| TODO | Two delivery profiles from one set of materials | Same repo serves a 90-min slot and a 3-hr workshop without a separate build |

---

## 14. Stakeholders

| Name   | Role     | What they need |
|--------|----------|----------------|
| Robert | Author / presenter | The repo, deck, and verified demos ready before the CFP date |
| TODO   | CFP / program committee | Accepted abstract; session length confirmed (90 min vs. half-day) |
| TODO   | Reviewer (optional) | A dry-run pass on the demos and timing before delivery |

---

## How to use this PRD

- First thing to read at the start of each work session — a 3-minute scan to
  recenter on what's being built and why.
- The reference when scope creep tempts ("is this in section 5? no? then it's
  not in this talk").
- The handoff document if a collaborator or assistant joins partway through.

Keep it under version control alongside the rest of the project. When something
significant changes (a demo dropped, a delivery profile cut, a version repinned),
update the relevant section and commit with a clear message. When the talk ships,
this PRD becomes the record of "what was intended" against the reconciliation
plan's "what was delivered."

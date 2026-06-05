// deck.js — Observability for Python with OpenTelemetry & the Grafana LGTM Stack
// Foundation iteration (r0.1): cover + Sections 0–3.
//
// Build:  export NODE_PATH=$(npm root -g) && node deck.js
// Shares diagrams with the Jekyll site: deck/png/*.png are rasterized from the
// same assets/diagrams/*.svg the site embeds (scripts/render_pngs.sh).

"use strict";

const H = require("./deck-helpers.js");
const {
  COLOR, FONT, W, ASSETS,
  newDeck, addFooter, addContentTitle, addBullets, addTwoColBullets,
  addStatusTable, addCaption, addCodeSlide, addDiagramSlide, addSectionDivider, addNotes,
} = H;

// Built decks live in the repo under presentations/ (one .pptx per talk/cut).
// Run from inside deck/ (cd deck && node deck.js) so ../presentations resolves
// to the repo root, and ./assets + ./png are found by deck-helpers.js.
const OUT = "../presentations/otel-lgtm-python.pptx";
const REV = "r01.0";

const pres = newDeck();
pres.title = "Observability for Python with OpenTelemetry & the Grafana LGTM Stack";
let pageNum = 0;

function S() {
  const s = pres.addSlide(); pageNum += 1; addFooter(s, pageNum); return s;
}
function divider(code, title, subtitle, notes) {
  const s = pres.addSlide(); pageNum += 1; addSectionDivider(s, code, title, subtitle); addNotes(s, notes);
}

// ── Cover ─────────────────────────────────────────────────────────────────
{
  const s = pres.addSlide();
  pageNum += 1;
  s.background = { color: COLOR.white };
  try { s.addImage({ path: `${ASSETS}/cover-panel.png`, x: 0, y: 0, w: W, h: 7.5 }); } catch (e) {}
  s.addText("OBSERVABILITY · PYTHON · OPENTELEMETRY", {
    x: 6.00, y: 1.86, w: 6.95, h: 0.34,
    fontFace: FONT.title, fontSize: 13, bold: true, color: COLOR.red, charSpacing: 5, align: "left", valign: "middle" });
  s.addText([
    { text: "Make a Python", options: { breakLine: true } },
    { text: "service observable", options: {} },
  ], {
    x: 5.95, y: 2.30, w: 7.05, h: 2.10, fontFace: FONT.title, fontSize: 46, bold: true, color: COLOR.ink, align: "left", valign: "top" });
  s.addText("OpenTelemetry and the self-hosted Grafana LGTM stack — traces, metrics, and logs from one SDK, correlated across one request as it crosses REST, gRPC, Kafka, and Postgres.", {
    x: 6.00, y: 4.50, w: 6.80, h: 1.30,
    fontFace: FONT.body, fontSize: 16, italic: true, color: COLOR.caption, align: "left", valign: "top" });
  s.addText(REV, { x: 11.85, y: 5.95, w: 0.95, h: 0.30, fontFace: FONT.mono, fontSize: 11, color: COLOR.caption, align: "right", valign: "middle" });
  try { s.addImage({ path: `${ASSETS}/logo-candidate-2.png`, x: 11.10, y: 6.80, w: 1.55, h: 0.37 }); } catch (e) {}
  addNotes(s,
    "Welcome. This is a hands-on talk about making a real Python service observable — not a survey of vendors. " +
    "By the end you will have taken one small FastAPI service and grown traces, metrics, and logs out of it with a single OpenTelemetry SDK, " +
    "and seen all three correlated in a self-hosted Grafana stack. Everything runs locally under Podman; nothing here needs a cloud account or a credit card. " +
    "Two ways to run it: a 90-minute core talk, or a half-day workshop where every demo runs live. Set expectations now for which one this session is.");
}

// ── Section 00 divider ──────────────────────────────────────────────────────
divider("00", "Foundations", "The stack, the signals, and the app we will instrument.",
  "This first part lays the groundwork: what the talk covers and how it is delivered, the tools and the running backend, the conceptual model of the three signals, and a close read of the example services. No instrumentation yet — we earn that by first understanding the system we are about to make transparent.");

// ── 0. What this talk is ─────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · OUTLINE", "A few small services, made fully observable");
  addBullets(s, [
    "The running example is a small set of services — order, inventory, payment, shipping, notification, review — where one POST /orders fans out across REST at the edge, gRPC between services, an asynchronous Kafka event, Postgres underneath, and a GraphQL read path.",
    "Over the talk that system grows traces, metrics, and logs from a single OpenTelemetry SDK, all correlated in Grafana, with a Collector in the path making the sampling and routing decisions.",
    "The backend is the open-source Grafana LGTM stack — Loki for logs, Grafana to view, Tempo for traces, Mimir for metrics — running locally under Podman. No paid accounts, no managed cloud on the path.",
  ], { fontSize: 17 });
  addNotes(s,
    "Frame the whole arc here. The system is deliberately a realistic shape — one request that crosses several services and protocols, not a single process. " +
    "That fan-out is the reason the demo earns its keep: context has to survive gRPC calls and a Kafka message, not just an in-process call, which is exactly where correlation usually breaks. " +
    "LGTM is the mnemonic: Loki, Grafana, Tempo, Mimir. Stress that everything is self-hosted and vendor-neutral — mapping it to a managed service later is the audience's to do, not ours.");
}

// ── 0b. The arc ──────────────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · OUTLINE", "The arc, in three parts");
  addStatusTable(s, [
    { code: "Foundations",       name: "the stack, the signals, the services", purpose: "Outline · Prerequisites · Fundamentals · The services" },
    { code: "The three signals", name: "traces, metrics, logs — and correlation", purpose: "Auto-instr · Metrics · Logs · Custom spans across Kafka · Auto/custom/hybrid · Reading it in Grafana" },
    { code: "The pipeline",      name: "the Collector and what to keep", purpose: "Sampling · Profiling" },
  ], { colW: [2.55, 4.20, 5.34], rowH: 0.95 });
  addCaption(s, "Foundations is this part; the three signals and the pipeline are the two halves that follow.");
  addNotes(s,
    "Walk the three parts left to right. Part one (today's foundation iteration) is conceptual and structural. " +
    "Part two adds each signal in turn and ends on carrying trace context across the Kafka hop — the hard, interesting bit. " +
    "Part three moves the costly sampling and routing decisions into the Collector and adds continuous profiling. " +
    "Refer to parts by name, never by slide number.");
}

// ── 0c. Two ways to deliver ──────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · OUTLINE", "Two ways to deliver it — and what it is not");
  addTwoColBullets(s,
    [
      { text: "Core (~90 min): foundations, the four headline demos — auto-instrumentation, logs-to-traces, custom spans across the Kafka hop, the correlated view — and the sampling discussion." },
      { text: "Workshop (~half day): every demo live, including metrics, the hybrid pattern, and continuous profiling, with one break in the middle." },
    ],
    [
      { text: "Not a Python, FastAPI, Kafka, or Postgres tutorial.", muted: true },
      { text: "Not a Kubernetes deployment.", muted: true },
      { text: "Not a commercial-vendor comparison — the backend is self-hosted and vendor-neutral.", muted: true },
    ]);
  addNotes(s,
    "Pick the profile out loud and tell the room which one they are in. The core path is demo-driven and keeps moving; the workshop pauses to run everything live. " +
    "The right column manages expectations: assume working knowledge of the four technologies. If the audience is shaky on Kafka, flag the producer/consumer hop as the one thing to watch and move on. " +
    "The duration numbers are targets to confirm in a timed rehearsal — they are marked unverified in the materials.");
}

// ── 1. Prerequisites — install ───────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · PREREQUISITES", "What you need installed");
  addBullets(s, [
    "Python 3.14 with Poetry for dependency management. The app's range stays open to 3.12+ so it installs on whatever supported CPython the current Red Hat UBI image ships while the 3.14 tag is confirmed.",
    "Podman with podman compose — not Docker. Podman is rootless by default and is the engine on the platforms this talk targets (current Fedora, current macOS via the Podman machine).",
    "On macOS, give the Podman machine at least 4 GB; the full stack uses roughly 3 GB across all its services.",
  ], { fontSize: 17 });
  addNotes(s,
    "The single biggest readiness risk in this whole talk lives on this slide: whether the OpenTelemetry auto-instrumentation wheels are published for a brand-new CPython 3.14. " +
    "Confirm that against upstream right before delivery. The dependency range is deliberately open to 3.12+ precisely so the demo still installs if 3.14 wheels are not ready yet. " +
    "Podman-first is a real constraint, not a preference — the compose file, the rootless build, and the UBI base images all assume it. If someone only has Docker, the compose file will mostly work, but do not promise it.");
}

// ── 1b. The stack, ports ─────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · PREREQUISITES", "One image, the whole backend");
  addStatusTable(s, [
    { code: "Grafana",   name: "localhost:3000", purpose: "the one UI for all three signals" },
    { code: "OTLP/HTTP", name: "localhost:4318", purpose: "where telemetry is sent (this talk's default)" },
    { code: "OTLP/gRPC", name: "localhost:4317", purpose: "the gRPC alternative — a one-line switch" },
    { code: "Tempo",     name: "localhost:3200", purpose: "trace storage and query" },
    { code: "Mimir",     name: "localhost:9090", purpose: "metric storage and query (Prometheus-compatible)" },
    { code: "Loki",      name: "localhost:3100", purpose: "log storage and query" },
    { code: "API",       name: "localhost:8080", purpose: "the demo service" },
  ], { colW: [2.20, 3.10, 6.79], rowH: 0.46 });
  addCaption(s, "From the host: localhost + port. Inside the compose network: service name (lgtm:4318) — the two are not interchangeable.");
  addNotes(s,
    "The backend is one image — grafana/otel-lgtm — that bundles Grafana, Tempo, Mimir, Loki, AND an OpenTelemetry Collector. Bundling keeps the demo to a single podman compose up, " +
    "but the architecture it stands for is the real one: apps send to a Collector, the Collector routes each signal to its backend. We mount our own Collector config in so sampling and routing stay first-class. " +
    "Hammer the host-vs-network distinction — it is the most common 'can't reach the Collector' bug. From your laptop it's localhost:4318; from inside a container it's lgtm:4318.");
}

// ── 1c. OTLP over HTTP ───────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · PREREQUISITES", "A house-style choice: OTLP over HTTP");
  addBullets(s, [
    "Telemetry can leave the SDK over OTLP/gRPC (4317) or OTLP/HTTP (4318). This talk defaults to HTTP on 4318.",
    "It is easier to debug — a plain curl can post to it — more firewall-friendly, and for a development workload the performance difference is negligible.",
    "The gRPC endpoint stays exposed, so switching is a one-line change to OTEL_EXPORTER_OTLP_PROTOCOL and the port. Endpoints in later chapters use the path-less form http://lgtm:4318, which the SDK completes per signal.",
  ], { fontSize: 17 });
  addNotes(s,
    "This is a deliberate, stated choice so nobody wonders later why the endpoints look the way they do. HTTP wins on debuggability for a teaching context — you can curl the receiver to prove it is listening. " +
    "In production with high telemetry volume you might prefer gRPC for throughput; say so, and point out it is genuinely a one-line switch because both receivers are live. " +
    "The path-less endpoint detail matters: the SDK appends /v1/traces, /v1/metrics, /v1/logs itself, so you configure the base once.");
}

// ── 2. Fundamentals — diagram fig-02 ─────────────────────────────────────────
{
  const s = S();
  addDiagramSlide(s, "FOUNDATIONS · FUNDAMENTALS",
    "One SDK, one Collector, three backends, one UI",
    "fig-02-otel-data-path",
    "Figure 2.1 — The app's SDK exports OTLP to the Collector, which routes traces → Tempo, metrics → Mimir, logs → Loki, all viewed in Grafana.");
  addNotes(s,
    "This is the spine of the whole talk; the same SVG appears in the tutorial as Figure 2.1. Trace the left-to-right flow: in-process SDK produces all three signals, exports once over OTLP to the Collector. " +
    "The Collector has three internal stages — receivers accept OTLP, processors act on the stream in order (memory_limiter, batch, later a sampler), exporters fan out to the three backends. " +
    "Grafana reads all three and links them because they share identifiers. The key teaching point: the app emits everything; the Collector decides what survives. That separation is why sampling and routing can change without touching app code.");
}

// ── 2b. Three signals ────────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · FUNDAMENTALS", "Three signals, three questions");
  addBullets(s, [
    "A trace answers where did the time go, and what happened along the way — a tree of spans sharing one trace_id, each with a duration, attributes, and a parent. One trace should span the REST request, both gRPC calls, the Postgres writes, the Kafka publish, and the shipping and notification consumers.",
    "A metric answers how much, how often, how slow — in aggregate. Cheap numbers over time: request rate, error rate, duration percentiles. Small enough to keep for everything, always — which is what alerts fire on.",
    "A log answers what exactly happened at this instant — a timestamped, ideally structured record carrying the detail a metric averages away and a span has no room for.",
  ], { fontSize: 16 });
  addCaption(s, "The trap is treating them as three products; their strength is the hand-off between them.");
  addNotes(s,
    "Give the canonical hand-off story: the metric tells you error rate just spiked, the trace shows which hop is failing, the log line gives the exact exception. " +
    "That chain only works if all three carry the same identifiers — which is the entire reason to use one OpenTelemetry SDK rather than three unrelated libraries. " +
    "Emphasize the trace_id as the thread running through all of it. Keep this conceptual; the wiring comes next.");
}

// ── 2c. The data path ────────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · FUNDAMENTALS", "The OpenTelemetry data path");
  addBullets(s, [
    "OpenTelemetry splits producing telemetry from shipping it. In your process the SDK creates spans, records measurements, and emits logs, all stamped with a shared resource — the service.name, version, and environment that say who produced this.",
    "The SDK exports over OTLP to the Collector — the decision point. Receivers accept OTLP; processors act in order (a memory_limiter so a flood can't take the Collector down, a batch processor, later a sampler); exporters route traces → Tempo, metrics → Mimir, logs → Loki.",
    "Putting the Collector in the path lets sampling, batching, redaction, and routing be configured in one place, owned by whoever runs the platform, without touching application code.",
  ], { fontSize: 16 });
  addNotes(s,
    "This slide narrates Figure 2.1 in words. The resource is easy to skip but important — it is the identity stamped on every signal, the thing that lets Grafana group everything from one service. " +
    "Processor ORDER matters: memory_limiter first so you protect the Collector before doing anything expensive, batch to ship efficiently, sampler later once we get there. " +
    "Land the punchline: the application emits everything; the Collector decides what survives. That is the whole argument for a Collector instead of exporting straight to each backend.");
}

// ── 2d. Shared context ───────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · FUNDAMENTALS", "Why the shared context is the point");
  addBullets(s, [
    "Context propagation is what makes this one system, not three. When a span is active the SDK can stamp its trace_id and span_id onto log records emitted in the same breath, and attach an exemplar — a pointer back to a representative trace — onto a metric.",
    "The hard part, and the part most material skips: keeping that context alive across a boundary that is not a function call. When the order service publishes order.placed to Kafka, the shipping and notification consumers are different processes with no shared call stack.",
    "Unless the trace context travels with the message, each consumer starts a brand-new trace and the chain breaks in the middle. Carrying it across that hop is the job of the custom-instrumentation chapter.",
  ], { fontSize: 16 });
  addNotes(s,
    "This is the thesis statement for the second half of the talk. Make the audience feel the problem before we solve it: an in-process call shares context for free through the call stack, and gRPC carries it in a header automatically, but a Kafka message is just bytes — the trace context is not in those bytes unless you put it there. " +
    "Plant the flag now: the single trace_id flowing through every hop is the foundation everything else is built on, and the Kafka hop is where it is easiest to lose. We will fix it explicitly later with a propagator that writes context into message headers.");
}

// ── 3. Example services — diagram fig-03 ───────────────────────────────────
{
  const s = S();
  addDiagramSlide(s, "FOUNDATIONS · THE EXAMPLE SERVICES",
    "One order, five protocols, six services",
    "fig-03-service-topology",
    "Figure 3.1 — POST /orders fans out: gRPC to inventory + payment, Postgres, Kafka order.placed → shipping + notification; review serves GraphQL.");
  addNotes(s,
    "Same SVG as Figure 3.1 in the tutorial. Walk the fan-out with your finger: a client POSTs to the order service; order calls inventory and payment over gRPC, writes Postgres, and publishes order.placed to Kafka; shipping and notification each consume that event; review answers a GraphQL read. " +
    "The cast is a small set of familiar e-commerce services — order, inventory, payment, shipping, notification, review — run on Podman compose, not Kubernetes, because this is an OpenTelemetry talk. The names are borrowed from a separate data-mesh reference project; here they are just realistic domains to instrument. " +
    "The teaching point: five protocols means five places a trace can continue or break. Auto-instrumentation will carry it across REST and gRPC for free; the Kafka hop is the one we wire by hand later.");
}

// ── 3b. The one request ──────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · THE EXAMPLE SERVICES", "The one request the whole talk follows");
  addBullets(s, [
    "POST /orders on the order service is the action everything hangs off. In sequence: reserve stock (gRPC → inventory), authorize payment (gRPC → payment), persist the order (Postgres), publish order.placed (Kafka), return the confirmed order.",
    "Two services react asynchronously: shipping consumes the event and writes a shipment; notification consumes the same event and sends a message. A separate review service exposes a GraphQL read API over orders and reviews.",
    "That is REST at the edge, gRPC between services, Kafka for the async fan-out, Postgres underneath, and GraphQL on the read side — one workflow, five protocols, all of which a single trace must stay whole across.",
  ], { fontSize: 16 });
  addCaption(s, "Reserve before you charge, charge before you promise, promise before you announce.");
  addNotes(s,
    "Set up the order of operations as deliberate, not arbitrary: you reserve stock before charging, charge before confirming, confirm before announcing — so a failure at any step leaves the system consistent and the customer correctly informed. " +
    "The order service short-circuits with a 409 if stock can't be reserved and a 402 if payment declines, writing a row with the reason either way so failures are visible. This is the spine the next slides instrument.");
}

// ── 3c. The shared obs library ───────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · THE EXAMPLE SERVICES", "One shared library carries all the telemetry");
  addBullets(s, [
    "Every service depends on a small package, obs (services/common/), so the instrumentation story is identical everywhere and lives in one reviewable place — application code stays clean.",
    "obs.otel.setup(name) builds the resource, the OTLP/HTTP exporters for all three signals, the W3C propagator, and turns on auto-instrumentation for FastAPI, gRPC, and asyncpg.",
    "obs.kafka / obs.kafka_propagation publish JSON events and carry trace context across Kafka; obs.db is one asyncpg pool; obs.logging emits trace-stamped JSON. In Foundations none of it is switched on yet (OTEL_SDK_DISABLED=true).",
  ], { fontSize: 16 });
  addNotes(s,
    "The point of a shared obs package is that the talk can show the SAME setup() call in every service rather than six slightly different bootstraps. It is also what makes the no-telemetry baseline a one-variable change: setup() checks OTEL_SDK_DISABLED first and returns no-op providers when it is true. " +
    "Name the four submodules so the audience has a map for the chapters that follow: otel (the bootstrap), kafka/kafka_propagation (the async hop), db (the pool), logging (correlated logs).");
}

// ── 3d. order handler (code) ─────────────────────────────────────────────────
{
  const s = S();
  addCodeSlide(s, "FOUNDATIONS · THE EXAMPLE SERVICES", "The order handler — the spine", "python · FastAPI",
    [
      "@app.post(\"/orders\")",
      "async def create_order(body: CreateOrder) -> dict:",
      "    order_id = str(uuid.uuid4())",
      "    amount_cents = UNIT_PRICE_CENTS * body.quantity",
      "    # 1. reserve stock (gRPC → inventory; auto-traced)",
      "    reservation = await app.state.clients.reserve(order_id, body.sku, body.quantity)",
      "    if not reservation.reserved:",
      "        raise HTTPException(409, \"insufficient stock\")",
      "    # 2. authorize payment (gRPC → payment; auto-traced)",
      "    auth = await app.state.clients.authorize(order_id, body.customer_id, amount_cents)",
      "    if not auth.authorized:",
      "        raise HTTPException(402, f\"payment declined: {auth.decline_reason}\")",
      "    # 3. persist (Postgres)   4. announce (Kafka, context in headers)",
      "    await repo.insert_order(order_id, ..., status=\"confirmed\")",
      "    await obskafka.publish_event(app.state.producer, ORDER_PLACED_TOPIC,",
      "                                 key=order_id, value={...})",
      "    return {\"order_id\": order_id, \"status\": \"confirmed\"}",
    ],
    "Two gRPC calls, a Postgres write, a Kafka publish — and not one line of tracing code.",
    { fontSize: 10 });
  addNotes(s,
    "The thing to point at is what is NOT here: no spans, no trace ids, no propagation. The handler reads as plain business logic — reserve, authorize, persist, announce — and yet by the next part it produces a full trace across two processes. " +
    "That is the payoff of auto-instrumentation plus the obs library: the gRPC client calls and the Postgres queries instrument themselves; the only deliberately-instrumented hop is the Kafka publish, and even that is hidden inside obskafka.publish_event. Stress the short-circuits: 409 on stock, 402 on payment — those give us repeatable error traces later.");
}

// ── 3e. inventory Reserve (code) ─────────────────────────────────────────────
{
  const s = S();
  addCodeSlide(s, "FOUNDATIONS · THE EXAMPLE SERVICES", "A gRPC service — inventory.Reserve", "python · grpc.aio + asyncpg",
    [
      "class InventoryServicer(inventory_pb2_grpc.InventoryServiceServicer):",
      "    async def Reserve(self, request, context):",
      "        pool = await db.get_pool()",
      "        # atomic check-and-decrement: only succeeds if enough on hand",
      "        remaining = await pool.fetchval(",
      "            \"UPDATE stock SET on_hand = on_hand - $2 \"",
      "            \"WHERE sku = $1 AND on_hand >= $2 RETURNING on_hand\",",
      "            request.sku, request.quantity)",
      "        if remaining is None:",
      "            return inventory_pb2.ReserveResponse(reserved=False)",
      "        reservation_id = str(uuid.uuid4())",
      "        await pool.execute(\"INSERT INTO reservations ...\", reservation_id, ...)",
      "        return inventory_pb2.ReserveResponse(reserved=True,",
      "            reservation_id=reservation_id, remaining=remaining)",
    ],
    "Contracts are shared protos at proto/shop/…; the gRPC server instrumentation continues the order's trace.",
    { fontSize: 10 });
  addNotes(s,
    "Two things to land. First, the single conditional UPDATE … WHERE on_hand >= qty RETURNING on_hand both checks and decrements stock atomically — no read-then-write race — and returns NULL when there isn't enough, which is how Reserve signals failure. A reservation row keyed by order_id makes a retry idempotent. " +
    "Second: this runs in a DIFFERENT process from the order service, yet because the gRPC server is auto-instrumented and the order service injected context on the wire, these spans and their Postgres children land under the order's trace. The proto that defines this service lives once at the repo top level and is compiled into the image.");
}

// ── 3f. The fragile bits ─────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · THE EXAMPLE SERVICES", "The fragile bits, named not hidden");
  addBullets(s, [
    "Every domain shares one Postgres database (appdb) for laptop simplicity; a production system might isolate a store per domain. The observability story — a Postgres span per service under one trace — is identical either way.",
    "The payment ceiling and the catalog unit price are hardcoded so demos are deterministic: a fixed amount authorizes, a large quantity declines, on demand.",
    "Kafka auto-creates the order.placed topic; production would create topics explicitly with chosen partition counts. None of these change the spans or metrics — they are scope cuts, stated out loud.",
  ], { fontSize: 16 });
  addNotes(s,
    "Naming the simplifications buys credibility and heads off the 'but what about…' questions. The one most likely to be challenged is the shared database — be ready to say that per-domain stores are the production ideal but co-locating them changes nothing about the telemetry, which is what this talk is about. Keep the focus on observability.");
}

// ── 3g. Run it — it's opaque ─────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · THE EXAMPLE SERVICES", "It works — and it is completely opaque");
  addBullets(s, [
    "cd examples/01-no-telemetry && ./demo.sh — brings the whole stack up in Podman with telemetry disabled and places one order.",
    "Expect a confirmed order in the response, a shipment row, and a notification log — proof the request travelled the full chain across REST, gRPC, Kafka, and Postgres.",
    "Then open Grafana and look for it. There is nothing there. Six services just collaborated to fulfil that order and you cannot see any of it — exactly the opacity the rest of the talk removes.",
  ], { fontSize: 16 });
  addCaption(s, "This is the baseline: no telemetry. Every later demo is measured against this opacity.");
  addNotes(s,
    "The emotional pivot of the foundation: the system works perfectly and tells you nothing. Run it, show the confirmed response, then pull up an empty Grafana and let the silence land. " +
    "Demo 1 ships with OTEL_SDK_DISABLED=true on purpose; the next part flips one variable and the same request lights up.");
}

// ════════════════════════════════════════════════════════════════════════════
divider("THE THREE SIGNALS", "Traces, metrics, logs — and the thread that ties them",
  "Auto-instrumentation · Metrics · Logs · Custom spans across Kafka",
  "This part turns the SDK on and adds one signal at a time to the exact same code, ending by carrying trace context across the Kafka hop so the async work rejoins the trace.");

// ── 4. Auto-instrumentation — diagram fig-04 ─────────────────────────────────
{
  const s = S();
  addDiagramSlide(s, "THE THREE SIGNALS · AUTO-INSTRUMENTATION",
    "Auto, custom, and the hybrid you actually ship",
    "fig-04-instrumentation-layers",
    "Figure 4.1 — Auto-instrumentation gives breadth for free; custom spans give depth where it matters; real systems run both.");
  addNotes(s,
    "Frame the three columns. Auto-instrumentation is breadth for free: turn it on and FastAPI, gRPC, and asyncpg emit spans with no code change. Custom instrumentation is depth where it matters: you open spans for the work the libraries can't see. The hybrid is what every real service is — and the one gotcha is the occasional duplicate span when auto and custom overlap. " +
    "This part starts with the free breadth, then earns the depth in the Kafka chapter.");
}

// ── 4b. setup() (code) ───────────────────────────────────────────────────────
{
  const s = S();
  addCodeSlide(s, "THE THREE SIGNALS · AUTO-INSTRUMENTATION", "Turn it on once, in the shared library", "python · obs.otel.setup",
    [
      "resource = Resource.create({",
      "    \"service.name\": cfg.service_name,    # the most important attribute",
      "    \"service.version\": cfg.service_version,",
      "    \"deployment.environment\": cfg.environment})",
      "",
      "tracer_provider = TracerProvider(resource=resource)",
      "tracer_provider.add_span_processor(",
      "    BatchSpanProcessor(OTLPSpanExporter(f\"{cfg.endpoint}/v1/traces\")))",
      "trace.set_tracer_provider(tracer_provider)",
      "# … MeterProvider + LoggerProvider wired the same way …",
      "",
      "AsyncPGInstrumentor().instrument()        # every query → a span",
      "GrpcAioInstrumentorClient().instrument()  # inject context on the wire",
      "GrpcAioInstrumentorServer().instrument()  # extract it on arrival",
    ],
    "service.name is what lets Grafana say 'this span happened in payment'; BatchSpanProcessor keeps export off the critical path.",
    { fontSize: 10 });
  addNotes(s,
    "Three beats. The resource is the identity stamped on every signal — service.name is the single most important attribute in the whole system, which is why we pass it explicitly rather than trust a default. The Batch processor ships spans on a background thread, so observing the service never slows the request. " +
    "And the three instrument() calls are the whole of 'auto': each patches its library process-wide, so the order handler we saw earlier — with no tracing in it — now produces gRPC and Postgres spans automatically. FastAPI is the exception, instrumented against the app object via instrument_fastapi(app).");
}

// ── 4c. The boundary where it stops ──────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "THE THREE SIGNALS · AUTO-INSTRUMENTATION", "One trace for free — until Kafka");
  addBullets(s, [
    "Place an order, open Tempo: one trace spans the POST /orders server span, the inventory and payment gRPC client+server spans, and every asyncpg query — none of it written by hand.",
    "Context crosses HTTP and gRPC because the instrumented client writes a traceparent header and the server reads it — the W3C Trace Context standard, propagated automatically.",
    "But the shipping and notification work shows up as separate, parentless traces. A Kafka message has no one filling in a traceparent for you, so the chain breaks at the broker. Demo 2 runs with propagation off to make that visible; Chapter 7 fixes it.",
  ], { fontSize: 16 });
  addNotes(s,
    "This is the honest edge of auto-instrumentation and the hook for the rest of the part. Show the beautiful free trace first, then deliberately point at what's missing: the consumers are off on their own. Resist the urge to hand-wave — name why (no instrumented client owns the Kafka publish header) so the fix in Chapter 7 feels inevitable rather than magic.");
}

// ── 5. Metrics ───────────────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "THE THREE SIGNALS · METRICS", "RED, mostly for free — and exemplars back to traces");
  addBullets(s, [
    "RED — Rate, Errors, Duration — is the default question set for a request-driven service: is it busy, is it broken, is it slow? The HTTP and gRPC auto-instrumentation emits most of it already, labelled by route, method, and status.",
    "Metrics are periodic aggregates, not per-event records: a MeterProvider with a PeriodicExportingMetricReader samples in-memory aggregations and exports them on an interval — the fundamental difference from a span.",
    "Exemplars are the payoff: a sample trace_id attached to a histogram bucket when the measurement was taken inside a span. Grafana renders them as dots on the latency graph; click one to open the actual slow trace in Tempo.",
  ], { fontSize: 16 });
  addCaption(s, "Cross-check: the request count per minute should match the number of order traces for the same window.");
  addNotes(s,
    "The single most valuable idea on this slide is exemplars — they turn 'p99 spiked at 14:32' from a dead end into 'here is a request that was actually slow.' That only works because the same SDK with the same resource emits both signals, so the ids line up. " +
    "Mention that domain questions ('how many orders declined for payment?') need a custom Counter you define with obs.otel.meter(); the transport metrics cover RED but not the business.");
}

// ── 6. Logs (code) ───────────────────────────────────────────────────────────
{
  const s = S();
  addCodeSlide(s, "THE THREE SIGNALS · LOGS", "Stamp every line with the active trace", "python · obs.logging",
    [
      "class TraceContextFilter(logging.Filter):",
      "    def filter(self, record):",
      "        span = trace.get_current_span()",
      "        ctx = span.get_span_context() if span else None",
      "        if ctx and ctx.is_valid:",
      "            record.trace_id = format(ctx.trace_id, \"032x\")",
      "            record.span_id = format(ctx.span_id, \"016x\")",
      "        else:",
      "            record.trace_id = record.span_id = \"-\"",
      "        return True   # a JsonFormatter then renders these as fields",
    ],
    "JSON + the trace_id on every record = a log in Loki links to its trace in Tempo, and back. The ids are the join key.",
    { fontSize: 11 });
  addNotes(s,
    "Two decisions make logs correlatable: structure (JSON, so trace_id is a queryable field, not buried in a string) and the trace context on every record. A logging Filter is the right hook because it runs at log time, so inside a request the ids are the request's ids and outside one they're '-'. " +
    "The hex formatting (032x / 016x) is the canonical form Tempo expects, so the value in Loki matches the trace exactly. Services log to stdout; the collector routes it to Loki, so the service stays ignorant of the backend.");
}

// ── 7. Custom spans across Kafka — diagram fig-07 ────────────────────────────
{
  const s = S();
  addDiagramSlide(s, "THE THREE SIGNALS · CUSTOM SPANS",
    "Carrying the trace across the Kafka boundary",
    "fig-07-context-propagation",
    "Figure 7.1 — gRPC propagates context for you; across Kafka you inject it into the message headers and extract it in the consumer.");
  addNotes(s,
    "This is the climax of the talk and the technique that generalises: anywhere context doesn't propagate automatically — a queue, a batch job, a custom protocol — you do exactly this. Walk the figure: the producer injects the active context into the Kafka message headers; the consumer extracts it and opens its processing span with that context as the parent. " +
    "The same traceparent the gRPC hop used, just placed and read by hand because no library does it for a Kafka message.");
}

// ── 7b. inject / extract / consume (code) ────────────────────────────────────
{
  const s = S();
  addCodeSlide(s, "THE THREE SIGNALS · CUSTOM SPANS", "Inject on publish, extract on consume", "python · obs.kafka_propagation",
    [
      "# producer side — inject the active context into Kafka headers",
      "def inject_headers(existing=None):",
      "    carrier = {}; propagate.inject(carrier)   # writes 'traceparent'",
      "    return [(k, v.encode()) for k, v in carrier.items()]",
      "",
      "# consumer side — rebuild the context, then parent the span to it",
      "ctx = extract_context(msg.headers)",
      "with otel.tracer().start_as_current_span(",
      "        \"shipping.handle_order_placed\", context=ctx):",
      "    await create_shipment(order)   # this span is now a child of the order",
    ],
    "context=ctx is the entire trick: without it the consumer starts a new trace; with it, it joins the order's.",
    { fontSize: 11 });
  addNotes(s,
    "Slow down on context=ctx — it is the whole chapter in one argument. propagate.inject is the same call the HTTP and gRPC instrumentors make internally; we do it explicitly only because no library will do it for a Kafka message. extract_context returns a context value, not an active one; passing it as context= to start_as_current_span is what makes the consumer's span a child of the order service's publish span, in a different process, reached asynchronously. " +
    "The asyncpg span for create_shipment then nests under that automatically. Two lines per consumer — extract, then pass context= — and the async hop is whole.");
}

// ── 7c. GraphQL resolver spans ───────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "THE THREE SIGNALS · CUSTOM SPANS", "Same API, a second use: GraphQL shape");
  addBullets(s, [
    "The review service uses the same start_as_current_span call for a different reason — not to cross a boundary, but to make one opaque POST /graphql legible.",
    "Each resolver opens a span (review.resolve_order, review.resolve_reviews), so a GraphQL query shows up as a resolver tree with its Postgres children — not a single span you can't see inside.",
    "Once you can open a span deliberately, you can give any custom work — resolvers, batch steps, scheduled jobs — the structure it deserves. That is the general lesson under the specific Kafka fix.",
  ], { fontSize: 16 });
  addCaption(s, "Run examples/05-spans-across-kafka and compare the trace to Demo 2: the consumers are now on it.");
  addNotes(s,
    "Close the part by generalising: start_as_current_span is not a Kafka tool, it is THE tool for making invisible work visible — the Kafka consumers and the GraphQL resolvers are two faces of the same move. End on the side-by-side: Demo 2's trace stopped at the broker; Demo 5's runs all the way through shipping and notification. Same code, one env var, the whole picture.");
}

// ── 8. Auto, custom, hybrid — the cost ───────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "THE THREE SIGNALS · HYBRID", "Auto, custom, hybrid — and what each costs");
  addBullets(s, [
    "Auto-instrumentation is breadth for free: every request, RPC, and query becomes a span with no code. The cost is volume you pay to export, store, and read, and blind spots — it sees nothing no instrumented library owns (the Kafka hop, a GraphQL resolver, the business meaning).",
    "Custom spans are depth where you decide: your names, your attributes (order_id, decline reason), wrapping work no instrumentor sees. The cost is code you maintain — so you spend it on the message boundary and the resolver, not on HTTP.",
    "Hybrid — auto everywhere, custom in the gaps — is the production default, and it is what this repo already runs. Two rules keep it cheap: instrument any one boundary once (two near-identical spans = double-instrumentation), and keep high-cardinality ids on spans, never on metric labels.",
  ], { fontSize: 15 });
  addCaption(s, "Demo 6 shows both layers in one trace; compare it to Demo 2 with the custom layer off.");
  addNotes(s,
    "This is the slide the senior engineers in the room are waiting for: the honest cost/benefit. Auto is not free — it is volume and it is library-shaped. Custom is not noble — it is maintenance you ration. The hybrid is the only realistic answer, and the two failure modes worth naming out loud are double-instrumenting one boundary (the duplicate-span smell) and shoving an unbounded id like order_id into a metric label, which is how an observability bill becomes a horror story. " +
    "Identifiers belong on spans, where one-per-request is already the shape; metrics get bounded labels — route, method, status.");
}

// ── 9. The correlated view — diagram fig-11 ──────────────────────────────────
{
  const s = S();
  addDiagramSlide(s, "THE THREE SIGNALS · CORRELATED VIEW",
    "Read one request across all three signals",
    "fig-11-correlation-graph",
    "Figure 9.1 — One trace_id links a trace in Tempo to its logs in Loki and its metrics in Mimir; the pivots are one click.");
  addNotes(s,
    "This is the payoff slide — open Grafana and actually use the correlation. Walk the four moves live if you can. (1) In Tempo, a trace read top-down IS the distributed business flow — the path across services with a duration on each hop, and on a failed order the error sits on the Authorize span with the decline reason as an attribute. " +
    "(2) From a span, 'Logs for this span' jumps by trace_id to exactly that service's lines in Loki — no grep, no window-guessing. (3) From a p99 bump in Mimir, an exemplar dot opens the slow trace behind it. (4) The gap between a gRPC client span and its server span is wire + serialization time, with message sizes on the spans — the serde cost read straight off the trace. " +
    "All four pivot on one trace_id flowing through every hop. That movement between signals is the whole point; it is what a wall of disconnected logs can never give you.");
}

// ── Closing / roadmap ────────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "THE THREE SIGNALS", "Where this goes next");
  addBullets(s, [
    "You now have the full correlation story across the services: traces across REST and gRPC for free, metrics with exemplars, logs stamped with the trace_id, custom spans that carry the trace across Kafka, the honest auto/custom/hybrid trade-off, and a Grafana walkthrough that pivots trace → logs → metrics on one click.",
    "Next part — the pipeline: move the costly decisions into the Collector. Where sampling happens, what it costs to keep telemetry at volume, and continuous profiling.",
    "Iteration r1.1 ships Sections 0–9, the six example services, the shared protos and obs library, and Demos 1–7. The Collector-side pipeline demos land in r2.0; see the iteration plan in the repo.",
  ], { fontSize: 15 });
  addNotes(s,
    "Re-walk the arc so the audience knows what they hold and what's coming. The foundation gave them the services and the model; this part gave them the three correlated signals, the cost of getting them, and the one-click view that ties them together; the pipeline part is about keeping all of it affordable at volume. " +
    "Be honest about iteration state: r1.1 is authored against the target versions but not yet run end-to-end here, so it ships marked unverified, and a live rehearsal against the real stack is the next milestone. Point people at the repo: the tutorial mirrors these slides chapter for chapter, and every example has a runnable demo.sh.");
}

pres.writeFile({ fileName: OUT })
  .then(p => console.log("WROTE", p, "slides:", pageNum))
  .catch(e => { console.error(e); process.exit(1); });

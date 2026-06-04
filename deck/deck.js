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

const OUT = "/mnt/user-data/outputs/otel-lgtm-python-r01.0.pptx";
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
  s.addText("OpenTelemetry and the self-hosted Grafana LGTM stack — traces, metrics, and logs from one SDK, correlated across an async Kafka round trip.", {
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
  "This first part lays the groundwork: what the talk covers and how it is delivered, the tools and the running backend, the conceptual model of the three signals, and a close read of the demo application. No instrumentation yet — we earn that by first understanding the system we are about to make transparent.");

// ── 0. What this talk is ─────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · OUTLINE", "One small service, made fully observable");
  addBullets(s, [
    "The running example is small but complete: a FastAPI service that takes a request, sends it across Kafka to a separate worker, which reads and writes Postgres, and replies across Kafka — one async round trip.",
    "Over the talk that service grows traces, metrics, and logs from a single OpenTelemetry SDK, all correlated in Grafana, with a Collector in the path making the sampling and routing decisions.",
    "The backend is the open-source Grafana LGTM stack — Loki for logs, Grafana to view, Tempo for traces, Mimir for metrics — running locally under Podman. No paid accounts, no managed cloud on the path.",
  ], { fontSize: 17 });
  addNotes(s,
    "Frame the whole arc here. The service is deliberately a realistic shape — a request that does not finish in one process. " +
    "That async round trip is the reason the demo earns its keep: context has to survive a message broker, not just an in-process call, which is exactly where correlation usually breaks. " +
    "LGTM is the mnemonic: Loki, Grafana, Tempo, Mimir. Stress that everything is self-hosted and vendor-neutral — mapping it to a managed service later is the audience's to do, not ours.");
}

// ── 0b. The arc ──────────────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · OUTLINE", "The arc, in three parts");
  addStatusTable(s, [
    { code: "Foundations",       name: "the stack, the signals, the app", purpose: "Outline · Prerequisites · Fundamentals · The demo app" },
    { code: "The three signals", name: "traces, metrics, logs — and correlation", purpose: "Auto-instrumentation · Metrics · Logs · Custom spans across Kafka" },
    { code: "The pipeline",      name: "the Collector and the payoff", purpose: "The hybrid approach · Sampling · Profiling · The correlated view" },
  ], { colW: [2.55, 4.20, 5.34], rowH: 0.95 });
  addCaption(s, "Foundations is this part; the three signals and the pipeline are the two halves that follow.");
  addNotes(s,
    "Walk the three parts left to right. Part one (today's foundation iteration) is conceptual and structural. " +
    "Part two adds each signal in turn and ends on carrying trace context across the Kafka hop — the hard, interesting bit. " +
    "Part three moves the sampling and routing decisions into the Collector and lands on the correlated view, where one click pivots metric → trace → log. " +
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
    "The right column manages expectations: assume working knowledge of the four technologies. If the audience is shaky on Kafka, flag the request/reply pattern as the one thing to watch and move on. " +
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
    "A trace answers where did the time go, and what happened along the way — a tree of spans sharing one trace_id, each with a duration, attributes, and a parent. One trace should span the HTTP request, the Kafka publish, the worker, Postgres, and the reply.",
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
    "The hard part, and the part most material skips: keeping that context alive across a boundary that is not a function call. When the API hands work to the worker over Kafka, that worker is a different process with no shared call stack.",
    "Unless the trace context travels with the message, the worker starts a brand-new trace and the chain breaks in the middle. Carrying it across that hop is the job of the custom-instrumentation chapter.",
  ], { fontSize: 16 });
  addNotes(s,
    "This is the thesis statement for the second half of the talk. Make the audience feel the problem before we solve it: an in-process call shares context for free through the call stack, but a Kafka message is just bytes — the trace context is not in those bytes unless you put it there. " +
    "Plant the flag now: the single trace_id flowing through every hop is the foundation everything else is built on, and the Kafka hop is where it is easiest to lose. We will fix it explicitly later with a propagator that writes context into message headers.");
}

// ── 3. Demo app — diagram fig-03 ─────────────────────────────────────────────
{
  const s = S();
  addDiagramSlide(s, "FOUNDATIONS · THE DEMO APP",
    "One request, there and back again",
    "fig-03-app-topology",
    "Figure 3.1 — Client → FastAPI → Kafka requests → worker → Postgres → Kafka replies → FastAPI → client.");
  addNotes(s,
    "Same SVG as Figure 3.1 in the tutorial. Walk the round trip with your finger: client POSTs to /compute; FastAPI publishes to compute.requests and then waits; a separate worker consumes it, does a SELECT then an INSERT against Postgres, computes a result, and publishes to compute.replies; " +
    "FastAPI has been consuming replies the whole time, matches this one to the waiting request, and returns it. " +
    "Stress the two Kafka hops and the process boundary — that is precisely what the trace context must survive to stay one trace. This topology is why the demo is worth instrumenting.");
}

// ── 3b. Shape of the round trip ──────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · THE DEMO APP", "The shape of the round trip");
  addBullets(s, [
    "A client POSTs to /compute. FastAPI publishes the job to compute.requests and then waits for a reply.",
    "A separate worker process consumes that topic, reads a config row from Postgres, computes a result, writes a jobs row, and publishes the answer to compute.replies.",
    "The API has been consuming the reply topic the whole time; it matches the reply to the waiting request and returns it to the client.",
    "That request/reply-over-Kafka pattern is the reason this demo earns its keep: the trace context has to survive two message hops and a process boundary to stay one trace.",
  ], { fontSize: 17 });
  addNotes(s,
    "This is the prose version of the diagram — use it to set up the code that follows. The phrase to repeat is 'publishes, then waits': the HTTP call is synchronous from the caller's point of view, but underneath it is fire-and-forget messaging that we glue back together. " +
    "Everything in the talk's second half is about keeping that glue traceable. Now we look at the two structures that make the synchronous-over-async trick work.");
}

// ── 3c. PENDING + handler (code) ─────────────────────────────────────────────
{
  const s = S();
  addCodeSlide(s, "FOUNDATIONS · THE DEMO APP", "Synchronous HTTP over async messaging", "python · FastAPI",
    [
      "PENDING: dict[str, asyncio.Future] = {}   # request_id -> the reply we await",
      "",
      "@app.post(\"/compute\")",
      "async def compute(req: ComputeRequest) -> dict:",
      "    request_id = str(uuid.uuid4())          # the correlation key",
      "    fut = asyncio.get_running_loop().create_future()",
      "    PENDING[request_id] = fut",
      "    try:",
      "        await app.state.producer.send_and_wait(   # publish + broker ack",
      "            settings.requests_topic, key=request_id,",
      "            value={\"request_id\": request_id, \"n\": req.n})",
      "        reply = await asyncio.wait_for(fut, settings.reply_timeout_s)",
      "    except asyncio.TimeoutError:",
      "        raise HTTPException(504, \"worker did not reply in time\")",
      "    finally:",
      "        PENDING.pop(request_id, None)        # never leak a pending entry",
      "    return {\"request_id\": request_id, \"n\": req.n, \"result\": reply[\"result\"]}",
    ],
    "PENDING maps request_id → Future; the handler parks one, publishes, and awaits it.",
    { fontSize: 10 });
  addNotes(s,
    "Every line earns its place. request_id is generated before anything is sent — it is the correlation key, doing by hand exactly what the trace_id will do for free later. " +
    "send_and_wait publishes AND waits for the broker to acknowledge, so a publish failure surfaces here rather than silently dropping the request. The message key is the request_id, which keeps all messages for one request on one partition and in order. " +
    "asyncio.wait_for is the bridge from async messaging back to a blocking HTTP response: it suspends the handler until the reply consumer resolves the future, or gives up and returns 504 rather than hanging forever. " +
    "The finally pops the entry whatever happens, so PENDING cannot leak entries for timed-out requests. Call out the parallel to trace_id explicitly — this hand-rolled correlation is the thing OpenTelemetry will automate.");
}

// ── 3d. Reply consumer (code) ────────────────────────────────────────────────
{
  const s = S();
  addCodeSlide(s, "FOUNDATIONS · THE DEMO APP", "The reply consumer — the other half", "python · aiokafka",
    [
      "async def _consume_replies(app: FastAPI) -> None:",
      "    consumer = await make_consumer(settings.replies_topic,",
      "                                   group_id=\"compute-api\")",
      "    app.state.reply_consumer = consumer",
      "    async for msg in consumer:",
      "        data = msg.value",
      "        fut = PENDING.get(data.get(\"request_id\"))",
      "        if fut is not None and not fut.done():",
      "            fut.set_result(data)            # wakes up the waiting handler",
    ],
    "Started in the app's lifespan; one consumer resolves every in-flight request's future.",
    { fontSize: 11 });
  addNotes(s,
    "This background task is the only thing that resolves the futures the handler parks. For every reply it looks up the waiting future by request_id and sets its result, which wakes the suspended handler. " +
    "The not fut.done() guard avoids setting a result twice if a duplicate reply ever arrives. " +
    "Starting it once in lifespan rather than per request means a single consumer serves every in-flight request in this process, sharing the same event loop as the handlers. " +
    "This is the close of the loop opened on the previous slide — handler parks and awaits, consumer matches and resolves.");
}

// ── 3e. The worker (code) ────────────────────────────────────────────────────
{
  const s = S();
  addCodeSlide(s, "FOUNDATIONS · THE DEMO APP", "The worker — where the work happens", "python · aiokafka + asyncpg",
    [
      "async for msg in consumer:",
      "    data = msg.value",
      "    request_id = data[\"request_id\"]",
      "    n = int(data[\"n\"])",
      "    multiplier = await db.get_multiplier()        # SELECT config",
      "    result = (n * (n + 1) // 2) * multiplier       # triangular number",
      "    await db.record_job(request_id, n, result)    # INSERT a jobs row",
      "    await producer.send_and_wait(",
      "        settings.replies_topic, key=request_id,",
      "        value={\"request_id\": request_id, \"result\": result})",
    ],
    "A read-then-write Postgres round trip, then a reply keyed by the same request_id.",
    { fontSize: 11 });
  addNotes(s,
    "The worker consumes a job, does a read-then-write round trip against Postgres — a SELECT for the multiplier config, an INSERT to record the job — computes the triangular number n·(n+1)/2 times that multiplier, and publishes the reply keyed by the same request_id. " +
    "The database calls are deliberate, not incidental: they give the later chapters real database spans to capture, and a place to show that a span from the worker and a span from Postgres can belong to one trace. " +
    "The computation itself is intentionally trivial — a stand-in for real work, present so there is something to trace.");
}

// ── 3f. The fragile bits ─────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · THE DEMO APP", "The fragile bits, named not hidden");
  addBullets(s, [
    "Topics auto-create in this demo (KAFKA_AUTO_CREATE_TOPICS_ENABLE=true); a production setup would create them explicitly with chosen partition counts.",
    "PENDING lives in one process, so the request/reply trick assumes the API is not running as multiple replicas behind a load balancer — fine for a laptop demo, not for a fleet.",
    "The computation is intentionally trivial — a stand-in for real work, present so there is something to trace, not because triangular numbers are interesting.",
  ], { fontSize: 17 });
  addNotes(s,
    "Naming the simplifications out loud buys credibility and heads off the 'but what about…' questions. None of these change the observability story; they are scope cuts to keep a laptop demo a laptop demo. " +
    "If asked how you would make PENDING multi-replica-safe: you would push the correlation into a shared store or use a reply topic keyed per instance — but that is a distributed-systems talk, not this one. Keep the focus on telemetry.");
}

// ── 3g. Run it — it's opaque ─────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS · THE DEMO APP", "It works — and it is completely opaque");
  addBullets(s, [
    "cd examples/01-app-no-telemetry && ./demo.sh — builds the app image, brings the stack up, waits for healthy, and posts one request.",
    "Expect {\"request_id\":\"…\",\"n\":100,\"result\":5050}. Cross-check the database directly: a jobs row whose result matches proves the request travelled the full chain and did not short-circuit.",
    "Then open Grafana and look for this request. There is nothing there. The app is healthy and completely opaque — exactly the starting point the rest of the talk fixes.",
  ], { fontSize: 17 });
  addCaption(s, "This is the baseline: no telemetry. Every later demo is measured against this opacity.");
  addNotes(s,
    "This is the emotional pivot of the foundation. The service works perfectly and tells you nothing. Run the demo, show the clean 5050 response, then pull up an empty Grafana and let the silence land. " +
    "The cross-check via psql matters as a habit we will repeat: never trust the HTTP 200 alone — confirm the side effect. A jobs row with result 5050 for n=100 is the proof the whole chain ran. " +
    "Demo 1 ships with OTEL_SDK_DISABLED=true on purpose; the next part turns the SDK on and the same request lights up.");
}

// ── Closing / roadmap ────────────────────────────────────────────────────────
{
  const s = S();
  addContentTitle(s, "FOUNDATIONS", "Where this goes next");
  addBullets(s, [
    "Next part — the three signals: auto-instrumentation produces traces without changing a line of this code; then metrics, then logs stamped with the trace_id, then custom spans carried across the Kafka hop.",
    "After that — the pipeline: move sampling and routing into the Collector, add continuous profiling, and land on the correlated view where one click pivots metric → trace → log.",
    "Foundation iteration (r0.1) ships Sections 0–3, the demo app, the stack, and the six shared diagrams. Demos 2–9 land in r1.0 and r2.0; see the iteration plan in the repo.",
  ], { fontSize: 17 });
  addNotes(s,
    "Close by re-walking the arc so the audience knows what they have and what is coming. The foundation gives them the model and the un-instrumented service; the payoff is the correlated view at the very end. " +
    "Be honest about iteration state: this deck and tutorial are the foundation cut. The remaining demos are authored against the target versions but not yet run end-to-end here — they are marked unverified, and a live rehearsal against the real stack is the next milestone. " +
    "Point people at the repo: the tutorial site mirrors these slides chapter for chapter, and every example has a runnable demo.sh.");
}

pres.writeFile({ fileName: OUT })
  .then(p => console.log("WROTE", p, "slides:", pageNum))
  .catch(e => { console.error(e); process.exit(1); });

---
title: "Auto, custom, and hybrid"
order: 8
part: "The three signals"
description: "What auto-instrumentation gives you for free, what a hand-placed span gives you that it can't, where the two collide into duplicate work, and why production almost always runs both."
duration: 14 minutes
---

By now you have used both kinds of instrumentation without naming the choice.
Chapter 4 turned the SDK on and got traces across the synchronous hops for free;
Chapter 7 added hand-placed spans for the things the SDK could not see — the
Kafka hop and the GraphQL resolver tree. This chapter steps back to the decision
itself: auto, custom, or both, and what each one actually costs. "Instrument
everything automatically" is not free, and "instrument it all by hand" is not
realistic, so the honest answer is a deliberate mix — and knowing where to draw
the line is the skill.

The code is the same code you already have; this chapter reads it through the lens
of the three approaches and runs `examples/06-hybrid/` to see them side by side.

{% include excalidraw.html file="fig-04-instrumentation-layers" alt="Three columns: auto-instrumentation gives breadth for free; custom spans give depth where it matters; the hybrid runs both, and is the real-world default." caption="Figure 8.1 — Auto for breadth, custom for depth, hybrid for both" %}

## The three approaches, and what each one costs

**Auto-instrumentation — breadth, for free, library-shaped.** The instrumentors
patch FastAPI, gRPC, and asyncpg process-wide, so every request, every
service-to-service call, and every query becomes a span with standard attributes
and no code. What it costs: you get exactly what the library authors chose to
emit — transport and timing, not your business meaning — and you get *all* of it,
which is volume you pay to export, store, and read. And it is blind to anything no
instrumented library owns: a Kafka publish is just bytes, a GraphQL resolver is
just a function, and neither shows up until you say so.

**Custom spans — depth, exactly where you decide.** A hand-placed span carries
your names and your attributes — the `order_id`, the SKU, the decline reason — and
can wrap work no instrumentor will ever see. What it costs: you write it and you
maintain it, so you spend it where it earns its keep. Nobody hand-instruments
HTTP; you hand-instrument the message boundary and the resolver because that is
where the automatic story goes dark.

**Hybrid — auto for breadth, custom for the blind spots.** This is what every real
service runs, and it is exactly what this repo does: auto-instrumentation supplies
the request, gRPC, and database spans; the custom spans from Chapter 7 supply the
Kafka continuation and the resolver tree. Breadth where breadth is cheap, depth
where depth is worth paying for.

## How the code works

**The auto layer is three lines.** In `obs.otel.setup`, `AsyncPGInstrumentor()`,
`GrpcAioInstrumentorClient()`, and `GrpcAioInstrumentorServer()` each `.instrument()`
their library once, for the whole process; `instrument_fastapi(app)` does the same
for HTTP. After those calls, every order's REST → gRPC → Postgres path is traced
with no per-handler code — that is the breadth.

**The custom layer is a handful of `start_as_current_span` calls.** The shipping
and notification consumers open a span with the extracted Kafka context as its
parent; the review resolvers open `review.resolve_order` and `review.resolve_reviews`.
Each one exists because the auto layer cannot: there is no instrumented client to
carry context across Kafka, and a GraphQL POST is one opaque span until you open
the resolvers up. That is the depth.

**The hybrid seam — and the duplicate-span trap.** The two layers meet cleanly
here because they cover different work. The trap appears when they cover the
*same* work. If you enabled an automatic Kafka instrumentor *and* kept the manual
propagation from Chapter 7, one publish would produce two spans — the library's
and yours — nested with almost no time between them. The repo avoids that by
choosing one mechanism: it propagates across Kafka by hand and leaves automatic
Kafka instrumentation off. The general rule: instrument any one boundary once.
When you see two spans for a single operation with a near-zero gap, that is the
signature of double-instrumenting, and the fix is to disable one side, not to add
a third.

**The attribute-versus-label cost.** Custom spans let you attach high-cardinality
identifiers like `order_id` — and that is fine *on a span*, because a trace is
already one-per-request and the id rides along for free. The mistake that makes
observability "noisier and more expensive" is putting that same id on a *metric*
as a label: every distinct value forks a new time series, and an unbounded label
melts the metric backend. Identifiers belong on spans; metrics get bounded labels
like route, method, and status. Keeping that line is most of what separates a
useful telemetry bill from a frightening one.

## Build, run, observe

```bash
cd examples/06-hybrid && ./demo.sh
```

It runs the system fully instrumented and places a couple of orders. Open the
trace in Tempo and you can see both layers in one tree: the auto spans (the
`POST /orders` server span, the gRPC client and server spans, the asyncpg
queries) and the custom spans (the consumer spans under the Kafka hop, the
resolver spans under a GraphQL query). Then recall the Chapter 4 trace, where the
custom layer was off: the consumers had floated off into their own traces and the
GraphQL call was a single blind span. The difference between those two traces is
precisely the hybrid layer.

## Cross-check

Every span should have a home: an auto span maps to a library call (a route, an
RPC, a query), a custom span maps to a `start_as_current_span` in your code. If a
span belongs to neither — or if one operation shows two near-identical spans —
something is double-instrumented, and that is the cheapest performance and noise
win available: stop paying to record the same thing twice.

## What you learned

- Auto-instrumentation is breadth, free and library-shaped, at the cost of volume
  and blind spots; custom spans are depth and your own semantics, at the cost of
  code you maintain.
- The hybrid — auto everywhere, custom in the gaps — is the production default,
  and it is what this repo already runs.
- Instrument any one boundary once; keep high-cardinality identifiers on spans,
  never on metric labels.

Next, *Reading it in Grafana* opens the stack and follows one request across all
three signals, using the correlation you have now built.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm that the fully-instrumented trace shows both auto and
custom spans in one tree, that no operation is double-instrumented, and that the
metric pipeline carries no unbounded labels. Per-backend cardinality limits are
the detail most worth checking against your real volume.*

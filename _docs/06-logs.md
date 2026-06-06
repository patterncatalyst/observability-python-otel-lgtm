---
title: "Logs: stamped with the trace"
order: 6
part: "The three signals"
description: "Structured JSON logs carry the active trace_id and span_id, so a line in Loki links to its trace in Tempo and back — the ids are the join key."
duration: 12 minutes
---

Logs are the signal teams already have, and usually the least useful, because a
log line on its own tells you *what* happened but not *which request* it belonged
to. The fix is small and high-leverage: stamp every line with the active
`trace_id` and `span_id`. Once you do, a log in Loki links to its trace in Tempo,
a span in Tempo links to its logs, and the three signals finally describe one
thing instead of three disconnected ones. That join key is the whole idea of
this chapter.

The code is in `examples/04-logs/`; the logging setup is
`services/common/obs/logging.py`.

{% raw %}{% include excalidraw.html file="fig-06-log-correlation" alt="A request span's trace_id is stamped onto each log record; the stdout JSON is the console view while the SDK exports the same record over OTLP to the Collector and Loki, and Loki and Tempo link to each other by the shared trace_id." caption="Figure 6.1 — Stamp the trace_id onto every log, and Loki and Tempo point at each other" %}{% endraw %}

## Why structured, and why the ids

Two decisions make logs correlatable. First, **structure**: emit JSON, not free
text, so fields like `trace_id` are queryable rather than buried in a string
Grafana would have to parse. Second, **the trace context on every record**: the
ids that identify the current span, written as fields, so Loki's
derived-field configuration can turn `trace_id` into a link to Tempo. Neither is
useful without the other — structure with no trace id is just tidy logs; the id
with no structure is unsearchable.

## How the code works

`obs.logging.configure()` is three moving parts: a filter that adds the ids, a
formatter that renders JSON, and the handler wiring that puts them on the root
logger.

**The filter reads the active span.** A logging `Filter` runs on every record
before it is formatted, which is exactly the hook we want — it lets us enrich the
record with whatever is true *at log time*:

```python
class TraceContextFilter(logging.Filter):
    def filter(self, record):
        span = trace.get_current_span()
        ctx = span.get_span_context() if span else None
        if ctx and ctx.is_valid:
            record.trace_id = format(ctx.trace_id, "032x")
            record.span_id = format(ctx.span_id, "016x")
        else:
            record.trace_id = "-"
            record.span_id = "-"
        return True
```

`get_current_span()` reads the span from the current context — the same context
the SDK set when the request span started — so inside a request handler the ids
are the request's ids, and outside one they are `-`. The hex formatting (`032x`
for the 128-bit trace id, `016x` for the 64-bit span id) is the canonical
representation Tempo expects, so the value in the log matches the value in the
trace exactly. Returning `True` means "keep this record" — a filter can also drop
records, but here we only use it to enrich.

**The formatter renders JSON.** `JsonFormatter.format` builds a dict — timestamp,
level, logger name, message, and the two ids the filter attached — and
`json.dumps` it. Because the ids were set as record attributes, they are just
fields like any other; if an exception is attached, the formatted traceback goes
in too. One line of JSON per log event, with the trace id as a first-class field.

**Two sinks, one habit.** `configure()` builds a `StreamHandler` to stdout,
attaches the formatter and the filter, and replaces the root logger's handlers so
every module's logger inherits the behaviour. That stdout stream is the local
view — what `podman logs` shows — and the filter is what puts the `trace_id` on
those console lines. The path to Loki is the OpenTelemetry log signal: `setup()`,
called right after `configure()`, appends an SDK `LoggingHandler`, so the same
records are exported over OTLP to the Collector, which routes them to Loki. The
SDK stamps the active `trace_id`/`span_id` onto those OTLP records itself — doing
automatically for Loki what the filter does explicitly for the console — so the
correlation holds without anyone parsing a stdout line. A service calls
`obslog.configure()` once, before `otel.setup()`, and from then on every
`log.info(...)` is both readable on the console and a correlated record in Loki.

## Build, run, observe

```bash
cd examples/04-logs && ./demo.sh
```

Place an order and the script tails the order service logs — you will see JSON
lines each carrying a `trace_id`. In Grafana > Explore > Loki, filter
`{service_name="order"}`, expand a line, and use the `trace_id` link to jump into
Tempo. From a span there, pivot back to its logs. Same id, both directions.

## What you learned

- Correlatable logs need two things: JSON structure and the active
  `trace_id`/`span_id` on every record.
- A logging `Filter` is the right place to read the current span and enrich the
  record at log time; a `Formatter` renders it as queryable JSON.
- Logs reach Loki over the OpenTelemetry log signal (the SDK `LoggingHandler`),
  while stdout JSON stays the local console view — and the trace id, stamped on
  both, makes logs and traces link both ways.

Next, *Custom spans and the Kafka boundary* — the climax — closes the gap
Chapter 4 left open and makes the asynchronous consumers part of the same trace.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm order logs are JSON with a populated `trace_id` during a
request, the value matches the trace in Tempo, and Loki's derived field links to
it. Logs reach Loki over the OTLP log signal; the stack's Collector config (both
the base and the tail-sampling variant) carries an `otlp → loki` logs pipeline,
so this path is wired — it just hasn't been run end to end here.*

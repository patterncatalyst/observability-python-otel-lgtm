# OpenTelemetry talk demos

A set of terminal demos for *presenting* the OpenTelemetry talk to an audience.
Each demo narrates what it's about to do, **stops** so you can talk over the
command on screen, runs it live against the stack, and — crucially — **steps you
out to the browser** (Grafana / Tempo) to look at the result, because the payoff
of every signal is in the UI. Run them one at a time or back-to-back as a guided
walkthrough.

These are **not** the tutorial's `examples/`. The `examples/` are step-by-step,
copy-along build instructions for the Jekyll site. These `demos/` are
presenter-driven: they assume the stack is already up, drive real traffic, and
cue the browser excursions you'll do on stage. They share the same services and
stack, so they line up with `_docs/` and the slides.

## Running

```bash
./demos/run.sh           # interactive menu
./demos/run.sh all       # the full walkthrough, in order
./demos/run.sh 2         # just demo 2
./demos/run.sh check     # preflight: tools + stack reachability
./demos/run.sh list      # list the demos
```

Each demo is also runnable on its own:

```bash
./demos/01-trace-for-free.sh
```

The scripts use a `bash` shebang and run fine from a `zsh` prompt. The
**narrate → stop → run → step to the browser** rhythm is the whole interaction:
read what's on screen, press **Enter** to run it, drive the browser when cued,
press **Enter** to advance. To rehearse without stopping, set `DEMO_NO_PAUSE=1`.

## The demos

| # | Demo | What it shows | Browser stop |
|---|------|---------------|--------------|
| 1 | A trace for free | One order fans out over REST → gRPC → Postgres; the whole trace is auto-instrumented | Tempo: the span tree |
| 2 | The trace breaks at Kafka | Propagation OFF → the trace stops at the publish; ON → shipping/notification rejoin it | Tempo: orphaned vs connected |
| 3 | Metrics & exemplars *(planned)* | RED metrics from the same traffic; click an exemplar straight to a trace | Grafana: metric → trace |
| 4 | Correlated logs *(planned)* | JSON logs stamped with trace_id; pivot log ↔ trace both ways | Loki ↔ Tempo |
| 5 | The correlated view *(planned)* | One request, read across traces, logs, and metrics on one screen | Grafana Explore |
| 6 | Sampling *(planned)* | Tail sampling keeps errors, slow, and `/orders`; samples the healthy rest | Tempo: what survived |
| 7 | Profiling *(planned)* | The flame graph for a slow span — where the CPU went | Pyroscope (sketch) |
| 8 | The live service graph *(planned)* | The topology lighting up with live request/error rates | Grafana: node graph |

Demos 1–2 are in. The rest are being built out in this same style, beat for
beat with the talk; demos 7–8 depend on the profiling and service-graph stack
wiring (still unverified), so they'll cue those as the experimental/extended
features they are.

## Prerequisites

`podman`, `curl`, and `jq`, plus the stack running locally. Run
`./demos/run.sh check` to see what's on your `PATH` and whether the order
service and Grafana are answering.

**Before a talk:** bring the stack up, place a handful of warm-up orders so
Tempo and the dashboards aren't empty, and have Grafana open in a tab.

```bash
(cd stack && podman compose up -d)        # bring the backend + services up
./demos/run.sh check                       # confirm everything answers
```

## Endpoint overrides

The demos honor these; override any before launching:

```bash
GRAFANA_URL=http://localhost:3000          # where every demo ends
ORDER_URL=http://localhost:8080            # the REST edge the demos drive
REVIEW_URL=http://localhost:8081           # the GraphQL edge
```

## Notes for presenters

- **Nothing aborts on stage.** A slow request or a service still warming up
  degrades to a short note and the demo keeps going (`run_soft`); a decline that
  returns HTTP 402 is treated as the teaching point, not a failure (`run_fail`).
- **The browser is half the demo.** Each `🌐 Step out to the browser` cue gives
  you the URL and exactly what to point at. That's where you spend the time.
- **Demo 2 recreates services.** Toggling `PROPAGATE_KAFKA_CONTEXT` restarts the
  producer and the two consumers (a few seconds each way) — narrate over it.
- **Warm up first.** Place a few orders before you start so the first trace
  search isn't empty and the graphs have shape.
- **Self-cleaning.** Background load generators are killed when a demo exits.

## Verification status

**Unverified.** Syntax-checked and built to the tutorial's conventions, but not
yet run end to end against a live stack. Before an audience: `./demos/run.sh
check`, bring the stack up, warm it up, and rehearse `./demos/run.sh all` once.

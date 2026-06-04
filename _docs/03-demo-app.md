---
title: "The demo app and how it's built"
order: 3
part: "Foundations"
description: "A FastAPI service and a Kafka worker that make one request travel API → Kafka → worker → Postgres → Kafka → API."
duration: 12 minutes
---

Everything that follows instruments one small service, so it is worth
understanding it well before any telemetry is added. It is deliberately a
realistic shape: a request that does not finish in one process, but crosses an
async message boundary and a database before it comes back.

The code is in `examples/01-app-no-telemetry/` and the shared app under `app/`.
The run script there builds the stack and drives one request; its `README.md`
covers what it does and how to drive it.

{% raw %}{% include excalidraw.html file="fig-03-app-topology" alt="A client POSTs to FastAPI, which publishes to the Kafka requests topic; a consumer reads it, queries and writes Postgres, and publishes to the replies topic, which FastAPI consumes and returns to the client." caption="Figure 3.1 — One request, two Kafka hops, a database round trip, and back" %}{% endraw %}

## The shape of the round trip

A client `POST`s to `/compute`. The FastAPI service publishes the job to the
`compute.requests` topic and then *waits* for a reply. A separate worker process
consumes that topic, reads a config row from Postgres, computes a result, writes
a `jobs` row, and publishes the answer to `compute.replies`. The API has been
consuming that reply topic the whole time; it matches the reply to the waiting
request and returns it to the client.

That request/reply-over-Kafka pattern is the reason this demo earns its keep:
the trace context has to survive two message hops and a process boundary to stay
one trace. Everything in the talk's second half is about that.

## How the code works

### The two structures that make request/reply work

The API turns an asynchronous, fire-and-forget message system into a synchronous
HTTP call, and it does that with one structure:

```python
PENDING: dict[str, asyncio.Future] = {}
```

`PENDING` maps a `request_id` to a `Future` representing "the reply we are still
waiting for." When a request comes in, the handler creates a `Future`, parks it
in `PENDING` under a fresh `request_id`, publishes the job, and then `await`s the
`Future`. A background task consuming the reply topic is the only thing that
resolves those futures. The `request_id` is the key because it is unique per
in-flight request, so a reply can be matched back to exactly the call that
produced it — the same idea as the `trace_id` you will add later, doing by hand
what the trace context will do for free.

### The request handler, in full

```python
@app.post("/compute")
async def compute(req: ComputeRequest) -> dict:
    request_id = str(uuid.uuid4())
    loop = asyncio.get_running_loop()
    fut: asyncio.Future = loop.create_future()
    PENDING[request_id] = fut
    try:
        await app.state.producer.send_and_wait(
            settings.requests_topic,
            key=request_id,
            value={"request_id": request_id, "n": req.n},
        )
        try:
            reply = await asyncio.wait_for(fut, timeout=settings.reply_timeout_s)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="worker did not reply in time")
    finally:
        PENDING.pop(request_id, None)
    return {"request_id": request_id, "n": req.n, "result": reply["result"]}
```

Each line earns its place. The `request_id` is the correlation key, generated
before anything is sent. `send_and_wait` publishes the job and waits for the
broker to acknowledge it, so a publish failure surfaces as an error here rather
than silently dropping the request. The message `key` is the `request_id`, which
keeps all messages for one request on one partition and in order. The
`asyncio.wait_for` is the bridge from async messaging back to a blocking HTTP
response: it suspends the handler until the reply consumer resolves the future,
or gives up after a timeout and returns `504` rather than hanging forever. The
`finally` removes the entry whatever happens, so `PENDING` cannot leak entries
for requests that timed out.

### The reply consumer, the other half

```python
async def _consume_replies(app: FastAPI) -> None:
    consumer = await make_consumer(settings.replies_topic, group_id="compute-api")
    app.state.reply_consumer = consumer
    async for msg in consumer:
        data = msg.value
        fut = PENDING.get(data.get("request_id"))
        if fut is not None and not fut.done():
            fut.set_result(data)
```

This runs as a background task started in the app's `lifespan`. For every reply,
it looks up the waiting future by `request_id` and resolves it. The `not
fut.done()` guard avoids setting a result twice if a duplicate reply ever
arrives. Starting it in `lifespan` (rather than per request) means one consumer
serves every in-flight request in this process, sharing the same event loop as
the handlers.

### The worker, where the work happens

```python
async for msg in consumer:
    data = msg.value
    request_id = data["request_id"]
    n = int(data["n"])
    multiplier = await db.get_multiplier()       # SELECT
    result = (n * (n + 1) // 2) * multiplier
    await db.record_job(request_id, n, result)    # INSERT
    await producer.send_and_wait(
        settings.replies_topic, key=request_id,
        value={"request_id": request_id, "result": result},
    )
```

The worker consumes a job, does a read-then-write round trip against Postgres —
a `SELECT` for the multiplier config, an `INSERT` to record the job — computes
the triangular number `n·(n+1)/2` times that multiplier, and publishes the reply
keyed by the same `request_id`. The database calls are deliberate: they give the
later chapters real database spans to capture and a place to show that a span
from the worker and a span from Postgres can belong to one trace.

### The fragile bits, named not hidden

A few simplifications are worth calling out so they do not surprise you. Topics
auto-create in this demo (`KAFKA_AUTO_CREATE_TOPICS_ENABLE=true`); a production
setup would create them explicitly with chosen partition counts. `PENDING` lives
in one process, so the request/reply trick assumes the API does not run as
multiple replicas behind a load balancer — fine for a laptop demo, not for a
fleet. And the computation is intentionally trivial; it is a stand-in for real
work, present so there is something to trace, not because triangular numbers are
interesting.

## Build, run, observe

```bash
cd examples/01-app-no-telemetry && ./demo.sh
```

This builds the app image, brings the whole stack up, waits for the API to
report healthy, and posts one request. Expect:

```
{"request_id":"…","n":100,"result":5050}
```

Then open Grafana at <http://localhost:3000> and look for this request. There is
nothing there. The app is healthy and completely opaque — which is exactly the
starting point the next part fixes.

## Cross-check

Confirm the request actually exercised the database, rather than trusting the
HTTP response alone:

```bash
podman exec -it postgres psql -U appuser -d appdb -c \
  "SELECT request_id, n, result FROM jobs ORDER BY created_at DESC LIMIT 1;"
```

A row whose `result` matches the HTTP response confirms the request travelled the
full chain — API to worker to Postgres and back — and did not short-circuit.

## What you learned

- The service is an async request/reply over Kafka: the API publishes a job and
  waits; the worker does the work against Postgres and replies.
- A `request_id` parked in a `PENDING` future map is what turns fire-and-forget
  messaging back into a synchronous HTTP response — and foreshadows the
  `trace_id`.
- A healthy service is opaque by default; the gap between "it works" and "I can
  see why" is what the rest of the talk closes.

The next part starts closing it — with auto-instrumentation that produces traces
without changing a line of this code.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm the round trip completes and returns `result: 5050` for
`n=100`, a `jobs` row is written, and the app image builds on the chosen UBI
Python base. See `examples/01-app-no-telemetry/README.md`.*

---
title: "Custom spans across the Kafka boundary"
order: 7
part: "The three signals"
description: "Inject trace context into Kafka message headers and extract it in the consumer, so the async shipping and notification work rejoins the originating trace — plus custom resolver spans in GraphQL."
duration: 18 minutes
---

Chapter 4 got us one trace across the synchronous hops for free and then showed
it break at Kafka: the shipping and notification work landed in separate,
parentless traces. This chapter closes that gap, and it is the heart of the talk,
because the technique generalises — anywhere context does not propagate
automatically (a message queue, a batch job, a custom protocol), you do exactly
this by hand. We also use the same span API to give the GraphQL read path a
meaningful shape.

The code is in `examples/05-spans-across-kafka/`; the bridge is
`services/common/obs/kafka_propagation.py`, used by the producer in
`services/common/obs/kafka.py` and the consumers under `services/shipping` and
`services/notification`.

{% include excalidraw.html file="fig-07-context-propagation" alt="A trace context flows from the order span across a gRPC call (automatic, via traceparent header) and across a Kafka message (manual, via injected header) into a consumer span, with the consumer span shown as a child of the order span." caption="Figure 7.1 — gRPC propagates context for you; across Kafka you inject and extract it yourself" %}

## Why the boundary breaks, and the fix in one sentence

Automatic propagation works on HTTP and gRPC because the instrumented client
writes the active context into a `traceparent` header and the instrumented server
reads it. Kafka has message headers too, but nothing writes `traceparent` into
them for you — a published message is just a key, a value, and whatever headers
*you* attach. So the fix is: on the producer, serialise the active context into
the message headers; on the consumer, deserialise it and start your processing
span with it as the parent. Two operations, inject and extract, around the
exact same W3C context the gRPC hop used.

## How the code works

**Inject — serialise the active context.** `inject_headers` asks the global
propagator to write the current context into a plain dict (the "carrier"), then
turns that dict into the `list[tuple[str, bytes]]` shape aiokafka wants:

```python
def inject_headers(existing=None):
    headers = list(existing or [])
    if not _enabled():
        return headers
    carrier = {}
    propagate.inject(carrier)          # writes 'traceparent' into carrier
    headers.extend((k, v.encode("utf-8")) for k, v in carrier.items())
    return headers
```

`propagate.inject` is the same call the HTTP and gRPC instrumentors make
internally; we are just doing it explicitly because no library will do it for a
Kafka message. The `_enabled()` gate (the `PROPAGATE_KAFKA_CONTEXT` env var) is
what lets Demo 2 show the break and Demo 5 show the fix from one codebase — in
production you would simply always inject.

**Publish — inject at send time.** `obs.kafka.publish_event` calls it on the way
out so every event carries context without the caller thinking about it:

```python
async def publish_event(producer, topic, key, value):
    headers = kafka_propagation.inject_headers()
    await producer.send_and_wait(topic, key=key, value=value, headers=headers)
```

The order service calls this for `order.placed`; the context it injects is the
order request's context, because the publish happens inside the request span.

**Extract — rebuild the context on the other side.** `extract_context` reverses
inject: read the headers back into a carrier dict, hand it to the propagator, get
a `Context` object:

```python
def extract_context(headers):
    if not _enabled():
        return Context()
    carrier = {k: v.decode("utf-8") for k, v in (headers or [])}
    return propagate.extract(carrier)
```

The returned context is not active yet — it is a value describing "the trace this
message came from." Activating it is the consumer's job.

**Consume — make the processing span a child.** In `services/shipping/shipping/worker.py`
the loop extracts the context and passes it straight to `start_as_current_span`:

```python
async for msg in consumer:
    ctx = extract_context(msg.headers)
    with otel.tracer().start_as_current_span("shipping.handle_order_placed", context=ctx):
        shipment_id = await _create_shipment(order)
```

The `context=ctx` argument is the entire trick. Without it, `start_as_current_span`
would start a root span — a new trace, disconnected from the order. With it, the
new span's parent is the order service's publish span, so this work, in a
different process, reached by an asynchronous message, lands under the original
trace. The asyncpg span for `_create_shipment` then nests under *that*, because
the consumer span is now the active context. Notification does the identical
thing for its side effect. Two lines per consumer — extract, then pass `context=`
— and the async hop is whole.

**The same API gives GraphQL its shape.** The review service uses
`start_as_current_span` for a different reason — not to cross a boundary, but to
make one opaque `POST /graphql` legible. Each resolver opens a span:

```python
@strawberry.field
async def order(self, order_id: str) -> Optional[Order]:
    with otel.tracer().start_as_current_span("review.resolve_order"):
        ...
```

So a GraphQL query shows up as a resolver tree — `resolve_order` with its
Postgres child spans — instead of a single span you cannot see inside. Same call,
same span API; once you can open a span deliberately, you can give any custom
work the structure it deserves.

## Build, run, observe

```bash
cd examples/05-spans-across-kafka && ./demo.sh
```

It runs with `PROPAGATE_KAFKA_CONTEXT=true`. Place an order, open the trace in
Tempo, and compare it to Demo 2: the shipping and notification spans are now
children of the same trace, each with their own Postgres spans beneath. One trace
now runs from the REST call all the way through the asynchronous consumers — the
end-to-end picture that was impossible in Chapter 3.

## What you learned

- Automatic propagation stops at boundaries no instrumented client owns; Kafka is
  the canonical example.
- The fix is inject (serialise the active context into message headers) on the
  producer and extract (rebuild it) on the consumer, then `start_as_current_span(..., context=ctx)`
  to parent the processing span to it.
- `start_as_current_span` is also how you give any custom work — GraphQL
  resolvers, batch steps — a visible span structure.

Next, *Auto, custom, and hybrid* steps back from the mechanics to name the
choice you have now exercised both sides of — what to let the libraries trace for
you, where a hand-placed span earns its keep, and what each approach costs.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm that with propagation on, shipping and notification spans
share the order's trace_id and parent to its publish span, and that GraphQL
resolver spans nest under the request. aiokafka header round-tripping of
`traceparent` is the highest-risk detail to verify.*

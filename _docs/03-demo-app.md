---
title: "The services and how they're built"
order: 3
part: "Foundations"
description: "Six small services — order, inventory, payment, shipping, notification, review — that turn one order into a journey across REST, gRPC, GraphQL, Kafka, and Postgres."
duration: 14 minutes
---

Everything that follows instruments one system, so it is worth understanding
that system before any telemetry is added. It is deliberately a realistic shape:
a single user action that does not finish in one process or even one protocol. It
crosses synchronous gRPC calls, an asynchronous message boundary, and a database
before the customer is told anything — the kind of fan-out where, without
tracing, "why was that order slow?" has no good answer.

The cast is a small set of familiar e-commerce services —
**order, inventory, payment, shipping, notification, review** — chosen only
because their interactions are the kind you actually run in production: a
synchronous request that pulls in other services, an asynchronous event that
fans out to more, and a database under each. They run as plain services on
Podman compose; the subject is the telemetry, not the domain.

The code is under `services/`, the shared protos under `proto/`, and the runnable
baseline in `examples/01-no-telemetry/`. The run script there builds the
stack and places an order; its `README.md` covers what it does.

{% raw %}{% include excalidraw.html file="fig-03-service-topology" alt="A client POSTs to the order service over REST; order calls inventory and payment over gRPC, writes Postgres, and publishes order.placed to Kafka; shipping and notification consume the event; the review service serves a GraphQL read API over Postgres." caption="Figure 3.1 — One order, five protocols, six services" %}{% endraw %}

## The one request the whole talk follows

`POST /orders` on the order service is the action everything else hangs off. In
order, it does five things in sequence:

1. **Reserve stock** — a gRPC call to the inventory service (`Reserve`).
2. **Authorize payment** — a gRPC call to the payment service (`Authorize`).
3. **Persist the order** — an `INSERT` into Postgres.
4. **Announce it** — publish an `order.placed` event to Kafka.
5. **Return** the confirmed order to the caller.

Two more services react asynchronously: **shipping** consumes `order.placed` and
writes a shipment row; **notification** consumes the same event and "sends" a
message (a log line standing in for email/SMS). Separately, the **review**
service exposes a **GraphQL** read API so a client can fetch an order and its
product reviews in one round trip.

That is five protocols in one workflow — REST at the edge, gRPC between order and
its two synchronous dependencies, Kafka for the async fan-out, Postgres
underneath most services, and GraphQL on the read side. Each is a different place
where a trace can either continue or break, which is exactly what makes it a good
teaching system.

## How the code works

**The shared library does the plumbing once.** Every service depends on a small
package, `obs` (under `services/common/`), so the instrumentation story is
identical everywhere and lives in one place. It exposes:

- `obs.otel.setup(name)` — builds the OpenTelemetry resource, the OTLP/HTTP
  exporters for traces, metrics, and logs, sets the W3C propagator, and turns on
  auto-instrumentation for the synchronous hops.
- `obs.kafka` / `obs.kafka_propagation` — a JSON producer/consumer plus the
  inject/extract helpers that carry trace context across Kafka.
- `obs.db` — one asyncpg pool from `DATABASE_URL`.
- `obs.logging` — JSON logs stamped with the current `trace_id`/`span_id`.

In this Foundations chapter none of that is switched on yet (the baseline runs
with `OTEL_SDK_DISABLED=true`); the next four chapters turn it on one signal at a
time. What matters here is that the *application* code below has essentially no
telemetry in it — that is the point.

**The order handler is the spine.** In `services/order/order/main.py`, the
handler creates an `order_id`, then calls the two gRPC dependencies through a
thin `Clients` wrapper (`services/order/order/grpc_clients.py`). It checks each
result and short-circuits with a meaningful HTTP status if either fails —
`409` when stock cannot be reserved, `402` when payment declines — writing a
row with the rejection reason either way so failures are not invisible. Only when
both succeed does it persist a `confirmed` order and publish the event. The order
of these calls is deliberate: reserve before you charge, charge before you
promise, promise before you announce.

**The gRPC services own a domain each.** Inventory (`services/inventory`) backs
`Reserve` with a single conditional `UPDATE ... WHERE on_hand >= $qty RETURNING
on_hand`, which both checks and decrements stock atomically, and records a
reservation row keyed by `order_id` so a retry is idempotent. Payment
(`services/payment`) authorizes any amount at or under a fixed ceiling and
declines anything above it — a trivial, deterministic rule whose only job is to
give us a repeatable success path and a repeatable failure path on demand.

**The contracts are shared protos.** The gRPC message and service definitions
live at the repo top level under `proto/shop/...` (inventory, payment, and a
common `Money` type), compiled to Python stubs by `scripts/gen-protos.sh`. One
copy of the truth, compiled into each service that needs it, so the message
shapes can never drift between caller and callee.

**The consumers and the read side.** Shipping and notification
(`services/shipping`, `services/notification`) are `aiokafka` consumers that
loop over `order.placed`; today they simply act on the event. The review service
(`services/review`) is a Strawberry GraphQL app whose resolvers read orders and
reviews from Postgres.

**Document, don't hide, the fragile bits.** For laptop simplicity every domain
shares one Postgres database (`appdb`) rather than a store per domain; the seam
is honest and noted in `stack/db/init/01-schema.sql`.
The payment ceiling and the catalog unit price are hardcoded so demos are
deterministic. Kafka auto-creates the `order.placed` topic. None of these change
the observability story — the spans and metrics are identical — but they would
all change in production.

## Build, run, observe

```bash
cd examples/01-no-telemetry && ./demo.sh
```

It brings the whole stack up in Podman with telemetry disabled and places one
order. You will get a `confirmed` JSON response — and nothing in Grafana, because
the SDK is off. That opacity is the baseline the next chapter starts to remove.

## What you learned

- One `POST /orders` fans out across REST, gRPC (twice), Postgres, and Kafka,
  with two async consumers and a separate GraphQL read path — five protocols.
- A shared `obs` library will carry all the instrumentation, so application code
  stays clean and the telemetry story is identical across services.
- gRPC contracts are shared protos at the repo top level; the async hop is plain
  JSON over Kafka.

Next, *Auto-instrumentation* turns the SDK on and gets a trace across the
synchronous hops for free — and shows exactly where that free ride ends.

---

*Verification status: <span class="status status--unverified">unverified</span>.
A real run must confirm all six service images build on the chosen UBI Python
base, the protos compile into each image, an order returns `confirmed`, and a
shipment row and notification log appear after the event. See
`examples/01-no-telemetry/README.md`.*

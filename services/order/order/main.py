"""Order service — the external REST front door.

POST /orders is the single user action the whole talk traces. One call fans out
across every hop in the mesh:

    HTTP (here) → gRPC Reserve (inventory) → gRPC Authorize (payment)
                → Postgres INSERT (here) → Kafka publish order.placed

gRPC and Postgres are auto-instrumented, so those spans attach to this request's
trace for free. The Kafka publish stamps the trace context into the message
headers (obs.kafka.publish_event) so the shipping and notification consumers can
continue the same trace — the one hop that needs explicit propagation.
"""
from __future__ import annotations

import logging
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from obs import otel, kafka as obskafka, db, logging as obslog
from .grpc_clients import Clients
from . import repo

log = logging.getLogger("order")

ORDER_PLACED_TOPIC = "order.placed"
UNIT_PRICE_CENTS = 1999  # a fixed catalog price keeps the demo deterministic


class CreateOrder(BaseModel):
    customer_id: str
    sku: str
    quantity: int = 1


@asynccontextmanager
async def lifespan(app: FastAPI):
    obslog.configure()
    otel.setup("order")
    otel.instrument_fastapi(app)
    app.state.clients = Clients()
    app.state.producer = await obskafka.make_producer()
    log.info("order service started")
    yield
    await app.state.producer.stop()
    await app.state.clients.close()
    await db.close_pool()


app = FastAPI(title="order", lifespan=lifespan)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/orders")
async def create_order(body: CreateOrder) -> dict:
    order_id = str(uuid.uuid4())
    amount_cents = UNIT_PRICE_CENTS * body.quantity
    log.info("placing order %s for %s x%d", order_id, body.sku, body.quantity)

    # 1. reserve stock (gRPC → inventory; auto-traced)
    reservation = await app.state.clients.reserve(order_id, body.sku, body.quantity)
    if not reservation.reserved:
        await repo.insert_order(order_id, body.customer_id, body.sku, body.quantity, amount_cents, "rejected_stock")
        raise HTTPException(status_code=409, detail="insufficient stock")

    # 2. authorize payment (gRPC → payment; auto-traced)
    auth = await app.state.clients.authorize(order_id, body.customer_id, amount_cents)
    if not auth.authorized:
        await repo.insert_order(order_id, body.customer_id, body.sku, body.quantity, amount_cents, "rejected_payment")
        raise HTTPException(status_code=402, detail=f"payment declined: {auth.decline_reason}")

    # 3. persist the confirmed order (Postgres; auto-traced)
    await repo.insert_order(order_id, body.customer_id, body.sku, body.quantity, amount_cents, "confirmed")

    # 4. announce it (Kafka; trace context injected into headers)
    await obskafka.publish_event(
        app.state.producer, ORDER_PLACED_TOPIC, key=order_id,
        value={
            "order_id": order_id, "customer_id": body.customer_id,
            "sku": body.sku, "quantity": body.quantity, "amount_cents": amount_cents,
        },
    )
    log.info("order %s confirmed and announced", order_id)
    return {"order_id": order_id, "status": "confirmed", "amount_cents": amount_cents}


@app.get("/orders/{order_id}")
async def read_order(order_id: str) -> dict:
    order = await repo.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="order not found")
    return order


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

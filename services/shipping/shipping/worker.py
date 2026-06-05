"""Shipping service — consumes order.placed and creates a shipment.

This is the consumer side of the async hop. The producer (order service) injected
the trace context into the Kafka message headers; here we extract it and open the
processing span with that context as its parent. Without these two lines the
span below would start a brand-new, disconnected trace — the break the
custom-instrumentation chapter is all about closing.
"""
from __future__ import annotations

import asyncio
import logging
import signal
import uuid

from opentelemetry import trace

from obs import otel, db, kafka as obskafka, logging as obslog
from obs.kafka_propagation import extract_context

log = logging.getLogger("shipping")

ORDER_PLACED_TOPIC = "order.placed"


async def _create_shipment(order: dict) -> str:
    pool = await db.get_pool()
    shipment_id = str(uuid.uuid4())
    await pool.execute(
        "INSERT INTO shipments (shipment_id, order_id, sku, quantity, status) VALUES ($1, $2, $3, $4, 'created')",
        shipment_id, order["order_id"], order["sku"], order["quantity"],
    )
    return shipment_id


async def _run() -> None:
    obslog.configure()
    otel.setup("shipping")
    consumer = await obskafka.make_consumer(ORDER_PLACED_TOPIC, group_id="shipping")

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    log.info("shipping consuming %s", ORDER_PLACED_TOPIC)
    try:
        async for msg in consumer:
            ctx = extract_context(msg.headers)            # continue the producer's trace
            with otel.tracer().start_as_current_span("shipping.handle_order_placed", context=ctx):
                order = msg.value
                shipment_id = await _create_shipment(order)
                log.info("created shipment %s for order %s", shipment_id, order["order_id"])
            if stop.is_set():
                break
    finally:
        await consumer.stop()
        await db.close_pool()


def main() -> None:
    asyncio.run(_run())

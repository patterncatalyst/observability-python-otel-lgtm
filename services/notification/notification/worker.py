"""Notification service — consumes order.placed and "sends" a notification.

The simplest consumer: no database, just a side effect (here, a log line standing
in for an email/SMS send). It still extracts the trace context from the message
headers and opens its span under the order's trace, so even this fire-and-forget
side effect is visible on the same end-to-end trace as the original request.
"""
from __future__ import annotations

import asyncio
import logging
import signal

from obs import otel, kafka as obskafka, logging as obslog
from obs.kafka_propagation import extract_context

log = logging.getLogger("notification")

ORDER_PLACED_TOPIC = "order.placed"


async def _run() -> None:
    obslog.configure()
    otel.setup("notification")
    consumer = await obskafka.make_consumer(ORDER_PLACED_TOPIC, group_id="notification")

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    log.info("notification consuming %s", ORDER_PLACED_TOPIC)
    try:
        async for msg in consumer:
            ctx = extract_context(msg.headers)
            with otel.tracer().start_as_current_span("notification.handle_order_placed", context=ctx):
                order = msg.value
                # Stand-in for an email/SMS provider call.
                log.info("notified customer %s about order %s", order["customer_id"], order["order_id"])
            if stop.is_set():
                break
    finally:
        await consumer.stop()


def main() -> None:
    asyncio.run(_run())

"""Consumer service: the work happens here.

Consumes the requests topic, performs the (toy) computation, does a read-then-
write round trip against Postgres, and publishes the result onto the replies
topic keyed by the same request_id so the API can match it back.
"""
from __future__ import annotations
import asyncio
import signal

from .settings import settings
from .messaging import make_producer, make_consumer
from .db import db


def _compute(n: int, multiplier: int) -> int:
    """Toy CPU work: triangular number times the configured multiplier."""
    return (n * (n + 1) // 2) * multiplier


async def run() -> None:
    await db.connect()
    consumer = await make_consumer(settings.requests_topic, group_id="compute-worker")
    producer = await make_producer()

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop.set)

    try:
        async for msg in consumer:
            if stop.is_set():
                break
            data = msg.value
            request_id = data["request_id"]
            n = int(data["n"])

            multiplier = await db.get_multiplier()      # SELECT
            result = _compute(n, multiplier)
            await db.record_job(request_id, n, result)   # INSERT

            await producer.send_and_wait(
                settings.replies_topic,
                key=request_id,
                value={"request_id": request_id, "result": result},
            )
    finally:
        await consumer.stop()
        await producer.stop()
        await db.close()


def main() -> None:
    asyncio.run(run())


if __name__ == "__main__":
    main()

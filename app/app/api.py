"""FastAPI front door.

POST /compute publishes a job to the requests topic and then waits for the
matching reply on the replies topic before returning to the caller — an async
request/reply round trip over Kafka.

Correlation is by request_id: a per-request asyncio.Future is parked in PENDING
when the request is published, and resolved by the background reply consumer
when its reply arrives. The two structures earn their keep:

  PENDING  — request_id -> Future, the in-flight requests this process awaits.
  (the reply consumer is the only thing that resolves those futures.)
"""
from __future__ import annotations
import asyncio
import contextlib
import uuid
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .settings import settings
from .messaging import make_producer, make_consumer

PENDING: dict[str, asyncio.Future] = {}


class ComputeRequest(BaseModel):
    n: int = Field(ge=0, le=1_000_000, description="Sum 1..n is computed by the worker.")


async def _consume_replies(app: FastAPI) -> None:
    """Background task: resolve the Future for each reply's request_id."""
    consumer = await make_consumer(settings.replies_topic, group_id="compute-api")
    app.state.reply_consumer = consumer
    try:
        async for msg in consumer:
            data = msg.value
            request_id = data.get("request_id")
            fut = PENDING.get(request_id)
            if fut is not None and not fut.done():
                fut.set_result(data)
    except asyncio.CancelledError:
        pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start the producer and the reply consumer that the endpoint depends on.
    app.state.producer = await make_producer()
    app.state.reply_task = asyncio.create_task(_consume_replies(app))
    try:
        yield
    finally:
        app.state.reply_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await app.state.reply_task
        if getattr(app.state, "reply_consumer", None):
            await app.state.reply_consumer.stop()
        await app.state.producer.stop()


app = FastAPI(title="compute-api", lifespan=lifespan)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


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


def main() -> None:
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")


if __name__ == "__main__":
    main()

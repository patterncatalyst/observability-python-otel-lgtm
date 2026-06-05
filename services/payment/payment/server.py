"""Payment service — async gRPC.

Authorizes (does not capture) funds for an order. Like inventory, the gRPC server
instrumentation continues the order's trace automatically. The authorization
write is a Postgres span under that same trace.

The decision rule is intentionally trivial and deterministic so the demo is
repeatable: anything at or under a ceiling authorizes; above it declines, giving
you a clean way to produce an error trace on demand.
"""
from __future__ import annotations

import asyncio
import logging
import uuid

import grpc

from obs import otel, db, logging as obslog
from mesh.payment.v1 import payment_pb2, payment_pb2_grpc

log = logging.getLogger("payment")

AUTH_CEILING_CENTS = 100_000  # $1,000 — above this we decline, for a demoable failure


class PaymentServicer(payment_pb2_grpc.PaymentServiceServicer):
    async def Authorize(self, request, context):
        amount = request.amount.amount_cents
        pool = await db.get_pool()

        existing = await pool.fetchrow(
            "SELECT authorization_id, authorized FROM authorizations WHERE order_id = $1",
            request.order_id,
        )
        if existing:
            return payment_pb2.AuthorizeResponse(
                authorized=existing["authorized"],
                authorization_id=existing["authorization_id"],
                decline_reason="" if existing["authorized"] else "amount over ceiling",
            )

        authorized = amount <= AUTH_CEILING_CENTS
        authorization_id = str(uuid.uuid4())
        await pool.execute(
            "INSERT INTO authorizations (authorization_id, order_id, customer_id, amount_cents, authorized) "
            "VALUES ($1, $2, $3, $4, $5)",
            authorization_id, request.order_id, request.customer_id, amount, authorized,
        )
        if authorized:
            log.info("authorized %d cents for order %s", amount, request.order_id)
            return payment_pb2.AuthorizeResponse(authorized=True, authorization_id=authorization_id, decline_reason="")
        log.warning("declined %d cents for order %s (over ceiling)", amount, request.order_id)
        return payment_pb2.AuthorizeResponse(authorized=False, authorization_id=authorization_id, decline_reason="amount over ceiling")


async def _serve() -> None:
    obslog.configure()
    otel.setup("payment")
    server = grpc.aio.server()
    payment_pb2_grpc.add_PaymentServiceServicer_to_server(PaymentServicer(), server)
    server.add_insecure_port("0.0.0.0:50052")
    await server.start()
    log.info("payment gRPC server listening on :50052")
    await server.wait_for_termination()


def main() -> None:
    asyncio.run(_serve())

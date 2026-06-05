"""Inventory service — async gRPC.

The gRPC server is auto-instrumented, so the trace context the order service sent
on the wire is picked up here automatically: CheckStock/Reserve spans and their
Postgres spans land under the order's trace, in a different process, with no
propagation code in this file.
"""
from __future__ import annotations

import asyncio
import logging
import uuid

import grpc

from obs import otel, db, logging as obslog
from shop.inventory.v1 import inventory_pb2, inventory_pb2_grpc

log = logging.getLogger("inventory")


class InventoryServicer(inventory_pb2_grpc.InventoryServiceServicer):
    async def CheckStock(self, request, context):
        pool = await db.get_pool()
        on_hand = await pool.fetchval("SELECT on_hand FROM stock WHERE sku = $1", request.sku) or 0
        return inventory_pb2.CheckStockResponse(available=on_hand >= request.quantity, on_hand=on_hand)

    async def Reserve(self, request, context):
        pool = await db.get_pool()
        # Idempotent on order_id+sku: a retry returns the original reservation.
        existing = await pool.fetchrow(
            "SELECT reservation_id FROM reservations WHERE order_id = $1 AND sku = $2",
            request.order_id, request.sku,
        )
        if existing:
            remaining = await pool.fetchval("SELECT on_hand FROM stock WHERE sku = $1", request.sku) or 0
            return inventory_pb2.ReserveResponse(reserved=True, reservation_id=existing["reservation_id"], remaining=remaining)

        remaining = await pool.fetchval(
            "UPDATE stock SET on_hand = on_hand - $2 WHERE sku = $1 AND on_hand >= $2 RETURNING on_hand",
            request.sku, request.quantity,
        )
        if remaining is None:
            log.warning("reserve failed for %s: insufficient stock", request.sku)
            return inventory_pb2.ReserveResponse(reserved=False, reservation_id="", remaining=0)

        reservation_id = str(uuid.uuid4())
        await pool.execute(
            "INSERT INTO reservations (reservation_id, order_id, sku, quantity) VALUES ($1, $2, $3, $4)",
            reservation_id, request.order_id, request.sku, request.quantity,
        )
        log.info("reserved %d of %s for order %s", request.quantity, request.sku, request.order_id)
        return inventory_pb2.ReserveResponse(reserved=True, reservation_id=reservation_id, remaining=remaining)


async def _serve() -> None:
    obslog.configure()
    otel.setup("inventory")
    server = grpc.aio.server()
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(InventoryServicer(), server)
    server.add_insecure_port("0.0.0.0:50051")
    await server.start()
    log.info("inventory gRPC server listening on :50051")
    await server.wait_for_termination()


def main() -> None:
    asyncio.run(_serve())

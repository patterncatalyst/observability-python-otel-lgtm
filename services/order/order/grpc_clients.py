"""gRPC stubs the order service calls service-to-service. Because gRPC is
auto-instrumented in obs.otel.setup, the trace context rides along on these
calls without any code here — the inventory and payment spans land under the
same trace as the incoming HTTP request."""
from __future__ import annotations

import os

import grpc

from mesh.inventory.v1 import inventory_pb2, inventory_pb2_grpc
from mesh.payment.v1 import payment_pb2, payment_pb2_grpc
from mesh.common.v1 import common_pb2


class Clients:
    def __init__(self) -> None:
        self._inv_channel = grpc.aio.insecure_channel(os.getenv("INVENTORY_ADDR", "inventory:50051"))
        self._pay_channel = grpc.aio.insecure_channel(os.getenv("PAYMENT_ADDR", "payment:50052"))
        self.inventory = inventory_pb2_grpc.InventoryServiceStub(self._inv_channel)
        self.payment = payment_pb2_grpc.PaymentServiceStub(self._pay_channel)

    async def reserve(self, order_id: str, sku: str, quantity: int):
        return await self.inventory.Reserve(
            inventory_pb2.ReserveRequest(order_id=order_id, sku=sku, quantity=quantity)
        )

    async def authorize(self, order_id: str, customer_id: str, amount_cents: int, currency: str = "USD"):
        return await self.payment.Authorize(
            payment_pb2.AuthorizeRequest(
                order_id=order_id,
                customer_id=customer_id,
                amount=common_pb2.Money(amount_cents=amount_cents, currency=currency),
            )
        )

    async def close(self) -> None:
        await self._inv_channel.close()
        await self._pay_channel.close()

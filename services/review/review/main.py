"""Review service — the GraphQL read edge of the mesh.

GraphQL is the external read API: a client asks for an order and its reviews in
one round trip, and the resolvers fan out to Postgres. The HTTP layer is
auto-instrumented (it's FastAPI under the hood), and each resolver opens a custom
span so the trace shows the resolver tree, not just one opaque POST /graphql.
That resolver-span pattern is what the custom-instrumentation chapter generalises.
"""
from __future__ import annotations

import logging
from typing import List, Optional

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from obs import otel, db, logging as obslog

log = logging.getLogger("review")


@strawberry.type
class Review:
    review_id: str
    sku: str
    rating: int
    body: str


@strawberry.type
class Order:
    order_id: str
    sku: str
    quantity: int
    status: str
    reviews: List[Review]


async def _reviews_for_sku(sku: str) -> List[Review]:
    pool = await db.get_pool()
    rows = await pool.fetch("SELECT review_id, sku, rating, body FROM reviews WHERE sku = $1", sku)
    return [Review(review_id=r["review_id"], sku=r["sku"], rating=r["rating"], body=r["body"]) for r in rows]


@strawberry.type
class Query:
    @strawberry.field
    async def order(self, order_id: str) -> Optional[Order]:
        with otel.tracer().start_as_current_span("review.resolve_order"):
            pool = await db.get_pool()
            row = await pool.fetchrow(
                "SELECT order_id, sku, quantity, status FROM orders WHERE order_id = $1", order_id
            )
            if row is None:
                return None
            reviews = await _reviews_for_sku(row["sku"])
            return Order(order_id=row["order_id"], sku=row["sku"], quantity=row["quantity"],
                         status=row["status"], reviews=reviews)

    @strawberry.field
    async def reviews(self, sku: str) -> List[Review]:
        with otel.tracer().start_as_current_span("review.resolve_reviews"):
            return await _reviews_for_sku(sku)


schema = strawberry.Schema(Query)
app = FastAPI(title="review")
app.include_router(GraphQLRouter(schema), prefix="/graphql")


@app.on_event("startup")
async def _startup() -> None:
    obslog.configure()
    otel.setup("review")
    otel.instrument_fastapi(app)
    log.info("review GraphQL service started")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


def main() -> None:
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

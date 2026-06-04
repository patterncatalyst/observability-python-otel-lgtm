"""Postgres access via an asyncpg connection pool.

Two operations make up the database round trip the worker performs per job:
a SELECT to read a small config value, then an INSERT to record the result.
"""
from __future__ import annotations
import asyncpg
from .settings import settings


class Database:
    def __init__(self) -> None:
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        # A pool (not a single connection) so concurrent requests don't serialise
        # on one socket. min/max kept small for a laptop-sized demo.
        self._pool = await asyncpg.create_pool(
            dsn=settings.dsn, min_size=1, max_size=10, command_timeout=10
        )

    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()

    async def get_multiplier(self) -> int:
        """Read the 'multiplier' config row (the SELECT half of the round trip)."""
        assert self._pool is not None
        row = await self._pool.fetchrow(
            "SELECT value FROM compute_config WHERE key = $1", "multiplier"
        )
        return int(row["value"]) if row else 1

    async def record_job(self, request_id: str, n: int, result: int) -> None:
        """Persist a completed job (the INSERT half of the round trip)."""
        assert self._pool is not None
        await self._pool.execute(
            "INSERT INTO jobs (request_id, n, result) VALUES ($1, $2, $3) "
            "ON CONFLICT (request_id) DO NOTHING",
            request_id, n, result,
        )


db = Database()

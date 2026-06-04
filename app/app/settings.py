"""Runtime configuration, read once from the environment.

Every value has a default that matches the compose stack, so the service runs
unconfigured inside the network and is overridable from the host for local runs.
"""
from __future__ import annotations
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "5432"))
    db_name: str = os.getenv("DB_NAME", "appdb")
    db_user: str = os.getenv("DB_USER", "appuser")
    db_password: str = os.getenv("DB_PASSWORD", "apppass")

    kafka_bootstrap: str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "127.0.0.1:9092")
    requests_topic: str = os.getenv("REQUESTS_TOPIC", "compute.requests")
    replies_topic: str = os.getenv("REPLIES_TOPIC", "compute.replies")

    reply_timeout_s: float = float(os.getenv("REPLY_TIMEOUT_S", "10"))

    @property
    def dsn(self) -> str:
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )


settings = Settings()

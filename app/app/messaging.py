"""Thin async Kafka helpers built on aiokafka.

Messages are JSON objects encoded to UTF-8 bytes. The message key is the
request_id so all messages for one request land on the same partition and keep
their order. (Trace-context headers get added in the custom-instrumentation
chapter; the baseline service carries none.)
"""
from __future__ import annotations
import json
from typing import Any
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from .settings import settings


def _encode(value: dict[str, Any]) -> bytes:
    return json.dumps(value).encode("utf-8")


def _decode(raw: bytes) -> dict[str, Any]:
    return json.loads(raw.decode("utf-8"))


async def make_producer() -> AIOKafkaProducer:
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap,
        value_serializer=_encode,
        key_serializer=lambda k: k.encode("utf-8"),
        enable_idempotence=True,
    )
    await producer.start()
    return producer


async def make_consumer(topic: str, group_id: str) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=settings.kafka_bootstrap,
        group_id=group_id,
        value_deserializer=_decode,
        key_deserializer=lambda k: k.decode("utf-8") if k else None,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
    )
    await consumer.start()
    return consumer

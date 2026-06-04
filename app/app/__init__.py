"""Compute demo service: a FastAPI front door and a Kafka-driven worker that
together make one request travel API → Kafka → worker → Postgres → Kafka → API."""
__version__ = "0.1.0"

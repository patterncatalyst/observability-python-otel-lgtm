"""obs — shared OpenTelemetry bootstrap and mesh plumbing for every service.

Typical service startup:

    from obs import otel, logging as obslog
    obslog.configure()
    otel.setup("order")               # traces + metrics + logs + auto-instrumentation
    # ... for an HTTP service, once the app exists:
    otel.instrument_fastapi(app)
"""
from . import otel, kafka, kafka_propagation, db, logging  # noqa: F401

__all__ = ["otel", "kafka", "kafka_propagation", "db", "logging"]

"""OpenTelemetry bootstrap shared by every service.

One call to :func:`setup` wires the SDK the same way everywhere: a shared
resource (who am I), OTLP/HTTP exporters for all three signals pointed at the
Collector, and the W3C trace-context propagator. It then turns on the
auto-instrumentation that needs no application code — FastAPI, gRPC (client and
server), and asyncpg — so a request is traced across the synchronous hops for
free.

The one hop it deliberately does *not* auto-propagate is Kafka: carrying trace
context across that asynchronous boundary is done explicitly with
:mod:`obs.kafka_propagation`, which is the subject of the custom-instrumentation
chapter. That keeps the teaching arc honest — auto-instrumentation gets you most
of the way; the message boundary is the part you wire by hand.
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry._logs import set_logger_provider
from opentelemetry.propagate import set_global_textmap
from opentelemetry.trace.propagation.tracecontext import TraceContextTextMapPropagator


@dataclass(frozen=True)
class ObsConfig:
    service_name: str
    service_version: str = os.getenv("SERVICE_VERSION", "0.1.0")
    environment: str = os.getenv("DEPLOY_ENV", "local")
    # Path-less OTLP/HTTP base; the SDK appends /v1/traces, /v1/metrics, /v1/logs.
    endpoint: str = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://lgtm:4318")
    disabled: bool = os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true"


_TRACER = None
_METER = None


def setup(service_name: str) -> ObsConfig:
    """Initialise tracing, metrics, and logs for this process. Idempotent-ish:
    call once at startup. Returns the resolved config for logging/diagnostics."""
    global _TRACER, _METER
    cfg = ObsConfig(service_name=service_name)

    if cfg.disabled:
        # Baseline demo: the SDK is off, the service is fully opaque on purpose.
        _TRACER = trace.get_tracer(service_name)
        _METER = metrics.get_meter(service_name)
        return cfg

    resource = Resource.create(
        {
            "service.name": cfg.service_name,
            "service.version": cfg.service_version,
            "deployment.environment": cfg.environment,
        }
    )

    # --- traces ---
    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{cfg.endpoint}/v1/traces"))
    )
    trace.set_tracer_provider(tracer_provider)

    # Propagation: W3C Trace Context. This is what makes the `traceparent` header
    # understood on both ends of every HTTP/gRPC hop, and it is exactly the format
    # obs.kafka_propagation injects into and extracts from Kafka headers by hand.
    set_global_textmap(TraceContextTextMapPropagator())

    # --- metrics ---
    reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=f"{cfg.endpoint}/v1/metrics")
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
    metrics.set_meter_provider(meter_provider)

    # --- logs ---
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=f"{cfg.endpoint}/v1/logs"))
    )
    set_logger_provider(logger_provider)
    # Bridge stdlib logging onto the OTLP log signal. This SDK handler exports every
    # record to the Collector, which routes it to Loki — and the SDK auto-stamps the
    # active trace_id/span_id onto each record, so the log↔trace correlation holds
    # without anyone parsing a stdout line. obs.logging.configure() keeps a separate
    # stdout JSON handler as the local `podman logs` view, so it must run *before*
    # setup() (this appends; configure() resets handlers).
    logging.getLogger().addHandler(
        LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
    )

    _TRACER = trace.get_tracer(service_name)
    _METER = metrics.get_meter(service_name)
    _enable_auto_instrumentation()
    return cfg


def _enable_auto_instrumentation() -> None:
    """Turn on the no-code instrumentation for the synchronous hops. Each import
    is local so a service that lacks one of these libraries still starts."""
    try:
        from opentelemetry.instrumentation.asyncpg import AsyncPGInstrumentor
        AsyncPGInstrumentor().instrument()
    except Exception:
        pass
    try:
        from opentelemetry.instrumentation.grpc import (
            GrpcAioInstrumentorClient,
            GrpcAioInstrumentorServer,
        )
        GrpcAioInstrumentorClient().instrument()
        GrpcAioInstrumentorServer().instrument()
    except Exception:
        pass


def instrument_fastapi(app) -> None:
    """FastAPI is instrumented against the live app object, so services that
    serve HTTP call this from their startup once the app exists."""
    if os.getenv("OTEL_SDK_DISABLED", "false").lower() == "true":
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
    except Exception:
        pass


def tracer():
    return _TRACER if _TRACER is not None else trace.get_tracer("uninitialised")


def meter():
    return _METER if _METER is not None else metrics.get_meter("uninitialised")

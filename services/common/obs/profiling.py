"""Continuous profiling — the fourth signal, as an optional hook.

Profiling is the least settled signal: the OpenTelemetry profiling signal (OTLP
profiles) is still experimental and its Python SDK support is nascent, so the
pragmatic path today is Grafana's Pyroscope SDK, which samples in-process and
pushes to Pyroscope (bundled in the otel-lgtm image).

This is deliberately optional and side-effect-free unless asked for: it no-ops
unless PYROSCOPE_ADDRESS is set, and the import is soft so a service without the
``pyroscope-io`` dependency still starts. Call it once at startup; obs.otel.setup
already does.
"""
from __future__ import annotations

import os


def setup_profiling(service_name: str) -> None:
    addr = os.getenv("PYROSCOPE_ADDRESS")
    if not addr:
        return
    try:
        import pyroscope  # provided by the optional `pyroscope-io` package
    except ImportError:
        return
    pyroscope.configure(
        application_name=service_name,
        server_address=addr,
        tags={"service_name": service_name},
    )

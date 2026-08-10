from __future__ import annotations

import asyncio
import logging

import httpx
import pytest
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from lumens_observability import (
    capture_background_context,
    configure_application_observability,
    force_flush,
    instrument_fastapi,
    install_logging_correlation,
    run_in_background_context,
    shutdown_observability,
)


def test_fastapi_server_span_is_automatic_and_instrumentation_is_idempotent() -> None:
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    app = FastAPI()

    @app.get("/health")
    async def health() -> dict[str, bool]:
        return {"ok": True}

    async def request() -> httpx.Response:
        assert instrument_fastapi(app, tracer_provider=provider) is app
        assert instrument_fastapi(app, tracer_provider=provider) is app
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
            return await client.get("/health")

    response = asyncio.run(request())

    assert response.status_code == 200
    spans = exporter.get_finished_spans()
    assert len([span for span in spans if span.kind is trace.SpanKind.SERVER]) == 1
    shutdown_observability(app)
    provider.shutdown()


def test_application_managed_configuration_preserves_explicit_provider() -> None:
    provider = TracerProvider()
    operations = configure_application_observability("1.0.0", tracer_provider=provider)
    assert operations is not None
    assert provider.get_tracer("com.deloitte.lumens.observability") is not None
    provider.shutdown()


def test_asyncio_task_preserves_active_trace_context() -> None:
    provider = TracerProvider()
    tracer = provider.get_tracer("test")
    seen: list[str] = []

    async def child() -> None:
        seen.append(trace.get_current_span().get_span_context().trace_id.to_bytes(16, "big").hex())

    async def run() -> str:
        with tracer.start_as_current_span("parent") as parent:
            await asyncio.create_task(child())
            return parent.get_span_context().trace_id.to_bytes(16, "big").hex()

    assert seen == [asyncio.run(run())]
    provider.shutdown()


def test_background_context_captures_active_trace() -> None:
    provider = TracerProvider()
    tracer = provider.get_tracer("test")
    with tracer.start_as_current_span("parent") as parent:
        callback = capture_background_context(lambda: trace.get_current_span().get_span_context().trace_id)
        expected = parent.get_span_context().trace_id

    assert asyncio.run(run_in_background_context(callback)) == expected
    provider.shutdown()


def test_logging_correlation_does_not_replace_handlers() -> None:
    logger = logging.getLogger("lumens-test")
    handler = logging.NullHandler()
    logger.addHandler(handler)
    before = list(logger.handlers)

    filter_ = install_logging_correlation(logger)
    assert install_logging_correlation(logger) is filter_
    assert logger.handlers == before
    record = logging.LogRecord("lumens-test", logging.INFO, __file__, 1, "message", (), None)
    assert filter_.filter(record)
    assert hasattr(record, "otelTraceID")
    logger.removeHandler(handler)


def test_force_flush_handles_noop_global_providers() -> None:
    assert force_flush() is True

"""FastAPI integration that delegates standard HTTP spans to OpenTelemetry instrumentation."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable, Mapping
from contextvars import copy_context
from typing import Any

from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import Tracer

from lumens_observability.core import AttributePolicy, LumensOperations, configure_observability, deny_all_attributes

_INSTRUMENTED_MARKER = "_lumens_fastapi_instrumented"


def configure_application_observability(
    contract_version: str,
    attribute_policy: AttributePolicy = deny_all_attributes,
    tracer_provider: TracerProvider | None = None,
    meter_provider: MeterProvider | None = None,
) -> LumensOperations:
    """Configure application-managed providers without replacing an existing global provider."""
    current_tracer_provider = tracer_provider or trace.get_tracer_provider()
    current_meter_provider = meter_provider or metrics.get_meter_provider()
    if tracer_provider is None and type(current_tracer_provider).__module__.startswith("opentelemetry.trace"):
        current_tracer_provider = TracerProvider()
        trace.set_tracer_provider(current_tracer_provider)
        current_meter_provider = MeterProvider()
        metrics.set_meter_provider(current_meter_provider)
    return configure_observability(
        contract_version,
        attribute_policy,
        current_tracer_provider.get_tracer("com.deloitte.lumens.observability"),
        current_meter_provider.get_meter("com.deloitte.lumens.observability"),
    )


def instrument_fastapi(app: FastAPI, *, tracer_provider: TracerProvider | None = None) -> FastAPI:
    """Install official FastAPI instrumentation once without wrapping handlers with Lumens spans."""
    if getattr(app.state, _INSTRUMENTED_MARKER, False):
        return app
    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer_provider)
    setattr(app.state, _INSTRUMENTED_MARKER, True)
    return app


def shutdown_observability(app: FastAPI | None = None) -> None:
    """Uninstrument an app when possible; global provider shutdown remains application-owned."""
    if app is not None and getattr(app.state, _INSTRUMENTED_MARKER, False):
        FastAPIInstrumentor.uninstrument_app(app)
        setattr(app.state, _INSTRUMENTED_MARKER, False)


def force_flush() -> bool:
    """Flush application-managed tracer and meter providers when they support it."""
    flushed = True
    for provider in (trace.get_tracer_provider(), metrics.get_meter_provider()):
        flush = getattr(provider, "force_flush", None)
        if callable(flush):
            flushed = bool(flush()) and flushed
    return flushed


class TraceContextFilter(logging.Filter):
    """Adds trace correlation fields without replacing logging handlers or formatters."""

    def filter(self, record: logging.LogRecord) -> bool:
        context = trace.get_current_span().get_span_context()
        record.otelTraceID = format(context.trace_id, "032x") if context.is_valid else ""
        record.otelSpanID = format(context.span_id, "016x") if context.is_valid else ""
        record.otelTraceSampled = "true" if context.trace_flags.sampled else "false"
        return True


def install_logging_correlation(logger: logging.Logger) -> TraceContextFilter:
    """Add one Lumens correlation filter without modifying existing handlers."""
    for existing in logger.filters:
        if isinstance(existing, TraceContextFilter):
            return existing
    filter_ = TraceContextFilter()
    logger.addFilter(filter_)
    return filter_


def capture_background_context(callback: Callable[..., Any]) -> Callable[..., Any]:
    """Capture the active context for FastAPI background work without leaking mutable context."""
    context = copy_context()

    def run(*args: Any, **kwargs: Any) -> Any:
        return context.run(callback, *args, **kwargs)

    return run


async def run_in_background_context(callback: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Run a synchronous callback in a thread with the current OpenTelemetry context copied."""
    return await asyncio.to_thread(capture_background_context(callback), *args, **kwargs)

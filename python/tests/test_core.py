from __future__ import annotations

import asyncio

import pytest
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import InMemoryMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

from lumens_observability import configure_observability, registered_attributes


class InMemoryTelemetry:
    def __init__(self) -> None:
        self.spans = InMemorySpanExporter()
        self.metrics = InMemoryMetricReader()
        self.tracer_provider = TracerProvider()
        self.tracer_provider.add_span_processor(SimpleSpanProcessor(self.spans))
        self.meter_provider = MeterProvider(metric_readers=[self.metrics])

    def operations(self, registered: set[str] = {"integration.provider", "safe.attribute"}):
        return configure_observability(
            "1.0.0",
            registered_attributes(registered),
            self.tracer_provider.get_tracer("test"),
            self.meter_provider.get_meter("test"),
        )

    def close(self) -> None:
        self.tracer_provider.shutdown()
        self.meter_provider.shutdown()


@pytest.fixture
def telemetry():
    fixture = InMemoryTelemetry()
    yield fixture
    fixture.close()


def span_named(telemetry: InMemoryTelemetry, name: str):
    return next(span for span in telemetry.spans.get_finished_spans() if span.name == name)


def test_nested_operations_preserve_parentage_and_record_metrics(telemetry: InMemoryTelemetry) -> None:
    operations = telemetry.operations()

    def outer(operation):
        operation.set_outcome("declined")
        return operations.observe("integration.enrich", lambda _: "ok", {"safe.attribute": "accepted"})

    assert operations.observe("payment.authorize", outer, {"integration.provider": "example-provider"}) == "ok"
    outer_span = span_named(telemetry, "payment.authorize")
    inner_span = span_named(telemetry, "integration.enrich")
    assert inner_span.parent.span_id == outer_span.context.span_id
    assert inner_span.context.trace_id == outer_span.context.trace_id
    assert outer_span.attributes["lumens.operation.outcome"] == "declined"
    assert inner_span.attributes["safe.attribute"] == "accepted"
    metric_names = {metric.name for resource_metrics in telemetry.metrics.get_metrics_data().resource_metrics for scope_metrics in resource_metrics.scope_metrics for metric in scope_metrics.metrics}
    assert {"lumens.operation.executions", "lumens.operation.duration"} <= metric_names


def test_failure_is_recorded_without_exception_message(telemetry: InMemoryTelemetry) -> None:
    operations = telemetry.operations()

    with pytest.raises(ValueError, match="do not export this message"):
        operations.observe("payment.authorize", lambda _: (_ for _ in ()).throw(ValueError("do not export this message")))

    span = span_named(telemetry, "payment.authorize")
    assert span.status.is_ok is False
    assert span.attributes["lumens.operation.outcome"] == "failure"
    assert span.attributes["error.type"] == "builtins.ValueError"
    assert "do not export this message" not in str(span.attributes)


def test_cancelled_async_operation_is_not_an_error(telemetry: InMemoryTelemetry) -> None:
    operations = telemetry.operations()

    async def cancelled(_):
        raise asyncio.CancelledError()

    with pytest.raises(asyncio.CancelledError):
        asyncio.run(operations.observe_async("payment.authorize", cancelled))

    span = span_named(telemetry, "payment.authorize")
    assert span.attributes["lumens.operation.outcome"] == "cancelled"
    assert span.status.is_ok is True


def test_async_operation_ends_after_awaited_work(telemetry: InMemoryTelemetry) -> None:
    operations = telemetry.operations()
    started = asyncio.Event()
    release = asyncio.Event()

    async def work(_):
        started.set()
        await release.wait()
        return "ok"

    async def run() -> None:
        task = asyncio.create_task(operations.observe_async("integration.enrich", work))
        await started.wait()
        assert telemetry.spans.get_finished_spans() == ()
        release.set()
        assert await task == "ok"

    asyncio.run(run())
    assert span_named(telemetry, "integration.enrich").attributes["lumens.operation.outcome"] == "success"


def test_manual_close_is_idempotent_and_attribute_policy_drops_unsafe_values(telemetry: InMemoryTelemetry) -> None:
    operations = telemetry.operations()
    operation = operations.start(
        "payment.authorize",
        {"safe.attribute": "kept", "request.password": "dropped", "unregistered": "dropped"},
    )
    operation.set_outcome("approved")
    operation.close()
    operation.close()

    spans = telemetry.spans.get_finished_spans()
    assert len(spans) == 1
    assert spans[0].attributes["safe.attribute"] == "kept"
    assert "request.password" not in spans[0].attributes
    assert "unregistered" not in spans[0].attributes


def test_default_policy_drops_all_custom_attributes(telemetry: InMemoryTelemetry) -> None:
    operations = configure_observability(
        "1.0.0",
        tracer=telemetry.tracer_provider.get_tracer("test"),
        meter=telemetry.meter_provider.get_meter("test"),
    )
    operations.observe("payment.authorize", lambda _: None, {"safe.attribute": "dropped"})
    assert "safe.attribute" not in span_named(telemetry, "payment.authorize").attributes

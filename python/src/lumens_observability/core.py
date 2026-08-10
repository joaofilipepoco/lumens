"""Core operation lifecycle, metrics, and source-level custom attribute policy."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable, Mapping
from contextlib import AbstractAsyncContextManager, AbstractContextManager
from time import perf_counter_ns
from typing import Any, Protocol, TypeVar

from opentelemetry import metrics, trace
from opentelemetry.metrics import Meter
from opentelemetry.trace import Span, Status, StatusCode, Tracer

INSTRUMENTATION_SCOPE = "com.deloitte.lumens.observability"
OPERATION_NAME = "lumens.operation.name"
OPERATION_OUTCOME = "lumens.operation.outcome"
CONTRACT_VERSION = "lumens.contract.version"
EXECUTIONS = "lumens.operation.executions"
DURATION = "lumens.operation.duration"

T = TypeVar("T")


class AttributePolicy(Protocol):
    """Filters custom telemetry fields before they reach OpenTelemetry."""

    def __call__(self, attributes: Mapping[str, str]) -> Mapping[str, str]: ...


def deny_all_attributes(_: Mapping[str, str]) -> Mapping[str, str]:
    """Safely reject custom attributes until a contract-derived policy is configured."""
    return {}


def registered_attributes(allowed: set[str]) -> AttributePolicy:
    """Accept registered non-secret-looking keys and non-null values only."""
    registered = frozenset(allowed)
    forbidden = ("authorization", "cookie", "credential", "password", "secret", "token")

    def policy(attributes: Mapping[str, str]) -> Mapping[str, str]:
        return {
            key: value
            for key, value in attributes.items()
            if key in registered and value is not None and not any(part in key.lower() for part in forbidden)
        }

    return policy


class LumensOperation(AbstractContextManager["LumensOperation"], AbstractAsyncContextManager["LumensOperation"]):
    """A manual operation. Call fail when handling a technical exception outside observe."""

    def __init__(
        self,
        span: Span,
        executions: Any,
        duration: Any,
        operation_name: str,
        contract_version: str,
        attributes: Mapping[str, str],
    ) -> None:
        self._span = span
        self._scope = trace.use_span(span, end_on_exit=False)
        self._scope.__enter__()
        self._executions = executions
        self._duration = duration
        self._operation_name = operation_name
        self._started_at_ns = perf_counter_ns()
        self._outcome = "success"
        self._closed = False
        span.set_attribute(OPERATION_NAME, operation_name)
        span.set_attribute(CONTRACT_VERSION, contract_version)
        for key, value in attributes.items():
            span.set_attribute(key, value)

    def set_outcome(self, outcome: str) -> None:
        if not self._closed:
            self._outcome = _bounded_outcome(outcome)
            self._span.set_attribute(OPERATION_OUTCOME, self._outcome)

    def fail(self, error: BaseException) -> None:
        if self._closed or isinstance(error, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
            return
        self._outcome = "failure"
        self._span.set_attribute(OPERATION_OUTCOME, self._outcome)
        self._span.record_exception(error)
        self._span.set_status(Status(StatusCode.ERROR))
        self._span.set_attribute("error.type", f"{type(error).__module__}.{type(error).__qualname__}")

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._span.set_attribute(OPERATION_OUTCOME, self._outcome)
        metric_attributes = {OPERATION_NAME: self._operation_name, OPERATION_OUTCOME: self._outcome}
        self._executions.add(1, metric_attributes)
        self._duration.record(max(0, (perf_counter_ns() - self._started_at_ns) / 1_000_000_000), metric_attributes)
        self._scope.__exit__(None, None, None)
        self._span.end()

    def __exit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, _: Any) -> bool:
        if exc is not None:
            if isinstance(exc, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                self.set_outcome("cancelled")
            else:
                self.fail(exc)
        self.close()
        return False

    async def __aenter__(self) -> "LumensOperation":
        return self

    async def __aexit__(self, exc_type: type[BaseException] | None, exc: BaseException | None, tb: Any) -> bool:
        return self.__exit__(exc_type, exc, tb)


class LumensOperations:
    """Framework-independent synchronous and asynchronous Lumens operations."""

    def __init__(self, tracer: Tracer, meter: Meter, contract_version: str, attribute_policy: AttributePolicy) -> None:
        self._tracer = tracer
        self._contract_version = contract_version
        self._attribute_policy = attribute_policy
        self._executions = meter.create_counter(EXECUTIONS)
        self._duration = meter.create_histogram(DURATION, unit="s")

    def start(self, operation_name: str, attributes: Mapping[str, str] | None = None) -> LumensOperation:
        _operation_name(operation_name)
        span = self._tracer.start_span(operation_name, kind=trace.SpanKind.INTERNAL)
        return LumensOperation(
            span,
            self._executions,
            self._duration,
            operation_name,
            self._contract_version,
            self._attribute_policy(dict(attributes or {})),
        )

    def observe(self, operation_name: str, callback: Callable[[LumensOperation], T], attributes: Mapping[str, str] | None = None) -> T:
        with self.start(operation_name, attributes) as operation:
            return callback(operation)

    async def observe_async(
        self,
        operation_name: str,
        callback: Callable[[LumensOperation], Awaitable[T]],
        attributes: Mapping[str, str] | None = None,
    ) -> T:
        async with self.start(operation_name, attributes) as operation:
            return await callback(operation)


def configure_observability(
    contract_version: str,
    attribute_policy: AttributePolicy = deny_all_attributes,
    tracer: Tracer | None = None,
    meter: Meter | None = None,
) -> LumensOperations:
    """Create Lumens core operations from existing or application-owned OpenTelemetry providers."""
    if not contract_version:
        raise ValueError("contract_version must not be empty.")
    return LumensOperations(
        tracer or trace.get_tracer(INSTRUMENTATION_SCOPE),
        meter or metrics.get_meter(INSTRUMENTATION_SCOPE),
        contract_version,
        attribute_policy,
    )


def _operation_name(value: str) -> str:
    if not value or not _stable_identifier(value):
        raise ValueError("operation_name must be a stable lowercase identifier.")
    return value


def _bounded_outcome(value: str) -> str:
    if not value or not value.replace("_", "").replace("-", "").isalnum() or value != value.lower():
        raise ValueError("outcome must be a stable lowercase bounded identifier.")
    return value


def _stable_identifier(value: str) -> bool:
    return value[0].islower() and all(character.islower() or character.isdigit() or character in ".-_" for character in value)

# Python Getting Started

MVP-F04 provides the framework-independent Python core API. MVP-F06 adds FastAPI instrumentation, provider coexistence, and logging correlation.

## FastAPI

FastAPI routes receive standard server spans from the official OpenTelemetry FastAPI instrumentor. Do not add a Lumens decorator to routes merely to obtain HTTP telemetry.

Platform-managed applications keep their existing OpenTelemetry providers and instrument the application once:

```python
from fastapi import FastAPI
from lumens_observability import instrument_fastapi

app = FastAPI()
instrument_fastapi(app)
```

Application-managed applications can configure Lumens core operations with explicit providers, then instrument the FastAPI app with the same tracer provider:

```python
from opentelemetry.sdk.trace import TracerProvider
from lumens_observability import configure_application_observability, instrument_fastapi

tracer_provider = TracerProvider()
operations = configure_application_observability(
    "1.0.0",
    tracer_provider=tracer_provider,
)
instrument_fastapi(app, tracer_provider=tracer_provider)
```

`instrument_fastapi` is idempotent and does not replace an application-owned provider. Use `shutdown_observability(app)` in controlled test or application shutdown paths to remove the FastAPI instrumentation.

## Logging And Background Work

`install_logging_correlation(logger)` adds trace ID, span ID, and sampling fields to records without replacing existing handlers. Configure formatters to use `%(otelTraceID)s`, `%(otelSpanID)s`, and `%(otelTraceSampled)s` where required.

Use `capture_background_context` for FastAPI background callbacks and `run_in_background_context` for synchronous work delegated to a thread. Standard `asyncio.create_task` propagation is preserved by Python context variables.

## Core Operations

Create operations from application-owned or existing OpenTelemetry providers. The attribute policy must allow only contract-registered, bounded attributes.

```python
from lumens_observability import configure_observability, registered_attributes

operations = configure_observability(
    contract_version="1.0.0",
    attribute_policy=registered_attributes({"integration.provider"}),
)

result = operations.observe(
    "integration.enrich",
    lambda operation: enrich(),
    {"integration.provider": "example-provider"},
)
```

Set a bounded business outcome inside the callback when the result is known:

```python
def authorize(operation):
    result = authorize_payment()
    operation.set_outcome("approved" if result.approved else "declined")
    return result

result = operations.observe("payment.authorize", authorize)
```

Unhandled exceptions are recorded once and re-raised unchanged. `asyncio.CancelledError` remains control flow and receives the `cancelled` outcome without an error status.

## Async Operations

`observe_async` keeps the operation open until the awaited work completes:

```python
result = await operations.observe_async(
    "integration.enrich",
    lambda operation: integration_client.enrich(),
    {"integration.provider": "example-provider"},
)
```

Manual lifecycle is available through synchronous and asynchronous context managers. Call `fail` when application code handles a technical exception instead of allowing `observe` to handle it.

```python
async with operations.start("payment.authorize") as operation:
    operation.set_outcome("declined")
```

## Boundaries

- Core operations are for distinct internal work, not already instrumented HTTP, database, or messaging boundaries.
- Arguments, return values, payloads, secrets, and unregistered attributes are not captured automatically.
- The default policy drops all custom attributes until a contract-derived policy is supplied.
- Business-event delivery and policy enforcement are deferred to MVP-F07.

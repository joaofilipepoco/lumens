# Python Getting Started

MVP-F04 provides the framework-independent Python core API. FastAPI integration and logging correlation are delivered in MVP-F06.

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
- FastAPI, background-task, logging, and application-managed initialization support are deferred to MVP-F06.

# Business Events

Business events are explicit, registered point-in-time domain occurrences. They are not spans, metrics, or audit records.

## Event Contract

Before an event can be emitted, its static name, required attributes, privacy, and cardinality must be registered in the semantic contract. Dynamic values belong in approved attributes.

The default envelope contains:

```text
event.name
event.schema.version
lumens.contract.version
trace_id
span_id
registered event attributes
```

Trace and span identifiers are included only when an active OpenTelemetry span exists.

## Java

```java
var events = new BusinessEvents(
        registry,
        LumensAttributePolicies.registeredKeys(Set.of("integration.provider")),
        new StructuredLoggingBusinessEventSink(logger));

events.emit("integration.enrichment.completed", Map.of(
        "integration.provider", "example-provider"));
```

## Python

```python
events = BusinessEvents(
    "1.0.0",
    {"integration.enrichment.completed": {"integration.provider"}},
    registered_attributes({"integration.provider"}),
    structured_logging_sink(logger),
)
events.emit("integration.enrichment.completed", {"integration.provider": "example-provider"})
```

## Delivery And Failure Behavior

- Unknown event names, missing required fields, and fields rejected by policy are dropped.
- Sink failures return `false` in Java or `False` in Python and never fail application logic.
- The default structured logging sink is non-audit-grade. It provides no delivery guarantee.
- Durable audit or compliance events require a custom sink backed by a transactional outbox, message broker, or equivalent durable application-owned mechanism.
- Lumens does not automatically duplicate a business event as a span event or metric.

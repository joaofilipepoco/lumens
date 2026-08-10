# Java Getting Started

MVP-F03 provides the framework-independent Java core API. Spring Boot auto-configuration and zero-touch framework instrumentation are delivered in MVP-F05.

## Core Operations

Create operations from an application-owned OpenTelemetry instance. The attribute policy must allow only contract-registered, bounded attributes.

```java
var operations = LumensOperationsFactory.create(
        openTelemetry,
        "1.0.0",
        LumensAttributePolicies.registeredKeys(Set.of("integration.provider")));

var result = operations.observe(
        "integration.enrich",
        Map.of("integration.provider", "example-provider"),
        operation -> {
            var result = enrich();
            operation.setOutcome("success");
            return result;
        });
```

`observe` records unhandled runtime failures once, rethrows them unchanged, and closes the operation. Cancellation remains control flow and receives the `cancelled` outcome without an error status.

For handled failures or custom lifecycle control, use `start` and call `fail` before closing:

```java
try (LumensOperation operation = operations.start("payment.authorize", Map.of())) {
    operation.setOutcome("declined");
} catch (Exception error) {
    // Call fail only when the application handles the exception itself.
    throw error;
}
```

## Async Operations

`observeAsync` ends spans and records metrics when the returned `CompletionStage` completes. It does not end the operation when the stage is created.

```java
CompletionStage<Result> result = operations.observeAsync(
        "integration.enrich",
        Map.of("integration.provider", "example-provider"),
        operation -> client.enrich());
```

## Boundaries

- Core operations are for distinct internal work, not already instrumented HTTP, database, or messaging boundaries.
- Arguments, return values, payloads, secrets, and unregistered attributes are not captured automatically.
- The default policy drops all custom attributes until a contract-derived policy is supplied.
- `@ObservedOperation` is declared for the optional Spring integration in MVP-F05; it has no core runtime behavior in MVP-F03.

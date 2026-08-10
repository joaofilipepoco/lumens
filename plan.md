# Lumens Observability by Design Backend Accelerator

## Objective

Build a production-quality internal accelerator for Deloitte engineers implementing client solutions.

The accelerator will provide consistent observability for:

- Java 21 and Spring Boot 3.x applications.
- Python 3.11-3.13 and FastAPI applications.
- Distributed calls between Java and Python.
- Automatic standard telemetry for supported frameworks and libraries without application annotations or decorators.
- Custom operations, business outcomes, metrics, and business events.
- OTLP export through an OpenTelemetry Collector.

React and JavaScript are explicitly out of scope for this release.

## Core Principle

Use standard OpenTelemetry for telemetry mechanics and Lumens for:

- Developer ergonomics.
- Business semantics.
- Safe defaults.
- Privacy and cardinality controls.
- Cross-language consistency.
- Testing and governance.

Do not create a proprietary tracing system or replace OpenTelemetry APIs.

Standard technical telemetry must be automatic for supported frameworks and libraries. Developers must not need Lumens annotations or decorators for HTTP server and client spans, database and messaging instrumentation, context propagation, technical failures, runtime metrics, or log correlation. Explicit Lumens APIs are reserved for business semantics and optional custom internal operations that standard instrumentation cannot infer.

Java and Python SDKs must not call or directly depend on one another. They interoperate through:

- W3C `traceparent` and `tracestate`.
- OTLP.
- Shared semantic conventions.
- A shared machine-readable Lumens contract.

OpenTelemetry must create and propagate trace IDs, span IDs, and parent relationships. Do not generate custom trace IDs or add redundant `parent_id` attributes.

## Execution Instructions

The Build Agent must:

- Implement the complete backend MVP, not only scaffolding.
- Build in the currently empty workspace.
- Use Maven for Java.
- Use `uv`, `pyproject.toml`, and Hatchling for Python.
- Pin exact compatible dependency versions.
- Record the tested compatibility matrix.
- Use ASCII unless existing standards require otherwise.
- Never include credentials or client-specific information.
- Never publish packages or create commits unless separately requested.
- Keep observability failures from failing application requests.
- Run all feasible tests and report anything that cannot run.

## Naming

Use stable accelerator coordinates:

| Item | Value |
|---|---|
| Maven group | `com.deloitte.lumens` |
| Java base package | `com.deloitte.lumens.observability` |
| Python distribution | `lumens-observability` |
| Python import | `lumens_observability` |
| Instrumentation scope | `com.deloitte.lumens.observability` |
| Default telemetry namespace | `lumens` |

Client customization must not require forking or renaming the SDKs.

Client-specific customization must be supported through:

- Standard `OTEL_*` configuration.
- Client contract overlays.
- Generated client semantic constants.
- Collector configuration overlays.
- Pluggable event sinks and policy extensions.

The generator must allow client-specific generated Java packages and Python modules while retaining the stable Lumens core packages.

## Repository Layout

```text
/
  plan.md
  README.md
  docs/
    architecture.md
    getting-started-java.md
    getting-started-python.md
    instrumentation-modes.md
    semantic-contract.md
    business-events.md
    privacy-and-cardinality.md
    client-customization.md
    troubleshooting.md
    compatibility.md
    adr/
      001-opentelemetry-foundation.md
      002-explicit-instrumentation-modes.md
      003-business-event-delivery.md
      004-semantic-registry.md
      005-browser-deferred.md

  contract/
    lumens-contract.yaml
    lumens-contract.schema.json
    examples/
      client-overlay.yaml
    generated/

  tools/
    contract/
      pyproject.toml
      src/
      tests/

  java/
    pom.xml
    lumens-observability-api/
    lumens-observability-spring-boot-autoconfigure/
    lumens-observability-spring-boot-starter/
    lumens-observability-spring-boot-runtime/
    lumens-observability-test/
    lumens-observability-bom/

  python/
    pyproject.toml
    uv.lock
    src/lumens_observability/
    tests/

  collector/
    local/
    production-reference/
    tests/

  examples/
    java-bff/
    python-integration/
    cross-service/
      compose.yaml
      tests/

  scripts/
    verify.ps1
    verify.sh
```

## Compatibility Baseline

Support:

- Java 21.
- Maven 3.9 or newer.
- A currently supported Spring Boot 3.x release.
- Spring MVC and Spring WebFlux.
- Python 3.11, 3.12, and 3.13.
- A current compatible FastAPI and Starlette release.
- OTLP over gRPC for backend services.
- OTLP over HTTP where configured.

Do not claim Spring Boot 4, native-image, older Java, or older Python compatibility without tests.

Resolve current compatible OpenTelemetry versions during implementation. Pin versions centrally rather than using dynamic versions.

## Instrumentation Modes

Support two explicit modes.

### Platform-Managed Mode

This is the recommended production mode.

Java:

- OpenTelemetry Java agent initializes telemetry.
- Lumens consumes the global OpenTelemetry APIs.
- Lumens must not create another provider or exporter.

Python:

- `opentelemetry-instrument` initializes telemetry.
- Lumens instruments FastAPI and provides business helpers without replacing providers.

In both languages, supported standard telemetry must work without source-code annotations or decorators. Lumens must not wrap an already instrumented framework boundary with a duplicate operation span.

### Application-Managed Mode

Use where agents or zero-code bootstrap are unsuitable.

Java:

- `lumens-observability-spring-boot-runtime` uses the official OpenTelemetry Spring Boot starter.
- The runtime configures providers and OTLP from standard `OTEL_*` settings.

Python:

- `configure_observability()` creates providers, processors, and exporters.
- `instrument_fastapi(app)` instruments the application.

### Conflict Handling

- Never silently initialize a second provider.
- Make the mode explicit.
- Detect agent/runtime conflicts where reliable detection exists.
- Fail startup for clear conflicting Lumens artifacts or modes.
- Emit actionable diagnostics for possible external-agent conflicts.
- Make initialization idempotent.
- Test repeated initialization and duplicate instrumentation.

## Semantic Contract

Create a YAML registry validated by JSON Schema.

The registry must define:

- Contract name and semantic version.
- Custom namespace.
- Operations.
- Allowed outcomes.
- Custom attributes.
- Business events.
- Metric dimensions.
- Baggage keys.
- Privacy classification.
- Cardinality classification.
- Attribute types.
- Required and optional fields.
- Owners and descriptions.
- Stability and deprecation status.

Example:

```yaml
contract:
  name: lumens
  version: 1.0.0
  namespace: lumens

operations:
  integration.enrich:
    description: Enrich data using an external integration
    owner: integration
    outcomes:
      - success
      - unavailable
      - rejected
      - failure

attributes:
  integration.provider:
    type: string
    privacy: internal
    cardinality: bounded
    allowed_values:
      - example-provider

events:
  integration.enrichment.completed:
    description: An integration enrichment completed
    owner: integration
    delivery: log
    required_attributes:
      - integration.provider
      - lumens.operation.outcome
```

Implement a generator that:

- Validates base contracts and client overlays.
- Rejects incompatible types and duplicate definitions.
- Generates Java constants.
- Generates Python constants.
- Supports configurable Java output package.
- Supports configurable Python output module.
- Produces deterministic output.
- Has a `--check` mode for CI.
- Never rewrites runtime attribute names dynamically.

## Operation Semantics

Use these standard Lumens attributes:

```text
lumens.operation.name
lumens.operation.outcome
lumens.contract.version
```

Use these metrics:

```text
lumens.operation.executions
lumens.operation.duration
```

Metric requirements:

- Execution metric is a counter.
- Duration metric is a histogram measured in seconds.
- Allowed dimensions are operation name and bounded outcome.
- IDs, users, tenants, URLs, exception messages, and payload values must never be dimensions.
- Metrics must be recorded independently of trace sampling.

Operation behavior:

- Span name equals the registered low-cardinality operation name.
- Default span kind is `INTERNAL`.
- Initial attributes are supplied when starting the span.
- Successful operations leave OTel status unset.
- Unhandled failures record the exception once and set `ERROR`.
- Failures include standard `error.type` where available.
- Cancellation is rethrown and does not become an error by default.
- Default outcomes are `success`, `failure`, and `cancelled`.
- Business outcomes such as `declined` or `unavailable` need not imply an OTel error.
- Operation spans always end exactly once.
- Arguments, return values, payloads, and arbitrary object strings are never captured automatically.
- Custom operation APIs are optional and must not be required for standard framework or library telemetry.
- Documentation must discourage custom operation instrumentation around an already instrumented boundary unless it represents a distinct business operation.

## Java Implementation

### Modules

`lumens-observability-api`:

- Depend only on stable OpenTelemetry APIs and minimal logging APIs.
- Provide `ObservedOperation`.
- Provide `LumensOperation`.
- Provide `LumensOperations`.
- Provide `BusinessEvent`.
- Provide `BusinessEventSink`.
- Provide policy and validation interfaces.
- Preserve direct access to standard `Tracer`, `Meter`, `Span`, and `Context`.

`lumens-observability-spring-boot-autoconfigure`:

- Configure Lumens beans.
- Add the annotation aspect.
- Bind Lumens-specific policy settings.
- Validate required resource configuration.
- Detect conflicting Lumens modes.
- Never own standard exporter configuration.

`lumens-observability-spring-boot-starter`:

- Provide platform-managed convenience dependencies.
- Do not initialize an OpenTelemetry SDK.

`lumens-observability-spring-boot-runtime`:

- Provide application-managed dependencies.
- Integrate the official OpenTelemetry Spring Boot starter.
- Back off or fail on conflicting provider initialization.

`lumens-observability-test`:

- Provide in-memory span and metric capture.
- Provide assertions for names, parentage, attributes, outcomes, and metrics.
- Provide Spring test utilities.

`lumens-observability-bom`:

- Align all Lumens and tested OpenTelemetry versions.

### Java API Example

Spring controllers, supported clients, repositories, and messaging integrations receive standard telemetry without `ObservedOperation`. Use the annotation or programmatic API only for a meaningful custom internal operation that standard instrumentation does not represent.

```java
@ObservedOperation("integration.enrich")
public EnrichmentResult enrich(Request request) {
    return integrationClient.enrich(request);
}
```

```java
try (LumensOperation operation =
        operations.start("payment.authorize", attributes)) {
    var result = authorize();
    operation.setOutcome(result.approved() ? "approved" : "declined");
    return result;
} catch (Exception exception) {
    throw exception;
}
```

The programmatic API must handle exception recording through an execution callback API as well as manual lifecycle usage. Clearly document that manual usage must call the failure method when exceptions are handled outside a Lumens callback.

### Java Async Requirements

Test and correctly support:

- Synchronous methods.
- `CompletionStage`.
- `CompletableFuture`.
- Reactor `Mono`.
- Reactor `Flux`.
- Success, error, and cancellation.
- Reactor multiple subscriptions.
- Context propagation across supported executors.
- No premature span completion.
- No leaked thread-local scope.

Spring proxy self-invocation limitations must be documented. The programmatic API is the escape hatch.

## Python Implementation

Provide:

- `configure_observability()`.
- `instrument_fastapi(app)`.
- `shutdown_observability()`.
- `force_flush()`.
- `observed_operation()`.
- `operation()`.
- `emit_business_event()`.
- `add_checkpoint()`.
- Test fixtures and in-memory exporters.

### Python API Example

FastAPI routes and supported libraries receive standard telemetry without `observed_operation`. Use the decorator or context manager only for a meaningful custom internal operation that standard instrumentation does not represent.

```python
@observed_operation("integration.enrich")
async def enrich(request: EnrichmentRequest) -> EnrichmentResult:
    return await integration_client.enrich(request)
```

```python
async with operation("payment.authorize") as current:
    result = await authorize()
    current.set_outcome("approved" if result.approved else "declined")
```

The operation API must support:

- Synchronous decorators.
- Asynchronous decorators.
- Synchronous context managers.
- Asynchronous context managers.
- Preserved function metadata and signatures.
- Nested operations.
- Disabled/no-provider operation.
- Correct `contextvars` restoration.
- `asyncio.create_task`.
- `TaskGroup`.
- `asyncio.to_thread`.
- FastAPI background tasks with explicit captured context.
- Cancellation without erroneous failure status.

Do not replace Python's standard `logging` API.

## Business Events

Business events are point-in-time domain occurrences, not spans.

Business events are emitted explicitly because their occurrence and attributes cannot be inferred safely. Prefer an emission call over an annotation so application code can emit events conditionally and at the precise domain decision point.

Provide:

- `BusinessEventSink` in Java.
- Equivalent Python protocol.
- A default structured logging sink.
- Schema validation against the semantic registry.
- Trace and span correlation when an active span exists.
- A separate checkpoint API for adding span events.

The default event representation must include:

```text
event.name
event.schema.version
lumens.contract.version
trace_id
span_id
registered event attributes
```

Rules:

- Event names are static and registered.
- Dynamic values belong in attributes.
- Invalid or sensitive fields are dropped with rate-limited diagnostics.
- Event emission failures never fail application logic.
- Do not automatically emit the same occurrence as a log, span event, and metric.
- Default logged events are not audit-grade.
- Document that durable audit requirements need a custom sink, transactional outbox, or message broker.

## Privacy and Cardinality

Classify every custom field as one of:

- Public bounded.
- Internal bounded.
- Internal high-cardinality.
- Pseudonymous.
- Personal or sensitive.
- Secret.

Default rules:

- Secrets are always rejected.
- Personal data is rejected unless explicitly approved.
- High-cardinality values are prohibited from metrics.
- Request and response bodies are never captured.
- Authorization, cookies, tokens, and credentials are never captured.
- Raw user and tenant IDs are prohibited by default.
- URLs must not include uncontrolled query values.
- Baggage is disabled unless keys are explicitly registered.
- Baggage must never be trusted for authorization.

Runtime policy violations must be dropped or warned about without breaking application requests. Test and CI validation may fail strictly.

## Logging Correlation

Java:

- Preserve SLF4J and Logback.
- Use standard OTel trace correlation.
- Ensure active logs expose trace ID, span ID, and sampling state.
- Avoid installing duplicate appenders.

Python:

- Preserve standard `logging`.
- Support trace correlation without replacing existing handlers.
- Avoid duplicate handlers.
- Keep OTLP log export optional because Python log signal integrations remain less stable than tracing.

## Collector Assets

Provide:

- Local development Collector configuration.
- Production reference configuration.
- OTLP gRPC and HTTP receivers.
- Memory limiter and batching.
- Health checks.
- Attribute removal and redaction.
- Environment-based upstream endpoint configuration.
- Collector self-observability.
- No embedded credentials.
- No direct browser endpoint.

The local environment should allow developers to inspect traces without requiring a commercial vendor.

The production reference must remain vendor-neutral and export through OTLP.

## Reference Applications

### Java BFF

Create a Spring Boot BFF that:

- Exposes an HTTP endpoint.
- Receives an automatic HTTP server span without annotating the endpoint.
- Calls the Python FastAPI service.
- Creates an automatic HTTP client span without annotating the client call.
- Propagates `traceparent`.
- Creates one registered Lumens operation for a distinct internal business operation.
- Records a bounded outcome.
- Emits one registered business event.
- Contains no real PII.

### Python Integration Service

Create a FastAPI service that:

- Receives the Java request.
- Continues the incoming trace through an automatic FastAPI server span without decorating the route.
- Creates a nested Lumens operation.
- Simulates an external integration with automatic supported-client instrumentation.
- Records a bounded outcome.
- Demonstrates async context propagation.
- Emits one registered business event.

## Cross-Language Verification

The integration test must prove:

- Java and Python spans share the same trace ID.
- The Python server span is a descendant of the Java client span.
- Each operation has a distinct span ID.
- Standard HTTP spans are not duplicated.
- Standard server and client spans and propagation require no Lumens annotations or decorators.
- Custom operation spans appear only where explicitly requested for distinct internal operations.
- Service resource names remain distinct.
- Logs and business events contain trace correlation.
- Business metrics exist even when traces are not sampled.
- Invalid `traceparent` values do not crash either service.
- Collector unavailability does not fail application requests.
- Forbidden test secrets never appear in captured telemetry.

Capture normalized OTLP output and compare semantic golden fixtures. Ignore timestamps, generated IDs, ordering, and other nondeterministic fields.

## Required Testing

Java tests:

- Unit tests with OTel in-memory exporters.
- Spring auto-configuration tests.
- Zero-touch Spring server and supported-client instrumentation tests.
- Optional custom-operation annotation tests.
- CompletionStage and Reactor tests.
- Agent-mode integration test.
- Application-managed integration test.
- Conflict and duplicate initialization tests.

Python tests:

- Unit tests with in-memory exporters.
- Zero-touch FastAPI ASGI and supported-client instrumentation tests.
- Optional sync and async custom-operation decorator tests.
- Background task tests.
- Context leakage tests across concurrent requests.
- Repeated initialization tests.
- Existing logging coexistence tests.

Contract tests:

- JSON Schema validation.
- Invalid privacy and cardinality combinations.
- Duplicate names.
- Invalid namespace.
- Breaking overlay changes.
- Deterministic generation.
- Generated Java and Python parity.

Collector tests:

- Configuration validation.
- Redaction tests.
- OTLP receiver tests.
- Export failure behavior.

## Documentation Requirements

Document:

- Five-minute Java setup.
- Five-minute Python setup.
- Agent versus application-managed mode.
- Which standard telemetry is automatic and requires no source annotations or decorators.
- When optional custom operation instrumentation is appropriate and how to avoid duplicate spans.
- Java-to-Python context propagation.
- When to use a span, span event, metric, log, or business event.
- Client contract customization.
- Privacy and cardinality rules.
- Sampling behavior.
- Duplicate instrumentation troubleshooting.
- Async and reactive limitations.
- Package publication instructions using environment-provided credentials.
- Supported versions and tested dependency matrix.

## Implementation Order

1. Create the repository structure and root documentation.
2. Implement the semantic registry schema and validator.
3. Implement deterministic Java and Python code generation.
4. Implement Java API and in-memory test support.
5. Implement Spring zero-touch standard instrumentation, auto-configuration, starter, runtime, and optional annotation behavior.
6. Implement Python zero-touch standard instrumentation, core business helpers, FastAPI integration, optional decorators, and test support.
7. Implement structured business-event sinks.
8. Implement Collector local and production reference configurations.
9. Build Java and Python reference applications.
10. Implement cross-language OTLP verification.
11. Add verification scripts and CI-ready checks.
12. Run all tests and update the compatibility document with actual results.

## Verification Commands

The Build Agent should provide working equivalents of:

```powershell
mvn -f java/pom.xml verify
uv sync --project python --all-extras
uv run --project python pytest
uv run --project tools/contract pytest
uv run --project tools/contract lumens-contract generate --check
docker compose -f examples/cross-service/compose.yaml up --build --abort-on-container-exit
.\scripts\verify.ps1
```

Also provide a POSIX `scripts/verify.sh`.

## Definition of Done

The MVP is complete only when:

- Java and Python packages build successfully.
- Unit and integration tests pass.
- The semantic generator produces matching Java and Python definitions.
- The Java BFF and Python service produce one correctly connected trace.
- Supported standard server and client telemetry works without Lumens annotations or decorators.
- No duplicate HTTP spans are present.
- Operation metrics are emitted independently from trace sampling.
- Business events are validated and correlated.
- Sensitive test markers are absent from exported telemetry.
- Platform-managed and application-managed modes are documented and tested.
- Collector outage tests prove application requests continue.
- All dependencies are pinned.
- Compatibility results are documented.
- No React or JavaScript implementation is included.
- No package is published and no repository commit is created automatically.

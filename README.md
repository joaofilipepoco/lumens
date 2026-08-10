# Lumens Observability by Design

Lumens is a planned, vendor-neutral observability accelerator for Java/Spring Boot and Python/FastAPI services. It combines standard OpenTelemetry instrumentation with governed business semantics, safe defaults, and consistent developer APIs.

> [!IMPORTANT]
> This repository is currently in the design phase. The SDKs and commands described below are target capabilities, not yet released packages. See [`plan.md`](plan.md) for the complete implementation specification and acceptance criteria.

## Why Lumens

OpenTelemetry already handles trace and span creation, context propagation, instrumentation, and export. Lumens does not replace it. Lumens adds the conventions and controls needed to apply it consistently across client solutions:

- Zero-code standard telemetry for supported frameworks and libraries.
- Explicit APIs for business events, outcomes, and meaningful custom operations.
- End-to-end context propagation between Java and Python services.
- Consistent business outcomes, metrics, and structured business events.
- A machine-readable semantic contract shared by both languages.
- Privacy, sensitive-data, and metric-cardinality safeguards.
- Vendor-neutral OTLP export through an OpenTelemetry Collector.
- Test utilities that verify telemetry behavior rather than only application behavior.

## Design Principles

- **OpenTelemetry-native:** use standard OTel APIs, W3C Trace Context, semantic conventions, and OTLP.
- **Thin and interoperable:** avoid proprietary replacements for tracers, meters, loggers, or propagators.
- **Safe by default:** never capture arguments, payloads, credentials, or arbitrary headers automatically.
- **Business-aware:** distinguish technical errors from valid business outcomes such as `declined`.
- **Low cardinality:** use stable operation names and bounded metric dimensions.
- **Failure-isolated:** telemetry failures must never fail application requests.
- **Client-configurable:** customize semantic catalogs and policies without forking the Lumens SDKs.

## Architecture

```text
Java/Spring Boot BFF                    Python/FastAPI integration
+--------------------------+           +--------------------------+
| OTel auto-instrumentation |           | OTel auto-instrumentation |
| Lumens operation API      |           | Lumens operation API      |
| Lumens semantic contract  |           | Lumens semantic contract  |
+------------+-------------+           +-------------+------------+
             |       W3C trace context                |
             +--------------------------------------->|
             |                                        |
             +------------------+---------------------+
                                | OTLP
                                v
                   +--------------------------+
                   | OpenTelemetry Collector  |
                   | policy, redaction, batch |
                   +------------+-------------+
                                |
                                v
                   Observability backend(s)
```

Java and Python SDKs do not directly depend on or communicate with each other. They remain compatible through:

- W3C `traceparent` and `tracestate` propagation.
- OpenTelemetry APIs and semantic conventions.
- A shared versioned Lumens contract.
- OTLP export through a Collector.

OpenTelemetry owns trace IDs, span IDs, and parent relationships. Lumens does not generate duplicate correlation identifiers.

## Planned Components

| Component | Purpose |
|---|---|
| Java API | Business events, outcomes, optional custom operations, and policy interfaces |
| Spring Boot integration | Auto-configuration for platform-managed and application-managed modes |
| Python SDK | Business events, outcomes, optional custom operations, lifecycle, and FastAPI integration |
| Semantic contract | YAML registry and JSON Schema for operations, attributes, outcomes, events, and baggage |
| Contract generator | Deterministic Java and Python constants with client overlay support |
| Collector assets | Local and production-reference OTLP pipelines, redaction, limits, and batching |
| Test kits | In-memory telemetry assertions and cross-language conformance tests |
| Reference services | Spring Boot BFF calling a FastAPI integration service |

## Scope

### Backend MVP

- Java 21 and Spring Boot 3.x.
- Spring MVC and Spring WebFlux.
- Python 3.11-3.13 and FastAPI.
- OTLP over gRPC, with HTTP available where configured.
- Java agent and Python zero-code instrumentation profiles.
- Application-managed instrumentation where agents are unsuitable.
- Automatic standard spans and metrics for supported frameworks and libraries.
- Optional custom spans, bounded operation metrics, business outcomes, and structured events.
- SLF4J/Logback and Python `logging` trace correlation.
- Shared semantic contracts and client overlays.
- Local and production-reference Collector configurations.

### Not in the MVP

- React or browser JavaScript instrumentation.
- Audit-grade event delivery.
- Continuous profiling.
- Broad legacy runtime support.
- Vendor-specific telemetry APIs.
- Automatic request or response payload capture.

## Instrumentation Modes

Lumens will support two explicit modes. Applications must select one to prevent duplicate providers, exporters, and spans.

### Platform-Managed

Recommended for production:

- Java uses the OpenTelemetry Java agent.
- Python uses `opentelemetry-instrument`.
- Lumens consumes the existing OpenTelemetry providers and adds business instrumentation without duplicating standard spans.

### Application-Managed

For environments where agents or zero-code bootstrap cannot be used:

- Java uses the Lumens runtime with the official OpenTelemetry Spring Boot starter.
- Python uses `configure_observability()` and `instrument_fastapi(app)`.
- Standard `OTEL_*` variables remain authoritative for SDK and exporter configuration.

Lumens must detect clear configuration conflicts, initialize idempotently, and never silently replace an application-owned OpenTelemetry provider.

## Intended Developer Experience

The following examples show the target API. Package artifacts are not available yet.

### Standard Observability

Supported HTTP servers, HTTP clients, database clients, messaging libraries, runtime metrics, context propagation, technical failures, and log correlation are instrumented automatically. Developers do not add Lumens annotations or decorators to Spring controllers, FastAPI routes, repositories, or supported clients.

Standard instrumentation is the default. Lumens must reuse OpenTelemetry instrumentation rather than create a second span or metric for an already instrumented boundary.

### Business Telemetry

Developers explicitly emit registered business events and set business outcomes because these semantics cannot be inferred reliably from framework activity. Business events use an emission API rather than an annotation because an event may occur conditionally within an operation.

### Optional Custom Operations

Annotations, decorators, and context managers are escape hatches for meaningful internal operations that are not already represented by standard instrumentation. They are not required for baseline observability and should not be placed on already instrumented framework boundaries solely to obtain telemetry.

### Java

```java
@ObservedOperation("integration.enrich")
public EnrichmentResult enrich(Request request) {
    return integrationClient.enrich(request);
}
```

```java
return operations.observe("payment.authorize", operation -> {
    var result = authorize();
    operation.setOutcome(result.approved() ? "approved" : "declined");
    return result;
});
```

### Python

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

Both APIs will:

- Create child spans from the active context.
- Support synchronous and asynchronous execution.
- End spans exactly once.
- Record unhandled failures and rethrow them unchanged.
- Treat cancellation as control flow by default.
- Record operation metrics independently of trace sampling.
- Avoid automatically serializing arguments, return values, or payloads.

## Business Telemetry

Lumens intentionally distinguishes telemetry signals:

| Need | Signal |
|---|---|
| Operation with meaningful duration | Span |
| Trace-local checkpoint | Span event |
| Count, rate, distribution, or SLO | Metric |
| Independently queryable occurrence | Structured business event |
| Troubleshooting narrative | Structured log |
| Property of an operation | Span attribute |

The initial operation model uses:

```text
lumens.operation.name
lumens.operation.outcome
lumens.contract.version

lumens.operation.executions
lumens.operation.duration
```

An expected business result such as `payment declined` can have `lumens.operation.outcome=declined` without marking the span as a technical error.

## Semantic Contracts

Each solution can extend the base Lumens registry with a client overlay. Contracts describe:

- Registered operation and event names.
- Attribute names, types, and allowed values.
- Business outcomes.
- Metric dimensions.
- Privacy and cardinality classifications.
- Approved baggage keys.
- Ownership, stability, and deprecation metadata.

The planned generator validates overlays and produces matching Java and Python constants. This keeps runtime package identities stable while allowing client-specific semantics.

```yaml
contract:
  name: lumens
  version: 1.0.0
  namespace: lumens

operations:
  integration.enrich:
    owner: integration
    outcomes: [success, unavailable, rejected, failure]

attributes:
  integration.provider:
    type: string
    privacy: internal
    cardinality: bounded
```

## Privacy and Safety

Lumens applies source-level controls before telemetry reaches the Collector:

- Secrets are always rejected.
- Personal data is rejected unless explicitly approved.
- Request and response bodies are not captured.
- Authorization headers, cookies, tokens, and credentials are not captured.
- Raw user and tenant IDs are prohibited by default.
- High-cardinality fields cannot be metric dimensions.
- Baggage is deny-by-default and must never be used for authorization.
- Policy violations produce bounded diagnostics without breaking application traffic.

Collector redaction is defense in depth, not a substitute for safe instrumentation.

## Repository Status

The repository currently contains the executable implementation plan:

```text
.
|-- README.md
`-- plan.md
```

The planned repository structure, implementation order, verification commands, and Definition of Done are maintained in [`plan.md`](plan.md).

## Development Prerequisites

The target build requires:

- JDK 21.
- Maven 3.9 or newer.
- Python 3.11, 3.12, or 3.13.
- [`uv`](https://docs.astral.sh/uv/).
- Docker with Compose for cross-service tests.
- PowerShell or a POSIX-compatible shell.

## Planned Verification

Once the implementation exists, the repository must provide working equivalents of:

```powershell
mvn -f java/pom.xml verify
uv sync --project python --all-extras
uv run --project python pytest
uv run --project tools/contract pytest
uv run --project tools/contract lumens-contract generate --check
docker compose -f examples/cross-service/compose.yaml up --build --abort-on-container-exit
.\scripts\verify.ps1
```

The cross-language test must verify that Java and Python spans share one trace, preserve correct parentage, avoid duplicate HTTP spans, and continue serving requests when telemetry export is unavailable.

## Package Identity

| Item | Value |
|---|---|
| Maven group | `com.deloitte.lumens` |
| Java package | `com.deloitte.lumens.observability` |
| Python distribution | `lumens-observability` |
| Python import | `lumens_observability` |
| Instrumentation scope | `com.deloitte.lumens.observability` |
| Default semantic namespace | `lumens` |

These identities remain stable across client implementations. Client-specific service names, versions, environments, semantic catalogs, policies, and Collector destinations are configuration rather than forks.

## Contributing

Before implementing a change:

1. Confirm it follows the architecture and scope in [`plan.md`](plan.md).
2. Prefer standard OpenTelemetry behavior over a new Lumens abstraction.
3. Add tests for emitted telemetry, context propagation, privacy, and failure isolation.
4. Update contracts and generated definitions together.
5. Document compatibility changes and any dependency constraints.
6. Do not commit credentials, customer data, or customer-specific identifiers.

## Security

Do not report vulnerabilities or disclose customer information through public channels. Follow Deloitte's approved internal security reporting process. Never include production telemetry, access tokens, credentials, personal data, or client-confidential information in an issue or test fixture.

## License

Licensing and distribution terms for this internal accelerator are to be defined before package publication. Third-party dependencies remain subject to their respective licenses.

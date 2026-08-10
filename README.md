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
- Vendor-neutral OTLP export to managed observability providers.
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
| Lumens business telemetry |           | Lumens business telemetry |
| Lumens semantic contract  |           | Lumens semantic contract  |
+------------+-------------+           +-------------+------------+
             |       W3C trace context                |
             +--------------------------------------->|
             |                                        |
             +------------------+---------------------+
                                | standard OTLP
                                v
                +----------------------------------+
                | Provider-managed OTLP endpoint, |
                | agent, or supported Collector   |
                +----------------+-----------------+
                                 v
                   Managed observability provider
```

Java and Python SDKs do not directly depend on or communicate with each other. They remain compatible through:

- W3C `traceparent` and `tracestate` propagation.
- OpenTelemetry APIs and semantic conventions.
- A shared versioned Lumens contract.
- Standard OTLP and a shared semantic contract.

OpenTelemetry owns trace IDs, span IDs, and parent relationships. Lumens does not generate duplicate correlation identifiers.

## Planned Components

| Component | Purpose |
|---|---|
| Java API | Business events, outcomes, optional custom operations, and policy interfaces |
| Spring Boot integration | Auto-configuration for platform-managed and application-managed modes |
| Python SDK | Business events, outcomes, optional custom operations, lifecycle, and FastAPI integration |
| Semantic contract | YAML registry and JSON Schema for operations, attributes, outcomes, events, and baggage |
| Contract generator | Deterministic Java and Python constants with client overlay support |
| Provider profiles | Tested deployment configuration for certified managed providers |
| OTLP test harness | Optional development and CI inspection; never deployed as solution infrastructure |
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
- Certified profiles for Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, and New Relic.
- Optional in-process or ephemeral OTLP test tooling for development and conformance testing.

### Not in the MVP

- JavaScript and TypeScript runtimes or frameworks.
- Audit-grade event delivery.
- Continuous profiling.
- Broad legacy runtime support.
- Vendor-specific telemetry APIs.
- Automatic request or response payload capture.
- A Deloitte-managed production Collector or telemetry gateway.
- AI agent and GenAI workload instrumentation.
- Automated GenAI creation of provider dashboards and other assets.

## Product Roadmap

The roadmap separates the current managed-services-first MVP from optional later product phases:

| Stage | Scope |
|---|---|
| MVP | Java/Spring Boot, Python/FastAPI, automatic standard telemetry, governed business telemetry, and provider-managed ingestion profiles |
| Phase 1 | Optional organization-managed OpenTelemetry Collector gateway |
| Phase 2 | JavaScript and TypeScript ecosystem for Node.js, NestJS, Next.js, React, and Angular |
| Phase 3 | AI agent and GenAI workload observability |
| Phase 4 | Lumens Experience Generator for dashboards, alerts, monitors, and SLOs |

Phase 1 is optional because operating a production gateway introduces infrastructure, security, availability, cost, and maintenance responsibilities. The MVP remains valid without it.

Phase 2 should provide one TypeScript SDK distribution with runtime-specific entry points rather than one universal runtime implementation. Node.js and NestJS use server-side OpenTelemetry; Next.js requires separate server, browser, and Edge handling; React and Angular use browser-safe instrumentation. Browser bundles must never contain provider access tokens and must use a provider-supported public RUM route or a secure ingestion proxy. Consent, Web Vitals, route changes, errors, fetch/XHR tracing, propagation allowlists, and strict PII controls are required before browser support can be certified.

Phase 3 will add governed observability for agent runs, workflows, model calls, tool use, retrieval, guardrails, handoffs, token usage, and cost. Phase 4 is described under Future Platform Options and remains independent of application instrumentation.

## Incremental Delivery

The MVP is delivered as independently requested features, not as one implementation request. Each feature in [`plan.md`](plan.md) has a stable identifier, prerequisites, scope, and acceptance criteria. Request a feature by identifier, for example: `Implement MVP-F03`.

Only the requested feature and its explicitly approved prerequisites are implemented in a delivery. Each delivery must leave the repository buildable, run the feature's feasible verification, update affected architecture or contract documentation, and report deferred work. Completing all MVP features is required for the overall MVP Definition of Done; completing one feature does not imply that later features have been started.

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

Instrumentation mode and export destination are independent decisions. A service uses either platform-managed or application-managed instrumentation, then selects a destination profile through deployment configuration.

## Managed Provider Destinations

The MVP certified destinations are Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, and New Relic. Each profile uses the provider's managed OTLP endpoint or provider-managed ingestion component. Lumens and Deloitte do not deploy or operate an OpenTelemetry Collector as part of the MVP solution.

```text
LUMENS_PROVIDER=dynatrace
OTEL_EXPORTER_OTLP_ENDPOINT=https://provider-endpoint.example
LUMENS_ACCESS_TOKEN=<deployment-secret>
```

Standard `OTEL_*` configuration remains authoritative. `LUMENS_PROVIDER` selects tested authentication, protocol, and signal conventions because these details differ by provider. Credentials come from a deployment secret manager, use least privilege, support rotation, and must never enter source code or telemetry.

Lumens defines three support levels:

| Level | Commitment |
|---|---|
| Certified | Documented and tested end to end by Lumens |
| OTLP-compatible | Expected to work through standard OTLP but not formally guaranteed |
| Custom | Configured and validated by the client |

Changing between certified providers requires no application source-code changes or rebuild. Only deployment configuration, credentials, provider-supported infrastructure, and provider-owned assets change. Historical data, dashboards, alerts, SLOs, proprietary queries, retention policies, and provider-specific topology do not migrate automatically.

Provider setup and migration documentation will live under `docs/providers/`, with dedicated guides for all certified destinations, a compatibility matrix, and a provider-switching runbook. Current endpoints, headers, and capabilities must be verified against official provider documentation during implementation rather than embedded as assumptions in Lumens core.

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

Lumens applies source-level controls before telemetry leaves the application:

- Secrets are always rejected.
- Personal data is rejected unless explicitly approved.
- Request and response bodies are not captured.
- Authorization headers, cookies, tokens, and credentials are not captured.
- Raw user and tenant IDs are prohibited by default.
- High-cardinality fields cannot be metric dimensions.
- Baggage is deny-by-default and must never be used for authorization.
- Policy violations produce bounded diagnostics without breaking application traffic.

Provider or Collector redaction is defense in depth, not a substitute for safe instrumentation.

## Future Platform Options

Phase 1 may provide an organization-managed OpenTelemetry gateway for centralized credentials, persistent queues, routing, sampling, redaction, dual-provider export, regional availability, and destination-specific enrichment. It is not required for the MVP architecture.

Phase 3 may add AI agent and GenAI workload observability using stable OpenTelemetry GenAI semantic conventions where available. It will cover agent and workflow runs, model requests, tool calls, retrieval operations, retries, fallbacks, guardrail decisions, human approvals, multi-agent handoffs, token usage, estimated cost, and business outcomes.

Agent telemetry must not capture prompts, responses, conversation history, retrieved documents, tool arguments, tool results, credentials, or customer data by default. Framework integrations such as LangChain/LangGraph, Semantic Kernel, AutoGen, CrewAI, and model-provider SDKs require individual compatibility and privacy validation before certification.

Phase 4 may add a **Lumens Experience Generator**. It will derive a vendor-neutral asset specification from the semantic contract, service metadata, and a solution archetype, then use provider adapters for Dynatrace, Splunk, Datadog, Grafana, and New Relic to propose dashboards, alerts, monitors, and SLOs, including agent-specific assets when Phase 3 telemetry is available.

The generator must use `generate`, `plan`, and explicitly approved `apply` stages. Provider tokens must never be exposed to a language model; production telemetry, payloads, PII, and customer data must not be sent to GenAI. Generated assets must be schema-validated, idempotent, auditable, version-tagged, drift-aware, and backed by deterministic templates when GenAI is unavailable.

## Architecture Documentation

Architecture will be maintained as version-controlled Markdown with Mermaid diagrams rather than one monolithic document. The documentation will provide:

- A system context showing applications, Lumens, managed providers, users, and external dependencies.
- Component views for the Java SDK, Python SDK, semantic contract, generator, provider profiles, and OTLP test harness.
- Sequence diagrams for automatic instrumentation, context propagation, business telemetry, provider export, failure isolation, and provider switching.
- Deployment views for MVP provider-managed ingestion and the optional Phase 1 organization-managed gateway.
- Trust-boundary views covering application data, credentials, browser telemetry, GenAI, and provider APIs.
- A roadmap view for the MVP and Phases 1 through 4.
- Architecture Decision Records for durable choices and their consequences.

Every phase must document scope, exclusions, responsibilities, data flows, APIs and contracts, security and privacy boundaries, deployment topology, failure modes, compatibility, testing, operational ownership, and Definition of Done. Provider guides remain separate because endpoints, authentication, signal support, and limitations change independently from the core architecture.

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

The cross-language test must verify that Java and Python spans share one trace, preserve correct parentage, avoid duplicate HTTP spans, and continue serving requests when provider ingestion is unavailable.

## Package Identity

| Item | Value |
|---|---|
| Maven group | `com.deloitte.lumens` |
| Java package | `com.deloitte.lumens.observability` |
| Python distribution | `lumens-observability` |
| Python import | `lumens_observability` |
| Instrumentation scope | `com.deloitte.lumens.observability` |
| Default semantic namespace | `lumens` |

These identities remain stable across client implementations. Client-specific service names, versions, environments, semantic catalogs, policies, and provider destinations are configuration rather than forks.

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

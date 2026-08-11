# Lumens Observability by Design Backend Accelerator

## Objective

Build a production-quality internal accelerator for Deloitte engineers implementing client solutions.

The accelerator will provide consistent observability for:

- Java 21 and Spring Boot 3.x applications.
- Python 3.11-3.13 and FastAPI applications.
- Distributed calls between Java and Python.
- Automatic standard telemetry for supported frameworks and libraries without application annotations or decorators.
- Custom operations, business outcomes, metrics, and business events.
- Standard OTLP export to managed observability providers.

JavaScript, TypeScript, Node.js, NestJS, Next.js, React, and Angular are explicitly out of scope for this release and reserved for Phase 2.

## Product Roadmap

Use these phase names consistently throughout implementation and documentation:

### MVP: Managed Provider Backend

- Java 21 with Spring Boot 3.x.
- Python 3.11-3.13 with FastAPI.
- Automatic standard observability without Lumens annotations or decorators.
- Explicit governed business telemetry and optional custom internal operations.
- Provider-managed ingestion profiles for the five certified destinations.
- No Lumens or Deloitte production Collector.

### Phase 1: Optional Organization-Managed Collector

- A production OpenTelemetry Collector gateway operated by an organization that explicitly accepts ownership.
- Central credentials, persistent queues, routing, sampling, filtering, redaction, dual export, high availability, and disaster recovery.
- Optional provider-specific enrichment after the portable processing pipeline.
- No application source-code dependency on the gateway.

Phase 1 is optional. It must not become a prerequisite for the MVP or later SDKs.

### Phase 2: JavaScript and TypeScript Ecosystem

- One TypeScript SDK distribution with isolated runtime-specific entry points.
- Node.js server instrumentation.
- NestJS integration.
- Next.js server integration through supported instrumentation hooks.
- Separate Next.js browser and Edge adapters because their runtime capabilities differ from Node.js.
- Framework-neutral browser support used by React and Angular integrations.
- Shared semantic contract, business-event API, privacy policy, generated constants, and test utilities.

Node.js and NestJS should provide automatic standard server telemetry where supported. React and Angular components must not require decorators for standard browser telemetry.

Browser support requires explicit consent controls, Web Vitals, route/navigation tracing, error capture, fetch/XHR instrumentation, cross-origin propagation allowlists, session policy, and strict payload and PII protection. Provider access tokens must never be included in browser bundles. Browser export must use a provider-supported public RUM endpoint or a separately approved secure ingestion proxy. Provider portability for browser telemetry must not be claimed until each route is tested.

### Phase 3: AI Agent and GenAI Workload Observability

- Agent and workflow execution traces.
- Model request latency, failures, retries, and fallbacks.
- Tool calls, retrieval operations, guardrail decisions, and human approval steps.
- Multi-agent handoffs with correct trace parentage.
- Token usage, estimated cost, and governed business outcomes.
- Incrementally certified agent-framework and model-provider integrations.

Use stable OpenTelemetry GenAI semantic conventions where available and govern Lumens extensions through the semantic contract. Prompts, responses, conversation history, retrieved documents, tool arguments, tool results, credentials, and customer data must not be captured by default.

### Phase 4: Lumens Experience Generator

- A shared GenAI-assisted planning engine.
- A vendor-neutral asset specification.
- Dynatrace, Splunk, Datadog, Grafana, and New Relic provider adapters.
- Safe generation of dashboards, alerts, monitors, SLOs, ownership metadata, and runbook links.

Later phases require separate plans, compatibility baselines, tests, security reviews, and Definitions of Done. The current Build Agent implements only the MVP, except for the explicitly requested extension-point documentation.

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

- Implement only the explicitly requested feature from the MVP Feature Plan, not the complete MVP in one request.
- State a feature's unmet dependencies before starting it and do not implement unrequested later features.
- Leave the repository buildable after each completed feature and run that feature's feasible verification.
- Update affected architecture, ADR, contract, provider, and compatibility documentation in the same feature delivery.
- Report completed acceptance criteria, test results, deferred work, and any blocked prerequisites.
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
- Provider destination profiles.
- Pluggable event sinks and policy extensions.

The generator must allow client-specific generated Java packages and Python modules while retaining the stable Lumens core packages.

## Repository Layout

```text
/
  plan.md
  README.md
  docs/
    architecture.md
    architecture/
      context.md
      components.md
      telemetry-flows.md
      deployment-models.md
      security-boundaries.md
      failure-model.md
      roadmap.md
    getting-started-java.md
    getting-started-python.md
    instrumentation-modes.md
    semantic-contract.md
    business-events.md
    privacy-and-cardinality.md
    client-customization.md
    troubleshooting.md
    compatibility.md
    verification.md
    mvp-definition-of-done.md
    feature-status.md
    providers/
      README.md
      dynatrace.md
      splunk.md
      datadog.md
      grafana-cloud.md
      new-relic.md
      switching-providers.md
      compatibility-matrix.md
    adr/
      001-opentelemetry-foundation.md
      002-explicit-instrumentation-modes.md
      003-business-event-delivery.md
      004-semantic-registry.md
      005-browser-deferred.md
      006-provider-managed-ingestion.md
      007-optional-collector-gateway.md
      008-agent-observability.md
      009-experience-generator.md

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

  providers/
    profiles/
      dynatrace/
      splunk/
      datadog/
      grafana-cloud/
      new-relic/
      generic-otlp/
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
- Managed ingestion profiles for Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, and New Relic.

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

## Destination Profiles

Instrumentation mode and export destination are separate concerns. Platform-managed and application-managed services must both select destinations through deployment configuration without changing application source code.

MVP certified destinations:

- Dynatrace.
- Splunk Observability Cloud.
- Datadog.
- Grafana Cloud.
- New Relic.

Support levels:

- Certified: documented and tested end to end by Lumens.
- OTLP-compatible: expected to work through standard OTLP without a formal compatibility guarantee.
- Custom: configured and validated by the client.

Use a minimal deployment interface equivalent to:

```text
OTEL_EXPORTER_OTLP_ENDPOINT=http://telemetry-agent:4317
```

Standard `OTEL_*` variables remain authoritative. Lumens does not translate vendor tokens into headers or infer a provider from an endpoint. Applications export to a provider Agent, customer-managed Collector, provider-supported component, or direct OTLP endpoint. For direct OTLP, the client injects `OTEL_EXPORTER_OTLP_HEADERS` through its secret manager. `LUMENS_PROVIDER` is optional metadata for documentation, compatibility validation, and future asset generation. Verify current endpoints, headers, and supported capabilities against official provider documentation during implementation.

Each certified profile must:

- Document a recommended topology and supported topologies for every provider.
- Keep credentials and header composition in client/provider-managed infrastructure, not Lumens application configuration.
- Require no provider-specific SDK or telemetry API in application code.
- Preserve canonical OpenTelemetry resource attributes and governed `lumens.*` semantics.
- Document traces, metrics, and logs support separately.
- Isolate provider-prefixed metadata and enrichment outside Lumens APIs and semantic contracts.
- Provide configuration validation and actionable diagnostics without logging secrets.
- Permit credential rotation without rebuilding the application.

Direct-OTLP headers must come from environment variables or an approved secret manager, use least privilege, and never be committed, sent as telemetry, included in fixtures, or exposed through diagnostics. Agent and customer-Collector credentials belong to that infrastructure rather than to application workloads.

Provider-specific enrichment such as Dynatrace `dt.*` entity metadata, Datadog `dd.*` metadata, Splunk-specific dimensions, Grafana data-source labels, or New Relic proprietary entity metadata may be added by provider-managed infrastructure. Lumens core must not depend on these fields.

The portability guarantee is limited to application instrumentation and semantic data: changing between certified providers requires no application source-code change or rebuild. Deployment configuration, credentials, provider-supported infrastructure, dashboards, alerts, SLOs, proprietary queries, historical data, retention policies, and provider-specific topology remain destination concerns.

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

## OTLP Test Harness

The MVP may use in-process exporters, ephemeral test containers, or another disposable OTLP receiver to inspect normalized telemetry and produce golden fixtures during development and CI. This test harness must support privacy checks and cross-language trace verification without becoming deployed solution infrastructure.

Do not package, deploy, or operate a Lumens OpenTelemetry Collector in the MVP. Production telemetry must use the selected provider's managed OTLP endpoint or provider-managed ingestion component.

## Phase 1: Optional Organization-Managed Gateway

Phase 1 may provide an organization-managed OpenTelemetry Collector gateway. It is explicitly outside the MVP and must be adopted only when an organization accepts operational ownership, cost, security, availability, and maintenance responsibilities.

Potential capabilities:

- A stable internal OTLP endpoint.
- Centralized provider credentials and rotation.
- Persistent queues and provider-outage buffering.
- Central routing, filtering, sampling, and redaction.
- Dual export during provider migrations.
- Regional high availability and disaster recovery.
- Provider-specific enrichment after the portable processing pipeline.
- Gateway capacity management and self-observability.

Applications and Lumens semantic contracts must remain independent of this gateway. Introducing or removing it must require deployment configuration changes only.

## Phase 2: JavaScript and TypeScript Ecosystem

Phase 2 may add JavaScript and TypeScript support through one npm distribution with runtime-specific exports for Node.js, NestJS, Next.js, browser, React, Angular, and Next.js Edge environments. Shared code must remain runtime-neutral, while Node and browser dependencies and bundles remain isolated.

Phase 2 requirements include:

- Automatic supported server telemetry for Node.js, NestJS, and Next.js server workloads.
- Browser-safe route, Web Vitals, fetch/XHR, and technical-error instrumentation for React, Angular, and Next.js client workloads.
- Explicit business-event and custom-operation APIs aligned with Java and Python semantics.
- Generated TypeScript semantic constants from the shared contract.
- Context propagation across supported server boundaries and allowlisted browser origins.
- Separate compatibility claims and tests for Node.js, browsers, and Next.js Edge.
- No provider credentials, Node-only modules, request payloads, or sensitive values in browser bundles.
- Consent, session, privacy, cardinality, and failure-isolation tests.
- A documented secure browser ingestion route for every certified provider before claiming support.

Phase 2 is not part of the current repository implementation order or MVP Definition of Done.

## Phase 3: AI Agent and GenAI Workload Observability

Phase 3 may add governed observability for AI agents and GenAI workloads in supported Java, Python, and later TypeScript runtimes.

Phase 3 requirements include:

- Represent an agent or workflow run as a trace or clearly bounded operation.
- Trace model calls, tool calls, retrieval and vector-database operations, guardrails, human approvals, retries, fallbacks, and multi-agent handoffs.
- Preserve parentage and context across asynchronous steps and framework boundaries.
- Record bounded model and provider identifiers, latency, technical failures, token usage, estimated cost, and business outcomes where available.
- Distinguish expected agent outcomes from technical errors.
- Use stable OpenTelemetry GenAI semantic conventions where available and register any `lumens.*` extensions.
- Keep metrics low-cardinality and independent of trace sampling.
- Provide failure isolation so instrumentation never breaks an agent workflow.

Privacy defaults must prohibit automatic capture of prompts, responses, conversation history, retrieved documents, embeddings, tool arguments, tool results, API keys, model credentials, user identifiers, and customer data. Any content capture requires an explicit policy, documented purpose, data classification, consent where applicable, redaction, retention controls, and dedicated tests.

Candidate integrations include LangChain/LangGraph, Semantic Kernel, AutoGen, CrewAI, and model-provider SDKs. Each integration requires an explicit compatibility baseline, privacy review, duplicate-instrumentation tests, and conformance tests before it can be certified. Do not claim generic compatibility with all agent frameworks.

Phase 3 should define agent-specific semantic contract entries and test fixtures that Phase 4 can use to generate agent health, model latency, tool reliability, token usage, cost, guardrail, and business-outcome dashboards.

## Phase 4: Lumens Experience Generator

Phase 4 may add an optional **Lumens Experience Generator** that creates provider assets from the Lumens semantic contract, service metadata, and a declared solution archetype:

```text
semantic contract + service metadata + solution archetype
                         |
                         v
                  GenAI planning layer
                         |
                         v
             vendor-neutral asset specification
                         |
                         v
                    provider adapter
                         |
                         v
             dashboards, alerts, monitors, SLOs
```

Use one shared planning engine with Dynatrace, Splunk, Datadog, Grafana, and New Relic adapters. Do not duplicate planning logic in five independent agents.

The component may generate service overview, request rate/error/duration, dependency, business-outcome, and business-event dashboards, plus provider-supported alerts, monitors, SLOs, ownership metadata, and runbook links.

Safety and lifecycle requirements:

- Produce and schema-validate a vendor-neutral intermediate specification.
- Provide deterministic templates when GenAI is unavailable or disabled.
- Separate `generate`, `plan`, and `apply`; default to dry-run and require explicit human approval before writes.
- Never expose provider tokens to the language model.
- Never send production telemetry, payloads, PII, secrets, or customer data to GenAI.
- Use least-privilege provider API credentials outside the model boundary.
- Make resource creation idempotent and tag ownership, contract version, and generator version.
- Detect drift and do not overwrite manually managed resources by default.
- Record auditable proposals and applied changes with rollback or deletion plans.

The MVP defines only the vendor-neutral asset model and provider-adapter extension points. GenAI execution and provider API writes are not MVP deliverables.

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
- Selects its destination profile entirely through deployment configuration.

### Python Integration Service

Create a FastAPI service that:

- Receives the Java request.
- Continues the incoming trace through an automatic FastAPI server span without decorating the route.
- Creates a nested Lumens operation.
- Simulates an external integration with automatic supported-client instrumentation.
- Records a bounded outcome.
- Demonstrates async context propagation.
- Emits one registered business event.
- Selects its destination profile entirely through deployment configuration.

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
- Provider ingestion unavailability does not fail application requests.
- Forbidden test secrets never appear in captured telemetry.
- Switching certified destination configuration requires no source change or application rebuild.
- Canonical service identity and `lumens.*` semantics remain stable across destination profiles.

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

OTLP test-harness tests:

- Normalized OTLP capture and golden-fixture tests.
- Privacy and redaction tests.
- Cross-language trace tests.
- Export failure behavior.
- Proof that no Collector is required in a deployed MVP solution.

Provider profile tests:

- Configuration validation for all five certified destinations.
- Guarded end-to-end ingestion tests that skip clearly when credentials are unavailable.
- No provider-specific application SDK or telemetry API.
- Authentication secrets absent from telemetry, fixtures, logs, and diagnostics.
- Consistent resource identity and business semantics across profiles.
- Provider-agent coexistence tests that prevent duplicate spans where applicable.
- Deployment-only switching tests with no application source change or rebuild.

## Documentation Requirements

### Architecture Documentation

`docs/architecture.md` is the architecture index and concise executive overview. Detailed views belong under `docs/architecture/` so ownership, deployment, security, and phase-specific concerns can evolve independently.

Required views:

- `context.md`: system context, users, application workloads, Lumens components, managed providers, external dependencies, and Deloitte/client/provider responsibility boundaries.
- `components.md`: Java and Python SDK modules, semantic registry and generator, provider profiles, event sinks, policy interfaces, test kits, and disposable OTLP test harness.
- `telemetry-flows.md`: automatic server/client instrumentation, W3C propagation, custom operations, outcomes, metrics, logs, business events, export, provider switching, and failure-isolation sequences.
- `deployment-models.md`: MVP direct provider-managed ingestion, provider-managed agents or ingestion components, and the optional Phase 1 organization-managed gateway including migration and dual-export considerations.
- `security-boundaries.md`: credentials, secrets, trust boundaries, data classification, prohibited telemetry, browser ingestion, GenAI processing, provider APIs, and defense-in-depth controls.
- `failure-model.md`: application behavior during SDK, exporter, network, provider, event-sink, test-harness, and future gateway failures, including buffering and data-loss expectations.
- `roadmap.md`: architecture scope and dependencies for the MVP, optional Collector, JavaScript/TypeScript ecosystem, AI agent observability, and Experience Generator.

Use Mermaid diagrams stored as text in Markdown. Include C4-style context and component diagrams, sequence diagrams for telemetry flows, deployment diagrams for ingestion models, trust-boundary diagrams for security, and workflow diagrams for provider migration and Experience Generator `generate -> plan -> approve -> apply` behavior. Diagrams must remain understandable in adjacent prose when Mermaid rendering is unavailable.

Every architecture view must identify:

- Scope and explicit exclusions.
- Component responsibilities and ownership.
- Data and control flows.
- Public APIs, semantic contracts, and configuration boundaries.
- Security, privacy, and trust boundaries.
- Deployment topology and operational ownership.
- Failure modes, degradation, retry, buffering, and data-loss behavior.
- Compatibility assumptions and provider-specific limitations.
- Relevant tests and Definition of Done criteria.

Architecture Decision Records must use a consistent template containing status, context, decision, alternatives, consequences, security/privacy impact, operational ownership, and supersession links. In addition to the existing ADRs, create:

- `006-provider-managed-ingestion.md`: why the MVP uses provider-managed ingestion and does not operate a Lumens production Collector.
- `007-optional-collector-gateway.md`: adoption criteria, ownership, risks, and application independence for Phase 1.
- `008-agent-observability.md`: GenAI semantic conventions, content-capture defaults, privacy controls, and framework certification for Phase 3.
- `009-experience-generator.md`: vendor-neutral asset model, provider adapters, approval workflow, token boundary, drift, and auditability for Phase 4.

Architecture documentation and ADRs must be updated in the same change as any implementation that alters component ownership, telemetry flow, security boundary, deployment model, public contract, or roadmap decision.

Document:

- Five-minute Java setup.
- Five-minute Python setup.
- Agent versus application-managed mode.
- Instrumentation mode versus destination profile.
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
- Certified, OTLP-compatible, and custom destination support levels.
- Provider setup guides for Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, and New Relic.
- A compatibility matrix covering ingestion route, authentication, transport, signals, and known limitations.
- A provider-switching runbook with validation, rollback, asset recreation, old-agent removal, and credential revocation.
- The Phase 1 optional organization-managed gateway and its ownership implications.
- The Phase 2 JavaScript and TypeScript runtime architecture, browser security boundary, and deferred compatibility claims.
- The Phase 3 AI agent observability semantics, privacy defaults, framework certification model, and conformance requirements.
- The Phase 4 Lumens Experience Generator architecture and safety boundaries.

Each certified provider guide must document prerequisites, the recommended managed ingestion route, current endpoint format, authentication, secret handling, required environment variables, TLS, signal support, Java and Python setup, end-to-end verification, duplicate-instrumentation prevention, provider enrichment, limitations, troubleshooting, and rollback. Verify changeable provider details against current official documentation during implementation.

## MVP Feature Plan

Implement the MVP as the following independently requested features. A feature may add only the smallest supporting changes required by its stated acceptance criteria. Do not begin the next feature automatically.

| ID | Feature | Depends on | Status |
|---|---|---|---|
| MVP-F01 | Repository foundation and architecture documentation | None | Complete |
| MVP-F02 | Semantic contract, validation, and code generation | MVP-F01 | Complete |
| MVP-F03 | Java core observability API and test kit | MVP-F02 | Complete |
| MVP-F04 | Python core observability API and test kit | MVP-F02 | Complete |
| MVP-F05 | Spring Boot integration and zero-touch instrumentation | MVP-F03 | Complete |
| MVP-F06 | FastAPI integration and zero-touch instrumentation | MVP-F04 | Complete |
| MVP-F07 | Governed business events and policy enforcement | MVP-F03, MVP-F04 | Complete |
| MVP-F08 | Provider profiles and provider documentation | MVP-F03, MVP-F04 | Complete |
| MVP-F09 | Reference applications and cross-language conformance | MVP-F05, MVP-F06, MVP-F07, MVP-F08 | Complete |
| MVP-F10 | Verification automation and MVP hardening | MVP-F09 | Complete |

### MVP-F01: Repository Foundation And Architecture Documentation

Scope:

- Create the Maven, Python, contract-tool, provider-profile, example, test, and script structure defined in this plan.
- Add root build configuration, pinned-version management placeholders, architecture views, ADRs, and contributor documentation.
- Do not implement runtime instrumentation, provider export, or future phases.

Acceptance criteria:

- Repository layout matches the planned structure.
- Architecture documentation and ADRs required by this plan exist and cross-reference the MVP and roadmap decisions.
- Root build and lint or placeholder verification commands fail clearly when unimplemented components are invoked.

### MVP-F02: Semantic Contract, Validation, And Code Generation

Scope:

- Implement the versioned YAML contract, JSON Schema, client-overlay validation, deterministic Java and Python constant generation, and `--check` support.
- Define base operation, outcome, attribute, event, metric-dimension, baggage, privacy, and cardinality semantics.

Acceptance criteria:

- Valid contracts and overlays generate deterministic Java and Python output.
- Invalid types, namespaces, duplicates, privacy/cardinality combinations, and breaking overlays fail with actionable messages.
- Generated definitions have Java/Python parity and `--check` detects stale output.

### MVP-F03: Java Core Observability API And Test Kit

Scope:

- Implement the Java API, operation lifecycle, outcomes, metrics, policy interfaces, and in-memory telemetry test kit.
- Support synchronous and asynchronous core operation behavior before framework auto-configuration.

Acceptance criteria:

- Operations create correctly parented internal spans, bounded metrics independent of trace sampling, and governed attributes.
- Success, failure, cancellation, manual lifecycle, and callback lifecycle behavior are tested.
- Arguments, return values, payloads, secrets, and uncontrolled high-cardinality data are not captured automatically.

### MVP-F04: Python Core Observability API And Test Kit

Scope:

- Implement Python lifecycle configuration, operation APIs, outcomes, metrics, policy interfaces, and in-memory telemetry test fixtures.
- Support synchronous and asynchronous operations before FastAPI integration.

Acceptance criteria:

- Sync and async operations preserve metadata, restore `contextvars`, and correctly handle success, failure, and cancellation.
- Metrics, privacy, cardinality, and failure-isolation behavior match the shared contract.
- Arguments, return values, payloads, secrets, and uncontrolled high-cardinality data are not captured automatically.

### MVP-F05: Spring Boot Integration And Zero-Touch Instrumentation

Scope:

- Implement Spring Boot starter, auto-configuration, runtime mode, instrumentation-mode conflict detection, optional custom-operation annotation behavior, and Spring test utilities.
- Integrate the supported OpenTelemetry Java agent or Spring Boot starter without creating duplicate providers or framework spans.

Acceptance criteria:

- Supported Spring server and client telemetry works without Lumens annotations.
- Platform-managed and application-managed modes initialize idempotently and reject clear conflicts.
- Optional custom operations work for distinct internal operations and do not duplicate framework spans.

### MVP-F06: FastAPI Integration And Zero-Touch Instrumentation

Scope:

- Implement FastAPI integration, platform-managed coexistence, application-managed initialization, logging correlation, and async context handling.
- Preserve standard Python logging and avoid duplicate handlers or server spans.

Acceptance criteria:

- Supported FastAPI server and client telemetry works without Lumens decorators.
- Repeated initialization, background tasks, `asyncio` propagation, cancellation, and logging coexistence are tested.
- Platform-managed and application-managed modes do not replace an application-owned provider.

### MVP-F07: Governed Business Events And Policy Enforcement

Scope:

- Implement registered business-event APIs and default structured logging sinks in Java and Python.
- Enforce semantic registry, privacy, cardinality, and trace/span correlation policies across custom operations, events, and metrics.

Acceptance criteria:

- Events are validated, correlated when active context exists, and emitted without breaking application logic.
- Invalid, sensitive, or unregistered fields are safely dropped with bounded diagnostics.
- Business outcomes remain distinct from technical errors, and the same occurrence is not automatically emitted as multiple signal types.

### MVP-F08: Provider Profiles And Provider Documentation

Scope:

- Implement deployment-only destination profiles for Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, New Relic, and generic OTLP.
- Create provider setup, compatibility, and switching documentation.
- Do not deploy or operate a Lumens production Collector.

Acceptance criteria:

- Every certified provider has documented managed ingestion, authentication, signal support, TLS, verification, limitations, rollback, and duplicate-instrumentation guidance.
- Profiles validate configuration without exposing secrets and preserve canonical OpenTelemetry and `lumens.*` semantics.
- Switching profile configuration requires no application source change or rebuild.

### MVP-F09: Reference Applications And Cross-Language Conformance

Scope:

- Build the Java BFF, Python integration service, disposable OTLP test harness, normalized fixtures, and cross-language integration tests.
- Exercise standard telemetry, a distinct internal operation, business outcomes, business events, privacy controls, provider failure isolation, and profile switching.

Acceptance criteria:

- The two services share a trace with correct server/client parentage and no duplicate HTTP spans.
- Business metrics remain available when traces are unsampled.
- Provider ingestion failures do not fail requests, and forbidden test markers do not appear in telemetry.

### MVP-F10: Verification Automation And MVP Hardening

Scope:

- Finalize verification scripts, CI-ready checks, compatibility results, dependency pinning, documentation links, and full MVP regression coverage.
- Do not implement Phase 1 through Phase 4 capabilities.

Acceptance criteria:

- Documented Java, Python, contract, provider-profile, and cross-service verification commands run or skip external credential checks clearly.
- All MVP Definition of Done criteria are verified and compatibility results are recorded.
- Deferred Phase 1 through Phase 4 work remains isolated from MVP implementation artifacts.

## Feature Delivery Protocol

When asked to implement a feature, the Build Agent must:

1. Confirm the requested feature identifier and check its dependencies.
2. Implement only that feature and minimal directly required fixes.
3. Run the feature's feasible verification and report unavailable external checks explicitly.
4. Update applicable contracts, architecture views, ADRs, provider guides, and compatibility records.
5. Stop after the feature is complete; wait for an explicit request before starting another feature.

The overall MVP Definition of Done applies only after `MVP-F10`. Earlier feature acceptance criteria define the delivery boundary for cost-controlled implementation.

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
- All five certified managed-provider routes have setup guides, profiles, and guarded compatibility tests.
- Certified provider switching requires no application source change or rebuild.
- Provider ingestion outage tests prove application requests continue.
- Development and CI telemetry inspection uses only disposable test tooling.
- No Deloitte-managed production Collector or gateway is required.
- Provider credentials are absent from source, fixtures, telemetry, and diagnostics.
- Required architecture views and ADRs exist, agree with the implementation, and document responsibility and security boundaries.
- Phase 1 Collector, Phase 2 JavaScript/TypeScript ecosystem, Phase 3 agent observability, and Phase 4 Experience Generator are documented but not implemented by the MVP Build Agent.
- All dependencies are pinned.
- Compatibility results are documented.
- No JavaScript, TypeScript, Node.js, NestJS, Next.js, React, or Angular implementation is included.
- No package is published and no repository commit is created automatically.

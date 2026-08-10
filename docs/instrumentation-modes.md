# Instrumentation Modes

Lumens supports two explicit modes per runtime. Select exactly one mode per application to prevent duplicate providers, exporters, and framework spans.

## Platform-Managed

This is the production default. Deploy the OpenTelemetry Java agent and add `lumens-observability-spring-boot-starter`.

```text
-javaagent:/path/opentelemetry-javaagent.jar
lumens.observability.mode=platform-managed
```

The Java agent owns standard Spring server/client, database, messaging, propagation, and runtime instrumentation. Lumens consumes the global OpenTelemetry APIs for business operations and does not create another provider, exporter, or HTTP span.

## Application-Managed

Use this mode when an agent is unavailable. Add `lumens-observability-spring-boot-runtime` instead of the platform-managed starter.

```properties
lumens.observability.mode=application-managed
OTEL_SERVICE_NAME=example-service
OTEL_EXPORTER_OTLP_ENDPOINT=https://provider-endpoint.example
```

The runtime initializes OpenTelemetry through the official SDK autoconfiguration path, so standard `OTEL_*` settings control providers and exporters. It accepts an application-supplied `OpenTelemetry` bean and does not replace it.

## Guardrails

- The runtime artifact with `platform-managed` mode fails startup.
- Repeated auto-configuration reuses the existing `LumensOperations` bean.
- Do not annotate controllers, repositories, or supported clients with `@ObservedOperation` merely to obtain standard telemetry.
- Use `@ObservedOperation` only for a distinct internal operation. Spring proxy self-invocation bypasses the aspect; use the programmatic `LumensOperations` API in that case.

## Python And FastAPI

Platform-managed Python applications use an existing `opentelemetry-instrument` setup and call `instrument_fastapi(app)` once. Lumens preserves the current providers and does not install logging handlers.

Application-managed Python applications call `configure_application_observability` with application-owned tracer and meter providers, then pass the tracer provider to `instrument_fastapi`. The helper accepts explicit providers for safe application ownership and testing; it does not replace an already configured global provider.

In both modes, the official FastAPI instrumentor owns standard ASGI server spans. Lumens core operations remain optional for distinct internal work.

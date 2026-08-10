# System Context

## Scope

This view describes the MVP Java and Python backend accelerator and provider-managed ingestion. It excludes browser telemetry, an organization-managed Collector, AI agent instrumentation, and provider dashboard automation.

```mermaid
C4Context
    title Lumens MVP system context
    Person(developer, "Application developer", "Builds Java or Python services")
    System(javaService, "Spring Boot service", "Uses OpenTelemetry and Lumens Java APIs")
    System(pythonService, "FastAPI service", "Uses OpenTelemetry and Lumens Python APIs")
    System(lumens, "Lumens", "Contracts, policies, business telemetry APIs, and provider profiles")
    System_Ext(provider, "Managed observability provider", "Dynatrace, Splunk, Datadog, Grafana Cloud, or New Relic")
    Rel(developer, javaService, "Develops")
    Rel(developer, pythonService, "Develops")
    Rel(javaService, pythonService, "HTTP with W3C trace context")
    Rel(javaService, lumens, "Uses")
    Rel(pythonService, lumens, "Uses")
    Rel(javaService, provider, "Exports OTLP")
    Rel(pythonService, provider, "Exports OTLP")
```

## Ownership

| Boundary | Owner |
|---|---|
| Business behavior and explicit business events | Application team |
| Lumens libraries, semantic contract, policies, and test kits | Lumens/Deloitte delivery team |
| Deployment configuration and secret injection | Client platform or application operations team |
| Ingestion availability, storage, dashboards, alerts, and retention | Provider and client operations team |

## Security And Failure Boundaries

Applications receive provider credentials only through deployment configuration. Lumens must not log credentials or automatically collect payloads. A provider or network outage may lose telemetry, but must not fail application work.

## Tests

MVP-F09 validates connected Java/Python traces, propagation, and provider-failure isolation. MVP-F08 validates destination-profile boundaries.

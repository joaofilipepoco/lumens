# Compatibility

## Verified MVP Baseline

| Component | Version | Verification |
|---|---:|---|
| Java | Temurin 21.0.12 | Maven reactor verification |
| Maven | 3.9.16 | Maven reactor verification |
| Spring Boot | 3.5.6 | Auto-configuration, mode, and AOP tests |
| OpenTelemetry Java | 1.59.0 | Core span/metric and Spring integration tests |
| Python | CPython 3.13.7 | Core and FastAPI tests |
| OpenTelemetry Python | 1.44.0 | Core and FastAPI instrumentation tests |
| FastAPI | 0.141.1 | ASGI automatic span and coexistence tests |
| uv | 0.12.2 | Locked dependency resolution and test execution |

## Provider Profile Verification

Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, New Relic, and generic OTLP profiles are validated structurally without credentials. Live provider ingestion is intentionally credential-gated and must skip clearly in client CI when endpoint or secret configuration is unavailable.

No provider SDK is required in application code. Provider endpoint, token scope, TLS, and supported-signal details must be verified against current provider documentation before a production deployment.

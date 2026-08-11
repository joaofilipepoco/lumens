# Datadog

Use Datadog Agent OTLP ingestion as the recommended topology. The application points standard OTLP configuration at the Agent:

```text
OTEL_EXPORTER_OTLP_ENDPOINT=http://datadog-agent:4317
```

The Datadog `DD_API_KEY` belongs in the Agent configuration, not in the application environment. A customer-managed OpenTelemetry Collector or direct OTLP endpoint are also possible when the client owns that configuration. Verify agent OTLP receivers, key scopes, logs support, TLS, and duplicate-agent behavior against current Datadog documentation. Datadog `dd.*` enrichment must remain provider-side.

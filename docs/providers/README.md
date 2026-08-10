# Provider Destinations

Lumens emits canonical OpenTelemetry and governed `lumens.*` semantics. The MVP routes it to a provider-managed ingestion path selected at deployment time; Lumens does not deploy or operate a production Collector.

```text
LUMENS_PROVIDER=dynatrace
OTEL_EXPORTER_OTLP_ENDPOINT=https://provider-endpoint.example
LUMENS_ACCESS_TOKEN=<secret-manager-reference>
```

Provider profiles live in `providers/profiles/`. They define metadata and required deployment variables only. They do not resolve secrets, install provider SDKs, or change application telemetry semantics.

Certified: Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, and New Relic. See the [compatibility matrix](compatibility-matrix.md) and [switching guide](switching-providers.md).

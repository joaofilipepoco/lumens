# Provider Destinations

Lumens emits canonical OpenTelemetry and governed `lumens.*` semantics. The application exports only through standard OpenTelemetry configuration. It does not interpret vendor tokens, compose vendor headers, install vendor SDKs, or operate a production Collector.

```text
OTEL_EXPORTER_OTLP_ENDPOINT=https://provider-endpoint.example
OTEL_EXPORTER_OTLP_HEADERS=<secret-manager-injected-headers>
```

The endpoint may be a provider Agent, a customer-managed OpenTelemetry Collector, a provider-supported component, or a direct cloud OTLP endpoint. The client selects and operates that delivery infrastructure.

From the application's perspective, every topology is OpenTelemetry: it sends OTLP to the configured endpoint. A Datadog Agent, Splunk-supported component, or customer-managed Collector is simply an OTLP receiver between the application and the provider cloud. The difference is operational ownership and where credentials live, not the Lumens application API.

Provider profiles in `providers/profiles/` define supported topologies and ownership boundaries. `LUMENS_PROVIDER` is optional metadata for documentation, compatibility validation, and future asset generation; it is not required for application export.

## First Pilot: Dynatrace Direct OTLP

Dynatrace is the recommended first pilot because it can test Lumens against a direct managed OTLP endpoint without a Deloitte-managed Collector:

```text
OTEL_SERVICE_NAME=lumens-pilot
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://<environment-id>.live.dynatrace.com/api/v2/otlp
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Api-Token <secret-manager-injected-token>
```

Provision the token and endpoint in the client secret manager. Verify current Dynatrace ingest scopes, endpoint format, TLS, and signal availability from official Dynatrace documentation before deployment. Do not run overlapping OneAgent and OpenTelemetry auto-instrumentation without an explicit duplicate-span strategy.

Certified: Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, and New Relic. See the [compatibility matrix](compatibility-matrix.md) and [switching guide](switching-providers.md).

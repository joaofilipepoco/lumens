# Dynatrace

Use Dynatrace direct OTLP ingestion for the first Lumens pilot. Configure the endpoint and authorization header with standard OpenTelemetry variables, injected from the client secret manager:

```text
OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
OTEL_EXPORTER_OTLP_ENDPOINT=https://<environment-id>.live.dynatrace.com/api/v2/otlp
OTEL_EXPORTER_OTLP_HEADERS=Authorization=Api-Token <token>
```

Lumens does not read or transform the token. The deployment platform resolves the secret into `OTEL_EXPORTER_OTLP_HEADERS`. Verify tenant endpoint format, token scopes, signal support, TLS, and retention against current Dynatrace documentation before deployment. Do not add `dt.*` fields to Lumens contracts; Dynatrace enrichment remains provider-side.

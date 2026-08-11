# Grafana Cloud

Use Grafana Cloud managed OTLP ingestion. Configure the stack endpoint with `OTEL_EXPORTER_OTLP_ENDPOINT` and inject the required authorization value through `OTEL_EXPORTER_OTLP_HEADERS`; Lumens does not compose the provider header.

Verify the stack-specific endpoint, token format, signals, TLS, and access-policy scopes against current Grafana Cloud documentation. Grafana data-source labels remain provider configuration.

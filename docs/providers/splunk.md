# Splunk Observability Cloud

Use a Splunk-supported ingestion component, a customer-managed Collector, or direct OTLP. The application uses `OTEL_EXPORTER_OTLP_ENDPOINT`; direct endpoint authentication is injected through `OTEL_EXPORTER_OTLP_HEADERS` by the client deployment platform.

Verify realm, token scopes, logs availability, TLS, and supported component configuration against current Splunk documentation. Splunk dimensions and entity enrichment remain outside Lumens application code.

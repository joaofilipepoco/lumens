# New Relic

Use New Relic managed OTLP ingestion. Configure the regional endpoint with `OTEL_EXPORTER_OTLP_ENDPOINT` and inject authentication through `OTEL_EXPORTER_OTLP_HEADERS`; Lumens does not interpret the ingest key.

Verify regional endpoint, key permissions, signal support, TLS, and retention against current New Relic documentation. New Relic entity metadata remains provider-side.

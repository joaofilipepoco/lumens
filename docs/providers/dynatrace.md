# Dynatrace

Use Dynatrace managed OTLP ingestion with `LUMENS_PROVIDER=dynatrace`. Supply the tenant OTLP endpoint in `OTEL_EXPORTER_OTLP_ENDPOINT` and an API token through `LUMENS_ACCESS_TOKEN`. The profile maps the token to the Dynatrace authorization header.

Verify tenant endpoint format, token scopes, signal support, TLS, and retention against current Dynatrace documentation before deployment. Do not add `dt.*` fields to Lumens contracts; Dynatrace enrichment remains provider-side.

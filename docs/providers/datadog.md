# Datadog

Use Datadog Agent OTLP ingestion with `LUMENS_PROVIDER=datadog`. Configure the agent endpoint in `OTEL_EXPORTER_OTLP_ENDPOINT` and inject the API key through `LUMENS_ACCESS_TOKEN` where the agent requires it.

Verify agent OTLP receivers, key scopes, logs support, TLS, and duplicate-agent behavior against current Datadog documentation. Datadog `dd.*` enrichment must remain provider-side.

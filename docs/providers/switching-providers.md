# Switching Providers

1. Provision the destination endpoint and least-privilege secret in the target provider.
2. Change the delivery topology, `OTEL_EXPORTER_OTLP_ENDPOINT`, and, for direct OTLP, `OTEL_EXPORTER_OTLP_HEADERS` in deployment configuration. `LUMENS_PROVIDER` is optional documentation metadata, not an application requirement.
3. Redeploy or restart without rebuilding application code.
4. Validate service identity, traces, metrics, logs, business-event correlation, propagation, and duplicate-span behavior.
5. Recreate provider-owned dashboards, alerts, monitors, and SLOs.
6. Remove the previous provider agent or enrichment only after validation.
7. Revoke the previous destination credentials and retain a rollback configuration.

Historical data, proprietary queries, topology, dashboards, alerts, retention, and provider AI features do not migrate automatically. Parallel export requires provider-supported infrastructure and is not a Lumens MVP requirement.

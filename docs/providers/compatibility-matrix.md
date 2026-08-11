# Provider Compatibility Matrix

| Provider | Recommended topology | Application target | Credential owner | Signals | Key limitation |
|---|---|---|---|---|---|
| Dynatrace | Direct OTLP | Dynatrace OTLP endpoint | Client secret manager | Traces, metrics, logs | Tenant endpoint and scopes vary |
| Splunk | Provider-supported component | Splunk component or endpoint | Component/client | Traces, metrics, logs | Realm and component configuration vary |
| Datadog | Datadog Agent | Datadog Agent OTLP endpoint | Datadog Agent | Traces, metrics, logs | Agent receiver configuration is required |
| Grafana Cloud | Direct OTLP | Grafana Cloud OTLP endpoint | Client secret manager | Traces, metrics, logs | Stack endpoint and auth format vary |
| New Relic | Direct OTLP | New Relic OTLP endpoint | Client secret manager | Traces, metrics, logs | Regional endpoint and key scope vary |
| Generic OTLP | Customer Collector | Client-owned collector or endpoint | Client | Destination dependent | Not certified |

Applications use `OTEL_EXPORTER_OTLP_ENDPOINT` and, only for direct OTLP, `OTEL_EXPORTER_OTLP_HEADERS`. Profiles are validated structurally in CI. Guarded live ingestion checks require client-owned credentials and must skip clearly when unavailable.

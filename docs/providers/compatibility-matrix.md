# Provider Compatibility Matrix

| Provider | MVP route | Transport | Generic secret | Signals | Key limitation |
|---|---|---|---|---|---|
| Dynatrace | Managed OTLP | HTTP | `LUMENS_ACCESS_TOKEN` | Traces, metrics, logs | Tenant endpoint and scopes vary |
| Splunk | Managed OTLP or supported component | HTTP | `LUMENS_ACCESS_TOKEN` | Traces, metrics, logs | Realm and component configuration vary |
| Datadog | Datadog Agent OTLP | gRPC or HTTP | `LUMENS_ACCESS_TOKEN` | Traces, metrics, logs | Agent receiver configuration is required |
| Grafana Cloud | Managed OTLP | HTTP | `LUMENS_ACCESS_TOKEN` | Traces, metrics, logs | Stack endpoint and auth format vary |
| New Relic | Managed OTLP | HTTP | `LUMENS_ACCESS_TOKEN` | Traces, metrics, logs | Regional endpoint and key scope vary |
| Generic OTLP | Client validated | gRPC or HTTP | `LUMENS_ACCESS_TOKEN` | Destination dependent | Not certified |

Profiles are validated structurally in CI. Guarded live ingestion checks require provider credentials and must skip clearly when unavailable.

# Architecture Roadmap

| Stage | Architecture scope | Dependency |
|---|---|---|
| MVP | Java/Spring Boot, Python/FastAPI, semantic contract, business telemetry, managed provider profiles | Provider-managed ingestion |
| Phase 1 | Optional organization-managed Collector gateway | Explicit operating ownership |
| Phase 2 | Node.js, NestJS, Next.js, React, Angular, and browser-safe telemetry | Secure browser ingestion and runtime-specific adapters |
| Phase 3 | AI agent and GenAI workload observability | Stable GenAI conventions and certified integrations |
| Phase 4 | Experience Generator for dashboards, alerts, monitors, and SLOs | Vendor-neutral asset model and provider APIs |

The MVP is independently valuable and does not require any later phase. Later phases must preserve canonical OpenTelemetry, governed `lumens.*` semantics, privacy defaults, and the separation between application instrumentation and destination configuration.

## Deferred Risks

- Phase 1 adds platform cost, operational responsibility, and availability obligations.
- Phase 2 introduces browser consent, private-token, cross-origin, and PII risks.
- Phase 3 introduces prompt, response, tool, retrieval, and cost-data governance risks.
- Phase 4 introduces provider API permissions, generated-resource drift, and human-approval requirements.

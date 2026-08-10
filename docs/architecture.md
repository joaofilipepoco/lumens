# Architecture

Lumens is a vendor-neutral observability accelerator. It uses OpenTelemetry for technical telemetry mechanics and adds governed business semantics without introducing a proprietary tracing system.

## MVP Architecture

The MVP supports Java/Spring Boot and Python/FastAPI applications. Standard framework and library telemetry is automatic. Applications use explicit Lumens APIs only for business events, business outcomes, and distinct internal operations that automatic instrumentation cannot infer.

Production applications export standard OTLP directly to a selected provider-managed ingestion route. Lumens does not operate a production Collector in the MVP.

## Architecture Views

| View | Purpose |
|---|---|
| [Context](architecture/context.md) | Actors, systems, trust boundaries, and responsibility ownership |
| [Components](architecture/components.md) | MVP component responsibilities and public boundaries |
| [Telemetry flows](architecture/telemetry-flows.md) | Automatic telemetry, business semantics, export, and failure isolation |
| [Deployment models](architecture/deployment-models.md) | Provider-managed MVP ingestion and future gateway option |
| [Security boundaries](architecture/security-boundaries.md) | Secrets, privacy, data classification, and trust boundaries |
| [Failure model](architecture/failure-model.md) | Degradation behavior and expected telemetry loss boundaries |
| [Roadmap](architecture/roadmap.md) | MVP and Phase 1 through Phase 4 architecture scope |

## Decisions

Architecture decisions are recorded in [ADRs](adr/). Any change to component ownership, public contracts, telemetry flows, deployment models, or security boundaries must update the affected view and ADR.

## MVP Exclusions

The MVP excludes a Deloitte-managed production Collector, JavaScript/TypeScript runtime support, AI agent instrumentation, and automated provider asset creation. See [the roadmap](architecture/roadmap.md) for the deferred phases.

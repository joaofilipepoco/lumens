# ADR 009: Experience Generator

## Status

Accepted for Phase 4 planning

## Context

Provider dashboards, alerts, monitors, and SLOs are provider-specific and expensive to recreate manually during solution delivery or provider migration.

## Decision

Phase 4 may add a shared planning engine that creates a vendor-neutral asset specification and delegates provider API work to dedicated adapters. The lifecycle is `generate`, `plan`, explicit approval, and `apply`.

## Alternatives

- One independent GenAI agent for every provider.
- Direct autonomous provider writes without review.

## Consequences

Generated assets must be schema-validated, idempotent, version-tagged, drift-aware, auditable, and protected from overwriting manually managed resources.

## Security And Privacy Impact

Provider tokens remain outside the model boundary. Production telemetry, customer data, prompts, and payloads are not model input by default.

## Operational Ownership

Client teams approve provider changes and own provider API credentials.

## Supersession

Not superseded.

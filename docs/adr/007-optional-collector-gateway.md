# ADR 007: Optional Organization-Managed Collector Gateway

## Status

Accepted for Phase 1 planning

## Context

Some organizations need centralized routing, credential management, queues, filtering, redaction, and dual-provider migration support.

## Decision

Treat an organization-managed OpenTelemetry Collector gateway as an optional Phase 1 capability. It is never an MVP prerequisite and must not alter application APIs or semantic contracts.

## Alternatives

- Require the gateway for all deployments.
- Never support a gateway.

## Consequences

Organizations adopting the gateway accept explicit availability, scaling, security, cost, and maintenance ownership.

## Security And Privacy Impact

The gateway can apply defense-in-depth controls but cannot replace source-level governance.

## Operational Ownership

The adopting organization owns gateway operations; Lumens may provide reference guidance only.

## Supersession

Not superseded.

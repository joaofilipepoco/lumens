# ADR 008: Agent And GenAI Observability

## Status

Accepted for Phase 3 planning

## Context

AI agent workloads need traces for workflow runs, model calls, tools, retrieval, guardrails, handoffs, token usage, cost, and outcomes, but may process sensitive content.

## Decision

Add governed agent observability in Phase 3 using stable OpenTelemetry GenAI semantic conventions where available. Certify frameworks incrementally after compatibility and privacy review.

## Alternatives

- Capture all prompts, responses, and tool data by default.
- Claim support for all agent frameworks without validation.

## Consequences

Prompts, responses, retrieved documents, tool arguments/results, credentials, and customer data remain excluded by default. Any content capture requires explicit policy and tests.

## Security And Privacy Impact

Agent telemetry has stricter content controls than ordinary technical telemetry.

## Operational Ownership

Application teams govern agent use cases; Lumens governs semantic and privacy controls.

## Supersession

Not superseded.

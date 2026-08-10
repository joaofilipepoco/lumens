# ADR 005: Browser Telemetry Deferred

## Status

Accepted

## Context

Browser telemetry has different consent, security, cross-origin propagation, session, and provider-ingestion requirements from backend telemetry.

## Decision

Defer JavaScript, TypeScript, Node.js, NestJS, Next.js, React, Angular, and browser telemetry to Phase 2. The MVP focuses on Java and Python backend services.

## Alternatives

- Deliver a universal JavaScript package in the MVP.
- Embed provider credentials in browser bundles.

## Consequences

Phase 2 must define isolated runtime adapters and secure browser ingestion before support is certified.

## Security And Privacy Impact

Private provider tokens must never be shipped to browsers. Consent and PII controls are mandatory.

## Operational Ownership

Future browser support requires client security and platform review.

## Supersession

Not superseded.

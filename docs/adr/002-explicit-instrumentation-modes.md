# ADR 002: Explicit Instrumentation Modes

## Status

Accepted

## Context

Applications may use platform-installed instrumentation or application-managed OpenTelemetry initialization. Mixing both can create duplicate providers, exporters, and spans.

## Decision

Support explicit platform-managed and application-managed modes. Lumens detects clear conflicts, initializes idempotently, and never silently replaces an application-owned provider.

## Alternatives

- One mandatory mode.
- Automatic mode guessing.

## Consequences

Deployment configuration must declare the selected mode. Both modes preserve the same Lumens business semantics.

## Security And Privacy Impact

Mode selection does not relax field governance or credential rules.

## Operational Ownership

Client platform teams select and deploy the mode; Lumens provides compatibility guidance.

## Supersession

Not superseded.

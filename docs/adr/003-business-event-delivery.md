# ADR 003: Business Event Delivery

## Status

Accepted

## Context

Business events are independently queryable domain occurrences and are not equivalent to spans, metrics, or logs.

## Decision

Expose explicit registered business-event APIs with a default structured logging sink. Validate events against the semantic contract and correlate them to an active trace when possible. Event failures never fail application logic.

## Alternatives

- Automatically duplicate events as spans, logs, and metrics.
- Treat logged events as audit-grade delivery.

## Consequences

Applications choose events deliberately. Durable audit delivery requires a custom sink, transactional outbox, or broker.

## Security And Privacy Impact

Unregistered, invalid, or sensitive fields are dropped. Event values remain governed by contract policy.

## Operational Ownership

Application teams choose business occurrences; Lumens supplies validation and sinks.

## Supersession

Not superseded.

# ADR 006: Provider-Managed Ingestion For MVP

## Status

Accepted

## Context

A Deloitte-managed production Collector introduces platform cost, availability, maintenance, credential, and operational ownership obligations.

## Decision

The MVP exports standard OTLP to certified provider-managed endpoints or provider-managed ingestion components. Lumens provides deployment-only profiles for Dynatrace, Splunk Observability Cloud, Datadog, Grafana Cloud, New Relic, and generic OTLP.

## Alternatives

- Operate a shared Lumens production Collector in the MVP.
- Embed vendor SDKs in application code.

## Consequences

Provider switching requires configuration and provider-asset changes, but no application source change. Central routing, queues, and dual export are deferred.

## Security And Privacy Impact

Credentials are injected through deployment secret management and never source controlled or emitted as telemetry.

## Operational Ownership

Providers and client operations own ingestion availability. Lumens owns profile guidance and compatibility validation.

## Supersession

Not superseded.

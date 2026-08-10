# ADR 001: OpenTelemetry Foundation

## Status

Accepted

## Context

Lumens needs interoperable tracing, metrics, logs, context propagation, and export across Java and Python services.

## Decision

Use OpenTelemetry APIs, W3C Trace Context, OpenTelemetry semantic conventions, and OTLP. Lumens adds governed business semantics and does not replace OpenTelemetry providers, tracers, meters, loggers, or propagators.

## Alternatives

- A proprietary Lumens telemetry protocol.
- Provider-specific application SDKs.

## Consequences

Applications remain portable across OTLP destinations. Lumens must track OpenTelemetry compatibility and avoid duplicate instrumentation.

## Security And Privacy Impact

OpenTelemetry transport does not remove source-level data controls. Lumens policies remain responsible for governing custom fields.

## Operational Ownership

Application teams own instrumentation selection; providers own managed ingestion in the MVP.

## Supersession

Not superseded.

# ADR 004: Semantic Registry

## Status

Accepted

## Context

Cross-language business telemetry needs stable names, types, allowed values, and privacy/cardinality rules.

## Decision

Use a versioned YAML semantic registry validated by JSON Schema. Generate deterministic Java and Python constants, and allow validated client overlays.

## Alternatives

- Runtime string literals without validation.
- Separate hand-maintained Java and Python definitions.

## Consequences

MVP-F02 owns contract tooling. Contract changes become reviewable and testable compatibility changes.

## Security And Privacy Impact

The registry classifies fields and enforces policy before custom telemetry is emitted.

## Operational Ownership

Lumens maintains base semantics; client teams maintain approved overlays.

## Supersession

Not superseded.

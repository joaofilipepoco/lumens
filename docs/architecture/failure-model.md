# Failure Model

## Principle

Observability is failure-isolated. Telemetry failures must not fail, delay materially, or change application work.

| Failure | MVP behavior | Owner |
|---|---|---|
| Invalid custom field | Drop field or event and emit bounded diagnostic | Lumens/application team |
| SDK or policy exception | Suppress internally and preserve application behavior | Lumens |
| Exporter or network outage | Application continues; telemetry may be lost | Provider/client operations |
| Provider rejection or throttling | Application continues; diagnostics and provider configuration are investigated | Provider/client operations |
| Business-event sink failure | Application continues; event may be lost | Lumens/application team |
| Disposable test-harness failure | Test fails clearly; production is unaffected | Delivery team |

## MVP Limits

The MVP has no Lumens persistent queue, retry gateway, or guaranteed event delivery. Those are possible Phase 1 gateway concerns and do not alter MVP application behavior.

## Tests

MVP-F03/F04 test core failure isolation. MVP-F07 tests event-sink isolation. MVP-F09 tests provider-ingestion unavailability.

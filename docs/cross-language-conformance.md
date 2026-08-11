# Cross-Language Conformance

MVP-F09 provides a Spring BFF and FastAPI integration reference pair plus a normalized OTLP fixture. The fixture verifies one shared trace, Java client to Python server parentage, distinct internal operations, correlated business events, and independent business metrics.

The Compose harness is optional because it requires Docker and local build tooling. It currently runs the services as independent smoke tests; it does not yet perform the live Java-to-Python call represented by the fixture. It must not require provider credentials. Use the disposable OTLP test harness or an in-memory exporter to inspect telemetry during integration testing.

from __future__ import annotations

from opentelemetry.sdk.trace import TracerProvider

from lumens_observability import BusinessEvents, registered_attributes


def test_event_is_validated_and_correlated_to_active_trace() -> None:
    captured = []
    events = BusinessEvents(
        "1.0.0",
        {"integration.enrichment.completed": {"integration.provider"}},
        registered_attributes({"integration.provider"}),
        captured.append,
    )
    provider = TracerProvider()
    with provider.get_tracer("test").start_as_current_span("parent"):
        assert events.emit("integration.enrichment.completed", {"integration.provider": "example-provider"})

    assert captured[0].attributes["event.name"] == "integration.enrichment.completed"
    assert captured[0].attributes["trace_id"]
    assert captured[0].attributes["span_id"]
    provider.shutdown()


def test_event_rejects_invalid_data_and_isolates_sink_failure() -> None:
    events = BusinessEvents(
        "1.0.0",
        {"integration.enrichment.completed": {"integration.provider"}},
        registered_attributes({"integration.provider"}),
        lambda _: (_ for _ in ()).throw(RuntimeError("sink failure")),
    )

    assert not events.emit("unknown.event", {})
    assert not events.emit("integration.enrichment.completed", {"password": "never-export"})
    assert not events.emit("integration.enrichment.completed", {"integration.provider": "example-provider"})

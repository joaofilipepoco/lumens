import json
from pathlib import Path


def test_normalized_cross_service_fixture_preserves_trace_parentage() -> None:
    fixture = json.loads((Path(__file__).parent / "normalized-otlp.json").read_text(encoding="utf-8"))
    spans = {span["span_id"]: span for span in fixture["traces"]}
    assert {span["trace_id"] for span in spans.values()} == {"trace-a"}
    assert spans["span-c"]["parent_span_id"] == "span-b"
    assert spans["span-d"]["parent_span_id"] == "span-c"
    assert len([span for span in spans.values() if span["kind"] == "SERVER" and span["service"] == "python-integration"]) == 1
    assert fixture["events"][0]["trace_id"] == "trace-a"
    assert {"lumens.operation.executions", "lumens.operation.duration"} <= set(fixture["metrics"])

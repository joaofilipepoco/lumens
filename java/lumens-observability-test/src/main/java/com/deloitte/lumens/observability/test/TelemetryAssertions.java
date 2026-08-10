package com.deloitte.lumens.observability.test;

import io.opentelemetry.sdk.trace.data.SpanData;
import java.util.List;
import org.junit.jupiter.api.Assertions;

/** Concise assertions for emitted Lumens telemetry. */
public final class TelemetryAssertions {
    private TelemetryAssertions() {}

    public static SpanData spanNamed(List<SpanData> spans, String name) {
        return spans.stream()
                .filter(span -> span.getName().equals(name))
                .findFirst()
                .orElseThrow(() -> new AssertionError("No span named '" + name + "'."));
    }

    public static void isChildOf(SpanData child, SpanData parent) {
        Assertions.assertEquals(parent.getSpanContext().getSpanId(), child.getParentSpanContext().getSpanId());
        Assertions.assertEquals(parent.getSpanContext().getTraceId(), child.getSpanContext().getTraceId());
    }
}

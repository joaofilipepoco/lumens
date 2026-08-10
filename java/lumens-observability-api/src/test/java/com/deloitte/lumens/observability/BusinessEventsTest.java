package com.deloitte.lumens.observability;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.testing.exporter.InMemorySpanExporter;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.SimpleSpanProcessor;
import java.util.List;
import java.util.Map;
import java.util.Set;
import org.junit.jupiter.api.Test;

class BusinessEventsTest {
    @Test
    void emitsValidatedEventWithActiveTraceCorrelation() {
        var captured = new java.util.concurrent.atomic.AtomicReference<BusinessEvent>();
        BusinessEvents events = new BusinessEvents(
                new BusinessEventRegistry("1.0.0", Map.of("integration.enrichment.completed", Set.of("integration.provider"))),
                LumensAttributePolicies.registeredKeys(Set.of("integration.provider")),
                captured::set);
        InMemorySpanExporter exporter = InMemorySpanExporter.create();
        OpenTelemetrySdk telemetry = OpenTelemetrySdk.builder()
                .setTracerProvider(SdkTracerProvider.builder()
                        .addSpanProcessor(SimpleSpanProcessor.create(exporter))
                        .build())
                .build();

        var span = telemetry.getTracer("test").spanBuilder("parent").startSpan();
        try (var ignored = span.makeCurrent()) {
            assertTrue(events.emit("integration.enrichment.completed", Map.of("integration.provider", "example-provider")));
        } finally {
            span.end();
        }

        assertTrue(captured.get().attributes().containsKey("trace_id"));
        assertTrue(captured.get().attributes().containsKey("span_id"));
        telemetry.close();
    }

    @Test
    void dropsUnregisteredIncompleteAndSinkFailureEvents() {
        BusinessEvents events = new BusinessEvents(
                new BusinessEventRegistry("1.0.0", Map.of("integration.enrichment.completed", Set.of("integration.provider"))),
                LumensAttributePolicies.registeredKeys(Set.of("integration.provider")),
                event -> { throw new IllegalStateException("sink down"); });

        assertFalse(events.emit("unknown.event", Map.of()));
        assertFalse(events.emit("integration.enrichment.completed", Map.of("password", "dropped")));
        assertFalse(events.emit("integration.enrichment.completed", Map.of("integration.provider", "example-provider")));
    }
}

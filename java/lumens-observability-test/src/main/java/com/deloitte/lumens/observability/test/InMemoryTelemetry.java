package com.deloitte.lumens.observability.test;

import com.deloitte.lumens.observability.LumensAttributePolicies;
import com.deloitte.lumens.observability.LumensAttributePolicy;
import com.deloitte.lumens.observability.LumensOperations;
import com.deloitte.lumens.observability.LumensOperationsFactory;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.metrics.SdkMeterProvider;
import io.opentelemetry.sdk.metrics.data.MetricData;
import io.opentelemetry.sdk.testing.exporter.InMemoryMetricReader;
import io.opentelemetry.sdk.testing.exporter.InMemorySpanExporter;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.data.SpanData;
import io.opentelemetry.sdk.trace.export.SimpleSpanProcessor;
import java.util.Collection;
import java.util.List;
import java.util.Set;

/** In-memory OpenTelemetry fixture for Lumens unit and integration tests. */
public final class InMemoryTelemetry implements AutoCloseable {
    private final InMemorySpanExporter spans;
    private final InMemoryMetricReader metrics;
    private final OpenTelemetrySdk openTelemetry;

    public static InMemoryTelemetry create(Set<String> registeredAttributes) {
        InMemorySpanExporter spans = InMemorySpanExporter.create();
        InMemoryMetricReader metrics = InMemoryMetricReader.create();
        OpenTelemetrySdk sdk = OpenTelemetrySdk.builder()
                .setTracerProvider(SdkTracerProvider.builder()
                        .addSpanProcessor(SimpleSpanProcessor.create(spans))
                        .build())
                .setMeterProvider(SdkMeterProvider.builder()
                        .registerMetricReader(metrics)
                        .build())
                .build();
        return new InMemoryTelemetry(sdk, spans, metrics);
    }

    private InMemoryTelemetry(OpenTelemetrySdk openTelemetry, InMemorySpanExporter spans, InMemoryMetricReader metrics) {
        this.openTelemetry = openTelemetry;
        this.spans = spans;
        this.metrics = metrics;
    }

    public OpenTelemetry openTelemetry() {
        return openTelemetry;
    }

    public LumensOperations operations(String contractVersion, Set<String> registeredAttributes) {
        LumensAttributePolicy policy = LumensAttributePolicies.registeredKeys(registeredAttributes);
        return LumensOperationsFactory.create(openTelemetry, contractVersion, policy);
    }

    public List<SpanData> finishedSpans() {
        return spans.getFinishedSpanItems();
    }

    public Collection<MetricData> metrics() {
        return metrics.collectAllMetrics();
    }

    @Override
    public void close() {
        openTelemetry.close();
    }
}

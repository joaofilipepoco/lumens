package com.deloitte.lumens.observability.test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.deloitte.lumens.observability.LumensOperation;
import com.deloitte.lumens.observability.LumensOperations;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.sdk.metrics.data.MetricData;
import io.opentelemetry.sdk.trace.data.SpanData;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CancellationException;
import java.util.concurrent.CompletableFuture;
import org.junit.jupiter.api.Test;

class LumensOperationsTest {
    private static final Set<String> REGISTERED = Set.of("integration.provider", "safe.attribute");

    @Test
    void recordsNestedParentageOutcomeAndIndependentMetrics() {
        try (InMemoryTelemetry telemetry = InMemoryTelemetry.create(REGISTERED)) {
            LumensOperations operations = telemetry.operations("1.0.0", REGISTERED);

            operations.observe("payment.authorize", Map.of("integration.provider", "example-provider"), outer -> {
                outer.setOutcome("declined");
                return operations.observe("integration.enrich", Map.of("safe.attribute", "accepted"), inner -> "ok");
            });

            SpanData outer = TelemetryAssertions.spanNamed(telemetry.finishedSpans(), "payment.authorize");
            SpanData inner = TelemetryAssertions.spanNamed(telemetry.finishedSpans(), "integration.enrich");
            TelemetryAssertions.isChildOf(inner, outer);
            assertEquals("declined", outer.getAttributes().get(io.opentelemetry.api.common.AttributeKey.stringKey("lumens.operation.outcome")));
            assertEquals("accepted", inner.getAttributes().get(io.opentelemetry.api.common.AttributeKey.stringKey("safe.attribute")));
            assertTrue(telemetry.metrics().stream().map(MetricData::getName).anyMatch("lumens.operation.executions"::equals));
            assertTrue(telemetry.metrics().stream().map(MetricData::getName).anyMatch("lumens.operation.duration"::equals));
        }
    }

    @Test
    void recordsUnhandledFailureOnceAndRethrowsOriginalRuntimeException() {
        try (InMemoryTelemetry telemetry = InMemoryTelemetry.create(REGISTERED)) {
            LumensOperations operations = telemetry.operations("1.0.0", REGISTERED);
            IllegalStateException failure = new IllegalStateException("do not export this message");

            IllegalStateException thrown = assertThrows(IllegalStateException.class,
                    () -> operations.observe("payment.authorize", Map.of(), ignored -> {
                        throw failure;
                    }));

            assertEquals(failure, thrown);
            SpanData span = TelemetryAssertions.spanNamed(telemetry.finishedSpans(), "payment.authorize");
            assertEquals(StatusCode.ERROR, span.getStatus().getStatusCode());
            assertEquals("failure", span.getAttributes().get(io.opentelemetry.api.common.AttributeKey.stringKey("lumens.operation.outcome")));
            assertEquals(1, span.getEvents().size());
            assertEquals(IllegalStateException.class.getName(), span.getAttributes().get(io.opentelemetry.api.common.AttributeKey.stringKey("error.type")));
            assertFalse(span.getAttributes().asMap().toString().contains("do not export this message"));
        }
    }

    @Test
    void treatsCancellationAsControlFlow() {
        try (InMemoryTelemetry telemetry = InMemoryTelemetry.create(REGISTERED)) {
            LumensOperations operations = telemetry.operations("1.0.0", REGISTERED);

            assertThrows(CancellationException.class, () -> operations.observe("payment.authorize", Map.of(), ignored -> {
                throw new CancellationException();
            }));

            SpanData span = TelemetryAssertions.spanNamed(telemetry.finishedSpans(), "payment.authorize");
            assertEquals(StatusCode.UNSET, span.getStatus().getStatusCode());
            assertEquals("cancelled", span.getAttributes().get(io.opentelemetry.api.common.AttributeKey.stringKey("lumens.operation.outcome")));
            assertTrue(span.getEvents().isEmpty());
        }
    }

    @Test
    void manualOperationEndsOnceAndDropsUnregisteredOrSensitiveAttributes() {
        try (InMemoryTelemetry telemetry = InMemoryTelemetry.create(REGISTERED)) {
            LumensOperations operations = telemetry.operations("1.0.0", REGISTERED);
            LumensOperation operation = operations.start("payment.authorize", Map.of(
                    "safe.attribute", "kept",
                    "request.password", "dropped",
                    "unregistered", "dropped"));
            operation.setOutcome("approved");
            operation.close();
            operation.close();

            assertEquals(1, telemetry.finishedSpans().size());
            SpanData span = telemetry.finishedSpans().getFirst();
            assertEquals("kept", span.getAttributes().get(io.opentelemetry.api.common.AttributeKey.stringKey("safe.attribute")));
            assertFalse(span.getAttributes().asMap().containsKey(io.opentelemetry.api.common.AttributeKey.stringKey("request.password")));
            assertFalse(span.getAttributes().asMap().containsKey(io.opentelemetry.api.common.AttributeKey.stringKey("unregistered")));
        }
    }

    @Test
    void closesAsyncSpanOnCompletionAndRecordsFailure() {
        try (InMemoryTelemetry telemetry = InMemoryTelemetry.create(REGISTERED)) {
            LumensOperations operations = telemetry.operations("1.0.0", REGISTERED);
            CompletableFuture<String> future = new CompletableFuture<>();

            var observed = operations.observeAsync("payment.authorize", Map.of(), ignored -> future);
            assertTrue(telemetry.finishedSpans().isEmpty());
            future.completeExceptionally(new IllegalArgumentException("failure"));
            assertThrows(Exception.class, observed.toCompletableFuture()::join);

            SpanData span = TelemetryAssertions.spanNamed(telemetry.finishedSpans(), "payment.authorize");
            assertEquals(StatusCode.ERROR, span.getStatus().getStatusCode());
            assertEquals("failure", span.getAttributes().get(io.opentelemetry.api.common.AttributeKey.stringKey("lumens.operation.outcome")));
        }
    }
}

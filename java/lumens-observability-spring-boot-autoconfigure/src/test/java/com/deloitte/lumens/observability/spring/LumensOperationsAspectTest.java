package com.deloitte.lumens.observability.spring;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import com.deloitte.lumens.observability.LumensAttributePolicies;
import com.deloitte.lumens.observability.LumensOperations;
import com.deloitte.lumens.observability.LumensOperationsFactory;
import com.deloitte.lumens.observability.ObservedOperation;
import io.opentelemetry.sdk.OpenTelemetrySdk;
import io.opentelemetry.sdk.testing.exporter.InMemorySpanExporter;
import io.opentelemetry.sdk.trace.SdkTracerProvider;
import io.opentelemetry.sdk.trace.export.SimpleSpanProcessor;
import java.lang.reflect.Method;
import java.util.concurrent.CompletableFuture;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.reflect.MethodSignature;
import org.junit.jupiter.api.Test;

class LumensOperationsAspectTest {
    @Test
    void createsSpanOnlyForAnnotatedInternalOperation() throws Throwable {
        InMemorySpanExporter exporter = InMemorySpanExporter.create();
        OpenTelemetrySdk telemetry = OpenTelemetrySdk.builder()
                .setTracerProvider(SdkTracerProvider.builder()
                        .addSpanProcessor(SimpleSpanProcessor.create(exporter))
                        .build())
                .build();
        LumensOperations operations = LumensOperationsFactory.create(
                telemetry, "1.0.0", LumensAttributePolicies.denyAll());
        LumensOperationsAspect aspect = new LumensOperationsAspect(operations);
        Method method = Target.class.getDeclaredMethod("internal");
        ProceedingJoinPoint joinPoint = new StubJoinPoint("result");

        assertEquals("result", aspect.observe(joinPoint, method.getAnnotation(ObservedOperation.class)));
        assertEquals(1, exporter.getFinishedSpanItems().size());
        assertEquals("integration.enrich", exporter.getFinishedSpanItems().getFirst().getName());
        telemetry.close();
    }

    @Test
    void endsAnnotatedAsyncOperationOnStageCompletion() throws Throwable {
        InMemorySpanExporter exporter = InMemorySpanExporter.create();
        OpenTelemetrySdk telemetry = OpenTelemetrySdk.builder()
                .setTracerProvider(SdkTracerProvider.builder()
                        .addSpanProcessor(SimpleSpanProcessor.create(exporter))
                        .build())
                .build();
        LumensOperations operations = LumensOperationsFactory.create(
                telemetry, "1.0.0", LumensAttributePolicies.denyAll());
        LumensOperationsAspect aspect = new LumensOperationsAspect(operations);
        Method method = Target.class.getDeclaredMethod("internal");
        CompletableFuture<String> future = new CompletableFuture<>();

        Object observed = aspect.observe(new StubJoinPoint(future), method.getAnnotation(ObservedOperation.class));
        assertTrue(observed instanceof java.util.concurrent.CompletionStage<?>);
        assertEquals(0, exporter.getFinishedSpanItems().size());
        future.complete("result");
        assertEquals(1, exporter.getFinishedSpanItems().size());
        telemetry.close();
    }

    static class Target {
        @ObservedOperation("integration.enrich")
        String internal() {
            return "result";
        }
    }

    private record StubJoinPoint(Object result) implements ProceedingJoinPoint {
        @Override public Object proceed() { return result; }
        @Override public Object proceed(Object[] args) { return result; }
        @Override public String toShortString() { return "stub"; }
        @Override public String toLongString() { return "stub"; }
        @Override public Object getThis() { return null; }
        @Override public Object getTarget() { return null; }
        @Override public Object[] getArgs() { return new Object[0]; }
        @Override public String getKind() { return "method-execution"; }
        @Override public org.aspectj.lang.Signature getSignature() { return null; }
        @Override public org.aspectj.lang.reflect.SourceLocation getSourceLocation() { return null; }
        @Override public org.aspectj.lang.JoinPoint.StaticPart getStaticPart() { return null; }
        @Override public void set$AroundClosure(org.aspectj.runtime.internal.AroundClosure arc) {}
    }
}

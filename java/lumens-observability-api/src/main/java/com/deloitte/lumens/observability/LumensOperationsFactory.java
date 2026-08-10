package com.deloitte.lumens.observability;

import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.common.AttributeKey;
import io.opentelemetry.api.common.Attributes;
import io.opentelemetry.api.metrics.DoubleHistogram;
import io.opentelemetry.api.metrics.LongCounter;
import io.opentelemetry.api.trace.Span;
import io.opentelemetry.api.trace.SpanKind;
import io.opentelemetry.api.trace.StatusCode;
import io.opentelemetry.api.trace.Tracer;
import io.opentelemetry.context.Scope;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.CancellationException;
import java.util.concurrent.CompletionException;
import java.util.concurrent.CompletionStage;
import java.util.concurrent.atomic.AtomicBoolean;

/** Creates core Lumens operations from application-owned OpenTelemetry instances. */
public final class LumensOperationsFactory {
    public static final String INSTRUMENTATION_SCOPE = "com.deloitte.lumens.observability";
    public static final String OPERATION_NAME = "lumens.operation.name";
    public static final String OPERATION_OUTCOME = "lumens.operation.outcome";
    public static final String CONTRACT_VERSION = "lumens.contract.version";
    public static final String EXECUTIONS = "lumens.operation.executions";
    public static final String DURATION = "lumens.operation.duration";

    private LumensOperationsFactory() {}

    /** Creates operations that reject all custom attributes until a contract-derived policy is supplied. */
    public static LumensOperations create(OpenTelemetry openTelemetry, String contractVersion) {
        return create(openTelemetry, contractVersion, LumensAttributePolicies.denyAll());
    }

    public static LumensOperations create(
            OpenTelemetry openTelemetry,
            String contractVersion,
            LumensAttributePolicy attributePolicy) {
        Objects.requireNonNull(openTelemetry, "openTelemetry");
        Objects.requireNonNull(contractVersion, "contractVersion");
        Objects.requireNonNull(attributePolicy, "attributePolicy");
        Tracer tracer = openTelemetry.getTracer(INSTRUMENTATION_SCOPE);
        LongCounter executions = openTelemetry.getMeter(INSTRUMENTATION_SCOPE)
                .counterBuilder(EXECUTIONS)
                .build();
        DoubleHistogram duration = openTelemetry.getMeter(INSTRUMENTATION_SCOPE)
                .histogramBuilder(DURATION)
                .setUnit("s")
                .build();
        return new DefaultLumensOperations(tracer, executions, duration, contractVersion, attributePolicy);
    }

    private static final class DefaultLumensOperations implements LumensOperations {
        private final Tracer tracer;
        private final LongCounter executions;
        private final DoubleHistogram duration;
        private final String contractVersion;
        private final LumensAttributePolicy policy;

        private DefaultLumensOperations(
                Tracer tracer,
                LongCounter executions,
                DoubleHistogram duration,
                String contractVersion,
                LumensAttributePolicy policy) {
            this.tracer = tracer;
            this.executions = executions;
            this.duration = duration;
            this.contractVersion = contractVersion;
            this.policy = policy;
        }

        @Override
        public LumensOperation start(String operationName, Map<String, String> attributes) {
            validateOperationName(operationName);
            return new DefaultLumensOperation(
                    tracer.spanBuilder(operationName).setSpanKind(SpanKind.INTERNAL).startSpan(),
                    executions,
                    duration,
                    operationName,
                    contractVersion,
                    policy.apply(Map.copyOf(attributes)));
        }

        @Override
        public <T> T observe(String operationName, Map<String, String> attributes, LumensOperationCallback<T> callback) {
            Objects.requireNonNull(callback, "callback");
            LumensOperation operation = start(operationName, attributes);
            try {
                return callback.execute(operation);
            } catch (CancellationException cancellation) {
                operation.setOutcome("cancelled");
                throw cancellation;
            } catch (RuntimeException exception) {
                operation.fail(exception);
                throw exception;
            } finally {
                operation.close();
            }
        }

        @Override
        public <T> CompletionStage<T> observeAsync(
                String operationName,
                Map<String, String> attributes,
                LumensOperationCallback<CompletionStage<T>> callback) {
            Objects.requireNonNull(callback, "callback");
            LumensOperation operation = start(operationName, attributes);
            try {
                CompletionStage<T> stage = callback.execute(operation);
                if (stage == null) {
                    operation.fail(new NullPointerException("Async operation returned null CompletionStage."));
                    operation.close();
                    throw new NullPointerException("Async operation returned null CompletionStage.");
                }
                return stage.whenComplete((ignored, error) -> {
                    if (error != null) {
                        Throwable cause = unwrap(error);
                        if (cause instanceof CancellationException) {
                            operation.setOutcome("cancelled");
                        } else {
                            operation.fail(cause);
                        }
                    }
                    operation.close();
                });
            } catch (CancellationException cancellation) {
                operation.setOutcome("cancelled");
                operation.close();
                throw cancellation;
            } catch (RuntimeException exception) {
                operation.fail(exception);
                operation.close();
                throw exception;
            } finally {
                operation.detach();
            }
        }

    }

    private static final class DefaultLumensOperation implements LumensOperation {
        private final Span span;
        private final Scope scope;
        private final LongCounter executions;
        private final DoubleHistogram duration;
        private final String operationName;
        private final long startedAtNanos;
        private final AtomicBoolean closed = new AtomicBoolean();
        private final AtomicBoolean detached = new AtomicBoolean();
        private String outcome = "success";

        private DefaultLumensOperation(
                Span span,
                LongCounter executions,
                DoubleHistogram duration,
                String operationName,
                String contractVersion,
                Map<String, String> attributes) {
            this.span = span;
            this.scope = span.makeCurrent();
            this.executions = executions;
            this.duration = duration;
            this.operationName = operationName;
            this.startedAtNanos = System.nanoTime();
            span.setAttribute(OPERATION_NAME, operationName);
            span.setAttribute(CONTRACT_VERSION, contractVersion);
            attributes.forEach(span::setAttribute);
        }

        @Override
        public void setOutcome(String outcome) {
            if (closed.get()) {
                return;
            }
            this.outcome = requireBoundedOutcome(outcome);
            span.setAttribute(OPERATION_OUTCOME, this.outcome);
        }

        @Override
        public void fail(Throwable error) {
            if (closed.get() || error instanceof CancellationException) {
                return;
            }
            outcome = "failure";
            span.setAttribute(OPERATION_OUTCOME, outcome);
            span.recordException(error);
            span.setStatus(StatusCode.ERROR);
            span.setAttribute("error.type", error.getClass().getName());
        }

        @Override
        public void close() {
            if (!closed.compareAndSet(false, true)) {
                return;
            }
            span.setAttribute(OPERATION_OUTCOME, outcome);
            Attributes metricAttributes = Attributes.builder()
                    .put(OPERATION_NAME, operationName)
                    .put(OPERATION_OUTCOME, outcome)
                    .build();
            executions.add(1, metricAttributes);
            duration.record(Math.max(0, (System.nanoTime() - startedAtNanos) / 1_000_000_000.0), metricAttributes);
            try {
                detach();
            } finally {
                span.end();
            }
        }

        @Override
        public void detach() {
            if (detached.compareAndSet(false, true)) {
                scope.close();
            }
        }
    }

    private static void validateOperationName(String operationName) {
        if (operationName == null || operationName.isBlank() || !operationName.matches("[a-z][a-z0-9]*(?:[._-][a-z0-9]+)*")) {
            throw new IllegalArgumentException("Operation name must be a stable lowercase identifier.");
        }
    }

    private static String requireBoundedOutcome(String outcome) {
        if (outcome == null || outcome.isBlank() || !outcome.matches("[a-z][a-z0-9_-]*")) {
            throw new IllegalArgumentException("Outcome must be a stable lowercase bounded identifier.");
        }
        return outcome;
    }

    private static Throwable unwrap(Throwable error) {
        if (error instanceof CompletionException && error.getCause() != null) {
            return error.getCause();
        }
        return error;
    }
}

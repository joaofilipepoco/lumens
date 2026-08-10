package com.deloitte.lumens.observability.spring;

import com.deloitte.lumens.observability.LumensOperation;
import com.deloitte.lumens.observability.LumensOperations;
import com.deloitte.lumens.observability.ObservedOperation;
import java.util.Map;
import java.util.concurrent.CancellationException;
import java.util.concurrent.CompletionException;
import java.util.concurrent.CompletionStage;
import org.aspectj.lang.ProceedingJoinPoint;
import org.aspectj.lang.annotation.Around;
import org.aspectj.lang.annotation.Aspect;

/** Creates operation spans only for explicitly annotated internal methods. */
@Aspect
public final class LumensOperationsAspect {
    private final LumensOperations operations;

    public LumensOperationsAspect(LumensOperations operations) {
        this.operations = operations;
    }

    @Around("@annotation(observedOperation)")
    public Object observe(ProceedingJoinPoint joinPoint, ObservedOperation observedOperation) throws Throwable {
        LumensOperation operation = operations.start(observedOperation.value(), Map.of());
        try {
            Object result = joinPoint.proceed();
            if (result instanceof CompletionStage<?> stage) {
                operation.detach();
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
            }
            operation.close();
            return result;
        } catch (CancellationException cancellation) {
            operation.setOutcome("cancelled");
            operation.close();
            throw cancellation;
        } catch (Throwable error) {
            operation.fail(error);
            operation.close();
            throw error;
        }
    }

    private static Throwable unwrap(Throwable error) {
        return error instanceof CompletionException && error.getCause() != null ? error.getCause() : error;
    }
}

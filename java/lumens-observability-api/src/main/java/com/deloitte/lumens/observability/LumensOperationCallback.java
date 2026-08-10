package com.deloitte.lumens.observability;

@FunctionalInterface
public interface LumensOperationCallback<T> {
    T execute(LumensOperation operation);
}

package com.deloitte.lumens.observability;

import java.util.Map;
import java.util.concurrent.CompletionStage;

/** Starts and observes distinct internal operations. */
public interface LumensOperations {
    LumensOperation start(String operationName, Map<String, String> attributes);

    <T> T observe(String operationName, Map<String, String> attributes, LumensOperationCallback<T> callback);

    <T> CompletionStage<T> observeAsync(
            String operationName,
            Map<String, String> attributes,
            LumensOperationCallback<CompletionStage<T>> callback);
}

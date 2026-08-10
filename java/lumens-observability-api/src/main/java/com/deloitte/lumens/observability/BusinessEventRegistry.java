package com.deloitte.lumens.observability;

import java.util.Map;
import java.util.Set;

/** Contract-derived registry used to validate event names and declared fields. */
public record BusinessEventRegistry(String contractVersion, Map<String, Set<String>> requiredAttributes) {
    public BusinessEventRegistry {
        requiredAttributes = requiredAttributes.entrySet().stream()
                .collect(java.util.stream.Collectors.toUnmodifiableMap(
                        Map.Entry::getKey,
                        entry -> Set.copyOf(entry.getValue())));
    }
}

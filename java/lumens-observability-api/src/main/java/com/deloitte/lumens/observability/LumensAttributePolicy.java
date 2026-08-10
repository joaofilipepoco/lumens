package com.deloitte.lumens.observability;

import java.util.Map;

/** Validates and filters custom attributes before they enter telemetry. */
@FunctionalInterface
public interface LumensAttributePolicy {
    Map<String, String> apply(Map<String, String> attributes);
}

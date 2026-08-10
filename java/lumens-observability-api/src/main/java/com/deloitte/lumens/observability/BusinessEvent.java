package com.deloitte.lumens.observability;

import java.util.Map;

/** A registered point-in-time business occurrence, distinct from a span or metric. */
public record BusinessEvent(String name, Map<String, String> attributes) {
    public BusinessEvent {
        attributes = Map.copyOf(attributes);
    }
}

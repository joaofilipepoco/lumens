package com.deloitte.lumens.observability;

import io.opentelemetry.api.trace.Span;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.Objects;
import java.util.Set;

/** Emits validated business events without affecting application control flow. */
public final class BusinessEvents {
    private final BusinessEventRegistry registry;
    private final LumensAttributePolicy policy;
    private final BusinessEventSink sink;

    public BusinessEvents(BusinessEventRegistry registry, LumensAttributePolicy policy, BusinessEventSink sink) {
        this.registry = Objects.requireNonNull(registry, "registry");
        this.policy = Objects.requireNonNull(policy, "policy");
        this.sink = Objects.requireNonNull(sink, "sink");
    }

    /** Returns false for invalid events or sink failures so business logic is never interrupted. */
    public boolean emit(String eventName, Map<String, String> attributes) {
        Set<String> required = registry.requiredAttributes().get(eventName);
        if (required == null) {
            return false;
        }
        Map<String, String> accepted = policy.apply(attributes);
        if (!accepted.keySet().containsAll(required)) {
            return false;
        }
        Map<String, String> envelope = new LinkedHashMap<>();
        envelope.put("event.name", eventName);
        envelope.put("event.schema.version", registry.contractVersion());
        envelope.put("lumens.contract.version", registry.contractVersion());
        SpanContextValues.addCurrentSpanCorrelation(envelope);
        envelope.putAll(accepted);
        try {
            sink.emit(new BusinessEvent(eventName, envelope));
            return true;
        } catch (RuntimeException ignored) {
            return false;
        }
    }

    private static final class SpanContextValues {
        private static void addCurrentSpanCorrelation(Map<String, String> attributes) {
            var context = Span.current().getSpanContext();
            if (context.isValid()) {
                attributes.put("trace_id", context.getTraceId());
                attributes.put("span_id", context.getSpanId());
            }
        }
    }
}

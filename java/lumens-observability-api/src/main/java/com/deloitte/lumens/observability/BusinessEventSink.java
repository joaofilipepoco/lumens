package com.deloitte.lumens.observability;

@FunctionalInterface
public interface BusinessEventSink {
    void emit(BusinessEvent event);
}

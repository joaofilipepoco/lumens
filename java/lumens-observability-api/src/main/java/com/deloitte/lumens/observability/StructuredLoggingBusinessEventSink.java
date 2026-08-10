package com.deloitte.lumens.observability;

import java.util.logging.Logger;

/** Default non-audit-grade sink that emits an event envelope as one structured log message. */
public final class StructuredLoggingBusinessEventSink implements BusinessEventSink {
    private final Logger logger;

    public StructuredLoggingBusinessEventSink(Logger logger) {
        this.logger = logger;
    }

    @Override
    public void emit(BusinessEvent event) {
        logger.info(() -> event.attributes().toString());
    }
}

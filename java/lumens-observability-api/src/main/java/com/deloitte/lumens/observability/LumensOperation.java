package com.deloitte.lumens.observability;

/** A manually managed internal operation. Call {@link #fail(Throwable)} for handled failures. */
public interface LumensOperation extends AutoCloseable {
    void setOutcome(String outcome);

    void fail(Throwable error);

    @Override
    void close();
}

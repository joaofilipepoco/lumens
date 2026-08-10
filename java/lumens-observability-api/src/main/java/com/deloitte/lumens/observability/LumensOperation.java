package com.deloitte.lumens.observability;

/** A manually managed internal operation. Call {@link #fail(Throwable)} for handled failures. */
public interface LumensOperation extends AutoCloseable {
    void setOutcome(String outcome);

    void fail(Throwable error);

    /**
     * Releases the operation context without ending its span. Framework adapters use this before an
     * asynchronous result completes; application code should normally use {@link #close()} instead.
     */
    void detach();

    @Override
    void close();
}

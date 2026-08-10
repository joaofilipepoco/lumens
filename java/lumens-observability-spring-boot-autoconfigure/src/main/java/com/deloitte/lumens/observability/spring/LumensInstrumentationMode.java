package com.deloitte.lumens.observability.spring;

/** Chooses who initializes OpenTelemetry providers and standard framework instrumentation. */
public enum LumensInstrumentationMode {
    PLATFORM_MANAGED,
    APPLICATION_MANAGED
}

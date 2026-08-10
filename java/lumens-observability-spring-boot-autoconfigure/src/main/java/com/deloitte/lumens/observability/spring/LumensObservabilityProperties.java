package com.deloitte.lumens.observability.spring;

import java.util.LinkedHashSet;
import java.util.Set;
import org.springframework.boot.context.properties.ConfigurationProperties;

/** Lumens-specific settings; standard OTEL_* configuration remains owned by OpenTelemetry. */
@ConfigurationProperties("lumens.observability")
public class LumensObservabilityProperties {
    private LumensInstrumentationMode mode = LumensInstrumentationMode.PLATFORM_MANAGED;
    private String contractVersion = "1.0.0";
    private Set<String> registeredAttributes = new LinkedHashSet<>();

    public LumensInstrumentationMode getMode() {
        return mode;
    }

    public void setMode(LumensInstrumentationMode mode) {
        this.mode = mode;
    }

    public String getContractVersion() {
        return contractVersion;
    }

    public void setContractVersion(String contractVersion) {
        this.contractVersion = contractVersion;
    }

    public Set<String> getRegisteredAttributes() {
        return registeredAttributes;
    }

    public void setRegisteredAttributes(Set<String> registeredAttributes) {
        this.registeredAttributes = new LinkedHashSet<>(registeredAttributes);
    }
}

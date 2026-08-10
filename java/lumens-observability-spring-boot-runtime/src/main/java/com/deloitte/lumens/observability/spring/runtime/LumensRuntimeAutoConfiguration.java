package com.deloitte.lumens.observability.spring.runtime;

import com.deloitte.lumens.observability.spring.LumensInstrumentationMode;
import com.deloitte.lumens.observability.spring.LumensObservabilityProperties;
import com.deloitte.lumens.observability.spring.LumensRuntimeArtifact;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.sdk.autoconfigure.AutoConfiguredOpenTelemetrySdk;
import org.springframework.beans.factory.ObjectProvider;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.context.annotation.Bean;

/** Initializes OpenTelemetry from standard OTEL_* settings in application-managed mode. */
@AutoConfiguration(beforeName = "com.deloitte.lumens.observability.spring.LumensObservabilityAutoConfiguration")
public class LumensRuntimeAutoConfiguration {
    @Bean
    LumensRuntimeArtifact lumensRuntimeArtifact() {
        return new LumensRuntimeArtifact();
    }

    @Bean
    @ConditionalOnMissingBean(OpenTelemetry.class)
    OpenTelemetry applicationManagedOpenTelemetry(
            LumensObservabilityProperties properties,
            ObjectProvider<OpenTelemetry> existingTelemetry) {
        if (properties.getMode() != LumensInstrumentationMode.APPLICATION_MANAGED) {
            throw new IllegalStateException(
                    "The Lumens application-managed runtime artifact requires "
                            + "lumens.observability.mode=APPLICATION_MANAGED.");
        }
        OpenTelemetry existing = existingTelemetry.getIfAvailable();
        if (existing != null) {
            return existing;
        }
        return AutoConfiguredOpenTelemetrySdk.initialize().getOpenTelemetrySdk();
    }
}

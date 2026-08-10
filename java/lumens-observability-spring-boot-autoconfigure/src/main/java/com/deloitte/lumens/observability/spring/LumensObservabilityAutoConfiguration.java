package com.deloitte.lumens.observability.spring;

import com.deloitte.lumens.observability.LumensAttributePolicies;
import com.deloitte.lumens.observability.LumensOperations;
import com.deloitte.lumens.observability.LumensOperationsFactory;
import io.opentelemetry.api.OpenTelemetry;
import io.opentelemetry.api.GlobalOpenTelemetry;
import org.springframework.beans.factory.InitializingBean;
import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.EnableAspectJAutoProxy;

/** Configures Lumens business instrumentation without owning exporter configuration. */
@AutoConfiguration
@EnableConfigurationProperties(LumensObservabilityProperties.class)
@EnableAspectJAutoProxy
public class LumensObservabilityAutoConfiguration {
    @Bean
    InitializingBean lumensModeValidator(
            LumensObservabilityProperties properties,
            org.springframework.beans.factory.ObjectProvider<LumensRuntimeArtifact> runtimeArtifact) {
        return () -> {
            if (properties.getMode() == LumensInstrumentationMode.PLATFORM_MANAGED
                    && runtimeArtifact.getIfAvailable() != null) {
                throw new IllegalStateException(
                        "The Lumens application-managed runtime artifact is present while "
                                + "lumens.observability.mode is PLATFORM_MANAGED. Remove the runtime artifact "
                                + "or select APPLICATION_MANAGED.");
            }
        };
    }

    @Bean
    @ConditionalOnMissingBean
    LumensOperations lumensOperations(
            LumensObservabilityProperties properties,
            org.springframework.beans.factory.ObjectProvider<OpenTelemetry> openTelemetry) {
        OpenTelemetry telemetry = properties.getMode() == LumensInstrumentationMode.APPLICATION_MANAGED
                ? openTelemetry.getIfAvailable(GlobalOpenTelemetry::get)
                : GlobalOpenTelemetry.get();
        return LumensOperationsFactory.create(
                telemetry,
                properties.getContractVersion(),
                LumensAttributePolicies.registeredKeys(properties.getRegisteredAttributes()));
    }

    @Bean
    @ConditionalOnMissingBean
    LumensOperationsAspect lumensOperationsAspect(LumensOperations operations) {
        return new LumensOperationsAspect(operations);
    }
}

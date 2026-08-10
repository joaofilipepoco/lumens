package com.deloitte.lumens.observability.spring.runtime;

import static org.assertj.core.api.Assertions.assertThat;

import com.deloitte.lumens.observability.LumensOperations;
import com.deloitte.lumens.observability.spring.LumensObservabilityAutoConfiguration;
import io.opentelemetry.api.OpenTelemetry;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;

class LumensRuntimeAutoConfigurationTest {
    private final ApplicationContextRunner contextRunner = new ApplicationContextRunner()
            .withPropertyValues("lumens.observability.mode=application-managed")
            .withUserConfiguration(
                    LumensRuntimeAutoConfiguration.class,
                    LumensObservabilityAutoConfiguration.class);

    @Test
    void applicationManagedModeUsesApplicationSuppliedOpenTelemetry() {
        contextRunner
                .withBean(OpenTelemetry.class, OpenTelemetry::noop)
                .run(context -> {
                    assertThat(context).hasSingleBean(LumensOperations.class);
                    assertThat(context).hasSingleBean(OpenTelemetry.class);
                });
    }
}

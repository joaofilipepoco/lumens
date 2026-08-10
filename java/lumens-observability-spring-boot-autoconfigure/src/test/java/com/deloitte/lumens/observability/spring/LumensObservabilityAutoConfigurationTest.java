package com.deloitte.lumens.observability.spring;

import static org.assertj.core.api.Assertions.assertThat;

import com.deloitte.lumens.observability.LumensOperations;
import com.deloitte.lumens.observability.ObservedOperation;
import org.junit.jupiter.api.Test;
import org.springframework.boot.test.context.runner.ApplicationContextRunner;

class LumensObservabilityAutoConfigurationTest {
    private final ApplicationContextRunner contextRunner = new ApplicationContextRunner()
            .withUserConfiguration(LumensObservabilityAutoConfiguration.class);

    @Test
    void platformManagedModeCreatesBusinessOperationsWithoutOwningSdk() {
        contextRunner.run(context -> assertThat(context).hasSingleBean(LumensOperations.class));
    }

    @Test
    void platformManagedModeRejectsRuntimeArtifact() {
        contextRunner
                .withBean(LumensRuntimeArtifact.class)
                .run(context -> {
                    assertThat(context).hasFailed();
                    assertThat(context.getStartupFailure())
                            .hasMessageContaining("PLATFORM_MANAGED");
                });
    }

    @Test
    void appliesAspectOnlyToExplicitCustomOperations() {
        contextRunner
                .withBean(AnnotatedService.class)
                .run(context -> {
                    AnnotatedService service = context.getBean(AnnotatedService.class);
                    assertThat(service.internalOperation()).isEqualTo("internal");
                    assertThat(service.standardBoundary()).isEqualTo("standard");
                });
    }

    static class AnnotatedService {
        @ObservedOperation("integration.enrich")
        String internalOperation() {
            return "internal";
        }

        String standardBoundary() {
            return "standard";
        }
    }
}

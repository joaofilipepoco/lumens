package com.deloitte.lumens.example;

import com.deloitte.lumens.observability.LumensOperations;
import java.util.Map;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestClient;

@RestController
class EnrichmentController {
    private final LumensOperations operations;
    private final RestClient integrationClient;

    EnrichmentController(
            LumensOperations operations,
            @Value("${PYTHON_INTEGRATION_URL:http://localhost:8081}") String integrationUrl) {
        this.operations = operations;
        this.integrationClient = RestClient.builder().baseUrl(integrationUrl).build();
    }

    @GetMapping("/enrich")
    Map<String, Object> enrich() {
        // The HTTP server span is supplied by standard OpenTelemetry instrumentation, not Lumens.
        return operations.observe("integration.enrich", Map.of(), ignored -> integrationClient.get()
                .uri("/integrate")
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(Map.class));
    }
}

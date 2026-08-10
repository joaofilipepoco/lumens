package com.deloitte.lumens.example;

import com.deloitte.lumens.observability.LumensOperations;
import java.util.Map;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
class EnrichmentController {
    private final LumensOperations operations;

    EnrichmentController(LumensOperations operations) {
        this.operations = operations;
    }

    @GetMapping("/enrich")
    String enrich() {
        // The HTTP server span is supplied by standard OpenTelemetry instrumentation, not Lumens.
        return operations.observe("integration.enrich", Map.of(), ignored -> "enriched");
    }
}

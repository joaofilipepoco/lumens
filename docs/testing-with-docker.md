# Testing Lumens With Docker

Use the reference Spring Boot BFF and FastAPI integration service to validate Lumens in containers without provider credentials.

## Prerequisites

- Docker Desktop with Docker Compose.
- Ports `8080` and `8081` available locally.
- The repository checked out at the current `main` revision.

The Docker test does not require Dynatrace, Datadog, Splunk, Grafana Cloud, New Relic, an OpenTelemetry Collector, or any ingest token.

## Start The Reference Services

From the repository root:

```powershell
docker compose -f examples/cross-service/compose.yaml up --build -d
```

Check that both containers are running:

```powershell
docker compose -f examples/cross-service/compose.yaml ps
```

Inspect startup output when a container is not running:

```powershell
docker compose -f examples/cross-service/compose.yaml logs
```

## Exercise The Services

Call the Spring Boot BFF:

```powershell
Invoke-WebRequest http://localhost:8080/enrich
```

Expected response body:

```text
enriched
```

Call the FastAPI integration service:

```powershell
Invoke-RestMethod http://localhost:8081/integrate
```

Expected response:

```json
{
  "outcome": "success"
}
```

## What This Proves

- The Java Spring Boot reference service builds and runs with the Lumens Spring Boot starter.
- The FastAPI reference service builds and runs with Lumens FastAPI instrumentation.
- Standard server instrumentation is configured without Lumens route annotations or decorators.
- The reference services require no provider credentials and do not require a Deloitte-managed Collector.

## Current Conformance Boundary

The current Compose services are independent smoke-test services. The Java BFF does not yet make a live request to the FastAPI container, so Docker Compose does not prove live `traceparent` propagation between the two processes.

The repository's normalized OTLP fixture validates the intended Java client to Python server parentage, internal operation span, correlated business event, and operation metrics:

```powershell
uv run --system-certs --project python pytest examples/cross-service/tests
```

Run the full credential-free verifier for Java, Python, contract, provider-profile, and normalized cross-language checks:

```powershell
.\scripts\verify.ps1
```

## Stop And Clean Up

```powershell
docker compose -f examples/cross-service/compose.yaml down --remove-orphans
```

Add `--volumes` only when you intentionally want to remove any named volumes created by a future version of the harness.

## Test With A Provider

After the local Docker smoke test, choose a certified provider topology:

- Dynatrace direct OTLP pilot: see [Dynatrace](providers/dynatrace.md).
- Datadog Agent OTLP: see [Datadog](providers/datadog.md).
- Other certified topologies: see [Provider Destinations](providers/README.md).

Inject production endpoint and authentication configuration through the client deployment platform. Never place provider tokens in the Compose file, source code, or test fixtures.

# Verification

Run the full credential-free MVP verification from the repository root:

```powershell
./scripts/verify.ps1
```

The script verifies:

- Maven Java core, Spring integration, business-event, and test-kit suites.
- Python core, FastAPI, and business-event suites.
- Semantic contract schema, overlays, generated constants, and stale-file detection.
- Provider profile metadata without reading credentials.
- Normalized cross-language OTLP conformance fixture.

Provider live-ingestion tests are not run by default. They require client-owned endpoints and secrets and must clearly report a skip when unavailable.

The Compose harness is optional:

```powershell
docker compose -f examples/cross-service/compose.yaml up --build -d
```

It uses no provider credentials and remains separate from the required local verifier. See [testing Lumens with Docker](testing-with-docker.md) for service calls, expected responses, cleanup, and the current live cross-service propagation boundary.

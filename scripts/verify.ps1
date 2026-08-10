$ErrorActionPreference = 'Stop'

$requiredPaths = @(
    'README.md',
    'plan.md',
    'CONTRIBUTING.md',
    'docs/feature-status.md',
    'docs/architecture.md',
    'docs/architecture/context.md',
    'docs/architecture/components.md',
    'docs/architecture/telemetry-flows.md',
    'docs/architecture/deployment-models.md',
    'docs/architecture/security-boundaries.md',
    'docs/architecture/failure-model.md',
    'docs/architecture/roadmap.md',
    'docs/adr/001-opentelemetry-foundation.md',
    'docs/adr/002-explicit-instrumentation-modes.md',
    'docs/adr/003-business-event-delivery.md',
    'docs/adr/004-semantic-registry.md',
    'docs/adr/005-browser-deferred.md',
    'docs/adr/006-provider-managed-ingestion.md',
    'docs/adr/007-optional-collector-gateway.md',
    'docs/adr/008-agent-observability.md',
    'docs/adr/009-experience-generator.md',
    'docs/providers/compatibility-matrix.md',
    'java/pom.xml',
    'java/lumens-observability-api/pom.xml',
    'java/lumens-observability-spring-boot-autoconfigure/pom.xml',
    'java/lumens-observability-spring-boot-starter/pom.xml',
    'java/lumens-observability-spring-boot-runtime/pom.xml',
    'java/lumens-observability-test/pom.xml',
    'java/lumens-observability-bom/pom.xml',
    'python/pyproject.toml',
    'python/uv.lock',
    'tools/contract/pyproject.toml'
)

$missing = $requiredPaths | Where-Object { -not (Test-Path $_) }
if ($missing) {
    throw "MVP-F01 repository foundation is incomplete. Missing: $($missing -join ', ')"
}

Write-Host 'MVP-F01 repository foundation verification passed.'
if (Get-Command mvn -ErrorAction SilentlyContinue) {
    mvn -f java/pom.xml verify
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host 'MVP-F03 Java verification passed.'
} else {
    Write-Warning 'Maven is unavailable; MVP-F03 Java verification was skipped.'
}
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run --system-certs --project python pytest python/tests
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host 'MVP-F04 Python verification passed.'
} else {
    Write-Warning 'uv is unavailable; MVP-F04 Python verification was skipped.'
}
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run --system-certs --project tools/contract pytest tools/contract/tests
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    uv run --system-certs --project tools/contract lumens-contract generate --check
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    Write-Host 'MVP-F02 contract verification passed.'
} else {
    Write-Warning 'uv is unavailable; MVP-F02 contract verification was skipped.'
}

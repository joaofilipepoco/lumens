#!/usr/bin/env sh
set -eu

for path in \
  README.md \
  plan.md \
  CONTRIBUTING.md \
  docs/feature-status.md \
  docs/architecture.md \
  docs/architecture/context.md \
  docs/architecture/components.md \
  docs/architecture/telemetry-flows.md \
  docs/architecture/deployment-models.md \
  docs/architecture/security-boundaries.md \
  docs/architecture/failure-model.md \
  docs/architecture/roadmap.md \
  docs/adr/001-opentelemetry-foundation.md \
  docs/adr/002-explicit-instrumentation-modes.md \
  docs/adr/003-business-event-delivery.md \
  docs/adr/004-semantic-registry.md \
  docs/adr/005-browser-deferred.md \
  docs/adr/006-provider-managed-ingestion.md \
  docs/adr/007-optional-collector-gateway.md \
  docs/adr/008-agent-observability.md \
  docs/adr/009-experience-generator.md \
  docs/providers/compatibility-matrix.md \
  java/pom.xml \
  java/lumens-observability-api/pom.xml \
  java/lumens-observability-spring-boot-autoconfigure/pom.xml \
  java/lumens-observability-spring-boot-starter/pom.xml \
  java/lumens-observability-spring-boot-runtime/pom.xml \
  java/lumens-observability-test/pom.xml \
  java/lumens-observability-bom/pom.xml \
  python/pyproject.toml \
  python/uv.lock \
  tools/contract/pyproject.toml
  if [ ! -e "$path" ]; then
    printf 'MVP-F01 repository foundation is incomplete. Missing: %s\n' "$path" >&2
    exit 1
  fi

printf 'MVP-F01 repository foundation verification passed.\n'
if command -v mvn >/dev/null 2>&1; then
  mvn -f java/pom.xml verify
  printf 'MVP-F03, MVP-F05, and MVP-F07 Java verification passed.\n'
else
  printf 'Maven is unavailable; MVP-F03 Java verification was skipped.\n' >&2
fi
if command -v uv >/dev/null 2>&1; then
  uv run --system-certs --project python pytest examples/cross-service/tests
  uv run --system-certs --project python pytest python/tests
  printf 'MVP-F04, MVP-F06, and MVP-F07 Python verification passed.\n'
else
  printf 'uv is unavailable; MVP-F04 Python verification was skipped.\n' >&2
fi
if command -v uv >/dev/null 2>&1; then
  uv run --system-certs --project tools/contract python providers/validate_profiles.py
  uv run --system-certs --project tools/contract pytest providers/tests
  uv run --system-certs --project tools/contract pytest tools/contract/tests
  uv run --system-certs --project tools/contract lumens-contract generate --check
  printf 'MVP-F02 contract verification passed.\n'
else
  printf 'uv is unavailable; MVP-F02 contract verification was skipped.\n' >&2
fi

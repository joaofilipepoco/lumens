"""Validate provider destination profile metadata without resolving secrets."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED = {"provider", "support", "recommended_topology", "supported_topologies", "application_configuration", "endpoint_variable", "headers_variable", "signals", "credential_owner", "notes"}
CERTIFIED = {"dynatrace", "splunk", "datadog", "grafana-cloud", "new-relic"}
TOPOLOGIES = {"direct_otlp", "provider_agent", "provider_managed_component", "customer_collector"}


def main() -> int:
    profiles = sorted(Path("providers/profiles").glob("*/profile.yaml"))
    seen: set[str] = set()
    for profile_path in profiles:
        profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
        missing = REQUIRED - profile.keys()
        if missing:
            raise ValueError(f"{profile_path}: missing fields {sorted(missing)}")
        provider = profile["provider"]
        if provider in seen:
            raise ValueError(f"Duplicate provider profile '{provider}'.")
        seen.add(provider)
        if not profile["endpoint_variable"].startswith("OTEL_"):
            raise ValueError(f"{provider}: endpoint must use a standard OTEL_* variable.")
        if profile["headers_variable"] != "OTEL_EXPORTER_OTLP_HEADERS":
            raise ValueError(f"{provider}: headers must use the standard OTEL_EXPORTER_OTLP_HEADERS variable.")
        if profile["application_configuration"] != "standard_otel":
            raise ValueError(f"{provider}: Lumens profiles must use standard OTEL application configuration.")
        if profile["recommended_topology"] not in TOPOLOGIES or not set(profile["supported_topologies"]) <= TOPOLOGIES:
            raise ValueError(f"{provider}: unsupported delivery topology.")
        if profile["recommended_topology"] not in profile["supported_topologies"]:
            raise ValueError(f"{provider}: recommended topology must be supported.")
        if not set(profile["signals"]) <= {"traces", "metrics", "logs"}:
            raise ValueError(f"{provider}: unsupported signal declaration.")
    if not CERTIFIED <= seen:
        raise ValueError(f"Missing certified provider profiles: {sorted(CERTIFIED - seen)}")
    print(f"Validated {len(profiles)} provider profiles without resolving credentials.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, yaml.YAMLError) as error:
        print(f"provider-profile validation failed: {error}", file=sys.stderr)
        raise SystemExit(1)

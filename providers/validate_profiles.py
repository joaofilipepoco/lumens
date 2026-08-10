"""Validate provider destination profile metadata without resolving secrets."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

REQUIRED = {"provider", "support", "ingestion", "transport", "endpoint_variable", "token_variable", "header_name", "header_template", "signals", "notes"}
CERTIFIED = {"dynatrace", "splunk", "datadog", "grafana-cloud", "new-relic"}


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
        if profile["token_variable"] != "LUMENS_ACCESS_TOKEN":
            raise ValueError(f"{provider}: token variable must remain generic and secret-manager supplied.")
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

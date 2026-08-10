# Semantic Contract

The Lumens semantic contract is the versioned source of truth for cross-language business telemetry. It defines approved operation, attribute, event, metric-dimension, and baggage names together with ownership, descriptions, stability, privacy, and cardinality policies.

## Files

| File | Purpose |
|---|---|
| `contract/lumens-contract.yaml` | Base Lumens registry |
| `contract/lumens-contract.schema.json` | Structural JSON Schema validation |
| `contract/examples/client-overlay.yaml` | Example client extension |
| `contract/generated/` | Deterministically generated Java and Python constants |

## Validation Rules

- Contract and overlay YAML reject duplicate mapping keys.
- Names use lowercase dot, dash, or underscore separated identifiers.
- Operations have non-empty bounded outcomes.
- Events may reference only registered attributes.
- High-cardinality, personal, and secret attributes cannot be metric dimensions.
- Client overlays add definitions but cannot redefine base definitions or target an incompatible base version.
- Generated identifiers must not collide after Java or Python normalization.

## Commands

Generate the base contract constants:

```powershell
uv run --project tools/contract lumens-contract generate
```

Validate an overlay and generate constants using client output locations:

```powershell
uv run --project tools/contract lumens-contract generate `
  --overlay contract/examples/client-overlay.yaml `
  --java-package com.example.contract `
  --python-module example_contract `
  --java-output contract/generated/example/LumensContract.java `
  --python-output contract/generated/example/lumens_contract.py
```

Use `--check` in CI to reject missing or stale generated files:

```powershell
uv run --project tools/contract lumens-contract generate --check
```

The generator preserves runtime attribute names exactly. It creates constants for source-code use; it never rewrites telemetry names dynamically.

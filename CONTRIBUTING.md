# Contributing

Lumens is delivered incrementally. Implement only the explicitly requested feature in the `MVP Feature Plan` in `plan.md` and check its dependencies first.

## Feature Delivery

1. Confirm the requested feature identifier and its prerequisites.
2. Keep the change within that feature's scope and acceptance criteria.
3. Update affected architecture views, ADRs, contracts, provider documentation, and compatibility records.
4. Run feasible verification and report unavailable tools or external credentials.
5. Stop after the requested feature; do not start the next feature automatically.

## Engineering Rules

- Use standard OpenTelemetry APIs and semantic conventions before introducing a Lumens abstraction.
- Do not add vendor SDKs, vendor-prefixed attributes, credentials, customer data, or telemetry payloads to application code.
- Do not create a Lumens production Collector in the MVP.
- Preserve failure isolation: telemetry errors must not fail application work.
- Keep custom fields governed by the semantic contract and safe for privacy and cardinality.
- Use ASCII unless existing content requires otherwise.

## Verification

`scripts/verify.ps1` and `scripts/verify.sh` validate the MVP-F01 repository structure. They intentionally report that runtime, contract, and provider checks are deferred to later features.

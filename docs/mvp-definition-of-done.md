# MVP Definition Of Done

MVP-F10 completes the planned MVP hardening. The following are verified by `scripts/verify.ps1` or documented as credential-gated client checks:

- Java and Python packages build and their unit/integration tests pass.
- Contract generation is deterministic and current.
- Java and Python core operations preserve parentage, privacy, failure isolation, and independent metrics.
- Spring and FastAPI integrations provide standard automatic server instrumentation without Lumens route annotations or decorators.
- Business events are validated, correlated, and non-failing.
- Provider profiles are secret-free metadata and switching requires deployment configuration only.
- The cross-language normalized OTLP fixture has correct parentage and no duplicate server span.
- The MVP requires no Deloitte-managed production Collector.
- Future Collector, JavaScript/TypeScript, agent observability, and Experience Generator work remain excluded.

Residual deployment checks are provider endpoint, token scope, TLS, and live-ingestion compatibility. Those remain client-owned and are intentionally not encoded as repository secrets or required CI inputs.

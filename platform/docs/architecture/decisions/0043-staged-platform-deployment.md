# ADR-0043: Staged platform delivery on Netlify and Hetzner

**Status:** Proposed — implementation package prepared; target activation awaits approval
**Date:** 2026-09-27
**Scope:** Platform deployment, initial PtS/Scribeswell adopters

## Decision

Use app/service-owned release manifests and separate images, assembled by
platform/deployment. GitHub main deploys isolated staging; production is a manual
promotion of an exact SHA with successful staging evidence and immutable backend
image digests. Netlify hosts the combined static frontends; standalone file-driven
APISIX on Hetzner is the only public backend ingress. Supabase owns hosted database,
Auth and private Storage. Terraform manages host/firewall/public-key resources only.

Preserve migration authority under [ADR-0015](0015-alembic-migration-authority.md),
owner migration coordination under [ADR-0016](0016-owned-migration-histories-and-coordination.md),
and separated authority under [ADR-0017](0017-runtime-and-migration-database-authority.md).
Bootstrap identity/Bible schemas explicitly, record source fingerprints, and block
release when approved target evidence is missing or stale. Keep migrations before
activation and never auto-downgrade, following
[ADR-0020](0020-safe-schema-changes-and-release-recovery.md).

Use selected safe operational fields under
[ADR-0023](0023-structured-operational-logs-and-sensitive-data.md), bounded container
shutdown and truthful failure evidence under
[ADR-0027](0027-bounded-worker-shutdown-and-deployment-reporting.md).
No worker or queue deployment is authorized by this decision.

## Consequences

Separate staging incurs Supabase and host usage. One-host Compose activation is
not atomic/high-availability; failure requires reconciliation and compatibility
checks before restoring previous images. Public DNS, real TLS renewal, target
permission/isolation and recovery tests remain activation gates. Provider native
auto-deploy paths are disabled to preserve one authority. Sensitive configuration
stays outside source, images, frontend bundles, Terraform and CI artifacts.

Scaffold contract documented for the future builder; no working generator claimed.
Shared UI and agent-context change: none. Operational procedures and onboarding:
[platform deployment runbook](../../../deployment/README.md).

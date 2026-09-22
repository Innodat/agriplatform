# ADR-0027: Bounded Worker Shutdown and Deployment Reporting

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Recoverable durable workers and their deployment/monitoring tooling

## Decision

On shutdown, stop claiming new work and allow bounded time to finish in-flight work
and record confirmed completion. Coordinate the grace period with request timeouts,
claim durations and deployment termination settings. If the process does not exit,
the deployment supervisor may force termination without routine manual intervention.
Support may pause a rollout or extend the wait deliberately during investigation.
Exact bounds are owned implementation/operations configuration, not business settings.

Recovery must remain correct after abrupt termination: incomplete or uncertain work
remains durable, abandoned claims become recoverable and retries preserve stable
identity and receiver deduplication. Never mark work complete merely because shutdown
started. Do not depend on a final application log/cleanup callback executing after a
forced stop. Verify this recovery before relying on automatic force termination.

If the grace period is exceeded, emit a deployment-report warning and a searchable
structured operational event. The supervising deployment mechanism records forced
termination even when the worker cannot. Include service/instance, release/deployment
identity, configured grace period, observed shutdown outcome and available recovery
status without sensitive payloads.

Distinguish graceful exit, forced termination and replacement health/recovery status.
Report that processing resumed only when verified. If no work exists, report healthy
idle state; if recovery/progress is not established, say it is unconfirmed. A successful
replacement does not erase the forced-shutdown warning or historical evidence.

An isolated forced stop with verified healthy recovery does not require paging by
default. Repeated forced stops, unhealthy replacement or stalled eligible work require
attention through the existing monitoring rules. Set those thresholds before release.
MVP needs the report warning and structured event, not a dedicated dashboard panel or
new support screen. Keep technical notifications external to the application channel.

## Impact and verification

- Acceptance: graceful drain, timeout/forced stop, absent final worker log, crash after
  remote acceptance, replacement health, eligible-work progress, idle queue and truthful
  unconfirmed-recovery reporting; preserve business effects and duplicate safety.
- Scaffold/deployment: prove stop/drain/recovery hooks and supervisor report/log evidence
  in delivery; promote reusable behavior without a custom orchestration engine.
- Shared UI: deployment/operations reporting only; no employee or Leave Manager screen.
- Agent context: link bounded recoverable shutdown and truthful reporting in guidance.
- Documentation: builder, observability direction and Leave requirements/tracker updated.
- ADR: complements [0020](./0020-safe-schema-changes-and-release-recovery.md),
  [0023](./0023-structured-operational-logs-and-sensitive-data.md) and
  [0024](./0024-durable-delivery-retries-and-audited-recovery.md); originals unchanged.
- Planning only; no runtime shutdown, deployment configuration or monitoring changes.

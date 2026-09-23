# ADR-0119: Initial Production Backup and Recovery Targets

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Leave initial production/pilot operational readiness

## Decision

Adopt these initial Leave targets:

- Recovery point objective: at most one hour of data loss.
- Recovery time objective: essential service restored within four hours after the
  incident is declared. This measures restoration, not detection or a promise of
  round-the-clock staffing; support coverage remains an operational arrangement.
- Backup retention: thirty days.
- Restore rehearsal: before pilot, then quarterly and after major backup changes.

These are targets to demonstrate before pilot, not a claim that the selected hosting
plan or existing infrastructure meets them. Technical lead and operations owner must
select/configure sufficient mechanisms and verify cost/capability before release.
Do not equate an hourly scheduled backup with a proven one-hour recovery guarantee.
Measure the latest usable recovery point and exercise the complete restoration path.

Cover application records, required identity/access/configuration dependencies and
private document contents as well as their metadata/references. Restore a consistent
usable relationship between database records and files; separately successful backups
are insufficient if associated files cannot be recovered at the selected point. Supabase
database backups do not include Storage file contents; verify the actual Azure Blob/
Supabase Storage recovery mechanism for the deployed providers. Backup retention is
separate from business record, medical-document and outbox retention requirements.

During restoration keep notification workers/outbound effects paused until replay
safety is checked. Restoring older outbox or receiver deduplication state must not
blindly resend already accepted/delivered messages. Reconcile available producer,
receiver and provider evidence under existing operation/event identity rules; uncertain
items remain held for investigation. A database restore cannot reverse external email.

The rehearsal measures elapsed recovery time, verifies the recovery point and checks
representative sign-in/access, request/balance consistency, private-document access and
queue recovery before normal operation resumes. Preserve a concise result/report and
remediation actions. Failed objectives remain release-readiness issues, not passed by
changing a test expectation without an explicit target decision.

## Impact and verification

- Scaffold/operations: controlled recovery/runbook hooks and isolated rehearsal fixtures;
  no custom backup engine required. Shared dependencies participate through their owners.
- Shared UI: no additional business administration screen.
- Agent context: existing safe-release and evidence requirements suffice.
- Documentation: requirements target table and implementation tracker synchronized.
- ADR: applies [platform ADR-0020](../../../../../platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md)
  and existing idempotency/recovery rules; accepted predecessors unchanged.
- Planning only; no backup configured, restore performed or provider SLA claimed.

## Source

[Supabase database backup scope](https://supabase.com/docs/guides/platform/backups),
checked 23 September 2026: storage objects require separate protection.

# ADR-0061: KDG first committed operation wins

**Status:** Accepted

**Date:** 2026-10-22

**Scope:** KDG capture.create / capture.edit retry contracts only

**Partially supersedes:** [ADR-0012](0012-operation-identity-idempotency-and-tracing.md), changed-submitted-content rejection for these KDG commands only

## Context and authority

The user explicitly selected simpler first-commit-wins retries and instructed that
fingerprints and HMAC be left until needed. The current KDG MVP does not need to compare
repeated submitted content. Its former HMAC/JCS, secret-file and key-backup/restore
selections imposed a prerequisite that this decision defers. Child observations remain
sensitive business data; this choice does not waive privacy, current access or ordinary
business-data backup/recovery gates. Accepted ADR-0012 bytes remain unchanged.

## Decision

The server defines command type from the capture create/edit handler; an arbitrary
client action field never establishes command type or authority. Keep uniqueness on
`(org_id, executor_account_id, command_type, operation_id)`. Business changes, required
immutable evidence and the compact successful outcome commit atomically. Concurrent
duplicates cannot execute effects twice; failed/uncommitted actions have no success receipt.

For a committed duplicate under that exact key, return the original authorized receipt,
including its original target and revision, even when incoming content differs. Resolve
the stored target privately and recheck current permissions on the actual stored
resource/command before disclosing anything. Supplied target/action grants no authority.
Preserve strict input validation, supported command/receipt versions, structural scope,
revision/lifecycle checks for fresh execution and bounded busy/unresolved/denial behavior
without foreign-resource existence leaks. Do not compare payloads or require SHA/JCS
command digests, HMAC or fingerprint metadata for these current KDG commands.

New business actions or changed intended submitted input receive new operation IDs.
Clients freeze queued command input; a receipt confirms only that submitted snapshot,
never later edited content. Pending predecessors continue blocking later sends; unknown
outcomes never automatically create a new operation. No automatic outcome expiry or
deletion is introduced. The owning [KDG contracts](../../../../apps/kdg-capture/docs/contracts.md)
define the receipt and queue details; this is no central operation service.

Fingerprints, HMAC, fingerprint secret files and associated key backup/restore are
future opt-in work requiring a concrete need and an explicit adopting contract. There
is no automatic algorithm fallback. Leave, PtS, Identity and Access retain their choices;
operator commands and historical runtime/migrations/SQL/tests are not converted.

## Consequences and delivery impacts

- Scaffold: future consumers may opt in to a proven mechanism. Existing fingerprint,
  secret-file and WRITE candidates, tests, evidence and synthetic resources remain
  historical reusable work; they are not current KDG prerequisites or proof of this model.
- Shared UI: document frozen-snapshot receipt interpretation and pending-predecessor
  blocking; no component change or new setting.
- Agent context: unchanged; existing repository instructions suffice.
- Documentation: reconcile current KDG contracts/readiness/handoff and label earlier
  HMAC selections superseded; ordinary backup/recovery and child privacy gates remain.
- ADR: partially supersedes ADR-0012 only as scoped above; all accepted source ADRs
  and other application choices remain unchanged.

This is a documentation/decision change only. No runtime conversion, migration,
implementation, provisioning, deployment or cleanup is authorized or claimed. Later
consuming delivery must prove these semantics with acceptance failures first and actual
atomicity/authorization/queue/recovery evidence; historical candidate results do not do so.

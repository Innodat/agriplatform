# ADR-0001: Explicit observation Save without unfinished-entry recovery

**Status:** Proposed — user-directed scope change, 2026-10-13; final architecture/readiness review pending
**Scope:** KDG observation capture and editing only

## Decision

Use explicit whole-form Save observation for a new capture and Save/Cancel for existing
capture editing. Unfinished input stays in memory; no autosave, persisted unfinished
form, draft list, resume workflow or unfinished-form merge is required. Closing or
restarting before Save may lose typing. Do not intentionally crash to recover storage.

The user judges the redo cost of this four-question MVP too small to justify exposing
unfinished-entry recovery machinery. This is a product tradeoff, not a measured claim
about crash frequency. The earlier interruption-safe draft requirement and autosave
choice are superseded for KDG capture.

Completed captures still persist locally before success acknowledgement, survive normal
offline close/reopen and queue idempotent creates/edits for sync. Save failure, uncertain
outcomes, current authorization, account/org isolation, original questionnaire versions
and concurrent completed-record edits remain protected.

## Platform relationship

[ADR-0051](../../../../../platform/docs/architecture/decisions/0051-saving-conventions-by-workflow.md)
is not a universal draft requirement and allows documented workflow exceptions with
UX rationale and acceptance evidence. This records that application rationale; no
accepted platform ADR is edited or superseded. [ADR-0050](../../../../../platform/docs/architecture/decisions/0050-inline-draft-save-failure-and-exit-confirmation.md)
does not mandate a draft where none is needed. Explicit-Save forms retain their own
unsaved-edit and uncertain-command handling.

Online questionnaire configuration still has draft/published versions and explicit
Save/Cancel/Publish. That is unrelated to storing unfinished observation input.

## Impacts and evidence

- Requirements/UX/contracts: remove observation autosave/recovery and draft-specific
  feedback/exit flows; pin an in-memory entry's version until Save or abandonment.
- Stories/tests: rework 1.5 into explicit local Save plus atomic pending operation and
  local reopen. Prove answers, hidden-detail exclusion, multiple same-day captures,
  failed/uncertain Save, repeat-click safety and account scope. Before-Save crash/close
  recovery is intentionally not required.
- Scaffold/shared UI: promote proven explicit-form/local-save/status/error patterns;
  do not build local-draft engines for this consumer.
- Agent/docs: distinguish completed local captures from unsaved in-memory input;
  retain independent synchronization/conflict/release evidence.

Planning only; no implementation or runtime/device evidence is claimed.

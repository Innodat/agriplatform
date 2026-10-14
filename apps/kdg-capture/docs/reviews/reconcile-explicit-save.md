# Explicit-Save scope reconciliation

Date: 2026-10-13. BMAD PRD/UX input reconciliation of current PRD, EXPERIENCE,
ARCHITECTURE-SPINE, contracts, revised candidate 1.5, testing, epic scope amendment
and proposed application ADR-0001. Read-only except this report. No runtime/code/test
review or evidence requirement is introduced.

## Verdict

The user-directed change is consistently represented in the main requirements, UX,
architecture, revised story and acceptance plan: unfinished observation input stays in
memory; only explicit Save creates durable capture plus pending operation. A stale
update instruction found during the initial read was corrected concurrently and the
final source recheck confirms the boundary is now explicit.

Open material findings: 0 critical, 0 high, 0 medium, 0 low.

## Concurrent correction verified

The initial contracts read contained “persist form state” before shell activation.
Final recheck of `contracts.md:247–249` instead defers activation until open input is
explicitly saved or deliberately abandoned and prohibits unfinished-form checkpoints.
Acknowledged captures, pending operations and unresolved outcomes remain independent
durable data. This closes the sole material contradiction identified during this pass.

## Confirmed closure

- PRD FR-7, glossary and revised A-4 remove observation autosave, resume and unfinished-
  entry durability promises. EXPERIENCE explicitly explains pre-Save closure/restart
  loss and ordinary app-controlled unsaved-change handling; no draft flush is required.
- Architecture AD-4 and candidate 1.5 require explicit atomic local capture/queue commit,
  no successful-save feedback before commit, local details/reopen, multiple same-day
  captures, original attempted IDs on uncertainty and repeat-click safety.
- Conditional detail buffers remain temporary in-memory editing aids; Nee excludes
  them from completed active answers. An open entry pins its questionnaire version
  without making that entry a persisted draft.
- Offline saved captures, queued creates/edits, account/Khula partitioning, seven-day
  local authority, current server checks, original author/version, ordered retries,
  revision conflicts and retained completed-record proposals remain protected.
- Questionnaire administrator **draft/published versions remain** in PRD FR-10/11,
  EXPERIENCE administration flow, persistence contracts, E4 and ADR-0001. Removing
  unfinished observation recovery does not remove saved questionnaire drafts.
- Testing A07/A08/A17 and the scope amendment remove unfinished-entry/flush/merge
  assertions while keeping explicit failed/uncertain Save, completed capture durability,
  update compatibility and questionnaire version checks.
- The former recoverable-input candidate is clearly withdrawn/superseded. Approved
  stories 1.1–1.4 retain historical text; the explicit epic amendment supersedes their
  future-draft references. They do not require rewriting to preserve approval history.
- Revised 1.5 and proposed ADR-0001 correctly remain awaiting normal review. Scope
  simplification does not imply implementation authorization or completed readiness.

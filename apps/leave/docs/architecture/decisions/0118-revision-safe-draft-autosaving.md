# ADR-0118: Revision-Safe Draft Autosaving

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** One employee draft per NGO across tabs/devices

## Decision

Apply platform ADR-0013 explicit revision checks to draft autosaves. Each save submits
the revision it started from; the backend atomically rejects a stale save if another
writer has advanced that revision. Do not silently fetch a new revision and overwrite
someone else's saved values. Existing same-user/NGO authorization remains required.

On conflict, pause autosaving in that tab and show **This draft changed elsewhere.
Your latest changes haven’t been saved.** Offer **Review saved draft** after checking
current access. Preserve unsaved local edits while the user decides what to keep;
do not promise those edits survive tab closure unless a separately supported recovery
mechanism provides it. No automatic merge or collaborative editor is required for MVP.

Serialize saves within each tab. While a save is in flight, retain subsequent typing
and send the next coalesced save with the acknowledged revision after success. Do not
let a late response replace newer local input or show the entire form as saved when
only an older edit was acknowledged. The existing uncertain-operation identity and
retry contract applies; do not start a competing fresh save before resolving an
uncertain preceding save.

Retain one draft per employee/NGO and existing no-reservation-before-submission rules.
The draft remains an autosaved form, not a consequential approval review. Explicit
conflict handling protects edits without adding a Save button or mandatory review
screen for ordinary uncontested typing.

## Impact and verification

- Acceptance: conflicting tabs/devices cannot overwrite newer saved values; pause and
  review path retain local input; serialized same-tab saves preserve newer typing;
  honest saved indicator; uncertain retry duplicate-safe; current access checks.
- Scaffold/shared UI: generic autosave revision/conflict behavior can be promoted when
  proven; Leave owns draft lifecycle and fields. Reuse existing review/error primitives.
- Agent context: existing revision/idempotency guidance suffices.
- Documentation: requirements, shared/Leave UX and implementation tracker synchronized.
- ADR: applies [platform ADR-0013](../../../../../platform/docs/architecture/decisions/0013-explicit-revisions-for-reviewed-changes.md);
  accepted predecessors unchanged.
- Planning only; no autosave code, UI behavior or database schema implemented.

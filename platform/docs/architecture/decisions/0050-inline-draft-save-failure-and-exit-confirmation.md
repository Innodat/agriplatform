# ADR-0050: Inline Draft Save Failure and Exit Confirmation

**Status:** Accepted  
**Date:** 2026-10-05  
**Supersedes in part:** [ADR-0048](./0048-simple-draft-save-failure-navigation.md), failure presentation only.

## Decision

For non-consequential autosaved drafts, keep editing uninterrupted. After bounded
background recovery fails to confirm saving, show an inline Changes not saved status
with Retry. This means saving is not confirmed, not proof of rollback. Users can keep
typing without a separate Keep editing action. Retry obeys existing operation/revision
rules; new typing does not authorize a competing write while an earlier one is unresolved.

Close immediately if current input is acknowledged. Otherwise flush/wait through the
existing bounded save/recovery flow. If saving still cannot be confirmed on exit, ask
Your latest changes may not be saved. Close anyway? Offer Stay and Close anyway.
Organization switching uses the equivalent Stay / Switch anyway. No three-choice dialog
while editing, extra technical explanation or endless wait. Leaving does not delete the
saved draft, undo an in-flight commit or guarantee preservation of unsent local input.
Reopen current authorized saved state. Do not call a confirmed save failure Saved.

Authorization, operation identity, revision/lifecycle protection and consequential-action
confirmation remain unchanged. This selects UX, not a universal requirement for drafts
or a shared draft table. Applications still determine where unfinished input is useful.

## Impacts and verification

Prove inline failure/Retry while typing, confirmed saved close without prompt, pending
flush, failed/unknown exit with Stay/Close anyway, context switching, lost response after
commit, late response isolation and accessible focus/status. Promote proven shared UI
and scaffold fixtures with the first consumer. Update experience, stories and agent
links; retain application-owned lifecycle. Accepted predecessors remain immutable.
Planning only; implementation and readiness evidence are still required.

# ADR-0075: Single Employee Application Draft and Safe Closing

**Status:** Accepted  
**Date:** 2026-09-15  
**Scope:** Employee application draft cardinality and closing behavior

## Decision

Keep one unfinished employee application draft per employee per NGO. Apply for
leave resumes it, with a small unfinished-application note beside the action.
No Drafts section or notification badge is needed. Discard draft within the form
requires confirmation. Submitted requests remain independent and may be multiple.

Use Close instead of Save and close. Close, desktop Escape, and mobile Back close
immediately when saved; finish an in-progress save before closing. On failure,
offer Retry, Keep editing, or Discard unsaved changes, retaining previously saved
content. Confirm before discarding an approver's unsent comment.

This partially supersedes [ADR-0067](./0067-automatic-draft-saving.md) for the
closing label and refines draft cardinality. Its truthful autosave, no-reservation,
NGO isolation, and submission revalidation requirements remain in force, as does
its linked platform API boundary decision.

## Consequences

- Scaffold impact: no change now; generic save/close handling may be reused when proven.
- Shared-UI impact: Leave owns draft cardinality; shared controls may support closing safeguards.
- Agent-context impact: existing instructions suffice.
- Documentation impact: synchronize product specification, tracker, UX draft, and decision log.
- ADR impact: partial supersession above; accepted historical ADR text is unchanged.
- Planning only; implementation and acceptance checks follow Phase 1 readiness.

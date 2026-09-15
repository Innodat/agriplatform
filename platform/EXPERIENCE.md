---
name: Agriplatform Shared Experience
status: draft
created: 2026-09-15
updated: 2026-09-15
sources:
  - docs/architecture/decisions/README.md
---

## Foundation

Shared experience conventions for application silos, with visual treatment in
[DESIGN.md](./DESIGN.md). This is an initial draft, not a complete platform UX
contract. Shared shell and drawer implementations remain to be proven during
delivery; existing application boundaries and authorization rules still apply.

## Component Patterns

### Contextual create/edit surfaces

Prefer a right-side drawer for focused create/edit tasks that benefit from keeping
the underlying page in context. On mobile or whenever the content would be cramped,
use a full page. Retain the same form, validation, and persistence semantics across
presentations. Long, complex, or multi-step workflows may use dedicated pages on
desktop too. Short confirmations use dialogs.

Keep decision-critical information inside the active form. The background must not
be necessary to understand or complete it.

## Interaction Primitives

### Shared uploads

Use a reusable upload component composed from platform UI primitives. On desktop,
offer Drag and drop a file, or browse, with Browse as a real keyboard-accessible
button. On mobile, use Choose a file. Provide accessible progress, errors, and
translatable labels. Applications supply allowed types, limits, required/optional
status, and domain authorization; this component does not grant access or bypass
server validation. Implement and prove it through Leave before promotion into
shared UI; existing apps adopt it explicitly. It is not a global mutation of
third-party shadcn controls.

### Closing autosaved forms

For an autosaved draft, label the closing action Close with Draft saved nearby
after persistence succeeds. Avoid Cancel where it could imply deletion or a
domain cancellation. Wait for outstanding saves; failed saves offer retry, stay,
or explicit discard of unsaved changes. Preserve the last persisted draft.

- Keep keyboard focus within an open modal drawer and its background inactive;
  return focus to the invoking control when closing back into the same page.
- Provide an explicit close action. Backdrop clicks do not dismiss task drawers.
- Route close/navigation attempts through the application's save and unsaved-change
  rules. Exact Escape/back navigation behavior must be specified and tested before
  the shared interaction contract is finalized.
- Give drafts stable URLs for direct access and resumption, with current permission
  checks. Direct navigation must have a meaningful return destination even when no
  underlying page was opened first.
- Domain-specific discard, acknowledgement, and approval rules remain owned by the
  application; opening or closing a drawer does not complete those actions.

## Accessibility Floor

Verify keyboard access, focus containment and restoration, accessible naming,
readable content at zoom, and announced validation states in the assembled control.
Full-page mobile presentation must preserve equivalent functionality.

## Responsive & Platform

The desktop drawer/mobile full-page preference is a shared design direction accepted
through the Leave design discussion. Exact breakpoints and drawer dimensions remain
open. Validate the pattern with Leave before promoting its implementation into
shared UI or builder templates. This draft introduces no runtime dependencies.

---
name: Agriplatform Shared Experience
status: draft
created: 2026-09-15
updated: 2026-09-16
sources:
  - docs/architecture/decisions/README.md
---

## Foundation

Shared experience conventions for application silos, with visual treatment in
[DESIGN.md](./DESIGN.md). This is an initial draft, not a complete platform UX
contract. Shared shell and drawer implementations remain to be proven during
delivery; existing application boundaries and authorization rules still apply.

## Component Patterns

### Roles and permissions

Include application-role assignment in Organization Administrator by default,
limited to the active NGO. Advanced custom roles may delegate administration for
specific applications. Application management roles do not automatically grant
general role-administration powers. A domain-specific temporary assignment may
grant its own bounded authority under the application's explicit rules; it is not
general role editing.

Use one shared access-management screen, such as People → person → Application
access, for authorized role assignment across enabled applications within the active
NGO. Application settings link to the relevant section. Share role pickers,
capability summaries, and custom-role editors rather than generating separate
editor implementations into each application. Scaffolding registers the application
catalog and connects shared controls when available.

Combine assigned-role grants within the active NGO, while preserving grant scope
and application-specific constraints. Omitting a capability from one custom role
does not negate a grant from another role. Show combined access clearly. Approval
assignment, self-approval restrictions, and separate sensitive-document checks still
apply. No role switching is required to use a person's combined access.

The shared platform owns assignment/custom-role administration and access-change
audit. Applications own business permission/default-role definitions and enforce
resource-level authorization in their APIs. Shared runtime capabilities use HTTP
contracts under the existing silo architecture; these components are not yet built.

In normal access setup, show role names with short descriptions and an expandable
What this role allows summary. Keep technical permission codes out of that flow.
Put Create custom role under advanced settings and label capabilities in plain
business language, such as Adjust employee balances.

Offer application-defined roles as the normal setup path. Keep individual business
permissions explicit underneath, with custom roles available as an advanced option.
Custom roles may start as copies; do not silently add future permissions to them.
Applications maintain their default definitions. Production access changes require
authorization regardless of who designed the role. Follow
[ADR-0011](./docs/architecture/decisions/0011-application-roles-and-business-permissions.md).

### Organizational directory — post-MVP direction

A future shared directory capability may populate reporting relationships from
Microsoft Graph for use by Leave, Travel, and other applications. Keep this separate
from calendar synchronization and existing Entra sign-in. Applications retain
ownership of approval policies; the directory supplies supervisor relationships.
Leave maintains supervisor assignments manually for MVP.

Preserve authorized overrides and expose missing or invalid manager assignments
for resolution. Imported relationships do not independently grant NGO membership
or approval eligibility. Do not silently reroute requests already awaiting approval.
Specific synchronization, tenant mapping, permissions, and conflict-resolution
contracts remain for later architecture work. Reference:
[Microsoft Graph manager relationship](https://learn.microsoft.com/en-us/graph/api/user-list-manager?view=graph-rest-1.0).

Impact: shared platform planning only; no directory runtime, scaffold, shared-UI,
or agent-context change now. No accepted ADR is superseded. Record architecture
decisions and HTTP contracts before delivering this capability.

### Collection views and filters

Use a shared responsive pattern for list, table, calendar, and timeline screens
that need multiple filters. On desktop, place view toggles beside the page heading,
aligned right. Group the compact toolbar by purpose: time navigation where relevant,
data attributes/search, and visibility modifiers/reset. Use available width before
wrapping groups; omit groups the application does not need. Keep legends beside the
data, outside the primary control sequence.

On mobile, keep essential navigation visible and open additional filters in a modal
bottom sheet. Initialize its provisional values from the applied filters. Apply
filters commits those values and closes the sheet. Close, Back, or any supported
dismissal discards unapplied edits. Reset filters restores application defaults
within the provisional selection; it takes effect only on Apply. Keep the heading,
close/reset controls, and Apply action reachable while the sheet body scrolls;
allow near-full-height presentation for keyboards, zoom, or longer forms.

The external Filters badge counts filter groups whose applied values differ from
their defaults, not individual selected options or matching records. Omit a zero
count. The Apply filters button has no count. Use accessible named controls,
focus containment, an inactive background, and focus restoration on close.

Applications supply filter fields, defaults, group definitions, permitted options,
query behavior, and domain labels. Shared controls do not own authorization or
business data. These conventions apply where filtering complexity warrants them;
simple screens need not acquire extra controls or a sheet.

Delivery impact: implement and validate reusable composition through Leave, then
promote domain-neutral toolbar, view-toggle, and filter-sheet controls into shared
UI. Update builder guidance/examples when those controls exist. This planning
change adds no runtime dependency, changes no agent instructions, and supersedes
no accepted ADR; architecture/contracts remain subject to delivery planning.

### Personal task inbox — deferred direction

A future shared personal inbox brings together actions assigned to a person across
applications. Each application owns its workflow and authoritative task state;
the inbox links to the source application to act. Show action, application, NGO,
and due date when applicable. Shared statuses are Needs action, Completed, and
No longer required; application-specific request statuses remain separate.
Completing one approval task does not imply the whole request is approved.

Notifications remain separate: reading a notification does not complete a task.
Current authorization and NGO boundaries apply to task visibility and linked actions.
Defer implementation until a second application needs this capability. Leave's
pending actions should support later integration, without a generic task engine
or extra inbox screen in its MVP. API contracts, synchronization, and architecture
remain to be designed at that point; this is a UX direction, not a runtime contract.

Impact: documentation direction only; no scaffold or shared-UI implementation now,
no agent-context change, and no accepted ADR superseded. Evaluate architecture and
record an ADR when the capability moves into delivery scope.

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

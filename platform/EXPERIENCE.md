---
name: Agriplatform Shared Experience
status: draft
created: 2026-09-15
updated: 2026-09-20
sources:
  - docs/architecture/decisions/README.md
---

## Foundation

Shared experience conventions for application silos, with visual treatment in
[DESIGN.md](./DESIGN.md). This is an initial draft, not a complete platform UX
contract. Shared shell and drawer implementations remain to be proven during
delivery; existing application boundaries and authorization rules still apply.

## Information Architecture

| Shared surface | Entry | Responsibility |
|---|---|---|
| Application access | Organization settings → People → person; application deep link | Assign roles for enabled applications within the active NGO |
| Custom roles | Application access → Advanced role settings | Create, duplicate, review, edit, and remove application-specific roles |
| Related person access | Role-holder link | Resolve an assignment and return to the originating role editor |
| Contextual drawer/full page | Application-owned record or create action | Host a focused task while preserving navigation context |
| Notification panel | Shared shell bell | Show permitted active-NGO notifications and link to application-owned records |
| Filter sheet | Collection-view Filters control on mobile | Stage filters and apply or discard the provisional selection |

Applications own their domain navigation and records. Shared role controls do not
create approval-step assignments or bypass domain checks. Planned cross-application
tasks and directory synchronization are listed separately under Deferred Capabilities.

## Voice and Tone

Use familiar business names in ordinary setup: Approver, What this role allows,
Review access changes. Keep technical permission identifiers out of the normal
flow. Use Close for leaving a saved draft, Reset filters for defaults, and Apply
filters for applying provisional choices. Describe actual consequences instead of
repeating explanatory summaries on every form. Specific application wording remains
in its experience contract.

## Component Patterns

### Notification panel

The shell bell opens a compact desktop panel, newest first. Use a full-width
sheet on mobile with the same content. Rows show a clear unread marker, a short
event/status title, permitted record context, and a secondary time. Provide Mark
all as read for the active NGO only. The empty state says No notifications yet.

Applications supply permitted event content and authorized destinations through
the planned shared notification contract. Selecting an item opens its destination
subject to current authorization; reading or marking it read never completes an
outstanding business action. Retain per-user read state and existing NGO count
privacy. Keep sensitive record content inside its authorized application view.
Leave's exact notification-content restrictions remain in its product contract.

Reuse shared modal focus, close and return behavior on mobile. A load failure is
not an empty inbox; retain the shared loading/error conventions. This is approved
UX direction, not an implemented shared control or finalized runtime API.

Impact: shared shell guidance and Leave references updated; scaffold integration,
shared-UI implementation and service contracts remain delivery work. No agent-context
change or accepted ADR replacement is needed for this layout refinement.

### Roles and permissions

Offer application-defined roles as the normal setup path. Keep individual business
permissions explicit underneath, with custom roles available as an advanced option.
Custom roles may start as copies; do not silently add future permissions to them.
Applications maintain their default definitions. Production access changes require
authorization regardless of who designed the role. Follow
[ADR-0011](./docs/architecture/decisions/0011-application-roles-and-business-permissions.md).

In normal access setup, show role names with short descriptions and an expandable
What this role allows summary. Keep technical permission codes out of that flow.
Put Create custom role under advanced settings and label capabilities in plain
business language, such as Adjust employee balances.

Use one shared access-management screen, such as People → person → Application
access, for authorized role assignment across enabled applications within the active
NGO. Application settings link to the relevant section. Share role pickers,
capability summaries, and custom-role editors rather than generating separate
editor implementations into each application. Scaffolding registers the application
catalog and connects shared controls when available.

The shared platform owns assignment/custom-role administration and access-change
audit. Applications own business permission/default-role definitions and enforce
resource-level authorization in their APIs. Shared runtime capabilities use HTTP
contracts under the existing silo architecture; these components are not yet built.

Include application-role assignment in Organization Administrator by default,
limited to the active NGO. Advanced custom roles may delegate administration for
specific applications. Application management roles do not automatically grant
general role-administration powers. A domain-specific temporary assignment may
grant its own bounded authority under the application's explicit rules; it is not
general role editing.

Each custom role belongs to one application; an application may have multiple
custom roles, and a person may hold multiple roles across applications within the
authorized NGO. Inherit application context from the access/settings section where
Create custom role is opened. Start with name, description, and unselected business
capabilities; do not require a Start from/template selector. Offer Duplicate role
on an existing role to prefill the same editor with a copy. Custom copies remain
independent. Defer cross-application role bundles until demonstrated need.

Combine assigned-role grants within the active NGO, while preserving grant scope
and application-specific constraints. Omitting a capability from one custom role
does not negate a grant from another role. Show combined access clearly. Approval
assignment, self-approval restrictions, and separate sensitive-document checks still
apply. No role switching is required to use a person's combined access.

Before confirming edits to an assigned custom role, show added/removed capabilities
and the number of people holding the role, with names expandable within authorized
scope. State that changes apply to all its holders. Explain that removing a grant
does not remove equivalent access provided by another role or valid temporary
assignment. Require review before confirmation and retain access-change audit.

Allow deletion of custom roles only when no people hold them. Otherwise, show the
holders as links to their application-access screen with the relevant application
selected. Return to the role editor through a visible Back to [role name] link or
browser Back, preserving draft and position through shared save/leave safeguards.
Refresh holders and deletion eligibility on return. Confirm deletion separately
after assignments are removed; retain historical definitions and audit records.
Application-defined roles are application-maintained and not deletable here.

The approved [Leave role-lifecycle study](../_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/mockups/custom-role-lifecycle-preview.html)
illustrates this shared composition with a partial capability catalogue. It does
not implement effective-access checks, assignment editing or deletion.

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


### Date inputs

Use a unified date-range control where the task needs a range, with calendar
selection and typed/keyboard entry. A one-day range uses the same start and end.
Allow incomplete entry while the person is still entering the value before showing
an error. Explain an end date before the start beside the control; never silently
swap dates. Calculate dependent values only once required inputs are valid; do not
represent incomplete input as a zero result. Applications supply date eligibility,
schedule, holiday, duration and other domain validation.

### Contextual create/edit surfaces

Prefer a right-side drawer for focused create/edit tasks that benefit from keeping
the underlying page in context. On mobile or whenever the content would be cramped,
use a full page. Retain the same form, validation, and persistence semantics across
presentations. Long, complex, or multi-step workflows may use dedicated pages on
desktop too. Short confirmations use dialogs.

Keep decision-critical information inside the active form. The background must not
be necessary to understand or complete it.

## State Patterns

| Context | Treatment |
|---|---|
| Filter sheet open | Provisional selection; Apply commits, dismissal discards unapplied edits |
| Save pending/failed | Wait for persistence on close; offer retry, stay, or explicit unsaved discard on failure |
| Related-record return | Restore originating context and refresh dependent counts/eligibility |
| Access revoked | Recheck current permissions and suppress inaccessible retained data |
| Role has assignees | Show authorized holder links and prevent deletion until assignments are removed |
| Additional role still grants access | Explain effective access rather than claiming a removed grant removed all access |
| New custom role | Empty name/description/capability form; duplication is a separate entry action |

### Collections, refresh and export

- While loading, show a quiet loading indicator; do not prematurely display an
  empty result. Distinguish successfully loaded empty data from no filter matches.
- For no filter matches, explain that no results match and offer Clear filters.
  Applications provide domain-specific factual empty-state wording.
- For failed loading, explain the failure and offer Retry, preserving filters.
  A failed fetch must never appear as an empty successful result.
- If refresh fails, retain previously loaded data only while access remains valid;
  clearly mark that it could not be refreshed and revalidate before accepting an
  action. Suppress protected data when access is lost.
- In a multi-section page, keep independently loaded authorized sections usable
  when another section fails. Retry the affected section without clearing other
  results or resetting their context. Respect actual data dependencies; a failed
  overview panel does not itself block a form whose required checks succeed.
- If export fails, keep the report visible and show Retry export.
- A failed supporting panel explains that its data could not be loaded. It does
  not independently block the main action unless an existing domain rule requires
  that information.

Applications supply wording, permissions, data dependencies and action restrictions.
These are shared presentation requirements, not claims of implemented controls.

## Interaction Primitives

### Return to origin

When opening a related record to resolve an issue, preserve the originating view's
draft, filters, and position where applicable. Provide an explicit contextual Back
link and coherent browser Back behavior. Route navigation through existing save
and unsaved-change safeguards, then refresh relevant dependencies on return.
Direct links without an origin need a sensible default destination. Recheck current
permissions; retained navigation state must not expose revoked data.

### Shared uploads

Use a reusable upload component composed from platform UI primitives. On desktop,
offer Drag and drop a file, or browse, with Browse as a real keyboard-accessible
button. On mobile, use Choose a file. Provide accessible progress, errors, and
translatable labels. Applications supply allowed types, limits, required/optional
status, and domain authorization; this component does not grant access or bypass
server validation. Implement and prove it through Leave before promotion into
shared UI; existing apps adopt it explicitly. It is not a global mutation of
third-party shadcn controls.

Show per-file state beside the upload field: Uploading… with Cancel; Couldn’t
upload this file with Retry and Remove; and Attached with Remove only once the
file is stored, associated with the record/draft, and any required checks finish.
Keep unrelated entered form data when an upload fails. Show rejected file types
or sizes beside the file with the actual application-supplied limits. Cancelling
an upload does not cancel the surrounding form.

Explain missing or unfinished required-document blockers beside the field. For an
optional failed attachment, require retry or explicit removal before submission;
do not silently omit a file the user intended to include. Pending uploads must
finish or be explicitly cancelled/removed before submission proceeds. Preserve
existing attachment authorization and retention rules. This interaction adds no
new malware-scanning requirement.

### Administrative edits with explicit confirmation

Administrative forms apply changes only after explicit confirmation. Where review
is required, use Edit → Review → Confirm; reviewing input does not publish policy,
post a balance adjustment, or grant access. Keep unconfirmed values while the form
is open; MVP does not require a separate administrative saved-drafts system.

Leaving a changed form asks **Discard these changes?**, with **Keep editing** and
**Discard changes**. Following a supported related-record link preserves the
unfinished form for the agreed return-to-origin journey. This does not promise
recovery after browser closure or refresh. Employee autosaved drafts retain their
separate persistence contract.

A failed confirmation retains input and explains the failure. If the result is
uncertain, check whether the change succeeded before retrying. If another actor
changed the underlying record, refresh the affected information and require a new
review before confirmation; never silently overwrite that change.

### A record changes during review

Reject stale actions rather than silently applying them to changed records.
After rechecking authorization, show the current state and only the actions that
remain valid. When another person edited the record, offer Review latest version
and require a fresh review before the user decides. Retain typed comments without
submitting them automatically. When the action is no longer needed, explain why
and offer a return to the originating queue; an unsent comment may remain locally
available to copy while the view stays open. Do not promise saved persistence for
that comment. Access loss follows the no-access treatment without exposing fresh
record details. Applications supply lifecycle wording and valid actions.

### Closing autosaved forms

Use a familiar close icon in the drawer header with an accessible Close name;
retain Close for the footer action when present. Both routes use the same save
and unsaved-change safeguards. Do not relabel Close as Cancel unless the actual
behavior discards changes and that meaning is intended.

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

- After confirmed submission replaces a form with its result, focus the result
  heading. On full-page task entry, focus its heading to establish context.
- When switching between a modal drawer and a full page, preserve entered values
  and the active field where it survives; otherwise focus the task heading. Focus
  trapping and inactive-background behavior apply only while the surface is modal.
- When validation blocks an action, retain input and guide focus to the error.
  Explain field errors beside and programmatically associated with their controls;
  use a linked error summary for multiple errors or the invalid field for one.
- Announce consequential changes such as save failure/recovery, completed actions,
  changed displayed periods, and newly required responses without unsolicited focus
  movement. Avoid announcing every keystroke or routine autosave. Result-heading
  focus can communicate completion without a duplicate announcement.
- Calendar/date controls expose the selected date both visually and to assistive
  technology; preserve useful return focus from detail content.

Applications supply domain wording, including Leave’s unpaid-amount response.
Verify these behaviors in assembled screens; written rules do not establish
browser or assistive-technology compliance.

## Key Flows

These are named walkthrough examples drawn from the accepted Leave discussion;
they are not new platform business roles or independently researched personas.

### Manage Ana’s application access

1. An authorized organization administrator opens Ana’s Application access in the active NGO.
2. They choose Leave roles and expand What this role allows when needed.
3. They review added/removed grants and the combined-access implications.
4. **Decision point:** they confirm the reviewed access change, which is audited.
5. If permissions or relevant data changed, refresh and re-evaluate rather than claiming an outdated change succeeded.

### Remove a custom role held by João

1. An authorized administrator opens the role and sees that João still holds it.
2. They follow João’s link to the appropriate application-access section, observing save/leave safeguards.
3. They remove or replace his assignment, then use Back to the originating role.
4. **Decision point:** the refreshed holder list determines whether deletion can proceed.
5. Confirm deletion separately; retain historical definitions and audit records. Revoked access or a remaining assignee prevents the corresponding action.

### Change mobile filters in Ana’s leave overview

1. A manager opens Filters from the collection view.
2. They change provisional values or reset to the application defaults.
3. **Decision point:** Apply filters commits and closes; Close or Back discards those edits.
4. The result view uses the applied values and counts changed groups in the badge.
5. An unavailable option must not be exposed through restored state; the application rechecks scope.

## Responsive & Platform

The desktop drawer/mobile full-page preference is a shared design direction accepted
through the Leave design discussion. The standard drawer width and spacing are
selected in DESIGN.md; content-driven breakpoints and additional variants remain
subject to rendered validation. Validate the pattern with Leave before promoting its implementation into
shared UI or builder templates. This draft introduces no runtime dependencies.

## Deferred Capabilities

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

## Open Implementation Details

These drafts describe accepted behavior, not implemented controls. Final theme
values, responsive thresholds, implementation of administrative persistence rules, direct-link
return fallbacks, API contracts, and role-administration limits need resolution
before their delivery items. Prototype markup and static examples do not establish
those contracts or demonstrate accessibility compliance.

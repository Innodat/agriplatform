---
name: Leave
description: Responsive Leave experience draft distilled from approved coaching decisions.
title: Leave Experience Design
status: draft
created: 2026-09-15
updated: 2026-09-20
sources:
  - ../../../../platform/EXPERIENCE.md
  - ../../../../apps/leave/docs/features.md
  - ../../../../apps/leave/docs/architecture/decisions/README.md
  - ../../../../apps/leave/docs/operations/migration-runbook.md
---

## Foundation

Responsive web for desktop and phones. [DESIGN.md](./DESIGN.md) owns visual identity;
[platform EXPERIENCE.md](../../../../platform/EXPERIENCE.md) supplies shared interaction
conventions, still in draft. No specific component library or implemented shared
shell is selected by this document. Leave owns its rules, calculations, permissions,
and workflows in the [feature specification](../../../../apps/leave/docs/features.md)
and linked accepted ADRs. This is a reviewable consolidation, not implementation
readiness or a completed accessibility assessment.

The paired spines take precedence over illustrative mocks for presentation;
authoritative product requirements and accepted superseding ADRs govern business
behavior. Unresolved source differences are listed in
[consolidation coverage](./consolidation-coverage.md), not silently decided here.

Everyone starts on My Leave. Show Approvals and Manage Leave according to current
permissions, in the same active NGO and session. Section badges count unresolved
work separately from unread notifications. Shared identity, NGO switching, language,
application access, and return-to-origin navigation remain platform-owned.

## Information Architecture

This table maps accepted needs to destinations; “partial” means the reference does
not cover every state or field. It does not grant the actor access to that surface.
Flow numbers refer to Key Flows below. Documentation-only and unresolved surfaces
are explicit rather than new screens inferred from the feature catalogue.

| Surface | Entry and purpose | Flow | Layout reference / coverage |
|---|---|---|---|
| My Leave and balance explanations | Default home; apply, available/reserved balances, pending responses, upcoming leave, history; request-date projection in Apply | 1, 2, 4 | [Apply background](./.working/apply-wireframe.html), partial; ledger composition open |
| Apply for leave / resume draft | My Leave action; one saved application per employee/NGO | 1 | [Apply](./.working/apply-wireframe.html), funded and shortfall layouts |
| Request details and lifecycle actions | Submission, own history, notification, overview | 2, 4 | [History](./.working/employee-history-wireframe.html) and [correction](./.working/leave-correction-wireframe.html), partial; acknowledgement/withdraw/cancel states specified below |
| My leave history | My Leave; Calendar/List and bounded year navigation | 2 | [Employee history](./.working/employee-history-wireframe.html); list filters not implemented in mock |
| Approvals and request review | Authorized section; assigned ordinary and temporary work | 3 | [Approval review](./.working/approval-review-wireframe.html), queue/filter coverage partial |
| Team availability | Inside approval review; permitted colleagues during requested dates | 3 | [Approval review](./.working/approval-review-wireframe.html), desktop timeline/mobile list |
| Manage Leave home | Authorized section; attention queues and grouped tools | 5 | [Manager home](./.working/leave-manager-home-wireframe.html) |
| Organization overview | Manage Leave heading action; scoped staffing view and request drilldown | 6 | [Organization overview](./.working/organization-overview-wireframe.html) |
| Escalation, deficit, affected-request and balance-override review | Attention item or authorized request action | 3, 5 | [Manager home](./.working/leave-manager-home-wireframe.html) entry previews; dedicated review layouts open |
| Administrative leave correction / apply on behalf | Authorized employee actions | 4 | [Returned-early correction](./.working/leave-correction-wireframe.html); on-behalf entry not separately visualized |
| Temporary approver assignment, review and termination | Authorized management action / coverage issue | 7 | [Temporary approver](./.working/temporary-approver-wireframe.html); end/conflict/expiry states spine-only |
| Leave types; current/scheduled/past policy; editor and publication review | Configuration | 8 | [Policy summary/review](./.working/policy-review-wireframe.html), [approval section](./.working/approval-workflow-wireframe.html); complete editor open |
| One-off adjustment and adjustment details | Employee actions or authorized notification link | 9 | [Balance adjustment](./.working/balance-adjustment-wireframe.html) |
| Employee recurring entitlement | Configuration → employee/type | 10 | [Employee entitlement](./.working/employee-entitlement-wireframe.html) |
| Work profiles and employee schedule | Configuration / setup | 11 | [Employee schedule](./.working/employee-schedule-wireframe.html); profile list/editor partial |
| Holiday calendars | Configuration / setup; calendar/date review | 11 | [Holiday calendars](./.working/holiday-calendars-wireframe.html) |
| Reports | Records; report selection, authorized results/export | 12 | [Reports](./.working/reports-wireframe.html), balance report example |
| Audit history | Records; filtered chronological changes and details | 13 | [Audit history](./.working/audit-history-wireframe.html) |
| Notification inbox | Shared shell bell; read state and authorized deep links | 4, 14 | Spine-only shared pattern |
| Setup checklist, organization/employment/supervisor maintenance, manual opening balances | Authorized setup/settings; no assumption of imported employees | 15 | Checklist behavior below; complete organization/employee forms remain open |
| Consultant migration and client email approval | Consultant tooling and email, not an application confirmation screen | 15 | [Migration runbook](../../../../apps/leave/docs/operations/migration-runbook.md); documentation-only |
| Application access and advanced custom roles | Shared organization settings | 16 | [Application access](./.working/application-access-wireframe.html), [custom role](./.working/custom-role-wireframe.html); editing/deletion review states spine-only |
| Sign-in, active NGO and language | Shared shell / account | 14 | Shared spine; dedicated visual coverage open |

## Voice and Tone

Use factual, friendly, plain language and explicit consequences. Say “Requested
unpaid” until the relevant decision; acknowledgement is not approval. Say
“Temporary approver”, “Acting for … until …”, and “Not required under absence policy”
where applicable. Avoid technical permission codes in ordinary access settings.
Keep “Review change” for opening a review and use the explicit confirmation verb
for the actual operation. Routine inherited information is quiet helper text;
unexpected request consequences and required responses remain prominent.

Default English dates use **15 Sep 2026**. Interface and notification strings remain
translatable; the user's language follows them across NGOs, with English fallback.
Portuguese for Mozambique and Angola is planned, not delivered. Locale does not
change work timezone, jurisdiction, permissions, or stored calculation values.

## Component Patterns

Shared primitives (task drawer/page, short confirmation, grouped toolbar, filter
sheet, disclosure, uploader, save status, return-to-origin) inherit platform behavior.
The corresponding Leave visual rules are in DESIGN.md Components. The sections
below define composite surface behavior without turning it into a new domain model.

### My Leave and balance explanations

Make Apply for leave prominent, followed by per-type available balances with
expandable explanations, pending requests, upcoming approved leave and history.
Place required employee responses near the top without replacing Apply. Show an
unfinished-application note beside Apply when a saved draft exists; no Drafts
section or draft badge. Show current available and reserved amounts distinctly,
with expandable ledger explanations. Defer the separate future-date balance
calculator and graph. Selecting dates in a leave draft automatically shows the
projected effect for those dates, paid/unpaid allocation and resulting balance;
exploring dates does not submit or reserve leave. Keep calculation details
expandable. Explain the applicable consequence: unpaid amount and required
acknowledgement, permitted use of future entitlement, or insufficient leave when
not permitted. Do not substitute a generic negative-balance warning for that
explanation. Existing policy, authorization and reservation rules still apply.

### Apply for leave

When reopening an older draft, preserve entered details and refresh balances and
applicable rules. Explain changes beside the affected field or balance, without
a separate Review draft screen. An increased unpaid amount requires acknowledgement
before submission. Past dates follow existing backdating rules; they are not
automatically invalid merely because the draft was saved earlier.

Keep one unfinished employee application draft per employee per NGO. Apply for
leave resumes it; show a small unfinished-application note beside the action on
My Leave, without a Drafts section or badge. Within the form, Discard draft asks
for confirmation before deletion. Submitted requests remain separate.

Close, desktop Escape, and mobile Back close immediately when saved and finish
an in-progress save before closing. On save failure offer Retry, Keep editing,
or Discard unsaved changes; the last option retains previously saved content.
Confirm before discarding an approver’s unsent comment.

Use the shared contextual task-surface direction: a sufficiently wide right-side
drawer over My Leave on desktop, with a full page on mobile or narrower screens.
Keep essential balance information inside the form. Apply the same draft saving,
validation, submission acknowledgement, and NGO ownership rules in both layouts.
The shared convention defines the interaction foundation; Leave owns the form
content and business meaning. Precise composition and widths remain open.

Inherit shared [date-input behavior](../../../../platform/EXPERIENCE.md#date-inputs).
Full days use one range control with calendar and typed entry; single-day requests
have matching start/end dates. Half days use one date without morning/afternoon;
hours use one date and the agreed 30-minute duration increments, without exact
times. Let users complete entry before errors appear; explain reversed ranges
beside the control without silently swapping dates. Once required inputs are
valid, calculate duration and balance. Incomplete input must not show a misleading
zero. If selected dates contain no scheduled working time, explain this and ask
for an adjusted selection. Leave owns schedule/holiday/policy validation.

The first form choice is leave type. Use it to determine applicable duration
options, policy guidance, and document requirements. No default type or duration
selection has been chosen.

After leave type, show the permitted Full day(s), Half day, and Hours options.
Full days use start/end dates. Half days use one date and exactly half the scheduled
working hours, without selecting first/second half. Hours uses one date and an amount
in 30-minute increments, without start/end times. An optional note can describe
arrangements. Update calculated duration and balance effect below as details are
entered. Warn about other active requests on the same date; block only when the
combined duration exceeds scheduled hours, subject to all other validation. Show
Part-day absence to colleagues without type or exact times; deduct actual requested
duration. See the authoritative ADR-0074 in the Leave decision collection.

### Request balance explanation

Show a compact summary inside the form: Requested, Available for these dates,
and Remaining after this request. For example, 2 hours requested against 16
available leaves 14 hours. Keep detailed accrual, carry-over, and reservation
calculations expandable. A shortfall prominently shows the exact requested unpaid
amount; it must not be hidden inside the calculation details.

Place the unpaid-amount acknowledgement beside the balance summary, not after
notes/documents. Example: Paid: 2 days · Requested unpaid: 1 day, followed by
I understand that 1 day is being requested as unpaid leave. Use the actual
calculated amount and schedule-aware units; preserve the existing requirement to
acknowledge a changed amount before submission. This is requested unpaid leave,
not an approved allocation.

Keep Requested unpaid inside the balance breakdown directly below Paid, with bold
label/amount and subtle neutral shading on that row. Keep acknowledgement directly
beneath the summary; do not separate the unpaid amount into its own panel outside
the calculation. Preserve the sequence Requested → Paid → Requested unpaid.
Use wording and weight rather than colour alone. The shortfall is a consequence
requiring acknowledgement, not a validation error, and does not use the accent
reserved for primary actions.

The summary follows the authoritative date-by-date funding rules. The simple
single-date example must not imply a multi-date request is affordable throughout
merely because it has a positive aggregate balance. Explain date-specific shortfalls
when applicable, preserving the existing explicit acknowledgement requirement.

### Notes and supporting documents

Place these below the balance summary. Label the note Note to approver — optional
unless an existing rule requires an explanation. Show Supporting document when
the selected policy permits or requires it, clearly labelled optional or required.
Show upload/save/verification status for attached files. If a required document
is missing or still being verified, explain why submission is not ready. Preserve
entered data, existing document permissions, and content-safety rules; this adds
no malware-scanning requirement to MVP.

### Request action area

Keep Close and Submit request visible at the bottom of the desktop
drawer, with Draft saved shown only after successful persistence. On mobile, keep the same controls reachable
without covering form content, including the last field and required
acknowledgements. Maintain the shared primary-action visual convention.

When submission is not ready, explain the blocker beside its relevant field.
Do not rely on an unexplained disabled button. Preserve existing submission
revalidation, save-failure behavior, and exact unpaid-amount acknowledgement rules.

### Agreed wireframe refinements

- Use one Leave dates range control for full days, supporting one-day ranges and
  keyboard/manual input. Half-day and hourly requests use a single-date picker.
- Present balance equivalents in standard days, including fractions, with hours
  and calculation accessible by click/tap/keyboard disclosure rather than hover
  alone. Keep hours prominent for hourly requests. Distinguish dates off from
  standard-day equivalents where schedules vary; canonical minute calculations
  remain unchanged.
- Replace the earlier Save and close label with Close and Draft saved. Wait for
  outstanding saves and use the existing retry/stay/discard-unsaved failure choices.
  Closing does not cancel leave or delete a persisted draft.
- Inherit the shared upload interaction: desktop drag/drop or Browse button,
  mobile Choose a file. Application-specific limits and permissions still apply.
- Use factual, friendly empty-state copy: You have no requests awaiting approval.
  A subtle decorative icon is optional, not a substitute for text.
- Retain readable muted text. The wireframe's #626262 on white measures 6.10:1;
  this colour-pair check does not establish full accessibility compliance.

Layout discussion artifact: [.working/apply-wireframe.html](./.working/apply-wireframe.html).
This grayscale mock illustrates the current direction; dimensions, final tokens,
input widgets, and unrendered states are not finalized.

### My leave history

Remember each employee's Calendar/List preference per NGO. On a new visit, open
the current year when it falls within available history bounds, retaining the
chosen presentation. Do not reopen an out-of-bounds year merely to show This year.

Bound year navigation by the earliest relevant employment or recorded leave year.
If employment end is defined, use its year as the upper bound unless later records
need access. Preserve prior employment/rehire history and records outside employment
that need review; do not hide them behind the latest employment interval. Without
an end date, impose no employment-end bound. Show full boundary years and mute
non-record dates outside employment, labelled Before employment or After employment.
Disable unavailable navigation controls. A This year shortcut must respect the same
bounds instead of opening an otherwise unavailable year.

Allow navigation to previous and next years with a This year return action.
Preserve the selected Calendar/List view and mobile month when changing years;
mobile month navigation can cross year boundaries. Display records for the selected
year and an honest empty state when none are available. Apply existing authorization
and date/timezone rules. The approved year-calendar layout and its navigation are
illustrated in [employee history](./.working/employee-history-wireframe.html).


Use one My leave history screen with Calendar and List views sharing a year
selector. Preserve the selected year when switching views. Selecting an entry
opens its request details in the desktop drawer or mobile page. Clearly distinguish
upcoming and pending entries with status labels and keep past leave easy to find.
Apply existing own-request authorization and compact month presentation on small
screens while retaining access to the history list.

Keep calendar day cells uncluttered with subtle leave markers. Selecting a date
reveals its requests with permitted type, duration, and status; selecting a request
opens details. Use neutral shapes or patterns to distinguish pending and approved
entries, with accessible text equivalents, rather than using the primary-action
accent or colour alone. The List view exposes equivalent information directly.
The approved employee-history mock illustrates the neutral markers and selected-date detail arrangement; final styling remains open.

The List view shows dates, leave type, duration, and status, with leave-type and
status filters. Default to most recent leave dates first. Selecting a row opens
the request details. On phones, group each request in a compact stacked row:
dates and status on the first line, type and duration below, with subtle separators
instead of heavy card borders or shadows. Avoid a horizontally scrolling wide table.

### Approver queue

Expose one Approver role in access management. Supervisor is a reporting
relationship used for assignment, and final approver is a workflow position;
neither needs a separate role selector. Retain step-specific responsibility,
absence rules, self-approval and document boundaries. The same role can decide
first or final steps when validly assigned, never arbitrary requests.

Show delegated requests in the temporary approver's normal Approvals queue with
a small Acting for [original approver] · until [end date] label. Reuse the usual
review and approval actions; do not add a separate delegated-work screen. History
records the actual decision-maker and the original approver they acted for.

Each row shows employee name and leave dates, leave type and duration, elapsed
time awaiting the current approver's action, and applicable flags such as balance
override or backdating. Only show authorized actionable requests under the existing
workflow rules. Selecting a row opens the review drawer, with the established
full-page presentation on mobile. Keep approve/reject actions inside the review
view rather than on queue rows so the approver sees context before deciding.

Provide employee-name search and filters for leave type, leave dates, and exception
flags. Default to longest waiting for the current approver's action first, with an
option to sort by earliest leave date. Apply authorization and privacy to the
results and filter choices; these controls do not broaden actionable scope.

### Approval review

Keep all steps required by default. For an explicitly enabled two-step absence
policy, the configured final approver (CEO in the example) may approve alone when
the supervisor has a recorded applicable absence. If the final approver is absent,
require a temporary final approver; the supervisor cannot decide alone. Label the
omitted supervisor step Not required under absence policy, not Approved. Retain
at least one valid approval, actual decision-maker attribution, self-approval and
other finalization checks. Apply absence conditions when approval is needed, not
on the applicant's leave dates. When both configured approvers are absent,
the temporary final approver may decide alone if their appointment explicitly states
May approve without the supervisor's step when the supervisor is absent. Include
this in the assignment review as a scoped temporary responsibility; preserve
self-approval restrictions. Do not require two substitutes solely for these steps.

In coverage review, recognize an available, policy-authorized final approver or
explicitly authorized temporary final approver as valid coverage for the supervisor
responsibilities they can handle alone. Do not request a duplicate substitute for
those responsibilities. Separately surface any remaining responsibilities needing
a substitute or explained exception.

A temporary approver or final approver using fallback may leave a request pending
to wait for the supervisor and optionally explain this in a normal visible comment.
Continue reminders/escalation and keep the request visible. When the supervisor
returns before any final decision, restore their outstanding step under the
snapshotted absence policy and record the transition. Completed final approval is
not reopened. Temporary assignments retain their agreed expiry/return process.

Include the ability to record a missing-temporary-approver exception in the default
Leave Manager role, backed by a distinct business permission that advanced custom
roles may omit. Do not require an extra permission setup step for the default role.
This capability does not confer approval authority. Use the shared role model in
platform ADR-0011.

If the applicant has approval responsibilities without coverage for the absence,
show Approval coverage needed and explain that a temporary approver must be arranged
before final approval, including coverage for new requests. Allow submission and
retain the request while an authorized actor arranges cover. An authorized Leave
Manager may record a justified exception with mandatory reason; keep the unresolved
gap visible. Exception authority is separate from approval authority and does not
waive other finalization requirements. Never alter actual absence dates to conceal
a coverage gap. Enforce the same condition for automatic finalization paths.

Order the content as employee/type/dates/duration, exceptions needing attention
(including requested unpaid leave), balance effect and employee explanation,
permission-controlled supporting-document status, then expandable approval history.
Keep Reject and Approve visible at the bottom without obscuring content.

Apply existing workflow-specific override and employee-acknowledgement gates;
final approval must not proceed while required renewed acknowledgement is missing.
Preserve the distinction between intermediate approval and final consumption.
The layout does not grant document access or permission to decide an override.

For approval, allow an optional comment followed by one explicit confirmation
action. Rejection requires a reason clearly labelled Visible to the employee.
After a confirmed decision, show the result and return to the queue. Do not imply
that an intermediate approval is final request approval.

If saving fails, keep the review open and preserve the comment. For an uncertain
outcome, check whether the decision succeeded before permitting a retry that might
duplicate it. Existing permission, concurrency, current-step, and acknowledgement
checks still apply; neither action silently overrides a conflicting decision.

### Team availability during approval

Within the review drawer, show Team availability for the selected request's dates
with a brief summary such as 2 colleagues have leave during these dates. Desktop
uses a compact timeline with employee rows and date columns; subtly emphasize the
requested range and initially show colleagues with relevant absences. Use full-day
bars and distinct labelled partial-day markers, with no implied morning/afternoon
or exact times. Existing privacy vocabulary and field permissions govern labels;
do not reveal leave type or medical details through markers or tooltips.

On mobile, use a compact list grouped by date rather than compressing the timeline.
Keep all results within permitted team scope, without requiring a separate calendar.

### Balance-override review

Show requested amount, available paid balance, and shortfall together, with unpaid
leave as the default proposal. An actor with override permission can accept that
proposal or specify an authorized alternative allocation, with a mandatory reason.
Preview the resulting paid/unpaid split before confirmation. Preserve existing
authorization for each funding source and employee acknowledgement requirements.
Keep this decision separate from ordinary approval; permission to approve a
request alone does not grant override authority.

Keep the override, revised allocation and employee response within the existing
request. An increased unpaid amount produces a notification and **Your response
is needed** on My Leave. Show previous/revised amounts, actor and reason. The
approver sees **Waiting for employee acknowledgement** and cannot complete approval
until the employee acknowledges the current amount. An unchanged or decreased
unpaid amount needs no renewed acknowledgement. The response resumes the remaining
approval workflow; it does not approve leave or create another workspace.

### Leave Manager home

Lead with Needs attention, grouped into escalated approvals, balance deficits, and
requests affected by changes. Preserve separate action permissions. On desktop,
keep Organization overview beside the heading at the right; use an internal
navigation arrow. Place Employee actions, Configuration, and Records in a secondary
right column separated by a subtle vertical divider.

On mobile, use a compact Overview text action beside the title and a Management
tools control immediately below. The control opens a modal bottom sheet containing
the same permitted tools in labelled groups with single-column links. Keep the
attention queue below the control. Do not require scrolling through the queue to
reach tools, or add a floating action button without demonstrated need. Target
at least 48px-high actionable rows, with full-row touch targets and visible focus.
The mobile tools sheet shares modal focus/close conventions, but navigation choices
open their destination directly; it does not use the filter sheet's Apply step.

### Organization leave overview

Use the available screen width to separate data controls from presentation controls.
Place Timeline/List beside the heading, aligned right on desktop. Group the compact
toolbar into time navigation first, attributes (employee search, location, team,
status), and modifiers/reset (Show all employees, Clear filters). Use subtle
dividers between groups and wrap coherently at narrower widths. Keep the legend
compact and adjacent to the timeline, outside the primary control sequence.
On mobile, retain a compact date navigation row and place Filters beside the view
controls below it; List remains the default. Filters opens the shared modal bottom
sheet defined in platform EXPERIENCE.md. Include employee search, approved/pending
status choices, location, team, and Show all employees. Apply filters commits and
closes; Close or Back discards unapplied changes. Reset filters restores defaults
in the provisional selection: empty search, approved and awaiting approval selected,
all locations/teams, and Show all employees off. Reset takes effect on Apply.
The outside badge counts applied groups differing from defaults; omit zero and put
no count on Apply filters. Keep header/footer reachable around scrollable content.

Provide Search employees alongside the filters, searching employee names within
the authorized NGO scope and preserving the selected dates and filters. Searching
does not silently enable Show all employees; users explicitly enable that option
to include employees without leave in the selected period.

Use checkmark and clock status icons on narrow bars, retaining text where it fits.
Keep a visible legend, the approved/pending border distinction, and accessible
status labels. At continuation edges, remove the bar border and retain the chevron.
The displayed date range is the calendar-picker trigger; omit a separate Date range
button. Implement it as a keyboard-accessible control with an accessible name.

For an empty period, show No leave to display for these dates and retain date
navigation and Show all employees. When filters exclude all results, show No leave
matches these filters with Clear filters. Never infer Everyone is available.
Loading failures show an error with Retry instead of an empty timeline.

Keep employee names fixed on the left and date headings fixed at the top while
scrolling the timeline. Mobile retains the default date-grouped list so sideways
timeline navigation is not required.
Keep date columns readable and comfortably selectable, using horizontal scrolling
when a full month does not fit. Allow long employee names to wrap in the fixed
name column. Exact widths remain provisional pending visual validation.

Show a small continuation marker at either bar edge when the request extends
beyond the visible date range. Selecting the entry shows its full date range;
the viewport boundary must not imply the request starts or ends there.

Bars are selectable but cannot be dragged or resized to change dates. Date changes
use the authorized request change or correction form, including the applicable
balance, unpaid amount, and approval consequences before confirmation. Make the
same actions accessible by keyboard and on mobile.

Default to an employee-row timeline for comparing availability, with a List view
for phones and detailed scanning. Do not add a third month-calendar presentation
without a demonstrated need. Use existing authorized date-range, department,
team, location, and status filters, and leave-type filtering only where permitted.
Entry selection opens currently authorized request details in the familiar desktop
right-side drawer or mobile full page. Show only permitted details and actions.
Closing restores the overview's dates, filters, and scroll position. After an
authorized change, refresh the affected entry while preserving that position.

Show approved and awaiting-approval requests by default. Approved entries use
softly filled bars; awaiting-approval entries use outlined bars with dashed borders.
Provide a small legend and written status in request details; do not rely on color
alone. The status filter supports approved-only viewing. Cancelled, withdrawn, and
rejected requests remain available in history.

Stack markers for multiple partial-day requests on the same date within the
employee row, expanding its height only when needed. Keep each request selectable
with its own approval status. Placement within the date column must not imply
morning, afternoon, or exact times. On mobile, list each request under that date.

Keep every date visible. Use very light shading within each employee's row for
their scheduled non-working days; do not assume Saturday and Sunday are everyone's
weekend. Preserve the location-aware holiday treatment below. Accessible date
details explain the shading so no leave booked is distinguishable from not
scheduled to work.

Render a request as one continuous bar across its date range, including intervening
non-working days, while keeping their shading visible. Request details show the
date range separately from calculated leave duration, with an expandable calculation.
For example, Friday through Monday spans four calendar dates but uses two working
days for a Monday-Friday schedule when both dates are otherwise eligible working
days. Bar length must not be presented as the entitlement deduction.

Open on the current month. Provide Previous, Today, and Next controls plus a custom
date range, preserving selected filters when moving between periods. This defines
the initial overview window, not an additional calendar presentation.

Default to employees with leave in the selected period. Offer Show all employees
for the complete staffing view, still subject to active filters and authorization.
This changes displayed rows, not underlying staffing calculations or employee scope.

Remember filters separately for each user and NGO; do not carry department, team,
or location selections between organizations. Clear saved selections that are no
longer valid or permitted and explain briefly without revealing inaccessible
metadata. Keep Clear filters available.

Show public holidays from configured calendars as restrained date-header context.
For one selected location, use subtle header shading and the holiday name. For
multiple locations, show a small Holiday in selected locations indicator that
expands to holiday names and locations. Do not shade a whole column as non-working
when the holiday applies only to some employees. Individual schedule/calendar rules
remain authoritative; a public holiday does not automatically mean every employee
is off work. Holiday and absence markers must not bypass existing privacy rules.

### Leave Manager escalated approvals

If a temporary approver becomes unavailable after the covered employee's leave is
approved, retain the leave approval and show Replacement approver needed to
authorized Leave Managers. Require authorized reassignment; do not automatically
cancel approved leave or extend another person's authority.

Support planned approval cover for each step, including final approval, with an
eligible named delegate and effective dates. Flag known approved absence without
waiting for escalation; missing cover must remain visible. Preserve completed
decisions and require explicit authorized rerouting for already assigned work.
Provide alternate authorized Leave Manager cover rather than relying on one actor.
Do not infer approval authority or substitutes from reporting relationships.

An authorized Leave Manager may select any active member of the same NGO as the
temporary approver. The explicit appointment supplies authority for the specified
responsibilities and dates; do not require a permanent Approver role first. Show
what authority is being granted and record actor/reason/scope/dates. Retain absence,
membership, and self-approval checks. Do not grant separate medical-document access
or unrelated approval/editing powers. The temporary authority ends at expiry.

Notify the temporary approver by email and in-app on appointment, changes, and
early termination. Include whom they act for, assignment dates, and a link to
Approvals, without sensitive request details. No acceptance step is required in
MVP; the appointing manager confirms availability beforehand and the assignment
takes effect on its start date. Delivery uses the shared notification capability.

Provide End assignment to authorized managers. Preview outstanding approvals and
their proposed destination: the eligible, available original approver or another
authorized appointment. Require a reason and end the temporary authority on
confirmation. Allow termination even without a replacement; keep requests pending
and flagged while preserving completed decisions. Retain the missing-temporary-
approver issue throughout the original approver's absence, even with no pending
requests, until valid replacement coverage exists or the original returns eligible.
Ending an assignment does not resolve the coverage issue or cancel approved leave.

Prevent overlapping temporary assignments for the same responsibilities on a date.
Show the existing assignment and allow date adjustment or explicit authorized
replacement. Permit sequential assignments, such as 1–15 and 16–31 December.
Do not silently choose an approver when assignments conflict.

Use Temporary approver in interface labels instead of cover. During setup, show
already-waiting requests and offer Include these pending approvals. An authorized
person confirms the selected reassignment with a recorded reason; completed
approvals remain unchanged.

The approved assignment layout groups original/temporary approver, dates, explicitly
granted responsibilities, pending-request selection, required reason, and conditional
return at expiry. Review assignment shows a plain-language summary of these effects
before Confirm temporary approver. For temporary final approval, explicitly state
whether supervisor-absence single approval is included. The prototype reference is
[temporary approver](./.working/temporary-approver-wireframe.html); its fixed sample
values and preview dialog are not production behavior.

During setup, disclose and authorize the default: When this assignment ends,
unfinished approvals return to [original approver]. At expiry, automatically return
outstanding steps only after rechecking the original approver's eligibility and
known continuing absence. Preserve completed approvals, audit the transfer, and
notify the returning approver. If checks fail, retain the pending request and flag
an authorized Leave Manager; do not automatically extend temporary authority.
An authorized extension before expiry postpones the return. This is a scheduled
transfer authorized at setup, not an unannounced directory-driven reroute.

Queue rows show employee, leave dates, current assigned approver, and time awaiting
action. Opening an item shows the request and escalation history. Show Reassign
approver only with existing rerouting permission; require a reason and preserve
earlier decisions. Apply the active NGO scope and existing permission checks to
both display and action. Escalation alone grants no approval or rerouting authority.

### Administrative leave correction

If an administrative replacement is rejected, show its rejection reason prominently
and add Correction needs follow-up to the Leave Manager attention queue. Keep the
original cancelled; do not automatically restore known-incorrect dates. An authorized
person can edit and resubmit the rejected replacement under the existing resubmission
rules, preserving history. Keep the unresolved historical record visible for follow-up.

In employee history, make the replacement the main entry with a Corrected label
separate from its current approval status. Expanded history shows the original as
Cancelled — replaced by corrected request. Display the replacement on its corrected
calendar dates with its current approval styling; keep the cancelled original in
history rather than showing another absence. Preserve both linked audit records.

When the employee opens a correction notification, show the updated request with
a brief notice naming the correcting actor, original and corrected dates, and the
employee-visible explanation. Below it, show current approval status and balance
effect; make the original request accessible through history. Do not require an
acknowledgement for the returned-early example. Increased requested unpaid leave
still requires the agreed acknowledgement. These details belong in the authorized
request view, not in the minimal email or in-app notification payload.

The approved returned-early layout shows the original approved record, corrected
dates, a before/after comparison, and the balance impact before confirmation.
Separate restoration of the original deduction from reservation for the linked
replacement; disclose other calculation effects when applicable. Require an
employee-visible explanation and explain notification and approval consequences.
Use Cancel original and submit replacement as the explicit confirmation action.
Correction permission does not grant approval authority. Preserve the original
on validation failure and retain its history after successful cancellation.

### Balance-deficit review

Show employee and affected leave type, deficit amount and triggering change,
before/after balance breakdown, and relevant history. Provide an outcome and
mandatory explanation visible to the employee. Any additional paid entitlement
must be an explicit, separately recorded authorized adjustment. Existing
balance-adjustment permission and NGO scope checks apply.

Illustrative departure case: 20 days granted upfront, 15 taken, entitlement
recalculated to 10 under the applicable policy, resulting in a five-day deficit.
Actual amounts use the agreed calendar-day proration and rounding, not an assumed
universal half-year formula. No automatic conversion of approved leave to unpaid
or salary deduction occurs.

Offer four outcome choices: Keep open for further discussion/investigation;
Correct source information and recalculate using existing permissions; Grant
additional entitlement through an explicit authorized adjustment with a reason;
or Record decision without adjusting the balance, retaining the deficit and
explaining the agreed handling. Review completion must not erase a deficit or
imply payment/recovery. These choices do not grant new employment-record editing
or other source-correction permissions.

### One-off balance adjustment

Send minimal email and in-app notifications: Your leave balance was updated, with
a link to authorized adjustment details. The detail view shows amount, effective
date, resulting balance, actor, and reason. Require no acknowledgement unless
requested unpaid leave increases, in which case the existing acknowledgement rule
applies. Keep sensitive detail out of notification payloads.

Correct an erroneous adjustment through another ordinary adjustment with a required
reason explaining the mistake. Do not add a dedicated Correct adjustment function
in MVP. Preserve the original entry and apply the same authorization, impact
preview, review, and confirmation; an opposite amount can still affect current
balances or reservations and must not be treated as a consequence-free undo.

Retain Review adjustment followed by Confirm adjustment for this infrequent,
high-impact action. Keep the review concise: employee, leave type, amount,
effective date, resulting balance, and reason. Make consequences for existing
requests prominent. This does not establish a two-step default for routine forms.

Show employee and leave type, Add or Deduct followed by an amount, effective date,
and mandatory reason. Preview current balance and resulting balance plus any
affected pending requests, then offer Review adjustment followed by Confirm adjustment. Preserve the resulting
ledger entry in the employee's balance history. Existing balance-adjustment
permission, audit, and explained unpaid-increase acknowledgement rules apply.
Keep this separate from a continuing entitlement override.

### Employee entitlement override

Keep the editing form concise: omit a repeated What changes summary. Put Applies
each leave year until changed beneath the override option, Next leave-period start
beside the effective date, and a quiet Adding leave just once? Adjust leave balance
link beneath source choices. Reserve the before/after comparison and relevant
current-balance explanation for Review change; keep unexpected consequences visible.

For MVP, recurring overrides continue until explicitly changed; omit an automatic
end-date field. Recurring changes, including Use policy entitlement, take effect
only at a leave-period boundary. Default to the next leave-period start (which
need not be 1 January); do not offer midperiod effective dates. Monthly accrual
does not change the policy’s leave-period boundaries. Do not reset current balances
or introduce automatic midperiod recalculation. Immediate balance changes use the
separate authorized one-off adjustment flow, subject to its impact preview and
validity/expiry rules. A one-off adjustment does not change recurring entitlement.

Use one Edit employee entitlement action for creating, changing, or ending an
override. Offer Use policy entitlement, displaying the inherited amount, and
Set employee-specific entitlement, enabling the override value. Returning to policy
ends the override from the chosen effective date with a required reason and impact
preview. Preserve its history; do not set available balance to the annual allowance.
No separate Remove override workflow is required.

Compare policy entitlement and proposed employee entitlement in the review, with
the effective date and mandatory reason. Preview balance and accrual effects before
confirmation. Clearly distinguish a continuing entitlement change from a one-off
balance adjustment. Apply existing configuration authorization, effective dating,
and audit rules; do not silently rewrite historical grants or requests.

### Leave-type and policy configuration

Provide an editable new-client starter approval configuration: one supervisor
step, self-approval off, temporary approvers available, reminders after three
calendar days and escalation after seven. Offer a second step and directional
absence fallback as optional settings. Help assign supervisors and flag invalid
or missing approval routes. Before activating the starter policy, obtain client
confirmation of entitlement, schedules, holidays, and organization-specific rules;
do not present sample allowances as universal country defaults.

Keep approval requirements separate from the source of supervisor assignments.
Maintain assignments manually for MVP; future shared Microsoft Graph directory
integration may populate them without replacing Leave's approval rules. Preserve
authorized overrides, flag missing/invalid assignments, and retain NGO/approver
eligibility checks. Do not silently reroute pending requests on directory changes.

Open a leave type's current policy as a readable summary before entering edit mode.
Group it into entitlement/accrual, request rules, approval requirements, and
documents/privacy. Show its effective date prominently; offer Edit policy to
authorized managers and previous versions through history. Editing prepares a new
version and does not immediately modify the active policy.

Use a dedicated editing page on desktop and mobile, with the same four sections
and expandable advanced options. Managers can directly reach a setting without
a sequential wizard. Review changes is the primary action; it leads to the
differences and effective-date review before publishing. This follows the shared
exception to drawers for longer, complex forms.

[Policy editor preview](./.working/policy-editor-preview.html) demonstrates the
four-section dedicated page, responsive section navigation, editable example
settings, changed/unchanged review and Back to editing. Publication is disabled;
affected-employee counts are illustrative and request impacts are not calculated.
Carry-over/cap/proration conditional fields now appear in the preview; a searchable
final-approver example now uses illustrative eligible people. The user approved the editor
layout on 20 September 2026; this does not authorize implementation or new policy
defaults.

Advanced controls reveal only applicable fields. Carry-over offers None, All unused
entitlement, or Up to a limit; reveal limit only for the last option, and expiry/
repeat-transfer options when carry-over is enabled. Applying a balance cap reveals
the maximum. Enabling proration reveals rounding. Two approval steps reveal the
final-approver picker and relevant absence rule. Duration-threshold document
requirements reveal the threshold. These expose existing policy capabilities;
layout approval does not choose policy defaults.

For two-step approval, show Step 1: Employee’s supervisor and Step 2: a searchable
final-approver picker. Search eligible people in the current NGO; show name and
team/job-title context where needed. Require an explicit selection without a CEO
or other person preselected. If none are eligible, explain the gap and provide
access-management navigation only to administrators authorized to manage access.
Assignment sets workflow responsibility without silently granting permissions.
Temporary cover remains separate. The preview uses illustrative eligible people;
production lookup and authorization still require implementation.

For carried-leave expiry, offer Does not expire or Expires after [months] from the
new leave-period start. Show the resulting last usable date beneath it. Three
months from 1 January ends on 31 March; from 1 July on 30 September. This avoids
annual fixed-date maintenance, respects anniversary periods and never extends an
existing carried portion’s expiry. Example values are not policy defaults.

Document example: Required above a duration threshold with 2 days means a request
of 1 or 2 days can be submitted without a document, while 3 days requires one.
Apply the configured request-duration calculation and show the requirement in the
application when relevant. The example value is not a legal or client default.

Before publishing, show changed settings with previous/new values, the effective
date, covered employees with overrides distinguished, and any existing requests
needing attention. Do not silently rewrite existing requests. Keep unchanged
settings expandable. Offer Back to editing and Publish policy version.

For future publication, retain the current policy as the main summary and show a
Scheduled change notice with its effective date and a link to the scheduled version.
Confirm Policy scheduled for [date], rather than implying immediate application.
Label the future version Scheduled and the existing version Current until the
effective date.

Start with a leave-type list showing name, current policy, and active/archived
status. Selecting a type opens configuration grouped into Entitlement, Request
rules, Approval, and Documents & privacy. Keep advanced settings in expandable
sections rather than displaying every rule at once. Preserve existing configuration
permissions, policy versioning, and archive semantics; these groups are navigation
and presentation, not new domain boundaries.

Before publishing policy changes, show the changed settings and effective date
in a review step, followed by Publish policy version. Unconfirmed edits follow the shared administrative edit/review/confirm contract;
they do not take effect or imply a separate persisted admin draft system. Explain that
historical requests retain their recorded policy and existing requests are not
silently recalculated. Apply existing effective-dated versioning and configuration
permissions; publishing is not a retroactive migration of request history.

### Work profiles and employee schedule defaults

The approved [employee schedule wireframe](./.working/employee-schedule-wireframe.html)
shows the assigned profile first, inherited values together, and field-specific
employee overrides clearly marked with an option to use the profile value. Preview
the effective-date change with a required reason and request impacts before
confirmation. Standard-day conversion remains distinct from daily scheduled hours.

Use reusable work profiles with NGO default, location/team profile, and employee
override layers. Profiles supply working days, daily hours, work timezone, holiday
calendar, and standard-day conversion duration. These are organization-configured
values, not assumptions about statutory or universal country schedules.

Assigning a profile fills inherited values. Show the source (for example, Inherited
from Maputo office), distinguish explicit employee overrides, and offer Reset to
profile. Profile changes are effective-dated and preview affected employees.
Preserve explicit employee overrides and historical request calculations.
Each employee has one explicitly assigned work profile. Location or team may
suggest the initial profile, but neither silently replaces it later. This resolves
conflicting location/team defaults through assignment rather than an implicit
precedence or field merge. Preserve employee overrides and the NGO default layer;
profile assignment changes use authorized effective-dated handling.

Before publishing a profile change, show effective date, changed values, and
affected employees. Highlight employee overrides that preserve a value unchanged.
List existing requests needing attention separately with the reason. Do not
silently rewrite their recorded calculations. Apply existing configuration
authorization and audit requirements.

### Holiday calendars

List calendars by location, showing each calendar's name and year. Opening a
calendar shows its holiday dates and names, with add/edit actions only for
authorized actors. Assign calendars to employees through work location or schedule
so one NGO can support staff in multiple countries. Preserve existing effective
configuration, historical request calculations, and authorization rules. The
employee schedule defaults now use the work-profile pattern described above.

### Reports

Start with a simple list of the existing MVP reports. Open each with relevant
filters, results, and Export CSV where permitted. Export uses the same date range,
filters, NGO scope, and privacy rules as the displayed results, through the
authorized Leave API with audit records.

Use shared reporting layout, date/filter controls, tables, pagination, loading/empty
states, and export feedback when established. Leave owns report definitions,
calculations, allowed filters, authorization, and export data. Prove reusable UI
through Leave before promotion to ui-business and scaffold templates. No separate
reporting service is required for MVP; shared reporting implementation is still
pending, not assumed present.

### Leave Manager audit history

Provide a searchable chronological list showing when, who, what changed, and why,
with filters for employee, action, and date range. Opening an entry reveals only
permitted before/after details and a link to the affected record. Apply active-NGO
authorization and sensitive-field permissions to list, search, details, and linked
records; audit access must not bypass medical-document authorization.

The [employee Leave-settings preview](./.working/employee-leave-settings-preview.html)
shows a readable employee summary grouped into Employment & approval, Work schedule
and Leave entitlement. Authorized group actions open focused edit/review examples;
balance adjustment is separate. A read-only preview hides mutation actions without
hiding leave history. Ana’s setup issue now links to this preview. Layout awaits
feedback; confirmation, real data lookup and impact calculations are not implemented.

The shared-identity example is Ana’s name and sign-in email, reused by Leave and
future applications. Leave-specific settings refer to that person rather than
maintaining a separate editable identity. This does not move all employment data
into a shared directory: supervisor assignment remains manual in Leave for MVP.
API/data-ownership contracts remain architecture work; no cross-silo imports or
new shared directory implementation are implied by the visual example.

### Setup and migration

Offer a non-sequential setup checklist linking to normal settings: work profiles
and holiday calendars, leave types/entitlements, employees/profile assignments,
and supervisors/approval routes. Omit a standard opening-balances checklist row.
Show completion and unresolved
issues. Name affected employees only when relevant data exists; otherwise show
configuration tasks. Do not assume migration or pre-existing employees.

[Setup checklist preview](./.working/setup-checklist-preview.html) shows a responsive
three-area checklist, expandable issues and linked employee context with return to
setup. Separate illustrative scenarios cover existing employees versus an empty
NGO. Consultant email approval and its waiting status stay outside the Leave UI;
no client confirmation, self-service import or activation action is added. Existing
settings previews are linked; complete employee/profile editors and production
readiness evaluation are not implemented. The user approved the layout with the
consultant-status/opening-balances row removed. Show balance issues only when
actually detected; a zero balance alone is not evidence of missing migration data.

For MVP, use a consultant-operated import tool and a simple client-facing results
and reconciliation summary rather than a general self-service upload screen.
The tool accepts documented templates, validates/previews changes, reports errors
by employee/row, prevents duplicate imports, and audits actor/batch/results. Use
supported authorized application import contracts, not ad hoc database edits.
Normal manual entry remains available. Defer self-service import UX until actual
migrations establish reusable patterns. The consultant sends the generated report
to an authorized client contact, receives approval or corrections by email, and
records approval evidence against the exact import batch before applying it.
Changed data requires a revised report and renewed approval. Do not add an in-app
confirmation page or Confirm balances action; use the consultant/email process.

The consultant establishes the source balance date, whether future approved leave
and pending reservations are already included, and which requests transfer. The
preview reconciles these together so request effects are counted once. Follow
the migration runbook linked from the Leave application README; do not add client UI for
these source-mapping tasks.

### Notification inbox

The bell opens a compact panel with newest notifications first, a clear unread
marker, and Mark all as read for the active NGO only. Display only the approved
minimal employee/date/status information and link. Selecting an item opens its
request under current authorization checks. Empty state: No notifications yet.
Retain per-user read state, NGO selector count privacy, and the distinction between
read notifications and unresolved business actions. This is a shared-shell pattern
to implement through the planned common notification contract.

### Application access and custom roles

Inherit the shared person-centric application-access flow. Expose Employee,
Approver and Leave Manager with descriptions and expandable plain-language
capabilities; actual permissions and assignment scope govern their contents.
Organization Administrator normally manages NGO application roles; advanced
per-application delegation does not give Leave Managers general role administration.
Keep approval, on-behalf correction, balance adjustment and sensitive documents
separately controlled. Review role additions/removals before applying them.

Custom-role creation inherits the application from settings and starts with empty
name, description and capability choices. No Start from selector. Duplicate role
is a separate action prefilling the same editor. Multiple custom roles may belong
to one application and a person may hold several; cross-application bundles are
deferred. A newly created role grants nobody access until assigned, and new
capabilities are not silently added to existing custom roles.

Before confirming edits to an assigned role, show added/removed capabilities,
number of holders with expandable names, and that changes affect everyone holding
it. Equivalent authority from another role or valid temporary appointment remains.
Delete custom roles only when no people hold them; show holders as links to their
application-access screens. Explicit Back to [role name] and browser Back preserve
origin/draft/position under shared save safeguards. Refresh holders and deletion
eligibility on return; confirm deletion and retain definition/audit history.
Application-maintained built-in roles cannot be deleted.

The [access mock](./.working/application-access-wireframe.html) illustrates role
selection and the [custom-role mock](./.working/custom-role-wireframe.html) illustrates
simple creation; neither is a permission catalogue. The access mock's older wording
about creation “from an application role” does not replace the accepted separate
Duplicate role action.

## State Patterns

These are approved behaviors, not evidence of rendered states. Every protected
surface rechecks current NGO and permission scope. Read/search/export cannot reveal
more than its destination permits. Loading and failed loads must not masquerade as
successful empty results. Detailed coverage gaps remain visible below.

| Surface group | Accepted state coverage | Remaining treatment to resolve |
|---|---|---|
| My Leave / balances / history | No pending/upcoming items; no history in selected year; explicit year bounds; required-response notice; own-data scope | Cold-load/error composition for balances and all history filters |
| Apply / details / lifecycle / acknowledgement | Saved/saving/failure, disconnected, expired session, stale/no access, field blocks, shortfall acknowledgement, submitted, rejection, withdrawal, cancellation/replacement | Complete upload-state visuals, part-day widgets and every lifecycle layout |
| Approvals / review / team availability | Empty versus filtered-empty queue; stale decision; failed/uncertain save; coverage and acknowledgement gates; no access | Rendered verification of shared loading and team-data failure treatment |
| Manager home / overview | Empty attention queue; no leave versus filtered-empty; overview load failure/Retry; missing coverage and correction follow-up | Dedicated deficit/escalation/override load/error details |
| Temporary assignment | Overlap conflict; pending transfer selection; expiry return eligibility failure; uncovered responsibilities remain flagged | Detailed termination/extension/concurrent-save layouts |
| Policy / entitlement / schedule / calendars | Current/draft/scheduled; inherited/override; impact review, invalid route, affected requests | Complete validation/loading and domain-specific presentations; shared confirmation recovery and stale-review rules apply |
| Adjustment / audit / reports | Required reason and review; audited before/after; inherited collection loading/empty/error/export feedback | Exact zero-results and export-failure treatment per report |
| Access / custom roles | Proposed changes, review; holders block deletion; effective authority can remain from other grants | Authoritative capability dependencies, concurrent changes and complete deletion states |
| Setup / notifications / shell | No assumed employees; unresolved tasks; empty notification inbox; shared access/session safeguards | Checklist failures/completion criteria, notification load failures and shared shell visuals |


### Empty approval queue

If no requests require the approver's action, show No requests need your approval.
Keep permitted team availability and access to My Leave available. If filters
produce no matches, show No requests match these filters with Clear filters.
Do not represent loading or a failed request as an empty successful result.

### Request changed during review

Stop an outdated action and show: This request has changed. Review the latest
version before continuing. Refresh the currently permitted details and status;
offer only actions valid for that state and the actor's current permissions.
Preserve any typed comment without automatically submitting it. For example, a
request withdrawn while an approver was reviewing it cannot subsequently be
approved from that stale view. If access is lost, use the no-access treatment
rather than revealing updated request data.

### Collection and supporting-panel feedback

Inherit shared [collection, refresh and export states](../../../../platform/EXPERIENCE.md#collections-refresh-and-export).
A loaded empty approval queue says You have no requests awaiting approval. A
filtered empty queue says No requests match these filters, with Clear filters.
Failed loading says We couldn’t load requests, with Retry and preserved filters.
Retained data after a failed refresh is marked as not refreshed, remains subject
to current access, and is revalidated before accepting actions. Export failure
keeps the report visible with Retry export.

Within approval review, failed team data says Team availability couldn’t be loaded;
it never implies nobody is away. Offer retry and do not independently block approval
unless an existing rule requires that information. Domain authorization, current
request checks and all other approval gates still apply.

### Administrative edit persistence and recovery

Balance adjustments, entitlement changes, schedules and roles inherit the shared
[administrative edit contract](../../../../platform/EXPERIENCE.md#administrative-edits-with-explicit-confirmation).
Edit → Review → Confirm applies the change only after confirmation. Keep input
while editing; ordinary departure with changes asks Keep editing or Discard changes.
Supported related-record navigation preserves the form for return. No separate
administrative saved-drafts system is required. Failed confirmations retain input;
uncertain outcomes are checked before retry. Concurrent changes require a refreshed
review. Employee leave-request autosave remains separate.

### Temporary connection loss

Keep entered text visible in the open form. Replace Draft saved in the persistent
save-status area beside the bottom actions with two lines: Connection lost / Your
latest changes aren't saved. We'll retry when you reconnect. Add a small status
icon with clear text; do not rely on a transient toast. Retry draft saving after
reconnection, and show Draft saved only after successful persistence. Previously
saved draft data remains intact.

Submission and approval require a connection and are not silently queued. Do not
promise newer unsaved changes will survive browser closure or refresh. Continue
checking current authorization and record versions when reconnecting.

### Session expiry while editing

Pause saves and submission and explain that sign-in is required. After successful
reauthentication, return the employee to their saved draft subject to current NGO
and request access. Say Your draft is saved only if the latest save succeeded.
Clearly warn about newer unsaved changes without promising they will survive
sign-in. No offline storage or browser-persistence mechanism is selected by this
experience rule; architecture must preserve privacy when implementing recovery.

### Request no longer accessible

Show: This request is no longer available to you. Your access may have changed.
Contact your organization administrator if you need help. Reveal no request
details, including stale details from a prior authorized view. Offer Back to My
Leave only if the user retains application access. Do not imply that a request
has been deleted when the actual condition is lack of current authorization.

### Revised unpaid amount needs employee acknowledgement

Lead with Your response is needed. Show the previously requested unpaid amount
and revised requested unpaid amount, followed by Changed by and the explanation.
Provide an explicit checkbox acknowledging the exact revised amount and an
Acknowledge action. Example: I acknowledge that 2 days are now requested as unpaid
leave. Keep Withdraw request available for eligible pending requests.

Acknowledgement satisfies the required employee response so approval can proceed;
it does not approve leave. Recheck the current amount before recording the response
and preserve the existing actor/reason/acknowledgement audit history.

### Change approved leave

Offer Change leave for authorized approved date/duration corrections. Prefill
replacement details from the original request, let the employee edit them, then
show the cancellation effects and replacement balance calculation together.
The final action is Cancel original and submit replacement. The replacement
starts a fresh approval cycle and remains linked to the original under
[ADR-0010](../../../../apps/leave/docs/architecture/decisions/0010-cancel-and-replace-approved-leave.md).

If validation fails, keep the original approved request intact and preserve entered
replacement details. Existing cancellation recalculation, authorization, history,
and exact unpaid-amount acknowledgement rules apply. The combined operation must
not leave a cancelled original merely because replacement validation failed;
architecture must define consistency and retry behavior before implementation.

### Rejected request and resubmission

Show the rejection reason prominently with Edit and resubmit. Open the request
form with previous details filled in, allowing the employee to correct them,
review the recalculated balance, and submit again. Retain the same request and
its history while starting a fresh approval cycle under
[ADR-0009](../../../../apps/leave/docs/architecture/decisions/0009-resubmit-rejected-request.md).
Prior decisions remain historical, not approvals of the revised submission.
Existing validation, permissions, and unpaid-amount acknowledgement still apply.

### Approved-leave cancellation confirmation

Identify the leave type and dates under Cancel this leave? Show the restored
amount, any applicable accrual correction or expiry effects, and resulting
available balance. Offer an expandable Why this adjustment? explanation. Omit
inapplicable correction rows but clearly surface any deficit or effect on other
requests; do not hide these consequences in the explanation disclosure.

Actions are Keep leave and Cancel leave. No additional approval is required for
cancellation. Use the authoritative cancellation recalculation and authorization
rules, not a simple restoration assumption. Example presentation: 2 days restored,
0.5 days deducted for accrual correction, resulting balance 8 days (given an
otherwise applicable starting balance of 6.5 days and no other effects). These are
illustrative values, not new entitlement rules.

### Pending-request withdrawal confirmation

For an eligible pending request, use a short confirmation dialog titled Withdraw
this request? Identify the leave type and dates and explain: This stops approval
and releases the balance reserved for this request. Actions are Keep request and
Withdraw request. Successful withdrawal shows Withdrawn and retains the request
in history, without another approval step. Existing current-state and permission
checks apply; the dialog must not imply withdrawal succeeded before confirmation
from the server.

### Missing configured approval route

If no eligible configured approval route exists, show “Your approval route needs
to be set up”, retain the saved draft, block submission and flag an authorized
manager. This differs from an applicant's missing approval coverage during their
absence: that request may be submitted but cannot finalize without valid coverage
or an authorized explained exception. Directional absence fallback uses the
configured policy and bounded temporary responsibilities, not an invented route.

### Submitted request

After confirmed submission, replace the form with request details in the same
desktop drawer; mobile retains its full-page presentation. Briefly show Request
submitted. Lead with leave type, dates, and current status, followed by requested
and paid amounts. Show Requested unpaid only when nonzero. Notes/documents and
approval history expand on demand under existing visibility rules. Show Withdraw
request for eligible pending requests; existing state and permission checks govern
the action. Place required employee responses prominently above the details.

Example: Annual leave · 12–13 Oct 2026, Awaiting approval, Requested 2 days,
Paid 2 days. Hide the zero unpaid row. Show Approved instead when authorized
automatic decisions completed approval. Do not reintroduce a prominent reference
number or next-approver name.

### Submission failure

Keep the request form open and preserve entered information. Show a plain-language
submission error near Submit and field-specific errors beside the relevant fields.
Offer Retry for a failed submission; when the result is uncertain, first check
whether it succeeded so retries cannot create duplicate requests or reservations.
Do not report success until confirmed or discard the draft because a response was
lost. Existing revalidation and exact unpaid-amount acknowledgement rules apply.

## Interaction Primitives

Click, tap and keyboard activate the same authorized action. Date-range controls
support manual/keyboard entry. Calculation disclosures work by click/tap/keyboard,
not hover alone. Timeline bars select details; dragging/resizing never edits leave.

Contextual tasks use a desktop right drawer and a mobile/narrow full page. Close,
Escape and Back use the saved/saving/failed-save rules above. Header Close has an
accessible name and can coexist with footer Close. Routine forms do not acquire an
extra review automatically; confirmed high-impact flows retain their approved
review. Long policy editing uses a dedicated page. Prototype preview dialogs do
not redefine that shared convention.

Mobile Filters stages changes: Apply commits/closes, Close/Back discards pending
edits, Reset changes the provisional defaults. Management tools is navigation and
opens its destination immediately. Return from a detail preserves dates, filters
and position; cross-record navigation uses shared return-to-origin safeguards.

## Accessibility Floor

Meet the source-required WCAG 2.2 AA target. This is a target, not a verified result.
Provide complete keyboard navigation, visible focus, labelled controls and errors,
text equivalents for status/holiday/non-working markers, and accessible date and
calculation disclosures. Shared modal focus/close behavior applies to drawers and
sheets; closing restores useful context. Maintain readable content and reachable
actions when zoomed or using a phone keyboard. No decision-critical text may be
hidden behind a fixed footer. Management-tool rows target at least 48px high as
approved; other final dimensions remain unresolved.

Inherit the shared [focus, validation and announcement rules](../../../../platform/EXPERIENCE.md#accessibility-floor).
After successful submission replaces the form, focus the request heading. Preserve
input/active field across drawer-to-page changes. Guide failed-submit focus to
associated field errors or their summary. Announce meaningful save failure/recovery,
displayed-period changes and newly required unpaid acknowledgement without stealing
focus or announcing every keystroke. History exposes the selected date visually
and programmatically, retaining useful return focus from its date details.

Visual contrast belongs in DESIGN.md. Test the assembled surfaces, focus order,
status announcements, screen-reader date navigation, zoom and touch behavior before
claiming compliance. No keyboard shortcut scheme, animation timing or offline
persistence mechanism is invented here.

## Responsive & Platform

| Desktop | Phone / narrow viewport |
|---|---|
| Contextual right drawer with background context | Full page with the same required information and actions |
| Policy summary/editor/review as dedicated pages | Dedicated pages with the same policy groups |
| Organization/team timeline with readable dates and fixed names/headings | Date-grouped list by default; overview retains Timeline/List choice |
| Twelve-month history overview | One-month navigation plus equivalent history list |
| Grouped collection toolbar, view toggle beside heading | Compact date/view controls and Filters sheet |
| Manager tools secondary column with divider | Management tools sheet above attention queue |
| Report selector beside filtered results | Compact report/results arrangement and filter sheet |
| Desktop drag/drop or Browse | Choose a file |

Responsive transitions are based on usable content, not approved numeric
breakpoints yet. Sample HTML widths, dates, people and calculations are illustrative.
Most references have structural/JavaScript checks only; browser, keyboard and
assistive-technology verification remains outstanding.

## Inspiration & Anti-patterns

The accepted direction is calm, practical and familiar. No external product was
chosen as a visual authority. Avoid repeated form summaries, obligatory wizards,
separate delegated-work or Drafts screens, a third organization calendar view,
colour-only status, quick queue approvals, implicit morning/afternoon positioning,
and repeated alerts for ordinary inherited information. A future shared personal
task inbox is deferred until another application needs it; notifications stay
separate from unresolved business actions.

## Key Flows

Names and examples below come from the accepted wireframes: Ana Matola, Sofia
Fernandes, João Pereira, Maria Santos and Joseph Chileshe Banda. They are illustrative
participants, not new personas or additional grants. Where a management operation
requires authority, its source-defined permission is a precondition. Flow names
map to the source catalogue in consolidation-coverage.md; sources define no UJ IDs.

### 1 — Leave application experience: Ana applies from My Leave

1. Ana opens My Leave in the active NGO, reads available balances and chooses Apply for leave; an existing saved draft resumes.
2. She chooses type, permitted duration and dates, then reads schedule-aware requested/paid/unpaid amounts and opens calculation details if needed.
3. She acknowledges the exact requested unpaid amount when required and adds the permitted note/document.
4. **Climax:** confirmed Submit request replaces the form with current request details; she sees Awaiting approval or an authorized automatic Approved result.

Failure / limits: A field or connection failure preserves entered data. Uncertain submission is checked before retry; an older draft refreshes rules beside affected fields.

### 2 — Employee workspace: Ana finds prior leave and manages a request

1. Ana opens My leave history, chooses a permitted previous year and switches Calendar/List without losing that year.
2. She selects a marked date/request and reads dates, type, duration, status and linked correction history.
3. **Climax:** the authorized detail gives her the appropriate lifecycle action: withdraw eligible pending leave, cancel approved leave with recalculated effects, Change leave through linked replacement, or Edit and resubmit a rejection.

Failure / limits: Unavailable years stay disabled; no records produces an honest empty state. Validation failure on replacement preserves the approved original; access loss hides details.

### 3 — Configurable approval workflows: João decides assigned work

1. João opens Approvals and selects an authorized request from the longest-waiting queue; temporary work identifies whom he acts for.
2. He reads exceptions, allocation, employee explanation, permitted documents and Team availability. A separate balance-override decision requires its own permission and reason.
3. He checks current-step, self-approval, coverage and employee-acknowledgement gates; an enabled absence fallback labels an omitted supervisor step explicitly.
4. **Climax:** his confirmed approval records the actual actor and returns to the queue; an intermediate step retains reservation, while valid final approval completes the request. Rejection instead requires an employee-visible reason.

Failure / limits: A changed request stops the decision and retains the comment. Uncertain saves are checked before retry. Missing acknowledgement/coverage never silently becomes approval.

### 3a — Balance override: Sofia revises Ana’s allocation

1. Sofia opens the shortfall in Ana’s existing pending request with the required override permission, chooses a permitted allocation and records a reason.
2. She reviews and confirms the revised split. In this example an authorized correction changes 3 paid + 2 unpaid days to 2 paid + 3 unpaid days; a new request cannot displace Ana’s existing reservation.
3. Ana receives a notification and opens Your response is needed on My Leave. She sees the previous/revised split, Sofia’s name and explanation, and acknowledges the exact current 3 unpaid days.
4. **Climax:** the request continues through its remaining approvals. João sees Waiting for employee acknowledgement until the response is recorded; acknowledgement never substitutes for his decision.

Failure / limits: Recheck the unpaid amount before recording acknowledgement; a stale amount cannot satisfy the current requirement. Keep eligible withdrawal available. No renewed acknowledgement is needed when unpaid leave stays the same or decreases. An uncertain confirmation follows the shared recovery rules; no separate workspace is introduced.

### 4 — Request lifecycle: Sofia corrects Ana’s returned-early leave

1. Sofia opens authorized Correct leave for Ana’s approved 7–11 September request and enters 7–9 September as the replacement.
2. She reviews original/replacement dates, restoration and new reservation, and the required employee-visible reason.
3. **Climax:** Cancel original and submit replacement preserves linked history and starts fresh approval. Ana opens the minimal notification to see the actor, dates, reason and current balance effect.

Failure / limits: Validation failure leaves the original intact. A later replacement rejection keeps the original cancelled and creates Correction needs follow-up. An increased requested unpaid amount sends Ana to explicit revised-amount acknowledgement; the returned-early example needs none.

### 5 — Leave Manager workspace: Sofia follows up an attention item

1. Sofia opens Manage Leave and sees escalated approvals, deficits and affected requests; permitted management tools remain independently reachable.
2. She opens Joseph’s illustrative five-day deficit, reads cause/history and chooses Keep open, authorized source correction, explicit adjustment, or recorded handling without adjustment.
3. **Climax:** the recorded outcome and employee-visible explanation distinguish review completion from any separately authorized balance change. Escalated-request reassignment similarly requires its own permission and reason.

Failure / limits: No attention items leaves tools/overview available. Review does not erase a deficit, imply salary recovery, or confer approval authority.

### 6 — Calendars and privacy: Sofia checks organization availability

1. Sofia opens Organization overview on the current month and searches/filter dates within her scope.
2. She compares approved/pending bars, stacked partial days, employee non-working dates and location-aware holidays; phone view groups entries by date.
3. **Climax:** selecting an entry exposes its full range and authorized detail, and closing restores the same dates, filters and scroll position.

Failure / limits: No leave differs from no filter matches or failed loading. Search does not silently enable Show all employees; bar length never states the entitlement deduction.

### 7 — Approval cover and planned absence: Sofia appoints João for Maria

1. Sofia selects an active same-NGO temporary approver, original approver, dates and exact responsibilities, checking overlaps and absence.
2. She chooses pending requests to transfer, records the reason and reviews conditional expiry return; special supervisor-absence authority must be explicit.
3. **Climax:** Confirm temporary approver grants only the appointed scope/dates without a permanent-role prerequisite, and sends minimal appointment notifications. João sees ordinary Approvals with Acting for Maria.

Failure / limits: An unavailable original at expiry leaves work pending and flagged; authority does not auto-extend. Early termination requires reason and destination preview, may leave coverage unresolved, and never cancels already-approved leave.

### 8 — Leave types and policy management: Sofia schedules a change

1. Sofia opens the current policy summary and enters the dedicated editor, moving directly among the four sections.
2. In Approval she configures supervisor first and a selected second approver when needed; optional directional absence behavior appears beside the final step.
3. She reviews changed values, effective date, employees with overrides and affected existing requests.
4. **Climax:** Publish policy version confirms Policy scheduled for the future date while the current summary remains Current.

Failure / limits: Invalid/missing routes require attention; publishing never silently replaces recorded routes or recalculates existing requests. Complete editor failure presentation remains open.

### 9 — Balance ledger and accrual: Sofia makes a one-off adjustment

1. Sofia opens Ana’s balance adjustment, chooses Add or Deduct, amount and effective date, and records a required reason.
2. She reviews the current/resulting balance and existing-request consequences using Review adjustment.
3. **Climax:** Confirm adjustment records a new ledger entry and minimal notification; Ana can open authorized amount/date/result/actor/reason details.

Failure / limits: Incorrect prior adjustments are corrected by another explained adjustment, retaining history and the same review. Increased requested unpaid amounts still require the existing acknowledgement.

### 10 — Employee entitlement overrides: Sofia changes recurring entitlement

1. Sofia opens Edit employee entitlement for Ana and chooses policy inheritance or employee-specific entitlement.
2. She supplies the recurring amount when applicable, next leave-period start and reason; the quiet one-off link remains separate.
3. **Climax:** Review change explains the before/after entitlement and affected requests before confirmation; the recurring choice continues until explicitly changed.

Failure / limits: No automatic end-date or current-balance reset is implied. Unexpected consequences remain visible; detailed save/concurrency presentation remains open.

### 11 — Jurisdictions and workplace calendars: Sofia restores Ana’s profile value

1. Sofia opens Ana’s schedule, sees one assigned Maputo office profile and the marked Friday override, and proposes Use profile.
2. She reviews the effective date, reason and request effects; standard-day conversion remains separate from Friday hours.
3. She reaches the associated holiday calendar to inspect configured names/dates and authorized changes.
4. **Climax:** review makes inherited versus explicitly overridden values and preserved historical calculations clear before any authorized change.

Failure / limits: Profile location/team suggestions do not silently reassign Ana. Calendar examples are organization closures, not official holiday facts; full profile/calendar failure states remain open.

### 12 — Reports and exports: Sofia exports matching balances

1. Sofia opens Reports, chooses the balances report and sets its relevant date and permitted filters.
2. She reads available/reserved values and their explanation.
3. **Climax:** authorized Export CSV uses the same query, NGO and privacy boundaries for all matching results, with an audit record.

Failure / limits: Loading/empty/export feedback inherit the planned shared collection pattern; report-specific copy and calculation/query contracts remain delivery details.

### 13 — Audit and operational administration: Sofia traces an adjustment

1. Sofia opens Audit history and searches employee/action/date within her scope.
2. She expands Ana’s adjustment event to read when, who, what changed and why.
3. **Climax:** permitted before/after values and the linked affected record explain the change without granting separate sensitive-document access.

Failure / limits: An inaccessible detail/link must not expose stale private fields. Detailed load/filter errors remain open.

### 14 — Identity, NGO context, and onboarding: Ana follows a notification

1. Ana uses the shared signed-in shell with an active authorized NGO; her preferred language is retained across NGO changes.
2. She opens the notification bell, reads the minimal current-NGO item and selects its authorized request link.
3. **Climax:** the destination displays current permitted detail and any unresolved response separately from notification read state.

Failure / limits: Expired sign-in pauses saves/actions; reauthentication returns to a saved draft only with current access. Membership/access loss removes protected details; unseen changes are never claimed saved.

### 15 — Setup and migration: Sofia checks client configuration

1. Sofia follows the authorized non-sequential setup checklist to normal work-profile/calendar, policy, employee and route settings. Consultant email approval is not tracked in this checklist.
2. Where migration applies, the consultant validates the exact batch and source balance-date/future-request conventions and sends the generated reconciliation report to the authorized client contact by email.
3. **Climax:** after client approval evidence and export-to-cutover reconciliation, the authorized import process applies that exact approved batch under the migration runbook; no in-app confirmation screen is added.

Failure / limits: Changed data requires a revised report and renewed approval; validation/row errors and duplicate protection prevent an unreviewed apply. Operational commands/rollback and full setup layout remain open.

### 16 — Permissions: Ana’s application access and a custom role

1. Ana’s authorized organization administrator opens her application access and reviews business capabilities behind role names.
2. In advanced settings the administrator creates a named app-specific role, or uses the separate Duplicate role action; role creation itself assigns nobody.
3. **Climax:** assignment or assigned-role edits show capability changes and affected holders before confirmation. Deletion requires removing every holder first, with links out and a preserved return to the role.

Failure / limits: Another role or valid appointment may retain equivalent authorization. Built-ins cannot be deleted; stale holder/effective-grant checks and the final permission catalogue remain contract work. The administrator is an existing source role, not a newly named persona.

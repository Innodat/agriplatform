---
title: Leave Experience Design
status: draft
created: 2026-09-15
updated: 2026-09-15
sources:
  - ../../../../platform/EXPERIENCE.md
  - ../../../../apps/leave/docs/features.md
  - ../../../../apps/leave/docs/architecture/decisions/README.md
---

## Foundation

Inherit common interaction conventions from
[platform EXPERIENCE.md](../../../../platform/EXPERIENCE.md), currently a draft.
Leave's authoritative product rules remain in the
[feature specification](../../../../apps/leave/docs/features.md). Screen-by-screen
coaching is in progress; this is not a finalized experience contract.

## Component Patterns

### Organization leave overview

Keep employee names fixed on the left and date headings fixed at the top while
scrolling the timeline. Mobile retains the default date-grouped list so sideways
timeline navigation is not required.

Show a small continuation marker at either bar edge when the request extends
beyond the visible date range. Selecting the entry shows its full date range;
the viewport boundary must not imply the request starts or ends there.

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

### Notification inbox

The bell opens a compact panel with newest notifications first, a clear unread
marker, and Mark all as read for the active NGO only. Display only the approved
minimal employee/date/status information and link. Selecting an item opens its
request under current authorization checks. Empty state: No notifications yet.
Retain per-user read state, NGO selector count privacy, and the distinction between
read notifications and unresolved business actions. This is a shared-shell pattern
to implement through the planned common notification contract.

### Work profiles and employee schedule defaults

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

### Leave Manager audit history

Provide a searchable chronological list showing when, who, what changed, and why,
with filters for employee, action, and date range. Opening an entry reveals only
permitted before/after details and a link to the affected record. Apply active-NGO
authorization and sensitive-field permissions to list, search, details, and linked
records; audit access must not bypass medical-document authorization.

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

### Holiday calendars

List calendars by location, showing each calendar's name and year. Opening a
calendar shows its holiday dates and names, with add/edit actions only for
authorized actors. Assign calendars to employees through work location or schedule
so one NGO can support staff in multiple countries. Preserve existing effective
configuration, historical request calculations, and authorization rules. The
employee schedule defaults now use the work-profile pattern described above.

### One-off balance adjustment

Show employee and leave type, Add or Deduct followed by an amount, effective date,
and mandatory reason. Preview current balance and resulting balance plus any
affected pending requests, then offer Confirm adjustment. Preserve the resulting
ledger entry in the employee's balance history. Existing balance-adjustment
permission, audit, and explained unpaid-increase acknowledgement rules apply.
Keep this separate from a continuing entitlement override.

### Employee entitlement override

Show policy entitlement alongside proposed employee entitlement, with effective
dates and a mandatory reason. Preview balance and accrual effects before
confirmation. Clearly distinguish a continuing entitlement change from a one-off
balance adjustment. Apply existing configuration authorization, effective dating,
and audit rules; do not silently rewrite historical grants or requests.

### Leave-type and policy configuration

Start with a leave-type list showing name, current policy, and active/archived
status. Selecting a type opens configuration grouped into Entitlement, Request
rules, Approval, and Documents & privacy. Keep advanced settings in expandable
sections rather than displaying every rule at once. Preserve existing configuration
permissions, policy versioning, and archive semantics; these groups are navigation
and presentation, not new domain boundaries.

Before publishing policy changes, show the changed settings and effective date
in a review step, followed by Publish policy version. Unpublished edits remain a
draft so configuration can be completed before taking effect. Explain that
historical requests retain their recorded policy and existing requests are not
silently recalculated. Apply existing effective-dated versioning and configuration
permissions; publishing is not a retroactive migration of request history.

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

### Leave Manager escalated approvals

Queue rows show employee, leave dates, current assigned approver, and time awaiting
action. Opening an item shows the request and escalation history. Show Reassign
approver only with existing rerouting permission; require a reason and preserve
earlier decisions. Apply the active NGO scope and existing permission checks to
both display and action. Escalation alone grants no approval or rerouting authority.

### Approver queue

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

### Approval review

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

### Balance-override review

Show requested amount, available paid balance, and shortfall together, with unpaid
leave as the default proposal. An actor with override permission can accept that
proposal or specify an authorized alternative allocation, with a mandatory reason.
Preview the resulting paid/unpaid split before confirmation. Preserve existing
authorization for each funding source and employee acknowledgement requirements.
Keep this decision separate from ordinary approval; permission to approve a
request alone does not grant override authority.

### My leave history


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
Exact marker shapes and date-detail layout remain to be visualized.

The List view shows dates, leave type, duration, and status, with leave-type and
status filters. Default to most recent leave dates first. Selecting a row opens
the request details. On phones, group each request in a compact stacked row:
dates and status on the first line, type and duration below, with subtle separators
instead of heavy card borders or shadows. Avoid a horizontally scrolling wide table.

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

## State Patterns

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

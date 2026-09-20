---
name: Leave
description: Calm, practical responsive Leave design inheriting approved Agriplatform conventions.
status: final
created: 2026-09-15
updated: 2026-09-20
sources:
  - ../../../../platform/DESIGN.md
  - ../../../../apps/leave/docs/features.md
  - ../../../../apps/leave/docs/architecture/decisions/README.md
colors: {}
typography: {}
rounded: {}
spacing: {}
components: {}
---

## Brand & Style

Calm, practical and low-friction. Balances and primary actions have clear hierarchy;
secondary explanations expand on demand. Required responses, exceptions and
paid/unpaid consequences remain visible. Inherit the draft
[platform DESIGN.md](../../../../platform/DESIGN.md) by reference. Use the planned shadcn-based platform primitives and Lucide icons with the
approved shared visual tokens. This contract defines the Leave MVP design; it
does not claim the shared wrappers or the application are implemented.

## Colors

Neutral backgrounds, restrained colour and subtle decorative borders. One accent is
reserved for primary actions; statuses/warnings rely on text and familiar cues as
well as appearance. Requested unpaid uses neutral emphasis, not error colouring.
Approved timeline bars are softly filled; awaiting approval uses dashed outlines,
with checkmark/clock icons and a legend. Employee non-working dates use very light
row-specific shading; a location-specific holiday never implies everyone is off.

**Selected light-mode palette: Neutral + Quiet lagoon.** MVP supports light mode only;
dark mode is deferred. Continue using shared semantic tokens so a later dark theme
can be validated across complete screens and states. No theme switch is needed.
Inherit the named colour
tokens in [platform DESIGN.md](../../../../platform/DESIGN.md#colors): page, surface,
text, text-secondary, border-subtle, border-control, primary, on-primary, focus and
emphasis. Leave has no colour overrides, so its local colors map remains empty.
The saturated accent is for primary actions; subtle lagoon-tinted emphasis may
identify selection and unpaid information using distinct borders/labels.

[Selected-palette preview with softer drawer dimming](./.working/quiet-lagoon-selected.html)
is a historical palette study of the desktop drawer and mobile form. Approved
overlay and shadow values now inherit {components.task-drawer}. Text and input
contrast stays unchanged. The measured primary pair is 6.62:1, secondary text on
white is 6.10:1 and secondary text on emphasis is 5.26:1. Browser rendering remains
unverified; numerical checks alone do not establish compliance.

Earlier explorations remain comparison references, not competing approved themes:
[original ocean options](./.working/ocean-palette-comparison.html),
[grayscale alternatives](./.working/neutral-palette-comparison.html), and
[neutral-base colour states](./.working/neutral-ocean-states-comparison.html).
Dark mode is deferred. Additional rendered interaction states still need verification; approved
corner/marker/icon defaults and drawer separation inherit the shared tokens.

## Typography

Inherit the selected [platform type scale](../../../../platform/DESIGN.md#typography):
system fonts; body/input/action text 1rem, labels/secondary text 0.875rem, headings
1.5rem and balance figures 2rem. Form controls have 2.75rem desktop and 3rem mobile
minimum heights, growing when needed. Local typography maps remain empty because
Leave has no overrides. Keep readable secondary details, bold unpaid label/amount,
and wrapping employee names.

[Combined selected design](./mockups/selected-design.html) is the current visual
reference. The [earlier scale comparison](./.working/typography-scale-comparison.html)
remains historical context: the user selected Proposed. The reported missing
Leave type remains present as the first form field; the comparison now resets
form scroll on switching, and the selected reference explicitly separates fixed
header/footer from the scrollable form. Browser reproduction of that reported
visibility issue remains outstanding; no field has been removed from the design.
Zoom, translations and responsive behavior still require rendered verification.

## Layout & Spacing

Generous padding and vertical rhythm keep forms readable without crowding phones.
A contextual task uses a sufficiently wide desktop right drawer; mobile/narrow
screens use a full page. Required information belongs inside the task, not only in
the dimmed background. Long policy editing uses a dedicated page with direct access
to its four groups. Short confirmations use shared dialog conventions.

Use available desktop width for compact purpose-grouped collection controls; move
mobile filters into the shared bottom sheet. Keep sheet header/footer reachable
around scrollable fields. Short related form fields can pair when readable and
stack when necessary. Inherit the selected platform defaults: 560px standard drawer,
32px desktop and 20px mobile horizontal padding, 24px form sections/vertical padding
and 8px label gaps. Determine content-driven responsive thresholds during rendered
validation; add width variants only when a delivered surface needs them.

The user selected Suggested in the
[layout comparison](./.working/layout-scale-comparison.html). The
[combined selected-design reference](./mockups/selected-design.html) includes the
approved palette, typography and starting layout scale. Comparison-board widths
are not approved responsive breakpoints; real zoom/reflow still needs validation.

## Elevation & Depth

Use subtle dividers and neutral surface distinction. Employee-history list rows
use separators without heavy card borders or shadows. Sheets keep the background
recognizable but inactive. Inherit the approved subtle divider, backdrop and shadow from
{components.task-drawer}; this does not add a broader elevation scale.

## Shapes

Use familiar controls. Status distinctions combine neutral shape, border and text;
partial-day markers stack separately when needed. At timeline continuation edges,
remove the border and retain the chevron. Inherit 6px button/input corners, 8px card/small-dialog corners, 4px marker
corners, 1px borders and Lucide icons from the shared visual tokens. Retain
non-colour status distinctions and accessible icon names.

Approved composition references are indexed in the [handoff inventory](./mockups/README.md).
Historical comparisons remain separately labelled; written contracts govern any
prototype simplifications.

## Components

The names below match EXPERIENCE.md Component Patterns. Shared task drawers/pages,
short confirmation dialogs, disclosures, toolbars, filter sheets, uploaders, save
status and return-to-origin navigation inherit the platform spines; these rows give
Leave-specific composition. States not pictured remain behavioral requirements.

| Component / composite | Approved visual rules | Reference |
|---|---|---|
| My Leave and balance explanations | Primary Apply action above clear per-type balances; secondary pending/upcoming groups and ledger disclosures. Required responses near the top. | [Layout](./mockups/apply-wireframe.html) |
| Apply for leave | Type then duration/date controls, balance breakdown, notes/documents. Generous readable single form; no separate unpaid panel. | [Layout](./mockups/apply-wireframe.html) |
| Request balance explanation | Requested → Paid → Requested unpaid when relevant; bold unpaid label/amount and subtle neutral row shading, acknowledgement immediately below. Standard-day equivalents with explicit hours disclosure. | [Layout](./mockups/apply-wireframe.html) |
| Notes and supporting documents | Labels state optional/required; uploader below balance, with readable upload/save/verification status. | [Layout](./mockups/apply-wireframe.html) |
| Request action area | Close and primary Submit request remain visible in a footer that occupies its own space; persistent save status nearby. Header Close icon has a name. | [Layout](./mockups/apply-wireframe.html) |
| Agreed wireframe refinements | Single full-day range control and single-date part-day variants; muted secondary text stays readable; no hover-only calculation. | [Layout](./mockups/apply-wireframe.html) |
| My leave history | Twelve-month desktop overview, compact mobile month and companion List. Quiet markers with selected-date detail. Stacked mobile rows put dates/status above type/duration. Corrected label is separate from approval status. | [Layout](./mockups/employee-history-wireframe.html) |
| Approver queue | Employee/date lead each row, then type/duration/wait time and exception flags; small Acting for label for temporary work. Actions live in review. | [Layout](./mockups/approval-review-wireframe.html) |
| Approval review | Details/allocation/explanation precede visible Team availability, permitted documents/history and comment/actions. Exceptions must remain visible. | [Layout](./mockups/approval-review-wireframe.html) |
| Team availability during approval | Compact employee/date timeline with requested-range emphasis; date-grouped mobile list. Partial-day markers never imply times. | [Layout](./mockups/approval-review-wireframe.html) |
| Balance-override review | Requested, available and shortfall grouped together; alternative allocation and reason distinct from ordinary approval. Approved layout keeps alternatives expandable and amount editable. | [Preview](./mockups/balance-override-preview.html) |
| Leave Manager home | Needs attention is primary. Overview action beside title; secondary desktop tools column with subtle divider. Mobile tools sheet opens above the queue. | [Layout](./mockups/leave-manager-home-wireframe.html) |
| Organization leave overview | Use available width; view toggle at heading right, grouped compact toolbar and adjacent secondary legend. Fixed employee names/date headers, readable horizontally scrollable columns. | [Layout](./mockups/organization-overview-wireframe.html) |
| Leave Manager escalated approvals | Employee/date/current approver/wait time identify rows. Temporary appointment groups people/dates, explicit responsibilities, pending transfers, reason and expiry explanation. | [Layout](./mockups/temporary-approver-wireframe.html) |
| Apply on behalf | Employee picker and recording actor precede familiar leave fields; carry reason, allocation and actual approval consequence into review. | [Preview](./mockups/apply-on-behalf-preview.html) |
| Administrative leave correction | Original and replacement comparison, separate restored deduction/new reservation, reason and consequences before the explicit action. | [Layout](./mockups/leave-correction-wireframe.html) |
| Balance-deficit review | Employee/type, deficit and cause precede before/after history, chosen outcome and explanation. Approved detail layout uses the standard drawer. | [Preview](./mockups/balance-deficit-preview.html) |
| One-off balance adjustment | Employee/type, direction/amount/date/reason, balance preview and existing-request impact; concise review repeats only decision-critical values. | [Layout](./mockups/balance-adjustment-wireframe.html) |
| Employee entitlement override | Source choices lead; short related fields may pair responsively. Quiet helper text explains recurrence/next period and one-off link. No repeated What changes box in the edit form. Comparison belongs in review. | [Layout](./mockups/employee-entitlement-wireframe.html) |
| Leave-type and policy configuration | Readable Current summary in four groups; Scheduled notice and date link. Dedicated editor and change review with old/new values, affected employees and request exceptions. Ordered workflow steps show absence option beside final step. | [Layout](./mockups/policy-review-wireframe.html) |
| Work profiles and employee schedule defaults | Assigned profile first, inherited values grouped, employee override visibly labelled beside its field and reversible Use profile action. | [Layout](./mockups/employee-schedule-wireframe.html) |
| Holiday calendars | Location/name/year list beside selected calendar and dated names; edit preview keeps usage and affected-request consequences nearby. | [Layout](./mockups/holiday-calendars-wireframe.html) |
| Reports | Report selector beside filtered results; heading/date/export context, grouped filters and readable results. Compact stacked results on phones. | [Layout](./mockups/reports-wireframe.html) |
| Leave Manager audit history | Chronological rows emphasize time/action/actor; expandable reason and before/after details with related-record link. | [Layout](./mockups/audit-history-wireframe.html) |
| Employee Leave settings | Shared identity header; Employment & approval, Work schedule and Leave entitlement groups; focused edits and separate balance/history actions. | [Preview](./mockups/employee-leave-settings-preview.html) |
| Setup and migration | Checklist links to normal settings; unresolved employee details appear only when data exists. Consultant report/email uses documentation, not a new confirmation UI. | [Preview](./mockups/setup-checklist-preview.html); derived readiness states specified in EXPERIENCE |
| Notification inbox | Compact newest-first panel; clear unread marker, minimal permitted context and active-NGO Mark all as read. | Approved shared written pattern; rendering to verify during delivery |
| Application access and custom roles | Application groups contain role names/descriptions and expandable capabilities. Advanced creation uses name/description/plain-language choices; separate Duplicate action. Reviews distinguish changes and holders. | [Layout](./mockups/custom-role-wireframe.html) |

The [approval workflow study](./mockups/approval-workflow-wireframe.html) isolates
the policy editor's ordered one/two-step section; the
[application-access study](./mockups/application-access-wireframe.html) shows
person-centric role selection before the advanced custom-role editor. These are
partial layout references with illustrative data and mostly disabled writes.
Historical labels or preview dialogs in mocks do not override current spine rules.

The approved [on-behalf preview](./mockups/apply-on-behalf-preview.html) places
employee selection and recording-actor attribution before familiar request fields,
with the reason and actual approval consequence carried into review. The approved
[custom-role lifecycle preview](./mockups/custom-role-lifecycle-preview.html)
shows capability additions/removals, affected holders, contextual person navigation
and separately confirmed deletion only when unassigned. Both are illustrative
references; disabled writes and static checks do not demonstrate runtime behavior.

The [policy editor preview](./mockups/policy-editor-preview.html) applies the selected
palette/type scale to a dedicated page with four directly reachable sections,
expandable advanced rules, effective date/reason and a separate changed-values
review. The user approved this layout on 20 September 2026. Conditional fields illustrate the approved reveal rules; sample calculations and
people lookup are partial and do not define the final policy schema.

The [setup checklist preview](./mockups/setup-checklist-preview.html) uses spacious
divider-separated rows, factual status labels and expandable issues. Desktop places
status beside the title; mobile wraps status beneath it. Existing employee issues
link to named contexts; a new-NGO scenario avoids invented affected people. The user
approved this layout with consultant status and the standard opening-balances row
removed. No completion percentage or extra activation action is added.

The [employee Leave-settings preview](./mockups/employee-leave-settings-preview.html)
uses shared identity in the header and three spacious groups of Leave-specific
settings, with explicit inherited/overridden values and separate balance actions.
Focused edit examples use the selected drawer dimensions and mobile full-width
presentation. The user approved this layout on 20 September 2026; its mobile modal simulation does not
establish production routing or focus behavior.

The [work-profile management preview](./mockups/work-profiles-preview.html) shows
a spacious list and the selected 560px edit/review drawer. Review groups changed
values, effective date/reason, inherited employee effects, retained overrides and
requests needing attention. Mobile uses a full-width task composition with stacked
actions where needed. The user approved this layout on 20 September 2026;
browser behavior remains unverified.

The [balance explanation preview](./mockups/balance-explanation-preview.html) uses
the selected contextual drawer/mobile full-width composition. A large available
amount precedes a compact breakdown, reserved-request link and divider-separated
expandable history entries. Positive/negative amounts use signs and words rather
than status colours. The user approved this layout on 20 September 2026;
runtime/browser checks remain open.

## Do's and Don'ts

| Do | Don't |
|---|---|
| Give balances, actual exceptions and required actions prominence | Hide unpaid amounts or acknowledgement in a disclosure |
| Keep routine helpers quiet; place comparisons in high-impact review | Repeat form contents in a What changes box |
| Use explicit text, borders and accessible status labels | Spend the primary-action accent on every status |
| Preserve dates, filters and position through contextual detail | Require the background page to explain a decision |
| Pair short fields only while readable | Force a complex policy form into a narrow drawer |
| Validate assembled responsive and accessible behavior | Treat sample CSS or structural checks as visual approval |

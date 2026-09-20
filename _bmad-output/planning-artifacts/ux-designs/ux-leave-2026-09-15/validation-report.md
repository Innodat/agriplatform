# Validation Report — Leave

- **DESIGN.md:** [Draft](./DESIGN.md)
- **EXPERIENCE.md:** [Draft](./EXPERIENCE.md)
- **Run at:** 2026-09-18T05:36:03+00:00

## Overall verdict

The accepted interaction direction is coherent and well preserved: the employee, approval and management journeys fit together, named composites agree between the spines, and references resolve. The pair is still a planning draft rather than a complete implementation contract: visual tokens, some operational journeys and adverse states remain deliberately open, and recurring-entitlement effective dates need one explicit product decision. These are predominantly acknowledged handoff gaps, not regressions or reasons to reopen approved preferences.

The accessibility review adds three medium and one low interaction-contract gaps: focus transitions, consequential status announcements, validation-error navigation, and selected-date state. These call for shared behavior clarifications rather than a redesign. This is a static document and prototype review, not rendered-browser testing or an accessibility compliance assessment.

Severity describes the risk of treating these drafts as implementation-ready. The critical token finding is an acknowledged handoff blocker, not a regression or a defect in a deployed application. No design source or approved business rule was changed by this review.

## Category verdicts

- Flow coverage — thin
- Token completeness — broken
- Component coverage — adequate
- State coverage — thin
- Visual reference coverage — strong
- Bloat & overspecification — adequate
- Inheritance discipline — thin
- Shape fit — strong

## Findings by severity

### Critical (1)

**UX-R02 [Token completeness] — There is no executable visual token contract**

Leave DESIGN.md lines 11–15 and Colors lines 34–41; platform/DESIGN.md Layout & Spacing and Open Visual Decisions. Surface, foreground, primary-action, border and focus combinations have no committed values or resolvable inherited tokens. This is explicitly disclosed and intentional for the draft, but implementations would otherwise invent incompatible palettes and cannot verify the promised contrast.

Fix: approve a shared starting theme and committed color pairs, map Leave to it, and record typography/spacing/radius and responsive decisions needed by its components. Preserve the draft/readiness gate until then; do not silently adopt mock CSS or add a dark-mode palette unless dark mode is selected.

### High (3)

**UX-R01 [Flow coverage] — High-impact management journeys lack a complete decision path**

EXPERIENCE.md Information Architecture, lines 51–65, and Key Flows 3, 5, 11 and 15 acknowledge dedicated balance-override/deficit, full employment/setup and profile/configuration gaps. In particular, the balance override is mentioned inside ordinary approval, but the authorized actor's allocation choice, employee acknowledgement handoff and return to the blocked approval are not demonstrated as one complete journey. The employee future-date balance projection is listed in IA but has no end-to-end flow.

Fix: close the balance-override/revised-acknowledgement and projection journeys, then use the existing coverage inventory to identify which remaining admin actions need dedicated layouts versus established form patterns. Do not create one flow per ledger calculation or a client migration-confirmation page.

**UX-R04 [State coverage] — Administrative editing and confirmation lack a committed persistence/recovery contract**

EXPERIENCE.md State Patterns lines 855–859; Key Flows 8–11 and 16; platform/EXPERIENCE.md Open Implementation Details. The shared Close/Back rules explicitly describe autosaved drafts, while policy, entitlement, schedule and custom-role editors have review/confirm actions without establishing whether their unconfirmed edits persist, what happens when leaving, or how a failed/uncertain confirmation and concurrent change are recovered. A consumer could accidentally equate saving editor input with publishing or granting access.

Fix: define one reusable admin edit → review → confirm state pattern with explicit draft persistence and close semantics, stale-review invalidation and confirmed/unknown-result recovery. Apply domain-specific consequences without changing the separate employee draft policy.

**UX-R07 [Inheritance discipline] — “Next leave-period start” is a default in the source but reads as a fixed input in the walkthrough**

features.md §5, lines 240–250, permits effective-dated changes and defaults to next period; EXPERIENCE.md Employee entitlement override lines 637–659 repeats that default but labels the field “Next leave-period start”; Key Flow 10 step 2 supplies the next period without stating whether alternatives are possible. consolidation-coverage.md explicitly identifies non-default midperiod starts as unresolved. This is a known decision gap, not evidence that either alternative was approved.

Fix: obtain an explicit choice between period-boundary-only recurring changes and an authorized non-default effective date. Then align the field, review and source. If non-default dates remain possible, define their prospective grant/accrual effects without silently resetting current balances or rewriting history.

### Medium (5)

**UX-R03 [Component coverage] — Date and duration controls remain a composition gap**

DESIGN.md Apply for leave and Agreed wireframe refinements; EXPERIENCE.md Apply for leave, Agreed wireframe refinements and Interaction Primitives. A unified range picker, single-date partial-day controls and a duration input are named, but their complete composition and invalid/incomplete range behavior are not assigned to an approved shared control or documented as an application delta. Manual/keyboard entry is required, which is a useful floor, but does not resolve the input/error behavior.

Fix: select or document the shared control behavior, then specify only Leave-specific date/duration constraints and examples. Keep the agreed duration-only partial-day model; do not introduce exact times.

**UX-R05 [State coverage] — Collection and secondary-surface fallback treatment is not yet a real inherited contract**

EXPERIENCE.md State Patterns lines 851–860 and Reports lines 760–765; platform/EXPERIENCE.md State Patterns. The Leave matrix describes some loading/empty/error/export feedback as inherited, while the platform says applications still specify it and Reports correctly says shared behavior is used “when established.” This is an unresolved dependency, not an implemented-service defect.

Fix: establish a small shared loading / empty / filtered-empty / failed-load / retry / failed-export pattern and identify application-specific cases, including team-availability failure inside a decision and notification failure. Never turn a failed fetch into a truthful-looking empty result.

**A11Y-01 [Accessibility] — Focus after replacing a form or changing its presentation is unspecified**

**Evidence:** [Submitted request](./EXPERIENCE.md#submitted-request) replaces the
application form with request details in the same drawer. [Interaction Primitives](./EXPERIENCE.md#interaction-primitives)
and [Responsive & Platform](./EXPERIENCE.md#responsive--platform) switch contextual
tasks between a modal drawer and a full page. Shared
[Closing autosaved forms](../../../../platform/EXPERIENCE.md#closing-autosaved-forms)
requires containment and restoration on close, but does not cover these transitions.

**Consequence:** Submission can remove the focused Submit button without putting
focus on the new request context. A resize/zoom transition can leave modal trapping
or an inactive background attached to a full-page layout. This is a missing shared
contract, not an assertion about a current runtime implementation.

Fix: Specify that successful form replacement focuses the resulting
request heading, and full-page task entry announces its heading through deliberate
focus. During a responsive transition, preserve the active field if it survives;
otherwise focus the task heading. Apply modal containment/inactive-background rules
only while the surface is modal. Continue using the approved save/leave safeguards.
One shared paragraph and targeted delivery checks are sufficient.

**A11Y-02 [Accessibility] — Dynamic feedback has visible wording but no agreed announcement behavior**

**Evidence:** [Temporary connection loss](./EXPERIENCE.md#temporary-connection-loss)
puts an important failure beside the footer, while [Apply for leave](./EXPERIENCE.md#apply-for-leave)
updates calculated balances as fields change. [Accessibility Floor](./EXPERIENCE.md#accessibility-floor)
calls for testing status announcements but does not say which consequential changes
must be announced without moving focus. In the history study, `#year-label` is a
polite live region but `#month-name` is not: moving between months in the same year
changes visible month content without an equivalent update announcement. Selected
date details do explicitly receive focus, so that interaction is already covered
by the prototype.

**Consequence:** A person editing near the top can miss failed draft saving or a
new unpaid acknowledgement requirement; a screen-reader user can miss the mobile
month change. Announcing every autosave keystroke instead would also be disruptive.

Fix: Add one shared status rule: announce meaningful save failure/recovery,
completed submission, changed displayed period, and newly required unpaid response
without unsolicited focus movement. Announce settled calculations rather than each
keystroke. Preserve the persistent visible feedback. A polite status mechanism is
appropriate for routine results; actual blocking failures need timely discoverable
feedback. Component implementation can select the exact mechanism.

**A11Y-03 [Accessibility] — Submission-error placement is specified, but the route to errors is not**

**Evidence:** [Submission failure](./EXPERIENCE.md#submission-failure) requires an
error near Submit and field-specific errors. Shared
[Accessibility Floor](../../../../platform/EXPERIENCE.md#accessibility-floor)
requires announced validation states, but neither specifies focus after a blocked
submit or links between the summary and invalid fields. The custom-role study's
`#review-role` handler focuses an empty role name and silently returns; it renders
no explanation and does not mark that field required.

**Consequence:** Errors in earlier scrollable content may be hard to find from a
persistent footer. Merely moving to a blank input does not explain what prevented
Review. The mock is illustrative; its behavior should not become the reusable
validation pattern.

Fix: Define the shared blocked-submit behavior: preserve values, provide
plain-language field errors programmatically associated with their controls, and
focus an error summary with links or the first invalid field when there is only
one error. A server-wide failure remains near the action and is announced. The
custom-role example can then illustrate this with a required Role name message.
No extra review screen is needed.

### Low (2)

**UX-R06 [Bloat & overspecification] — Repeated policy-publication rules increase maintenance drift**

EXPERIENCE.md Leave-type and policy configuration, especially lines 687–712, repeats changed values/effective-date/impact review and protection of existing requests; similar brief repetitions occur across Components, State Patterns and Key Flows.

Fix: keep each detailed rule in one canonical component/state section and retain short linked walkthrough summaries. Preserve meaningful failure paths and source links; do not shorten away approval/acknowledgement safeguards.

**A11Y-04 [Accessibility] — History day selection has no nonvisual selected-state contract**

**Evidence:** [My leave history](./EXPERIENCE.md#my-leave-history) defines selecting
a date to reveal its requests. In the [history study](./.working/employee-history-wireframe.html),
selected days receive a `.selected` class, but their accessible label/state does
not reflect that selection. The code correctly focuses the details region after
selection; this is not a claim that its details are inaccessible. The specification
has no requirement covering the selected date when returning to the calendar.

**Consequence:** A keyboard or screen-reader user returning from details may not
know which date the retained detail region represents without rereading it.

Fix: Include the full selected date in the detail heading (as the mock
already does) and expose the retained selected date through the chosen calendar
control's appropriate accessible state. Preserve a useful return focus target.
Do not invent a custom calendar keyboard system here: verify the selected platform
control and its List alternative during delivery.

## Mechanical evidence

- All 64 checked local Markdown links across the Leave and platform spines resolve.
- All 17 working HTML wireframes are referenced; all 26 composite names match between the Leave spines.
- No browser, screen-reader, zoom, touch, or complete palette contrast test was performed.

## Suggested next action

Roll the shared interaction clarifications into the draft documents, then resolve recurring entitlement effective dates with the user. Complete the remaining balance journeys and shared theme before implementation handoff. Keep the drafts and readiness gates open.

## Reviewer files

- [Consistency/completeness](./review-rubric.md)
- [Accessibility](./review-accessibility.md)

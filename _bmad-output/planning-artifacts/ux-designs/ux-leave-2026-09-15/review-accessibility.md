---
name: Leave UX accessibility and responsive interaction review
status: review-findings
reviewed: 2026-09-18
scope: Static design-contract and representative-wireframe review
---

## Result and limits

Three medium findings and one low finding; no critical or high findings established.
These are gaps to resolve before adopting the drafts as a production interaction
contract, not evidence that the existing layout preferences are unsuitable.
No browser, keyboard, assistive-technology, zoom, touch, or contrast-palette test was
performed. No compliance result is claimed. This review cites repository evidence;
it does not add a new interpretation of an external standard.

Reviewed Leave DESIGN.md and EXPERIENCE.md, platform equivalents, and the Apply,
Organization overview, Employee history, and Custom-role HTML studies. The shared
modal focus containment/restoration, equivalent history List, accessible status
labels, manual date entry, persistent save feedback, and inactive modal background
are already sound requirements. Keep them. Missing theme tokens and unrendered
states are explicitly acknowledged by the drafts and are not rediscovered defects.

## Findings

### A11Y-01 — Medium — Focus after replacing a form or changing its presentation is unspecified

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

**Small fix:** Specify that successful form replacement focuses the resulting
request heading, and full-page task entry announces its heading through deliberate
focus. During a responsive transition, preserve the active field if it survives;
otherwise focus the task heading. Apply modal containment/inactive-background rules
only while the surface is modal. Continue using the approved save/leave safeguards.
One shared paragraph and targeted delivery checks are sufficient.

### A11Y-02 — Medium — Dynamic feedback has visible wording but no agreed announcement behavior

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

**Small fix:** Add one shared status rule: announce meaningful save failure/recovery,
completed submission, changed displayed period, and newly required unpaid response
without unsolicited focus movement. Announce settled calculations rather than each
keystroke. Preserve the persistent visible feedback. A polite status mechanism is
appropriate for routine results; actual blocking failures need timely discoverable
feedback. Component implementation can select the exact mechanism.

### A11Y-03 — Medium — Submission-error placement is specified, but the route to errors is not

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

**Small fix:** Define the shared blocked-submit behavior: preserve values, provide
plain-language field errors programmatically associated with their controls, and
focus an error summary with links or the first invalid field when there is only
one error. A server-wide failure remains near the action and is announced. The
custom-role example can then illustrate this with a required Role name message.
No extra review screen is needed.

### A11Y-04 — Low — History day selection has no nonvisual selected-state contract

**Evidence:** [My leave history](./EXPERIENCE.md#my-leave-history) defines selecting
a date to reveal its requests. In the [history study](./.working/employee-history-wireframe.html),
selected days receive a `.selected` class, but their accessible label/state does
not reflect that selection. The code correctly focuses the details region after
selection; this is not a claim that its details are inaccessible. The specification
has no requirement covering the selected date when returning to the calendar.

**Consequence:** A keyboard or screen-reader user returning from details may not
know which date the retained detail region represents without rereading it.

**Small fix:** Include the full selected date in the detail heading (as the mock
already does) and expose the retained selected date through the chosen calendar
control's appropriate accessible state. Preserve a useful return focus target.
Do not invent a custom calendar keyboard system here: verify the selected platform
control and its List alternative during delivery.

## Explicit readiness items, not additional findings

- **Theme and target-size verification:** DESIGN.md deliberately leaves tokens
  empty. Its one measured muted-text pair does not cover other surfaces, borders,
  focus, disabled controls, or status patterns. EXPERIENCE.md only fixes the
  approved management rows at 48px. Define and test the shared controls' eventual
  sizing/contrast contract during theme selection; do not promote mock values.
- **Responsive coverage:** Apply is a static desktop/phone composition with fixed
  illustrative canvases and noninteractive field boxes. Organization overview bars
  are static `span` elements and its timeline scroll container is not a proven
  keyboard interaction. The spine explicitly requires selectable accessible bars
  and a mobile List. These limitations are prototype coverage, not separate
  production defects. Delivery validation should exercise the chosen control at
  narrow widths and zoom, long employee names, translated labels, an open phone
  keyboard, and fixed footers/headers, while retaining all required actions.

## Suggested disposition

Resolve A11Y-01 through A11Y-03 once in the shared interaction contract and reference
that contract from Leave. Resolve A11Y-04 in the history behavior. Keep the existing
calm visual direction, drawers/full pages, bottom sheets, and calendar/List choices.
Do not claim that these text clarifications replace rendered accessibility testing.

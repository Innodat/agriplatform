---
name: Leave UX accessibility and responsive interaction review
status: review-findings
reviewed: 2026-09-20
scope: Final design-contract review and static inspection of representative approved references
---

## Result and limits

**Two medium and one low finding; no critical or high finding established.** All
three are prototype divergences from an already documented accessibility contract,
not new product requirements or demonstrated production failures. The previous
review's four design omissions are addressed in the shared and Leave contracts.
Resolve or explicitly annotate the divergences before treating these references as
interaction examples for implementation.

Reviewed both Leave spines and both platform spines, with static inspection of the
history, organization-overview, policy-editor, Apply-on-behalf, custom-role
lifecycle, revised-unpaid acknowledgement and allocation-override references.
Checks included accessible names, error relationships, scripted focus, dynamic
feedback, date/history semantics, responsive CSS and selected token contrast.
Other linked previews supplied context; this is not an exhaustive control audit of
every historical comparison artifact.

No browser, screen-reader, keyboard, touch, zoom or mobile-keyboard test ran. Native
`dialog` use and syntactically valid JavaScript do not establish assembled behavior.
The parent reports all 26 executable inline scripts across 35 HTML references pass
`node --check`; that is syntax evidence only. No WCAG conformance claim is made.
Light-mode-only MVP and spine-only coverage of routine states are approved choices;
neither is a finding or a waiver of delivery accessibility checks.

## Findings

### UX-A01 — Medium — Field errors in current previews are not associated with their inputs

**Classification:** Prototype divergence; shared design rule already exists.

**Evidence:** `platform/EXPERIENCE.md:321` requires programmatic field-error
association. In [.working/apply-on-behalf-preview.html](./.working/apply-on-behalf-preview.html)
line 6, `#reason` is required and the separate `#error` has `role="alert"`, but there
is no error-description relationship. Its validation handler on line 13 shows the
message and focuses the input. The same pattern occurs in
[.working/balance-override-preview.html](./.working/balance-override-preview.html)
lines 7 and 16. In
[.working/custom-role-lifecycle-preview.html](./.working/custom-role-lifecycle-preview.html)
lines 5–6 and 14, the blank-name error is remote from `#name`, with no associated
error or invalid-state update.

**Consequence:** An alert may announce the message once, but revisiting the field
does not reliably expose why it failed. This particularly matters in a long,
scrolling role editor. Moving focus and having a visible message are useful but do
not implement the promised field relationship.

**Fix:** Give field-specific errors stable IDs, associate them with the relevant
input, and expose/clear invalid state on validation. Keep general deletion/workflow
errors separate from the name field; do not attach a multipurpose error container
to every input. Preserve current focus and input-retention behavior. W3C provides
an applicable implementation technique using
[aria-invalid and associated error descriptions](https://www.w3.org/WAI/WCAG22/Techniques/aria/ARIA21.html).

### UX-A02 — Medium — Allocation changes update the acknowledgement consequence silently

**Classification:** Prototype divergence; no new acknowledgement rule needed.

**Evidence:** [.working/balance-override-preview.html](./.working/balance-override-preview.html)
line 7 places the revised acknowledgement consequence in plain `#effect` text.
`update()` on line 12 changes that text and the allocation amounts; the radio and
amount-input handlers on line 15 invoke it without a status announcement. The
amount's description references only `amount-help`. This differs from shared
`platform/EXPERIENCE.md:324` and Leave `EXPERIENCE.md:1275`, which require meaningful
consequence updates without unsolicited focus changes or per-keystroke noise.

**Consequence:** A screen-reader user changing the discretionary grant can miss
whether Ana must acknowledge a new unpaid amount. The later review repeats the
consequence, so it is not wholly inaccessible; the immediate decision feedback is
unequal to the visible experience.

**Fix:** Announce a concise settled allocation and acknowledgement consequence when
the choice or valid committed amount changes. Keep the persistent visible summary,
do not move focus, and do not announce every number-field keystroke or initial
render. Use a suitable status mechanism and test actual announcement timing. This
matches the intent of [W3C status-message guidance](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html).

### UX-A03 — Low — The retained history reference still omits the now-agreed month and selection semantics

**Classification:** Older prototype drift, not an unresolved spine decision.

**Evidence:** [.working/employee-history-wireframe.html](./.working/employee-history-wireframe.html)
line 5 gives `#year-label` a polite live region but not `#month-name`; lines 42 and
53 update the mobile month within the same year without an equivalent announced
period. Line 36 adds only `.selected` to a chosen day; its accessible name/state
never identifies selection. `EXPERIENCE.md:1275` explicitly requires period
announcements and programmatic selected-date state.

**Consequence:** The retained example can teach an implementer the superseded
behavior. A user may miss a same-year month change or be unable to identify the
selected date when returning from details. The existing full-date detail heading,
focus move on line 24 and List alternative reduce the impact.

**Fix:** Bring this reference into line with the spine or label its remaining
accessibility limitations beside the reference. Announce the changed visible
period, expose the selected day through semantics appropriate to the chosen
control, and preserve useful return focus. Do not add grid roles without also
implementing their keyboard contract.

## Contrast verification

Recomputed the selected `platform/DESIGN.md:8` tokens using the sRGB relative
luminance contrast formula. Results below are rounded for presentation, not for
threshold decisions. W3C defines the relevant
[text contrast](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
and [non-text contrast](https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html)
requirements; these pair calculations do not certify assembled controls.

| Pair | Ratio |
|---|---:|
| White / primary `#17685C` | 6.62:1 |
| Secondary `#626262` / white | 6.10:1 |
| Secondary / page `#F5F5F5` | 5.59:1 |
| Secondary / emphasis `#E8F0ED` | 5.26:1 |
| Control border `#858585` / white | 3.69:1 |
| Control border / page | 3.38:1 |
| Control border / emphasis | 3.18:1 |
| Focus `#294E47` / white | 9.23:1 |
| Focus / emphasis | 7.96:1 |
| Subtle border `#DEDEDE` / white | 1.35:1 |

The documented primary/secondary figures are correct. The subtle border is suitable
for decoration; it must not become the sole necessary control or state indicator.
This is not a request to darken every separator. Interaction states, native-control
rendering, focus-ring adjacency and forced-colour behavior still need verification.

## Sound decisions and delivery checks

- **Focus and keyboard:** Shared modal containment, inactive backgrounds and return
  focus are specified; mobile full pages have a different focus model. The revised
  submission flow explicitly restores useful focus on My Leave and announces
  success (`EXPERIENCE.md:1272`). Test real routing, related-person return, Escape,
  confirmations and removal of focused actions after concurrent changes.
- **Errors and dynamic states:** Shared error-summary/field association, meaningful
  status announcements and retained input are adequate design requirements. Upload
  progress/failure/required-file blockers inherit them; there is no need to invent
  another upload screen. Test per-file names and cancellation/retry feedback.
- **Calendars and timelines:** Manual date entry, full accessible status labels,
  non-colour status distinctions, selectable rather than draggable bars, and a
  mobile List alternative are specified (`EXPERIENCE.md:143`, `:460`, `:481`). Older
  static bars are layout illustrations, not verified keyboard widgets. Test the
  chosen real date control and keep date/employee context available to assistive
  technology; avoid duplicating a custom calendar interaction unnecessarily.
- **Mobile, enlargement and targets:** Shared relative typography and growing
  44px/48px minimum controls are specified (`platform/DESIGN.md:79`). Several
  illustrative files still use pixel typography and nowrap buttons. Keep the
  spine authoritative; test enlarged text, narrow reflow, translated action labels,
  fixed footers, an open mobile keyboard and touch targets in actual components.
  Do not infer successful reflow from media queries alone.
- **Notifications and partial loading:** Minimal notification payloads, read versus
  unresolved-action distinction, local retries and retained loaded sections are
  sensible. Verify accessible unread names, load/error announcements and focus on
  actual destinations without forcing more steps after submission.

## Disposition

The approved visual direction and workflow choices need no redesign on the evidence
reviewed. Correct the three reference gaps or explicitly quarantine them before
handoff; retain browser and assistive-technology verification as delivery work.
This review does not authorize Leave implementation or close Phase 1 readiness.

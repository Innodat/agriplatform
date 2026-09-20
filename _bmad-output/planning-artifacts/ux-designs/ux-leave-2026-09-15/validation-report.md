# Validation Report — Leave

- **DESIGN.md:** [Leave design](./DESIGN.md)
- **EXPERIENCE.md:** [Leave experience](./EXPERIENCE.md)
- **Run at:** 2026-09-20T16:11:06+00:00
- **Scope:** final completeness/consistency and accessibility source review; supersedes the earlier consolidated review snapshot.

Subsequent corrections are tracked in [review-resolution.md](./review-resolution.md).
The findings below remain the original review snapshot.

## Current disposition — 20 September 2026

The two original **thin** ratings below are historical. Their underlying findings
have since been addressed:

- **Token completeness (UX-R08):** approved radii, borders, Lucide icons, marker
  corners and drawer separation now have an owning source in
  [shared DESIGN.md](../../../../platform/DESIGN.md).
- **Visual reference coverage (UX-R11):** 28 approved references were promoted to
  `mockups/`, with a [handoff inventory](./mockups/README.md); seven comparison
  studies remain historical.

Both Leave design contracts are now final. These are verified source corrections,
not newly assigned rubric ratings or browser/accessibility certification. The
original review and verdicts below are retained for provenance; see the
[resolution log](./review-resolution.md) for all finding dispositions.

## Original review synthesis

The approved employee, approval and management journeys now form a coherent design contract. The earlier major design gaps are addressed; remaining findings concern a few handoff decisions, ambiguous approval-gating wording and document organization. The design documents should remain draft until these are resolved; runtime contracts and browser verification remain separate delivery work.

Accessibility review found three prototype differences from already adequate written requirements: field-error associations, allocation-consequence announcements and retained history semantics. No redesign of the approved visual direction or workflows is indicated. This was static source review, not browser or assistive-technology testing.

**Findings: 0 critical · 0 high · 6 medium · 3 low.** No overall grade is assigned. These counts do not establish implementation readiness.

## Category verdicts

- Flow coverage — **adequate**
- Token completeness — **thin**
- Component coverage — **adequate**
- State coverage — **adequate**
- Visual reference coverage — **thin**
- Bloat & overspecification — **adequate**
- Inheritance discipline — **adequate**
- Shape fit — **strong**

## Findings by severity

### Critical (0)

None established by these reviews.

### High (0)

None established by these reviews.

### Medium (6)

#### UX-R08 — Remaining visual defaults need an owning source
**Token completeness** · Locations: `DESIGN.md:98; platform/DESIGN.md:102`

Corner radii, icon family, marker geometry and drawer shadow/overlay remain uncommitted, with no selected component theme to inherit them from.

**Fix:** Choose a small shared default set or a concrete approved primitive/theme. Do not adopt incidental prototype CSS wholesale; dark mode remains deferred.

#### UX-R10 — Define setup checklist status criteria
**State coverage** · Locations: `EXPERIENCE.md:926; EXPERIENCE.md:1032`

Ready, Needs review and Not started are illustrated, but the source of truth for readiness is not fully defined for the three setup groups.

**Fix:** Specify concise status predicates and unavailable-assessment treatment using existing settings/review evidence. Do not add client-email approval UI, a new activation action or manual mark-complete flow.

#### UX-R11 — Promote approved references for handoff
**Visual reference coverage** · Locations: `DESIGN.md:46; EXPERIENCE.md:42; .working/`

All 35 HTML studies remain under .working, without a stable keeper inventory separating approved references from historical comparisons.

**Fix:** Promote approved keepers to mockups/ or wireframes/, update links, and document historical studies and accepted written-pattern coverage. No additional routine mockups are requested.

#### UX-R13 — Clarify final versus intermediate approval gating
**Inheritance discipline** · Locations: `EXPERIENCE.md:413; EXPERIENCE.md:1351; apps/leave/docs/features.md:714; ADR-0032`

Some renewed-acknowledgement wording could block all remaining approval decisions, while accepted product rules specifically gate final approval.

**Fix:** Use final approval cannot complete consistently and reference the accepted finalization rule for intermediate steps. A broader restriction would need a new explicit product decision.

#### UX-A01 — Associate prototype validation errors with fields
**Accessibility** · Locations: `.working/apply-on-behalf-preview.html:6; .working/balance-override-preview.html:7; .working/custom-role-lifecycle-preview.html:5`

Visible alerts and focus moves do not establish a programmatic error relationship or invalid state for the affected input. The shared design contract already requires this.

**Fix:** Give field errors stable IDs, associate them with their inputs, and expose/clear invalid state. Keep general workflow errors separate from field errors.

#### UX-A02 — Announce settled allocation consequences
**Accessibility** · Locations: `.working/balance-override-preview.html:7; .working/balance-override-preview.html:12`

Changing the discretionary grant updates unpaid allocation and acknowledgement consequences visibly but without the meaningful status announcement already required by the contract.

**Fix:** Announce a concise settled allocation and acknowledgement consequence after a valid committed change, without moving focus or announcing each keystroke. Verify real announcement timing.


### Low (3)

#### UX-R09 — Index the approved Apply on behalf composition
**Component coverage** · Locations: `DESIGN.md:118; DESIGN.md:154; EXPERIENCE.md:641`

The approved layout exists in prose but is missing from the visual component table.

**Fix:** Add the matching component-table row and existing preview link; avoid repeating the narrative.

#### UX-R12 — Remove obsolete open-status wording
**Bloat & overspecification** · Locations: `DESIGN.md:57; DESIGN.md:143; platform/DESIGN.md:75; platform/EXPERIENCE.md:366`

Some text still calls dark mode, standard drawer dimensions and setup visuals unresolved, or does not distinguish approved written-pattern coverage from missing layouts. Policy review wording is repeated.

**Fix:** Consolidate current status in the IA/state inventory and keep history in the log. Retain only the actual outstanding validation or architecture work.

#### UX-A03 — Align retained history semantics with the contract
**Accessibility** · Locations: `.working/employee-history-wireframe.html:5; .working/employee-history-wireframe.html:36`

The older history reference announces the year but not same-year mobile month changes, and marks selection only with a CSS class.

**Fix:** Announce the visible period and expose selected-date semantics appropriate to the chosen control, or explicitly label these reference limitations. Preserve return focus; do not add grid roles without their keyboard behavior.

## Mechanical evidence and limits

- All 110 local Markdown file links across the Leave/shared spine pair resolve.
- All 26 executable inline prototype scripts across 35 HTML references pass `node --check`; this checks syntax only.
- All 35 working HTML studies are linked from at least one spine; none are promoted yet.
- Selected palette contrast pairs were recalculated and match the documented values; see the accessibility review for the measured pairs and W3C source links.
- No browser, screen-reader, keyboard, touch, zoom or mobile-keyboard verification ran.
- No approved design documents or prototypes were changed as part of this review. Documents remain draft; Phase 1 readiness is still required before implementation.

## Suggested update order

1. Align approval-gating wording with ADR-0032 and define setup-status predicates.
2. Resolve the remaining shared visual defaults without reopening approved layouts.
3. Correct or explicitly annotate prototype accessibility differences.
4. Refresh document status wording, complete the component index and promote approved references.

## Reviewer files

- [Completeness and consistency](./review-rubric.md)
- [Accessibility](./review-accessibility.md)

The reviewer reports retain the full evidence and line citations for this source snapshot. This report does not silently resolve their findings.

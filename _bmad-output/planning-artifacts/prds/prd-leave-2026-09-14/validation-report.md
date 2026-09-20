# Validation Report — Leave Tracker Functional Specification

- **PRD:** [Authoritative features.md](../../../../apps/leave/docs/features.md)
- **Rubric:** [Standard requirements-quality review](./review-rubric.md)
- **Run at:** 2026-09-20T16:54:23+00:00
- **Grade:** Excellent
- **Scope:** resumed standard quality review; no additional reviewer lens or new product specification.

Subsequent decisions and corrections: [resolution log](./review-resolution.md).
The findings below remain the original review snapshot.

## Current disposition — 20 September 2026

Requirements validation and approved finding dispositions are complete for architecture and story planning. R3 and R9 are resolved by ADR-0089 and ADR-0088; R10 is corrected; R6 has approved owners and decision gates. Numerical operational targets and their verification remain downstream work. This does not authorize implementation. See the [resolution log](./review-resolution.md).

## Original review verdict

The specification now provides a coherent and substantially testable product baseline: the previous major calculation, lifecycle and privacy ambiguities have been resolved through explicit rules, examples and linked decisions. It supports architecture and story planning, with one remaining product handoff clarification for unpaid on-behalf requests, a narrowly bounded expiry-date decision, and operational acceptance targets to settle before their affected readiness gates. The approved scope and UX do not need redesign.

**Current findings: 0 critical, 0 high, 3 medium, 1 low.** Findings are counted once under their primary dimension. Prior findings: six resolved, two partially resolved; none remain open in their original breadth.

The grade evaluates the specification’s usefulness for planning. It does not close the remaining findings or authorize implementation.

## Dimension verdicts

- Decision-readiness — adequate
- Substance over theater — strong
- Strategic coherence — strong
- Done-ness clarity — adequate
- Scope honesty — strong
- Downstream usability — adequate
- Shape fit — strong

## Findings by severity

### Critical (0)

None established by this review.

### High (0)

None established by this review.

### Medium (3)

#### R3 — Remaining carry-over month arithmetic needs an accepted outcome
**Done-ness clarity** — §6, `features.md:642–647`; ADR-0085, Consequences; `implementation-plan.md:494`

The specification now resolves the original broad calculation gap, but explicitly says “month-end/leap-day anniversary arithmetic requires deterministic delivery examples.” “Three months from 1 January” does not determine the last usable day for a period starting on 31 January or 29 February. Date-library behavior could produce different employee entitlements.

**Fix:** Before the affected calculation story passes readiness, record the chosen month-addition/clamping rule and a compact month-end/leap-day acceptance table, preserving inclusive expiry and never extending an existing expiry. This is the already acknowledged narrow product/calculation decision, not a request to revisit the approved accrual model.

#### R6 — Operational acceptance targets still lack bounded ownership and decision gates
**Done-ness clarity** — Non-functional requirements, `features.md:1992–2004`; implementation plan Phases 3, 9 and 10; finalized UX Responsive & Platform

“Short-lived signed content operations,” “actionable alerts,” “Tested backups, restoration” and “Performance targets agreed before release testing” still do not provide repeatable bounds. Mobile/keyboard journeys and visual behavior are much clearer now, but supported browser coverage and operational targets are not supplied by those UX contracts. Broad team ownership and eventual test tasks do not state who agrees each target and when the dependent architecture/story can be accepted.

**Fix:** Assign the responsible architecture, security, operations and product decision owners (roles suffice), and record gates for signed-operation lifetime, recovery objectives/rehearsal outcomes, critical alert conditions, supported browser coverage, and latency/workload targets. Let architecture and delivery supply those values and link them back; do not invent numerical targets in this review or block unrelated product planning on them.

#### R9 — Initial unpaid acknowledgement has no defined on-behalf handoff
**Done-ness clarity** — §7, `features.md:1074–1092`; §10 automatic on-behalf decisions; UX EXPERIENCE “Apply on behalf,” lines 651–665 and Key Flow 4a

Ordinary submission requires acknowledgement of the exact unpaid amount “before submission.” The on-behalf UX explicitly says its illustrated request is fully funded and leaves “employee unpaid acknowledgement” to existing requirements, while also keeping the manager's work separate from the employee's own draft. The later-increase response flow starts from an existing pending request and therefore does not determine how Ana acknowledges an initial two-day unpaid amount in Sofia's not-yet-submitted request. Implementers could either accept Sofia's checkbox as Ana's consent, prevent a supported on-behalf use case, or invent a new submission exception.

**Fix:** Agree who acknowledges, when that occurs relative to manager submission, and how the employee reaches the exact version/amount without changing their own saved draft. Add an acceptance example for an initially unpaid on-behalf request, including a submitter who owns the sole approval step and an amount that changes before acknowledgement. Preserve attribution, employee protection and independent approval authority; do not infer that on-behalf permission includes employee acknowledgement.


### Low (1)

#### R10 — Request-page inventory retains superseded input/action wording
**Downstream usability** — §7, `features.md:1128–1139`

“Accessible date and time inputs” and “Save draft and submit actions” can be extracted as requirements for exact-time fields and an explicit Save draft button. The same specification and ADR-0074/0075 instead require date plus duration without exact times, automatic draft saving, and Close.

**Fix:** Update this inventory to name accessible date/duration controls and truthful autosave with Close/Submit. Keep the accepted ADRs unchanged; this requires no additional product choice.


## Prior finding disposition

| Prior ID | Current disposition | Evidence / remaining work |
|---|---|---|
| R1 | Resolved | Explicit on-behalf permission, attribution/reason and independent assigned-step approval rules |
| R2 | Resolved | Observable employee history/balance tasks, funding comprehension flows, refine/retest requirement; pilot execution remains delivery |
| R3 | Partially resolved | Extensive calculation rules/examples accepted; only acknowledged month-end carry-over expiry outcomes remain in this finding |
| R4 | Resolved | Required steps, automatic decisions, final consumption, same-request resubmission and linked cancellation/replacement specified |
| R5 | Resolved | Deterministic role/channel visibility and allowed/denied API/document examples |
| R6 | Partially resolved | Mobile/accessibility behavior elaborated; operational bounds/owners/gates still needed |
| R7 | Resolved | English/date format named; Portuguese readiness versus translation delivery separated |
| R8 | Resolved | Finalized named cross-role UX journeys and failure handoffs |

New findings are R9 (medium) and R10 (low). Current dimension judgments: Decision-readiness adequate; Substance over theater strong; Strategic coherence strong; Done-ness clarity adequate; Scope honesty strong; Downstream usability adequate; Shape fit strong.

## Mechanical notes

- **Source freshness:** `features.md` still says Last updated 2026-09-14 although it includes later ADRs and approved September 20 decisions. Refresh that metadata on the next authorized source edit; do not read it as evidence that later decisions are absent.
- **Links and identifiers:** Parent validation found all 96 local file-link targets in `features.md` present; numbered feature headings remain 1–20. There is no FR/UJ/SM ID scheme to validate. Requirement-level story/test references should retain existing section and ADR anchors.
- **Terminology and navigation:** NGO/organization and request/application are intelligible aliases. A short alias note or subsection anchors would help extraction from the large §6, but this is optional organization work rather than another product blocker.
- **Assumptions:** No formal inline assumption/index scheme exists, so no roundtrip defect is asserted. Explicit prose deferrals and tracker gates govern the remaining decisions.
- **Verification boundary:** Document review only. No product, UX, ADR, code or tests were changed by this reviewer. Structural mock checks do not establish browser or assistive-technology compliance. Architecture, stories and implementation readiness remain pending.

## Review and context files

- [Standard quality rubric](./review-rubric.md)
- [Source reconciliation context](./revalidation-context.md)

No requirements, accepted ADRs or UX contracts were changed in this validation run. The next update can reconcile stale wording and track the remaining decisions without creating a competing PRD.

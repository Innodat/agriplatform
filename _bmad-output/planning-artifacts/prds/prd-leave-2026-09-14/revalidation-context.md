# Leave PRD revalidation context — 20 September 2026

This is source extraction for the standard PRD revalidation, not an independent
review, a findings closure decision, or an implementation-readiness assessment.
It maps the 14 September review to subsequent recorded product decisions and the
completed UX handoff. The reviewer must assess current sources independently.
No product source or accepted ADR was changed in this extraction.

## Source authority and chronology

- Authoritative requirements: `apps/leave/docs/features.md`; delivery gates:
  `apps/leave/docs/implementation-plan.md`.
- Accepted decisions and supersession chain:
  `apps/leave/docs/architecture/decisions/README.md` (currently through ADR-0087).
  Older accepted records remain historical; follow linked superseding decisions.
- Original findings: this workspace's `validation-report.md`. Its Fair grade,
  three high, four medium and one low findings describe the 14 September snapshot.
- This workspace's `.memlog.md` records the subsequent coached decisions through
  ADR-0073. Its earlier statements that specific issues remain open describe that
  moment, not necessarily the present state.
- Current UX contracts:
  `_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/DESIGN.md` and
  `EXPERIENCE.md`. Read `handoff-coverage.md`, `review-resolution.md`, and
  `mockups/README.md` alongside them. They record final UX handoff, 28 promoted
  references, accepted written-pattern coverage and resolved design findings.
  This does not assert browser/assistive-technology compliance or Phase 1 readiness.
- Shared visual/interaction contracts: `platform/DESIGN.md` and
  `platform/EXPERIENCE.md`; generic runtime implementation is not thereby claimed.

## Prior finding map

| Prior ID | Later source evidence | Extraction disposition for revalidation |
|---|---|---|
| R1 — on-behalf scope qualifier | Features Permissions now lists `leave.admin.on_behalf` as a separate permission. Sections 6, 10, 11 and 17 give reason, attribution, scope, automatic assigned-step decisions and correction limits. ADRs 0007/0008, 0053 and 0082 qualify the original baseline; UX has an approved on-behalf journey/reference. | The obsolete “if later approved” uncertainty appears reconciled. Preserve the distinction between submitting for someone and approval authority. |
| R2 — observable employee-understanding pilot | Features UX requirements now name pilot tasks: find last year's leave and identify per-type available balances. Worked acceptance includes distinguishing historical/future/pending leave, available/reserved amounts, ledger explanations and request-date paid/unpaid effects. It explicitly says implement UX before pilot testing, refine observed confusion and retest. ADRs 0062 and 0084 narrow projection to Apply. | Tasks and observable behavior are now present. These excerpts do not establish an agreed representative cohort, success threshold or observation protocol; don't silently infer a pilot pass or invent metrics. |
| R3 — calculation consequences | Features §6 now contains schedules (annual upfront, monthly start/end, manual), calendar-day/no proration, one final whole-minute rounding, employment-date correction, carry-over and inclusive expiry, cap/headroom, cancellation recalculation, period basis, work timezone, date-by-date projection and worked reservation examples. ADRs 0019–0049, 0083 and 0085 supply decisions. | The original absence of supported choices and worked outcomes is substantially elaborated. Deterministic same-expiry allocation tie-breaking is explicitly deferred before the allocation story; period-relative expiry month-end/leap arithmetic is a tracked readiness item. These should not be confused with unanswered choices about whether proration/carry-over exist. |
| R4 — lifecycle paths | Zero-step policies were deliberately removed by ADR-0007; explicit authorized automatic decisions remain. ADR-0008 covers later-step acceptance before the first step. Features §§10–11, State models and ADRs 0009/0010 specify same-request rejected resubmission, linked replacement for approved corrections, no extra approval for cancellation, retained intermediate reservation and consumption on final approval. | Original contradictory paths now have substantive approved rules and examples. Do not demand zero-step behavior from the original report. UX clarification preserves ADR-0032: renewed unpaid acknowledgement blocks final approval; otherwise-authorized intermediate decisions may proceed. Architecture still owns transaction/concurrency mechanics. |
| R5 — privacy visibility | Features Permissions, Attachments, Notifications and Calendars/privacy define owner/assigned-approver/Leave-Manager access; colleagues see Unavailable or Part-day absence for every leave type. Notes, comments, metadata and indirect type-filter/icon/export/API disclosure are addressed. ADRs 0011–0018 and 0074 provide the evolution. Notifications contain minimal name/date/status/link data; document permission remains separate. | A deterministic role/channel basis and allow/deny examples have replaced the broad intent. Revalidation should assess current coverage, not reopen the approved approver right to sensitive types and employee notes. |
| R6 — measurable release-quality bounds | Features still lists short-lived signed operations, actionable alerts, tested restore/rollback and performance targets agreed before release testing. UX now specifies mobile workflows, control dimensions, accessible focus/errors/announcements, and content-driven responsive adaptation. Handoff explicitly leaves rendered browser/AT verification open. | UX behavior is more concrete, but the extracted sources do not settle signed-operation lifetime, restore/recovery objectives, alert thresholds, workload/response targets or supported-browser coverage. Keep the original requirement for owners and bounded gates visible; do not fabricate operational numbers or call these validated. |
| R7 — unspecified MVP locale | Features UX requirements and ADRs 0059–0061 specify English, dates such as 15 Sep 2026, user language preference with English fallback, and Portuguese next for Mozambique and Angola. Portuguese delivery is excluded from English MVP. | The original missing-value issue appears resolved. Portuguese release timing remains openly deferred; language does not change jurisdiction or work timezone. |
| R8 — cross-role journeys | Final EXPERIENCE IA maps destinations to numbered Key Flows with protagonists, handoffs, outcomes and failures. Approved references include submission, approval, correction, revised acknowledgement, deficit review, allocation override, on-behalf and employee settings. Handoff coverage records normal and exceptional paths and accepted shared patterns. | The requested UX elaboration now exists; use linked contracts rather than creating a competing journey catalogue in the PRD workspace. |

## Nonnegotiable current scope

- One request may explicitly split paid and unpaid leave; the employee acknowledges
  the exact unpaid amount. New requests cannot displace existing reservations.
  Authorized changes increasing unpaid leave require actor/reason/old-new amounts
  and renewed acknowledgement before final approval. No automatic conversion of
  already approved leave to unpaid.
- One Approver role with workflow-assigned steps, normally one approver at setup.
  Self/on-behalf automatic decisions are explicitly authorized, not universal.
  Coverage and optional directional absence rules qualify finalization. No blanket
  privilege for platform/organization administrators to view employee records.
- Canonical minutes, half-day exactly half scheduled hours, hourly increments of
  30 minutes. Partial days use duration without exact clock times; same-date warnings
  and aggregate daily limits replace the superseded interval-overlap interpretation.
- Recurring employee entitlement changes at entitlement-period boundaries;
  immediate one-off changes use audited adjustments. Immutable ledger, snapshots,
  effective-dated versions and archive markers have distinct purposes.
- One autosaved employee draft per employee/NGO; safe Close. Confirmed submission
  returns to My Leave (ADR-0087); uncertain outcome is checked before retry.
- Light-only Neutral + Quiet Lagoon MVP inherits shared platform patterns.
  No standalone future-balance calculator, generic task-management product,
  mandatory separate unpaid application, or consultant-confirmation screen is
  implied by the approved walkthroughs.
- Migration is a consultant tool/runbook plus approval by email tied to the exact
  batch. Setup status derives from application configuration, not consultant email.
  Microsoft organization graph, calendar/HRIS integrations and Portuguese delivery
  remain future scope.
- BMAD Phase 1 requirements, architecture, stories and readiness gates remain.
  UX completion is not authorization to implement Leave. Apps remain silos; shared
  runtime contracts use services, and generic UI/scaffolding is promoted deliberately.

## Open work versus new product questions

The final UX handoff records no remaining user visual-design choice. It identifies
architecture/delivery work: exact policy-field validation, schedule/ledger impact
calculation, period-relative expiry arithmetic, version/snapshot schemas, imports,
rollback and runtime authorization/concurrency. Responsive breakpoints, rendered
focus/keyboard/zoom/AT testing and full interactions for partial mocks are delivery
verification, not evidence that approved behavior is missing.

The original pilot-success and operational acceptance-bound questions (R2/R6)
are the main prior areas whose complete resolution cannot be inferred from the
extracted material. Their product/release owners and gates need assessment by the
actual review. Any arithmetic edge case changing an externally visible date must
be resolved explicitly before its story is ready, even when tracked under architecture.
No new findings or product requirements are asserted here.

# PRD Quality Review — Leave Tracker Functional Specification

Review date: **2026-09-20**. Standard quality-rubric revalidation, replacing the 2026-09-14 snapshot after assessing its R1–R8 findings. No additional review lens.

Authoritative product source: `apps/leave/docs/features.md` (repository-owned specification, not a generated PRD). Context includes the implementation tracker, applicable accepted Leave ADRs, and the finalized `ux-leave-2026-09-15` DESIGN/EXPERIENCE handoff. Locations use the reviewed files' current line numbers. This report is review evidence; it does not amend product decisions or authorize implementation.

## Overall verdict

The specification now provides a coherent and substantially testable product baseline: the previous major calculation, lifecycle and privacy ambiguities have been resolved through explicit rules, examples and linked decisions. It supports architecture and story planning, with one remaining product handoff clarification for unpaid on-behalf requests, a narrowly bounded expiry-date decision, and operational acceptance targets to settle before their affected readiness gates. The approved scope and UX do not need redesign.

**Current findings: 0 critical, 0 high, 3 medium, 1 low.** Findings are counted once under their primary dimension. Prior findings: six resolved, two partially resolved; none remain open in their original breadth.

## Decision-readiness — adequate

The product makes consequential choices explicitly: protected reservations, date-by-date funding, an acknowledged paid/unpaid split within one request, single employee drafts, duration-only partial days, one Approver role with assigned steps, and directional absence fallback. Accepted ADRs retain historical choices while linking superseding decisions; the specification correctly reflects return to My Leave after confirmed submission (ADR-0087).

On-behalf authority is now approved without the old “if later approved” qualifier, including reason, attribution and independent approval authorization (Permissions and §10). R1 is resolved. The remaining initial-unpaid/on-behalf handoff is a real product clarification, recorded as R9 below, rather than a reason to reopen all approval design.

## Substance over theater — strong

Most detail serves an observable outcome. The operational roles define access and action boundaries rather than decorative personas. Examples specify minutes, date boundaries, authorization denials, concurrency, exact acknowledgement amounts, privacy transformations and idempotent effects. The document avoids invented market differentiation and unsupported adoption metrics.

The long catalogue has grown through real decisions, especially §6; its length is a navigation concern rather than evidence that the substance is unnecessary. Operational adjectives that still lack pass/fail bounds are handled in R6, not dismissed as generic boilerplate across the entire specification.

## Strategic coherence — strong

Employee clarity, auditable administration, NGO isolation and reusable platform mechanisms remain the consistent thesis. The boundaries preserve that thesis: no statutory engine, self-service migration UI, generic workflow builder or Microsoft directory synchronization in MVP; no duplicate employee identity; shared controls promoted only when proven. The simple request-focused balance view expressly defers a separate future calculator (ADR-0084).

R2 is resolved at product-specification level. The UX requirements now supply observable pilot tasks—finding prior-year leave, distinguishing taken/future/pending leave, identifying available/reserved balances and understanding the request's paid/unpaid consequence—and require refining and retesting observed confusion (`features.md:1928–1948`, ADR-0062, UX Key Flows 1–3a). A pilot script, representative participants and evidence collection remain delivery work; arbitrary speed or adoption thresholds are not needed to make this product thesis actionable. Privacy and correct calculation remain explicit guardrails.

## Done-ness clarity — adequate

The earlier high findings no longer describe the baseline. Grant schedules, proration, rounding, inclusive expiry, entitlement periods, allocation ordering, reservation priority and cancellation recalculation have worked examples. Lifecycle rules now distinguish automatic decisions from zero-step workflows, intermediate from final consumption, same-request resubmission from linked replacement, and cancellation from another approval. Privacy rules identify owners, assigned approvers, managers and ordinary colleagues, including APIs, metadata, notifications and exports. R4 and R5 are resolved.

The remaining findings concern bounded acceptance gaps. R3 and R6 already have legitimate downstream design work; they must remain visible gates rather than be mistaken for settled numerical requirements. R9 requires an explicit actor/timing decision because existing rules do not determine a usable on-behalf path with unpaid leave.

### Findings

- **[medium] R3 — Remaining carry-over month arithmetic needs an accepted outcome** (§6, `features.md:642–647`; ADR-0085, Consequences; `implementation-plan.md:494`) — The specification now resolves the original broad calculation gap, but explicitly says “month-end/leap-day anniversary arithmetic requires deterministic delivery examples.” “Three months from 1 January” does not determine the last usable day for a period starting on 31 January or 29 February. Date-library behavior could produce different employee entitlements. *Fix:* Before the affected calculation story passes readiness, record the chosen month-addition/clamping rule and a compact month-end/leap-day acceptance table, preserving inclusive expiry and never extending an existing expiry. This is the already acknowledged narrow product/calculation decision, not a request to revisit the approved accrual model.

- **[medium] R6 — Operational acceptance targets still lack bounded ownership and decision gates** (Non-functional requirements, `features.md:1992–2004`; implementation plan Phases 3, 9 and 10; finalized UX Responsive & Platform) — “Short-lived signed content operations,” “actionable alerts,” “Tested backups, restoration” and “Performance targets agreed before release testing” still do not provide repeatable bounds. Mobile/keyboard journeys and visual behavior are much clearer now, but supported browser coverage and operational targets are not supplied by those UX contracts. Broad team ownership and eventual test tasks do not state who agrees each target and when the dependent architecture/story can be accepted. *Fix:* Assign the responsible architecture, security, operations and product decision owners (roles suffice), and record gates for signed-operation lifetime, recovery objectives/rehearsal outcomes, critical alert conditions, supported browser coverage, and latency/workload targets. Let architecture and delivery supply those values and link them back; do not invent numerical targets in this review or block unrelated product planning on them.

- **[medium] R9 — Initial unpaid acknowledgement has no defined on-behalf handoff** (§7, `features.md:1074–1092`; §10 automatic on-behalf decisions; UX EXPERIENCE “Apply on behalf,” lines 651–665 and Key Flow 4a) — Ordinary submission requires acknowledgement of the exact unpaid amount “before submission.” The on-behalf UX explicitly says its illustrated request is fully funded and leaves “employee unpaid acknowledgement” to existing requirements, while also keeping the manager's work separate from the employee's own draft. The later-increase response flow starts from an existing pending request and therefore does not determine how Ana acknowledges an initial two-day unpaid amount in Sofia's not-yet-submitted request. Implementers could either accept Sofia's checkbox as Ana's consent, prevent a supported on-behalf use case, or invent a new submission exception. *Fix:* Agree who acknowledges, when that occurs relative to manager submission, and how the employee reaches the exact version/amount without changing their own saved draft. Add an acceptance example for an initially unpaid on-behalf request, including a submitter who owns the sole approval step and an amount that changes before acknowledgement. Preserve attribution, employee protection and independent approval authority; do not infer that on-behalf permission includes employee acknowledgement.

## Scope honesty — strong

The specification and tracker now distinguish product approval, UX completion and pending implementation readiness. Deferred localization names English as MVP, a concrete date format, and Portuguese for Mozambique/Angola as a later translation delivery (R7 resolved). Consultant migration remains an external email-approved exact-batch process, not an application approval page.

The UX handoff openly lists partially illustrated journeys, written-state coverage and outstanding browser/accessibility verification. These are not absent product features or completed runtime claims. The inherited light-only theme and future dark-mode option are bounded in the shared/Leave design contracts. R3 and R6 identify the remaining acceptance decisions without silently removing functionality.

## Downstream usability — adequate

Twenty stable feature headings, 67 acceptance-example labels and linked ADRs provide usable source anchors without forcing the repository into a duplicate FR/UJ/SM template. The finalized EXPERIENCE document supplies named role journeys, failure paths and handoffs. Stories can cite feature sections plus applicable ADRs and UX patterns, then add requirement-to-test traceability under the existing ATDD gate.

Some old checklist phrasing still contradicts stronger rules elsewhere. Repairing it is documentation reconciliation, not a new design decision.

### Findings

- **[low] R10 — Request-page inventory retains superseded input/action wording** (§7, `features.md:1128–1139`) — “Accessible date and time inputs” and “Save draft and submit actions” can be extracted as requirements for exact-time fields and an explicit Save draft button. The same specification and ADR-0074/0075 instead require date plus duration without exact times, automatic draft saving, and Close. *Fix:* Update this inventory to name accessible date/duration controls and truthful autosave with Close/Submit. Keep the accepted ADRs unchanged; this requires no additional product choice.

## Shape fit — strong

A repository-owned capability specification remains appropriate for this multi-role internal product and its platform-reference purpose. It need not acquire fictional personas, marketing metrics or a new document hierarchy to meet a generic PRD template. The technical invariants are justified by historical balances, sensitive information and cross-NGO risks.

R8 is resolved through the finalized UX Key Flows: Ana applies and reads outcomes, João handles assigned decisions, and Sofia manages allocations, corrections, coverage and configuration. Normal paths and failures connect actors and results. The scope remains represented once in product truth, with UX elaborating behavior and the tracker owning delivery sequencing.

## Mechanical notes

- **Source freshness:** `features.md` still says Last updated 2026-09-14 although it includes later ADRs and approved September 20 decisions. Refresh that metadata on the next authorized source edit; do not read it as evidence that later decisions are absent.
- **Links and identifiers:** Parent validation found all 96 local file-link targets in `features.md` present; numbered feature headings remain 1–20. There is no FR/UJ/SM ID scheme to validate. Requirement-level story/test references should retain existing section and ADR anchors.
- **Terminology and navigation:** NGO/organization and request/application are intelligible aliases. A short alias note or subsection anchors would help extraction from the large §6, but this is optional organization work rather than another product blocker.
- **Assumptions:** No formal inline assumption/index scheme exists, so no roundtrip defect is asserted. Explicit prose deferrals and tracker gates govern the remaining decisions.
- **Verification boundary:** Document review only. No product, UX, ADR, code or tests were changed by this reviewer. Structural mock checks do not establish browser or assistive-technology compliance. Architecture, stories and implementation readiness remain pending.

### Prior finding disposition

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

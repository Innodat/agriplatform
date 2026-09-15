# Validation Report — Leave Tracker Functional Specification

- **PRD:** `apps/leave/docs/features.md`
- **Rubric:** `.agents/skills/bmad-prd/assets/prd-validation-checklist.md`
- **Run at:** 2026-09-14T06:19:34.268596+00:00
- **Grade:** Fair
- **Scope:** Standard requirements-quality review; no source changes or implementation authorization.

## Overall verdict

The specification is a credible, well-bounded product baseline: it connects multi-NGO leave management to concrete privacy, historical integrity, and platform reuse decisions. It supports continued Phase 1 planning, but calculation outcomes, lifecycle paths, and privacy visibility need more precise acceptance rules before the affected stories are ready to implement. The approved scope should be preserved while these details are resolved through the existing specification and subsequent UX, architecture, and readiness work.

## Dimension verdicts

- Decision-readiness — adequate
- Substance over theater — strong
- Strategic coherence — adequate
- Done-ness clarity — thin
- Scope honesty — adequate
- Downstream usability — adequate
- Shape fit — adequate

## Findings by severity

### Critical (0)

None.

### High (3)

**[Done-ness clarity] — R3 — Configurable calculation options lack enough defined consequences** (§4, `features.md:167–172`; §6, `features.md:208–209`; §9, `features.md:265–271`)

The catalogue lists “Entitlement, proration, rounding, carry-over, cap, and expiry” and “projected on the leave date” without defining the supported calculation choices or their ordering. It does not establish, for example, how a future request spanning an accrual/expiry boundary is evaluated or how an existing pending reservation affects that projection. Accepted Leave ADRs 0001–0003 establish ledger, versioning, and minute-storage invariants, but do not resolve these product outcomes.

Fix: Before balance-engine and policy stories pass readiness, add a compact supported-rule table and worked acceptance examples covering accrual/expiry boundaries, proration/rounding, and competing reservations. State which values NGOs configure and which calculation behavior is fixed. Preserve the approved 50% half-day rule, 30-minute hourly increment, immutable history, and default unpaid deficit; do not invent jurisdictional entitlement formulas.

**[Done-ness clarity] — R4 — The lifecycle does not fully explain already supported paths** (§10, `features.md:275–276`; §11, `features.md:300–310`; Application status, `features.md:434–448`; Balance reservation, `features.md:463–469`)

Zero-approval workflows are allowed, but the only success path shown passes through “In approval.” The diagram ends rejection at “Resubmitted,” which is absent from the approved application-status list. “approval → convert reservation to consumption” does not explicitly say whether this is final approval when two steps exist. These omissions can change statuses, notifications, and balance timing.

Fix: Add a transition table using the existing approved statuses: trigger, authorized actor, destination, workflow-step effect, balance effect, and notification consequence. Explicitly cover zero-step approval, intermediate versus final approval, and resubmission, stating whether it reuses or replaces the request. Clarify amendment's existing alternative (“cancellation and a replacement request or an explicitly versioned amendment flow”) before its story. Align §14's “Request cancellation” wording with the accepted no-further-approval cancellation rule. Any genuinely new user-visible state or transition still requires product review under the existing state-model policy.

**[Done-ness clarity] — R5 — Shared-view privacy lacks a deterministic visibility rule** (§4, `features.md:175`; §13, `features.md:344–346`; §15, `features.md:371`; §18, `features.md:398–403`)

“Privacy classification,” “minimum necessary information,” and “Shared views may show Unavailable” express the right intent but do not identify which viewer can see which fields for each classification. An implementation could display a sensitive type to an approver or expose it through a type filter while claiming to follow these statements. Accepted Leave ADR-0006 establishes separate document authorization but does not supply the ordinary-view field rules.

Fix: Agree a concise visibility matrix for request owner, assigned approver, team/organization viewer, and permitted sensitive-document reader, covering type label, note/reason, comments, and document metadata across screens, notifications, filters, and exports. Specify the default when no explicit visibility permission applies. Turn at least one allowed and one denied sensitive-view case into acceptance examples before the corresponding stories.

### Medium (4)

**[Decision-readiness] — R1 — On-behalf permission still appears unapproved** (Permissions, `features.md:116`; §17, `features.md:391–392`)

The permission list says “`leave.admin.on_behalf` if later approved,” while the Leave Manager workspace already includes submission and approval on behalf. The implementation plan's confirmed-decision table at line 81 and accepted Leave ADR-0004 explicitly approve the capability with separate permission, attribution, reason, and conflict checks. A downstream reader could incorrectly defer the feature or omit its security criteria.

Fix: Align the permission wording and associated acceptance references with the existing approved decision, including its conflict-check requirement; do not silently broaden permission scope.

**[Strategic coherence] — R2 — Employee understanding has no observable pilot criterion** (Product principles, `features.md:52–53`; MVP acceptance summary, `features.md:515–516`)

“Make the employee's next action obvious” and an employee who can “understand the exact current/projected balance calculation” are meaningful goals, but displaying the numbers alone does not prove either. No pilot task, pass criterion, or observation method is specified.

Fix: Agree a small representative pilot task and an observable result, such as an employee correctly explaining the duration and balance consequence before submitting without assistance. Product should choose the criterion; pair any speed or completion target with a correctness/privacy guardrail. This does not require a marketing-metrics section or arbitrary usage targets.

**[Done-ness clarity] — R6 — Several release-quality statements still need measurable bounds** (UX requirements, `features.md:475`; Non-functional requirements, `features.md:488–495`; MVP acceptance summary, `features.md:524–525`)

“Work well on mobile and desktop,” “Short-lived signed content operations,” “actionable alerts,” “Tested backups, restoration,” and “Performance targets agreed before release testing” cannot yet determine a repeatable pass/fail result. WCAG 2.2 AA is already a concrete standard; the other statements have no equivalent stated criterion. The performance deferral is explicit and legitimate, but no owner or bounded decision record accompanies it.

Fix: Record who will agree supported viewport/browser coverage, signed-operation lifetime, restoration/recovery objectives, critical alert conditions, and response targets with workload assumptions, plus the planning/story gate by which each is needed. UX and architecture may supply the details; link them back to these requirements. Do not fabricate numerical targets during validation.

**[Shape fit] — R8 — Cross-role journeys need outcomes and handoffs before UX is finalized** (§7, `features.md:213–239`; §§14–17, `features.md:348–394`)

The employee list includes “Apply for leave” and “View request status and approval timeline”; the supervisor list includes “Review assigned requests.” Neither carries one request through those actors with its pending state, next action, and employee-visible outcome after rejection, override, or cancellation. The lifecycle contributes state names but does not describe the user's experience across handoffs.

Fix: Use the upcoming `bmad-ux` work to capture a few short, role-named journeys linked to existing sections: normal submission/decision, insufficient-balance decision, and rejection/resubmission or cancellation. Include NGO context and what the employee and approver each see at handoff. Write these as approved behavior elaboration, not new scope or a duplicate feature catalogue; resolve the lifecycle questions in R4 with product input.

### Low (1)

**[Scope honesty] — R7 — The supposedly agreed MVP locale is not identified** (MVP exclusions, `features.md:506`)

“Full localization beyond the agreed MVP locale” refers to a decision whose value is not present in this specification, its implementation plan, or the reviewed accepted ADRs. UX cannot source a concrete initial language and date/number-format convention from those inputs.

Fix: Name or link the agreed MVP locale; if it is not yet agreed, record it as a UX decision to resolve. Keep locale distinct from the already required employee-specific timezone and jurisdiction configuration.

## Dimension assessments

### Decision-readiness — adequate

The product principles and feature catalogue state consequential choices directly: multiple NGO memberships, immutable ledger entries (§6), exact half-day consumption (§8), unpaid deficit by default (§9), snapshotted workflows (§10), and explicit limits on document access (§12). The implementation plan's confirmed decisions and accepted ADRs provide the alternatives and costs, so repeating those trade-offs in a newly formatted PRD would add little value.

One obsolete qualifier conflicts with an already accepted permission decision. This requires document reconciliation, not a fresh debate over whether the capability belongs in MVP.

### Substance over theater — strong

This is a capability specification, and most of its detail earns its place. The six role descriptions are operational permission boundaries, not decorative personas: employees, supervisors, final approvers, Leave Managers, organization administrators, and platform administrators have different responsibilities and access limits. Reducing their number merely to satisfy a persona-count heuristic would damage the document.

Product-specific consequences include upload limits and types (§12), the 30-minute increment and employee-specific half-day calculation (§8), retry-safe accrual (§6), and exclusions that rule out calendar integrations and a statutory engine. Generic language in several non-functional bullets needs acceptance detail, recorded under done-ness clarity rather than treated as evidence that the whole specification is boilerplate.

### Strategic coherence — adequate

The purpose at lines 10–16 clearly combines a usable leave product with a reference implementation for platform mechanisms. The employee, approver, and manager capabilities serve that purpose, and the implementation plan makes foundation work precede dependent features. Scope exclusions and the prove-then-promote UI/scaffold rule constrain platform ambitions without silently dropping product requirements.

The acceptance summary establishes functional release gates but does not yet show how pilot use will validate the employee-understanding claim.

### Done-ness clarity — thin

Several requirements already have clear tests: file count/size/type limits, half-day consumption, active membership checks, ledger immutability, retry deduplication, and authenticated approval links. The plan deliberately places detailed acceptance examples before each implementation slice, which is appropriate. However, the financially significant policy calculations, approved lifecycle, and sensitive-data visibility currently leave choices that could produce different externally observable behavior from the same input.

The following high findings concern the affected implementation stories; they do not invalidate Phase 0's approved direction or require all later-phase test cases before UX planning begins.

### Scope honesty — adequate

The MVP boundary is explicit in the header and exclusions. Deferred malware scanning, jurisdiction-reviewed configuration, configurable medical-document retention, no mandatory approval for cancellation, and informational capacity warnings are stated honestly. The implementation plan already has a risks table and confirms on-behalf work is in scope. The status “detailed acceptance criteria remain living documentation” accurately distinguishes scope approval from complete implementation readiness.

There are no inline `[ASSUMPTION]`, `[NOTE FOR PM]`, or formal Open Questions entries; that is not inherently a defect in an existing repository specification. The real deferrals are in prose and in the plan. R1 and R6 address two places where making their status clearer changes downstream decisions.

### Downstream usability — adequate

The numbered feature sections, explicit roles, state models, related-document links, acceptance summary, and implementation phases provide useful extraction anchors. The accepted ADRs should remain linked authority rather than being copied into a second specification. The full feature catalogue runs continuously from 1 through 20, and all local Markdown link targets in `features.md` resolve.

There are no FR/UJ/SM identifiers or dedicated glossary, but that template difference alone is not a failure. During story creation, stable feature-section references can support the existing requirement-to-test chain; finer identifiers are useful only where individual bullets would otherwise be ambiguous. “NGO”/“organization” and “request”/“application” are understandable in context, but a brief terminology note would make extraction safer. The actual state-name mismatch is addressed in R4 rather than counted again here.

### Shape fit — adequate

A role-oriented capability specification fits this internal, multi-stakeholder application, and its technical constraints are justified by its reference-application purpose. There is no need to invent market differentiation, fictional persona biographies, or a new PRD structure. The role workspaces do identify protagonists, but their action lists do not yet show the handoffs that materially shape UX.

## Mechanical notes

- **Identifiers:** Feature sections 1–20 and acceptance items 1–10 are continuous. No FR/UJ/SM scheme exists, so no gaps or duplicates in such a scheme are asserted.
- **Cross-references:** A local-path existence check found no missing targets among `features.md` Markdown links. Accepted ADRs were read as context, including their alternatives and consequences.
- **Terminology:** “NGO”/“organization” and “request”/“application” would benefit from a short alias note when stories are extracted. “Resubmitted” versus the enumerated statuses is a behavioral issue already counted in R4.
- **Assumptions:** No inline tagged assumptions or Assumptions Index exist; there is no tag/index roundtrip defect to report. Prose deferrals remain subject to the scoped findings above.
- **Journeys:** No formal UJs are present. Existing role names are suitable protagonists; R8 concerns missing handoff behavior, not naming conventions.
- **Tracking context:** The implementation plan's header says “Planning complete — ready for Phase 1,” while Phase 1 explicitly still includes PRD, UX, architecture, stories, and readiness work. Interpret the header as Phase 0 baseline completion, not permission to implement; the detailed checklist and repository instructions control.
- **Verification boundary:** This is a document review, with source/context reads and a local link-target check. No application code or automated product tests were changed or run, and no readiness or release gate was declared passed.

## Reviewer files

- `review-rubric.md`

---
project: Leave
status: epic-structure-approved
created: 2026-09-23
stepsCompleted: []
currentCheckpoint: Incomplete input preservation approved; E1 acceptance map drafted; consolidate remaining technical contracts
requirementsInventoryStatus: Source-indexed coverage proposal; granular extraction and confirmation pending
epicApproval: Approved by user on 2026-09-23, including E5 and delivery sequence
implementationReadiness: pending
inputDocuments:
  - ../../AGENTS.md
  - ../../apps/leave/docs/features.md
  - ../../apps/leave/docs/architecture/ARCHITECTURE-SPINE.md
  - ../../apps/leave/docs/implementation-plan.md
  - ../../platform/docs/architecture/decisions/README.md
  - ../../apps/leave/docs/architecture/decisions/README.md
  - ../../platform/docs/architecture/decisions/0038-finalized-content-byte-identity.md
  - ../../platform/DESIGN.md
  - ../../platform/EXPERIENCE.md
  - ux-designs/ux-leave-2026-09-15/DESIGN.md
  - ux-designs/ux-leave-2026-09-15/EXPERIENCE.md
  - ux-designs/ux-leave-2026-09-15/handoff-coverage.md
  - architecture/architecture-leave-2026-09-20/review-resolution.md
  - ../../platform/builder-cli/README.md
  - ../../apps/leave/docs/operations/migration-runbook.md
---

# Leave — approved epic structure

The user approved all eight epic groupings and the delivery sequence on 2026-09-23,
explicitly including E5. Granular requirements extraction, individual stories,
story readiness and implementation authorization remain incomplete. The workflow
steps are not marked complete while their remaining extraction/coverage work is open.
Inputs were read from the current working tree; `git status --short` showed no
pre-existing changes at the start of this session.

The [feature specification](../../apps/leave/docs/features.md) remains product
truth. The [implementation plan](../../apps/leave/docs/implementation-plan.md)
remains the delivery tracker, including its phase exit gates. The
[architecture spine](../../apps/leave/docs/architecture/ARCHITECTURE-SPINE.md),
accepted ADRs and approved UX govern the decomposition. This document maps that
authority into proposed work; it does not replace requirements or reproduce ADRs.

## Proposed epic list

Numbers indicate the proposed main delivery sequence, not new tracker phases.
Shared prerequisites are assigned to their owning platform/service work and linked
to the first consuming slice. Each epic includes the tests, operational mechanisms
and impact work necessary for its own outcome.

| Epic | Outcome and boundary | Principal source coverage |
| --- | --- | --- |
| E1 — Start and safely resume my leave draft | Sign in → select organization → create/resume draft → enter details → autosave → close → reopen. Prove current access, organization isolation, safe persistence and recoverable desktop/mobile interaction. No entitlement reservation or submission. | Features §1, draft portion of §7, §14, Permissions and UX; spine AD-1, AD-2, AD-4, AD-8, AD-12, AD-13; tracker Phase 1 and first delivery slice, relevant Phases 2–3 |
| E2 — Set up organization access, people and working arrangements | Authorized invitation/membership and application access administration, default/custom roles, organizational structure, shared-person references, shared employment facts and optional department/location/manual supervisor assignments plus Leave-specific employee settings, work profiles and holidays. Effective-dated edits, archive dependencies and honest setup assessments. | Features Permissions, §1–3, relevant §10 and §17; AD-1–3, AD-5, AD-12; tracker Phases 2, 3, 5 |
| E3 — Configure entitlement and understand available leave | Versioned leave types/policies, recurring overrides, opening/manual adjustments and their notifications; authoritative daily/upfront/monthly entitlement, precision, caps, carry-over, expiry and date-by-date request previews. Employees see explainable current/reserved/projected amounts; managers review consequences before changing entitlement. | Features §4–6, calculation portions of §7–9, §13–14 and §17; AD-3–7, AD-10–12; tracker Phases 5–6 and first required notification work from Phase 8 |
| E4 — Attach and retrieve supporting documents safely | Recoverable draft/request attachments through the shared Content Service, accurate attaching/verification states, private authorized reads, retention and coordinated cleanup. Include provider migration/parity and the complete fixed-byte contract. | Features §12, attachment portions of §7 and §13, document permissions; AD-2, AD-9, AD-12–13; tracker Phase 4 and relevant Phase 7 |
| E5 — Submit leave and complete the right approval process | Full/half/hourly requests, validation, reservations, ordinary and on-behalf submission, exact employee unpaid responses, authorized overrides, decisions, withdrawal and rejected-request resubmission. Include required coverage, temporary appointments/return, directional fallback, reminders/escalation and finalization checks. Deliver own request history/calendar, actionable Approvals with permitted team availability, manager coverage/escalation attention and required notifications. | Features §7–11, §13–16, approval portions of §17–18 and State models; AD-2–8, AD-10–13; tracker approval portions of Phase 2, Phases 7–8 and relevant Phase 9 |
| E6 — Correct leave and resolve its consequences | Approved cancellation and linked replacement, administrative corrections, historical employment/policy/balance corrections, deficit review and correction follow-up. Preserve original decision evidence; explain revised effects and require renewed unpaid acknowledgement where applicable. | Features §6, §11, correction portions of §17 and §20; AD-3–7, AD-10–12; tracker Phases 6–8 and manager attention in Phase 9 |
| E7 — Understand organization absence and report with privacy | Broader organization overview, role-scoped dashboards, all specified reports and CSV exports, searchable authorized audit history. Include matching screen/API/export privacy, useful filters and return context. E5 already provides the history and team information needed to apply and decide. | Features §17–20, reporting portions of §6; AD-2, AD-5, AD-12; tracker Phase 9 |
| E8 — Reconcile pilot data and operate Leave recoverably | Consultant import/preview/reconciliation and exact-batch client email evidence, cutover, representative role UAT and pilot activation. Demonstrate recovery, migration compatibility/failure handling, worker recovery, alerting, browser/performance and accessibility targets. | Features NFRs, operational targets, MVP acceptance and consultant-import scope; AD-13; tracker Phase 10 and migration runbook |

E5 is deliberately the largest domain epic: its approval, coverage and acknowledgement
conditions must work together. Story decomposition will keep implementation units
bounded; it must not postpone finalization safeguards to E6. E6 adds correction
journeys, while every earlier writer must already preserve its applicable history,
authorization, attribution, revision and impact invariants. Introducing requests in
E5 requires verifying all existing configuration writers against those requests.

## Delivery sequence and shared prerequisites

1. Complete this planning conversation, granular traceability and story decomposition;
   resolve relevant pre-story contracts and pass the existing BMAD sprint-readiness
   gate before implementation. Architecture consolidation is already complete.
2. Deliver E1 as the first working application slice. Include only the minimum
   shared identity/access, shell, persistence, generator and verification work it
   needs. Authorized test fixtures can supply configuration; E1 does not require
   delivering the full E2/E3 administration experience first.
3. Expand to E2 and E3. Establish shared notification handover/delivery with the
   first actual notice-producing capability, including E3 entitlement changes and
   adjustments; notifications cannot be postponed wholesale until requests exist.
4. Deliver E4 before enabling document-dependent submission. Its provider and
   association contract work can proceed independently once its inputs are ready;
   a content blocker does not block the unrelated draft outcome.
5. Deliver E5, then E6 and E7. Extend existing delivery mechanisms with each domain
   event. Scheduled coverage returns and reminders need durable due-work discovery,
   missed-run recovery and fresh authorization, separate from automatic entitlement.
6. Complete E8 before pilot enablement. Instrumentation, security, accessibility,
   compatible migrations and recoverability begin in their first affected delivery
   item; E8 assembles and demonstrates release evidence rather than adding them late.

The builder is a documented placeholder, not an available generator. E1 therefore
needs explicit bounded platform work to prove the minimal pattern, establish its
generator/template and disposable-app tests, and meet the existing generated-slice
exit gate. Do not claim `generate Leave` is an executable starting command.

## Binding readiness contracts

Use the spine's [Deferred and Delivery Gates](../../apps/leave/docs/architecture/ARCHITECTURE-SPINE.md#deferred-and-delivery-gates)
and existing tracker for ownership and completion evidence. The proposal closes none.

| First affected work | Required contract/evidence and owner |
| --- | --- |
| E1 identity/access | Platform identity owner + Leave lead: service placement and adoption of existing identity schema; person/service/membership/permission identifiers, current authorization API, role management, allowed references, revocation execution bounds |
| E1 API and persistence | Platform API owner + Leave lead: operation/result recovery, scoped deduplication window, revisions, stable error fields compatible with the numeric-code template, generated clients/adapters; concrete draft lifecycle/uniqueness, attribution, restricted roles, RLS and transaction context |
| First dependent build | Technical lead + operations: dependency compatibility/pins, environment isolation, hosting/provider configuration and secret handling; owner migration histories, coordination and release-failure recovery |
| E2/E3 and every consequential writer | Leave technical lead: tables/keys, historical intervals/buckets, event/snapshot representation, deterministic allocation ties, employee/configuration/cross-employee protection, lock order and bounded waits; all alternate writers participate. Unresolved policy transition semantics must be settled before a story exposes them. |
| E3 first notification and later E5 scheduling | Leave + notification owners: event versions, restricted claims, heartbeat, leases/shutdown, retry limits, durable receiver acknowledgement/deduplication/expiry; scheduled domain transitions require their own due-work and reauthorization design |
| E4 attachments | Content owner + Leave lead: authorized pending/confirmed association handshake, cleanup coordination, fixed verified byte/version binding and provider-enforced capability lifetimes; verify before attachment-story readiness |
| E7/E8 reports and import | Leave + shared UI/tool owners: scoped report/export contracts, import batch identity, reconciliation and exact-batch consultant approval evidence |
| Relevant story planning and pilot | Product owner + technical lead: browsers, representative NGO/history workloads and measurable response targets. Operations: probes/routing/log retention, backup capability, restore and alert evidence before pilot |

For E4, [platform ADR-0038](../../platform/docs/architecture/decisions/0038-finalized-content-byte-identity.md)
requires proof against outstanding upload-capability replay and uploads racing
verification/finalization. Reads and associations must retain the verified byte
identity; replacement needs new content identity, verification and an authorized
audited association change. A checksum on a mutable object is insufficient.

This is separate from ADR-0036's five-minute read/fifteen-minute upload target.
The architecture review records the standard Supabase upload API's two-hour
capability as an open provider-feasibility issue. Prove a supported enforcement path
or obtain a superseding decision before readiness; a frontend timer cannot close it.
No provider experiment or new capability verification was performed in this planning
session.

## Requirements inventory and traceability approach

The source has twenty numbered feature areas, not an existing FR1…FRn catalogue.
Preserve those section references and their acceptance examples. Do not mislabel
feature-area counts as counts of atomic functional requirements.

| Authoritative feature area | Proposed coverage |
| --- | --- |
| §1 Identity, NGO context, onboarding | E1 first access/switching; E2 onboarding/setup |
| §2 Organization and employment | E2; consequential correction paths E6 |
| §3 Jurisdictions and calendars | E2; calculation integration E3 |
| §4 Leave types and policies | E3; workflow execution E5 |
| §5 Employee entitlement overrides | E3 |
| §6 Balance ledger and accrual | E3; protected request effects E5; corrections E6 |
| §7 Application experience | E1 draft; E3 previews; E4 files; E5 submission |
| §8 Hourly and half-day leave | E3 duration calculation; E5 request execution |
| §9 Insufficient-balance override | E3 projection; E5 authorized allocation/acknowledgement |
| §10 Approval workflows and cover | E2 supervisor/access setup; E3 policy configuration; E5 execution/cover |
| §11 Request lifecycle | E1 drafts; E5 pending/rejection/resubmission; E6 approved cancellation/replacement |
| §12 Attachments | E4 |
| §13 Notifications | First notices E3/E4; request/cover/reminder events E5; correction events E6 |
| §14 Employee workspace | E1 shell/draft; E3 balances; E5 requests/history/calendar/responses; E6 corrections |
| §15–16 Approver workspace and final steps | E5, including team availability |
| §17 Leave Manager workspace | E2/E3 setup; E5 coverage/escalation; E6 corrective attention; E7 wider overview |
| §18 Calendars and privacy | E4 document boundary; E5 personal/team views; E7 organization/export |
| §19 Reports and exports | E7 |
| §20 Audit and operational administration | Immutable audit in every originating epic; searchable business audit E7; operational commands with owning service work and E8 rehearsal |

Permissions, accepted state models, UX, NFRs, MVP exclusions and all applicable
platform/Leave ADRs apply across this map. Retain supersession chains: older ADR
wording does not restore configurable rounding, exact partial-day times, posted
daily accrual, separate final-approver roles or the superseded submission destination.

Before individual stories are finalized, expand this map to each actionable source
requirement and acceptance example, applicable AD/ADR, UX flow/component/state,
owning story and intended test boundary. Mark coverage pending until checked in
both directions; this section-level map is not a completed completeness assessment.

UX coverage must include shared semantic tokens and accessible controls, shell/NGO/
language, task drawer/page, safe close/save states, date entry, disclosures, field
errors, return navigation, review/confirm, role-holder navigation, upload recovery,
notification panel, collection toolbar/filter sheet, calendar/timeline/list and
report/export states. Use the approved Leave DESIGN/EXPERIENCE pair and inherited
platform spines; the 28 visual references remain illustrative rather than evidence
of browser or assistive-technology compliance.

For E1 specifically, retain simultaneous create/resume, same-tab save coalescing,
multi-tab revision conflict, discard/late-save protection, uncertain-save recovery,
failed close/save, save-before-NGO-switch and same-user session return. Closing
the form retains the draft; discarding/finalizing closes its lifecycle. Submission
race coverage joins when submission is implemented in E5.

## Completion controls and impacts

Every delivery item records scaffold, shared-UI, agent-context, documentation and ADR
impact decisions. Proven generic work updates owning templates, generated-client
workflows, generation tests, validation, catalogue/docs, changelog and applicable
existing-app migration notes in the same item. Leave calculations, states, grants
and resource authorization remain application-owned. Shared runtime prerequisites
retain HTTP boundaries; no second person directory or cross-silo server imports.

ATDD observes the relevant acceptance failure before user-visible behavior or service
contracts; focused TDD follows, then affected suites. Characterize unprotected
behavior before risky legacy migration. Record requirement → scenario → tests →
implementation → exact verification commands/results. Root dev/build are not
repository verification. Required security/domain code reviews and all existing
phase gates remain binding.

Initial proposal impacts: planning document only. Subsequent approved architecture
amendment: platform ADR-0039/0040, source ownership/prerequisites, shared-UI ownership
guidance, scaffold guidance and agent instructions synchronized. No runtime/scaffold
implementation or tracker milestone was marked complete. No application code,
migrations or application tests were executed; documentation checks are separate
from implementation readiness.

## Discussion checkpoint

Approved: retain eight outcome-oriented epics and the sequence above, including E5
as one approval journey epic. Minimum shared prerequisites remain in E1, and reliable
notification delivery accompanies its first consuming feature. This is epic approval,
not a readiness pass or approval of individual stories.

### Follow-up: shared employee information

The user requested the deliberate ownership change be documented on 2026-09-23.
[Platform ADR-0040](../../platform/docs/architecture/decisions/0040-shared-employment-core-and-application-settings.md)
now establishes one shared owner for common employment facts through authorized
HTTP contracts. Leave retains domain settings; a full HR suite is not a prerequisite.
The spine, feature specification and tracker reflect this ownership amendment.
Minimal shared reference/read contracts gate E1; shared employment administration
contracts gate E2; freshness/change-impact handling gates dependent mutation stories.

[Platform ADR-0039](../../platform/docs/architecture/decisions/0039-organization-neutral-tenancy.md)
records organization as the general tenant for nonprofit and for-profit organizations.
Earlier NGO wording in the approved epic proposal means organization; new code and
generic controls use organization and established org_id conventions.

Approved follow-up: [platform ADR-0041](../../platform/docs/architecture/decisions/0041-shared-supervisor-department-and-location.md)
places optional manually maintained supervisor and nullable department/location
assignments with shared employment. These are organization-specific, with stable
scoped references and effective-dated history. They require no organization-chart
editor or Graph import. Teams remain separately scoped. Leave work profiles retain
schedule/timezone/holiday ownership; location changes do not silently reassign them.

E2 includes simple authorized shared administration with unassigned choices and
null-versus-unavailable behavior. E5 resolves an eligible supervisor on submission
when the policy requires one and snapshots the workflow; missing/ineligible routes
retain the draft, and shared changes cannot silently reroute submitted requests.
E7 filters/reports must handle unassigned department/location values. These contracts
remain readiness work; the eight epics and first draft slice are unchanged.

### Follow-up: automated acceptance and human UAT

The user asked about automating acceptance from stories and suggested Playwright.
Existing ADR-0009 already requires acceptance examples before implementation.
Recommended tooling, pending delivery selection: Playwright for critical browser
journeys, pytest for Python domain/API/database/contract behavior, and Vitest with
React Testing Library for focused UI interaction. No tools were installed or tests
generated. The current web template has no test scripts; setup and generated-sample
verification must be explicit E1/scaffold work.

Give each story traceable acceptance scenarios with intended automated boundary and
human checks. The first browser acceptance journey preserves the agreed E1 path;
also cover real persistence, two NGOs, conflicting tabs, failed saves and session
return without treating mocked success as end-to-end proof. Use isolated synthetic
data and safe test artifacts. Routine tests may use controlled authentication setup;
separate integration evidence must verify actual Entra/Supabase sign-in.

Automated regression supports UAT but does not replace pilot users assessing whether
calculations, wording, workflows and accessibility work for them, or their acceptance
sign-off. Expected outcomes come from the approved requirements and agreed examples,
not from whatever the implementation currently returns.

### Browser test language recommendation

Recommend Playwright Test in TypeScript for browser acceptance alongside the React/Vite
frontend, using its integrated runner, reports, tracing and browser projects. Python
Playwright remains valid through pytest; there is no need to maintain the same browser
suite in both languages. Keep Python domain/API/database tests in pytest. This is a
recommendation pending tool selection, not an installation or story-readiness claim.
Official comparison: https://playwright.dev/docs/languages (checked 2026-09-23).


## E1 decomposition discussion — 2026-09-23

**Work breakdown approved by the user; not detailed story approval.** These work boundaries preserve the approved first
slice and support the next collaborative planning discussion. They do not close
pre-story contracts, replace granular requirements extraction, or authorize implementation.
Story numbering and Given/When/Then criteria follow after the applicable contracts
are resolved. No later epic is a prerequisite for this draft journey.

| Order | Proposed capability | Source requirements and acceptance coverage | Intended evidence |
| --- | --- | --- | --- |
| 1 | Sign in and enter an authorized organization | Features §1 and Permissions; spine AD-1/2/12; P-0019/0021/0039/0040. Entra/Supabase sign-in, prominent organization context, current membership/permissions, minimal shared employment reference/read. Distinguish denied access from unavailable authorization; never grant access from authentication alone. | Browser entry/selection plus real authentication integration evidence; API/contract isolation, revoked membership and unavailable dependency tests. |
| 2 | Start or resume my one draft | Features §7/14; spine AD-4/8; P-0033/0034. Apply for leave opens the existing authorized draft or atomically creates one; simultaneous starts return one identity without overwriting values. Show the unfinished-application note; reserve no entitlement. Persist only the minimum records needed here. | Browser open/resume; database concurrency and scoped uniqueness using restricted runtime roles; authorized recovery of original create outcomes. |
| 3 | Edit, autosave, close and reopen safely | Features §7 acceptance example; L-0067/0075/0118; spine AD-4/8/12. Persist agreed draft fields, truthful acknowledged save status, serialized/coalesced same-tab saves, preserved newer typing, uncertain-outcome recovery and revision conflicts. Close/Escape/mobile Back obey saved/saving/failed rules and preserve the last saved draft. | The complete first-slice browser journey against persisted data; API revision/idempotency tests; controlled network failure, delayed acknowledgements and conflicting tabs; keyboard/focus/save-status checks. |
| 4 | Switch organizations while editing | Features §1/7 switching acceptance example; L-0068. Save in the original organization before opening the selected workspace; failed saves offer Retry, Stay, or Discard unsaved changes and switch. Never transfer draft values; preserve previously saved content. | Two-organization browser journey and API scope checks, including failed/uncertain saves and no prior-organization content in the new workspace. |
| 5 | Discard a draft deliberately and start again | Features §7; P-0033/0034; L-0075/0118. Confirm Discard draft; distinguish it from discarding unsaved edits. Late saves and old create retries cannot resurrect the closed draft or overwrite a later one. New draft requires explicit action. | Browser confirmation/cancel/new-start; database/API discard-versus-save/create-retry races. Submission-specific closure and reservation races join in E5. |
| 6 | Recover my draft after sign-in expires | Features session-recovery requirement and §7; P-0032; spine AD-2/8. Restore validated same-user organization/page/draft context after renewed authentication and current access checks. Account change, lost access and invalid return targets get safe fallback; make unsaved recovery limits explicit. | Browser expiry/return/account-change scenarios; API access rechecks, safe return-target and sensitive-data isolation tests. |

UX sources for the table are the approved Leave
[EXPERIENCE](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md#apply-for-leave)
(Apply for leave, State Patterns, Interaction Primitives, Accessibility Floor and
Responsive & Platform), its paired
[DESIGN](ux-designs/ux-leave-2026-09-15/DESIGN.md), and inherited platform spines.
These are source references, not a claim that all atomic UX requirements have been
mapped. Each capability inherits server authorization and safe session failure from
its first protected action; item 6 adds the complete return journey rather than
postponing those protections. Likewise, lifecycle/revision guards accompany the first
writer; item 5 introduces the user-facing discard transition.

Item 3 is the main sizing checkpoint: retain revision/failure/close correctness with
the autosave behavior. Once concrete contracts are available, split it further only
if each increment has a safe, independently verifiable user outcome. Do not deliver
an unprotected happy-path autosave and depend on a future story to prevent data loss.

### Contracts to settle before detailed E1 stories

Use the existing spine gates and implementation-plan tracker, with decisions recorded
in their owning documents. Work through these in dependency order:

1. Shared identity/access and minimum employment read: service ownership/placement,
   stable organization/person/membership/employment identifiers, current authorization,
   permitted references and safe missing/unavailable behavior. Optional shared
   department/location/supervisor administration remains E2; no E1 HR interface.
2. API and persistence: operation/result recovery and deduplication lifetime, error
   compatibility, draft field/schema boundary, lifecycle/uniqueness/revision contracts,
   restricted runtime access, attribution and migration coordination.
3. Delivery/test foundation: verified dependency compatibility, environment isolation,
   supported browsers/targets, minimal generator path and disposable-app verification.
   Playwright Test in TypeScript remains the recorded recommendation, not an installed
   or verified test stack.

The first capability carries bounded shared access/client/shell prerequisites; the
first persisted capability carries its database/migration prerequisites. Proven
patterns update their owning scaffold and generated-sample checks in the same delivery
item. Each detailed story must record scaffold, shared-UI, agent-context, documentation
and ADR impacts. This outline neither creates a separate platform-first epic nor
assumes that the placeholder builder already works.

The user approved these E1 boundaries and requested the next contract discussion.
The owning [identity/access/employment proposal](../../platform/docs/architecture/contracts/identity-access-employment-e1.md)
records existing schema evidence, proposed owner placement and identifiers, minimal
reads/current authorization, employment-period choices and remaining wire decisions.
Its proposals are pending discussion, not a passed contract gate. Resolve the minimum
identity/access/employment contract before drafting the first detailed story. Global
requirements coverage and BMAD implementation readiness remain pending.

Follow-up agreement: one shared employment relationship per person per organization,
with preserved employment periods across rehire. Accountless-person support and the review recommendations were subsequently approved
under [platform ADR-0042](../../platform/docs/architecture/decisions/0042-person-account-employment-and-legacy-adoption.md). The user requested a platform-wide identity and
receipt/expense consolidation review before finalizing the shared contract; see the
[owning review and integration plan](../../platform/docs/architecture/reviews/identity-expense-consolidation-2026-09-23.md).


The user accepted the identity/Expense review recommendations and accountless support
on 2026-09-23; platform ADR-0042 records the binding direction. The next
[draft persistence/recovery discussion](../../apps/leave/docs/architecture/contracts/e1-draft-persistence-and-recovery.md)
proposes concrete draft/operation/revision boundaries and identifies remaining
employment-eligibility, wire, retention and cleanup decisions. No story or readiness
gate is marked complete.


Draft discussion agreement, 2026-09-23: current/future employees with granted access
may prepare drafts; ended employment retains an authorized read-only draft; rehire
resumes retained input with refreshed context. Passing selected end dates never
implicitly discards a draft; current backdating rules gate later submission.
Authoritative features and UX now record this. The draft contract proposes separate
active-content, discarded-content and compact replay-evidence retention, including a
scope-generation guard against never-seen delayed starts. These technical proposals
and remaining pre-story gates are not marked complete.


Approval, 2026-09-24: explicit discard removes editable form contents while minimal
server-side lifecycle/replay evidence remains; E1 has no automatic expiry of active
drafts or compact receipts. Recovery evidence belongs in the application database,
with proposed separate lifecycle and operation-receipt records. Shared-platform
implementation is attached to E1's first consumer and updates reusable scaffolding,
clients/UI and disposable generated-app tests. Later apps adopt the pattern but own
their records, transactions and domain rules; no central draft/operation service or
mandatory Leave-style draft workflow. Physical contracts/readiness remain pending.

Next contract proposal, 2026-09-24: the platform-owned
[API error and operation-recovery contract](../../platform/docs/architecture/contracts/api-errors-and-operation-recovery.md)
defines an additive stable error identifier, numeric-code compatibility, typed safe
details and committed/unresolved operation responses. The Leave draft contract maps
revision, discarded/submitted lifecycle and read-only outcomes to existing UX. Shared
template/adapters/generated-type tests belong to the first E1 consumer, with domain
scenarios mapped to E1 autosave/recovery and E5 submission. Proposal only; exact
payloads/routes/time budgets and remaining shared/persistence gates are still open.

User approved bounded automatic recovery followed by truthful unresolved feedback and
Retry on 2026-09-24; exact timing remains contract work. The next draft-input proposal
preserves incomplete typed values through acknowledged save/reopen, distinguishes
draft persistence from request validation, and requires explicit input-format context
and safe bounds. It maps §7/date-input UX/ADR-0118 to E1 autosave scenarios; domain
calculations remain E3 and submission remains E5. No readiness status changed.

User approved incomplete-input preservation on 2026-09-24; features and UX now record
that agreement. The [E1 acceptance map](../../apps/leave/docs/testing/e1-acceptance-map.md)
links 18 scenario groups to authoritative sources, approved work boundaries and intended
browser/API/database/shared-scaffold evidence. These are scenario IDs, not atomic
requirement IDs or finalized stories. No tests were implemented/executed and global
coverage/readiness remain pending. Next: consolidate remaining technical contract
parameters and surface only behavior-changing choices for product discussion.

---
project: Leave
status: epic-structure-approved
created: 2026-09-23
stepsCompleted: []
currentCheckpoint: Stories 2.1–2.19 approved; Story 2.20 employee work-profile assignment under discussion; readiness pending
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
| 4 | Switch organizations while editing | Features §1/7 switching acceptance example; L-0068. Save in the original organization before opening the selected workspace; failed saves offer Retry, Stay, or Switch anyway. Never transfer draft values; preserve previously saved content. | Two-organization browser journey and API scope checks, including failed/uncertain saves and no prior-organization content in the new workspace. |
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


Technical consolidation, 2026-10-01: current working tree was clean at resumption.
The existing `services/access` PtS owner now supersedes the earlier service-absence
assumption; extend it with compatible versioned Leave contracts rather than adding a
second Access owner. Content/deployment work also exists; ADR-0043 remains Proposed.
Current deployment documentation is historical evidence, not a live target check.

The owning identity and error contracts now capture this adoption path and the two
legacy error response families. The draft contract supplies concrete routes, bigint
wire representation, local scope/receipt coordination, draft input limits and bounded
save/recovery timing. Proposed product defaults awaiting discussion: 4,000-character
notes and retaining each duration mode's inputs across mode switches. Outstanding
identity/freshness, schema/key, environment/pin/browser and verification gates remain
explicit; no story, sprint-readiness or implementation milestone is marked complete.


User approved the 4,000-character note limit and per-duration-mode input preservation
on 2026-10-01; features, UX and the draft contract now record them as agreed. The
identity contract adds concrete person/account/actor mapping, v2 response fields,
explicit-grant adoption and employee-work-timezone date interpretation. One new
behavior is proposed for discussion: an already-checked draft-only save can finish
within its bounded execution window despite a concurrent remote employment change;
the next action rechecks. This does not apply to submission/approval/calculation.
No identity migration, runtime or readiness verification is claimed.


Approval, 2026-10-01: the user accepted the in-flight draft-save boundary and requested
platform-wide treatment. Platform ADR-0044 now defines the reusable bounded shared-input
observation pattern for draft preservation without consequential effects. Leave adopts
a ten-second total execution bound; other applications select and verify their own.
New execution rechecks; submission/approval/reservation and entitlement consistency
remain excluded. Runtime implementation and readiness are still pending.


Planning checkpoint, 2026-10-01: draft input v1 now has an exact stored envelope,
explicit format IDs and parse examples without changing approved preservation rules.
The existing implementation tracker contains a scoped E1 pre-story contract status
map, distinguishing design prerequisites from later failing/passing implementation
evidence. No full SP readiness run occurred and no global coverage claim is made.
The user approved current/previous major Chrome, Edge, Firefox and Safari, including
Android Chrome and iPhone/iPad Safari. Requirements, UX and the acceptance map now
record the policy and distinguish actual browser evidence from engine emulation.


Technical block completed at design level, 2026-10-01 (fingerprint algorithm/key proposal
superseded by the simplification below): the draft contract now specifies
local PK/FK/uniqueness/lifecycle rules, restricted-role/RLS authority, immutable receipt
writes and overflow/error handling. Fingerprints use a versioned canonical command
with HMAC-SHA-256 and JCS, backed by an application/environment keyring; rotation and
restore must preserve old receipt verification. The tracker and E1 scenarios identify
remaining implementation/verification evidence. No application code, schema migration,
key generation or test execution occurred; no readiness gate was marked passed.


Scope correction, 2026-10-01: user confirmed no need to cater for old Expense receipts.
Platform ADR-0045 removes historic Expense receipt/purchase conversion/compatibility
from prerequisites. Shared identity and current PtS/Access/Content adoption requirements
remain. Operation outcome records (previously called operation receipts) are unrelated:
Leave has no old ones to migrate, but future duplicate-safe recovery remains required.


Fingerprint simplification and security follow-up, 2026-10-01: following the user's
complexity discussion, E1 now selects versioned SHA-256/JCS for retry consistency,
without a fingerprint keyring or rotation requirement. The user requested logging
stronger protection for future applications and raised AI-assisted attack concerns.
The [platform enhancement candidate](../../platform/docs/architecture/contracts/operation-fingerprint-security-evolution.md)
records HMAC, its specific database-disclosure benefit, limits, adoption triggers and
key lifecycle costs. This is not a blanket recommendation for every application's
sensitive data. Leave’s existing pilot security assessment must evaluate predictable
health-related values and retained outcomes, adopting stronger protection before
exposure if needed. Draft contract, tracker and acceptance map reflect the baseline;
accepted ADRs and readiness gates remain unchanged. No implementation performed.


Next contract discussion, 2026-10-01: recorded the user's agreement with the
fingerprint simplification and risk-based security enhancement. The shared employment
contract now proposes exact discovery/effective response variants, errors and minimum
fixtures, including an explicit setup-needed state when a relationship has no periods.
That setup handling remains a discussion item. Identity migration, full API schemas,
environment/scaffold design and requirement coverage gates remain open; no individual
story or implementation readiness is declared complete.


Contract discussion continuation, 2026-10-01: user approved setup-needed handling
for missing employment periods, preserving drafts/authorized reading and blocking
creation/editing until corrected. The shared contract now proposes concrete Access
v2 check/list schemas, current-authority organization selection, bounded pagination,
service-versus-user failure mapping and compatibility fixtures. No access is inferred
from account login or employment. Identity baseline/migration ownership and other
pre-story gates remain open. No new story approved or implementation authorized.


Identity transition scope, 2026-10-01: organization-selection behavior approved. User
reports three noncritical production PtS users and can coordinate manual recreation
and user instructions. Select a supervised small-cohort identity transition, retaining
account UUIDs where convenient and mapping replacements/references if needed. No bulk
migration framework or zero-downtime transition is required for this cohort; existing
controlled migration, maintenance/recovery and scoped runtime-authority contracts
remain binding. Owning shared contract records baseline ownership and discovery
authority gaps. No production access, deletion, migration or user messaging performed.


Scope correction, 2026-10-01: user clarified that PtS and Scribeswell are read-only
applications. Remove the inferred user-document ownership/access migration from the
small-cohort transition. Preserve read-only application content and verify replacement
account sign-in, membership/grants and intended reading. Repository document endpoints
are not evidence of production user documents. No production data change performed.


Draft read continuation, 2026-10-01: user agreed to the retry/concurrency safeguards.
Owning draft contract now proposes current-context, active/read-only and discarded
response shapes, keeping input/revision snapshots consistent and protecting newer
local edits. Reads have no create/save effects. Wire design does not close schema,
compatibility, environment, scaffold or global traceability/readiness gates.


Environment discussion, 2026-10-01: proposed a dedicated synthetic local Leave stack
and fresh CI instances, with real Access/People/persistence for the first draft journey
and a separate actual Entra sign-in check. The [owning environment proposal](../../apps/leave/docs/testing/e1-environment-and-dependencies.md)
records inspected dependency differences, Access's current PtS requirements coupling,
service-owned resolution and remaining exact-pin/bootstrap/auth/browser evidence.
No standing hosted staging environment, installation or implementation authorized.


Environment approved, 2026-10-02: user accepted local-first synthetic development,
fresh isolated CI and separate real Entra verification. Next discussion is measurable
E1 performance: proposed healthy-network p95 open/close within 3 seconds and save
acknowledgement within 2 seconds of dispatch. Workload is provisional pending expected
organization size/concurrency; no latency or capacity claim is verified. Exact pins,
bootstrap, browser evidence and other existing readiness gates remain open.


Performance discussion, 2026-10-02: user supplied 1,000 employees as expected largest
organization and endorsed 500 as the normal test scenario. Environment contract now
includes both sizes and explains the proposed timing budgets as engineering judgment
informed by UX guidance, not prescribed save-time standards. Concurrency/history
assumptions and proposed latency targets remain open; no benchmark performed.


Performance agreement/scaffold discussion, 2026-10-02: user accepted retaining the
initial E1 timing targets (p95 save acknowledgement ≤2 seconds after dispatch;
open/close ≤3 seconds) with 500-employee baseline and 1,000-employee qualification.
Concurrency/history remain explicit test assumptions. The authoritative tracker now
bounds generator foundation, generated reference evidence and same-item promotion
at each Leave consumer. Generated-slice/readiness gates remain binding; no code or
new story approval is inferred from this scaffold proposal.


## E1 entry requirement traceability — 2026-10-02

User approved the scaffold boundary: standard sign-in/session/organization/access
integration; optional typed employment integration; shared owners retain records and
rules, and Leave retains domain decisions. The references below decompose approved
sources into coverage entries, not new product requirements. `E1-ENTRY-*` labels are
planning traceability identifiers only. This is a scoped inventory, not completion of
the global FR/NFR/UX mapping or implementation readiness.

Source keys: F1 = [features §1](../../apps/leave/docs/features.md#1-identity-ngo-context-and-onboarding);
FP = [Permissions](../../apps/leave/docs/features.md#permissions);
A = [spine AD-1/2/12](../../apps/leave/docs/architecture/ARCHITECTURE-SPINE.md);
SC = [owning shared contract](../../platform/docs/architecture/contracts/identity-access-employment-e1.md);
UX-S = [platform session recovery](../../platform/EXPERIENCE.md#session-recovery-and-return-navigation);
UX-L = [Leave experience](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md);
T = [E1 acceptance map](../../apps/leave/docs/testing/e1-acceptance-map.md).

| Entry | Required outcome from source | Owning delivery and evidence |
| --- | --- | --- |
| E1-ENTRY-01 | Entra sign-in through Supabase establishes verified identity. F1. | Shared auth integration plus Leave entry; T01/12, actual provider callback evidence distinct from local fixture login. |
| E1-ENTRY-02 | Login alone grants neither organization access nor employment; joining requires authorized provisioning. F1, FP, SC. | Access/identity fixture provisioning and protected Leave boundary; T13/15; no invitation/admin UI prerequisite. |
| E1-ENTRY-03 | List only current accessible organizations, including pagination; show empty versus unavailable distinctly. SC, A. | Access v2 and Leave selector; T01/13/17. Missing employee setup must not hide otherwise authorized application access. |
| E1-ENTRY-04 | Select and prominently display the organization; reuse the same identity across organizations without transferring context. F1, ADR-0039. | Leave shell and shared selector; T01/09/15/16. Initial selection now; unsaved-edit switching belongs to the later E1 capability. |
| E1-ENTRY-05 | Resolve current capability and scope on each protected action; queued/new execution rechecks after revocation. F1, A, ADR-0019/0021. | Access and consumer adapters; T13/15, actual current-state and bounded-execution evidence. |
| E1-ENTRY-06 | Isolate organization and employee references; browser business data uses Leave API and shared data uses authorized HTTP. F1, A, SC. | Generated boundary, Access/People and Leave integration; T15/18 under actual restricted roles, not UI filtering alone. |
| E1-ENTRY-07 | Missing account/person/actor/employment setup is distinct from denied authority or service failure; no automatic record creation. SC, ADR-0042. | Typed service/Leave adapters; T13/14/17. Accountless model is supported without an E1 administration screen. |
| E1-ENTRY-08 | Resolve only the minimum employment/timezone inputs needed by draft use; null department/location/supervisor is valid. SC, ADR-0040/0041/0044. | People read and Leave draft-context consumer after entry; T14/15. Policies, schedules and reporting workflows are not all prerequisites for sign-in. |
| E1-ENTRY-09 | Renew/check authentication safely, validate return targets and clear previous-user protected context. UX-S, UX-L, ADR-0032. | Shared session foundation in first protected screen; T12/15/17. Full saved/unsaved draft recovery is verified with the later E1 recovery journey. |
| E1-ENTRY-10 | Record security-relevant identity and organization-context changes with safe attribution. F1, ADR-0023/0025. | Identity/Access and Leave context owner; uses the approved audit/context ownership contract; verify its schema and atomic failure semantics in the owning item. No claim that diagnostic logs alone satisfy business/security audit. |
| E1-ENTRY-11 | Accessible keyboard/focus, mobile and loading/denied/setup/unavailable states follow approved design; protected content is removed on lost access. UX-L, A. | Shared controls and Leave shell; T12/13/16/17, browser plus human accessibility evidence. |
| E1-ENTRY-12 | Proven generic integrations/templates update with their consuming work; generated slice runs locally and in CI. Features product principles, tracker Phase 1. | Platform foundation and every first consumer; T18 and explicit scaffold/shared-UI/context/docs/ADR impact evidence. |

Here T01 means E1-AC-01 and so on. Exact executable test IDs are assigned by the
owning delivery item; these scenario references do not claim tests already exist.

### Proposed delivery boundaries for entry

Deliver in dependency order, each with its own acceptance evidence; no item relies
on a future story to make its already-exposed behavior safe:

1. Minimum generator and authenticated domain-neutral reference foundation, under
   the existing generated-slice gate. It consumes only the currently supported Access
   contract/capabilities it needs; it must not falsely demonstrate Leave v2 readiness.
2. Shared identity baseline and the small-cohort transition design, then the Access v2
   permission check and organization discovery. Split baseline/check/discovery into
   separate bounded stories where needed; retain v1 compatibility throughout the
   supported path or use the already agreed planned-maintenance route.
3. Generated Leave sign-in and organization-selection journey consuming the verified
   shared contracts, with current access, safe setup/failure and accessible shell.
   No employment writer, draft start, balance or approval screen is required here.
4. Minimum shared People reads and Leave employee-context integration before the
   first create/resume draft capability. Keep accountless/rehire/scoped constraints
   but do not deliver E2's employee administration as an entry prerequisite.

These are proposed delivery boundaries, not finalized story IDs or single-session
size claims. Formal Given/When/Then stories follow the remaining source mapping and
relevant contract closure. The entry extraction identified security-audit ownership
and failure handling as a concrete remaining contract gap. Browser execution projects,
pins and identity schema baseline also remain open. No implementation authorized.


Application access refinement, 2026-10-02: user approved the entry delivery grouping
and requires configuration of organization and user app access; PtS sign-in must not
reveal Leave without applicable organization access. Scribeswell has no organization
concept. [Proposed ADR-0046](../../platform/docs/architecture/decisions/0046-application-availability-and-access-scopes.md)
separates catalogue availability, organization enablement and user grants, proposing
account-scoped Scribeswell access without a public organization. Its admission policy
awaits discussion. Directory's current all-enabled-apps listing needs replacement
with current Access-derived discovery; direct APIs enforce the same scope. Add to
E1-ENTRY-02/03/05/06 and E1-AC-01/13/15/17/18. E1 needs configured fixtures/enforcement;
shared administration screens stay E2. This precedes the outstanding audit contract.


Scribeswell/access clarification, 2026-10-02: user permits public unsigned-in reading
now; public account registration is future work, and selected app access (initially
PtS) should confer Scribeswell access. Proposed ADR-0046 now distinguishes public
reading, future account capabilities and explicit one-way derived grants. Neither
registration nor public reading grants PtS/Leave or creates an organization. Domain
recommendation remains under discussion; current deployment documents place PtS at
the scribeswell.com apex and the reader under /scribeswell/, so any canonical-domain
change needs deliberate route mapping. No configuration or deployment changed.


Hostname discussion, 2026-10-02: user approved scribeswell.com for the public reader,
pts.boabab.com and leave.boabab.com, with no optional Scribeswell suite alias. Current
apps are not actively used; old users/bookmarks need not constrain separation, so no
legacy redirect/user-migration project is required. Domain/deployment configuration
is not executed. User asked about organization hostnames; ADR-0046 records a pending
recommendation to retain app hostnames with authorized organization context, deferring
organization-branded portals until there is a concrete need.


Audit discussion, 2026-10-02: user agreed to app-name hostnames with authorized
organization selection, no organization subdomain system for E1. Returning to
E1-ENTRY-10, the [owning audit proposal](../../platform/docs/architecture/contracts/e1-security-audit-ownership.md)
assigns provider authentication evidence, Access identity/grant changes and Leave
context/draft/sensitive-read evidence. Local mandatory records gate their effects;
remote diagnostic/export failure does not. Failure behavior awaits discussion;
selection/read schemas, retention and executable evidence remain open.


Audit agreement and wire design, 2026-10-02: user approved mandatory local evidence
with nonblocking remote export. Owning contract now specifies minimal idempotent
organization selection/outcome endpoints, separate from employment-bound draft
records, and sensitive draft release events without payload duplication or revision
changes. Required race/failure fixtures link to E1-ENTRY-10 and the acceptance map.
No runtime readiness claim; schema review, retention and executable evidence remain.


Admission contract discussion, 2026-10-02: [owning wire/behavior proposal](../../platform/docs/architecture/contracts/application-admission-and-discovery.md)
separates Access admission from Directory publication, proposes non-destructive
organization-app suspension and restoration of still-valid grants, and specifies
versioned public/complete/unavailable launcher outcomes plus direct-API enforcement.
These new semantics await discussion. E1 supplies fixture enforcement; administration
UI stays E2. No access changes, public signup or derived-grant engine implemented.


Application admission agreement, 2026-10-02: user approved non-destructive suspension,
restoration of still-valid access and usable public Scribeswell with explicitly
unavailable protected discovery. Consolidated accepted platform ADR-0046; predecessor
ADRs unchanged. Owning contract now specifies internal Access app discovery, restricted
Directory caller, safe minimal response and bounded failure mapping. Features, spine
and agent context link the accepted policy. Exact schema/migration/tests remain gates.
Return to remaining E1 draft requirement extraction; global coverage is not complete.


## E1 draft requirement traceability — 2026-10-02

Scoped extraction of approved draft behavior. `E1-DRAFT-*` labels identify planning
coverage entries, not replacement source requirements. Source F7 =
[features §7](../../apps/leave/docs/features.md#7-leave-application-experience);
DC = [owning draft contract](../../apps/leave/docs/architecture/contracts/e1-draft-persistence-and-recovery.md);
UX = [Leave experience](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md);
T = [E1 acceptance map](../../apps/leave/docs/testing/e1-acceptance-map.md).
Existing E1 entry controls apply to every protected capability below.

| Entry | Required behavior and authority | Existing work boundary; acceptance coverage |
| --- | --- | --- |
| E1-DRAFT-01 | Explicit Apply creates/resumes one employee/organization draft atomically; database uniqueness, no initial overwrite. F7, P-0034, DC. | 2; T02/11/15 |
| E1-DRAFT-02 | Apply resumes retained content, with unfinished-application note; no Drafts section or notification badge. F7, UX. | 2–3; T01/03/16 |
| E1-DRAFT-03 | Start replay resolves its original draft; a never-seen stale-generation start fails rather than creating/resuming a replacement. F7, DC, P-0033/0034. | 2, safeguarded before later discard; T02/06/11 |
| E1-DRAFT-04 | Current/future employment may prepare with explicit access; confirmed ended employment is read-only; no periods is setup-needed, while missing timezone is a nonblocking notice; rehire retains the same relationship/draft. F7, DC, shared contract. | 2–3; T13/14/15 |
| E1-DRAFT-05 | Draft creates no reservation/request/approval and Saved is not validity/eligibility confirmation. F7, DC. | 2–3; T01/03 |
| E1-DRAFT-06 | Preserve exact incomplete/invalid/reversed typed input, blank selections and input-format context; no silent defaults, swaps or misleading zero result. F7, UX, DC input v1. | 3; T03/17 |
| E1-DRAFT-07 | Preserve inactive duration-mode entries; selected mode alone applies later. Notes cap at 4,000 Unicode code points with no truncation; enforce declared field/body limits. F7, UX, DC. | 3; T03/16/17 |
| E1-DRAFT-08 | Serialize/coalesce same-tab saves, apply revision acknowledgements without overwriting newer typing, truthful Saved/Not saved and bounded scheduling. F7, L-0118, DC. | 3; T04/06/07 |
| E1-DRAFT-09 | Two-tab stale revision pauses saving, retains local edits where practical and offers authorized Review saved draft; no automatic merge/overwrite. F7, L-0118. | 3; T05/15 |
| E1-DRAFT-10 | Lost-response recovery uses identical operation/input; bound retries, then honest unresolved state; no competing fresh save or false rollback claim. DC, P-0012. | 3; T06/07/17 |
| E1-DRAFT-11 | Close saved immediately, flush pending saves, wait safely for in-flight resolution; inline failure offers Retry; exit offers Stay/Close anyway without deleting the draft or promising rollback. Escape/mobile Back equivalent. F7, UX, P-0050, L-0123. | 3; T08/16 |
| E1-DRAFT-12 | Reopen same acknowledged input; passing selected dates causes no automatic expiry; later validation cannot rewrite stored input. F7, DC. | 3; T01/03/14 |
| E1-DRAFT-13 | Save in original organization before switching; failure preserves scope and offers approved choices; successful target selection is audited; never carry another organization's values. F7, L-0068, audit contract. | 4; T09/13/15 |
| E1-DRAFT-14 | Cancel discard leaves draft unchanged; confirmed discard atomically removes payload, closes/increments lifecycle evidence and rejects late writes. No restore UI or new draft without explicit action. F7, DC, P-0033. | 5; T10/11 |
| E1-DRAFT-15 | No automatic active-draft or operation-evidence expiry in E1; no notes/form snapshots duplicated into outcome/audit records. F7, DC. | First persistence onward; T10/11/17 |
| E1-DRAFT-16 | Renew session and restore authorized same-user context; account change or revoked access removes protected content; never promise unsaved text survived redirect. UX, P-0032. | Safe foundation from entry, full journey in 6; T12/13/15 |
| E1-DRAFT-17 | Current authorization and shared employment observation precede short local transaction; local revision/lifecycle and required audit remain atomic; timezone/date guards apply only when dated interpretation is actually used, under P-0049/L-0122. DC, P-0022/0044, audit contract. | First writer/read onward; T02/06/10/13/14/15 |
| E1-DRAFT-18 | Desktop drawer/mobile page, keyboard/focus, readable statuses and errors follow approved UX; unsupported/malformed responses cannot become false Saved. UX, P-0031, DC. | Every consuming boundary; T16/17 |
| E1-DRAFT-19 | Measure agreed normal-operation latency at 500/1,000 employee fixture scales; failure scenarios preserve data regardless of speed. Environment contract. | 2–6; T01/04/06/07/08/13/15 |
| E1-DRAFT-20 | First-consumer changes update reusable templates/clients/controls and generated-sample checks with explicit impact decisions. Features product principles, tracker Phase 1. | All; T18 |

T02 means E1-AC-02, etc. Full application FR/NFR/UX extraction remains incomplete.
E3 owns duration/balance/eligibility calculation, E4 attachments (including P-0038),
and E5 submission/reservation; E1 must neither fake those results nor declare their
requirements covered by a preserved draft. Before edit-form readiness, bind minimal
Leave-type choice metadata/fixture reads explicitly without introducing the whole E3
policy editor. This dependency is not yet an executable endpoint contract.

### Candidate Story E1-D1: Create or resume my application draft

**Planning draft for discussion — provisional label, not implementation-ready.**
Dependencies: approved generator/reference foundation, generated Leave entry, current
Access admission, verified People read and local minimal setup contracts. Final story
numbering follows the bounded prerequisite stories. No dependency on a future discard
UI to make creation/retries safe; use synthetic closed-history fixtures to verify guards.

As an employee with authorized Leave access,
I want Apply for leave to create or reopen my one unfinished application,
So that I can continue without duplicate drafts or losing existing work.

**Acceptance Criteria:**

**Given** current own-read/manage access, organization enablement, current or future
employment/ownership and required scope setup, with no active draft (missing work
timezone alone is nonblocking under platform ADR-0049 and Leave ADR-0122),
**When** I explicitly choose Apply for leave,
**Then** one organization/employee-owned active draft is committed and opened,
**And** no submitted request, entitlement reservation or approval is created.

**Given** an authorized active draft already exists,
**When** I choose Apply for leave,
**Then** that draft's saved input is read unchanged at its current revision,
**And** My Leave displays the unfinished-application note without a separate Drafts
section or notification badge.

**Given** two starts run concurrently for the same eligible employee/organization,
**When** both are resolved,
**Then** both refer to the same active draft and neither overwrites its values,
**And** restricted-role database constraints enforce the invariant.

**Given** a response is lost or an old start is replayed after its draft closes,
**When** the original operation is resolved under current authorization,
**Then** its recorded identity is retained without creating/resuming a replacement,
**And** an unseen stale-generation start is rejected with the agreed refresh path.

**Given** ended employment, incomplete setup, revoked access or unavailable verification,
**When** I attempt to start/resume,
**Then** the agreed read-only/setup/denied/unavailable result is shown distinctly,
**And** existing drafts remain stored without exposing unauthorized content or creating
new records to repair setup automatically.

**Given** required draft attribution or atomic operation outcome persistence fails,
**When** creation is attempted,
**Then** the draft cannot commit without that required evidence,
**And** uncertain commit follows operation recovery without false success. Ordinary
own-draft reads require current authorization but no separate read-audit write.

**Scope/sizing:** This candidate delivers create/resume and safe reading; editing is
not enabled until the autosave/close item supplies its safety guarantees. If too large
for one dev agent, first split reusable persistence/recovery prerequisites into proven
reference work; do not omit authorization, uniqueness or lost-response safeguards.

**Traceability:** E1-DRAFT-01–05, 12, 15, 17–20; E1-AC-01/02/06/11/13/14/15/16/17/18,
with E1-AC-01 only partially covered until editing/close/reopen are delivered. Shared
mechanisms promote in the same item; Leave uniqueness/lifecycle remain application-owned.
Agent context/docs/ADR impacts follow approved boundaries; no new ADR required here.

**Readiness still open:** schema/constraint and safe-error mapping validation, exact
dependency compatibility, executable fixture/command design, source coverage and the
existing BMAD SP gate. This candidate neither closes those gates nor authorizes code.


Draft evidence agreement, 2026-10-02: user accepted the create/resume boundary and
clarified audit value. Keep creation/last-update attribution on the draft, compact
operation outcomes and minimal discard evidence; remove duplicate creation/autosave
audit and ordinary own-draft read events from the earlier proposal. Sources and
create/resume acceptance criteria now reflect this. Existing broader sensitive-access
audit requirements are not waived. Candidate remains subject to readiness gates.

### Candidate Story E1-D2: Edit, autosave, close and reopen my draft

**Planning draft for discussion — provisional label, not implementation-ready.**
Depends on E1-D1 and the proven create/read operation foundation. This parent also
owns the first draft-update revision/lifecycle and input-control proof; E1-WRITE/REF
do not establish mutable-editor behavior. Approved D2-A/D2-B boundaries below separate backend proof from browser integration.
Bind minimum leave-type choice metadata before readiness; E3's full policy editor and
calculation engine are not prerequisites. Existing scaffold/ATDD gates remain binding.

As an employee editing my authorized draft,
I want my entered details saved automatically and restored when I reopen it,
So that I can pause without re-entering work or losing changes silently.

**Acceptance Criteria:**

**Given** an editable draft,
**When** I enter leave type, duration mode, dates/duration or an optional note,
**Then** the input-v1 contract preserves the exact acknowledged values, including
incomplete/reversed input and inactive-mode entries,
**And** bounds are explained without silent truncation or invented defaults.

**Given** I pause typing or keep typing while no save/recovery is in flight,
**When** the agreed autosave trigger runs,
**Then** saves are serialized/coalesced with revision and operation identity,
**And** Saved applies only to the latest acknowledged input, never newer unsaved typing.

**Given** saved, saving or failed/uncertain input,
**When** I use Close, Escape or mobile Back,
**Then** the approved safe-close behavior applies, including immediate flush when
needed, bounded recovery and exit-only Stay/Close anyway under platform ADR-0050,
with inline Retry while editing,
**And** abandoning local edits never deletes the previously saved draft.

**Given** the draft save committed,
**When** I close and later reopen through Apply for leave,
**Then** the same saved input returns with its current authorized editability,
**And** past selected dates do not delete the draft, reserve entitlement or imply
submission validity. No E3 balance result or E5 submission success is fabricated.

**Given** another tab saved first, or this save's response was lost,
**When** my tab resolves its operation,
**Then** stale input cannot overwrite the newer revision, and uncertain saves retain
the original identity/input until resolved,
**And** the approved conflict/retry presentation preserves local edits honestly with
no automatic merge, new operation or silently advanced revision.

**Given** employment/access/setup changes,
**When** a subsequent protected action checks current state,
**Then** the agreed read-only/setup/denied/unavailable response applies,
**And** the approved bounded in-flight rule does not permit stale revisions,
closed-draft resurrection or access by a different user.

**Given** keyboard, desktop drawer or mobile-page use,
**When** I edit, receive save/error feedback and close,
**Then** focus, labels, status feedback and responsive controls follow the approved UX,
**And** current authority, attribution and recovery evidence remain consistent across
layouts without adding content copies or ordinary own-draft read audits.

**Traceability:** E1-DRAFT-05–12/15–20; E1-AC-01/03–08/12–18 as applicable. The full
saved-input first-slice journey becomes executable here; dedicated organization-switch,
discard and interactive reauthentication journeys remain subsequent E1 capabilities,
with their authorization/lifecycle safety already enforced by the first writer.

**Sizing/impacts:** Reuse the prior proven persistence/recovery mechanisms; this item
owns Leave form wiring, save scheduling and safe close/reopen. Promote proven generic
input/status/close handling and generated-sample checks in the same item. Leave field
meaning and lifecycle stay local. Split prerequisite mechanism work if needed rather
than shipping an unsafe autosave happy path. Agent context/docs/ADR decisions follow
existing approved boundaries; no new ADR. Exact fixture commands, toolchain/schema
validation and SP readiness remain required; no code or runtime evidence claimed.


Autosave story agreement, 2026-10-02: user accepted E1-D2's edit/autosave/close/reopen
boundary with its failure/concurrency safeguards. This is scope agreement, not a pass
of outstanding contracts, global traceability or implementation-readiness checks.

### Candidate Story E1-D3: Switch organizations without losing or mixing draft data

**Planning draft for discussion — provisional label, not implementation-ready.**
Depends on E1-D1/D2-A/D2-B, current app admission/discovery and the audited context-selection
contract. No new shared employee administration or cross-organization draft transfer.

As an employee with Leave access in more than one organization,
I want to switch organizations safely while working on a draft,
So that my work stays with the correct organization and I understand any save failure.

**Acceptance Criteria:**

**Given** I am editing in organization A and select currently eligible organization B,
**When** my latest input is successfully saved in A,
**Then** the application confirms authorized target selection and opens B's My Leave,
**And** A's draft stays in A with its acknowledged values; switching creates no draft in B.

**Given** A's draft is already saved with no newer input or uncertain operation,
**When** I select B,
**Then** no redundant draft save is required,
**And** current target authorization and required selection evidence still precede entry.

**Given** saving A's changes fails,
**When** the switch cannot safely complete,
**Then** I remain in A and the exit confirmation offers Stay / Switch anyway,
**And** Stay returns to the form with inline Retry and retained local input. Retry uses
existing safe operation recovery; Switch anyway abandons only unsent local input without
deleting A's saved draft or promising rollback of an already-sent save.

**Given** a source save's outcome is uncertain rather than confirmed failed,
**When** switching/recovery choices are shown,
**Then** the application does not claim the save rolled back or that abandoning local
edits can undo a server commit,
**And** any retained recovery identity remains scoped to A and cannot become a save in B.
No late acknowledgement can overwrite B's form or initiate navigation after Stay.
Simple exit presentation follows platform ADR-0050/Leave ADR-0123. Lost-reference/delayed-save
ordering remains a backend verification requirement; no custom recovery-record TTL
or durable sensitive form store is required.

**Given** A's save succeeds but B's access check, selection evidence or response fails,
**When** target entry cannot be confirmed,
**Then** A's acknowledged draft remains saved and no protected B workspace is displayed,
**And** Retry/Stay follow target-selection recovery; a definitive denial differs from
service unavailability and stale responses cannot complete an abandoned selection.

**Given** membership, app enablement or permissions change during switching,
**When** subsequent protected actions are checked,
**Then** only currently authorized data remains visible,
**And** the application uses a safe destination if A is no longer readable, rather than
claiming it can keep the user on protected content. B is checked independently.

**Given** separate tabs select different organizations,
**When** one tab switches or receives a delayed request response,
**Then** the other tab's organization is not silently changed,
**And** component state, caches, draft IDs and pending operations remain scoped to their
original organization/account; shared session account changes clear protected context.

**Given** keyboard or mobile use,
**When** I select an organization and handle save/switch feedback,
**Then** the active organization remains prominent, controls and errors are accessible,
**And** focus and return behavior follow the approved shell/task-surface UX.

**Traceability:** Features §1/7 switching example; Leave ADR-0068; E1-ENTRY-03–06/09–12;
E1-DRAFT-13/16–20; E1-AC-09/12/13/15/16/17/18. Use real two-organization persistence,
controlled save/selection faults, delayed responses and actual current-access changes.
No draft/form value from A may appear in B in API payloads, caches or rendered UI.

**Impacts/sizing:** Reuse D2 save/recovery and the shared selector/context acknowledgement.
Promote proven safe navigation/selection primitives and generated-sample fixtures in
the same item; Leave owns My Leave navigation and draft semantics. Documentation and
agent impact decisions follow the existing contracts; no new ADR. Exact commands,
remaining contract/coverage checks and SP readiness still gate implementation.


Organization-switch story agreement, 2026-10-02: user accepted E1-D3's boundary.
The recorded unresolved-save abandonment presentation remains a pre-readiness contract
check, not a claim that cancelling a browser request rolls back a server save.

### Candidate Story E1-D4: Deliberately discard my draft and start again

**Planning draft for discussion — provisional label, not implementation-ready.**
Depends on D1/D2-A/D2-B's safe persistence, operation recovery and revision/lifecycle guards.
No submission, attachment cleanup or restore-discarded-draft feature is included.

As an employee with an editable draft,
I want to deliberately discard it and later start a fresh application,
So that I can abandon the whole unfinished request without old saves bringing it back.

**Acceptance Criteria:**

**Given** my active draft is open,
**When** I choose Discard draft,
**Then** a confirmation clearly distinguishes deleting the whole saved draft from
abandoning only unsaved edits,
**And** cancelling keeps the form and its values, with no discard mutation. Ordinary
autosave behavior is not reclassified as a discard effect.

**Given** I confirm discard with current permission and editability,
**When** the guarded command commits,
**Then** editable payload removal, closed lifecycle, revision/scope-generation advance,
minimal discard evidence and operation outcome commit atomically,
**And** the application returns to My Leave with no unfinished-draft note and no
automatically created replacement. No note/form snapshot survives in discard evidence.

**Given** a save is pending or its outcome is uncertain,
**When** I attempt to confirm discard,
**Then** that operation is resolved under the existing serialization/recovery contract
before a competing discard is sent,
**And** no timeout is treated as proof that the pending save rolled back. After a
conflict, do not silently replace the discard's expected revision and resend it.

**Given** another tab changes the draft after the discard's observed revision,
**When** my discard request is checked,
**Then** it fails safely with the agreed revision conflict,
**And** reviewing the current authorized draft and a fresh explicit decision are
required before discarding newer work. No automatic retry with a new guard.

**Given** required local discard evidence fails or the response is lost,
**When** the outcome is handled,
**Then** an uncommitted failure preserves the draft and a possibly committed result
uses the same operation recovery without false success or false restoration,
**And** matching retries do not repeat revision/generation changes or audit effects.

**Given** the draft has been discarded,
**When** another tab's delayed save or an old create/discard retry arrives,
**Then** it cannot resurrect the contents, create a replacement or affect a newer draft,
**And** the user receives the agreed discarded/current-outcome recovery after current
authorization, without a restore-discarded-draft action.

**Given** I explicitly choose Apply for leave after discard is resolved,
**When** the new start commits using current authorized scope context,
**Then** a new draft identity is created with the declared empty input,
**And** no values are copied from discarded content; simultaneous starts still produce
one active draft and reserve no entitlement.

**Given** access or editability changes,
**When** I attempt discard or outcome recovery,
**Then** current permissions/employment rules and safe disclosure still apply,
**And** denial/unavailability cannot delete the draft through a fallback write path.

**Traceability:** F7 draft/discard and retention agreements; Leave ADR-0075/0118;
platform ADR-0012/0025/0033/0034/0035; E1-DRAFT-01/03/14/15/17/18/20;
E1-AC-02/06/07/10/11/13/15/16/17/18. Include confirmation cancel/confirm, two-tab
revision conflict, real restricted-role discard/save races, lost response, new start
and immutable minimal evidence checks. Operational backup expiry is separate; do not
promise immediate deletion from backups because live draft input was removed.

**Impacts/sizing:** Reuse existing safe confirmation, serialization, revision and
operation-recovery mechanisms. Promote proven generic terminal-state/late-write fixtures
and accessible confirmation primitives in the same delivery item; Leave owns its
discard state and new-start action. Documentation/agent impact decisions remain
required; no new ADR. Gates and exact test commands remain open; no implementation.


Discard/retention agreement, 2026-10-02: user accepted E1-D4 and retaining compact
closed draft rows for simpler checks. Discard clears form contents atomically; E5
submission clears them with permanent request/effect creation. Automatic age-based
cleanup remains deferred until coordinated outcome expiry/reference/audit rules exist.
No separate archive database and no immediate hard deletion of closed rows. Sources
now record this clarification; earlier suggested hard-delete alternative was not adopted.

### Candidate Story E1-D5: Return safely to my draft after sign-in expires

**Planning draft for discussion — provisional label, not implementation-ready.**
Depends on the entry/session foundation and D1/D2-A/D2-B/D3 recovery/context contracts.
Authentication/access checks already protect every earlier story; this item completes
the interactive reauthentication return journey and its user-facing recovery evidence.

As an employee whose sign-in expires while working,
I want to sign in again and return to my authorized draft,
So that saved work is recoverable without exposing it to another user or silently
submitting or overwriting anything.

**Acceptance Criteria:**

**Given** authentication can renew normally,
**When** the session needs renewal,
**Then** attempt the supported renewal flow before asking me to sign in,
**And** subsequent protected actions still check current access; token renewal does
not preserve a revoked grant or authorize an old queued action.

**Given** interactive sign-in is required while editing,
**When** the application detects that condition,
**Then** pause new saves/actions and explain Please sign in again to continue,
**And** distinguish acknowledged saved values from newer unsaved input without claiming
that unsaved text is durable or guaranteed to survive sign-in. Authentication-provider
unavailability is retryable unavailability, not a false permission-revocation message.

**Given** I return as the same verified account/person with current access,
**When** the validated return target is resolved,
**Then** re-establish the authorized organization/page/draft context and read current
saved values/editability,
**And** do not reset me to home unnecessarily, start a replacement draft, submit,
discard or confirm any consequential action automatically.

**Given** only saved values remain after returning,
**When** my draft opens,
**Then** explain that saved values were restored and newer unsaved changes may be lost,
**And** do not fill missing values from another user's/tab's context or silently merge
local text into a newer server revision. Supported retained local input, if any, follows
existing revision/recovery safeguards before it can be saved.

**Given** a save may have committed before authentication expired,
**When** recovery resumes with the original operation reference,
**Then** recheck current authority and resolve that outcome before another save,
**And** reuse identical payload only if the original payload remains available. Losing
local recovery context never proves rollback and never permits automatic reconstruction
of the lost write. After full-page return, reload current authorized saved state;
subsequent user edits use normal revision/lifecycle guards. Prove safe ordering against
delayed saves; no read or elapsed time proves rollback. Use supported validated auth
return navigation without the custom per-tab recovery record or TTL. No sensitive form
values or tokens in return URLs and no durable browser form store are introduced.

**Given** sign-in returns a different account, even one linked to the same person,
**When** the callback completes,
**Then** clear the previous account's protected local context and verify the new account's
own grants before showing any protected page,
**And** do not transfer prior local edits or operation-recovery authority between accounts.
The new account may later open permitted shared-person records through fresh checks.

**Given** the organization/draft is no longer accessible, has been discarded, or is
now read-only,
**When** I return,
**Then** show the appropriate authorized lifecycle/access state or safe destination,
**And** reveal no stale protected content and never infer that access loss means deletion.

**Given** an invalid or external return URL, or repeated/late auth callbacks,
**When** return navigation is evaluated,
**Then** only a validated permitted internal destination can be opened,
**And** no callback overwrites newer navigation, duplicates context effects or leaks
credentials/form data through URLs, logs or another tab's account context.

**Traceability:** Features §1/7 session/failure requirements; platform ADR-0032 and
platform EXPERIENCE Session Recovery; Leave EXPERIENCE Session expiry/Request no
longer accessible; E1-ENTRY-01/05/07/09/11; E1-DRAFT-10/16–18/20;
E1-AC-06/07/12/13/14/15/16/17/18. Include synthetic browser expiry/account-change
fixtures and separate real Entra/Supabase callback evidence in the agreed isolated
environment. Cross-account disclosure and invalid return targets need direct API/client
contract evidence as well as browser flows.

**Impacts/sizing:** Reuse and promote the proven shared auth-return/error/recovery
mechanism with generated-app fixtures; Leave owns its draft/lifecycle destination.
No custom authentication provider, employee linking UI or browser offline editor.
Agent context and docs update in the same item; accepted ADRs unchanged. Remaining
return-context schema, exact commands/toolchain, global coverage and SP gates remain
open. The candidate is not implementation authorization or test evidence.


Sign-in recovery agreement, 2026-10-02: user approved E1-D5's boundary. All five
draft-specific candidate boundaries have now been discussed; their readiness gaps
remain. Coverage check found that sign-in/organization entry had source mapping and
approved grouping but no formal candidate, supplied below. This is not E1 completion
or a substitute for the global requirement inventory or shared prerequisite stories.

### Candidate Story E1-A1: Sign in and enter an authorized Leave organization

**Planning draft — formalizes the previously approved entry boundary; provisional
label, not implementation-ready.** Dependencies: verified generator/reference
foundation, shared identity/Access adoption, app admission/discovery and context-audit
contracts. These prerequisite delivery items must precede this candidate; no later
draft/People administration story is required just to select an authorized organization.

As a user granted Leave access,
I want to sign in and choose an organization I may access,
So that I enter the correct workspace with clear context and appropriate permissions.

**Acceptance Criteria:**

**Given** I am not signed in,
**When** I sign in through Microsoft Entra and Supabase Auth,
**Then** the application obtains verified identity and loads current Leave access,
**And** neither successful sign-in nor a legacy role claim alone grants organization
or application access. Local fixture login is not proof of this provider journey.

**Given** my account can use Leave in one or more organizations,
**When** I enter Leave,
**Then** selection includes only organizations with current app admission, membership
and applicable capability, including all pages of the list,
**And** after authorized selection the shell prominently identifies the organization.
No draft, employee or grant is created merely by selecting it.

**Given** I have no eligible Leave organization or access cannot be checked,
**When** the entry screen resolves,
**Then** the confirmed no-access outcome and retryable unavailable outcome are distinct,
**And** public Scribeswell remains independent; PtS access alone never reveals Leave.

**Given** an organization is selectable but my employee mapping/setup is incomplete,
**When** I enter its workspace,
**Then** application entry is not denied solely for lack of employment,
**And** attempting an employee-only capability uses the agreed setup-needed response
without automatic linking, grant creation or fabricated employment.

**Given** a listed organization is subsequently disabled or my membership/grant revoked,
**When** selection or another protected request runs,
**Then** current authority is rechecked and the direct API rejects unauthorized action,
**And** a cached listing, bookmarked URL or old selection acknowledgement grants no access.

**Given** organization selection is retried or its response is lost,
**When** the original operation resolves,
**Then** one required selection event/result exists and safe recovery confirms the
original target only for the current pending transition,
**And** audit persistence failure does not acknowledge entry, while remote log-export
failure cannot undo already-durable selection.

**Given** keyboard/mobile use, session expiry, account change or an unsafe return URL,
**When** the shell/entry flow handles it,
**Then** accessible selection, safe verified return navigation and previous-user data
isolation apply from the first protected screen,
**And** no future recovery story is needed to make entry safe. E1-D5 later verifies
full draft-return behavior using this foundation.

**Traceability:** E1-ENTRY-01–07/09–12; features §1/Permissions; spine AD-1/2/12;
platform ADR-0019/0021/0031/0032/0039/0042/0046; E1-AC-01/12/13/15/16/17/18.
Source requirements for employee preparation remain with the People/context consumer
and E1-D1, not falsely marked complete here.

**Impacts:** Reuse and promote generated auth/access/discovery/context clients and
accessible shell controls with disposable-app evidence. Leave owns its landing
workspace and capability mapping; no employee admin, balance, approval or audit console.
Record scaffold/shared-UI/agent/docs/ADR decisions in the delivery item; no new ADR.
Exact commands, migration/schema compatibility, pins and SP readiness remain pending.

### E1 candidate coverage checkpoint — 2026-10-02

| Approved user-facing boundary | Candidate | State |
| --- | --- | --- |
| Sign in/select organization | E1-A1 | Formal candidate now recorded against already-agreed entry behavior |
| Create/resume draft | E1-D1 | Boundary agreed, simplified attribution applied |
| Edit/autosave/close/reopen | E1-D2 | Boundary agreed |
| Switch organization while editing | E1-D3 | Boundary agreed; inline Retry and exit-only Stay/Switch anyway under platform ADR-0050 |
| Discard/new explicit start | E1-D4 | Boundary agreed; compact closed-row retention reaffirmed |
| Recover after interactive sign-in | E1-D5 | Simplified saved-draft return agreed; supported callback and delayed-save ordering evidence remain |

These labels are provisional, not six implementation-ready stories. Final numbering
includes bounded prerequisite items and dependency order. Still needed: generator/
reference delivery decomposition, shared Access/People schema/migration/provisioning
items, minimal leave-type metadata read, exact pins/browser execution projects,
remaining recovery contracts and bidirectional full FR/NFR/UX coverage. Separate design
readiness from later failing/passing runtime evidence; preserve the Phase 1 exit gate.


### Candidate Story E1-P1: Generate a runnable application foundation safely

**Planning draft for discussion — provisional prerequisite label, not implementation-ready.**
Owner: platform builder; first consumer: Leave. This begins the approved minimum
foundation. It does not claim the later authenticated reference-slice exit gate passed.

As a platform/application developer,
I want to generate a runnable application foundation with owned configuration and tests,
So that Leave and later applications start consistently without copying another app's
server code or manually repairing incomplete templates.

**Acceptance Criteria:**

**Given** a valid application identifier, display name and explicit target configuration,
**When** I run the documented generator command against a disposable target,
**Then** it creates an app-owned React/TypeScript web shell, FastAPI API foundation,
configuration examples, explicit test/build/start commands and owned migration layout,
**And** all template placeholders resolve, generated code is syntactically valid, and
no Leave business entity, employee master or permission grant is created.

**Given** the generated application's documented locked toolchain and local configuration,
**When** its verification commands run locally and in CI,
**Then** dependency installation, type-check, focused tests, build and API startup/health
succeed using the generated output rather than the template source,
**And** the browser can load the shell without an unintended production service call.
A running shell/health endpoint is not proof of authentication or business readiness.

**Given** missing/invalid required configuration or an unsupported generation option,
**When** generation or startup validates it,
**Then** an actionable error identifies the problem without exposing secrets or falling
back to production settings,
**And** unsupported or unfinished options are rejected rather than advertised as working.

**Given** existing target files, a path-escaping application name or an invalid destination,
**When** generation is attempted,
**Then** it cannot overwrite user files or write outside the selected permitted target,
**And** conflicts are reported before publication, with no partially generated output
left claiming success. An existing documentation-only silo such as Leave is supported
by adding only nonconflicting generated paths while preserving its docs unchanged.

**Given** the same template version, input and locked dependency configuration,
**When** I generate into two clean disposable targets,
**Then** the relevant generated source/configuration is reproducible,
**And** a small generation manifest identifies template version and supplied nonsecret
inputs without embedding credentials, workstation paths or production identities.

**Given** the generated backend and migration entry points,
**When** the API starts,
**Then** it does not run migrations or use deployment-only database credentials,
**And** the owner migration layout excludes other owners/Supabase-managed schemas.
No application tables are created merely to fill the scaffold; the reference story
adds only the example record it needs under its own failing acceptance test.

**Given** the generation feature is completed,
**When** its delivery evidence is recorded,
**Then** it includes an initially failing generation acceptance, passing disposable
output checks, exact commands/results, documentation and a scaffold changelog,
**And** generated agent guidance links authoritative specs/ADRs and BMAD rules rather
than copying a competing specification or lifecycle. Generated-file ownership and
manual extension points are documented so later changes update the correct source.

**Scope/sizing:** Implement the minimum app generation path and reusable rendering/
validation core. A separately bounded service-only variant follows when Access/People
foundation work needs it; no wizard, template marketplace, retrofit engine or complete
feature-generator catalogue. The generated foundation exposes no protected business
endpoint until the next reference work supplies real auth/authorization. Existing
AppLauncher/templates/examples may be reused after verifying actual source; placeholder
README claims do not count as implementation.

**Traceability:** Features product purpose/continuous scaffold evolution; tracker
Phase 1 generation and disposable-app checks; E1-ENTRY-12; E1-AC-18; platform
ADR-0003/0014–0018/0020/0023/0025. This is partial foundation coverage, not the
authenticated organization-scoped read/write reference acceptance.

**Impacts:** Owning generator/templates/tests/docs/changelog change together. Shared
UI uses only existing proven pieces needed for the shell; no new generic component
library in this story. Agent-context output is required; accepted ADRs unchanged.
Finalize supported inputs, output ownership, dependency pins/workspace lock ownership
and executable commands before implementation readiness. No generator code written.

Proposed next prerequisite: prove the generated foundation with an authenticated,
organization-scoped reference record read/write. Include real HTTP authorization,
restricted-role persistence, isolation, attribution and migration evidence there;
then use proven mechanisms in the shared/Leave consumers. Keep dependent items
sequential and bounded rather than claiming P1 alone closes Phase 1.


Generator agreement, 2026-10-02: user approved E1-P1, explicitly reaffirming owned
migrations run through controlled deployment rather than API startup.

### Candidate Story E1-REF: Prove a generated authenticated application against real persistence

**Boundary refinement approved 2026-10-08:** this is the maintained platform verification
application, not a separate disposable product. REF owns its reusable journey and local/CI
proof; VERIFY deploys the same source/tests to hosted environments. Freshly generated CI
instances remain disposable generator-test artifacts. WRITE supplies the prior backend.

**Planning draft for discussion — named prerequisite, final number assigned by dependency
order; not implementation-ready.** Owner: platform builder/reference verification.
Depends on E1-P1 and an earlier bounded Access capability-registration/current-check
item plus the identity baseline required by the selected wire version. This conversation
previews the reference outcome; it does not schedule those prerequisites after it.

Current Access accepts three PtS permissions and PtS/Content caller keys only. A
generated reference must have its own isolated app namespace, exact read/write
capabilities, service identity and explicit test grants. It cannot borrow PtS permissions
for a write or count a mocked authority response as shared-service proof. Reuse the
chosen current Access contract after its required extension; do not build a second
authorization server or require People employment for a generic example.

As a platform/application developer,
I want a generated sample to demonstrate authorized organization-scoped read/write,
So that I can trust the foundation before using it for Leave business data.

**Acceptance Criteria:**

**Given** a freshly generated disposable sample, synthetic users and two organizations,
**When** an authorized test user signs in, selects an authorized organization and
creates a simple example record,
**Then** browser → generated API → real current Access HTTP check → owned database
persistence succeeds and the record is returned on a later authorized read,
**And** the browser has no direct business-table path and no shared server imports exist.
The sample records only a bounded non-sensitive label; it is not a draft/HR product.

**Given** the user lacks the exact write/read capability, the organization's app is
disabled, or membership is revoked while the token remains valid,
**When** the relevant new protected request runs,
**Then** it fails under the current access contract,
**And** changing UI state or directly calling the API cannot bypass that decision.
The approved already-authorized bounded-execution rule still applies.

**Given** a record belongs to organization A,
**When** a caller operating in B submits A's record ID or a pooled connection is reused,
**Then** API ownership checks and actual restricted-role RLS prevent disclosure/write,
**And** missing scope, rollback and transaction completion leave no reusable tenant
authority in that connection. Test with nonowner/non-bypass runtime identities.

**Given** current authorization cannot be checked or request validation fails,
**When** the sample handles the failure,
**Then** typed safe errors distinguish unavailable, denied and invalid input,
**And** logs/errors contain no credentials or raw payload dumps. Clients derive their
contract from the declared API; no English-message parsing or success-shaped failure.

**Given** a create is retried or its response is lost after commit,
**When** the same action is resolved,
**Then** one record/result is recognized through the adopted scoped operation mechanism,
**And** server-managed creation/update actor/time evidence accompanies the record.
Do not expose an unprotected duplicate-prone create merely because this is a sample.
The example needs no separate autosave UI, full editor, discard lifecycle or audit console.

**Given** the sample requires its initial owned table/migration,
**When** controlled setup applies it and later starts the application,
**Then** only the sample's owned objects/history are changed, API startup runs no
migration, and runtime credentials cannot perform DDL,
**And** injected migration failure blocks dependent activation and reports the outcome
without automatically reversing committed changes. Reuse the release coordinator.

**Given** the sample feature is built through ATDD/TDD,
**When** the delivery is verified locally and in CI,
**Then** evidence shows the original failing acceptance, focused tests and passing
generated-output install/type-check/build/start/browser/API/database checks,
**And** tests use synthetic isolated resources and cleanup cannot target production or
prepared PtS/Scribeswell data. A supported real Auth test flow is used; separate real
Entra callback evidence remains required for Leave entry.

**Traceability:** Tracker Phase 1 generated authenticated-slice gate and continuous
scaffold evolution; E1-ENTRY-02/05/06/12; E1-AC-13/15/17/18; platform
ADR-0003/0012/0014–0020/0022/0023/0025/0031/0035/0046. Reference passing is platform
foundation evidence, not proof of Leave employment, autosave, policy or browser coverage.

**Impacts/sizing:** Keep one create/read resource and two declared capabilities. Update
templates, reusable clients, fixtures, exact commands, generator tests, changelog and
extension guidance together. Promote only proven shared UI; add generated agent links.
No universal CRUD engine, employee service, approval workflow, backup platform or new
release orchestrator. If mechanisms exceed one agent-sized item, deliver their bounded
reference/contract prerequisites first; do not cut safeguards from the exposed sample.

**Ordering/readiness:** P1 generator → required identity/Access and shared
operation/owned-persistence foundation items → E1-REF → generated Leave consumers.
Use final sequential numbering only after decomposing those foundations. Concrete
reference permission IDs, API schema, safe source fixtures and pinned commands must
be settled before implementation. No reference generated, service extended or test run.


Reference-app agreement, 2026-10-02: user accepted E1-REF's bounded authenticated
create/read journey and real Access/persistence evidence. Required shared capabilities
precede it in delivery; discussion order is not implementation numbering.

### Candidate Story E1-ID: Establish verified person and actor identities

**Planning draft for discussion — named prerequisite, not implementation-ready.**
Owner: shared identity/Access maintainers. Supplies the identity baseline consumed by
v2 authorization and later People; depends on inspected baseline/owned migration and
controlled setup design, not on a later Leave application story.

As a platform administrator,
I want existing accounts linked deliberately to stable person and actor identities,
So that shared services identify people consistently and preserve who performed actions
without treating every user as an employee or granting access through a link.

**Acceptance Criteria:**

**Given** the inspected supported identity schema and its existing migration/bootstrap
owners,
**When** the controlled adoption runs on a disposable representative database,
**Then** the identity owner has a separate verified migration history and explicit
object ownership inventory,
**And** Access's existing migration filter does not silently take over legacy objects,
Supabase-managed tables or another owner's schema. Clean setup and the supported
existing-schema adoption route are both documented and verified.

**Given** an authorized operator and verified account-to-person mapping,
**When** a person/link/actor is provisioned,
**Then** account, person and actor identifiers have their distinct declared meanings,
**And** at most one active person link exists per account, with immutable link-change
evidence and server-managed attribution. The record is reusable across applications;
no editable Leave person copy is created.

**Given** a person without a login, or an identified service actor,
**When** its shared identity is represented,
**Then** a person need not have an Auth account and a service need not have a fake person
or employment record,
**And** legacy system profiles are explicitly classified instead of automatically
converted into human employees. This creates no accountless administration UI.

**Given** two accounts share an email or are deliberately linked to one person,
**When** provisioning or identity resolution occurs,
**Then** email matching alone cannot merge/link people and grants never combine
implicitly between the accounts,
**And** client-supplied person/actor IDs or ordinary self-profile edits cannot establish
or alter a privileged identity link. Verified linking grants neither membership nor
application access nor employment.

**Given** the small existing PtS user cohort described by the user,
**When** a supervised transition is rehearsed,
**Then** existing Auth UUIDs can be retained with explicit manual mappings, or accounts
can be deliberately recreated with intended membership/grants re-established,
**And** no bulk-import framework, user-document migration or zero-downtime cutover is
required. Preserve read-only application content and applicable historical actor
references; an account change does not require rewriting immutable attribution.

**Given** incomplete mapping, deactivation or account replacement,
**When** a consuming identity check resolves the caller,
**Then** the agreed setup-needed/current-link behavior applies without fabricated
identity or stale grant fallback,
**And** durable actor references remain interpretable after account deactivation.
Legacy consumer contracts keep their supported meanings through the selected transition.

**Given** migration failure, conflicting link provisioning or missing required evidence,
**When** setup/adoption is attempted,
**Then** constraints and the controlled migration/audit transaction prevent partial
identity links from being presented as complete,
**And** failed migration blocks dependent activation with accurate outcome/recovery
reporting rather than automatic destructive rollback. An uncertain outcome is reconciled
before rerun; fixture reruns do not silently relink an existing account.

**Traceability:** Accepted platform ADR-0020/0025/0035/0040/0042/0045/0046;
[identity contract](../../platform/docs/architecture/contracts/identity-access-employment-e1.md);
E1-ENTRY-02/05–07/10/12; E1-AC-12/13/14/15/17/18. Include actual constraints,
restricted provisioning/runtime authorities, synthetic human/service/accountless
fixtures, conflicting/repeated mapping, v1 compatibility and recovery rehearsal.
Repository fixtures are not evidence that the production cohort has been changed.

**Scope/impacts:** Minimum person/link/actor adoption, not a profile editor, HR suite,
account-merging product or organization administration UI. Do not implement People
employment periods here. Reuse owner migration/audit helpers and promote proven
bootstrap fixtures/templates with this item; no new shared UI. Update owner runbook,
changelog, generated-context links and the requirement/test map. Accepted ADRs unchanged.

**Readiness:** Final schema/constraint/link-history representation, exact ownership
inventory, provisioning authority and selected transition commands must be settled
before implementation. Split baseline adoption from link provisioning into sequential
items if the verified inventory makes this too large for one agent; no reduction in
compatibility/security checks to preserve an arbitrary story size. No code, account
change, database connection or migration is performed by drafting this candidate.


Identity prerequisite agreement, 2026-10-02: user accepted E1-ID's minimum verified
person/account/actor adoption scope. Final schema/ownership and readiness checks remain
open; no actual account migration or runtime acceptance is implied.

### Candidate Story E1-ACCESS: Check current application access through the shared owner

**Planning draft for discussion — named prerequisite, not implementation-ready.**
Owner: existing `services/access`; depends on E1-ID and approved owned migration/
provisioning contracts. Delivers current authorization needed by E1-REF and Leave;
Directory integration and organization/app discovery receive a separate subsequent
item. A consumer can test this check with explicit synthetic organization context
before the launcher/discovery UI exists.

As an application owner,
I want each protected action checked against current application and user access,
So that my application cannot grant authority from login alone, stale roles or another
application's service credential.

**Acceptance Criteria:**

**Given** a registered protected app, declared capabilities, explicit organization
enablement and operator-provisioned user grants,
**When** a permitted service calls the selected v2 authorization contract for a user,
**Then** Access checks global app admission, organization enablement, current membership
and the exact capability together,
**And** returns verified account/person/actor/membership/organization references, exact
capability/scope and decision/time evidence under the owning wire contract.

**Given** the first consumers are the generated reference app and Leave,
**When** their synthetic fixtures are provisioned,
**Then** each has a distinct registered app namespace, narrow service credential and
explicit own-read/manage capabilities,
**And** the reference does not borrow PtS permissions, Leave does not inherit them, and
no future capability is granted by a wildcard. Select explicit reference capability
IDs and scope before readiness; read/manage are separately granted, not inferred.

**Given** the caller credential is invalid or scoped to another application,
**When** it requests a decision even with a valid user bearer,
**Then** service authorization rejects the call without protected identity details,
**And** a service key alone cannot impersonate a user or perform arbitrary capability
checks. Keys and bearer tokens are absent from logs, fixtures and generated output.

**Given** a membership/grant is revoked or the app is disabled globally/in the selected
organization while the user token remains valid,
**When** the next authorization check runs,
**Then** it denies under current state without cached positive-grant fallback,
**And** re-enabling restores only still-valid access; employment or verified account
linking alone cannot confer it. Bounded already-authorized execution follows ADR-0021.

**Given** expired authentication, absent identity mapping, confirmed lack of access
or unavailable verification,
**When** the check is evaluated,
**Then** safe typed outcomes distinguish those cases using the declared disclosure
order,
**And** no profile details or person-setup information are revealed before the caller
and relevant application/organization authority have been established.

**Given** existing PtS/Content callers use the supported v1 contract,
**When** the v2 capability/admission work is deployed through the selected transition,
**Then** supported v1 response meanings remain compatible and current protected-app
admission cannot be bypassed through v1,
**And** transition/provisioning explicitly establishes intended PtS admission instead of
assuming every existing account or organization is enabled for every app.

**Given** concurrent provisioning, pooled connection reuse or a failed migration,
**When** the relevant path is exercised,
**Then** owner constraints/scoped runtime authority prevent cross-organization grants
or context leakage, required grant/enablement transition evidence commits atomically,
and migration failure blocks activation under the existing release contract,
**And** E1 operator configuration is not exposed as an unauthenticated setup endpoint.

**Traceability:** E1-ENTRY-02/05/06/07/10/12; E1-AC-13/15/17/18; accepted
platform ADR-0011/0019/0020/0021/0023/0025/0031/0035/0042/0046;
[identity wire contract](../../platform/docs/architecture/contracts/identity-access-employment-e1.md)
and [admission contract](../../platform/docs/architecture/contracts/application-admission-and-discovery.md).
Observe failing direct contract/integration checks before implementation; verify current
state under actual restricted roles plus provider authentication evidence. Mocked
success alone does not prove authorization, revocation or credential isolation.

**Scope/impacts:** Extend the existing Access owner, service-owned dependencies, exact
catalog and typed caller adapter; update migrations, isolated fixtures, generated-client
examples and compatibility tests together. No custom-role administration UI, billing
engine, People server or complete Directory integration here. Shared UI consumes safe
errors later; generated context/docs link current contracts. Accepted ADRs unchanged.
If registry/provisioning and check implementation need separate agent-sized items,
split them in that order while keeping first exposed checks complete and safe.

**Readiness:** Final registry/grant schema, permission-to-app mapping, reference
capability IDs, caller-key provisioning, v1 admission transition, exact dependency
resolution and test commands remain to validate. This candidate does not authorize
code, secrets, grants or deployment changes.


Access prerequisite agreement, 2026-10-02: user accepted E1-ACCESS and clarified
consumer service credentials versus end-user permissions. Both checks remain mandatory.

### Candidate Story E1-DISCOVERY: Discover only currently accessible organizations and apps

**Planning draft for discussion — named prerequisite, not implementation-ready.**
Owner: Access, with narrow identity-owner discovery integration. Depends on E1-ID and
E1-ACCESS. Supplies real data for the reference/Leave selectors and Directory; frontend
launcher adoption follows in its own bounded item. No duplicate entitlement store.

As a user with access to selected applications and organizations,
I want discovery to reflect my current permissions,
So that selectors do not offer workplaces or protected apps I cannot enter.

**Acceptance Criteria:**

**Given** a verified user and a permitted application service,
**When** current organizations are requested for that registered application,
**Then** return only organizations with current membership, app enablement and an
applicable capability, with the declared minimal identity/name fields and pagination,
**And** no employee record is required merely to list an otherwise accessible workspace.
Support the reference and Leave app IDs explicitly through the reviewed registry;
reject arbitrary/disallowed application selectors rather than accepting a wildcard.

**Given** more organizations exist than fit one page,
**When** subsequent pages are requested,
**Then** the cursor conveys only position and each page rechecks current authority,
**And** duplicate/invalid cursors and concurrent access changes follow the declared
contract without cross-user disclosure or a promise of a frozen entitlement snapshot.

**Given** App Directory's own restricted service identity and verified end-user bearer,
**When** it requests current protected applications through `/v2/applications`,
**Then** Access returns only registered admitted app IDs/scope kinds meeting current
access in at least one applicable scope, plus observation time,
**And** it does not disclose organization names, employee data, role lists, credentials
or arbitrary other users' grants. Display URLs/icons remain Directory-owned.

**Given** valid identity but no matching current organizations/protected apps,
**When** discovery completes successfully,
**Then** return the declared empty result,
**And** expired authentication, forbidden consumer credentials and unavailable current
verification remain distinct typed errors, never misleading empty successes.

**Given** access to organization A but not B, or a membership/app/grant revocation
between requests,
**When** discovery is repeated or an old cursor is reused,
**Then** current results exclude unauthorized contexts,
**And** no positive cross-request permission cache preserves removed authority. A
previous result never substitutes for the subsequent action's own Access check.

**Given** the current identity bridge assumes an already-selected organization,
**When** the new pre-selection discovery query runs,
**Then** a narrow identity-owned projection/routine supplies only the verified caller's
permitted membership/organization fields to Access,
**And** runtime credentials gain no universal identity-table read, superuser bypass or
ability to set authority from unsigned client actor headers. Validate transaction-local
context and pool reuse under actual restricted roles. Exact SQL grants remain readiness
work; the example of a projection/routine does not prescribe unchecked SECURITY DEFINER.

**Given** delayed dependencies or malformed/unknown upstream data,
**When** discovery cannot finish within its declared budget,
**Then** it returns the safe unavailable contract with no stale grant fallback,
**And** absence of person/employment mapping alone is not misreported as application
access loss. Public Scribeswell requires no synthetic grant or discovery membership.

**Traceability:** E1-ENTRY-03/05/06/07/12; E1-AC-01/13/15/17/18; accepted
ADR-0019/0021/0031/0042/0046; shared identity/admission contracts. Verify real
current-state queries for two organizations, a synthetic pagination-size fixture,
for-profit naming, unauthorized app namespace, service caller isolation, mapping gaps,
revocation and unavailable providers. No production data enumeration is part of this
planning item.

**Scope/impacts:** Two minimal discovery endpoints share the prior Access evaluator.
No grant editor, invitation flow, organization portal, employment listing or billing
API. Update service schemas, restricted grants/migrations, typed client examples,
generation fixtures, docs and exact commands together. Shared UI consumes this in the
next selector/launcher items; no new UI here. Existing agent/ADR guidance applies.
Final query authority, registry limits, pagination fixtures, dependency pins and runtime
evidence remain open before readiness; no implementation or grants changed.


Discovery agreement, 2026-10-02: user accepted E1-DISCOVERY's current organization/app
responses, scoped authority and distinct empty/unavailable results.

### Candidate Story E1-LAUNCHER: Show accessible apps with honest discovery states

**Planning draft for discussion — named prerequisite, not implementation-ready.**
Owners: App Directory, typed directory client and shared AppLauncher; consumers PtS,
Scribeswell and generated shells. Depends on E1-DISCOVERY and its current admission
evaluator, not on Leave business screens or future access-administration UI.

As a user moving between applications,
I want the launcher to show apps I can use and explain when access could not be checked,
So that I can navigate without confusing public availability, missing permission and
a temporary service problem.

**Acceptance Criteria:**

**Given** I am not signed in,
**When** the launcher loads the published catalogue,
**Then** Scribeswell is omitted from the shared launcher, as are protected apps,
**And** anonymous reading remains available separately at scribeswell.com without
a forced login or organization membership.

**Given** I am signed in and current discovery succeeds,
**When** Directory composes its v2 response,
**Then** it shows published protected app IDs admitted by Access and includes the
Scribeswell entry only if current PtS admission is present,
**And** the launcher uses catalogue-owned names/icons/canonical URLs without treating
JWT roles, a catalogue enabled flag or a cached result as a permission grant.

**Given** I have PtS access but no qualifying Leave organization,
**When** the launcher renders,
**Then** Leave is absent,
**And** adding Leave admission/membership/capability in a qualifying organization makes
it discoverable on the next current check. A selected organization in the originating
app does not hide account/public apps or grant cross-app access.

**Given** current protected discovery is unavailable,
**When** the response is handled,
**Then** no app links are inferred from stale results or public reachability, and a
clear could-not-check state and Retry remain visible even with no links,
**And** this failure is not presented as a complete no-access list. A total
Directory failure also shows an actionable failure state without blocking the already
open public reader; do not invent a stale protected fallback list.

**Given** an expired/invalid supplied token, sign-out, account change or an older
in-flight response from a previous account,
**When** discovery/session state changes,
**Then** typed authentication handling and previous-user cache clearing apply,
**And** a late response cannot restore the previous account's app list. Public content
remains available through its anonymous path; invalid authentication is not relabelled
as a verified user with no grants.

**Given** valid discovery with no protected apps, loading, partial/unavailable results
or no entries,
**When** the launcher renders and receives keyboard/touch input,
**Then** each state remains distinguishable and accessible, including Retry where
applicable,
**And** empty results cannot hide an error, trap focus or break arrow/Home/End/Escape
navigation. Preserve existing accessible icon-only and labelled variants. Existing
AppLauncher currently returns null for an empty nonloading list; update that behavior
where necessary so it cannot suppress the new failure state.

**Given** I follow an app link,
**When** its target opens using the existing new-tab launcher behavior,
**Then** it uses the configured approved application URL with no bearer tokens or
sensitive form values appended,
**And** the destination rechecks authority and resolves its own organization context.
Hostname configuration follows the accepted arrangement; DNS/hosting migration is
separate deployment work, not an unannounced effect of this component change.

**Given** existing PtS/Scribeswell consumers and the v1 Directory response shape,
**When** the updated client/service/component is adopted,
**Then** both consumers and generated-shell templates use verified compatible contracts,
**And** any still-supported v1 path filters protected apps through the same authority
and reports unavailability honestly. The full catalogue's existing admin-labelled
endpoint is restricted by explicit authority or removed from public deployment; it
cannot act as an unguarded production administration interface.

**Traceability:** E1-ENTRY-02/03/05/06/11/12; E1-AC-01/12/13/15/16/17/18;
ADR-0031/0032/0046/0047; application admission/discovery contract and existing AppLauncher
behavior. Cover anonymous public reader with no launcher entry, non-PtS user without a
Scribeswell entry, PtS-only user with that entry, multiple organization grants,
revocation, outage/partial results, account-race response rejection and keyboard/mobile
interaction. Characterize existing launcher behavior before changing shared controls;
verify real Directory/Access integration as well as focused state/component fixtures.

**Impacts/sizing:** Evolve the existing Directory/client/launcher rather than creating
a new portal. Keep metadata owned by Directory, decisions by Access, and app domain
flows in their owners. Update schemas, adapters, consumer calls, shared UI docs/tests,
templates, generated sample checks and changelog together. Agent-context links remain
sufficient; no new ADR. If the cross-consumer change needs subdivision, land compatible
service/client support before UI adoption without exposing all-enabled protected apps.
No billing, public signup, organization-admin screen or full SSO redesign. Exact
commands/schema/error compatibility and readiness gates remain open; no code changed.


Launcher scope correction/agreement, 2026-10-02: user approved the remaining launcher
scope but requested Scribeswell be listed only for current PtS users. Public reading
at scribeswell.com stays independent. Accepted ADR-0047 narrowly supersedes ADR-0046's
automatic public menu/fallback behavior; owning contract, candidate and agent guidance
updated. No public-account signup, grant change or deployment performed.


### Candidate Story E1-PEOPLE: Resolve my shared employment for the selected organization

**Planning draft for discussion — named prerequisite, not implementation-ready.**
Owner: shared People service. Depends on verified identity and current Access contracts,
owned migration/provisioning and the bounded service scaffold variant. Deliver before
Leave's employee draft-context/start consumer; it is not needed merely for app entry.

As an authorized employee using Leave,
I want my employment relationship resolved from the shared source for my organization,
So that Leave can apply its draft rules without maintaining a duplicate employee record.

**Acceptance Criteria:**

**Given** a verified caller and permitted consuming service in an authorized organization,
**When** the service requests my own employment,
**Then** People derives my person identity from verified context and returns the
minimal declared discovery/effective read representation,
**And** no arbitrary client-supplied employee ID, email match or cross-owner table read
can substitute for authorization. Return no unnecessary profile/assignment details.

**Given** employment records are provisioned through the controlled owner setup,
**When** the same person joins or rejoins an organization,
**Then** one enduring employment relationship exists for that person/organization with
separate stable employment periods,
**And** database constraints prevent duplicate relationships, reversed dates and
overlapping inclusive periods. Accountless people are valid; no Auth account or
application grant is created to satisfy the employment model.

**Given** a valid caller-supplied business date,
**When** People interprets the employment periods,
**Then** it returns current, otherwise next-future, otherwise ended employment as
defined in the contract, with exact period identity/dates, relationship revision,
observation time and the date used,
**And** a relationship without periods is setup-needed, not proof of termination.
A gap before a known rehire is future employment; it grants no leave in that gap.

**Given** no business date is supplied,
**When** discovery is requested,
**Then** return stable relationship references without inventing today's UTC effective
status,
**And** Leave remains responsible for deriving its date from the employee's Leave work
timezone. People owns shared employment facts, not Leave work profiles or editability.

**Given** no relationship, missing verified identity setup, denied authority or an
unavailable dependency,
**When** the read resolves,
**Then** those outcomes remain distinct under the declared safe envelope/disclosure order,
**And** an outage is never returned as no employee or stale positive authority.
Inconsistent stored periods fail safely rather than selecting an arbitrary row.

**Given** shared optional department, location or supervisor is unassigned,
**When** the minimal E1 read occurs,
**Then** it remains valid and does not block a Leave draft on that basis,
**And** these facts retain shared People ownership but need no E1 directory lookup,
organization-chart import or maintenance screen. Their E2 scoped/history/retirement
contracts remain binding; shared location does not replace Leave work profiles.

**Given** a relationship changes between discovery and effective read,
**When** a client consumes the observations,
**Then** the response supplies consistent identity/date/revision evidence that allows
the client to reject identity mismatch and apply its agreed freshness rules,
**And** People does not claim that a read locks employment through a later Leave commit.
Leave's draft-only ten-second rule remains with the consumer, not a universal policy
for all applications or submission/approval.

**Given** missing/wrong transaction scope, concurrent fixture writes or pooled connection
reuse,
**When** real restricted-role reads/constraints are exercised,
**Then** no other organization's employment is exposed and structural/history/attribution
invariants hold,
**And** owner-controlled migration failure blocks activation without API-startup
migrations or runtime schema authority. No cross-owner database FK is introduced.

**Traceability:** Features §1/2/7; platform ADR-0040/0041/0042/0044; Leave ADR-0023/0094;
E1-ENTRY-07/08/12; E1-DRAFT-04/17; E1-AC-13/14/15/17/18;
[shared employment contract](../../platform/docs/architecture/contracts/identity-access-employment-e1.md).
Fixtures include two organizations, current/future/ended/rehire/no-period/no-relationship,
accountless people, null assignments, exact bigint serialization and caller isolation.
No production employee import or UI operation is implied by synthetic provisioning.

**Scope/impacts:** One owner, minimum relationship/period model and own-employment read.
No HR suite, employee admin screen, Microsoft topology sync, on-behalf access or Leave
policy calculation. Generate the new service from the bounded service variant; reuse
proven restricted context, safe errors and immutable attribution patterns. Promote
optional typed employment clients/fixtures in the same item without forcing employment
on every generated app. Shared UI uses existing setup/error states; docs/context record
ownership and null semantics; accepted ADRs unchanged.

**Readiness:** Final People schema/period constraints, current caller permission mapping,
service-only generator item, baseline/provisioning commands and dependency pins remain
to settle. Split model/provisioning from HTTP read in dependency order if necessary
for one-agent delivery; do not expose an unprotected read first. No service, migration,
fixture or application code implemented by this candidate.


People prerequisite agreement, 2026-10-02: user accepted E1-PEOPLE's minimum shared
relationship/period/read scope, without employee administration or organization-chart
features. Required schema/caller/fixture and implementation-readiness checks remain.

### Candidate Story E1-SERVICE: Generate an independently owned internal service

**Planning draft for discussion — named prerequisite, not implementation-ready.**
Owner: platform builder. Depends on E1-P1's shared rendering/validation backend
foundation; deliver before generating the new People service. Existing Access is
extended in place, not regenerated over its current implementation.

As a shared-service developer,
I want to generate a backend-only service with its own configuration, dependencies
and migration boundary,
So that reusable capabilities can be consumed over HTTP without depending on an
application's server code or frontend scaffold.

**Acceptance Criteria:**

**Given** a valid service identifier and explicitly selected supported configuration,
**When** I run the service-only generation path into a disposable target,
**Then** it creates an owned FastAPI package, API/test/start commands, safe configuration
examples, health behavior and the selected owned persistence layout,
**And** it creates no React frontend, application launcher entry, employee model,
organization grants or Leave-specific domain objects.

**Given** the generated service's declared dependencies and locked toolchain,
**When** install, focused tests, startup/health and package/container verification run,
**Then** the disposable generated service runs independently of any app's requirements
file or server imports,
**And** configuration uses explicit service URLs and restricted credentials, never
a universal platform key, browser-exposed secrets or production fallback values.

**Given** a stateful service uses its generated persistence/migration extension points,
**When** controlled setup and runtime startup are exercised,
**Then** its schema/history, runtime and migration roles remain distinct from other
owners,
**And** runtime startup performs no schema migration, runtime cannot perform DDL,
and only the explicitly declared owner migration participates in coordinated setup.
Do not create business tables before a consuming story requires them.

**Given** an internal service consumer is configured,
**When** the generated HTTP/auth/error boundaries are extended by its domain story,
**Then** they provide the proven hooks for caller authentication, verified user/scope
propagation, bounded HTTP waits and safe typed error/log handling,
**And** no permissive placeholder protected endpoint is exposed while integration is
incomplete. Caller authorization policies remain explicit, not inferred from being
on a private network. Health exposes no configuration secrets.

**Given** existing runtime-manifest/release tooling is the selected deployment adapter,
**When** the generated service configuration is validated,
**Then** it identifies its image/build inputs, required environment, health endpoint
and declared dependencies/owner migration without a second deployment runner,
**And** validation is isolated and does not register, start or publish a production
service. Existing deployment implementation is reuse evidence, not automatic acceptance
of proposed deployment ADR-0043 or every deployment option.

**Given** an invalid name, path escape, conflicting target or failed generation,
**When** the generator attempts output publication,
**Then** E1-P1's no-overwrite/reproducible-output guarantees apply,
**And** a People service generation cannot replace Access code or change another
owner's migration files. Generated versus hand-maintained extension points are explicit.

**Given** this variant is delivered through failing-first acceptance,
**When** generation is verified locally and in CI,
**Then** the disposable service's actual output passes its declared checks,
**And** the application-generation regression still passes so sharing backend templates
does not silently break application output. Record exact commands and relevant results.

**Traceability:** Tracker Phase 1 service/application variants, independent histories,
environment validation and generated-output checks; E1-ENTRY-06/12; E1-AC-15/17/18;
platform ADR-0003/0014–0020/0022/0023/0031. The subsequent People story proves actual
employment authorization/constraints; this variant's startup test does not claim them.

**Scope/impacts:** Reuse the generator core rather than introducing another CLI. Update
service templates, fixtures, reference configuration, documentation/changelog and
generated agent links together. No new shared UI, service mesh, public API gateway,
worker farm, generic HR backend or remote deployment. Existing ADRs unchanged.
Minimum supported configuration and exact toolchain/commands remain readiness inputs;
no generator, service, fixture or deployment code implemented by this candidate.

Service scaffold discussion, 2026-10-02: user accepted the remaining E1-SERVICE
scope and asked about table-driven API generation and later custom behavior, including
non-API services. Apply existing platform ADR-0001/0014: generate persistence plumbing
and explicitly selected API contracts/operations; do not infer public CRUD or permissions
from tables. Custom domain commands remain owner-maintained and protected from
regeneration. See the builder README's generation-input/extension guidance; no accepted
ADR changes or implementation authorization are implied.

**Additional E1-SERVICE acceptance criterion:**

**Given** a disposable generated service has a hand-maintained custom behavior module,
**When** supported regeneration is exercised,
**Then** that module is preserved and its behavior check still passes,
**And** generation never publishes table-derived fields or protected operations without
explicit contract and authorization configuration. Unsupported regeneration/conflicts
fail safely without overwriting custom code. Prove only the minimum supported path;
this does not add a generic database-to-API engine to E1.

Non-API worker/job scaffolding follows the same generated/custom ownership separation,
but is driven by declared work/event contracts, with optional persistence. Deliver its
proven variant with the first consuming epic under worker/event ADRs, rather than adding
unused worker machinery to E1. Scaffold/docs impact: update owning guidance and future
fixtures; no shared UI or additional agent rule needed; existing ADRs remain authoritative.


Service generation agreement, 2026-10-04: user approved the clarified table-assisted
persistence, explicitly selected API contracts, protected custom extensions and
first-consumer approach to non-API scaffolding. E1-SERVICE remains subject to readiness.

### Candidate Story E1-ENV: Reproduce an isolated development and acceptance environment

**Planning draft for discussion — not implementation-ready.**
Owner: platform development/test tooling, with owner-controlled setup from each service.
This is the bounded executable foundation for the already approved
[E1 environment contract](../../apps/leave/docs/testing/e1-environment-and-dependencies.md).
Deliver its base environment before the generated reference acceptance; each later
consumer adds its own migrations, fixtures and tests in its delivery item. The base
story does not depend on an unimplemented People service or Leave application.

As a developer or acceptance tester,
I want a reproducible isolated environment with synthetic accounts and explicit commands,
So that I can verify generated services and later the Leave journey without affecting
existing application data.

**Acceptance Criteria:**

**Given** the documented prerequisites and selected pinned toolchain,
**When** I bootstrap a fresh local or CI instance with the declared owner commands,
**Then** the supported Auth/PostgreSQL foundation starts with explicit target identity,
separate setup/runtime credentials and repeatable verification commands,
**And** required versions and resolved dependencies are recorded; a bootstrap smoke
check demonstrates the actual foundation without claiming the Leave journey is complete.

**Given** another application's prepared local environment or an unapproved target,
**When** bootstrap, fixture reset or cleanup is requested,
**Then** writes are refused outside this disposable instance's allowlisted target,
**And** project/container/volume names and ports prevent accidental reuse, credentials
have no production fallback, and cleanup is limited to this instance or CI run.

**Given** a consuming owner joins the environment through its declared configuration,
**When** its controlled migration and fixture setup run,
**Then** only that owner's declared setup executes, failure blocks dependent startup,
**And** runtime credentials cannot migrate schemas or acquire setup privileges.
The base story verifies this boundary using an available disposable fixture; later
owners supply their own schemas and fixtures without importing server implementations.

**Given** synthetic accounts and organization fixtures are provisioned,
**When** the foundation's authentication and isolation smoke checks run,
**Then** local Auth and real PostgreSQL are exercised with two organizations, including
a for-profit organization, and current restricted-role boundaries,
**And** fixture credentials stay out of committed files and diagnostic output. Synthetic
local authentication is explicitly distinguished from the required actual Entra check.

**Given** the generated reference and later Leave consumers are integrated,
**When** their owning stories add acceptance coverage,
**Then** they reuse this isolated foundation and provide their own real HTTP/persistence
checks and explicit test commands, including TypeScript Playwright where browser
behavior is involved,
**And** browser/device qualification and the Entra callback check retain separate
traceable evidence; the environment smoke test cannot mark either gate complete.
This criterion constrains later integration; those consumer tests are not required to
complete the base environment story.

**Traceability:** Tracker Phase 1 environment/generated-reference gates; E1-AC-15/18;
E1 environment contract topology, dependency ownership and real-sign-in sections;
platform ADR-0003/0014–0020/0023/0035/0039. Existing performance/browser policies apply
when their consumers are tested, not as an unmeasured foundation capacity claim.

**Scope/impacts:** Promote proven environment configuration, fixture boundaries and
commands into owning scaffold/test guidance in the same delivery item. No new shared
UI; link existing agent safety/ATDD guidance. Existing ADRs unchanged. No general
purpose environment manager, hosted staging, production changes or unused workers.
Exact pins, commands and target validation design remain readiness inputs. No tools
installed, environments started, migrations applied or application code implemented.


Environment story agreement, 2026-10-04: user accepted E1-ENV's isolated, repeatable
local/CI foundation and incremental owner integration. Pins, concrete commands and
remaining readiness evidence are still open.

### Candidate Story E1-CONTEXT: Explain whether I can start or edit a Leave draft

**Planning draft for discussion — not implementation-ready.**
Owner: Leave. Depends on generated Leave/API foundations, E1-ID/ACCESS/PEOPLE and
protected entry. Deliver before D1/D2. Draft existence/generation fields from the
complete context endpoint are added by D1 with its owned persistence; this earlier
item proves eligibility resolution without inventing draft tables or placeholder
claims about whether a draft exists.

As an employee entering Leave,
I want the application to explain whether I can prepare a draft or need setup help,
So that I can distinguish missing configuration from lost access or a temporary fault.

**Acceptance Criteria:**

**Given** current Leave access and a verified shared employment relationship,
**When** Leave resolves draft context,
**Then** authorized scope/ownership and confirmed editability restrictions determine
whether preservation is allowed,
**And** missing or invalid work timezone alone cannot deny create/edit/save/reopen.
Return a nonblocking setup notice without claiming calculation/submission readiness.

**Given** a valid work timezone is available and dated employment interpretation is used,
**When** Leave requests that interpretation,
**Then** the date derives from the server clock in that work timezone, never browser
location or implicit UTC,
**And** confirmed ended employment follows its existing read-only rule. With timezone
missing, use authorized discovery without fabricating current/ended eligibility.

**Given** missing identity/employment scope, confirmed no employment periods, insufficient
capability or a required authority/ownership-service failure,
**When** context is resolved,
**Then** existing setup/read-only/denied/unavailable outcomes remain distinct,
**And** the timezone simplification does not fail open for lost authority or invent an
employee. Null department/location/supervisor alone does not block preparation.

**Given** configuration changes while input is preserved,
**When** a draft save executes,
**Then** current authorization and local revision/lifecycle checks remain required,
**And** full calculation-setting validation is not a new save prerequisite. Only a dated
interpretation actually used requires its corresponding freshness evidence. D1/D2 prove
these branches against actual writes; no UI context result is a reusable authorization.

**Given** synthetic setup and draft fixtures,
**When** context behavior is exercised,
**Then** missing/invalid timezone permits otherwise authorized preservation, while
confirmed restrictions and cross-organization denial still hold,
**And** no balances, eligibility or submission success are fabricated. Existing profile/
default/override precedence remains with timezone-dependent consumers; no duplicate
permanent employee or timezone master is created for this simpler path.

**Traceability:** Features §1–3/7; E1-ENTRY-05–08/11/12; E1-DRAFT-04/17;
E1-AC-13/14/15/17/18; Leave ADR-0023; shared identity/access/employment contract
and Leave draft-context/editability contract. Existing source contracts remain authoritative.

**Scope/impacts:** Minimum Leave draft context with nonblocking business-setup notices
and existing authorized read-only/error presentation under P-0049/L-0122. Full work-profile/holiday administration remains E2;
leave-type choice metadata is a separate D2 prerequisite, and policy/calculation work
remains E3. Promote only proven generic service/error integration into scaffolding;
work-timezone/employment eligibility stays Leave-owned. No new shared UI library or
agent rule; update source-linked docs and test mapping. Existing ADRs unchanged.
No application code or readiness approval is implied.


Draft-context agreement, 2026-10-04: user accepted E1-CONTEXT's minimum Leave-owned
settings/eligibility boundary. Concrete schema, contracts and readiness remain open.

### Candidate Story E1-CHOICES: Choose a leave type and its permitted duration mode

**Planning draft for discussion — not implementation-ready.**
Owner: Leave. Depends on generated/protected Leave foundations and controlled local
fixtures; deliver before D2. D2 adds persistence/reopening of these choices. E3's policy
editor and calculation engine must not become hidden prerequisites for this item.

As an employee preparing a leave application,
I want to choose an organization-configured leave type and an allowed duration mode,
So that I can enter the right details in my unfinished draft.

**Acceptance Criteria:**

**Given** current authority to view my organization's draft choices,
**When** Leave loads the minimum choice metadata through its own API,
**Then** it returns only authorized organization-scoped type identities, display metadata
and permitted duration modes through an explicit API contract,
**And** the frontend does not query tables directly or treat catalog presence as
submission eligibility. Current access is checked on the API, independently of the UI.

**Given** configured choices are available,
**When** I open the form or choose a type,
**Then** no type is selected automatically; first choosing a type in a new request
initializes Full days when permitted, otherwise leaves the mode unselected,
**And** the form offers that type's permitted Full day(s), Half day and Hours modes
without arbitrary day fractions and preserves usable saved selections, including null,
on reopen; obsolete selections follow ADR-0122 field clearing,
**And** keyboard, focus, labels and mobile controls follow the approved Leave UX.

**Given** I have entered values and change the leave type,
**When** the newly selected type disallows my selected duration mode,
**Then** that obsolete selection is cleared with a brief Choose again notice, requiring
an explicit permitted choice and normal guarded autosave,
**And** entered mode-specific values remain recoverable without silently selecting a
replacement or erasing them. D2 proves these behaviors through actual save/reopen.

**Given** configuration is missing, its read fails, or a previously saved selection is
no longer offered,
**When** the form resolves choices,
**Then** empty configuration differs from unavailable data, with setup guidance or Retry
as appropriate, and no fabricated default type or balance is shown,
**And** D2's draft-preservation contract still allows incomplete input to be saved when
current authority and editability permit. Saved input is not silently replaced by the
first available option. Exact unavailable/archived-reference display and allowed input
handling must be specified before dependent readiness, without disclosing another
organization's type details.

**Given** controlled synthetic configuration,
**When** this item is verified,
**Then** tests exercise different permitted-mode sets, empty/unavailable results and
cross-organization references,
**And** provisioning uses the owning versioned type/configuration design rather than
hardcoded frontend options or a parallel disposable-only product model. Use the feature
specification's Annual, Sick and Family Responsibility examples as fixture examples,
not assumed statutory entitlement or globally prescribed organization policy.

**Traceability:** Features §4/7; Leave EXPERIENCE request form; draft contract input
version 1 and mode preservation; D2 prerequisite and E1 draft-input/authorization
acceptance scenarios. Exact choice endpoint, response/version fields, scope filtering,
active-date/version selection and minimal owned schema remain pre-story contract inputs.
Do not infer policy eligibility from the employee's current date alone.

**Scope/impacts:** Minimum configured read/choice UI and controlled provisioning only.
Full type/policy administration, entitlement, policy guidance, document requirements,
balances and authoritative calculation remain in their already assigned epics. Leave
owns choice semantics; promote only proven generic accessible selection/error primitives
and generated contract fixtures when applicable. Update source-linked documentation;
existing agent guidance and ADRs suffice. No code or readiness approval is implied.


Choice/default agreement, 2026-10-04: user approved E1-CHOICES with all three modes
initially enabled for new leave-type configuration and Full days initially selected
for a new request where permitted. Managers may restrict allowed modes. Arbitrary
fractions remain excluded; Half day and Hours serve partial-day entry. Defaults do
not backfill existing configuration or overwrite restored/explicit selections. This
refines product/UX defaults without changing accepted duration ADR-0074. Features,
UX and draft contract updated; configuration-editor evidence remains with E3.

### Next contract discussion: minimal context across interactive sign-in

E1-D5's remaining carrier decision is proposed as per-tab sessionStorage containing
only a versioned, short-lived return/recovery reference: prior account/person binding,
validated route key, organization/draft identifiers and any uncertain operation ID.
Keep form values and tokens out of this application recovery record and return URLs.
Treat all stored values as untrusted hints, never authorization. Use the supported
Auth flow's own callback/state mechanism; do not replace its security state.

After sign-in, verify the account and current resource authority, obtain current saved
data and resolve a retained uncertain operation before allowing another mutation.
Without the original payload, do not replay/reconstruct its write. An unresolved
outcome remains unresolved; a reload is not proof that a late write cannot commit.
Clear the recovery record after resolved consumption, expiry, explicit sign-out or
account mismatch. Stale/repeated callbacks cannot consume newer navigation context.
Browser-storage failure or a closed tab means honest recovery from server-saved data
through ordinary navigation, not a promise of local edit survival.

This is a proposal for the existing D5/shared-session implementation, not a new story
or accepted platform ADR. Exact schema, TTL, callback/tab binding, cleanup and unresolved
outcome handling must be settled and tested before readiness. Unsaved text stays in
memory where possible and is not guaranteed across full-page sign-in. Scaffold impact:
prove and promote generic return/reference handling with generated-app fixtures;
Leave owns draft destinations and lifecycle. Existing ADR-0032 remains authoritative.


Sign-in carrier agreement, 2026-10-04: user approved per-tab sessionStorage for minimal
navigation/recovery references, excluding form values/tokens, with current identity/access
checks and truthful saved-only recovery. Recorded in the owning draft contract. E1-D5's
carrier approach is settled; exact schema/TTL/callback/lost-reference checks remain open.

### Next contract discussion: leaving a form with an uncertain save outcome

Proposed refinement for the existing D2/D3 stories: distinguish a confirmed save failure
from an unknown outcome after bounded automatic recovery. For the latter show:
“We could not confirm whether your latest changes were saved.” Offer Retry, Keep editing
(or Stay during organization switching), and an explicit leave-without-waiting action.
Its explanation states: “Changes already sent may still be saved. Changes not sent
will be lost.” Final localized wording and accessible dialog layout remain UX work.

Leaving abandons local unsent input and further client retries; it neither cancels nor
reverses a possible server commit. Preserve the original scoped operation reference
through the agreed metadata-only carrier while recovery is unresolved. Do not issue a
new save merely because the user navigated away, and do not let a late response close
or overwrite a different organization's form or newer navigation. Switching still
requires current target access and confirmed target-selection handling. If the user
stays, retain local edits but block a fresh save until the uncertain operation is
resolved. Reopening reads current authorized state and resolves outstanding recovery;
it does not claim that the pre-failure snapshot is necessarily the latest saved state.

This proposal clarifies presentation under the existing no-rollback/no-resurrection
contracts; it does not change the deliberate Discard draft command. Known failed-save
handling retains Retry/Keep editing/Close anyway. Include commit-with-lost-
response, unsent newer input, late response after navigation and cross-organization
fixtures in D2/D3. Readiness must settle expired/missing recovery-reference handling
and prove it cannot bypass safe ordering. No runtime implementation is authorized.


Draft failure UX agreement, 2026-10-04: the user rejected the preceding technical
leave-without-waiting presentation and approved the simpler platform-wide approach.
Platform ADR-0048 and Leave ADR-0121 are authoritative: use the simple warning and
Try again / Keep editing / Close anyway (Stay / Switch anyway). No extra technical
confirmation. The preceding proposal is superseded as presentation only; internal
recovery/isolation protections remain. Apply to E1-D2/D3 and shared scaffold promotion.


### Candidate Story E1-WRITE: Prove safe owned writes for generated backends

**Planning draft for discussion — not implementation-ready.**
Owner: platform scaffold, proven in a disposable owned backend fixture. Depends on
E1-P1, the isolated E1-ENV foundation and verified identity/Access contracts and setup.
Deliver before E1-REF's full browser journey. E1-REF integrates this proven backend
pattern; this story must pass its own real API/database checks without that later UI.
No new shared runtime write service or generic workflow engine is introduced.

As a developer delivering a generated backend,
I want its first protected write to preserve scope, attribution and safe retry behavior,
So that applications can use the foundation without independently reinventing these
platform requirements.

**Acceptance Criteria:**

**Given** a disposable generated backend with one non-sensitive example resource,
**When** a currently authorized caller creates and reads it through the API,
**Then** current Access HTTP authorization and owned restricted-role persistence are
exercised, and the API exposes only explicitly selected fields,
**And** the record and required compact operation outcome commit together, with
server-derived actor IDs and UTC creation/update attribution. Client-supplied audit
fields cannot override verified attribution. This fixture is not a Leave draft model.

**Given** the same scoped create action is retried, concurrently or after a lost response,
**When** the backend resolves its stable operation ID,
**Then** one resource and one successful outcome exist, without repeating effects,
**And** changed input under that ID is rejected. Outcome reads check current authority;
a missing outcome is unresolved, not proof of rollback. No payload snapshot is retained
in the compact receipt. Canonical input and retention/rejection rules must be declared
for this reference command before readiness, not copied from Leave without inspection.

**Given** another organization's ID, missing scope or a reused pooled connection,
**When** requests and database checks run under actual restricted runtime identities,
**Then** unauthorized data cannot be read or written and transaction completion/rollback
cannot leak scope to another request,
**And** runtime credentials cannot perform schema changes. Owned setup/migration authority
is exercised separately through the established environment and coordination contract.

**Given** an error before commit, an unavailable Access dependency or a lost response
after commit,
**When** the corresponding failure is injected,
**Then** pre-commit failure leaves neither business effect nor successful receipt,
post-commit recovery finds the durable result, and typed errors preserve the distinction,
**And** logs/errors contain no credentials or raw payload dumps. External service waits
occur outside business write locks; helpers never commit independently of the owner.

**Given** these behaviors have passing API/database/concurrency evidence following
observed acceptance failure,
**When** the proven template is regenerated into another disposable target,
**Then** the same declared contract checks pass against the generated output,
**And** custom extension modules remain intact. Record exact commands/results and update
owning templates, fixtures, version/changelog and documentation together.

**Traceability:** E1-REF prerequisite; tracker Phase 1 generated authenticated slice;
E1-AC-15/17/18; platform ADR-0003/0007/0012/0014–0020/0022/0023/0025/0031/0035.
Reference scope is one create/read resource. Mutable-resource revision checks and
Leave lifecycle/generation guards remain with their first relevant writer, including
D1/D2; this story must not advertise arbitrary safe CRUD it has not proved.

**Scope/impacts:** Build-time templates copied into each owner, not a central operation
service or cross-owner table access. No new frontend or shared UI; reference browser
acceptance stays E1-REF. Generated context links existing platform safeguards; no new
agent policy or ADR. Minimum schema/wire/permission identifiers, command retention and
compatible pins remain readiness inputs. Split further only if delivery sizing proves
necessary; do not remove mandatory safeguards to make the sample pass.


Safe-write foundation agreement, 2026-10-04: user approved E1-WRITE. Prove the
bounded generated backend with real authorization/persistence before the E1-REF browser
journey. Existing readiness and failing-first acceptance requirements remain binding.

### Consolidated E1 delivery sequence — discussion checkpoint, 2026-10-04

There are 18 agreed candidate boundaries. This orders their delivery dependencies;
previous discussion order and provisional labels are not implementation numbering.
The grouping below introduces no additional epic, story or delivery phase.

| Order | Candidate | Deliverable |
| --- | --- | --- |
| 1 | E1-ENV | Isolated local/CI base environment and guarded owner setup hooks |
| 2 | E1-P1 | Reproducible application generator and owned backend/web layout |
| 3 | E1-SERVICE | Backend-only generator variant with protected custom extensions |
| 4 | E1-ID | Verified identity/person/actor baseline and explicit existing-user adoption |
| 5 | E1-ACCESS | Current protected app admission and exact capability checks |
| 6 | E1-DISCOVERY | Authorized organization/application discovery |
| 7 | E1-LAUNCHER | Directory/shared menu integration and honest discovery states |
| 8 | E1-WRITE | Proven owned write/attribution/retry foundation |
| 9 | E1-REF | Generated authenticated browser-to-API-to-database reference journey |
| 10 | E1-PEOPLE | Shared employment relationship/period read through its owned service |
| 11 | E1-A1 | Generated Leave sign-in, organization selection and protected shell |
| 12 | E1-CONTEXT | Minimum Leave settings and draft eligibility resolution |
| 13 | E1-CHOICES | Minimum leave-type/duration choice configuration and UI |
| 14 | E1-D1 | Atomic create/resume and current draft context |
| 15 | E1-D2 | Edit, autosave, close and reopen |
| 16 | E1-D3 | Safe organization switching during draft editing |
| 17 | E1-D4 | Deliberate discard and explicit fresh start |
| 18 | E1-D5 | Complete draft return/recovery after interactive sign-in |

Dependency clarifications: ENV proves its base without future domain schemas; each
owner adds actual migrations/fixtures with its own item. P1/SERVICE validate generated
structure without exposing placeholder protected routes. ID/ACCESS extend existing
owners in place. WRITE proves the backend independently; REF adds browser integration.
The reference gate passes before generating Leave business consumers. PEOPLE precedes
draft eligibility but is not required merely to list/select authorized organizations.
Early entry includes safe authentication/return primitives; D5 proves their complete
draft-specific recovery, not retroactive security for earlier stories. CHOICES proves
its configured read/selection behavior; D2 proves persistence/reopening. Runtime draft
write guards are tested when D1/D2 introduce their writes, not deferred to E2.

The first usable Leave outcome remains sign in → select organization → create/resume
draft → autosave → close → reopen. No E2 administration screen or E3 calculation engine
is a hidden prerequisite: E1 has controlled owner provisioning of its minimum inputs.
No attachment, submission, approval, reservation or notification worker enters this slice.

This is a scope/order checkpoint, not epic completion or implementation authorization.
Before E1 planning completion, reconcile granular requirement/UX coverage against all
18 candidates, remove superseded wording from active criteria, resolve concrete entry/
choice/settings/recovery schema gaps and verify story sizing/dependency consistency.
Before implementation, the existing Phase 1/BMAD readiness checks additionally require
applicable exact pins/commands, schema/migration ownership and executable evidence plans.
E4 finalized byte-identity and E5 consequential-action contracts remain binding later.


E1 sequence agreement and scoped coverage reconciliation, 2026-10-04: user approved
the consolidated 18-candidate order. The acceptance map now assigns every existing
12-entry/20-draft inventory item and all 18 scenario groups to named candidates in
that order. This confirms ownership within the extracted E1 inventory, not global
requirements completeness or runtime verification. Current D2/D3/D5 criteria now
reflect the approved defaults, simple failure UX and metadata-only recovery approach;
historical discussion notes remain historical where later decisions supersede them.

The existing tracker now owns the remaining technical-contract closure list. No new
product decision is requested merely to choose a schema field or toolchain version.
Resolve those through evidence within the approved scope; bring genuine behavioral
tradeoffs back to the user. E1 planning completion still requires full scoped source
coverage/sizing validation and closure of applicable pre-story contracts. E2 breakdown
has not started, and neither SP nor implementation is authorized by this consolidation.


Identity technical-contract progress, 2026-10-04: shared contract now links the
source-object/migration ownership inventory. Proposed identity history placement is
separate from access.alembic_version under the existing maintainer; no new runtime
service. E1-ID/ACCESS retain target/grant/compatibility and controlled handover gates.
No application or migration code changed. Next technical closure should validate the
baseline/handover design and exact app-admission schema against these dependencies.


Access schema design progress, 2026-10-04: owning contract contains concrete E1 table/key
and capability/service-policy design with an additive migration sequence. Applies to
ID/ACCESS/DISCOVERY/LAUNCHER/WRITE/REF. Existing membership uniqueness means retirement/
rejoin binding must be resolved before those dependent stories are ready; no implicit
old-grant restoration is accepted. Service policy remains explicit configuration rather
than a new management product. User product approvals remain unchanged.


Access schema agreement, 2026-10-04: user approved the four-table boundary and explicit
service-policy approach. Membership lifecycle is now concretized in the Identity-owned
contract: retire retained row, explicit rejoin creates a new ID, no inherited grants or
roles. E1-ID/ACCESS adopt the constraint/compatibility tests; E2 administration reuses
this lifecycle. No new product workflow, migration execution or readiness pass implied.


Discovery contract progress, 2026-10-04: shared admission contract specifies minimal
Identity projection and Access-only filtered reads with restricted routine roles;
organization pagination follows admission filtering. HTTP checks bind the verified
account and calling-service policy; SQL context is not independent authentication.
E1-DISCOVERY owns actual privilege/RLS/compatibility evidence. No new product choices
or service-management UI introduced, and no implementation-readiness gate passed.


People schema design progress, 2026-10-04: shared owning contract now specifies minimal
employment/period/change records, composite scope constraints and inclusive range
exclusion, while preserving accountless people and one lasting relationship on rehire.
E1-PEOPLE proves authorized own-read and controlled provisioning; E2 supplies shared
assignment administration and mutation-impact contracts. Optional department/location/
supervisor scope remains approved and shared. No new user-visible decision or readiness
pass is implied; exact schemas/privileges and executable fixtures remain technical work.


Leave timezone design progress, 2026-10-04: E1-CONTEXT now references the repository-owned
minimum work-timezone configuration contract. Explicit assignment/default and override
precedence follow existing requirements. Full scheduled edits/administration remain E2;
physical version applicability and local commit guards remain before E1 writer readiness.
No fabricated schedule or duplicated shared employee/location data is introduced.


User-approved draft simplification, 2026-10-04: Leave ADR-0122 governs E1-CONTEXT/CHOICES/
D1/D2 over earlier timezone-required preservation or always-retained invalid-choice
criteria. Permit saving unfinished values without valid timezone; clear definitively
obsolete choices with notice, retaining independent dates/notes. Avoid release-specific
complexity merely to preserve obsolete draft options. Required access/ownership and
revision/lifecycle protections remain. No runtime data is cleared by this documentation.
Current candidate criteria/wire schema must be reconciled before readiness; full work-
profile applicability remains with timezone-dependent consumers, not every draft save.

Platform scope agreement, 2026-10-04: user requested the draft simplicity approach be platform-wide. Accepted platform ADR-0049 now generalizes it; Leave ADR-0122 remains immutable domain-specific adoption. Shared builder/UX/agent guidance updated. No other application acquires Leave-specific employment rules, and consequential/release safeguards remain binding.


Lightweight draft reconciliation, 2026-10-04: D1, CONTEXT and CHOICES active criteria
now follow P-0049/L-0122; the draft wire distinguishes nonblocking setup_notices from
editability and excludes timezone-only mutation rejection. Draft evidence must distinguish
undated ownership discovery from any actual dated eligibility observation. Remaining
technical closure: People period-presence discovery without a timezone, definitive
choice lookup/reset behavior and exact evidence schema. These are owning contract work,
not a renewed request for the already-approved product behavior.


Consumer contract progress, 2026-10-05: E1-PEOPLE discovery includes has_periods;
E1-CONTEXT/D1/D2 evidence distinguishes undated discovery from dated interpretation.
E1-CHOICES/D2 now use the owning definitive choice-resolution contract, with selected-ID
lookup independent of pagination, simple reset notices and no extra save-time catalogue
locking. Existing product decisions remain; schema/fixture readiness is not declared.


Choice-schema refinement, 2026-10-05: E1-CHOICES now references two minimal owned
records (stable type and published metadata version), explicit scoped choice pointer,
metadata bounds and cursor contract. E1 does not select effective submission policies
or implement E3 scheduled publication. Source IDs stay stable; obsolete selection reset
uses the existing simple guarded-save flow. Candidate scope unchanged; no runtime
implementation, fixture application or readiness pass is claimed.


Readiness consolidation, 2026-10-05: the repository implementation tracker now owns
Remaining E1 gates by timing, separating pre-story contracts, implementation evidence
and later-epic/pilot work. Scope and 18-candidate order are unchanged. Existing BMAD
customization/prompt-transition tasks and global coverage/sizing remain open; scoped
E1 mapping is not global completeness. No new product confirmation is required for
routine technical closure and no readiness workflow or application code was executed.


Owner-command progress, 2026-10-05: platform controlled-provisioning contract now defines the bounded E1 setup catalogue and owner-local outcomes/events. Referenced by audit contract, tracker and acceptance map. Current actor/link/membership migration and operator-adapter validation remain required; no runtime command or account/grant change performed.


Recovery metadata progress, 2026-10-05: D5/A1 owning contract specifies return record v1,
30-minute navigation lifetime and no form payload. Missing/expired record never authorizes
write replay. Callback adapter support and lost-reference editor ordering still need
proof before readiness; no new draft UI or retrospective test pass is claimed.


Sign-in simplification — approved 2026-10-05: supersedes the earlier carrier proposal,
carrier agreement and recovery-metadata progress notes above. A1/D5 use supported auth
return navigation and current authorized saved-draft reload, with honest loss of unsaved
typing. The custom sessionStorage record, v1 fields, 4 KiB bound and 30-minute lifetime
are removed from scope. Platform ADR-0032 is unchanged. Current account/access checks,
validated destinations, no automatic consequential action and backend revision/lifecycle
safety remain binding. D2/WRITE must prove delayed-save ordering after reopen; this is
not a new persistent browser recovery feature. Scaffold/shared UX/acceptance/tracker
impacts are recorded in the owning contract. No code or readiness pass is claimed.
Next bounded technical planning item: reproducible toolchain/configuration contract,
followed by remaining source traceability and story sizing; keep Phase 1 gates open.


Toolchain contract progress — 2026-10-05: ENV/P1/SERVICE now reference the environment contract's dependency ownership and planned local/CI command surface. Leave browser is a standalone npm package with one lock; affected Python owners use their own pyproject/uv lock, with Access dependency separation in its owning item. Shared-source identity accompanies local package locks. Existing package files are unchanged. Exact compatibility pins, guarded bootstrap commands, auth callback target and executable evidence remain open. No global inventory/sizing or Phase 1 gate is marked complete.


### E1 sizing discussion — 2026-10-05

The [source/sizing cross-check](../../apps/leave/docs/testing/e1-acceptance-map.md#e1-source-and-sizing-cross-check--2026-10-05)
confirms ID ownership for the existing 12-entry/20-draft/18-scenario extraction, not full
product coverage. It reconciles stale recovery wording and makes locale/accessibility/
performance and Phase 1 governance obligations explicit. ENV must use disposable fixture
scope before later Identity/Access schemas exist. No runtime evidence or readiness pass.

Propose two sequential subdivisions: E1-ID-A migration baseline/adoption then E1-ID-B
person/account/actor and membership/provisioning behavior; E1-D2-A guarded draft save/read
API then E1-D2-B complete browser autosave/close/reopen. Parent requirements and acceptance
IDs remain linked; all other relative ordering stays. This would produce 20 candidates,
subject to user discussion and further sizing validation. No approved candidate sequence
has yet been renumbered or replaced. The first usable Leave outcome stays unchanged.

D2 previously assumed a proven mutable-write foundation that WRITE/REF do not provide;
active criteria now correctly assign that proof to D2. Proposed split makes it independently
testable before browser integration without dropping safety. ID's baseline/adoption work
is separately verifiable before introducing new linking behavior. No accepted ADR changes.


### Approved revised E1 delivery sequence — 2026-10-05

The user approved both proposed splits. This sequence supersedes the earlier 18-item
delivery table; parent E1-ID and E1-D2 remain traceability groupings, not additional
implementation stories. Final numeric story IDs and complete sizing remain pending.

| Order | Candidate | Delivery outcome |
| --- | --- | --- |
| 1 | E1-ENV | Isolated base environment and guarded owner setup hooks |
| 2 | E1-P1 | Reproducible application generator and owned layout |
| 3 | E1-SERVICE | Independently owned HTTP-service generator variant |
| 4 | E1-ID-A | Verified identity migration baseline and controlled adoption |
| 5 | E1-ID-B | Person/account/actor linking, membership lifecycle and controlled transition |
| 6 | E1-ACCESS | Current app admission and exact capability checks |
| 7 | E1-DISCOVERY | Authorized organization/application discovery |
| 8 | E1-LAUNCHER | Directory/menu integration and honest discovery states |
| 9 | E1-WRITE | Proven create/read, attribution and retry backend foundation |
| 10 | E1-REF | Generated authenticated real-stack browser reference |
| 11 | E1-PEOPLE | Shared employment relationship/period read service |
| 12 | E1-A1 | Generated Leave sign-in, organization selection and shell |
| 13 | E1-CONTEXT | Minimum Leave draft context and nonblocking setup notices |
| 14 | E1-CHOICES | Minimum leave-type/duration metadata and choices |
| 15 | E1-D1 | Atomic create/resume and current draft context |
| 16 | E1-D2-A | Authorized exact-input save/read with revision/lifecycle protection |
| 17 | E1-D2-B | Browser autosave, truthful status, safe close and reopen |
| 18 | E1-D3 | Safe organization switching while editing |
| 19 | E1-D4 | Deliberate discard and explicit fresh start |
| 20 | E1-D5 | Saved-draft return after interactive sign-in |

ACCESS depends on completed ID-B, not only ID-A. D3/D4/D5 depend on completed D2-B.
ID-A and D2-A each have independent acceptance before their following item. Existing
Phase 1 generated-reference gate and remaining pre-story/readiness contracts remain
binding. The first usable slice completes at D2-B; later E1 branches still qualify it.
No application code, live account transition or migration is authorized by this approval.

### Candidate Story E1-ID-A: Establish a verified identity migration baseline

**Acceptance scope approved 2026-10-05; not implementation-ready.**
Owner: shared Identity maintainer under the existing Access maintenance boundary.
Depends on ENV's isolated base and the inspected ownership/adoption contract; it does
not require ID-B's new person/link/actor structures or later Access admission changes.

As a platform maintainer,
I want identity schema changes to have one verified migration owner and a safe adoption path,
So that new shared identity work can proceed without conflicting migration histories or
breaking existing sign-in and identity references.

**Acceptance Criteria:**

**Given** the current source inventory and a fresh isolated database,
**When** controlled setup creates the identity baseline,
**Then** the declared identity-owned objects are created once through the dedicated
Identity history, with a separate version table and restricted migrator/runtime roles,
**And** Access history, Supabase-managed Auth tables and other owners' objects are not
silently taken over. Project-owned public routines and Auth-attached hooks are explicitly
included where the ownership inventory assigns them to Identity.

**Given** a synthetic existing-schema fixture representing a supported legacy baseline,
**When** adoption checks definitions, constraints, owners, grants and dependencies,
**Then** a matching baseline may be adopted without recreating its records,
**And** an unexpected mismatch blocks adoption with a safe diagnostic and an explicit
repair/recovery path; no blind migration stamping or automatic destructive repair.
Account UUIDs and existing identity/organization/attribution references keep their meanings.

**Given** the SQL composer and the new Identity migration history,
**When** the selected clean/adopt setup route runs,
**Then** only one migration authority manages each adopted object,
**And** source handover is implemented in the owning composer/configuration, never by
editing generated migration output. Remaining Finance/content dependencies and supported
clean bootstrap are accounted for, without inventing historical receipt conversion.

**Given** legacy Auth hooks, role lookup, self-profile updates and routine grants,
**When** characterization and restricted-role checks exercise them,
**Then** intended existing sign-in/profile behavior remains supported while privileged
self-update, unauthorized role lookup and unsafe helper execution are prevented,
**And** function ownership/search paths/execute grants are explicit. Preserve intended
compatibility, not an observed authorization flaw; do not defer baseline privilege safety
to ID-B. Record intentional tightening and affected-consumer evidence.

**Given** migration failure or an incompatible adoption change,
**When** coordinated setup/release attempts to proceed,
**Then** dependent activation is blocked, completed changes are reported accurately and
an explicit recovery procedure is exercised on disposable data,
**And** API startup cannot migrate, runtime identities cannot perform DDL and failure
never triggers automatic destructive downgrade. Use the approved maintenance route if
ordinary previous-version compatibility cannot be maintained.

**Given** the baseline has been built through failing-first acceptance and focused tests,
**When** this item is completed,
**Then** clean/adopt/mismatch/privilege/failure tests pass independently of ID-B,
**And** exact commands/results, owned migration inventory, recovery instructions and
reusable scaffold/coordinator changes are recorded. No production user or database is
used as a destructive test fixture or claimed migrated by synthetic evidence.

**Traceability:** Parent E1-ID foundational contribution; E1-ENTRY-02/06/10/12;
E1-AC-15/17/18, with legacy sign-in compatibility contributing to AC-12. Platform
ADR-0015–0020/0023/0025/0035/0042/0045; owning
[identity inventory](../../platform/docs/architecture/contracts/identity-migration-ownership-inventory.md).
ID-B owns the new identity/link/membership behavior and small-cohort transition rehearsal.

**Impacts/sizing:** One baseline/adoption outcome with necessary privilege and recovery
checks. Update reusable migration/coordinator/fixture guidance with the proven work;
no shared UI or second identity runtime service. Existing agent instructions suffice;
update runbook/changelog and source links. Accepted ADRs unchanged. Exact handover,
role/grant schemas and compatibility fixtures remain pre-story inputs. Detailed runtime
proof follows during authorized implementation; this draft supplies none of that evidence.


ID-A acceptance agreement — 2026-10-05: user approved the verified baseline/adoption
story criteria. Remaining schema/handover/compatibility inputs and failing-first runtime
evidence are still required; no migration or readiness assessment was performed.

### Candidate Story E1-ID-B: Link accounts to people and preserve membership history

**Acceptance scope approved 2026-10-05, with history/retry/transition clarification; not implementation-ready.**
Owner: Identity under the existing shared maintainer. Depends on completed ID-A and
ENV, with the controlled owner-provisioning contract. Supplies Identity behavior to
later ACCESS/PEOPLE consumers; it does not implement app grants or employment records.

As a platform administrator,
I want verified accounts connected to stable people and historical actor identities,
with explicit organization membership changes,
So that applications identify people consistently without granting unintended access
or losing who performed earlier actions.

**Acceptance Criteria:**

**Given** the verified Identity baseline and a person with or without a login account,
**When** an authorized owner command creates the person or links an existing account,
**Then** person, account and actor identifiers keep their separate declared meanings,
**And** each account has at most one active person link. No account is required merely
to represent a person; neither creation nor linking creates employment, membership,
app enablement or permissions. Existing account UUIDs remain unchanged where retained.

**Given** an explicit verified account/person mapping and trusted operator identity,
**When** linking is accepted,
**Then** the link, durable actor association, required change evidence and compact
operation outcome commit atomically under the Identity owner,
**And** verification evidence is an opaque reference, not a copied identity document.
Legacy human actor UUIDs remain interpretable; service actors have their own stable IDs
without requiring fake people or employees. Runtime credentials, self-profile edits and
actor IDs supplied in a manifest cannot perform privileged linking.

**Given** matching emails, a conflicting existing link or several accounts linked to one person,
**When** provisioning or resolution occurs,
**Then** email alone never merges people, a conflicting link is rejected rather than
overwritten, and accounts retain separate membership/permission authority,
**And** E1 supports absent or identical verified mapping, not an account-merging UI or
arbitrary relinking workflow. Missing/inactive link or actor setup yields the declared
safe state without inventing a person, copying grants or treating an outage as absence.

**Given** an account and organization with no active membership,
**When** an authorized first join or explicit rejoin names the expected prior history,
**Then** the owner serializes that scope and creates one new membership ID with the
explicitly authorized owner flag (default false) and no inherited roles/grants,
**And** simultaneous or delayed commands cannot create two active memberships, revive
a retired row or mistake a later membership for the outcome of an earlier join.
Existing retained membership IDs and their historical references remain stable.

**Given** an active membership or a retired membership followed by a rejoin,
**When** retirement, replay or a delayed command is handled,
**Then** retirement targets the exact membership ID and expected revision; retired rows
remain retired, and an old retirement cannot affect the replacement membership,
**And** replay returns its original compact outcome without a duplicate event. Current
Identity lookup and legacy role/hook routines reject retired or foreign membership
claims. Employment is neither ended nor recreated by membership changes.
For example, a retried removal of Ana's old membership cannot remove the new access
membership created when she rejoined. Shared person/employment identity, retained drafts
and Leave request history remain associated with the same enduring employment relationship;
a new membership does not delete or duplicate them. Subsequent authorized Leave access
can expose that retained history under current permissions. People/Leave consumers prove
that integration in their owning stories; ID-B does not depend on their future tables.

**Given** a changed payload under an existing operation ID, evidence-write failure,
unauthorized operator or unsafe fixture target,
**When** an owner command is attempted,
**Then** it fails with a safe stable error and no partial accepted identity change,
**And** lost-response recovery resolves the original operation under current operator
authority. Actor/link/membership evidence contains no credentials or whole profile dumps.
Required local evidence failure rolls back; optional diagnostic-export failure does not.

**Given** synthetic accounts representing the three existing noncritical PtS production
users identified by the user (not three Leave employees),
**When** the retained-account path and supported manual-recreation alternative are rehearsed,
**Then** explicit mappings preserve old attribution and identify intended replacement
memberships and separately owned app grants,
**And** account replacement does not rewrite immutable history or silently restore old
access. Preserve read-only PtS/Scribeswell content; no user-document transfer, historical
receipt conversion, bulk-import framework or production-user test fixtures are required.
The later ACCESS item verifies actual membership-bound app admission and regrant behavior.

**Given** the new Identity membership constraints and their supported existing consumers,
**When** the item is completed and its eventual activation is prepared,
**Then** Identity-owned tests independently prove linking, membership races, retirement,
legacy hook/role compatibility, protected references and owner-command recovery,
**And** a release gate prevents activation of rejoin/new-constraint behavior with old
Access checks or incompatible writers. ACCESS supplies the subsequent v1/v2 grant-binding
integration proof before coordinated activation. Passing ID-B alone does not authorize
live cutover or claim that downstream application-access behavior has been tested.

**Traceability:** Parent E1-ID; E1-ENTRY-01/02/05–07/10/12; E1-DRAFT-16 identity
foundation only; E1-AC-12/13/15/17/18 contributions. Accepted platform ADR-0020/0025/
0035/0042/0045/0046; [identity contract](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#person-account-actor-distinction),
[membership lifecycle](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#membership-retirement-and-rejoining--concrete-e1-design-2026-10-04)
and [owner provisioning](../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md).
Current Access enforcement is E1-ACCESS; one employment per person/organization is
E1-PEOPLE; administration screens remain E2. No new shared identity HTTP service.

**Impacts/sizing:** Promote proven owner-command/evidence fixtures and migration patterns
with this item; keep identity rules in the owning service, not Leave copies. No new shared
UI; existing agent ownership/ATDD instructions suffice. Update owner runbook, synthetic
transition instructions, compatibility notes and acceptance mapping. Accepted ADRs remain
unchanged. Exact schema/role/command bounds and operator adapter remain readiness inputs;
observe failing acceptance before implementation and record actual passing commands then.
This is a minimal controlled-provisioning scope, not a general identity administration suite.


ID-B acceptance agreement — 2026-10-05: user approved after clarification that membership
controls access separately from person/employment and retained Leave history. Retrying
an old membership removal cannot remove a later rejoin membership. The three-user
transition refers to the existing PtS cohort, rehearsed with synthetic accounts. No new
product policy, production change or readiness pass; accepted ADRs remain unchanged.
Next child-story detail is D2-A; intervening previously approved candidate scopes stand.


### Candidate Story E1-D2-A: Save and read my draft input safely

**Acceptance scope approved 2026-10-05; not implementation-ready.**
Owner: Leave API, with same-item promotion of proven generic write helpers. Depends on
D1 create/resume, CONTEXT/CHOICES and earlier Identity/Access/People and WRITE foundations.
It introduces the first mutable draft-save proof; WRITE's create/read sample is not
that proof. Pass independently through real API/database tests before D2-B's browser UI.

As an employee with an editable draft,
I want the details I save to be preserved accurately and protected from conflicting changes,
So that I can resume my work without losing acknowledged input or overwriting another save.

**Acceptance Criteria:**

**Given** my authorized active draft and its current revision,
**When** I save a complete, structurally valid input-v1 envelope through the declared API,
**Then** the exact bounded text, selections, input-format context and inactive-mode entries
are persisted, including unfinished/invalid dates or hours and saved null selections,
**And** no trimming, default filling, date swapping, calculation success, reservation or
submission is introduced. Malformed envelopes, unsafe/unknown fields and exceeded bounds
receive safe field errors without partial replacement or silent truncation.

**Given** a save passes current authority, ownership and applicable employment checks,
**When** its local transaction commits,
**Then** revision and editability are checked atomically, and input, one revision advance,
server-derived update attribution and compact operation outcome commit together,
**And** client input cannot change owner, organization, lifecycle or attribution. Failure
before commit leaves no partial accepted save. Preserve the approved bounded shared-input
observation and execution deadlines, with external waits outside business write locks.

**Given** incomplete calculation setup or changed configuration,
**When** an otherwise authorized draft save is checked,
**Then** missing/invalid work timezone alone does not block preserving input, while actual
ownership/access failure, no-period setup or confirmed ended-employment restrictions retain
their agreed behavior,
**And** no invented date or eligibility result substitutes for missing setup. Definitively
obsolete choice clearing uses CHOICES' normal guarded-input update; unrelated dates/notes
remain intact. A read never clears input and an outage never proves a choice obsolete.
No full policy, schedule or submission engine is required for this item.

**Given** the same save is retried concurrently or after its committed response was lost,
**When** the original scoped operation identity and unchanged command are presented,
**Then** one saved revision and its original compact outcome are recognized without
repeating the mutation,
**And** changed input under that identity is rejected. Current authority is checked for
outcome lookup; an old result is not a claim about current draft content or editability.
An unresolved lookup does not claim rollback. No note/full-input snapshots are added to
outcomes, diagnostics or duplicate per-save business audit records.

**Given** two writes starting from the same revision, including a delayed save from an
editor that has since closed or navigated through sign-in,
**When** those writes reach the transaction boundary in either order,
**Then** only the first accepted write advances that revision and the other receives a
revision conflict without overwriting it,
**And** the response never authorizes a client to silently adopt the new revision and
resend stale input. If the delayed write finishes before reopening reads current state,
that read includes it; if it finishes after the read, the same revision checks resolve
the race. Lost browser context neither reconstructs the old request nor proves rollback.

**Given** a draft has been closed, is missing, or is not writable by this caller,
**When** an old or new save is attempted,
**Then** it cannot recreate, reopen or transfer the draft, and cannot change a later draft,
**And** errors reveal no unauthorized input. E1 tests its active/discarded lifecycle using
controlled owner fixtures before D4 exists; E5 adds submitted-state integration later.
No discard or submission command implementation is moved into this item.

**Given** a saved draft and current permission to read it,
**When** it is fetched through the owning API,
**Then** input and revision come from a coherent current snapshot with truthful lifecycle,
editability and nonblocking setup notices,
**And** reading creates no draft, revision or duplicate audit event. Passed selected leave
dates do not expire it. Requests with another account, organization, employment or operation
scope cannot disclose protected data, including through pooled database connections.

**Given** the save/read contract is implemented through ATDD and focused TDD,
**When** this item is completed,
**Then** real HTTP/current-service/restricted-database checks prove round-trip preservation,
atomic failure, concurrent revisions, lost-response replay, delayed-save ordering and
scope isolation independently of browser code,
**And** declared OpenAPI/generated TypeScript contracts, safe error fixtures and generic
write helpers/templates stay aligned. Record exact commands/results and initial acceptance
failure. D2-B supplies browser scheduling, conflict presentation, Close/reopen, human UX
checks and integrated performance evidence; those are not claimed passed here.

**Traceability:** Parent D2; E1-DRAFT-05–12/15–20 with backend contributions only;
E1-AC-03/05/06/13/14/15/17, plus backend support for AC-01/07/08/12/18. Sources:
[features §7](../../apps/leave/docs/features.md#7-leave-application-experience),
[draft persistence contract](../../apps/leave/docs/architecture/contracts/e1-draft-persistence-and-recovery.md),
[choice contract](../../apps/leave/docs/architecture/contracts/e1-draft-choice-resolution.md),
platform ADR-0012/0013/0019/0021/0022/0025/0031/0033/0035/0044/0048/0049 and
Leave ADR-0118/0121/0122. Numeric route/schema limits and deadlines remain in the owning
contracts rather than duplicated here. No new HMAC/key-rotation or browser recovery store.

**Impacts/sizing:** Extend D1's owned persistence rather than create a second draft model.
Promote only proven generic revision/transaction/retry/schema fixtures; Leave retains
input and lifecycle rules. No new UI in this item; update generated client contracts,
owner docs, scaffold changelog and acceptance map together. Existing agent guidance and
accepted ADRs suffice. Schema/constraint/error completeness and toolchain gates remain
required before readiness. No code, migrations or runtime tests performed by this draft.


D2-A acceptance agreement — 2026-10-05: user approved exact input save/read with current
authority, atomic revision/lifecycle/outcome protection and duplicate/delayed-save checks.
Pre-story contracts and implementation evidence remain required. No code or runtime tests.

### Candidate Story E1-D2-B: Edit, autosave, close and reopen my draft

**Acceptance scope agreed through 2026-10-05 refinements; not implementation-ready.**
Owner: Leave browser, consuming D2-A's proven save/read API and earlier A1/CONTEXT/CHOICES.
Uses the generated API client and real Access/People/database stack. This completes the
first usable slice; subsequent D3/D4/D5 add their dedicated switching/discard/sign-in
journeys without deferring the current item's authorization or save safety.

As an employee preparing leave,
I want the form to save my work automatically and show clearly whether it is saved,
So that I can close it and continue later without re-entering acknowledged details.

**Acceptance Criteria:**

**Given** Apply for leave opens or resumes my authorized draft,
**When** I edit its leave type, duration mode, date/duration inputs or note,
**Then** the form uses the declared input-v1 contract and preserves inactive-mode values,
unfinished input and saved null selections,
**And** no type is auto-selected. First type selection in a new request initializes
Full days only if permitted; restored or later explicit choices are not overwritten.
Bounds produce understandable feedback without silently truncating text. Definitively
obsolete choices clear with a brief notice and normal save, preserving independent input;
outages do not clear values. Locale changes do not reinterpret recorded input formats.

**Given** editable changes and no save/recovery in flight,
**When** typing pauses for one second or continues for five seconds,
**Then** autosave dispatches the latest coalesced snapshot using the declared revision
and operation identity, with at most one save/recovery sequence in flight,
**And** show Draft saved only for acknowledged current input, with no redundant Save
button. A successful acknowledgement advances the base revision for subsequent input
without replacing newer typing. Saved means all current input has been acknowledged;
a delayed acknowledgement never labels newer unsaved input Saved or resets the editor.

**Given** saved input, pending changes or an in-flight save,
**When** I use Close, desktop Escape or in-app mobile Back,
**Then** saved input closes immediately; pending input is flushed immediately and any
in-flight save resolves through the bounded existing flow before successful close,
**And** closing returns to useful My Leave context/focus without deleting the draft.
After closing, Apply for leave resumes the same current saved values with the small
unfinished-application note; no Drafts section, notification badge or replacement draft.
Browser termination is not treated as a guaranteed save opportunity.

**Given** a save fails or its outcome remains uncertain after bounded automatic recovery,
**When** the form displays the failure,
**Then** show inline Changes not saved with Retry under platform ADR-0050/Leave ADR-0123,
retaining local input and allowing typing without a separate Keep editing button,
**And** Retry uses the safe original-operation flow where applicable, with no endless
loop or fresh competing save. Continued typing does not bypass an unresolved operation.
Only on attempted exit after bounded saving remains unconfirmed, ask Your latest changes
may not be saved. Close anyway? with Stay / Close anyway. Close anyway leaves the stored
draft intact and does not promise
rollback of an already-sent save or survival of unsent typing. Users see no operation-ID,
fingerprint or commit explanation as a required part of leaving the form.

**Given** another tab saved first or the draft was closed elsewhere,
**When** the API reports a revision/lifecycle conflict,
**Then** stop autosaving, preserve local edits where practical, and offer the approved
current-state navigation such as Review saved draft or Back to My Leave,
**And** recheck access before showing saved details. Do not silently merge, update the
expected revision and resend, recreate a draft, or discard local edits merely because an
older response arrived. E1 closed-state tests use controlled fixtures until D4 delivers
its command; E5 adds submitted-state integration without being an E1 prerequisite.

**Given** access, employment or setup changes during editing,
**When** the next protected operation returns its current state,
**Then** handle read-only/setup/denied/unavailable states without false Saved feedback,
remove protected content when access is lost, and pause writes when authentication is required,
**And** missing work timezone alone does not block authorized preservation or force an
administrator-contact step. Use the existing supported auth-return primitives; D5 owns
the complete interactive-sign-in journey. Unsaved typing has no guaranteed durable browser
store. A stale response cannot repopulate a different account/organization's editor.

**Given** keyboard, screen-reader, zoom or phone use,
**When** I edit, encounter save/conflict feedback or close the form,
**Then** labelled controls, visible focus, associated errors and meaningful status
announcements follow the approved shared UX without stealing focus on every keystroke,
**And** desktop drawer/mobile page changes retain input and a useful active field; required
actions remain reachable with the phone keyboard. Shared language preference and English
fallback remain consistent. No full Portuguese translation delivery is claimed by E1.

**Given** the real isolated stack with synthetic authorized users and organizations,
**When** this story is verified through TypeScript Playwright and focused scheduling tests,
**Then** sign in → select organization → create/resume → edit/autosave → close → reopen
returns the exact acknowledged values through real persistence, with failure, delayed
response, concurrent-tab and cross-scope cases covered,
**And** evidence records actual supported-browser/device and applicable human accessibility
checks at their qualification points. Measure agreed open/save/close targets at 500 and
1,000 employee fixture scales, identifying concurrency/history assumptions. Engine
emulation, mocked saves or configured timeouts do not establish those results.

**Traceability:** Parent D2; E1-DRAFT-02/04–12/15–20; E1-ENTRY-05/06/08/11/12;
E1-AC-01/03–08/12–18 as applicable, with D5 retaining full auth-return evidence. Sources:
[features §7](../../apps/leave/docs/features.md#7-leave-application-experience),
[draft contract](../../apps/leave/docs/architecture/contracts/e1-draft-persistence-and-recovery.md),
[Leave experience](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md),
[environment/performance contract](../../apps/leave/docs/testing/e1-environment-and-dependencies.md).
Platform ADR-0031/0032/0033/0048/0049 and Leave ADR-0075/0118/0121/0122 apply.

**Impacts/sizing:** Wire the existing shell/choices to D2-A, promoting proven domain-neutral
input/status/close primitives and disposable reference checks in the same item. Leave
owns field meaning, routes and lifecycle presentation; no shared runtime draft service.
Update client/UX/test traceability, scaffold changelog and documentation. Existing agent
instructions and ADRs suffice. Observe failing acceptance before implementation; retain
exact commands/results. D2-A's backend proof limits this item to the complete browser
interaction and its integration evidence. No code, browser run or readiness pass here.


Failure-UX refinement approved — 2026-10-05: platform ADR-0050 and Leave ADR-0123
replace the earlier three-choice presentation with inline Retry and an exit-only
Stay / Close anyway confirmation. D2-B active criteria updated; earlier discussion
wording is superseded. User is considering the value of Leave drafts; no draft removal
or change to the first slice has been agreed. D2-B overall acceptance remains pending.


Saving convention agreement — 2026-10-05: user accepted platform ADR-0051/Leave ADR-0124
and continued planning. Retain the autosaved Leave request with Draft saved feedback;
use explicit whole-form Save for business administration and separate immediate personal
preferences. This withdraws the suggested direct autosave of descriptive administration
fields. D2-B incorporates this and the approved ADR-0050 inline/exit failure refinement.
The original first slice and previously approved D3/D4/D5 scopes stand; no need to repeat
their product approval. Reconcile remaining active source wording, complete missing source
coverage and validate remaining technical contracts/sizing before declaring E1 complete.
No SP run, runtime evidence or implementation permission is implied.


Active E1 reconciliation — 2026-10-05: updated draft inventory, parent D2 and D3 criteria,
source features, contract and acceptance map to current inline Retry/exit-only confirmation.
D3/D4/D5 name D2-A/D2-B dependencies; prior user scope approvals stand. Earlier dated
three-choice/carrier proposals remain historical and superseded. The existing tracker
now has a current E1 closure checkpoint distinguishing outstanding planning contracts
from delivery evidence. No global source-completeness, final sizing or readiness pass
is claimed; source extraction is the next planning task, not renewed product confirmation.


## Supplemental source coverage: permissions, UX and operations — 2026-10-05

These E1-X references identify existing source obligations and their first consumers;
they are not new feature requirements or a duplicate specification. They supplement the
12 entry/20 draft inventory. Every row specifies E1 versus later-epic evidence to avoid
both lost requirements and an oversized first slice. They do not establish completion
of the twenty-area feature catalogue extraction or runtime compliance.

Sources: [Permissions](../../apps/leave/docs/features.md#permissions),
[UX requirements](../../apps/leave/docs/features.md#ux-requirements),
[NFRs and operational targets](../../apps/leave/docs/features.md#non-functional-requirements),
[MVP acceptance](../../apps/leave/docs/features.md#mvp-acceptance-summary),
[spine](../../apps/leave/docs/architecture/ARCHITECTURE-SPINE.md),
[Leave DESIGN](ux-designs/ux-leave-2026-09-15/DESIGN.md),
[Leave EXPERIENCE](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md),
[UX handoff](ux-designs/ux-leave-2026-09-15/handoff-coverage.md),
[platform EXPERIENCE](../../platform/EXPERIENCE.md) and
[observability direction](../../platform/docs/operations/observability-and-ai-investigation-direction.md).

| ID | Source obligation | E1 owner / evidence | Later consumer / boundary |
| --- | --- | --- | --- |
| E1-X01 | Permissions: exact capabilities and active organization/resource scopes; grant union must preserve each scope. | ACCESS/A1/D1/D2-A: own read versus own manage, no role-name shortcut; AC-13/15. Explicit fixture grants suffice for the first slice. | E2 default/custom role management and scoped combination tests; E5 approval-step/self-approval and on-behalf checks. No wildcard permission is automatically granted. |
| E1-X02 | Permissions and platform role lifecycle: application-owned custom roles, impact review, deletion only when unassigned, holder return navigation and audit. | No role editor in E1; ACCESS provisions only exact controlled setup grants. | E2 owns complete role UI/lifecycle and new-permission review; cannot claim covered by Access check endpoints. |
| E1-X03 | Permissions: approvers may read request type/note, but sensitive documents need separate permission; on-behalf rights do not arise from approval authority. | D1/D2 restrict own draft data, including IDs in direct API/outcome reads; AC-15. No approver access is inferred. | E4 document authorization; E5 assigned-request and on-behalf scope; E6 cancellation/replacement rights. |
| E1-X04 | Features UX/ADR-0066: start on My Leave, authorized sections and separately scoped action badges. | A1 opens the minimum My Leave workspace; LAUNCHER/A1 hide unauthorized/unimplemented destinations without fetching protected counts; AC-01/13/15. | E2 Manage Leave surfaces; E5 Approvals and actionable badges/notification independence. No fake empty queue proves later behavior. |
| E1-X05 | Features/EXPERIENCE language: shared preference follows organization changes with English fallback, independent of access/timezone/calculation. | A1/D3, REF where shared shell is proven: preference isolation/retention; D2-B input formats remain unchanged. AC-09/16/17. | First notification consumer uses recipient locale; Portuguese translation release remains separately planned, not an E1 deliverable. |
| E1-X06 | Features dates/UX: English display such as 15 Sep 2026; translatable labels with stable stored values. | CHOICES/D2-A/B: distinguish date presentation from versioned raw editor input; test locale change without reinterpreting partial text. AC-03/17. | E3 calculation/date-only semantics, E5 history and notifications, E7 exports. No universal UTC timestamp conversion for business dates. |
| E1-X07 | DESIGN: light-mode Neutral + Quiet lagoon, inherited semantic colors/system typography/control dimensions; no theme switch. | P1/REF/A1/D2-B: rendered visual/token checks and responsive bounds, AC-16/18. Existing numerical contrast results are not browser/AT certification. | Each later surface inherits and verifies the same design; dark mode remains deferred. |
| E1-X08 | UX accessibility: WCAG 2.2 AA, keyboard/date navigation, focus, status not color-only, zoom/reflow and meaningful announcements. | A1/CHOICES/D2-B/D3/D4/D5: AC-16 automated and human evidence per introduced surface; no status announcement on every keystroke. | All later surfaces extend evidence; E8 release qualification cannot replace earlier accessible implementation. |
| E1-X09 | EXPERIENCE interaction: drawer to mobile page retains input/active field; close restores useful focus; required actions visible with keyboard. | D2-B and shell/reference controls: resize, mobile keyboard, Escape/in-app Back and return-focus fixtures, AC-08/16/18. | E2/E3 related-record edit-return flows and later collections retain their own specified context. |
| E1-X10 | Platform dependency behavior: failures are operation-specific; no permanent outage inference, endless retries or false denial/success. | ACCESS/PEOPLE/CONTEXT/D2/D5 adapters: AC-07/13/17; unavailable, missing, read-only and denied are distinct, including independent-data availability. | E3/E5 partial balance/history panels and notification failure remain independent where domain contracts allow. |
| E1-X11 | ADR-0050/0051: drafts autosave, administration saves explicitly, separate preferences apply immediately; no field-level mixture. | D2-B/D3: Draft saved, inline Retry and exit-only choices; AC-04/07/08/09. | E2/E3 whole-form Save/Cancel and existing Review/Confirm; no hidden field writes or additional administration draft system. |
| E1-X12 | NFR isolation across API/DB/cache/log and later jobs/files. | Every protected E1 consumer: AC-15 restricted-role/pool/context/cache tests; AC-17 excludes sensitive data from diagnostics/errors. | First file and worker consumers E4/E3/E5 extend isolation; E8 integrates release evidence. |
| E1-X13 | NFR encryption in transit and at rest. | ENV/P1/SERVICE define explicit transport/credential configuration; deploying any protected E1 data requires evidence of encrypted exposed transport and storage coverage. Isolated local fixture transport must be documented, never presented as production compliance. | Deployment owner/E8 verify actual database, volumes and backups; E4 additionally verifies content storage/transfer. Provider defaults are not assumed evidence. |
| E1-X14 | NFR idempotence and optimistic concurrency. | WRITE/REF create replay; D1/D2-A/D4 real retries/revision/lifecycle and closed-row guards, AC-02/05/06/10/11. | E2/E3 configuration concurrency, E3 deterministic accrual, E5 consequential writes/events and E6 corrections retain their stronger contracts. |
| E1-X15 | Spine AD-13 / observability: safe logs, operation/trace correlation, basic backend OpenTelemetry with bounded asynchronous export. | SERVICE/WRITE/REF and first HTTP consumers: demonstrate API-to-shared-service trace linkage and business success despite diagnostic-export failure; supplement AC-17/18. Distinguish trace ID from operation identity; no payload logging. | First workers add linked processing evidence; E8 verifies a working external monitor. Browser instrumentation and vendor comparisons do not block E1. |
| E1-X16 | Phase 1/spine: configuration validation, API health/readiness, separate runtime/migrator identities and controlled failure-blocked activation. | ENV/P1/SERVICE/ID-A/REF: actual disposable failure/role/startup checks, AC-15/18; API readiness reflects required dependencies. | Workers/notification delivery expose separate health when introduced. A notification outage must not disable unrelated API work. |
| E1-X17 | NFR recoverability: tested migration and operational recovery, one-hour RPO/four-hour essential-service RTO/thirty-day backups. | ID-A/REF rehearse scoped migration failure/recovery; preserve sufficient declared source/lock/config evidence. This is not a full production restore. | E8 demonstrates integrated identity/config/database/private-content restoration before pilot; quarterly/major-change repeats and outbound-side-effect hold remain mandatory. |
| E1-X18 | NFR retention/deletion and consequential audit. | D1/D2-A/D4: attribution, compact outcomes and cleared discarded input; no automatic active-draft/outcome expiry, duplicate autosave audit or content snapshots. AC-10/11/17. | E4 file cleanup, E7 authorized audit views and E8 retention/privacy controls. Future closed-row cleanup needs safe retry/reference policy; do not invent an X-day purge. |
| E1-X19 | NFR deterministic dates and representative performance/browser qualification. | CONTEXT/D2 and ENV: undated preservation versus actual dated observations; approved 500/1,000 fixtures and open/save/close p95 targets with declared load assumptions; AC-01/03/04/08/14/16. Actual browser/device evidence remains distinct from engine emulation. | E3 arithmetic/allocation/time boundaries; E7 report workload and E8 qualification. E1 timings do not qualify every later endpoint. |
| E1-X20 | ADR-0036/0038: private signed lifetimes and finalized byte identity. | No E1 attachment dependency or test-pass claim. | E4 must prove association/cleanup and immutable verified bytes against capability replay/racing uploads before readiness; E8 restoration retains consistent associations. |
| E1-X21 | ADR-0120/spine: API/heartbeat and overdue-notification alerts, recovery-age and integrity alerts, grouping and verified recovery. | SERVICE health/instrumentation supplies signals; no unused worker or alert console in the draft slice. | E3/E5 worker/delivery consumers supply signals; operations/E8 validates configured thresholds and routing before pilot. No implied staffed SLA. |
| E1-X22 | MVP acceptance/Phase 1: ATDD/TDD, source traceability and same-item scaffold/shared-UI/context/docs/ADR impact. | Every story records applicability and evidence; ENV/P1/SERVICE/WRITE/REF prove generated output rather than template text. AC-18; BMAD customization/prompt transition stays in tracker. | Applies across E2–E8. No planning document or migration discovery check substitutes for observed acceptance failure and passing runtime suites. |

Findings closed by ownership assignment: encryption lacked an explicit first-release
evidence boundary; backend tracing had been subsumed under generic safe logging; visual
tokens/localization needed explicit first-consumer checks. These obligations were already
in authoritative sources, so no new product scope or user decision is introduced. They
are now linked to delivery evidence, not marked implemented. Remaining source extraction
covers detailed business catalogue/UX flows and later-epic test ownership; global coverage
and final story sizing remain open.


## Business-feature and UX journey coverage — 2026-10-05

This pass assigns concrete business outcomes from the approved feature catalogue and
UX key flows. BIZ identifiers are planning references, not replacement requirements.
The source's examples, ADRs and detailed rules stay authoritative. Rows group related
outcomes for ownership; they are not final stories, estimates or proof of exhaustive
atomic rule coverage. In particular, §6's extensive entitlement rules need their own
rule/example ledger before E3 decomposition can be declared complete.

Sources: [feature catalogue](../../apps/leave/docs/features.md#feature-catalogue),
[state models](../../apps/leave/docs/features.md#state-models),
[UX key flows](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md#key-flows),
[architecture rules](../../apps/leave/docs/architecture/ARCHITECTURE-SPINE.md#invariants--rules)
and [migration runbook](../../apps/leave/docs/operations/migration-runbook.md).
All ordinary configuration editors follow platform ADR-0051; consequential review and
confirmation remain explicit. An owning epic must later assign each row's acceptance
examples to concrete stories/tests rather than treating this table as execution evidence.

| ID | Source outcome / acceptance distinction | Owner and dependencies |
| --- | --- | --- |
| BIZ-01 | §1/Permissions, UX flows 14/16: authorized invitations/membership, application enablement, default/custom roles and holder-impact review. | E1 supplies Identity/Access enforcement and controlled setup; E2 supplies authorized administration UI, role lifecycle and explicit access changes. E5 adds notification deep links with current access. |
| BIZ-02 | §1, UX flow 15: non-sequential setup derives Not started/Needs review/Ready/Couldn't check from current configuration; no manual complete flag, consultant-email tracking or assumed missing opening balance. | E2 checklist foundation; E3 adds policy/entitlement checks as available. E8 owns import evidence separately. Do not mark the entire checklist Ready while required later configuration is absent. |
| BIZ-03 | §2, UX flow 15a: shared person/employment, one enduring person/organization relationship, periods and optional manual supervisor/department/location; no duplicate Leave identity. | E1 PEOPLE read/controlled fixtures; E2 shared owner writes and Leave settings UI with explicit scope/history. Account linking/access remain separate. Graph topology sync deferred. |
| BIZ-04 | §2/3, UX flow 11: effective-dated profiles, organization default, explicit assignments/overrides, holiday calendars; shared location never silently changes work settings. | E2; E1 only minimum draft context. E3 calculation consumes historical schedule/timezone. E6 handles historical corrections with effects. |
| BIZ-05 | §3/4: stable identity versus effective versions and archive markers; prevent profile archive while default/current/scheduled dependencies exist; retain used policy/type history. | E2 profiles, E3 policy/types; authorized dependency navigation and explicit Save/Review. Creating a profile never assigns employees automatically. |
| BIZ-06 | §4, UX flow 8: full policy metadata/conditional editor, active/effective dates and current versus scheduled publication; organization confirmation of starter rules. | E3 configuration; E1 CHOICES owns minimal type/mode metadata only. Publishing does not silently replace existing request snapshots/routes. |
| BIZ-07 | §5, UX flow 10: recurring override versus one-off adjustment; recurring choice persists, changes at leave-period boundaries, no automatic end/reset. | E3, using E2 employment/settings; test inherit/custom transitions and reviewed effects. E6 correction consumers reuse its invariants. |
| BIZ-08 | §6, UX flow 9: Add/Deduct adjustment, reason/effective date, before/after/request impact, Review/Confirm and immutable correction by another adjustment. | E3 with first notification/outbox delivery prerequisite; cannot postpone notifications until E5. E6 reuses authorized corrections, not a competing ledger editor. |
| BIZ-09 | §6/8: backend-authoritative on-demand daily/upfront/monthly entitlement and manual grants; immutable actual events and historical inputs; no worker-posted daily accrual/double count. | E3 calculation foundation; exact earning/proration/cap/carry-over/rounding rule ledger remains to extract. E1 draft values are not calculation evidence. |
| BIZ-10 | §6: date-by-date future availability, protect prior reservations, earliest eligible expiry first, inclusive expiry and effective-date earning in employee work timezone. | E3 projection/allocation; E5 reservation writes. Resolve deterministic same-expiry ties before the allocation story is ready. Later accrual cannot fund an earlier shortfall. |
| BIZ-11 | §6, ADR-0109–0112: expiry/rollover before earning, stable server order for same-day events, modest immutable action snapshots, fresh consequential validation/confirmation. | E3 establishes ordering/evidence; E2/E3 relevant configuration writers participate; E5/E6 consume. No historical-code execution engine or balance-cache prerequisite. |
| BIZ-12 | §6/7, UX flow 3a: existing reservation protection and increased unpaid amount on pending requests requires actor/reason, previous/new amounts and employee acknowledgement. | E3 models impact; E5 implements pending-request acknowledgement/finalization. Before E5 activation, update/test existing E2/E3 writers for actual pending requests. E6 corrections use the same contract. |
| BIZ-13 | §6: leaving employment, historical policy/schedule changes and spent deficits preserve original decisions, recalculate from corrected history and flag affected requests. | E2/E3 effective changes include applicable history/review rules; E6 corrective workflows. E5 blocks leave dates beyond known employment end and verifies all actual request-impact protections. No automatic paid-to-unpaid rewrite of approved leave. |
| BIZ-14 | §7, UX flow 1: exact unfinished input with one draft, autosave, close/reopen and retained history across rehire, distinct from eligibility or submission. | E1 D1/D2-A/B/D3/D4/D5 and current contracts. Keep approved direct-save/draft conventions; no E2/E3 dependency merely to preserve input. |
| BIZ-15 | §7/8: duration-only Full days/Half day/Hours, effective schedule, exact half-day and half-hour input increments distinct from ledger minute precision. | E1 collects permitted-mode input; E3 computes minutes and explanations; E5 validates submitted durations and overlap. No exact-time or arbitrary-fraction interface. |
| BIZ-16 | §7/10, UX flow 1: submit summary/allocation, exact employee unpaid acknowledgement, current policy/employment/overlap/documents/route checks, reservation and atomic draft closure. | E5 depends on E3 calculations and E4 required attachments; preserves idempotence/audit/outbox. No missing-route fallback approval or draft-save eligibility claim. |
| BIZ-17 | §7/10, UX flow 4a: on-behalf submission needs separate scoped capability and reason; actor differs from employee, does not replace employee draft or automatically gain approval authority. | E5; accountless employment does not bypass employee-only unpaid response. Confirmation/automatic-step satisfaction follow the accepted authorization rules. |
| BIZ-18 | §9, UX flow 3a: separate balance-override decision and reason, authorized funding lines, visible proposed paid/unpaid consequences, required renewed acknowledgement. | E3 preview/allocation types; E5 authorized override plus ordinary approval independent. Cross-type funds are never silently borrowed. |
| BIZ-19 | §10, UX flows 3/8: one/two-step routes, explicit eligible final approver, supervisor setup, self-approval and conditional automatic decision rules. | E2 relationship/access setup; E3 policy configuration; E5 route snapshots and execution. No zero-step preset or assumed CEO. |
| BIZ-20 | §10: optional directional absence fallback—final approver may cover absent supervisor when enabled, never reverse; at least one valid approval. | E3 configuration, E5 execution/evidence. Recorded absence is distinct from slow response; omitted step is explained, not silently approved. |
| BIZ-21 | §10, UX flow 7: temporary approver scope/dates, selected pending-work transfer, acting-for display, no permanent role prerequisite, expiry/early termination and unresolved cover. | E2 supplies underlying identities/access facts; E5 owns appointment lifecycle, authorization, due processing and notifications. No silent authority extension or automatic approved-leave cancellation. |
| BIZ-22 | §10/15/16, UX flow 3: actionable longest-waiting queue, scoped team availability, independent final coverage/unpaid gates, rejection reason and safe stale-decision recovery. | E5 complete approval workspace and finalization; reminders/escalation and due-work mechanisms included, not postponed to E7/E8. |
| BIZ-23 | §11/state models: submission reserves; intermediate approval retains; final approval consumes once; rejection/withdrawal releases. | E5 atomic request/step/ledger/outbox transitions and replay/concurrency tests. Request state is not derived from one mutable approver field. |
| BIZ-24 | §11, UX flow 2: rejected request edited/resubmitted under the same request ID with history and a fresh approval cycle/reservation. | E5; old decisions do not approve the revised request. This is distinct from E6 approved cancellation/replacement and from E1 draft discard. |
| BIZ-25 | §11, UX flow 4: approved cancellation needs no new approval; replacement gets new linked ID and fresh validation/approval, with original preserved. | E6 employee and authorized on-behalf paths; E5 establishes the underlying immutable request/ledger invariants. Validate before atomic cancel-and-replace; rejection of a later replacement does not restore the original. |
| BIZ-26 | §6/17, UX flows 4/5: correction needs follow-up and deficit review; explicit outcomes/reasons, source correction or separate adjustment; review does not erase deficit. | E6; only applicable permissions authorize balance changes. Notify affected employee and preserve original approval evidence. No inferred payroll recovery. |
| BIZ-27 | §12, UX notes/uploads: permitted PDF/JPEG/PNG, 10 MB each/3 files/20 MB total, sniffing and verification, no required malware scan. | E4 full owned attachment/association lifecycle, retry/cleanup and private reads; retained domain permissions apply. Limits are sources, not a new selection. |
| BIZ-28 | §12: sensitive document metadata/read scope, no filename/preview without separate permission; configurable retention with two-year medical default after closure subject to organization review. | E4 authorized API and UI, owner disposal/evidence; E8 privacy/retention qualification. Assigned approval alone permits only provided/verification status. |
| BIZ-29 | §13, UX flow 14: email/in-app channels, authorized recipients, minimal name/date/status/link payloads, no type/note/comment/document leakage anywhere. | E3 first adjustment notification; E4 attachment notices; E5 request/appointment/reminder events. Shared delivery foundation must precede its first producer; later producers extend versioned contracts. |
| BIZ-30 | §13 and platform durable-event rules: atomic outbound intent, retry/deduplication, relevance, localized recipient fallback and observable delivery independent of domain success. | First E3 notification consumer proves shared foundation; E4/E5 extend events/due work; E8 validates release/recovery/alerts. Read notification state never satisfies business acknowledgement. |
| BIZ-31 | §14/UX, flows 1/2: current per-type balances and ledger explanation; own year calendar/list/history, employment/record-history bounds, preference per person/organization. | E3 balances; E5 own request history/calendar and lifecycle actions; E6 linked correction history. E1 only minimum My Leave draft entry, no fake balances/history. |
| BIZ-32 | §17/18, UX flows 5/6: manager attention plus independently reachable tools; scoped organization overview, sensitive absence privacy, partial days/nonworking dates/holidays and preserved filters/position. | E2 tools/setup, E5 escalation/coverage attention, E6 deficits/follow-up, E7 broader overview. Team availability needed to decide requests stays E5. |
| BIZ-33 | §19, UX flow 12: current/point-in-time balances, accrual/adjustment history, leave used by employee/type/team/period, upcoming absence, approval aging and override/adjustment reports. | E7; each report needs explicit query/date/privacy examples and all-matching CSV scope/audit. No inference that a paginated screen's visible rows are the entire export. |
| BIZ-34 | §20, UX flow 13: immutable consequential attribution and permitted before/after/reason/delegated context; searchable audit with authorized linked detail. | Every first writer supplies required evidence; E7 supplies audit UI/reporting. E1 ordinary draft read/autosave exceptions remain unchanged. Sensitive reads/exports are not exempted. |
| BIZ-35 | MVP exclusions/import scope, UX flow 15: consultant validation, preview/row errors, duplicate protection, exact batch reconciliation and client email approval before apply. | E8 runbook/tooling through supported owner contracts, cutover/recovery and renewed approval for changed data. No self-service upload/approval screen; E2 ordinary manual setup remains available. |
| BIZ-36 | MVP acceptance: representative roles can apply/decide/report privately, scoped imports reconcile, operational/browser/accessibility evidence passes before pilot. | E8 assembles evidence from E1–E7 and executes release qualification; it does not defer earlier security/correctness work. No integrations, generic workflow builder, AI repair tooling or Portuguese translation delivery silently added. |

### Cross-epic dependency checks

1. **E3 first notifications:** adjustment/entitlement notices require shared delivery,
   local outbox, privacy and retry contracts before that producer is complete. Introduce
   only the workers needed by the consumer; on-demand accrual itself requires none.
2. **E2/E3 writers before E5:** initial configuration stories work with no submitted
   requests. E5 must integrate their protected impact/revalidation contracts against
   real requests before request writes go live. Calling this E6 correction work cannot
   waive the safeguards on ordinary configuration changes.
3. **E4 before consequential required-document validation:** preserve platform ADR-0038
   fixed-byte provider proof, association/cleanup and signed-lifetime feasibility before
   attachment readiness. E5 consumes verified domain attachment status, not upload success.
4. **E5 versus E6:** rejection/resubmission keeps the same ID in E5; approved cancellation
   and linked replacement belongs to E6. Historical decisions remain immutable in both.
5. **Operational assembly:** producers own events/audit/privacy and worker correctness;
   E8 joins their evidence into actual release/restore qualification. It is not where
   first-time per-feature tests are postponed.

The generic §11 illustration includes Draft → Withdrawn, while the later explicit §7
and accepted E1 contracts define confirmed Discard draft with cleared input and retained
closed-row evidence. For E1 use the latter; E5 withdrawal concerns submitted/in-approval
requests. Do not generate a second draft-withdrawal command or interpret the overview
illustration as permission to bypass discard protection. No accepted ADR is changed.

All numbered UX key flows 1–16, including 3a/4a/15a, now have owner references in this
pass. Detailed UI state/field and §6 arithmetic examples still need complete extraction;
this is bounded business/journey assignment, not all-story readiness or final inventory.


## Entitlement rule and acceptance-example ledger — 2026-10-05

Source: [features §6](../../apps/leave/docs/features.md#6-balance-ledger-and-accrual),
[§5 overrides](../../apps/leave/docs/features.md#5-employee-entitlement-overrides),
[§8 duration](../../apps/leave/docs/features.md#8-hourly-and-half-day-leave),
[§9 override](../../apps/leave/docs/features.md#9-insufficient-balance-override) and their
accepted Leave ADRs. CALC references map existing rules/examples to future acceptance;
they are not a new calculation specification or implemented tests. ADR numbers below
are Leave numbers unless explicitly prefixed Platform. E3 owns calculation, E5 consumes
it in protected request commands, and E6 owns corrective workflows. E1 only preserves input.

| ID | Rule / authoritative ADR | Required example or boundary evidence | Owner |
| --- | --- | --- | --- |
| CALC-01 | 0090/0106: daily, annual upfront, monthly instalments or manual-only; automatic entitlement is on-demand, not worker-posted. | Repeated reads yield identical earning with no new event/snapshot; manual-only earns zero without an authorized grant; never count derived and posted earning twice. | E3 |
| CALC-02 | 0041/0042: standard-day conversion is distinct from scheduled leave-day hours; calendar versus anniversary period is distinct from earning frequency. | Eight-hour standard day and six-hour Friday: five-day carry-over cap converts to 40 hours, Friday full/half leave consumes 6/3 hours. 1 July anniversary ends 30 June. | E2 inputs; E3 calculation |
| CALC-03 | 0044: leap-day anniversary resolves 28 February in non-leap years and returns to 29 February. | 29 February 2024 start yields 28 February 2025 boundary; 2027 period ends 28 February 2028 before next start on 29 February. Preserve original anchor. | E3 |
| CALC-04 | 0091/0092/0094: daily earning starts at the day's beginning, inclusive employment dates, actual full leave-year denominator, no double proration. | 8,640 annual minutes × 100/365 yields 2,367 usable minutes; full year 8,640. One-date employment earns one eligible day; test 366-day years and dates outside employment. | E3 |
| CALC-05 | 0093/0095: chronological daily cap, precise cap before whole-minute usability rounding; no catch-up. | At cap Monday, a later Monday deduction allows Tuesday's normal earning only. Cap 120, accumulated 119.8, new 0.5: accept 0.2, exclude 0.3. | E3 |
| CALC-06 | 0096: daily rate changes prospective by date, retaining exact portions and full-year denominators. | Rate 18 to 24 effective 1 July in a 365-day year: 18×181/365 + 24×184/365 before applicable conversion/rounding; no segment-length denominator or rewrite of earlier earning. | E3 |
| CALC-07 | 0098: changing availability method waits for each employee's next leave-period start. | Daily/monthly/upfront transition leaves current period intact; anniversary employees may have different dates shown in preview. Not a ban on CALC-06 rate changes. | E3 |
| CALC-08 | 0043/0102: upfront grant at period start or prorated joining date; annual amount changes next period. | Calendar grant 1 January, midperiod start 1 July receives joining grant; 18→24 preserves current 18-day grant. Immediate increase requires separate adjustment. | E3 |
| CALC-09 | 0025/0103/0104: policy chooses partial-period proration or full eligible allowance; new monthly policies default to adjustment for time employed. | 480×15/30 = 240 versus full 480; standalone upfront 481×15/30 = 240.5 floors once to 240. Manual-only amount is explicit; daily mode hides partial-period selector. | E3 |
| CALC-10 | 0099/0100: twelve monthly instalment periods align to original leave-year anchor without iterative clamp drift. | 15 July–14 August; 31 January boundaries clamp February then return to 31 March and 30 April. Each ends before next boundary; cover full year without gaps/overlap. | E3 |
| CALC-11 | 0045/0046/0047: start/end instalment timing and midperiod joining; grant usable from beginning of its effective date. | Start 16 April, 480 monthly ×15/30 gives 240 on 16 April or 30 April according to policy. End-April grant funds 30 April, never 29 April; no duplicate April portion. | E3 |
| CALC-12 | 0097: complete unchanged monthly nominal portions are differences of cumulative floored entitlement, independent of actual remaining balance. | 8,550 annual minutes gives 712 then 713, totaling 8,550 after twelve portions. Consumption or cap exclusions cannot enlarge a later nominal instalment. | E3 |
| CALC-13 | 0105 supersedes partial-portion rounding in 0097: retain related monthly fractions across partial employment and rate changes. | Exact 712.5 + 952.5 yields 712 then cumulative 1,665 (increment 953); 240.5 + 481 gives usable 721 with 0.5 retained in precise calculation. No authorized cross-year fractional transfer follows. | E3 |
| CALC-14 | 0101: monthly rate changes next instalment; rate start differs from first availability; notify effective changes and amendments/cancellations. | Mid 15 July–14 August change starts 15 August; end-period availability is 14 September. Continuing override without changed employee amount must not cause misleading entitlement-change notice. | E3 plus notification foundation |
| CALC-15 | 0083: recurring employee override persists until explicitly changed at a leave-period boundary. | Default next period, not necessarily 1 January or next monthly instalment; no current-balance reset or automatic override end. Return to policy through same reviewed action. | E3 |
| CALC-16 | 0033/0034/0037: accumulated cap differs from carry-over cap; earned reservations count, future reservations do not; resume next scheduled date only. | Cap 2,400/current 2,280/new 240 admits 120. Earned 2,400 with 600 reserved still capped; approval consumes to 1,800, withdrawal leaves 2,400. No catch-up of excluded amounts. | E3; E5 transactions |
| CALC-17 | 0028/0040: no/all/limited carry-over and schedule-based conversion at rollover. | 600 eligible minutes transfers 0/600/480 per policy; five-day limit at 8/6 hours converts to 2,400/1,800. Preserve conversion context; later schedules do not rewrite it. | E3 |
| CALC-18 | 0085/0089: period-relative inclusive expiry uses calendar months once; do not extend an earlier expiry. | One month from 15 January 2026 ends 14 February; from 31 January ends 28 February (29 in 2028); twelve from 29 February 2028 ends 28 February 2029. | E3 |
| CALC-19 | 0029/0030: once-only/repeated carry-over preserves validity and caps; nontransferred unused entitlement expires with explanation. | Earlier 120-minute carried portion cannot transfer again under once-only; repeated never resets expiry. Of 600 with cap 480, explain 480 carried/120 expired; no payout or cross-type transfer. | E3 |
| CALC-20 | 0021/0022/0023/0109: leave-date validity in employee work timezone; expiry/rollover before new earning. | 31 January expiry cannot fund 1 February even for viewer still in January. Effective 1 February earning cannot fund 31 January. At cap 20, 2 expiring 31 March leave headroom before 1 April earning. | E3 |
| CALC-21 | 0019/0020: every requested date affordable in order, earliest eligible expiry first, no expired/future/already-reserved funds. | 240 now plus 240 between workdays funds 240 each, not 480 first day. Expiry between dates can create second-day shortfall. Allocate 300 as 120 earliest +180 next. Same-expiry tie rule remains design gate. | E3 projection; E5 reservation |
| CALC-22 | 0035/0036: projected leave-date funding and independent configurable advance horizon, default twelve months for every date. | Submission 14 September 2026 permits through 14 September 2027, not 15 September; an in-window start cannot excuse out-of-window end. Year-3 funding cannot use expired year-1 entitlement. | E3 preview; E5 validation |
| CALC-23 | 0031/0032: reservations never extend expiry; new requests cannot displace existing valid reservations. | Existing 240 of 480 remains protected; new earlier 360 gets only 240 funded and 120 shortfall. Rollover shortfall retains pending status with exact paid/unpaid warning, not automatic cancellation. | E3 funding/impact; E5 request state |
| CALC-24 | 0032: authorized change increasing pending unpaid amount needs actor/reason and renewed exact-amount employee acknowledgement before final approval. | Funding 480→360 creates 120 unpaid; prior decisions remain, final approval blocked until acknowledgement. Same/decreased unpaid needs no renewed acknowledgement; acknowledgement is not approval. | E5, with E2/E3 writers integrated; E6 consumers |
| CALC-25 | §9: explicit multi-source exceptional allocation is separate from ordinary approval and recurring entitlement. | Show deficit/default unpaid; authorized lines identify source, duration, actor/reason. No silent use of another leave type or implicit paid grant. | E3 data/preview; E5 decision |
| CALC-26 | 0048/0049: end-date correction uses policy proration and preserves explained history; requests cannot include dates after known end. | 480 April upfront with last date 15 April becomes 240 under proration, stays 480 under no-proration. 30 June end permits 30 June, blocks 1 July. Affected existing request is flagged, never silently date-edited. | E3 calculation; E2/E5 guards; E6 correction |
| CALC-27 | 0003/0074/0103: half-hour request increment is not earning precision; half day is exactly half the scheduled date. | 137 available can fund 120 leaving 17; a 450-minute day has 225-minute half day. Inactive draft modes preserved; no exact times or arbitrary fractions required. | E3 duration; E5 validation; E1 input only |
| CALC-28 | 0074/0052: same-date warning, but active total may not exceed scheduled time across types. | Eight-hour day with two 2-hour requests totals four and is allowed with warning; full day plus positive time blocked. Count submitted/in-approval/approved only; concurrent submissions preserve limit. | E3 preview; E5 atomic guard; E6 corrections |
| CALC-29 | 0050/0051: short-notice default zero versus backdating with mandatory reason and no fixed cutoff. | Seven-day notice/three-day lead requires explanation; zero does not waive backdating. 10 September submitted 15 September uses historical date rules; fourteen days late not rejected solely for age. | E3 policy/preview; E5 submission |
| CALC-30 | State model: intermediate approval retains reservation; final consumes once; reject/withdraw releases. | Two-step 480-minute request remains entirely reserved after first approval, then consumed once at final approval. Retry/resubmission cannot duplicate effects. | E5 |
| CALC-31 | 0038/0039: cancel approved consumption with counterfactual capped-earning correction, preserving other actual events and original expiry. | At cap 20: approve 5, earn 2, take other 4 →13; cancel restores 5 and reverses 2 →16. Show effects before confirmation; retries duplicate neither part. Spent deficit needs authorized reasoned review, no automatic paid-to-unpaid change. | E6 using E3 replay/E5 ledger |
| CALC-32 | 0107/0111: historical correction shows corrected balance without rewriting original approval/snapshot evidence. | Compare original Balance at approval with recalculation; corrected historical balance is not substituted for today's balance. Snapshot captures actual values/immutable versions plus calculation version, only at consequential events. | E3 evidence; E5 decisions; E6 correction |
| CALC-33 | 0110: same-effective-date user changes use server sequence after automatic boundary effects. | Equal timestamps/client-clock differences cannot reorder results; retry retains original sequence; backdated change retains recorded time and impact rules. User history need not display internal sequence. | E3/E5/E6 writers |
| CALC-34 | 0112/0113: fresh confirmation inputs and bounded per-employee coordination; configuration writers participate. | Changed consequential amount/duration requires renewed confirmation, irrelevant change need not. Distinguish busy-before-effect from unknown commit; concurrent requests cannot consume same entitlement. Exact lock order/timeouts remain design inputs. | E2/E3/E5/E6 first affected writer |
| CALC-35 | 0108: direct indexed historical calculation first, no speculative cache/checkpoint or accrual worker. | Measure realistic multi-year history and workload before release; only measured need justifies checkpoints. If later introduced, invalidate affected descendants after correction and never confirm from stale checkpoints. | E3 performance; E8 qualification |
| CALC-36 | §6/UX: explain earned/used/reserved/current/projected/requested amounts without double counting; adjustment reason/actor and request links retained. | 9 earned −3 deducted −2 reserved =4 available; year filter changes history only, not today's balance. Explain shortfall in schedule-aware units without hiding canonical precision. | E3 balances; E5 request integration; E7 reports |

### Precedence and open representation decisions

- [ADR-0105](../../apps/leave/docs/architecture/decisions/0105-monthly-precision-across-partial-periods-and-rate-changes.md)
  explicitly supersedes ADR-0097's partial-month standalone rounding. CALC-13 follows
  cumulative precision; CALC-09 retains standalone upfront final rounding. Do not change
  immutable ADR-0097 text or treat its old paragraph as another configurable option.
- [ADR-0106](../../apps/leave/docs/architecture/decisions/0106-on-demand-accrual-with-decision-evidence.md)
  makes automatic earning authoritative without posting. Earlier source phrases such as
  scheduled grant/record expiry must be reconciled in the E3 physical event design with
  immutable actual changes and auditable explanations. Source explicitly leaves interval/
  bucket/ledger representation open. No daily worker, write-on-read or second entitlement
  total is selected here; auditable rollover/expiry explanations are not waived.
- Exact same-expiry allocation ties, precise bucket/fraction treatment through historical
  cap/expiry transitions, schema/event/snapshot representation, protected configuration
  version checks and relevant calculation workload remain pre-story contracts. Existing
  formulas alone do not close these. Raise an actual unresolved business outcome if found;
  choose routine implementation details within the already accepted behavior.
- Compound fixtures must combine partial monthly/rate changes with caps and expiry,
  boundary dates with reservations, and cancellation with subsequent real consumption.
  Pure arithmetic tests alone cannot prove authorization, serialization, immutable evidence
  or duplicate-safe writes. Pair deterministic calculation fixtures with real transaction
  tests in the owning delivery stories.

No new defaults, arithmetic policy or request scope were introduced. This ledger expands
BIZ-07–18/23/25–26 and preserves source examples; full workflow-state extraction and final
story decomposition remain pending. No application calculation tests were executed.


## Approval and request-state coverage — 2026-10-05

Sources: [features §7](../../apps/leave/docs/features.md#7-leave-application-experience),
[§10](../../apps/leave/docs/features.md#10-configurable-approval-workflows),
[§11](../../apps/leave/docs/features.md#11-request-lifecycle),
[state models](../../apps/leave/docs/features.md#state-models),
[UX approval review](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md#approval-review) and
[temporary assignment/escalation UX](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md#leave-manager-escalated-approvals).
FLOW identifiers trace existing obligations, not new workflow states or final stories.
ADR numbers here refer to Leave decisions. E5 owns request execution and required
appointment/due-work mechanisms; E2/E3 supply earlier configuration and E6 corrections.

| ID | Required behavior / source | Acceptance boundary | Owner |
| --- | --- | --- | --- |
| FLOW-01 | §10/0007: one/two-step presets with at least one required approval. | No zero-step policy; two steps default to supervisor then explicitly selected eligible final approver, never inferred CEO. Self-approval disabled by default. | E3 configuration; E5 resolution |
| FLOW-02 | §10: missing/invalid route blocks submission, preserving saved draft and directing to Leave Manager. | No unauthorized alternate or implicit skipped step. This is distinct from applicant coverage; saving incomplete draft itself remains allowed. | E5 with E1 preservation/E2 setup |
| FLOW-03 | §10: starter one-supervisor setup, temporary appointments available, 3-day reminder/7-day escalation, optional second step/fallback off. | Client confirms schedules/entitlement/calendars/rules before starter policy activation; no universal statutory allowance. | E2 setup; E3 policy |
| FLOW-04 | §10: submission snapshots the resolved route. | Later supervisor/directory/role changes do not silently rewrite outstanding assignees; explicit permissioned reroute preserves completed decisions. | E5; E2 writers participate |
| FLOW-05 | 0007/0008: valid submitting approver may satisfy only their own authorized step; on-behalf and self-approval are separate permissions. | Without explicit self-approval no automatic own-request approval. On-behalf authority alone satisfies no approval step; another person's step remains pending. | E5 |
| FLOW-06 | 0008: authorized later-step submission records that step immediately. | Step 2 approved with step 1 pending retains 480 reserved. Step 1 approval can finalize without repeating step 2; step 1 rejection releases reservation but retains the historical step-2 decision. | E5 |
| FLOW-07 | §10: configurable handling of consecutive identical approvers. | Do not ask for an identical decision twice; do not collapse distinct people/authority requirements arbitrarily. Exact supported collapse rule/configuration must be bound before story readiness. | E3 contract; E5 |
| FLOW-08 | 0069: own request with requested unpaid amount requires explicit acknowledgement of that exact current amount before submission. | Stale amount cannot satisfy current split; no acknowledgement needed for zero unpaid. Approval and override authority remain independent. | E5 with E3 allocation |
| FLOW-09 | 0088: authorized on-behalf unpaid submission precedes employee response and does not alter the employee's draft. | Only employee acknowledges; manager cannot impersonate response. Sole submitting approver's step may be approved while overall request/reservation remain pending. Finalize once after response and all checks, without repeat approval. | E5 |
| FLOW-10 | 0032/0088: explained increased unpaid amount invalidates stale acknowledgement. | Two→three unpaid days requires current three-day response; unchanged/decreased amount does not require renewed acknowledgement. Preserve actor/reason/previous amount, allow otherwise eligible withdrawal and intermediate steps. | E5; E2/E3/E6 impacts |
| FLOW-11 | 0078: applicant's missing responsibility cover permits submission but gates final approval. | Check entire absence and potential new work; employees with no approval responsibilities have no coverage gate. Every automatic-finalization path checks it too. | E5 |
| FLOW-12 | 0078: authorized coverage exception needs reason and leaves unresolved gap visible. | Exception does not create coverage, approval authority or satisfy unrelated gates. Do not change actual absence dates to conceal gap. Capability is part of Leave Manager default but custom role may omit it. | E2 capability model; E5 |
| FLOW-13 | 0078/0076: loss of arranged cover after approval preserves employee leave. | Show Replacement approver needed to authorized managers; no automatic cancellation, substitute selection or authority extension. Flag known absence without waiting seven days. | E5 |
| FLOW-14 | 0079: appointment grants bounded responsibility/date authority to an active same-organization member. | No permanent Approver role prerequisite; check known absence/self-conflict/membership. No medical-document permission, unrelated editing power or authority after expiry/inactive membership. | E5 consuming Access |
| FLOW-15 | §10: temporary assignments for identical responsibility/date cannot overlap; sequential ones allowed. | Show conflicting appointment; require adjusted dates or explicit authorized replacement; no arbitrary winner under concurrency. | E5 |
| FLOW-16 | 0076/0077: setup explicitly selects Include these pending approvals, with reason and disclosed conditional scheduled return. | Only selected outstanding work reroutes; completed approvals unchanged. Directory changes alone cannot transfer tasks. | E5 |
| FLOW-17 | 0077: at expiry, preauthorized return rechecks original approver eligibility/absence, records transfer and notifies. | Ineligible original leaves work pending/flagged; authority does not extend. Authorized pre-expiry extension postpones return; retries cannot duplicate transfer or overwrite later reroute. | E5 due-work/transaction contract |
| FLOW-18 | §10/UX: early termination ends authority on confirmation, with reason and destination preview. | May end without replacement: preserve decisions and pending flags, including coverage gap while no requests wait. Return only to eligible original or authorized replacement; preserve approved leave. | E5 |
| FLOW-19 | §10: temporary appointment/change/early termination notifies appointee; no appointee acceptance step. | Manager confirms availability beforehand; authority starts on configured date. Minimal original-approver/date/Approvals-link content without sensitive request details. | E5 notification producer |
| FLOW-20 | 0080/0081: optional directional absence fallback uses absence when approval is needed. | Eligible final approver may omit absent supervisor step; absent final approver cannot be replaced by supervisor alone. Do not use applicant's future dates or slow response as approver absence. | E3 policy; E5 execution |
| FLOW-21 | 0080/0081: both absent may use temporary final approver alone only with explicitly granted supervisor-absence responsibility. | Fallback can satisfy that supervisor-responsibility coverage without duplicate substitute; other responsibilities still need cover/exception. Label omitted step Not required under absence policy; require at least one valid approval. | E5 |
| FLOW-22 | 0081: request may wait for supervisor return without pausing reminders/escalation. | Before final decision, return restores outstanding supervisor step with evidence; completed valid final decision remains valid. Temporary appointments keep their separate expiry-return rule. | E5 |
| FLOW-23 | §10/0057/0058: only currently required unanswered approvals get reminders/escalation. | Default 3/7 calendar days configurable; stop acted/withdrawn/cancelled work. Escalation notifies eligible manager but does not reroute, approve, reject or grant authority. Exact timer anchor/restart/due-work semantics remain design inputs. | E5 |
| FLOW-24 | §10/15/16: actionable queue, review context and rejection reason. | Approver sees scoped type/note, balance/history/flags/team availability; document rights separate. Required rejection reason, comments preserved on stale review; email opens authenticated UI and never decides anonymously. | E5; E4 document boundary |
| FLOW-25 | State model/§11: intermediate decisions retain reservation; final consumes once; reject/withdraw releases. | Overall request is not derived from a single step state. Concurrent finalizers/acknowledgement/config change cannot double-consume or bypass applicable gates. | E5 |
| FLOW-26 | 0009: rejected request resubmits same ID, preserving previous detail/reason/decisions and starting fresh cycle. | 480 rejected releases old reservation; revised 240 reserves once; old decisions do not approve revision. Authorized automatic outcomes are freshly evaluated. | E5 |
| FLOW-27 | 0010/0052–0054: approved cancellation/replacement distinct from rejected resubmission. | Cancel reverses applicable effects once; linked replacement new ID/new approval. On-behalf correction needs scoped capability/reason; invalid replacement leaves original intact, later replacement rejection leaves original cancelled with follow-up. | E6 |
| FLOW-28 | 0087/0071: confirmed submission returns to My Leave with context and authoritative status. | Brief Request submitted, optional View request, no prominent reference/next-approver name. Lost response resolves existing operation before retry; no second request/reservation; remove submitted-draft indicator. | E5 |

### Finalization scenario matrix

This matrix distinguishes approval-step evidence from the request's overall lifecycle.
It introduces no new waiting status: use accepted request/step states with explanatory
UI messages. Each row also requires current authorization, valid funding/documents/
employment, fresh reviewed inputs and duplicate-safe local effects.

| Scenario | Permitted result |
| --- | --- |
| All required decisions satisfied; coverage valid or authorized exception; required employee acknowledgement current | Finalize once and convert reserved allocation to consumption. |
| Submitting second approver authorized; earlier distinct approver still pending | Record second approval; overall request stays in approval with reservation. |
| Sole on-behalf submitting approver valid; employee unpaid response missing | Step approved; overall request remains pending, no consumption. Employee response may trigger finalization once remaining checks pass. |
| Decisions satisfied and acknowledgement current, but applicant coverage missing with no authorized exception | Do not finalize, including automatic paths; show unresolved coverage. |
| Missing approval route before submission | Do not submit; preserve draft. This is not the same as a coverage gap. |
| Later-step approval already recorded; earlier required approver rejects | Reject/release once and retain historical later-step decision; no consumption. |
| Coverage later disappears after valid request approval | Keep request approved; flag replacement needed and arrange authorized coverage. |
| Supervisor returns before final-approver absence fallback decides | Restore outstanding supervisor step under recorded policy; continue normal required-step checks. |

### Remaining concrete design gates

- Bind current effective appointment authority to the Access/Leave boundary without
  granting permanent roles or sensitive-document rights. E1 Access checks alone do
  not prove temporary E5 authority; extend contracts with the first consumer.
- Specify responsibility identity, interval uniqueness, availability evidence and
  explicit transfer/extension/termination command versions, locks and outcome shapes.
  Recheck at execution; old timers/commands must not overwrite newer assignment state.
- Define due-work identities, timezones, timer anchors and restart rules for reminder,
  escalation and scheduled return, with fresh authorization and version compatibility.
  Preserve privacy/outbox/worker recovery; generic notification retry is not a scheduler.
- Specify all entry points that can complete finalization, including employee response,
  final outstanding approval and resolution of a coverage gate after decisions already
  exist. Sources require the same checks/one consumption; they do not yet establish all
  exact command triggers. Do not infer background auto-finalization for unspecified paths.
- Complete scoped withdrawal/visibility/error-state examples with their owning stories;
  source says eligible pending withdrawal remains available, not an unrestricted API.

Precedence: 0078 qualifies automatic finalization in 0007/0008; 0088 qualifies 0069's
on-behalf acknowledgement timing; 0077/0079 refine 0076 temporary authority/return;
0081 refines 0080 timing and return. Accepted originals remain immutable. No new
product decision, workflow engine, runtime implementation or readiness pass here.


## Privacy, notification and screen-state coverage — 2026-10-05

Sources: [features](../../apps/leave/docs/features.md) §6 notification read/count rules,
§12–13, §18–20; [Leave EXPERIENCE](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md)
Notification inbox, Organization leave overview, Reports, Leave Manager audit history
and State Patterns; [platform EXPERIENCE](../../platform/EXPERIENCE.md) Notification
panel, Collection views and filters, and Collections, refresh and export. These
PRIV identifiers expand BIZ/FLOW/E1-X coverage without replacing authoritative sources
or creating additional stories. Later-epic ownership is not completed story decomposition.

| ID | Source obligation | Required acceptance evidence | First owner / consumers |
| --- | --- | --- | --- |
| PRIV-01 | §18: colleague absence privacy covers every leave type. | Annual and sick leave both show Unavailable or Part-day absence; authorized employee/interval only. API, export, filters, colours, icons, grouping and tooltips cannot expose type, note, comments or attachment metadata. | E5 team availability; E7 overview/export |
| PRIV-02 | §18: assigned approver and manager can see scoped type/note/history. | Authorized sensitive type/note is visible; unrelated request and other organization are denied. Medical-document authority remains separate. | E5 review; E7 manager views |
| PRIV-03 | §18: own request history includes decisions, named approvers, times and full comments. | Employee and assigned approver see permitted history; no private approver-only comment field. Colleagues and notifications do not receive it. | E5 history; E6 correction |
| PRIV-04 | §12: medical-document permission controls metadata as well as bytes. | Approver/manager without permission gets only provided/verification status, with safe status text; direct API metadata/preview/read attempts expose no filename or URL. Permission alone cannot bypass resource scope/safety; own permitted document access works. | E4 Content/Leave contract; E5 review |
| PRIV-05 | §13: email and in-app request information is limited to employee name, dates, status and secure link. | Assert allowed fields in API, subject, body, banner, preview, link text/parameters; exclude all types, notes, comments and document details. “Rejection with reason” event does not put the reason into notification content; read it in the authorized request. | E3 notification foundation; E4/E5/E6 producers |
| PRIV-06 | §13: delivery/link possession grants no authority. | Current recipient/resource scope controls exposure; old link rechecks sign-in, membership and request access. Wrong organization or revoked access yields no request/document details. | E3 foundation; E5 request links |
| PRIV-07 | §6: active-organization inbox and explicitly limited cross-organization counts. | A:2/B:3 shows active A bell/inbox only; selector counts only for active memberships, no B previews. Retiring B membership removes its count/access. | E3 shared notification integration |
| PRIV-08 | §6: per-user read state is independent of business action. | Opening one A item reduces A count; Mark all as read clears only that user's A items, not B or another user. Neither approves a request nor satisfies unpaid acknowledgement. Required-action indicator remains until business response. | E3 read-state contract; E5 acknowledgement |
| PRIV-09 | Shared/Leave notification panel UX. | Newest first, unread marker/time, desktop panel/mobile sheet with focus/return behavior. Failed load is not No notifications yet; retry respects active organization. | E3 shared shell/UI |
| PRIV-10 | My Leave sections load/retry independently where contracts allow. | Failed balances show Retry, never zero balance; successful requests/history remain usable with context. Apply remains available; its own failed calculation blocks submission but not input preservation. Dashboard failure alone does not block successful form checks. | E1 shell/draft; E3 balances; E5 history/submission |
| PRIV-11 | Shared collection empty, filtered-empty, loading and failure are distinct. | Preserve filters on retry; Clear filters for no matches. Failed refresh labels retained authorized data stale; lost access suppresses it; actions revalidate current state. | E1 applicable surfaces; E2–E7 collections |
| PRIV-12 | Approval review supporting data failure does not imply availability. | Team availability failure says unavailable with retry; do not infer nobody away. Informational capacity does not block approval, while required coverage/funding/authorization checks still do. | E5 |
| PRIV-13 | Stale review preserves input without executing it. | Withdrawn request loses Approve/Reject and offers Back to approvals; retained comment can be copied while open, without survival promise. Changed request requires latest review; lost access reveals no refreshed details. | E5; E6 applicable review |
| PRIV-14 | Shared mobile filters are provisional until Apply. | Dismiss/Back discards unapplied changes; Reset changes provisional defaults only. Badge counts applied nondefault groups, not options/results; accessible focus and reachable controls. | First applicable E2/E3 collection; E5/E7 consumers |
| PRIV-15 | Overview query/default/context rules. | Current month, approved and awaiting approval, employees with leave by default; explicit Show all employees stays within permission/filters. Search does not enable it. Persist per-user/per-organization filters; clear invalid/disallowed choices with safe notice. | E7 |
| PRIV-16 | Overview navigation and permitted details. | Desktop timeline/mobile list, preserved filters/date/position on detail close and targeted refresh; no drag/resize date edits. Authorized change uses correction workflow. Empty period never claims Everyone is available. | E7 consuming E6 |
| PRIV-17 | Timeline conveys dates separately from deducted duration. | Continuous date span and continuation markers; partial requests individually selectable without invented morning/hour placement. Friday–Monday example shows calendar span distinct from working-day deduction. Non-working shading uses individual schedule, not assumed weekends. | E7 consuming E2/E3 |
| PRIV-18 | Holiday context respects location and schedule. | Multi-location holiday does not shade all employees as off; accessible date details and permitted holiday context. Existing resource/privacy restrictions still apply. | E7 consuming E2 |
| PRIV-19 | Reports/export use matching authorized query and transformations. | All six MVP report definitions retain date/filter/scope rules in CSV; failed export keeps report with Retry export. No privacy bypass through export. | E7 |
| PRIV-20 | Audit UI is a protected data surface. | Search/list/detail/linked records expose permitted before/after and actor/reason only; audit access is not medical-document permission. Producers capture required evidence at their owning write, before E7 UI exists. | E2 onward producers; E7 audit UI |
| PRIV-21 | Shared admin saving and request autosave remain distinct. | Whole-form Save/Cancel and existing Review/Confirm where specified; uncertain outcome checked before retry, stale review refreshed. No extra admin draft system or direct autosave fields inside explicit-Save forms. | E1 D2-B/D3; E2/E3/E5/E6 admin consumers |
| PRIV-22 | Disconnected/request draft states follow current adopted decisions. | Input retained in open form, saved indicator only after acknowledgement; inline Retry and exit-only Stay / Close anyway (Switch anyway for organization switch). Submission/approval never silently queued. | E1 D2-B/D3/D5; E5 actions |

### Delivery checks and remaining contracts

- Pair browser checks with API assertions for PRIV-01–08/19–20; hiding DOM fields
  cannot prove disclosure control. Include allowed and denied roles, separate document
  permission, wrong organization and revoked access. Real-browser/accessibility
  qualification remains required under the accepted browser policy.
- E3 owns the first notification integration because adjustment/entitlement producers
  precede request submission. Bind shared envelope, recipient authorization, read/count
  operations and deduplication/retention contracts before those stories are ready.
  Request-specific payload limits do not invent dates for non-request events; use
  their existing approved minimal event content. Reading remains a separate operation
  from any acknowledgement, approval or correction command.
- For partial loading, bind actual endpoint dependencies and current-access treatment;
  this is not permission to keep sensitive cached data after revocation or to bypass a
  required calculation/coverage check. Avoid adding an unrelated dashboard dependency
  to the first draft slice.
- E4 still requires the provider binding protocol and race/replay evidence in
  [platform ADR-0038](../../platform/docs/architecture/decisions/0038-finalized-content-byte-identity.md)
  before affected attachment story readiness. Metadata privacy tests do not prove
  finalized-byte identity, safe association or signed-operation lifetime.
- Impact: reuse/prove domain-neutral loading, filter, notification and saving controls
  at the first real consumer, then update shared UI and scaffold examples in that
  delivery item. Leave owns domain disclosure projections, query rules and messages.
  No new runtime service, agent-context rule, product default or ADR is introduced;
  this matrix and the authoritative tracker are the documentation impact. Accepted
  platform 0050/0051 and Leave 0123/0124 govern current saving presentation.

This pass assigns existing privacy/notification/state requirements; it is not a
runtime test result or a claim that the complete inventory/readiness gates passed.
Next: inspect P1/ACCESS/PEOPLE story size and dependency boundaries, then close the
remaining explicit technical-contract inputs before final E1 numbering.


## Remaining E1 foundation sizing — 2026-10-05

**Approved decomposition on 2026-10-05; the 21-item sequence below now applies.**
The following assessment records the rationale. No additional product capability is proposed.
Existing E1-P1/ACCESS/PEOPLE criteria and traceability remain binding.

### Repository evidence and recommendation

| Candidate | Working-tree evidence / existing boundary | Recommendation |
| --- | --- | --- |
| E1-P1 | [Builder README](../../platform/builder-cli/README.md) is explicitly a placeholder; templates exist but are not a working CLI or generation-test suite. P1 already excludes protected business routes, feature generation, retrofit tooling and the service-only variant. | Keep one story: minimum deterministic generator plus runnable web/API output and generation-safety checks. One declared app configuration, no option matrix. ENV settles the supported toolchain first. |
| E1-SERVICE | Existing service-only candidate reuses P1 core; includes owner configuration/migration hooks and preservation of custom extensions, not a table-to-public-API engine. | Keep the separate existing variant story. Do not fold it into P1 or add worker scaffolding before a consumer. |
| E1-ACCESS | [Current handler](../../services/access/main.py) has one v1 check, three PtS permissions and two accepted service keys; [migration](../../services/access/migrations/versions/0001_initial.py) owns one grants table. [Container](../../services/access/deployment/Dockerfile) still installs PtS requirements. Planned registry, bound grants, operator writes, v2 checks and v1 adoption are substantial independent changes. | Split into ACCESS-A controlled admission configuration, then ACCESS-B current checks and compatible activation. Preserve all original acceptance obligations. |
| E1-PEOPLE | No services/people implementation exists. Existing scope is two core entities, two controlled setup commands and one own-employment read with optional business-date interpretation. SERVICE and ID-B provide prior foundations. | Keep one end-to-end owner story: provision relationship/periods and prove authorized own-read. Do not split two tables away from their first useful consumer or introduce directory/HR administration. |

These are scope-based planning judgments, not measured implementation-time estimates.
Outstanding contracts must be resolved before declaring any item agent-sized and ready.

### Proposed ACCESS-A — Controlled app and grant configuration

Depends on ENV and ID-B, reusing the already established owner-command/evidence
contract. Delivers the existing Access-owned registry, permission mapping, organization
app enablement and exact membership-bound grants through restricted operator commands.
No new public administration API or role editor.

Independent acceptance boundary:

- In a disposable environment, register explicit PtS/reference/Leave capabilities;
  configure organization enablement; assign/revoke/regrant against exact current
  membership IDs. App registration starts disabled and employment creates no grant.
- Verify wrong owner/command/scope, stale revision, retired membership and conflicting
  registration rejection; replay succeeds once with atomic minimal audit/outcome.
  Concurrent updates and actual restricted database roles exercise the owning constraints.
- Rehearse the selected legacy grant/actor mapping, supported old-writer compatibility
  and migration failure/recovery. Expand-only schema changes must remain compatible
  with the prior running version; defer incompatible enforcement to the coordinated
  transition or use the existing explicit maintenance/recovery path.
- Separate Access's package/container dependencies from PtS while preserving the
  characterized current v1 behavior. Reuse rather than rebuild ID-B's common operator
  adapter; Access supplies only its command authority and owner-local operations.

**Activation boundary:** this proves configuration and mutation integrity, not effective
new admission enforcement. Do not publish the new enable/disable controls as operational
access controls, enable new consumers, or claim suspension effective while old checks
ignore them. New operator commands are exercised in isolation; production activation
of the admission feature waits for ACCESS-B's compatibility proof. This is a normal
coordinated feature release, not a future dependency in ACCESS-A's acceptance tests.
Do not activate stricter constraints that would break a supported existing writer.

### Proposed ACCESS-B — Current checks and compatible admission activation

Depends on ACCESS-A. Delivers complete v2 caller/user/capability authorization and the
compatible v1 transition using one current admission evaluation. No discovery endpoint
or launcher implementation; those retain their existing following stories.

Independent acceptance boundary:

- Verify registered app, global/org enablement, current account/membership and exact
  nonrevoked membership-bound capability; v2 supplies verified person/actor context.
  Test separate read/manage grants, rejoin without old grant restoration and re-enable
  restoring only still-valid access.
- Apply explicit service-to-app/endpoint policy; valid user credentials cannot let an
  unrelated calling service request decisions. Preserve safe disclosure order and
  typed expired/denied/setup/unavailable outcomes without positive-cache fallback.
- Exercise v1 and v2 with current revocation/suspension and retained v1 wire semantics;
  the old endpoint cannot bypass app admission. Characterization protects intended
  existing PtS behavior, not historical lack of admission enforcement.
- Rehearse coordinated migration/configuration/activation and supported callers with
  synthetic identities. Keep failure-blocked activation and declared recovery evidence;
  no live three-user transition or credential provisioning occurs during planning.

### Dependency, traceability and impact reconciliation if accepted

Replace the single ACCESS position with ACCESS-A → ACCESS-B. DISCOVERY and WRITE
consume completed ACCESS-B; PEOPLE consumes SERVICE, ID-B and ACCESS-B. Existing
DISCOVERY → LAUNCHER → WRITE → REF ordering and subsequent Leave sequence stay as
approved. This would make **21 delivery items**, retaining ACCESS as the parent
requirement grouping rather than an additional implementation item.

ACCESS-A owns the original configuration/provisioning/concurrency/migration obligations;
ACCESS-B owns direct authorization, caller policy, disclosure, revocation and v1/v2
compatibility. Both retain E1-ENTRY-02/05/06/07/10/12 and E1-AC-13/15/17/18 as applicable;
final acceptance-map rows must distinguish evidence rather than claim duplicate coverage.

P1 must not depend on future authentication to prove shell generation; SERVICE must not
expose permissive placeholder business routes; PEOPLE tests own-employment via real
Access using explicit fixtures and dates without a future Leave work-profile service.
Leave derives its date later. Nullable assignments remain nonblocking and their E2
maintenance/history scope is unchanged. First delivery remains sign in → select
organization → create/resume → autosave → close → reopen.

Scaffold impact: P1/SERVICE own generator output; Access updates its typed client/error
and command fixtures; People promotes only an opt-in employment adapter with proven
contracts. Shared UI has no additional feature in this sizing pass. Existing generated
agent guidance and ownership rules suffice. Documentation changes here and in the
tracker record the recommendation; accepted ADRs and product requirements are unchanged.

Remaining gates: exact generator inputs/pins/commands, owner operator authority adapter
and typed command bounds, schema/legacy-writer transition and permission/caller mappings
remain binding. In particular, a missing common operator adapter belongs to ID-B's
readiness/delivery scope, not a hidden new framework inside both Access and People.
No code, migration, runtime test or readiness completion is implied.


## Access split agreement and current E1 sequence — 2026-10-05

The user approved ACCESS-A → ACCESS-B, retaining P1/SERVICE/PEOPLE at their bounded
existing scopes. This supersedes the earlier twenty-item delivery sequence, not its
requirements. Parent ACCESS remains a traceability grouping. Detailed child criteria
are discussed in sequence; decomposition approval is not implementation readiness.

| Order | Candidate |
| --- | --- |
| 1 | E1-ENV |
| 2 | E1-P1 |
| 3 | E1-SERVICE |
| 4 | E1-ID-A |
| 5 | E1-ID-B |
| 6 | E1-ACCESS-A |
| 7 | E1-ACCESS-B |
| 8 | E1-DISCOVERY |
| 9 | E1-LAUNCHER |
| 10 | E1-WRITE |
| 11 | E1-REF |
| 12 | E1-PEOPLE |
| 13 | E1-A1 |
| 14 | E1-CONTEXT |
| 15 | E1-CHOICES |
| 16 | E1-D1 |
| 17 | E1-D2-A |
| 18 | E1-D2-B |
| 19 | E1-D3 |
| 20 | E1-D4 |
| 21 | E1-D5 |

ACCESS-A follows ID-B and ENV; ACCESS-B follows ACCESS-A. References from DISCOVERY,
WRITE, PEOPLE and Leave consumers to completed ACCESS mean completed ACCESS-B, not
just new configuration tables. SERVICE remains a prerequisite for generating People.
All other dependency and first-slice boundaries remain unchanged.

### Candidate Story E1-ACCESS-A: Configure application admission and grants safely

**Acceptance scope approved 2026-10-06. Not implementation-ready.**
Owner: existing Access service. Depends on ENV and completed ID-B's verified identity,
membership and controlled operator foundation. ACCESS-B supplies runtime enforcement.

As a platform administrator,
I want controlled setup of application availability and exact account or organization grants,
So that each organization and account receives only its intended application access.

**Acceptance Criteria:**

**Given** an authenticated operator authorized for the exact Access command and target,
**When** explicit application and capability registrations are provisioned,
**Then** immutable app/capability associations and each capability's required scope are recorded with required attribution,
**And** new applications begin disabled, unknown/conflicting mappings fail, and no
wildcard, implied read grant or user grant is created automatically.

**Given** a verified organization and exact current account/membership,
**When** the operator configures organization enablement or assigns/revokes/regrants a
specific registered capability using expected absence or the current revision,
**Then** the owner commits only that intended target's change,
**And** grants bind the exact membership; retired membership, stale state and wrong
organization fail safely. Rejoining never restores old grants, and an old revoke
cannot retire a replacement grant. Disabling retains grants without deleting them.

**Given** a verified account and registered account-scoped capability,
**When** the operator assigns, revokes or regrants that exact account capability,
**Then** expected absence/revision, current operator authority and atomic evidence guard
that account grant without organization, membership or employment requirements,
**And** scope-mismatched commands fail. No account grant satisfies an organization action;
no organization grant supplies account authority. Explicit entry-capability configuration
uses the app's registered read capability; grants are never expanded implicitly.

**Given** duplicate attempts, changed input under the same operation ID, or a lost response,
**When** the command is executed or its outcome retrieved with current operator authority,
**Then** identical retries produce one durable local effect and compact outcome; changed
input fails and unknown outcomes remain unresolved rather than inviting a new duplicate,
**And** changed-state evidence and revision commit atomically with the change; unchanged
registration creates no fictitious change event. Receipts are not current-state queries.

**Given** an ordinary runtime credential, a spoofed actor in input, an unapproved target
or missing scope,
**When** provisioning or receipt lookup is attempted,
**Then** authority is rejected before protected changes or evidence are disclosed,
**And** runtime cannot administer grants or perform DDL. Restricted owner writers,
server-derived actors, external reference validation before local locks and pooled
connection isolation are proved against a real disposable database.

**Given** the declared supported legacy schema and synthetic PtS grant/actor data,
**When** the Access-owned migration and adoption procedure run,
**Then** known permission mappings and membership/actor bindings are verified explicitly,
**And** unknown mappings block adoption; unmatched grants do not acquire invented access.
Preserve existing account IDs and attribution meanings. Add stricter constraints only
when supported writers are compatible, or through the declared maintenance procedure.
Migration failure blocks dependent activation without automatic destructive rollback.

**Given** the existing Access owner and declared consumer transition,
**When** Access receives its own locked dependencies/container inputs and schema adoption,
**Then** characterization protects intended current behavior before coordinated replacement,
**And** new configuration is not claimed effective while old checks ignore it. Legacy PtS
wire/membership semantics need not survive the planned transition under ADR-0052.
Prove previous-version compatibility where applicable or use the declared maintenance
path; no permissive intermediate endpoint. ACCESS-B supplies current scope enforcement,
and PTS-ADOPT owns actual PtS consumer activation. A completes with isolated fixtures.

**Given** this story's initially failing acceptance checks and its completed delivery,
**When** verification evidence is recorded,
**Then** controlled configuration, replay/concurrency, restricted-role, compatible-writer
and migration-failure checks pass without future discovery, launcher or administration UI,
**And** exact commands/results, owner templates/fixtures, client/error compatibility,
runbook and changelog are updated. No production account mutation is an acceptance fixture.

**Traceability:** Parent ACCESS; E1-ENTRY-02/05/06/07/10/12, E1-DRAFT-17 and
E1-AC-13/15/17/18 as configuration foundations. ACCESS-B owns live decision/denial and
revocation enforcement evidence; A alone does not pass those complete scenario groups.
Sources: [admission contract](../../platform/docs/architecture/contracts/application-admission-and-discovery.md)
and [controlled provisioning](../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md).

**Scope/impacts/readiness:** Access-owned schema and commands only; no public setup API,
role UI, generic provisioning service or employment mutation. Reuse ID-B's established
operator adapter and shared error/evidence conventions, with Access-specific authority
and transactions. Scaffold/fixtures/docs change with the owner; no new shared UI or
agent rule; accepted ADRs unchanged. Exact operator authentication/target authority,
typed command/result bounds, compatible writer handover, migration privileges and
locked dependency resolution remain explicit pre-story inputs. Do not silently move
an unfinished shared operator framework into this item.

Next discussion: confirm this child scope, then detail ACCESS-B's current authorization
and supported v1/v2 activation checks. No application code or runtime tests in this pass.


ACCESS-A acceptance agreement — 2026-10-06: user approved its detailed controlled
configuration/adoption criteria. Operator adapter, typed bounds, compatible writer
handover and migration privileges remain readiness inputs. Approval does not activate
new admission controls or authorize application implementation/live account changes.

### Candidate Story E1-ACCESS-B: Enforce current application and user access

**Detailed criteria reconciled 2026-10-07 to accepted ADR-0052–0055; decomposition approved. Technical readiness pending.**
Owner: existing Access service. Depends on completed ACCESS-A and its Identity/ENV
prerequisites. Subsequent DISCOVERY, WRITE and PEOPLE consume this completed boundary.

As an application user,
I want protected actions to respect my current organization and application permissions,
So that sign-in or an old link cannot expose information I am no longer allowed to use.

**Acceptance Criteria:**

**Given** an authorized calling service and authenticated user,
**When** `/v2/check` evaluates an exact capability and typed authorization_scope,
**Then** the registered scope determines the check: account capabilities require current
account/profile, global app admission and exact account grant; organization capabilities
also require current organization/membership, organization enablement and exact bound grant,
**And** mismatched scope fails without fallback. E1 Leave own-request checks add verified
person/actor and resource_scope; account checks require verified actor but no employment,
person link or membership. Read/manage/export/document grants do not imply one another.

**Given** a valid user token but an invalid calling credential or a service configured
for a different app/operation,
**When** it requests a check,
**Then** Access rejects the service without revealing protected identity/setup details,
**And** a service credential alone cannot impersonate a user. Leave, PtS and the
synthetic reference use their explicit allowed operations; no wildcard service authority
or new credential-rotation subsystem is introduced.

**Given** successful account and organization authorization observations,
**When** a new check follows a relevant revocation or disable even with a valid token,
**Then** it evaluates current state without cached-positive/JWT-role fallback: account or
app disable affects applicable account and organization checks; membership/organization
changes affect only corresponding organization authority; independent account access remains,
**And** rejoin cannot restore old membership-bound grants; re-enable resumes only still-valid
authority. No membership/employment/draft is created. Already-authorized bounded execution
keeps ADR-0021 semantics, not instantaneous distributed cancellation.

**Given** expired authentication, unavailable verification or missing person/actor setup,
**When** the check is evaluated,
**Then** it returns the owning contract's distinct safe authentication, unavailability
or setup error; setup information is disclosed only after relevant access is established,
**And** a missing grant remains denial even if person setup is also missing. The typed
consumer adapter treats service-credential rejection as dependency/integration failure,
not a false message that the employee lost permission. No outage becomes access denial.

**Given** an allowed response or error,
**When** the client consumes it,
**Then** private/no-store behavior, exact UUID and decimal-string bigint serialization,
matching capability/authorization_scope and the variant's identity/resource fields are verified,
**And** decision ID/time are observation evidence, never reusable authorization tokens.
Malformed/duplicate/unknown input fields fail safely. Logs/errors contain no tokens,
service secrets or unnecessary personal fields; provider waits occur outside DB locks.

**Given** explicit account and organization capabilities in the synthetic reference fixture,
**When** either or both are granted and checked,
**Then** each succeeds only through its registered scope and exact independent grant,
**And** missing organization for an organization action or cross-scope authority fails.
The fixture uses its own capabilities, not PtS grants. It proves mixed-scope platform
behavior without delivering future PtS organization features. No mandatory legacy v1
response parity remains; PTS-ADOPT owns the actual caller replacement under ADR-0052.

**Given** restricted database roles, connection reuse and concurrent access changes,
**When** direct contract/integration tests exercise allowed and denied checks,
**Then** missing/wrong scope and unrelated account/organization requests expose no
protected data, runtime cannot mutate grants or schemas, and declared in-flight ordering
is demonstrated,
**And** provider-authentication and real database tests complement fault-injection tests;
mocked success alone cannot establish current authorization or isolation.

**Given** the declared existing/new consumer compatibility matrix and synthetic cohort,
**When** the controlled release transition is rehearsed,
**Then** required migrations/provisioning precede activation and failure blocks dependent
activation with explicit recovery,
**And** mixed old binaries that ignore admission are never reported as enforcing the new
controls. Prove the supported compatible rollout or use the existing planned-maintenance
route. Coordinate later Directory/consumer activation before claiming end-to-end discovery
and suspension; ACCESS-B acceptance itself needs no future launcher UI or People endpoint.

**Given** the initially failing acceptance tests and completed implementation,
**When** delivery evidence is recorded,
**Then** current check, service isolation, typed disclosure, revoke/rejoin/re-enable,
scope-variant/transition and restricted-role tests pass with exact commands/results,
**And** updated OpenAPI/client adapters, fixtures, safe logging and rollout documentation
are owned together. This does not claim the complete Leave browser journey has passed.

**Traceability:** Parent ACCESS, E1-ENTRY-02/05/06/07/10/12, E1-DRAFT-17 and
E1-AC-13/15/17/18. [Identity wire contract](../../platform/docs/architecture/contracts/identity-access-employment-e1.md)
and [admission/transition contract](../../platform/docs/architecture/contracts/application-admission-and-discovery.md)
remain authoritative. Platform ADR-0019/0020/0021/0023/0025/0031/0035/0042/0046 and 0052–0055 apply.
Content trusts its authenticated owning API under 0054; no duplicate per-user Access
check inside Content is required. PtS itself checks document permission before streaming.

**Scope/impacts:** Current access checks and compatible transition, with no role editor,
discovery API, People business rule, document permission expansion or copied app-local
authorization authority. Shared scaffold receives proven typed clients/error adapters and
contract fixtures; subsequent UI consumes existing safe states. Existing agent rules
suffice; owner docs/runbook/changelog update together; accepted ADRs unchanged.

**Remaining readiness inputs:** Final caller policy including People/reference mapping,
exact reference capability IDs, request/response bounds, selected baseline/writer and
consumer transition matrix, authentication provider evidence and executable verification
commands. ACCESS-A controls are prerequisites, not proof these checks work. No code,
credential, live grant, migration or runtime test was changed in this planning pass.


## PtS individual-access correction — accepted 2026-10-06

The user directs PtS to adopt the new platform with individual access and no organization.
[Platform ADR-0052](../../platform/docs/architecture/decisions/0052-pts-account-scoped-access-and-coordinated-adoption.md)
governs earlier contradictory PtS organization/v1-preservation criteria, including
ACCESS-A's recently approved compatibility criterion and ACCESS-B's proposed v1 parity.
Do not implement those superseded clauses as target product behavior.

- ACCESS-A: retain controlled owner provisioning, add explicit account grants for PtS;
  Leave grants remain membership-bound. Reconcile transition fixtures rather than
  require unchanged old PtS behavior indefinitely. No automatic conversion of all
  legacy organization grants into account authority.
- ACCESS-B: check each declared scope: PtS account/app/capability; Leave organization
  enablement/membership/capability plus employee identity context where applicable.
  Replace mandatory v1/v2 parity with coordinated PtS/Access/Content caller adoption.
  Existing protection continues until replacement activation, using planned maintenance
  if necessary; no permissive intermediate endpoint.
- DISCOVERY/LAUNCHER: a PtS-granted account with zero memberships sees PtS and the
  permitted Scribeswell menu entry; Leave remains absent without its independent grants.
  PtS has no organization selector. Public Scribeswell reading remains unchanged.
- ID/transition: do not create memberships to restore PtS access. Small-cohort manual
  account recreation remains allowed, with explicit individual grants and actor evidence.
- Scaffold: prove explicit organization/account scope variants and optional selector;
  People is not a PtS dependency. API clients must not assume every success has org_id
  or membership_id. Existing organization-only Leave response remains its typed variant.

The 21-item sequence remains the planning baseline, but ACCESS-A/B sizing must be
rechecked after inventorying PtS corpus/read/export/Content consumers and settling
account-grant/check contracts. This is material prerequisite scope, not a hidden task
inside Leave. No new story split or concrete wire/storage design is silently approved.
No application code, account/grant change, migration or implementation authorization.


## Capability-level scope agreement — 2026-10-06

User approved [ADR-0053](../../platform/docs/architecture/decisions/0053-capability-scoped-access-in-mixed-scope-applications.md):
current PtS individual capabilities, future separately authorized PtS organization
features, organization-independent Scribeswell and organization-scoped Leave. This
qualifies ADR-0052's whole-app wording without reviving legacy PtS compatibility.

ACCESS-A's registry binds exact capabilities to app and required scope; account and
organization provisioning use separately constrained targets. ACCESS-B dispatches only
to the registered scope and proves both through a synthetic mixed-scope fixture; no
fallback after denial and no cross-scope implied grant. Global app disable affects both;
organization disable preserves independent account access. These refinements govern
older whole-app scope/membership-only criteria, which cannot be used as target acceptance.

DISCOVERY/LAUNCHER list one eligible app entry, keep account paths free of mandatory
organization selection and scope organization discovery to actual eligible contexts.
Earlier single `scope_kind` per app response proposals need reconciliation before
readiness. Current Scribeswell menu rule uses PtS account access; future organization
features do not implicitly change it. Their product implementation is deferred.

Scaffold capability/client and scope fixtures, agent context, owning PtS architecture
and platform contracts now reference this decision. Leave's first slice and current
21-item sequence remain the baseline; sizing is revisited after concrete PtS caller/
corpus/Content transition design. Next work: reconcile typed account/organization check
and discovery contracts, then inventory PtS resource boundaries. No code or readiness pass.


## Capability check and discovery wire refinement — 2026-10-06

Owning contracts now specify [typed authorization variants](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#canonical-capability-check-wire--2026-10-06)
and [one-row-per-app discovery](../../platform/docs/architecture/contracts/application-admission-and-discovery.md#canonical-discovery-refinement--2026-10-06).
ACCESS-B's old required top-level org/membership/person for all responses is replaced by
closed account and organization-own variants. Authorization scope and resource scope
are distinct. Caller identity comes from the token; capability registration determines
scope, and mismatch never falls back. Account checks require actor evidence, not employment.

DISCOVERY returns eligible_scope_kinds, not an exclusive application scope. PtS zero-
membership users work; mixed apps appear once. Entry uses explicit read capabilities
(PtS poetry read, Leave own request read); manage/export never implies read. Scribeswell
menu eligibility uses the account variant of PtS. LAUNCHER keeps AppEntry presentation;
protected navigation/direct actions recheck current authority. No future PtS org UI.

Update ACCESS-A registry entry configuration and ACCESS-B/DISCOVERY/LAUNCHER/client
fixtures together during authorized delivery. No runtime implementation or API compatibility
is claimed. Next concrete prerequisite: inventory PtS corpus/Content read boundaries and
choose the storage/resource transition, then settle account grant/actor persistence.


## PtS corpus transition proposal — 2026-10-06

[Owning source inventory and proposed boundary](../../apps/pts/docs/architecture/contracts/account-access-and-corpus-transition.md)
traces browser/org header, Access, repository RLS, Content read/import and source upload.
Recommend an application-owned shared corpus with individual read/export/document
capabilities. No fake membership, per-account corpus copies or blanket RLS relaxation.
The read-only clarification excludes personal document migration, not preservation of
existing corpus source assets. Internal storage locators do not determine user authority.

This is a proposed resource boundary, not yet approved DDL or Content association protocol.
PtS/Content adoption should have its own bounded delivery item rather than be hidden inside
ACCESS-B. Set its concrete scope/dependencies after agreement; the current 21-item baseline
is not silently renumbered. First Leave journey and all pre-story/provider gates remain.


## Content authorization boundary agreement — 2026-10-06

User accepted [platform ADR-0054](../../platform/docs/architecture/decisions/0054-application-authorized-content-and-enforced-ownership.md):
application API checks the user/domain record; Content authenticates the service and
enforces stored single-app ownership and typed resource scope before signed issuance.
No callbacks or extra authorization service. No list of shared owning applications.
Browser byte transfers remain direct; control-plane calls use the app API. This replaces
the PtS proposal's duplicate user-permission check inside Content, not domain protection.

PtS adoption and E4 attachment stories need both independent-layer and integrated tests,
including wrong app/scope, sensitive-document denial and fixed bytes. Ownership scope
is separate from permission scope: PtS individual document permission can release an
application-owned corpus file. Content records service executor and asserted initiator
accurately, without claiming independent end-user verification.

Remaining concrete contracts: owned metadata/legacy mapping, service-policy/typed command
and actor bounds, association/cleanup and provider evidence. Keep existing 21-item baseline
until the separate PtS adoption boundary is sized; no implementation/readiness approval.


## Authenticated private download agreement — 2026-10-06

The user requires sign-in/current authorization for most file reads; future exceptions
are handled when needed. [ADR-0055](../../platform/docs/architecture/decisions/0055-authenticated-private-downloads-by-default.md)
sets private authenticated streaming through the owning API and Content as the default,
superseding signed browser read URLs. P-0054 ownership enforcement remains; direct signed
uploads remain. No public-share feature/switch is added now.

PtS adoption must prove auth/preview/download/range, bounded streaming, proxy/cache and
upstream/disconnect behavior before E4 reuses it. Each new request rechecks, without
promising recall of downloaded bytes or instant termination of in-flight streams.
Content metadata/legacy mapping and PtS adoption sizing remain open. No code/readiness pass.


## Content and PtS adoption decomposition proposal — 2026-10-06

[Content ownership/authenticated-read design](../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md)
now records minimum metadata, trust/streaming boundaries and the existing composite
key/immutability/audit migration constraints. This is source-grounded design, not DDL
or provider evidence. Each file has one app owner and one typed resource scope; uploader
attribution is separate. No per-scope bucket requirement or optional sharing system.

Propose CONTENT-READ (shared ownership/adoption/streaming proof with synthetic caller)
then PTS-ADOPT (real account-based browser/API/corpus/Content/launcher integration), after
LAUNCHER and before WRITE/REF. ACCESS-B stays focused on access decisions. This would
produce 23 items; await discussion before changing the approved 21-item matrix.
Contracts for storage mapping, auth preview/ranges, bounded streaming and proxy limits
remain binding; no future Leave dependency or PtS organization features are introduced.


## Content/PtS split approved and current sequence — 2026-10-06

User approved CONTENT-READ then PTS-ADOPT after LAUNCHER, before WRITE/REF. This
23-item sequence supersedes earlier 21-item ordering, not existing requirements.
Decomposition is accepted; detailed child acceptance and technical readiness are separate.

| Order | Candidate |
| --- | --- |
| 1 | E1-ENV |
| 2 | E1-P1 |
| 3 | E1-SERVICE |
| 4 | E1-ID-A |
| 5 | E1-ID-B |
| 6 | E1-ACCESS-A |
| 7 | E1-ACCESS-B |
| 8 | E1-DISCOVERY |
| 9 | E1-LAUNCHER |
| 10 | E1-CONTENT-READ |
| 11 | E1-PTS-ADOPT |
| 12 | E1-WRITE |
| 13 | E1-REF |
| 14 | E1-PEOPLE |
| 15 | E1-A1 |
| 16 | E1-CONTEXT |
| 17 | E1-CHOICES |
| 18 | E1-D1 |
| 19 | E1-D2-A |
| 20 | E1-D2-B |
| 21 | E1-D3 |
| 22 | E1-D4 |
| 23 | E1-D5 |

CONTENT-READ proves its owner boundary with restricted synthetic service callers;
placement after LAUNCHER does not make the launcher part of its isolated acceptance.
PTS-ADOPT consumes ACCESS-B, CONTENT-READ and DISCOVERY/LAUNCHER for the integrated
PtS transition. WRITE/REF still prove their own generated foundation; no Content
requirement is added to every generated app. Existing subsequent dependencies remain.
First Leave slice completes with D2-B; no attachment UI or future PtS organization
feature moves into that journey.

### Candidate Story E1-CONTENT-READ: Protect owned files and stream private reads

**Acceptance scope approved 2026-10-06. Not implementation-ready.**
Owner: existing Content service. Requires ENV, established Identity/service actor
conventions and finalized owner schema/service-policy/streaming contracts. Synthetic
caller fixtures prove this story without a future PtS UI or Leave attachment endpoint.

As an application owner,
I want Content to enforce file ownership and stream verified private bytes to my authorized API,
So that my application can protect downloads without exposing reusable storage read links.

**Acceptance Criteria:**

**Given** controlled creation or verified legacy adoption,
**When** Content records a file's owner,
**Then** one application and one valid application/organization/account ownership variant
are enforced structurally, with required identifiers and separate initiator attribution,
**And** ordinary runtime operations cannot reassign ownership; equal hashes in different
ownership scopes do not merge files or reveal another scope's content. No synthetic org
or nullable-org bypass is introduced for application/account resources.

**Given** a restricted authenticated application service and an exact content reference,
**When** it requests a private read with expected ownership context,
**Then** Content verifies the service's permitted app/operation, stored resource scope,
readiness and applicable safety/lifecycle before opening its own provider locator,
**And** wrong app, mismatched scope, unknown caller, unsupported operation or a bare browser
bearer releases no bytes or protected metadata. Caller-supplied application names and
provider URLs confer no authority. Organization/account checks compare recorded scope;
Content does not claim independently to verify the application's end-user decision.

**Given** a valid read of finalized content,
**When** Content streams to the authenticated application server,
**Then** it returns the exact verified byte identity using bounded buffers/backpressure,
**And** no signed read URL, credential or provider redirect is exposed in the read response.
Database transactions finish before transfer waits. File size/type and supported range
responses follow the finalized contract, with no truncation silently reported as success.

**Given** GET, HEAD or a supported range/resume request,
**When** the Content boundary handles it,
**Then** it repeats service/ownership/readiness checks and applies safe private no-store
headers to authorized output; unsupported variants fail safely,
**And** metadata requests cannot bypass authorization. The consuming app independently
rechecks user/resource authority on each browser request; that integrated proof belongs
to PTS-ADOPT and later E4, not a duplicated user-permission engine in Content.

**Given** provider failure, slow transfer or downstream cancellation,
**When** the declared bounds are reached or the client disconnects,
**Then** streams/connections close and resources remain bounded; safe typed failures are
returned before headers where possible, while failures after streaming starts terminate
an incomplete transfer without appending JSON or silently retrying the entire file,
**And** evidence distinguishes requested/started/completed/failed delivery observations
without claiming the user saved the file. New requests recheck; no instantaneous recall
of previously delivered bytes or universal mid-stream revocation guarantee is claimed.

**Given** the supported synthetic legacy object/event/association baseline,
**When** owned clean/adopt/mismatch and migration-failure rehearsals execute,
**Then** IDs, verified bytes, associations and original attribution/history retain their
meanings under an explicit mapping; unknown ownership, collisions and mismatches block
adoption rather than guessing,
**And** constraints, immutability triggers, event FKs and restricted runtime/import roles
are migrated consistently. No all-org-to-PtS mapping, startup migration, destructive
rollback or live production-data fixture. Use the approved maintenance/recovery path
where previous-version compatibility cannot be maintained.

**Given** the changed shared ownership schema and authenticated read adapter,
**When** failing-first acceptance and affected regressions run,
**Then** actual restricted-role scope/pool isolation, byte-identity, large-file streaming,
service-policy and migration recovery tests pass with exact commands and results,
**And** upload/finalization/retry/association behavior affected by the changes is protected.
Direct signed uploads remain; ownership changes do not waive ADR-0038 race/replay proof
or claim Leave E4's remaining attachment/cleanup/provider-lifetime gates are complete.

**Traceability:** Platform ADR-0035/0038/0054/0055 and the
[Content contract](../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md).
E1-ENTRY-06/10/12 and AC-15/17/18 receive shared-owner prerequisite evidence, not Leave
attachment acceptance. PTS-ADOPT provides the end-user read/resource authorization proof.

**Impacts/readiness:** Update owning migration/service/provider adapters, typed server
client, synthetic fixtures and release runbook together; promote only proven streaming
helpers to scaffold. Existing UI patterns suffice; no new preview/sharing product or
agent rule. Accepted ADRs unchanged. Final DDL/mapping, service credentials/actor bounds,
read/error/header contract, range support, transfer/concurrency budgets and proxy behavior
must be fixed before implementation. Their size may require further technical decomposition;
this planning approval cannot stand in for runtime evidence or close readiness.


CONTENT-READ acceptance agreement — 2026-10-06: user approved the detailed service
ownership/streaming/adoption criteria. Concrete metadata DDL, credentials, transport
bounds, browser/proxy design and executable evidence remain required; no readiness pass.

### Candidate Story E1-PTS-ADOPT: Use PtS through individual platform access

**Acceptance scope approved 2026-10-07, including permission/download/preservation clarification. Not implementation-ready.**
Owner: PtS, consuming completed ACCESS-B, CONTENT-READ and DISCOVERY/LAUNCHER.
Identity/ENV and provider/owner migration contracts are prerequisites. No Leave API,
employment record or future PtS organization feature is required to complete this story.

As an individually authorized PtS reader,
I want to open the existing poetry collection and permitted source documents without
selecting or joining an organization,
So that my individual access works consistently through the shared platform.

**Acceptance Criteria:**

**Given** a current account with explicit PtS read permission and no organization memberships,
**When** I sign in and open PtS,
**Then** the existing collection, filters, poem/source views and permitted navigation work
without an organization selector, org header or employment prerequisite,
**And** login/help/return and account-change states no longer ask me to choose an
organization. Supported return restores authorized view/filter context, never prior-user
data; stale organization parameters cannot select another corpus or confer authority.

**Given** read, export and document capabilities are assigned independently,
**When** a user calls the relevant API directly or through the UI,
**Then** each action requires its exact current account capability and PtS availability,
**And** missing/revoked grants deny, verification outages return unavailable, and changing
organization membership does not affect independent PtS account grants. Organization
or Leave authority never substitutes for a PtS account capability. No legacy endpoint
may bypass the new checks during coordinated activation.

**Given** a permitted source document associated with the selected PtS corpus,
**When** the browser requests its private contents,
**Then** PtS resolves the association server-side, checks current document authority and
streams through the authenticated Content boundary without exposing a storage read URL,
**And** each new GET/HEAD or supported range/resume request rechecks authorization. A copied
application URL grants no access to an unauthorized user; arbitrary Content IDs and
forged resource context cannot retrieve unrelated files. Existing external link-only
source references remain explicitly external; PtS does not claim to control third-party
access or turn external URLs into an unrestricted proxy.

**Given** supported browser download/preview behavior and representative existing large files,
**When** files are read, interrupted, retried or access changes before another request,
**Then** the chosen authenticated transport preserves correct bytes and bounded server
resources, with no shared-cache bypass, token-in-URL fallback or complete-file success
for a failed transfer,
**And** preview/range/HEAD, expired-session and account-change behavior are verified against
the actual app/proxy path. Already delivered copies are not recalled; an in-flight stream
is governed by its declared bounds. This adds no new preview product or public sharing.

**Given** the inventoried legacy PtS corpus and Content mapping,
**When** controlled owner migrations/import configuration adopt application-owned resources,
**Then** poems, witnesses, source/rights metadata, original payloads, import/conflict history
and source-document associations retain their intended meanings and verified bytes,
**And** no per-account copy, implicit all-org corpus merge or personal-document migration
is introduced. Reimport remains duplicate-safe and conflicting changes remain explicit.
Restricted runtime/import/migrator roles and resource isolation are exercised on a real
synthetic baseline; unknown partitions/identity mismatches stop adoption safely.

**Given** the updated Directory/launcher contract,
**When** current discovery succeeds for an account with PtS read access,
**Then** published PtS and its permitted Scribeswell menu entry appear without membership,
**And** Leave requires its own organization entry capability. Revocation removes current
eligibility; unavailable discovery shows its agreed failure state without inferred access.
Public Scribeswell reading stays independent and no account signup or new protected
Scribeswell feature is added.

**Given** the selected old/new caller inventory and small-cohort transition procedure,
**When** coordinated PtS/Access/Content/Directory adoption is rehearsed,
**Then** required configuration/migrations verify before activation; failure prevents
partial unsafe activation and follows explicit recovery, using planned maintenance if needed,
**And** old organization-based PtS responses need not be preserved permanently. Any manual
account recreation provisions intended individual grants explicitly, without fake
membership. Synthetic acceptance does not mutate the three production users or deploy.

**Given** the initially failing acceptance scenario and subsequent focused implementation,
**When** the story's verification is completed,
**Then** actual account sign-in/current checks, corpus API/database, authenticated source
streaming and browser journey evidence pass with exact commands/results,
**And** characterization protects existing search/filter/citation/export and corpus semantics;
no expected result is changed merely to conceal an unexplained regression. Tests also
cover wrong account/capability/content, stale URL context, no memberships and interruptions.

**Traceability:** Platform ADR-0052–0055, ADR-0020/0023/0025/0038 and the
[PtS transition contract](../../apps/pts/docs/architecture/contracts/account-access-and-corpus-transition.md).
E1-ENTRY-02/05/06/10/12 and AC-13/15/17/18 receive shared-platform adoption evidence;
this is not the Leave draft journey, E4 medical-document acceptance or full pilot evidence.

**Scope/impacts/readiness:** Modify PtS's owner API/web/corpus migrations/import adapters
and consume proven shared contracts; no copied Access/Content server implementation.
Promote proven account-route/download/client fixtures to scaffold with applicable shared
UI fixes. Existing agent rules suffice; PtS owner docs and release runbook plus Leave
traceability update together, preserving historical frozen specifications/accepted ADRs.
Finalize corpus DDL/mapping and selected real-state inventory, browser authentication/
preview transport, transfer/proxy limits and activation/recovery before readiness. This
story does not absorb Content's provider implementation or new PtS organization features.
The approved 23-item sequence remains; no code or runtime evidence from this planning pass.


## PtS approval and Access reconciliation — 2026-10-07

User approved PTS-ADOPT including the clarified meanings: read/export/document checks
are separate capabilities that may be granted together; private source downloads use
authenticated requests; preservation covers existing corpus relationships and import
history, not new user-facing features. No new role editor or extra per-user setup flow.

ACCESS-A/B current child text now reflects accepted ADR-0052–0055: account and organization
capabilities, explicit entry mapping, typed scope/response variants, no automatic grant
inheritance, no permanent PtS v1 parity requirement and no duplicated user check in Content.
Earlier dated parent stories remain historical combined references; current child text
and owning contracts govern. This reconciliation introduces no new product decision and
requires no reapproval of the accepted scope. Exact schemas, operator adapter, current
actor mapping and transport/release evidence remain readiness inputs.

The approved 23-item sequence is unchanged. Next contract work: account-grant storage
and controlled provisioning alongside membership-bound grants, then Content transport/
legacy mapping and the remaining E1 readiness inputs. No runtime tests or implementation.


## Individual grant contract progress — 2026-10-07

[Access-owned individual grant design](../../platform/docs/architecture/contracts/application-admission-and-discovery.md#individual-grant-persistence-and-administration--2026-10-07)
selects separate account_grants keyed by account/capability, with fixed scope constraints,
revision/revocation/attribution and shared owner-command evidence. Organization grants
retain membership binding. Controlled platform-operator account_grant.assign/revoke
commands reuse the existing envelope; no new role UI or permissions-management service.

ACCESS-A tests structural scope enforcement and write/replay/concurrency; ACCESS-B tests
current account/org effects. Same-person accounts do not inherit each other's grants;
new account IDs require explicit provisioning. App/account disable suspends current
access, while explicit revocation is retained. No automatic legacy grant conversion.
Existing 23-item sequence and Leave first slice unchanged. Next: ensure actor projection
supports account-only users without forced employment/person setup, then remaining
Content streaming/mapping and E1 readiness contracts. No code or runtime evidence.


## Account-only actor contract refinement — 2026-10-07

User confirmed multiple organization memberships plus independent individual grants.
[Identity actor design](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#account-only-actor-resolution--2026-10-07)
now explicitly separates account attribution from optional person linking. ID-B provides
account_actor.ensure with stable mapping and retained historical actors; no runtime
read creates identity. PtS needs no employee/person setup; Leave still resolves its
verified person for own-request scope. Two accounts for one person do not merge actors
automatically or combine grants; recreation preserves earlier evidence, not access.

This qualifies earlier ID-B wording that coupled all account actor creation to person
linking. ID-B/ACCESS-B/CONTENT-READ/PTS-ADOPT own the declared tests at their respective
boundaries. No new product screen, service or ADR; exact actor DDL/projection and operator
bootstrap remain gates. Existing 23-item sequence and first Leave slice unchanged.
Next: choose the minimal authenticated browser download/preview transport and bound
streaming/proxy behavior, then settle Content legacy mapping and remaining E1 inputs.


## Actor registry decision — accepted 2026-10-07

The user selected the separate actor registry for clarity between human account profiles
and attribution identities. [ADR-0056](../../platform/docs/architecture/decisions/0056-durable-actor-registry-separate-from-login-accounts.md)
confirms Identity-owned account/system/service actors, including retained System/Migrate,
without requiring new service Auth accounts. identity.users keeps its Auth-account meaning.
Earlier discussion of retaining the old unified model was an alternative, not the decision.

ID-B owns registry/mapping/bootstrap and writer/deletion-history evidence; Access consumes
verified account actors; Content keeps executor/asserted initiator distinction. Existing
UUIDs/history are preserved where verified, not overwritten by actor migration. No new
actor per login provider/run or actor-management UI. The 23-item order stays unchanged;
concrete DDL/operator/projection and streaming contracts still precede readiness. No code.


## Actor schema contract progress — 2026-10-07

[Minimum Identity actor persistence/lifecycle](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#minimum-actor-persistence-and-lifecycle--2026-10-07)
now specifies actor and immutable one-to-one account_actor mapping, constrained actor kind,
retained historical account IDs and live-account verification. System/Migrate/service
actors use controlled registration without new Auth accounts. Clean bootstrap records its
trusted migrator provenance; ordinary writes cannot fall back to a generic system actor.

ID-B owns new schema/projection/bootstrap and explicit old FK/text-writer adoption; later
consumers reuse verified actor context. Historical preservation is not a promise that
existing Auth/profile deletion dependencies are already migrated. No actor UI/relink,
per-run actor creation or cross-owner FK engine. Exact DDL privilege/limit/compatibility
work remains; 23-item ordering and implementation gate unchanged. Next: return to the
Content browser/streaming contract with the attribution boundary settled in design.


## Authenticated browser file transport proposal — 2026-10-07

[Owning discussion](../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md#browser-transport-proposal--2026-10-07)
proposes an app-specific secure HttpOnly authentication cookie tied to existing sign-in,
so normal file/preview requests can authenticate without token URLs. Every request still
checks current access. No new sign-in, generic sharing ticket, full-app cookie conversion
or refresh-token engine is selected. Logout/account-switch/viewer expiry behavior must
be explicit. This direction awaits discussion; exact adapter remains pre-story design.

Netlify's documented proxy timeout is a concrete large-source-file readiness concern.
PTS-ADOPT must prove a suitable routed app API path; CONTENT-READ proves upstream bounded
streaming. Do not bypass private-read policy to accommodate hosting limitations. Existing
23-item order/approved scope remains; no code, deployment or runtime evidence added.


## Download ingress direction and verification — 2026-10-07

User approved resolving Netlify limits before release. The [direct application ingress
contract](../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md#direct-application-download-ingress--direction-accepted-2026-10-07)
proposes per-app download origins to the existing gateway and owning API, avoiding Netlify
for bytes while retaining frontend hosting. Exact hostnames remain proposed, not verified
DNS or deployment. Current renderer's single host/origin and generic timeout settings need
explicit owner changes, not handwritten generated config.

PTS-ADOPT owns authenticated browser/gateway path and current-session lifecycle; CONTENT-READ
owns upstream streaming. Plan a 128 MiB synthetic file throttled near 1 MiB/s to exceed
26 seconds, plus bounded failure/range/disconnect/cache/isolation checks. Limits at each
hop and auth binding must be concrete before readiness; deployed-path proof before release.
The 23-item sequence remains. No provider changes, runtime tests or new download service.


## File authentication lifecycle discussion — 2026-10-08

[Owning proposal](../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md#file-authentication-lifecycle-proposal--2026-10-08)
reuses existing sign-in/refresh, binds file requests to current account/session, renews
without a second refresh token, and requires logout/switch plus native-viewer isolation.
This is behavior for discussion, not a selected opaque session store or token cookie.

Provider JWT expiry does not by itself prove logout revocation. Exact current-session
checks and late Set-Cookie/account-switch ordering must be tested; the app's existing
JavaScript account epoch alone is insufficient for native file requests. PTS-ADOPT owns
that proof; Content remains service/ownership enforcement. No duplicate auth framework,
signed-URL fallback, new story or readiness pass is introduced.


## File lifecycle approval and transfer behavior — 2026-10-08

User approved the file-authentication lifecycle behavior: existing sign-in/refresh,
expiry recovery, logout and account-switch isolation. This supersedes the earlier
for-discussion status; the exact adapter and provider revocation proof remain open.

[Download/preview behavior](../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md#download-and-preview-behavior--proposed-2026-10-08)
is the next proposal: native download/PDF viewing, single-range support, fixed finalized
bytes and honest interrupted-transfer handling. CONTENT-READ owns shared transport;
PTS-ADOPT owns browser/gateway proof; Leave E4 later consumes it. Existing E1 sequence
and first draft slice remain unchanged. No implementation or readiness pass.


Download acceptance clarification — 2026-10-08: user accepted browser-owned
download/viewer/resume behavior enabled by application headers, partial reads and current
authorization. Record these as technical criteria within CONTENT-READ/PTS-ADOPT; no custom
viewer/download manager or separate browser-feature story.

Next discussion: [concrete PtS adoption mapping](../../apps/pts/docs/architecture/contracts/account-access-and-corpus-transition.md#concrete-adoption-mapping--proposed-2026-10-08)
proposes reviewed legacy-to-target object/association evidence, preserving bytes and
verified IDs without copying per account or implicitly merging unrelated partitions.
Physical schema, deployed inventory and readiness remain open. No application code changed.


PtS concrete adoption mapping approved — 2026-10-08: reviewed selected-object mappings,
application ownership, preserved bytes/associations and verified IDs; existing opaque
provider paths may remain. Physical inventory/schema/rehearsal remain pending.

Next discussion: [operator execution surface](../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md#operator-execution-surface--proposed-2026-10-08)
proposes protected owner-local command-line entry points for E1 setup, with verified
execution identity and restricted owner writers. This refines the existing command
contract; it does not replace E2 administration or create another story. Concrete
authentication/privileges, other technical contracts and readiness remain unresolved.


Operator execution surface approved — 2026-10-08: protected owner-local CLI setup,
verified execution identity and restricted owner writers; E2 administration remains.
Concrete binding/privileges and technical readiness stay open. Next proposal:
[setup verification boundary](../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md#setup-verification-boundary--proposed-2026-10-08),
using existing acceptance suites/runbooks to distinguish local command completion from
effective authorization and a working consumer. No new story, product status system,
production mutation or runtime evidence.


Setup verification boundary approved — 2026-10-08. User additionally proposed a test
application in development, staging and production for release/support verification.
[Platform verification app proposal](../../platform/docs/architecture/contracts/platform-verification-app.md) recommends extending E1-REF
with an explicitly sized hosted scope, real shared-service paths and restricted synthetic
production journeys; application-specific tests remain on their owning apps. Direction
is under discussion; no new story count, production fixture permission, implementation
or readiness pass. Current disposable reset safeguards remain binding.


Platform verification direction approved — 2026-10-08: [approved responsibility split](../../platform/docs/architecture/contracts/platform-verification-app.md#approved-boundary).
The verification app exercises shared platform features; app-specific synthetic journeys
run in each actual application with dedicated accounts/test data and required org fixtures.
Shared runners/reporting do not duplicate product workflows. Hosted scope still requires
explicit sizing; 23-item sequence, first Leave slice and readiness gates remain unchanged.
No implementation, deployment, production test execution or new schedule authorized.


### Candidate Story E1-VERIFY: Exercise the shared reference journey in hosted environments

**Scope and placement approved 2026-10-08; not implementation-ready.** Platform deployment/test
owner. Depends on completed E1-REF and its prerequisites. Placement immediately
after REF, before PEOPLE makes 24 E1 items. Earlier PtS adoption keeps
its own release checks and does not depend on VERIFY.

As a platform maintainer,
I want the proven reference journey available in development, staging and production,
So that I can check deployed shared functionality after releases and during support.

**Acceptance Criteria:**

**Given** the proven reference application and explicitly configured environment,
**When** an authorized internal tester signs in and creates/reads its synthetic example,
**Then** the real deployed shared Access and persistence path is exercised,
**And** ordinary user and organization permissions apply with no test bypass.

**Given** pre-provisioned synthetic identities with allowed and denied capabilities,
**When** the existing Playwright runner executes the approved hosted suite,
**Then** it verifies successful persistence and expected access refusal,
**And** output identifies environment, scenario, deployed versions and safe trace references;
incomplete or skipped tests cannot be reported as successful verification.

**Given** a production target,
**When** an authorized on-demand or post-release run executes,
**Then** only the approved bounded synthetic journeys and owned records can be selected,
**And** fixture cleanup cannot target customer data or invoke disposable-environment reset.
No destructive failure injection, load testing or customer impersonation is included.

**Given** the application is being published or updated,
**When** staging verification fails or required target/credential/isolation evidence is absent,
**Then** dependent production activation is blocked,
**And** a production verification failure follows the existing release-recovery runbook
without automatic destructive schema rollback.

**Traceability:** User-approved platform/app verification split; existing E1-REF foundation,
E1-AC-15/17/18, ADR-0020/0023/0046 and the
[hosted verification contract](../../platform/docs/architecture/contracts/platform-verification-app.md#hosted-delivery-increment--proposed-2026-10-08).
This story proves hosted reference integration, not Leave draft or PtS workflow acceptance.

**Impacts/readiness:** Reuse scaffold output, deployment manifests and test reporting;
no new shared UI beyond the reference surface, no new agent-context rule or ADR decision.
Update owner runbook, fixture/release commands and traceability together. Exact hosted
configuration, operator/run authority, production fixture restrictions and cleanup bounds
must be settled before readiness. New platform scenarios join with their owning delivery;
no assumption that this first increment tests all platform functionality.


## Hosted verification approved and current sequence — 2026-10-08

User approved VERIFY after REF, clarifying there is one maintained platform reference
application. REF builds its reusable journey/tests; VERIFY adds hosted deployment and
release operations using those same artifacts. This supersedes prior 23-item sequencing.

| Order | Candidate |
| --- | --- |
| 1 | E1-ENV |
| 2 | E1-P1 |
| 3 | E1-SERVICE |
| 4 | E1-ID-A |
| 5 | E1-ID-B |
| 6 | E1-ACCESS-A |
| 7 | E1-ACCESS-B |
| 8 | E1-DISCOVERY |
| 9 | E1-LAUNCHER |
| 10 | E1-CONTENT-READ |
| 11 | E1-PTS-ADOPT |
| 12 | E1-WRITE |
| 13 | E1-REF |
| 14 | E1-VERIFY |
| 15 | E1-PEOPLE |
| 16 | E1-A1 |
| 17 | E1-CONTEXT |
| 18 | E1-CHOICES |
| 19 | E1-D1 |
| 20 | E1-D2-A |
| 21 | E1-D2-B |
| 22 | E1-D3 |
| 23 | E1-D4 |
| 24 | E1-D5 |

The first Leave draft slice and all pre-story/readiness gates remain binding. Hosted
configuration, isolation/cleanup bounds and commands still require concrete design.
No code, deployment, production test run or schedule is authorized by story approval.


Hosted fixture proposal — 2026-10-08: [verification contract](../../platform/docs/architecture/contracts/platform-verification-app.md#hosted-fixture-boundary--proposed-2026-10-08)
proposes stable per-environment synthetic accounts/two organizations, known allowed/denied
permissions, bounded run records and exact owner-scoped cleanup. Ordinary production
runners cannot administer accounts/grants or reset environments. Other applications use
their own lifecycle rules for synthetic data. Refines VERIFY only; 24-item sequence and
readiness gates stay unchanged. Concrete retention/limits and invocation remain open.


Hosted fixture boundary approved — 2026-10-08. Stable dedicated identities, known
allowed/denied access, bounded test records and exact ownership-checked cleanup stay
within VERIFY; concrete limits remain to settle. Next discussion returns to ACCESS-B:
[initial service caller matrix](../../platform/docs/architecture/contracts/application-admission-and-discovery.md#initial-service-caller-matrix--proposed-2026-10-08)
proposes explicit per-service operations, including People's narrow Leave own-read
consumer mapping and Content's already approved service/ownership boundary. No new
story or implementation; 24-item sequence and readiness gates remain binding.


People caller-policy correction — 2026-10-08: user accepts the other matrix boundaries
but questions People querying Leave permissions. Withdraw that proposed coupling. Leave
checks its own access; People enforces its independent authorized service/current user/
person/organization own-employment boundary, as the existing identity contract requires.
Exact verified-context wire remains open; no raw-header trust or employment-based access
grant is introduced. Corrected recommendation remains for discussion; accepted ADRs,
24-item sequence and readiness gates unchanged. Documentation only.


People boundary approved — 2026-10-08: People does not check Leave capability names.
Next [current-context wire proposal](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#people-current-identity-context--proposed-2026-10-08)
uses a restricted Access-owned identity/membership projection for People, alongside
People's service/own-data policy and Leave's independent application authorization.
ACCESS-B supplies the endpoint before PEOPLE; no new service/story or future dependency.
Wire remains for discussion; 24-item sequence and readiness gates remain unchanged.


People API boundary reaffirmed — 2026-10-08: user agrees to independent HTTP ownership;
co-hosting is not a deciding factor. Retain existing API/no-cross-owner-table architecture,
with no accepted ADR change. This does not claim the proposed identity-context endpoint
or its provider verification has been implemented or independently approved in detail.

Initial [reference capability names](../../platform/docs/architecture/contracts/platform-verification-app.md#initial-reference-capability-identifiers--2026-10-08)
are now concrete: `reference.record.read` and `reference.record.create`, organization
scope, entry by read. Existing setup/Access/WRITE/REF/VERIFY responsibilities share those
identifiers; no extra story or expanded CRUD. Remaining technical contracts/readiness
stay open; 24-item sequence unchanged.


Reference example wire proposal — 2026-10-08: [owning contract](../../platform/docs/architecture/contracts/platform-verification-app.md#example-record-and-createread-wire--proposed-2026-10-08)
uses one immutable labeled example, creation attribution, separate create/read permissions
and an account/org-scoped compact operation receipt. Cleanup retains retry evidence so
late retries cannot recreate deleted fixtures. This narrows WRITE's generic attribution
wording to creation-only for this immutable example under ADR-0025; mutable consumer
records still require update attribution. WRITE/REF/VERIFY share the same contract.
Payload/routes remain for discussion; exact storage/retention/bounds and readiness remain
open. No new story, runtime tests or application implementation; 24-item sequence remains.


Reference growth discussion — 2026-10-08: initial create/read is a first increment,
not the final reference scope. Proposed later editor, draft and immediate-preference
examples must distinguish ADR-0051 saving patterns; autosaved drafts have no Save button.
Recommend one internal verification/demo application, with real shared behavior and
separate manual versus automated fixtures. Additional scope/placement remains under
discussion; existing tests persist as regression coverage. No new story count or readiness
claim; see the reference contract's saving examples and demonstration role section.


Verification/demo role approved — 2026-10-08: one maintained app demonstrates the
three saving conventions and provides automated platform coverage, with separate manual
and automated fixtures. [Incremental placement proposal](../../platform/docs/architecture/contracts/platform-verification-app.md#incremental-example-placement--proposed-2026-10-08)
assigns draft examples to D2-B/D3/D4/D5 shared-artifact promotion, explicit Save editing
to the first E2 configuration writer, preference examples to their first real consumer,
and finalization only with E5. Initial REF/VERIFY remains create/read and independently
completable. Additional demo scope must be included in consuming-story sizing; no new
standalone count or implementation authorization. First Leave slice/readiness unchanged.


Reference example placement approved — 2026-10-08: incremental demonstrations join
their first proven consumer as proposed, with explicit sizing and no future dependency
for initial REF/VERIFY. Next [minimal draft example proposal](../../platform/docs/architecture/contracts/platform-verification-app.md#minimal-draft-demonstration--proposed-2026-10-08)
uses optional title/note, its own account/org ownership and explicit single-active scope,
plus existing autosave/close/discard protections. No Leave business fields or People
dependency. New draft capability registration and hosted checks occur only with their
consumer/cleanup readiness. 24-item sequence unchanged; no implementation or test runs.


## Current E1 contract checkpoint — 2026-10-08

The user approved the minimal reference draft demonstration. Reference scope is now
settled at the behavior level: one maintained test/demo application, initial create/read
then hosted verification, followed by shared-pattern examples with their first consumers.
There are 24 currently ordered E1 items. Do not reopen those decisions or imply that
reference checks replace actual Leave/PtS journeys. Preserve the first Leave draft slice.

This is a navigation checkpoint within existing BMAD planning, not another readiness
workflow, an exhaustive validation report or an implementation authorization.

| Remaining planning input | Owning contract and delivery items | Concrete next work |
| --- | --- | --- |
| Reproducible toolchain and generator inputs | Leave testing environment contract; ENV/P1/SERVICE | Supported compatibility set, lockfile ownership, generator input shape and exact owner commands; verify existing packages before choosing pins. |
| Identity/Access/People details | Identity, admission and controlled-provisioning contracts; ID-A/B, ACCESS-A/B, PEOPLE | Current identity-context endpoint proposal, provider/session verification, operator credential binding, owner projection privileges and exact migration/writer adoption. |
| Content and PtS adoption | Content ownership/read and PtS transition contracts; CONTENT-READ/PTS-ADOPT | Ownership DDL/mapping, file-auth adapter and revocation/races, range/headers and bounded transfer policy; target inventory and release rehearsal evidence distinguished from design. |
| Reference persistence and hosted operations | Platform verification contract; WRITE/REF/VERIFY | Final create/read wire, compact-outcome retention/retry policy, exact target/fixture/cleanup limits and deployment contracts. Minimal draft wire/lifecycle accompanies its approved later consuming increments. |
| Leave draft contract consistency | Leave draft persistence/recovery contract; CONTEXT/CHOICES/D1–D5 | Validate typed models, physical constraints and chronology against the already approved lightweight preservation, recovery and saving decisions; do not invent new draft business requirements. |
| Coverage and final sizing | Existing acceptance map and source-indexed inventory | Reconcile owner rows with reference demonstration work, finish granular requirements/UX traceability and ensure each story has only prior dependencies and bounded delivery scope. |

Design inputs must be resolved at their stated pre-story/readiness gates. Runtime
acceptance, deployed browser/provider behavior and migration/recovery proof are delivery
or activation evidence where the owning gate requires them; do not report them passed
from document inspection, or demand application implementation before authorization.
Architecture consolidation/review stays complete. Later epic contracts retain their own
gates rather than becoming speculative prerequisites for the first slice.

Next planning focus: reproducible ENV/P1/SERVICE inputs, starting with the repository's
actual package/configuration ownership. Make routine naming/document consistency choices
within approved scope; surface substantive alternatives for collaborative discussion.


Build ownership proposal — 2026-10-08: [working-tree inventory and PtS integration](../../apps/leave/docs/testing/e1-environment-and-dependencies.md#dependency-ownership-and-pts-integration--proposed-2026-10-08)
recommends including PtS/reference/Leave web in root npm workspaces and one root lock,
with coordinated deployment/test command adoption. User explicitly questioned retaining
PtS's separate lock; no architectural need for that split was established. Python owners
retain their own dependency locks; Access/Content stop depending on PtS requirements in
their owning stories. Version differences require compatibility evidence, not blind
alignment. Proposal only; 24-item sequence, first slice and readiness gates unchanged.


Frontend hosting clarification — 2026-10-08: shared npm workspace/lock does not
merge application deployments or authentication. User described the public Scribeswell
domain/separate hosting rationale and reopened a possible Boabab alias. Recommendation
remains public canonical scribeswell.com with PtS launcher access; optional alias would
redirect one way to it from the same Scribeswell deployment. Alias and platform suffix
remain discussion points, not accepted DNS changes. Existing combined-artifact manifests
need per-app publication reconciliation during delivery; no live routing claim or change.


Frontend build/hosting arrangement approved — 2026-10-08: shared npm workspace/root
lock includes PtS and new Reference/Leave frontends, while Scribeswell is separately
published publicly at scribeswell.com. No Boabab Scribeswell alias or redirect. Current
PtS account access controls only launcher visibility; it does not gate public reading.
[Publication target and owner mapping](../../apps/leave/docs/testing/e1-environment-and-dependencies.md#frontend-publication-target--approved-2026-10-08)
assigns workspace tooling to ENV and coordinated current-app publication adoption to
PTS-ADOPT/deployment, with affected Scribeswell checks. Final sizing/readiness remains
binding; 24-item sequence unchanged. No code, lockfile, hosting or DNS changes executed.


## E2 — Set up organization access, people and working arrangements

**Story planning resumed, 2026-10-08.** Platform naming exploration is parked; existing
identifiers/domains remain the planning baseline until a deliberate later decision.
E1's 24 agreed candidate scopes and first draft slice remain recorded. Their open
technical contracts, source-coverage reconciliation and final sizing remain binding;
starting E2 discussion does not mark E1 or Phase 1 ready/complete.

E2 goal: authorized administrators establish app access, shared employment and Leave
working arrangements without duplicating employee identity or granting unrelated access.
Sources: features Permissions, §1–3 and applicable §10/17; tracker Phases 2/3/5; spine
AD-1/2/3/5/12; platform role/access UX and Leave application-access/setup UX. Existing
scope includes invitations, roles, nullable shared assignments, profiles/schedules and
holidays. Discuss bounded stories sequentially; do not implement or pre-create every
entity. Preserve later employment/history/change-impact pre-story gates.

### Story 2.1: Enable or suspend Leave for an organization

**Scope approved by the user, 2026-10-11; not implementation-ready.** Owner: platform administration
UI/API and Access. Consumes E1 Identity, ACCESS-A/B, current organization-reference and
provisioning/evidence foundations. Ordinary organization administrators do not acquire
this authority. Exact admin capability/controller contract must be resolved first.

As a platform administrator authorized to manage application availability,
I want to enable or suspend Leave for a specific organization,
So that organizations use the applications assigned to them while retained data and
individual permissions remain intact.

**Acceptance Criteria:**

**Given** an authorized administrator and a current organization,
**When** they open that organization's application availability settings,
**Then** Leave's saved organization enablement and separate global availability are shown,
**And** permitted settings remain reachable even when that organization cannot enter
Leave. This administrative route must not require Leave employee access or employment.

**Given** Leave is globally available but disabled for this organization,
**When** the administrator reviews and confirms enabling it,
**Then** Access commits the organization enablement under current admin authority,
expected revision and duplicate-safe operation identity,
**And** no membership, employee, role or user grant is created. Only members with current
explicit Leave capabilities become eligible; unrelated organizations are unchanged.

**Given** Leave is enabled for this organization,
**When** the administrator reviews the suspension consequence and confirms disabling it,
**Then** new protected checks for that organization's Leave capabilities fail and current
discovery no longer offers that organization for Leave,
**And** drafts, employment and existing grants are retained. A short already-authorized
operation follows ADR-0021; queued/restarted/new execution cannot reuse old authority.
If the user has another eligible organization, their Leave launcher entry may remain.

**Given** the organization is re-enabled later,
**When** users enter Leave or reopen a saved draft,
**Then** current account, membership, capability and resource rules are checked afresh,
**And** revoked grants or retired memberships are not restored by re-enablement.
Retained draft data is available only to its currently authorized owner.

**Given** Leave is globally unavailable, the caller lacks platform management authority,
or a request substitutes another organization/revision,
**When** a UI or direct API request attempts a change,
**Then** global unavailability is not overridden by the organization setting and missing
management authority or stale expected state is rejected safely,
**And** being an organization administrator, employee or infrastructure operator alone
cannot grant this app-availability management authority or protected business-data access.

**Given** an edited setting has not been confirmed, or verification/persistence fails,
**When** the administrator cancels or receives a failed/uncertain result,
**Then** Cancel abandons only uncommitted changes and failed input remains recoverable,
**And** the UI never reports success from optimistic state alone. Resolve an uncertain
original operation before retrying; commit enablement, required immutable change evidence
and compact outcome together. Configuration uses whole-form Save/Cancel and the shared
Review/Confirm behavior, not field autosave or an administrative draft system.

**Given** the feature is delivered through ATDD/TDD,
**When** the owner records acceptance evidence,
**Then** tests prove current admin authority, wrong-org denial, revision/retry handling,
atomic audit failure, disable/direct-access/discovery behavior and valid re-enablement,
**And** actual restricted roles and real Access integration complement browser checks.
No planned fixture is reported as runtime evidence here.

**Traceability:** [features §1 and Permissions](../../apps/leave/docs/features.md),
[tracker Phase 2](../../apps/leave/docs/implementation-plan.md), spine AD-1/2/3/12,
platform ADR-0011/0012/0013/0019/0020/0021/0023/0025/0031/0035/0046/0053,
[shared saving convention ADR-0051](../../platform/docs/architecture/decisions/0051-saving-conventions-by-workflow.md),
[platform experience](../../platform/EXPERIENCE.md) and Leave application-access UX.
ADR-0046 reserves organization app enablement for platform administration; organization
role assignment is a following story. Global registry/availability administration,
account grants, membership invitations, role editors and billing are outside this item.

**Impacts and readiness:** Reuse Access-owned state/command/evidence semantics through
an explicitly authorized platform-admin HTTP controller; the browser receives no operator
or database credential. Keep migrations owner-local and API startup migration-free.
Promote proven admin form/review/status components and typed clients; count the agreed
minimal reference Save/Cancel demonstration in this first configuration consumer's sizing,
using its own fixture model/permissions rather than production Access state. Split that
increment explicitly before its consumer if concrete scope exceeds a single agent-sized
item. Update generated agent guidance only where new reusable usage requires it; existing
rules/accepted ADRs remain authoritative. Document admin authority, target scope, command
wire, concurrent global-disable behavior, audit fields and verification commands before
implementation readiness. No application code, grants, deployment or migration executed.


### Story 2.2: Assign Leave roles to an existing organization member

**Scope approved by the user, 2026-10-11, with supervisor-routing clarification; not implementation-ready.** Owner: shared
platform access-management UI/API and Access; Leave supplies its maintained role/catalog
metadata and resource rules. Depends on E1 Identity/Access/discovery/current member
projections and Story 2.1's availability foundation, not a later invitation/custom-role
editor. Existing members are provisioned by the approved earlier controlled commands.

As an organization administrator authorized to manage Leave access,
I want to review and change an existing member's Leave roles,
So that they have appropriate access without requiring me to configure technical
permission codes individually.

**Acceptance Criteria:**

**Given** current organization-scoped access-administration authority,
**When** I open Organization settings → People → member → Application access → Leave,
**Then** I see the exact target account/current membership, saved role assignments and
combined effective access for that organization,
**And** Leave settings can link to the same shared screen. Changing organization or
account clears prior protected context; person identity alone cannot combine grants
from separate accounts or memberships.

**Given** globally available Leave enabled for this organization and a current member,
**When** I choose from the maintained Employee, Approver and Leave Manager roles,
**Then** each has a short description and expandable plain-language capability summary,
**And** technical permission codes are not required in the normal flow. Multiple roles
may be selected; any assignment must fall within my actual management authority.
Leave Manager status alone does not grant general role administration.

**Given** proposed additions/removals,
**When** I save and review the change,
**Then** the review identifies the member/account, organization, added/removed roles and
resulting capability changes before confirmation,
**And** Cancel abandons uncommitted edits. No field-level autosave, administrative draft
system, role-name shortcut or client-supplied effective-grant list applies the change.
A newly assigned role cannot authorize the operation that assigns it.

**Given** current authorized confirmation and matching expected assignment/catalog state,
**When** Access commits the change,
**Then** role assignments, their effective permission consequences, required immutable
change evidence and compact operation outcome commit consistently under the owner,
**And** ordinary new authorization checks observe the result. Lost responses and matching
retries resolve the same operation rather than duplicating assignments/evidence.
Stale reviewed state must be refreshed and reviewed again, not silently overwritten.

**Given** two roles or another still-valid source provide the same permission,
**When** I remove one role,
**Then** only that assignment's contribution is removed and remaining legitimate access
is shown accurately,
**And** preserved scopes, domain appointments and resource rules remain binding. E1 direct
grants cannot disappear accidentally during adoption into role-backed administration;
legacy direct-grant/role mapping must be declared and tested before readiness.

**Given** Approver, Leave Manager or another role is assigned,
**When** the user performs an application action,
**Then** Leave still checks current capabilities, organization/resource scope and applicable
workflow rules; an Approver role alone does not authorize decisions on unassigned requests,
**And** separate sensitive-document/on-behalf permissions are not inferred from the role
name. Role administration grants no implicit right to inspect employee business records.
This story tests assignment effects using delivered protected paths/contract fixtures;
it does not implement later approval, balance or document workflows.

**Given** disabled Leave, retired membership, an accountless person, wrong organization,
missing assignment authority or unavailable current verification,
**When** I request or confirm an assignment,
**Then** the command rejects safely with the appropriate unavailable/denied/setup outcome,
**And** it cannot enable Leave, create accounts/memberships/employment, revive old grants or
assign roles by matching a display name/email. A person without an account has no login
membership to receive app access; their employment record remains independently valid.
Administrative state/retained assignments may still be read under separate authorized
management access when Leave is disabled; disabled app cannot be entered by this route.

**Given** browser and real Access/restricted-role fixtures,
**When** the story is implemented through the ATDD/TDD loop,
**Then** evidence proves default-role descriptions, explicit confirmation, combined grants,
removal with retained equivalent authority, stale-review/retry/audit handling and direct
API denial for wrong authority/org/membership,
**And** the actual target account is unambiguous even when multiple accounts share a person.
No executed tests or effective production changes are claimed in this planning draft.

**Traceability:** Features Permissions, Personas and §1; tracker Phase 2 role/capability
integration; spine AD-1/2/3/12; platform ADR-0011/0012/0013/0019/0020/0021/0023/0025/
0031/0035/0042/0046/0051/0053; Leave ADR-0012/0013/0082 resource/field boundaries;
[shared role-assignment UX](../../platform/EXPERIENCE.md#roles-and-permissions) and
[Leave access UX](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md#application-access-and-custom-roles).
Organization app enablement is Story 2.1. Invitations/membership retirement, account grants,
custom role creation/editing/deletion and acting-approver workflows are later independent
items, not dependencies for this default-role assignment boundary.

**Impacts/readiness:** Shared access owner supplies the one administration implementation;
Leave registers its catalog and links to it. Promote proven shared role picker, capability
summary and review/error controls; scaffold generates catalog/client integration rather
than copies of an access editor. Keep People employment facts outside authorization and
use HTTP across runtime owners. Existing agent instructions/accepted ADRs suffice; update
owner docs/runbooks and requirement-to-test mapping during delivery. Before readiness,
settle exact role/capability definitions, metadata/version upgrade policy, per-app delegated
assignment authority and escalation limits, current member/account projection, assignment
DDL/operation/revision wire and E1 direct-grant adoption. Size the UI plus owner-local role
persistence work explicitly; split prerequisite mechanisms before this consumer if needed.
No application code, migration, grants or deployment authorized or performed here.


## Supervisor replacement and approval-routing discussion — 2026-10-11

User asks whether Approver role assignment should automatically assign work and whether
supervisor replacement needs bulk editing or missing-route reporting. Story 2.2 remains
under discussion; this recommendation does not approve a new role/routing policy.

Existing authority: platform ADR-0041 and features §2/10 already make the shared supervisor
relationship available to Leave's configured Employee's supervisor step. Resolve an
eligible supervisor automatically on new submission and snapshot the assignment. The
Approver role supplies capability; it does not choose which employees report to a person
or assign every pending request. Other configured routes keep their own resolution rules.
The setup checklist already flags missing/invalid routes. Existing pending-request and
temporary-cover contracts require explicit authorized/audited reassignment and preserve
completed approvals. No accepted ADR replacement is needed for those existing behaviors.

### Recommended additional bounded convenience — for discussion

- Retain independent role assignment and relationship/routing configuration. Clarify
  Story 2.2's wording: an eligible configured supervisor is automatically resolved for
  new requests using that policy; simply selecting Approver is not a supervisor change.
- Propose a focused shared-employment Replace supervisor action: show employees whose
  current supervisor is the selected person, select the affected employees, choose an
  effective date and a replacement, review the exact set and confirm. Reuse authorized
  organization/person selectors, Save/Review/Confirm and per-item change evidence.
  No arbitrary bulk spreadsheet editor or generic cross-platform bulk-write engine.
- Shared People owns relationship history; Leave separately shows whether the replacement
  is eligible for the applicable routes and links authorized administrators to role/setup
  repair when needed. Supervisor change must never silently grant app permissions.
- Proposed E2 convenience scope covers changed relationships and future route resolution.
  Existing pending work remains assigned. With E5's protected reassignment capability,
  offer a separate review of selected outstanding steps to transfer with a reason; never
  silently move completed decisions or all work by changing a role or relationship.
- Use existing People/setup filters and status guidance for missing/invalid supervisor
  routes. Do not add a standalone report or fail draft preservation for that issue;
  unavailable checks remain unavailable, not confirmed missing configuration.

Example for discussion: twelve employees report to Pat; an administrator replaces Pat
with Sam effective 1 November. New supervisor-based routes resolve Sam when applicable
and eligible; existing pending steps stay with Pat until an authorized explicit reroute.
The employee count is illustrative, not a measured supervisor ratio or performance claim.

Pre-story inputs if adopted: scoped batch request/preview, exact employee selection and
expected revisions, effective-date/current-history rules, authorized actor/consumer and
replacement-reference validation, result/partial-failure/retry policy, transaction bounds
and E5 affected-request freshness/confirmation. All writes remain with their owner over
HTTP; no distributed transaction or UI list treated as current authority. Determine
single-owner atomic versus explicit per-item results with bounded batch size before
readiness rather than assume bulk update always succeeds together.

Scaffold/shared UI: promote proven selection/review/per-item feedback where domain-neutral;
People owns the supervisor-change command and Leave owns approval consequences. No new
agent-context rule or generic lifecycle. If approved, add the narrowly sized action to E2
employment story decomposition and E5 pending-work criteria, updating authoritative
feature/UX/contract references together. No new numbered story, implementation, readiness
completion or permission to mutate employment is implied by this discussion.


Supervisor convenience approved — 2026-10-11: user accepts the recommendation above.
Features §2/10 and shared/Leave UX now record selected Replace supervisor with effective
date/review, existing missing-route guidance and separately confirmed pending transfers.
Story 2.2's role assignment remains independent; supervisor-based new routes resolve
configured eligible supervisors automatically. Add the focused replacement action during
E2 employment decomposition and E5 pending-work coverage, with scoped batch/history/
impact contracts and concrete sizing. Accepted ADR-0041/0076 remain unchanged.

### Story 2.3: Create or duplicate an application-specific custom role

**Scope approved by the user, 2026-10-11; not implementation-ready.** Owner: shared access
administration UI/API and Access; Leave owns capability/default-role definitions. Depends
on completed Story 2.2's role catalogue/assignment and current authority foundations.
No dependency on later editing/deleting assigned custom roles or membership invitations.

As an organization administrator authorized to customize Leave access,
I want to create a named Leave role from selected business capabilities or duplicate
an existing role,
So that access fits my organization's responsibilities while remaining understandable.

**Acceptance Criteria:**

**Given** current authority to create custom roles for Leave in this organization,
**When** I open Advanced → Create custom role from Leave's access/settings context,
**Then** the editor inherits Leave and organization and starts with name, description
and unselected plain-language capabilities,
**And** no mandatory template/Start from choice, technical-code entry, cross-app bundle
or employment requirement is introduced.

**Given** a readable built-in or existing custom Leave role in the same authorized context,
**When** I choose Duplicate role,
**Then** a new unsaved role editor is prefilled with its capabilities and an editable name,
**And** the duplicate will be independent of its source. Its recorded source/version is
provenance, not a live inheritance link or authority to assign its permissions.

**Given** selected capabilities and a valid role name,
**When** I review and confirm creation,
**Then** the server verifies current create authority and assignable capability boundaries,
locks a versioned reviewed definition to explicit registered Leave capabilities, and
commits role identity/definition with required audit and operation outcome atomically,
**And** the role is visible in the existing assignment picker. It assigns nobody and grants
no permission until an independently authorized role assignment is confirmed through 2.2.
Repeated matching creation resolves to the same role; changed-payload/stale-source review
fails safely. Name uniqueness/normalization and typed field bounds are pre-story inputs.

**Given** Cancel, failed validation, lost response or unavailable verification,
**When** the editor handles that outcome,
**Then** Cancel abandons uncommitted edits, failed input remains available and an uncertain
command is resolved under its original identity before retry,
**And** no autosaved role/draft or success-shaped failure is introduced. Shared explicit
Save/Cancel and Review/Confirm apply with keyboard/focus/mobile behavior.

**Given** future capability additions or a later change to a duplicated source role,
**When** existing custom definitions are evaluated,
**Then** their explicit reviewed capability set remains unchanged until an authorized edit,
**And** no future-matching wildcard silently broadens access. The application remains owner
of built-in definitions; duplicating one never changes or deletes that built-in.

**Given** wrong app/organization, an unauthorized actor or a capability outside permitted
authority,
**When** direct API or UI creation is attempted,
**Then** the request is refused without protected role/holder information,
**And** a new role cannot bootstrap its creator's authority. Creating a role containing
Approver capability still does not establish a supervisor relationship or pending request
assignment; Leave resource/approval/document checks remain independent.

**Given** implementation through ATDD/TDD,
**When** acceptance evidence is recorded,
**Then** blank creation, independent duplication, assignment through completed 2.2,
capability boundaries, no silent future grants, concurrency/retry/audit atomicity and
safe browser failure behavior are verified,
**And** shared types, restricted-role tests and generated integration fixtures agree.
Mocks or planning text alone do not establish protected assignment or persistence.

**Traceability:** Features Permissions; tracker Phase 2 custom/default-role work; spine
AD-1/2/3/12; platform ADR-0011/0012/0013/0019/0020/0023/0025/0031/0035/0046/0051;
[shared role UX](../../platform/EXPERIENCE.md#roles-and-permissions) and
[Leave access/custom-role UX](ux-designs/ux-leave-2026-09-15/EXPERIENCE.md#application-access-and-custom-roles).
Editing assigned roles with holder-impact review and unassigned-only deletion are
following bounded stories; they are not prerequisites for creating/assigning a custom
role. Account-scoped PtS role management and cross-app bundles are outside this story.

**Impacts/readiness:** Implement one shared role editor and typed Access contracts;
scaffold registers app capability labels/catalogues and shared-control integration rather
than copying role administration into Leave. Catalogue/authority/definition/assignment
models introduced by 2.2 must already support the 2.3-created definitions; prove 2.2
using registered fixtures without requiring this later UI. Separate custom definition
history from effective grants and declare reference integrity, names/bounds, capability
selection/review revisions and duplicate operation semantics before readiness. Update
owner documentation/runbook and requirement-to-test evidence; existing agent rules and
accepted ADRs remain sufficient. Scope/sizing remains subject to concrete contracts.
No code, roles/grants, migrations, deployment or readiness pass performed.


Role-assignment entry-point question — 2026-10-11: Story 2.3 approved. User asks about
assignment on the “me view”; whether this means the target member detail or the signed-in
user's own profile is not yet explicit. Existing shared UX uses Organization settings →
People → member → Application access, with authorized links from application settings.
Recommend that member view as the main administration entry; an own-profile access
summary does not introduce self-service permission assignment. No UX/authority change
is approved from the ambiguous term alone.


Role-assignment drawer approved — 2026-10-11: shared desktop right-side drawer and mobile
full-screen sheet, invoked from member/application settings or role-holder list, with
explicit target context, review/confirm, unsaved-edit safeguards and return/focus behavior.
Features, shared UX and Leave UX are synchronized. This supplements Story 2.2, preserving
its current authority and account/membership boundary. It does not decide the earlier
ambiguous Me-page question or introduce self-service role grants. Role definitions use
a dedicated editor page. Shared drawer/form tests and scaffold integration are part of
the same delivery item; accepted ADRs and E1 readiness gates stay binding.

### Story 2.4: Review and apply changes to a custom role held by members

**Scope approved by the user, 2026-10-11; not implementation-ready.** Owner: shared Access
role administration and editor. Depends on completed 2.2 assignment and 2.3 role-creation
foundations; no later deletion screen, bulk supervisor action or approval UI dependency.

As an organization administrator authorized to edit a Leave custom role,
I want to review the capability changes and affected holders before applying an edit,
So that I understand how access will change for everyone holding that role.

**Acceptance Criteria:**

**Given** current role-edit authority for Leave in the organization,
**When** I open a custom role's editor,
**Then** its saved name, description, explicit capabilities and current holder information
are available on the dedicated page,
**And** built-in roles remain application-maintained. Editing a duplicate changes only
that custom definition; it does not change its source role or another organization's role.

**Given** proposed capability additions/removals,
**When** I proceed to review,
**Then** I see added/removed capabilities in plain business language, the number of current
holders with authorized expandable names, and an explicit statement that the change
applies to all holders,
**And** the review explains that removing a contribution may leave equivalent access from
another role or still-valid scoped appointment. Definition changes do not retire members,
change employment/supervisors or automatically reroute pending approval requests.

**Given** current holders shown during review,
**When** I open one holder's application access,
**Then** the shared assignment drawer opens with the exact account/membership, organization
and Leave context while preserving the originating editor's local edits and position,
**And** on return current holders/effective access are refreshed. No later role-deletion
feature is needed to prove this contextual navigation. Browser refresh/closure need not
preserve unconfirmed administration input.

**Given** a reviewed definition and affected-holder state,
**When** I explicitly confirm,
**Then** Access verifies current edit authority and allowed capabilities plus expected
role/catalog/holder-impact state before committing the versioned definition and its
required audit/compact outcome consistently,
**And** all applicable current holders receive the new role contribution on subsequent
checks. Changed review state requires refreshed impact and a new review; the browser
cannot silently adopt new revisions and confirm again. Retain historical role meaning.

**Given** another role provides a retained capability or another holder receives a scoped
appointment,
**When** this custom role's contribution changes,
**Then** independent authority is evaluated accurately without overwriting unrelated grant
sources or treating absent capability as a deny rule,
**And** existing application resource/self-approval/document constraints still apply.
Already-authorized short execution follows ADR-0021; new action checks use current state.

**Given** Cancel, validation failure, denied authority, unavailable required verification,
or a lost response,
**When** the editor handles the result,
**Then** unconfirmed edits never grant permissions; Cancel abandons only those edits,
failed input remains recoverable, and uncertain confirmation resolves the original
operation before retry,
**And** unchanged replay produces no duplicate role version/change event. Missing required
local audit/outcome aborts the mutation; diagnostics contain no raw payloads or secrets.

**Given** new application capabilities introduced later,
**When** an existing custom role is evaluated or opened,
**Then** its saved reviewed set is retained and new capabilities are visibly selectable
only through a new authorized edit,
**And** no wildcard or application role upgrade silently broadens a custom definition.
No capability beyond the editor's management authority can be added through direct API.

**Given** initially failing acceptance and real owner integration,
**When** the story is built and verified,
**Then** holder-impact review, retained equivalent grants, drawer return, stale/concurrent
role or assignment changes, safe retry and cross-org/API refusal have evidence,
**And** an assigned synthetic role proves the effective change through current Access,
not just a saved editor value. Real Leave domain checks retain their own later acceptance.

**Traceability:** Features Permissions; tracker Phase 2 shared custom-role lifecycle;
spine AD-1/2/3/12; platform ADR-0011/0012/0013/0019/0020/0021/0023/0025/0031/0035/0051;
[shared role lifecycle](../../platform/EXPERIENCE.md#roles-and-permissions), shared
administrative Edit/Review/Confirm and Leave application-access/custom-role UX.
Unassigned-only role deletion is the following independent item; member invitations and
bulk supervisor replacement are separate E2 work. No cross-app role bundles or app
capability definition editor is introduced.

**Impacts/readiness:** Reuse the one shared role editor/review/assignment drawer and typed
clients; promote proved holder/context/conflict controls through shared UI. Scaffold
registers role metadata/client integration, never copied app-local role administration.
Before readiness, declare role-version/holder-set observations and commit serialization,
source-preserving effective-grant evaluation, per-app edit/escalation authority, event/
outcome shape and name/bound constraints. If active application workflows can be affected,
resolve their mandatory impact/freshness contracts before activating such edits against
those workflows; do not assume removing eligibility silently transfers work. Define
bounded commit/read timings without external waits under locks and compatible owner
migrations. Record owner docs, commands and source-to-test evidence; update generated
agent guidance only if proven usage requires it. Existing accepted ADRs remain unchanged.
No role edits, code, migration, deployment or readiness pass performed.


### Story 2.5: Delete an unassigned custom role while preserving its history

**Scope approved by the user, 2026-10-11; not implementation-ready.** Owner: shared Access
role administration. Depends on completed 2.2–2.4 role assignment/definition/holder review.
No employee invitation, organization directory, supervisor replacement or later approval
workflow UI is needed to prove this boundary.

As an organization administrator authorized to delete a Leave custom role,
I want to remove an unused role and resolve any assignments that block deletion,
So that the role catalogue stays manageable without silently changing people's access
or losing historical evidence.

**Acceptance Criteria:**

**Given** a custom role in my authorized organization/application,
**When** I open its deletion action,
**Then** current holders and deletion eligibility are checked and shown,
**And** application-maintained built-in roles cannot be deleted through this UI or API.
No implied authority follows from being able to read a role.

**Given** a custom role has current assignments,
**When** deletion is requested,
**Then** it is blocked with an explanation and authorized links to the holders' application
access drawers, already scoped to exact account/membership, organization and Leave,
**And** removing/replacing those assignments uses the existing independently confirmed
2.2 action. Do not offer a delete-and-revoke-everyone shortcut. Suspended app admission
is not evidence that retained assignments are absent; historical retired assignments
are distinguished under the owner lifecycle contract.

**Given** I follow a holder link to resolve an assignment,
**When** I return to the role page,
**Then** invoking context/position and supported local unconfirmed role-editor input are
preserved and holders/eligibility refresh,
**And** a previously empty list is not reusable deletion authority. Assignment failure
cannot be presented as completed cleanup. No cross-account or cross-org context leaks.

**Given** a custom role is currently unassigned and deletion is permitted,
**When** I confirm its clearly identified deletion with reviewed revision/operation identity,
**Then** Access atomically verifies role/assignment state and current authority, retires
the role from active selection and commits required immutable evidence/compact outcome,
**And** its stable identity, historical definitions and past access-change references are
retained. Delete removes the active custom-role choice; it does not erase historical
attribution or reuse the identity for a new role.

**Given** a concurrent assignment or role edit occurs after the deletion review,
**When** deletion is confirmed,
**Then** stale state is refused and requires a refreshed review,
**And** shared database/transaction guards ensure that either the valid assignment wins
and blocks deletion, or deletion wins and the assignment cannot attach the retired role.
An old creation/edit/assignment retry cannot resurrect a deleted role or its authority.

**Given** confirmation response loss, repeated delete, Cancel, denied authority or outage,
**When** the client resolves that result,
**Then** matching committed retries return the original compact result without repeated
history/effects; Cancel changes nothing; uncertain outcome is checked before retry,
**And** the interface never claims deletion from an empty screen or optimistic state.
New read/actions recheck current authority before disclosing role/history information.

**Given** initially failing acceptance and real restricted-role Access integration,
**When** the story is delivered,
**Then** tests prove assigned-role/built-in denial, drawer return and refreshed eligibility,
concurrent assign/delete/edit ordering, retained history and duplicate-safe deletion,
**And** wrong application/organization/actor cannot delete or enumerate protected holders.
Planned test cases are not executed evidence here.

**Traceability:** Features Permissions; tracker Phase 2 custom-role lifecycle; spine
AD-1/2/3/12; platform ADR-0011/0012/0013/0019/0020/0023/0025/0031/0035/0046/0051;
[shared role lifecycle UX](../../platform/EXPERIENCE.md#roles-and-permissions) and Leave
application-access/custom-role UX. Current unassigned-only deletion is authoritative;
history/retirement implements that UX without adding a restore screen or deletion of
shared person/account/membership records.

**Impacts/readiness:** Reuse shared confirmation, holder-link drawer and safe retry/status
controls; scaffold promotes verified role lifecycle/client fixtures rather than copied
administration. Before readiness, specify role retirement and assignment FK/write guards,
which retained/suspended assignments block deletion, reviewed revision/holder state,
command/outcome retention, immutable history privileges and compatible owned migrations.
Resolve every supported alternate assignment/edit path, not just the visible drawer.
Keep external verification outside locks and bounded local commit behavior. Update owner
runbook/types/source-to-test mapping; existing agent context/accepted ADRs remain binding.
No roles, grants, code, database or deployment changed by this story proposal.


### Story 2.6: Invite a person to join an organization securely

**Scope approved with ADR-0057 onboarding clarification, 2026-10-11; not implementation-ready.** Owner: shared
Identity membership/invitation administration and its UI/API; provider/deployment owner
supplies the selected invitation delivery/sign-in integration. Consumes E1 actor/person/
account/membership/recovery and restricted authority foundations plus the earlier E2
member/access navigation. Exact invitation transport and recipient-binding contract must
precede readiness; do not assume an invitation endpoint is already implemented.

As an organization administrator authorized to invite members,
I want to invite a specific recipient and see the invitation's status,
So that people join the correct organization through a deliberate verified process.

**Acceptance Criteria:**

**Given** current organization-scoped invitation authority,
**When** I prepare an invitation for a recipient and review/confirm it,
**Then** the invitation binds the exact organization, intended recipient and inviter,
**And** its durable creation, required audit/operation result and required delivery intent
are recorded under the owning contract. Recipient/account existence is not disclosed
through an unauthenticated public lookup. No person/account merge is inferred from email.

**Given** an issued invitation and supported provider delivery,
**When** the invitation is presented or delivery fails,
**Then** the administrator sees truthful pending/accepted/expired/cancelled and delivery
failure information as applicable, with a supported retry/resend action,
**And** a durable invitation is not called delivered or accepted merely because local
creation succeeded. Resend/replacement and old-link validity have explicit bounded,
duplicate-safe semantics; do not manufacture a fresh membership on an email retry.

**Given** the intended recipient follows a valid invitation,
**When** they sign in through the approved identity-provider flow and accept,
**Then** the server verifies current invitation validity, recipient/account binding and
organization admission before creating or recognizing the exact membership,
**And** possession of a copied invitation URL or a matching unverified email alone does
not authorize a different account. An account can already belong to other organizations.
Show the invited organization clearly before acceptance; wrong-account recovery uses
existing session/account-isolation handling, not automatic account/person relinking.

**Given** acceptance is repeated/concurrent, the recipient is already a member, or they
previously left,
**When** membership creation is resolved,
**Then** the current active membership is not duplicated or replaced, and a legitimate
rejoin follows the earlier membership-history/predecessor guard with a new membership,
**And** old invitation/create retries cannot retire or replace that new membership.
Retain historical membership/employment references and do not restore old roles/grants.

**Given** an expired/cancelled/superseded invitation, unavailable verification or changed
organization/account state,
**When** acceptance is attempted,
**Then** the request fails safely with clear expired/invalid/denied/unavailable recovery,
**And** no membership is acknowledged from optimistic UI or stale positive verification.
Cancellation invalidates the invitation; after acceptance, ending membership is a
separate authorized lifecycle action, not retroactive invitation cancellation.

**Given** an invitation is accepted,
**When** membership is confirmed,
**Then** no employment record or Leave/PtS capability is created automatically,
**And** authorized administrators can use completed 2.2 role assignment for the new member.
The member receives an honest next-step/access state rather than an unauthorized Leave
page. A new login account, if necessary, follows the configured provider/invitation
onboarding policy; this feature does not enable general public signup for protected apps.
Account-to-existing-person/employment linking remains separately verified, not inferred
from invitation acceptance or an employee name.

**Given** acceptance/creation response loss, a repeated admin command or audit failure,
**When** the owner resolves the command,
**Then** current authorized outcome lookup and same-operation replay prevent duplicate
invitations/memberships and required local audit/outcome failure aborts its mutation,
**And** provider delivery waits occur outside business write locks. No distributed
transaction with email/provider/account creation is claimed; confirmed local stages
remain recoverable and failure cannot be presented as overall completed onboarding.

**Given** initially failing acceptance and actual supported provider/Identity integration,
**When** implementation evidence is recorded,
**Then** intended/wrong-account, expired/cancelled/duplicate/concurrent acceptance, existing
member/rejoin, cross-org authority, provider failure and current permission checks pass,
**And** token/recipient data remain out of logs and ordinary error payloads. Use isolated
synthetic users/controlled recipients; no invitation is sent during planning.

**Traceability:** Features §1 authorized invitations and Permissions; tracker Phase 2
secure invitation/onboarding; spine AD-1/2/3/4/12; platform ADR-0002/0012/0013/0019/0020/
0021/0022/0023/0025/0031/0032/0035/0042/0046/0056; Identity membership/account separation
and shared administrative saving/account-switch UX. Shared employment creation/linking,
initial role selection within an invitation and membership retirement screens are
separate items; no later People directory or custom-role screen is needed to accept.

**Impacts/readiness:** Define provider compatibility with Entra/Supabase, authenticated
inviter authority, recipient verification, invitation token/lifetime/storage/reissue/
revocation bounds, exact acceptance/membership state and actor setup, audit/outcome/
outbound-intent schema, and controller/recovery wire before delivery. Select and size
actual invitation delivery foundation now; do not assume a future E3 notification service
or introduce a new general inbox merely to invite someone. Earlier E3-first business
notification planning does not waive this required E2 provider/invitation dependency.
Scaffold/shared UI promotes proven invite/status/identity-recovery components with the
first consuming implementation; owner docs/configuration and test traceability update
together. Existing agent rules/accepted ADRs remain sufficient; no generated server
imports or cross-owner table access. No code, invite, account, migration or deployment
executed; implementation readiness remains pending.


Invitation versus provider sign-in clarification — 2026-10-11: user accepts the core
invitation story but questions whether SSO users need invitations. Authentication via
configured Entra/Supabase does not inherently require an application invitation; invited
members still use that provider to authenticate. Organization membership remains a
separate authorized admission under ADR-0002/0042 and features §1. Invitation is one
admission path, not the mandatory login path or a replacement for authentication when
no provider is configured. Earlier owner-controlled authorized membership provisioning
continues to permit membership without an emailed invitation.

Recommendation for discussion: retain ordinary Microsoft sign-in and explicit authorized
membership/role provisioning; use an invitation when a recipient needs organization
onboarding. A future trusted provider-tenant/group mapping could perform authorized
automatic membership provisioning, but a generic Microsoft login or email domain cannot
imply organization admission. Tenant-managed identity-provider configuration, trust/mapping,
join/leave/rejoin and role synchronization require a separately scoped contract under
ADR-0002's revisit clause. Do not silently add Graph/SCIM synchronization or auto-grants
to Story 2.6. No broad automatic-admission policy is accepted from this question alone.


## Organization onboarding policy refinement — proposed 2026-10-11

User asks whether invitations should be the only normal onboarding option without a
configured tenant provider, and whether tenant setup should offer automatic onboarding.
Recommend yes for ordinary organization onboarding UI:

- With no verified organization-to-provider tenant mapping, invite-and-accept is the
  normal onboarding route. Do not add an ordinary Add verified account bypass screen.
- After a trusted tenant mapping is saved and verified by an authorized administrator,
  explicitly offer Enable automatic onboarding for this tenant? with the current default
  remaining off. Review the exact organization, trusted tenant and permitted audience
  before enabling. A provider configuration save must never enable it implicitly.
- With automatic onboarding off, retain invitations. With it on, eligible authenticated
  identities may acquire current organization membership under the declared policy;
  membership still creates no employment or privileged app role by itself.
- Disabling automatic onboarding stops new automatic joins; it does not retire existing
  memberships. Provider authentication, current membership and app authorization remain
  independently enforced. New access to other organizations is never implied.

Existing restricted owner setup/migration/bootstrap commands remain necessary for the
already approved E1 foundations and deliberate adoption. They are not a normal onboarding
UI escape hatch or public API; preserve their operator authority/audit contracts. This
narrows the earlier recommendation for routine admin provisioning rather than removing
all administrative database setup authority.

The refinement is for discussion, not an accepted tenant-configuration/automatic-join
feature. If approved, settle explicit tenant trust verification, issuer/subject/tenant
claim binding, guest/external account treatment, auto-join audience and join/rejoin/
revocation lifecycle; do not rely on email-domain matching. Microsoft sign-in is already
the MVP provider, but tenant-managed enrollment is additional scope under ADR-0002's
revisit clause. Size provider mapping/auto-onboarding separately from the invitation
story, record any accepted architecture change in a linked ADR, and update authoritative
feature/UX contracts only once the direction is approved. No Graph/SCIM group-sync
engine, implicit role import or automatic permission grant is added by this proposal.

Scaffold/shared UI: explicit optional enrollment policy and reviewed setup prompt only
when implemented; normal invitation/profile/access components remain. Agent-context/docs/
ADR impact must be dispositioned with adoption; accepted ADRs are unchanged. E1 first
slice and all pre-story/implementation-readiness gates remain binding. No application
code, accounts, invitation, provider configuration or live deployment changed.


Onboarding policy approved — 2026-10-11: [platform ADR-0057](../../platform/docs/architecture/decisions/0057-invitation-onboarding-and-trusted-tenant-enrollment.md)
records invitation-only normal onboarding until trusted tenant verification and separate
opt-in enrollment, without changing the Entra/Supabase provider or granting app roles.
Features and shared UX/agent context reflect the bounded scope amendment. Invitation
2.6 remains independently completable while automatic enrollment is off. Tenant setup
and automatic join are split into separate increments to preserve bounded delivery.

### Story 2.7: Verify a trusted Microsoft Entra tenant for an organization

**Scope approved by the user, 2026-10-11; not implementation-ready.** Owner: shared
Identity configuration/controller and existing Supabase/Entra integration. Consumes
E1 identity/current authority and 2.6 invitation fallback. Automatic join is the following
story; setup must work with enrollment remaining off and does not depend on that story.

As an administrator authorized to configure an organization's identity connection,
I want to verify the Microsoft Entra tenant trusted for that organization,
So that tenant-based onboarding can later be enabled deliberately for the right users.

**Acceptance Criteria:**

**Given** current configuration authority for the exact organization,
**When** I open identity-connection settings,
**Then** I see the saved Entra tenant and its verification state plus that automatic
onboarding is off in this increment,
**And** the screen uses the retained shared Supabase/Entra integration, not a different
provider broker or direct browser access to configuration secrets.

**Given** proposed tenant details,
**When** I save and complete the declared verification/control-proof flow,
**Then** the server establishes the exact trusted tenant/issuer binding using supported
provider evidence and current administrator authority,
**And** an email suffix or tenant ID typed into a field alone cannot mark it verified.
Configuration, actor/time and required local outcome/audit are recorded consistently.
Actual proof protocol/provider feasibility must be selected before story readiness.

**Given** verification is incomplete, fails or becomes unavailable,
**When** the screen reports its state,
**Then** it distinguishes not configured, verification pending/failed and couldn't check,
with appropriate safe retry/guidance,
**And** no automatic admission occurs. Existing authorized invitation onboarding remains
available and failure never silently enables enrollment or maps an unrelated tenant.

**Given** verification succeeds,
**When** the saved connection is displayed,
**Then** its organization and tenant identity are clear and enrollment stays off,
**And** no membership, employment, role or app grant is created. The following opt-in
story adds the approved Enable automatic onboarding prompt/confirmation; this setup
story is accepted against verified configuration with no unfinished join dependency.

**Given** tenant details are replaced, stale reviewed state is submitted, or a wrong-org
caller attempts a change,
**When** the configuration operation is resolved,
**Then** current authority/revisions and verification provenance are protected and changed
bindings require fresh verification,
**And** current accepted memberships are not reassigned/deleted by this setting. Define
mapping replacement/revocation and any later enrollment shutdown effects before exposing
those transitions; saved verification cannot survive an unchecked tenant replacement.

**Given** lost response, matching retry or required local audit failure,
**When** setup confirms its result,
**Then** the original operation is resolved without duplicate bindings/evidence, and a
failed required local commit cannot be reported as saved,
**And** provider waits occur outside database write locks. Failed/uncertain confirmation
retains safe input and existing reviewed-change UX; no provider secrets/claim dumps in
logs, browser state or return URLs.

**Given** authorized delivery with isolated tenant/account fixtures,
**When** tests exercise successful/failed verification and cross-organization authority,
**Then** evidence proves actual issuer/tenant verification, stale/retry handling and no
implicit joins or roles,
**And** existing invitation/Entra sign-in and independent PtS account access regressions
remain protected. No real provider configuration is changed during planning.

**Traceability:** Features §1 and ADR-0057 scope amendment, tracker Phase 2 onboarding;
spine AD-1/2/3/12; platform ADR-0002/0012/0013/0019/0020/0022/0023/0025/0031/0042/0057
and shared organization-onboarding/admin UX. Supabase/Entra remain authoritative.
Arbitrary providers, Graph/SCIM synchronization, automatic membership admission and
role import are outside this item. Account/person/employment remain separate.

**Impacts/readiness:** Define actor/admin authority, organization/provider configuration
owner/schema, real proof flow, provider tenant/issuer/subject/audience validation and
secret/credential handling, callback bounds, verification expiry/change policy and
compatible configuration activation/recovery before readiness. Size actual provider
setup separately if evidence shows multiple implementation items are needed. Shared
UI/scaffold promotes proven connection/status/review/error contracts; no copied app
identity-provider implementation. Owner docs/types/runbooks and acceptance links update
with delivery; generated agent guidance follows ADR-0057. Accepted predecessors stay
immutable. No application code, invitation, accounts, DNS, provider config or deployment.


### Story 2.8: Explicitly enable automatic onboarding from a trusted tenant

**Scope approved with advance-access clarification, 2026-10-11; not implementation-ready.** Owner: shared
Identity admission policy/controller and existing provider integration. Depends on
completed Story 2.7 verification, 2.6 invitation fallback, E1 account/actor/membership
history and completed current Access/role-assignment boundaries. No role import,
People employee administration or directory synchronization dependency.

As an administrator authorized to manage organization onboarding,
I want to explicitly enable automatic joining for an approved trusted-tenant audience,
So that eligible users can join when signing in without individual invitations.

**Acceptance Criteria:**

**Given** a currently verified tenant mapping and current onboarding-management authority,
**When** its setup completes or I open onboarding settings,
**Then** I am offered Enable automatic onboarding for this tenant? with default off,
**And** review names the exact organization, trusted tenant and eligible audience and
explains that membership creates no employment or application roles. Cancel or saving
provider details alone leaves enrollment off. Only supported verified audience policies
can be selected; exact guest/group eligibility is a pre-story contract, not a permissive
fallback or an implicit Graph/SCIM integration.

**Given** I explicitly confirm enabling against current reviewed mapping/policy state,
**When** Identity commits the policy change,
**Then** current authority and tenant verification are rechecked under the declared bounds,
with guarded revision, required local audit and compact operation outcome,
**And** future eligible joins may use that exact policy. No existing accounts/memberships
are created in bulk and no permissions are imported from tenant roles or JWT claims.

**Given** a newly authenticated eligible account from the configured trusted tenant,
**When** the explicit post-authentication admission workflow executes for this organization,
**Then** it verifies current account/provider identity, issuer/tenant/subject/audience,
current verified policy and membership history before creating a membership,
**And** repeated/concurrent login callbacks produce at most one current membership.
Plain context/list/read endpoints cannot provision membership as a side effect.
Email/domain/name matching cannot merge person/accounts or choose another organization.

**Given** an account already has a current membership,
**When** automatic onboarding executes again,
**Then** it recognizes the existing membership without replacing its ID or roles/grants,
**And** no duplicate enrollment event or employment record is created. Separate accounts
linked to one person remain separately admitted and permissioned; tenant identity does
not imply admission to every organization with a similar domain.

**Given** the account previously had membership retired/removed,
**When** it signs in under an otherwise eligible automatic policy,
**Then** this proposed initial behavior requires deliberate authorized rejoin rather than
silently recreating membership,
**And** rejoin uses a new membership and explicit predecessor/current-state guards, with
no restoration of old grants. This closes the removal-bypass risk for discussion; exact
retired/excluded-account rules must be approved and represented before readiness.

**Given** wrong tenant, unsupported/ambiguous eligibility, unverified/changed mapping,
disabled policy or unavailable current verification,
**When** automatic admission is attempted,
**Then** no new membership is granted and the existing invitation/recovery route is offered
where permitted,
**And** failure is distinct from denial. Mapping replacement cannot reuse old verified
status/enrollment consent. Define verification-revocation and policy-off/in-flight commit
ordering so stale callbacks cannot create memberships after the permitted boundary.

**Given** onboarding is enabled,
**When** an authorized administrator reviews/confirms turning it off,
**Then** new automatic joins stop under the declared current-state execution boundary,
**And** existing memberships, grants, employment and drafts are retained. Normal current
access and provider authentication still govern those accounts; account/org access
revocation remains its separate explicit action. Invitations remain usable as permitted.

**Given** joining succeeds but no app role has been assigned,
**When** the user returns from sign-in,
**Then** the shared entry presents honest membership/access-pending next steps,
**And** direct Leave APIs/discovery still enforce global/org enablement, current capability
and resource rules. The user is not shown an authorized Leave page solely from membership.
No fake employment or automatic Employee/Approver/Administrator role is created.

**Given** retries, response loss or required audit/outcome failure,
**When** policy changes or enrollment resolve,
**Then** same-operation results prevent duplicate memberships/evidence, failed required
local evidence prevents its mutation, and uncertain results use the existing lookup/retry
contract,
**And** provider waits occur outside short business locks. Verified human initiator and
service executor attribution are recorded where applicable; no raw claims/credentials
in outcomes, URLs or diagnostic logs. No distributed provider/database transaction.

**Given** initially failing acceptance and real supported provider/Identity/Access fixtures,
**When** the item is delivered,
**Then** evidence proves default-off, explicit enable, valid/wrong-tenant eligibility,
concurrent callback, current-member preservation, removed-member protection, policy-off/
mapping-change races and no implicit app grants,
**And** invocation tests are scoped to synthetic accounts/organizations and actual sign-in
configuration, not an authentication bypass. No running checks are claimed here.

**Traceability:** Features §1/ADR-0057 scope amendment; tracker Phase 2 invitation/
onboarding; spine AD-1/2/3/4/12; platform ADR-0002/0012/0013/0019/0020/0021/0022/0023/
0025/0031/0032/0035/0042/0046/0053/0056/0057; shared organization-onboarding and reviewed
administration UX. Supabase/Entra remains the provider; arbitrary providers, group/directory
sync, employment creation and automatic role grants are outside the item.

**Impacts/readiness:** Define exact policy schema/controller/actor authority, verified
identity evidence transport through Supabase, supported audience and guest/external
rules, mapping uniqueness/organization selection, explicit admission invocation and
provider observation validity. Complete removed/excluded account and deliberate rejoin
rules, short commit/disable ordering, operation/audit/history retention and owner-local
constraints before readiness. Resolve automatic account actor/profile setup through the
existing Identity contract; no unauthorized read-side bootstrap. Promote proven typed
admission client and setting/status/recovery UI with scoped fixtures; scaffold does not
make auto-join the default for every app. Update owner docs/runbook and source-to-test
links; agent guidance follows ADR-0057. Scope may split on concrete provider/policy work
before declaring the item agent-sized. Accepted ADRs are unchanged. No accounts, policy,
provider, app code, schema or deployment modified by planning.


## Administrator-prepared access before first sign-in — proposed 2026-10-11

User asks whether an administrator can establish membership/roles while preparing employee
access instead of waiting for sign-in. Recommend supporting explicit advance preparation:
existing current organization members already receive role assignments through 2.2;
for a person not yet admitted, prepare the intended admission/role assignments and bind
activation to verified identity and the approved onboarding route. Keep automatic tenant
membership enrollment distinct from explicit administrator-approved app-role grants.

For the unconfigured-tenant or enrollment-off case, normal onboarding remains a pending
invitation with intended roles prepared by an authorized actor. Those intended grants
are pending until the recipient/account binding and membership acceptance are verified;
no Add member bypass or immediate email-based grants. For trusted enabled tenant enrollment,
prepare access for a verified tenant principal, activating only against the correct current
platform account/membership under the declared enrollment policy. A current verified
account can use the earlier completed assignment mechanisms as its admission is resolved;
a never-signed-in person must not require a fabricated Auth account or person/email merge.

Pending intended access must name exact organization/application, reviewed roles/catalog
state, verified target identity/recipient binding and approving actor/authority evidence.
Activation rechecks pending approval validity, onboarding/tenant state, membership history,
role definitions and assignment boundaries; role changes after review require the owning
fresh-review policy. Revoked invitations/pending approvals or retired membership cannot
silently reactivate old roles. Separate owner commits have honest partial status/recovery;
no distributed Identity/Access/People transaction is claimed. Multiple accounts linked to
one person cannot receive each other's intended grants implicitly.

This is a proposal to add a bounded administrator-preparation/activation story following
2.8, consuming invitation and assignment foundations; it is not an accepted amendment
to ADR-0057 or an implemented feature. If accepted, link a refining ADR for pending explicit
assignment and any admin-preenrollment allowance, update authoritative UX/requirements,
and resolve provider-identity evidence, pending role storage/activation/review/history and
recovery contracts before readiness. No Graph/SCIM directory sync assumed; a targeted
provider lookup, if selected, is its own explicit prerequisite. No app roles arise from
being a tenant user or employee alone. Story 2.8 remains under discussion.


Advance-access direction approved — 2026-10-11: [platform ADR-0058](../../platform/docs/architecture/decisions/0058-administrator-prepared-access-before-first-sign-in.md)
records explicit administrator-prepared roles before first sign-in, activated only against
verified admission/current assignment state. This clarifies 2.8's no automatic roles:
previously confirmed explicit preparation may activate, while tenant enrollment itself
selects no role. Features/shared UX/agent context are synchronized; detailed activation
contracts remain open and no accepted predecessor ADR was edited.

### Story 2.9: Prepare and activate application access before first sign-in

**Scope approved with automatic-activation clarification, 2026-10-11; not implementation-ready.** Owner: shared Access
pending assignments/UI, with Identity admission/target verification HTTP integration.
Depends on completed 2.2 role assignment, 2.3–2.5 role lifecycle and 2.6–2.8 onboarding.
People employment does not need to exist; no later employee-management UI dependency.

As an organization administrator authorized to assign Leave roles,
I want to prepare a recipient's application access before their first sign-in,
So that their reviewed roles can become active when verified onboarding completes.

**Acceptance Criteria:**

**Given** current assignment authority and an intended recipient identified under the
approved target contract,
**When** I open the shared member/application access drawer and select roles,
**Then** I can review/confirm the exact organization, application, recipient/login identity
and intended role definitions before platform account/membership completion,
**And** the saved result is Pending onboarding with no effective grants. A person name,
employee record or entered email alone cannot establish the activation identity.

**Given** the recipient already has the verified account and current membership,
**When** access is prepared,
**Then** existing 2.2 assignment applies immediately under its current checks,
**And** a redundant pending preparation or extra invitation is not required for an already
admitted member. No rights are copied from another account linked to the same person.

**Given** pending preparation and a valid invitation or enabled trusted-tenant admission,
**When** the intended recipient completes verified onboarding,
**Then** Identity establishes/recognizes the exact current membership and Access activates
only the separately approved roles after validating target, approval/policy and reviewed
role state,
**And** the result becomes Active only after the actual assignment commit. No fake Auth
account, automatic employment or unsolicited default role is created. Wrong-account/
wrong-tenant acceptance cannot consume the intended assignment.

**Given** revoked invitation/preparation, retired/replaced membership, disabled app or
changed/deleted role definition,
**When** pending activation is evaluated,
**Then** stale approval cannot silently attach to a replacement account/membership or
activate a different capability set; the status and authorized next steps are explicit,
**And** changed review-dependent state requires renewed review under its owner contract.
Onboarding success may stand while app access is still Pending/Needs review; do not roll
back another owner's committed membership or claim full Leave access prematurely.

**Given** a pending approval is no longer wanted,
**When** an authorized administrator confirms withdrawal,
**Then** future activation is prevented with required evidence/current-state guards,
**And** active access is revoked only through the existing assignment action. Withdrawal
versus activation concurrency cannot report successful prevention after grants committed.

**Given** callback/delivery retry, repeated activation or a lost response between owners,
**When** the same prepared action is resolved,
**Then** each owner uses its scoped operation evidence to prevent duplicate membership,
assignments and audit, and recovery reports the actual committed stages,
**And** required dependency verification failures keep access pending without positive
cache fallback or a broad service credential. Provider/external waits are outside locks.

**Given** initially failing acceptance and real Identity/Access integration,
**When** the item is delivered,
**Then** evidence proves pre-sign-in preparation, correct/wrong recipient activation,
review-state conflict, withdrawal/activation race, rejoin safeguards and cross-owner
partial recovery,
**And** both prior human approval and service execution are attributed without retaining
credentials or invite-link payload dumps. Actual Leave entry after activation still
checks current app/resource/employment rules in its own stories.

**Traceability:** Features §1/Permissions and ADR-0058 amendment; tracker Phase 2 secure
onboarding/role assignment; spine AD-1/2/3/4/12; platform ADR-0011/0012/0013/0019/0020/
0021/0022/0023/0025/0031/0035/0042/0046/0056/0057/0058; shared assignment-drawer and
advance-access UX. Normal invitation-only admission and default-off trusted enrollment
remain. No account-scoped PtS grant preparation or identity-directory sync is included.

**Impacts/readiness:** Specify owner-local pending assignment schema/target references,
provider recipient evidence and account binding, expected membership predecessor/current
state, role-version/authority approval and activation review policy, expiry/withdrawal,
operation retention and restricted activation identity before readiness. Define each
HTTP handoff and atomic local effect with safe per-stage outcomes and bounded retries;
no distributed transaction or generic onboarding workflow engine. Reuse tested drawer/
role review/status controls and typed activation clients; scaffold promotion occurs with
the first proven implementation. Update owner docs/runbooks, agent guidance links and
source-to-test fixtures. Include exact invocation/state/retention/provider feasibility in
single-agent sizing; split a concrete prerequisite before this consumer if needed.
Accepted ADRs remain unchanged. No actual roles, accounts, invitations, code or deployment.


Advance-access activation clarified/approved — 2026-10-11: the user confirms automatic
activation of previously explicitly approved roles once verified target/admission and
current approval/role checks pass. No second routine administrator confirmation is
needed in the unchanged valid case; relevant changed state remains Pending/Needs review.
This implements ADR-0058, not automatic default roles for every tenant account.

### Story 2.10: Remove a member's organization access without erasing history

**Scope approved with membership clarification, 2026-10-11; not implementation-ready.** Owner: shared
Identity membership administration UI/API with current Access/Directory consumers.
Consumes E1 membership retirement guards, earlier E2 member/role/onboarding views and
2.8–2.9 retired-member/pending-activation protections. No employee-termination command
or future approval-management UI dependency.

As an organization administrator authorized to manage membership,
I want to remove a member's access to this organization,
So that they cannot continue organization-scoped actions while existing business and
employment history is preserved.

**Acceptance Criteria:**

**Given** current membership-management authority and an exact active account/membership,
**When** I open Remove from organization,
**Then** review clearly identifies the account, organization and affected organization-
scoped access and explains that employment/history are retained,
**And** this action is distinct from removing one app role, disabling the Auth account,
ending employment or disabling an app for the whole organization. Another account linked
to the same person is not silently removed by an account/membership-scoped operation.

**Given** reviewed current membership state and authorized confirmation,
**When** Identity commits removal with expected revision and operation identity,
**Then** it retires that exact membership with required audit/compact outcome atomically,
**And** new protected organization checks and discovery use the retired state immediately
under the declared ADR-0021 boundary. Existing token claims/open forms cannot preserve
new execution authority; short already-authorized execution retains its bounded rule.
No cross-owner grant deletion is needed to make retirement effective.

**Given** saved drafts, historical requests/decisions, actor attribution and employment
belong to that organization,
**When** the membership is retired,
**Then** those records and stable references remain intact under their owner retention,
**And** future reading still requires current resource permission. Retention does not
promise the former member continuing access. Employment does not end automatically.
Independent account-scoped PtS access and memberships in other organizations remain
subject to their own unchanged authorization.

**Given** an automatically enrolled or previously invited member is removed,
**When** a later sign-in, stale invitation, pending-role activation or callback is replayed,
**Then** it cannot silently recreate membership or reactivate the retired membership's
grants under the completed 2.8/2.9 lifecycle rules,
**And** deliberate authorized re-admission creates a new membership with new reviewed
role assignments, never copies old roles simply because the person/account returned.

**Given** a delayed removal retry and a newer replacement membership,
**When** the original operation is resolved,
**Then** it targets/returns its original membership result and cannot retire the replacement,
**And** concurrent retirement/rejoin/assignment is guarded by owner constraints and current
expected state. Required local audit/outcome failure aborts the removal; lost response
uses current authorized recovery of the original operation without an extra retirement.

**Given** a removed member has approval responsibilities when such workflows exist,
**When** dependent current checks or required workflow-impact handling execute,
**Then** the person cannot perform new decisions through the retired membership and
outstanding requests retain their snapshots/completed decisions,
**And** any transfer is an explicitly authorized application-owned reroute. Define and
verify the existing missing/replacement-approver flags and affected-work contract before
activating removal against those workflows. This story uses synthetic contract fixtures;
E5 owns actual queue/notification/reroute integration, not a future dependency here.

**Given** wrong organization/account/membership, stale review, missing authority or outage,
**When** removal is attempted through the UI or direct API,
**Then** it fails safely without exposing unrelated member/business records,
**And** Cancel abandons uncommitted input, relevant current-state changes require review,
and the interface cannot claim access removal from optimistic UI. Define last-owner/
organization-administration continuity guards and supported self-removal before readiness;
do not silently invent a universal administrator or lockout recovery permission.

**Given** initially failing acceptance with actual Identity/Access/Directory integration,
**When** the story is delivered,
**Then** retirement/direct-action/discovery denial, retained history, independent account
access, wrong-org API refusal and stale retry versus rejoin are verified,
**And** actual restricted database roles and alternate writers preserve the membership
lifecycle. No production user or membership is altered by this planning story.

**Traceability:** Features §1 current/ended membership checks; tracker Phase 2 suspension/
authorization; spine AD-1/2/3/4/12; platform ADR-0002/0012/0013/0019/0020/0021/0022/
0023/0025/0031/0035/0042/0046/0052/0053/0057/0058; Identity membership-retirement/rejoin
contract and shared reviewed-administration UX. Shared employment ending/correction,
account-wide disabling, app-wide suspension and application pending-work rerouting remain
separate owning actions with their existing contracts.

**Impacts/readiness:** Reuse existing retirement command through explicitly authorized
membership-admin HTTP; browser gets no operator/DB credentials. Promote proven exact-
membership review/conflict/recovery controls and scoped Identity/Access fixtures; shared
scaffold retains application/account versus organization separation. Complete current
member/admin projections, continuity/self-removal policy, role/pending binding invalidation,
retirement/rejoin ordering and protected dependent-work contracts before readiness.
Keep owner-local short transactions, safe attribution and migration compatibility.
Update owner docs/runbook, generated client and requirement-to-test evidence; existing
agent rules/accepted ADRs remain sufficient. No implementation, membership, grants,
accounts, schema or deployment changed.


Membership re-admission clarification approved — 2026-10-11: a fresh membership is a
new account-to-organization access record. Reuse verified login/person and preserve the
enduring employment relationship, periods and domain history. Administrator-facing
Re-admit does not require managing database IDs; old roles require deliberate new
assignment, and delayed old commands cannot affect the replacement membership.

### Story 2.11: Add an employee with an initial employment period

**Scope approved with person/employment wording clarification, 2026-10-11; not implementation-ready.** Owner: shared People
employment administration and Identity person references through HTTP contracts. Consumes
E1 shared person/employment/provisioning/read foundations and established E2 administration
surfaces/authority. No later work-profile/policy editor, department/location catalogue,
supervisor replacement or login invitation is required to save this minimum employee.

As an administrator authorized to maintain employment in this organization,
I want to add a person as an employee with their initial employment dates,
So that their employment is recorded once and can be used consistently by Leave and
other authorized applications.

**Acceptance Criteria:**

**Given** current employment-administration authority for the selected organization,
**When** I open Add employee,
**Then** I can select a permitted verified existing person reference or create the required
person identity through its owning contract, and enter the initial start date plus an
optional end date,
**And** the form shows organization/person context and does not require a login account,
invitation, app role, work profile, department, location or supervisor to save employment.
Name/contact/profile field bounds and permitted person lookup/create scope must be
settled before readiness; no cross-organization people enumeration is introduced.

**Given** an existing person/account/member is selected,
**When** employment is created,
**Then** the existing verified person ID is reused rather than creating a Leave employee
identity copy,
**And** account linkage remains verified. Equal name/email or a supplied employee ID alone
cannot merge people or bind another person's account; ambiguous matches require explicit
resolution under Identity's verified-linking contract.

**Given** valid initial dates and reviewed confirmation,
**When** People commits the organization/person relationship and initial period,
**Then** one enduring employment relationship and one nonoverlapping inclusive period
are saved with stable identities, relationship revision, server actor/UTC attribution,
required change history and compact operation outcome under the owner,
**And** optional end is null or at/after start; equal start/end is one valid day. Enforce
organization/reference/date invariants at both API and database boundaries. No Auth
account, membership, role or Leave draft is created by the employment write.

**Given** the person already has employment in this organization or concurrent creates race,
**When** creation is requested,
**Then** database/API integrity prevents duplicate relationships and presents the existing
permitted record or a safe conflict without overwriting it,
**And** a return to employment uses a later period under the same employment ID, not a
second employee record. Employment in another organization remains independent and is
not disclosed to an unauthorized administrator.

**Given** the employee has no login account or application access yet,
**When** the record is viewed after saving,
**Then** the employee record is valid and account/access status is shown truthfully,
**And** authorized navigation may lead to completed invitation/advance-access flows.
This is a next step, not automatic onboarding or proof of employee-only participation;
no proxy unpaid acknowledgement or other employee-confirmed action is enabled.

**Given** work/approval settings have not been configured,
**When** Leave reads the new shared employee,
**Then** its domain setup status may identify required remaining work without invalidating
saved shared employment,
**And** preserve the accepted lightweight draft rules. Shared location is not a work
profile and saving employment cannot invent schedules, timezone, holiday or entitlement
values. Domain effective-status interpretation uses the approved explicit date contract,
not an assumed UTC today for missing input.

**Given** new person creation commits but a later People save fails or a response is lost,
**When** the UI recovers the operation,
**Then** it reports/reuses the verified created person and actual employment stage without
duplicating identity, deleting another owner's committed person or claiming full success,
**And** matching employment retries resolve their original result. Required People local
history/outcome failure aborts its local relationship/period change. External owner calls
and validation occur outside write locks; there is no distributed Identity/People commit.

**Given** Cancel, invalid dates, changed expected state, denied authority or outage,
**When** confirmation is handled,
**Then** shared whole-form Save/Cancel and Review/Confirm behavior preserves useful failed
input and safe exact-target context, with no hidden field autosave,
**And** a typed error cannot leak raw person data/credentials or silently become absence.
No stale revision substitution or unverified person-header fallback is allowed.

**Given** initially failing acceptance and actual Identity/People/restricted-role integration,
**When** the item is delivered,
**Then** linked/accountless creation, duplicate/concurrent relationship, inclusive dates,
cross-org refusal, server attribution/history and staged recovery have evidence,
**And** consumer HTTP fixtures prove no duplicate employee master and no access implied
by employment. Real Leave work/profile/calculation features keep their own acceptance.

**Traceability:** Features §2 shared employment/accountless support and §1 access separation;
tracker Phases 2/3; spine AD-1/2/3/5/12; platform ADR-0012/0013/0014/0017/0018/0019/
0020/0022/0023/0025/0031/0035/0040/0041/0042/0051/0056/0058; shared employment contract
and Leave Employment & approval settings UX. Employment changes/end/rehire, optional
assignment management and Leave-specific settings are following bounded stories.

**Impacts/readiness:** Define minimum Identity profile/lookup/create authority and People
employment-create API/transaction, stable references, date/bounds/operation/revision schemas
and actual restricted read/write/RLS/migration privileges before readiness. Identity global
profile fields and People organization facts keep separate owners; no app HTTP bypass or
cross-owner table access. Resolve authorized initial historical/future date creation and
any applicable consequential impact constraints before activating against existing data.
Promote proven person/date/create/review/status controls and typed clients; scaffold adds
opt-in employment integration, not a mandatory HR dependency for every app. Document
creation recovery, authority and source-to-test commands; existing agent rules/accepted
ADRs suffice. No employee/account/role, code, schema or deployment changed in planning.


Employee wording clarified/approved — 2026-10-11: Select an existing person, or add the
person and their employment in this organization. Identity owns the reusable person,
People owns organization employment and Leave owns its domain settings. Organization
settings → People can expose shared administration; no standalone HR app or new login
record is implied. The person may have multiple organization employment relationships.

### Story 2.12: Record an employment end date with reviewed consequences

**Scope approved by the user, 2026-10-11; not implementation-ready.** Owner: shared People
employment administration, with consuming Leave impact contracts. Depends on completed
2.11/E1 employment/revision/history and earlier current access foundations. Scope is
setting/revising the end of the identified current/future period; correcting unrelated
historical periods and adding a rehire period are separate items.

As an administrator authorized to maintain employment,
I want to record the employee's last employment date and review applicable consequences,
So that future application actions use the correct employment boundaries while history
and organization-access decisions remain explicit.

**Acceptance Criteria:**

**Given** current employment-management authority for an exact organization/relationship/
period,
**When** I edit its last employment date,
**Then** the start/current end date and applicable dates are clear,
**And** the end is inclusive, not before start, and cannot overlap another retained period.
Use date-only values and the owner relationship revision; do not confuse end of employment
with organization membership removal or account disablement.

**Given** a proposed end date and declared consumer-impact contracts,
**When** I proceed to review,
**Then** I see the exact dated change and consequences available for currently delivered
consumers, with a required explanation for affected consequential Leave changes,
**And** required impact verification unavailable/changed state prevents claiming complete
review or silently confirming stale effects. Do not hold business locks while reviewing
or waiting on external services. The end-date/consumer-freshness coordination contract is
mandatory before this writer is ready against consequential consumers.

**Given** current reviewed state and authorized confirmation,
**When** People commits the period change,
**Then** it preserves the enduring employment/period identities and dated history, advances
the relationship revision and commits required audit/change evidence and operation outcome,
**And** provider/consumer coordination uses bounded owner HTTP contracts without distributed
transaction claims. Repeated original confirmation cannot duplicate history or dependent
effects. Changed current/end/related impact state requires fresh review.

**Given** a last employment date of 30 June,
**When** Leave later evaluates submission/final approval dates,
**Then** 30 June remains eligible under normal rules and any requested date after 30 June
is rejected under Leave ADR-0049,
**And** existing affected requests retain their dates/decisions and are flagged with the
administrator explanation for authorized correction/cancellation. No automatic trimming,
approval reroute or cancellation. Actual request/approval UI arrives in E5; this story
uses explicit consuming-contract fixtures without depending on that later UI.

**Given** grants/balances are present when the change becomes applicable,
**When** Leave applies its approved entitlement impact rules,
**Then** proration/no-proration and deficit/explanation behavior follow Leave ADR-0048,
with immutable correction evidence and duplicate-safe dependent effects,
**And** approved leave is not silently changed to unpaid. Calculations/correction workflows
remain E3/E6; their first consuming writers must integrate/prove this employment-impact
contract before activation. The E2 item does not fake those undeveloped calculations or
claim completeness merely because the People date saved.

**Given** employment is ended for Leave's effective employee-local date,
**When** an otherwise authorized employee returns to a saved draft,
**Then** the agreed ended-employment read-only behavior preserves input/history,
**And** membership/roles and other app rights remain governed separately. Ending employment
does not implicitly retire membership, remove independent PtS access or create a new
person/employee. Authorized next steps can link to completed membership removal if desired.

**Given** Cancel, invalid dates, missing authority, outage or lost response,
**When** the form resolves its outcome,
**Then** explicit Save/Cancel and Review/Confirm preserve uncommitted failed input; Cancel
cannot reverse a committed change, and uncertain confirmation resolves its original
operation before retry,
**And** server-derived attribution and safe typed errors expose no private payload dumps.
Missing local required history/outcome prevents the local change from committing.

**Given** initially failing acceptance and actual People/restricted-role/HTTP fixtures,
**When** this item is delivered,
**Then** inclusive boundaries, scoped date constraints, concurrent revisions, history/retry,
wrong-org authority and honest impact-outage handling have evidence,
**And** E1 Leave draft read-only integration remains covered. Later consequential consumers
supply their real request/balance/notification tests in their own stories; no mock output
is claimed as those features working.

**Traceability:** Features §2, employment/draft rules in §7 and entitlement departure rule;
tracker Phases 2/3/6; spine AD-1/2/3/5/6/12; platform ADR-0012/0013/0019/0020/0022/0023/
0025/0031/0035/0040/0042/0044/0051; Leave ADR-0023/0048/0049/0094/0112/0113 and employment
settings/administrative-impact UX. App permissions, membership retirement, rehire and
historical correction remain independent workflows; shared location/work profile stays
separate from employment boundaries.

**Impacts/readiness:** Define exact period mutation and relationship revision guards,
current/future versus historical edit bounds, reason/impact schemas, authorized read/write
scope, version/validity/affected-consumer handshake and bounded recovery/event delivery
before readiness. Preserve already approved short transactions and owner-local migrations;
no unbounded external waits or automatic cross-owner rollback. Shared UI/scaffold promotes
proven dated review/conflict/history/client mechanisms; Leave eligibility/entitlement stays
in Leave. Update owner docs/runbooks and exact source-to-test evidence; existing agent
rules/accepted ADRs remain authoritative. Size dependent foundation work explicitly before
this consumer; no incomplete impact contract is waived to make the story smaller. No
employment, access, code, migration or deployment changed by planning.


### Story 2.13: Record a return to employment without replacing the employee

**Scope approved by the user, 2026-10-11; not implementation-ready.** Owner: shared People
employment administration and consuming application clients. Depends on completed 2.11
relationship/period setup, 2.12 period-end administration and E1 effective reads/history/
current-access foundations. Reuse earlier membership/role onboarding when separately
needed; adding an employment period does not depend on a new identity provider.

As an administrator authorized to maintain employment,
I want to record a returning employee's new employment period,
So that employment continuity and prior history remain understandable without creating
a duplicate person or employee.

**Acceptance Criteria:**

**Given** a permitted existing person/organization employment relationship,
**When** I open Record return to employment,
**Then** I see the retained periods and can enter a new start date and optional end date,
**And** the form clearly reuses the person and employment identity. An open/overlapping
existing period must be resolved through its authorized date-change action first;
recording return cannot silently shorten or rewrite an old period.

**Given** valid reviewed date-only values and current authority,
**When** I confirm the new period,
**Then** People adds one stable new period under the same employment ID, advances the
relationship revision and commits required history/attribution and compact outcome,
**And** inclusive nonoverlap is database-enforced across all periods. Starting the day
after a prior end is valid; sharing the prior end date overlaps. A supplied end may be
null or at/after the new start. No copied employee master or overwritten original period.

**Given** concurrent returns, repeated confirmation or response loss,
**When** the command is resolved,
**Then** expected relationship revision and scoped operation identity prevent duplicate
periods or competing overlapping writes,
**And** a matching committed replay identifies its original period/result. Changed-input
replay or changed periods require safe conflict/fresh review, not a new implicit create.

**Given** the new period is future/current for the explicitly requested effective date,
**When** an authorized application reads the shared relationship,
**Then** it returns that date's correct effective period/state and retained revision,
**And** a date in the intervening gap is not treated as continuous employment. Derived
current/future/ended states remain date-based, not independently edited flags; consumer
work timezone/entitlement rules stay with the application.

**Given** prior Leave history, settings and an active preserved draft,
**When** the returning employee has current required access and resumes Leave,
**Then** Leave reuses the preserved records/draft with fresh shared and local context,
**And** invalid obsolete selections follow the existing notice/preservation contract.
Submitted/discarded drafts are not resurrected and a return does not fabricate balances,
reset ledger history or silently replace work profiles/policies. Consequential date/
entitlement impact follows the existing E3/E5/E6 contracts when those consumers exist.

**Given** the person's organization membership remains active or was previously retired,
**When** the employment return is recorded,
**Then** no membership/login/role change is implied: still-valid access is checked normally,
and retired membership requires the earlier deliberate re-admission with new reviewed grants,
**And** accountless returning employees remain supported. Employment return is not proof
of employee authentication or an employee-only acknowledgement.

**Given** required impact checks are unavailable, review-dependent state changes, input
is invalid, or the actor lacks authority,
**When** Save/Review/Confirm is attempted,
**Then** no stale/unauthorized period change is acknowledged and failed input is preserved
under shared administrative conventions,
**And** cancellation does not reverse an already committed result. Required local evidence
failure aborts the local mutation; external waits remain outside write locks.

**Given** initially failing acceptance and actual People/Access/restricted-role fixtures,
**When** the item is implemented,
**Then** same-employee rehire, gap/effective-date interpretation, inclusive constraints,
concurrent revision/retry/history and separate admission behavior have evidence,
**And** E1's real draft-resumption contract remains protected. Later entitlement/request
features own their full domain regression tests and cannot claim continuity from mocked
shared reads alone.

**Traceability:** Features §2 enduring employment/period history and §7 rehire draft behavior;
tracker shared employment and draft integration; spine AD-1/2/3/5/6/8/12; platform
ADR-0012/0013/0019/0020/0022/0023/0025/0031/0033/0035/0040/0042/0049/0051/0057/0058;
Leave ADR-0023/0094 and approved employment/settings UX. Membership re-admission,
account linking and historical date corrections remain their separate owner actions.

**Impacts/readiness:** Declare exact period-add request/result, date/bounds/revision guards,
current/historical effect policy and applicable consumer impact/freshness coordination
before readiness. Specify how explicit employment periods feed each application's tenure/
anniversary/proration rules without guessing a universal restart of service; earning in
a gap must not be inferred from one continuous start/end pair. Prove owner constraints,
restricted roles and transactional history through the shared read/command fixtures.
Promote reusable period/date/history/conflict/status controls and typed clients; scaffold
retains opt-in employment and no cross-owner table access. Update owner docs/runbooks,
agent usage guidance where needed and requirement-to-test links; accepted ADRs unchanged.
No employee/login/membership/roles, code, migrations or deployment changed by planning.


### Story 2.14: Maintain simple organization departments and locations

**Scope approved with simple Create/Save/Cancel behavior, 2026-10-11; not implementation-ready.** Owner: shared People
organization-reference administration. Consumes completed E1/2.11 shared employment and
current organization/admin foundations. Employee assignment follows this catalogue story;
fixture references can prove lifecycle behavior without a later assignment UI dependency.

As an administrator authorized to maintain organization employment references,
I want to create, rename and archive departments and locations,
So that employees can use consistent optional organization records across applications.

**Acceptance Criteria:**

**Given** current authority for the organization,
**When** I open its Departments or Locations settings,
**Then** I see only authorized records and active/archived state, with create/edit actions
when permitted,
**And** a missing catalogue is an honest empty state while failed retrieval is unavailable.
These settings use People-owned records, not a separate Leave employee master.

**Given** a proposed department or location name and declared optional metadata,
**When** I choose Create/Save,
**Then** People stores a stable identity and exact organization/type with server attribution,
required change evidence and duplicate-safe outcome,
**And** the declared scoped naming/uniqueness rules apply in the database and API. The
same label in another organization never selects that other organization's record.
No default Unknown sentinel or mandatory catalogue entry is created.

**Given** a permitted saved record,
**When** I explicitly save a rename against its current revision,
**Then** its stable identity and references remain while the new name and required history
are recorded,
**And** historical reference/label evidence is preserved under the declared version/read
contract. Do not rewrite historical employee/workflow attribution to imply a different
organizational placement; exact label/history representation precedes readiness.

**Given** a department/location is no longer used for new placement,
**When** I review and confirm archiving it,
**Then** it is unavailable for new ordinary assignments while authorized existing references
and history remain resolvable,
**And** referenced employees are not silently moved or cleared. Show affected existing
references where authorized, with normal future reassignment links when that UI exists.
Archive is not cascading employee/period deletion or membership revocation.

**Given** employee data or future Leave consumers refer to the record,
**When** its name/state changes,
**Then** nullable placement and current scope rules remain intact,
**And** existing Leave work profiles, schedules, timezone, holidays, overrides and approval
snapshots are not silently changed. A location reference is organizational placement;
application settings remain application-owned under ADR-0041.

**Given** wrong organization, missing authority, invalid input, stale revision, Cancel,
response loss or dependency outage,
**When** a mutation is attempted,
**Then** whole-form Create/Save and Cancel apply for simple creation/rename, with a separate
explicit confirmation for archive where its impact is shown; safe typed errors/current
revision checks and same-operation recovery prevent duplicate records/change events,
**And** required local evidence failure aborts the mutation. No hidden field autosave,
raw payload logging, cross-owner writes or positive authorization fallback.

**Given** initially failing acceptance and real restricted People persistence,
**When** delivery records its evidence,
**Then** scoped catalogue lookup, create/retry/concurrent uniqueness, rename/history,
archive/reference preservation and direct API wrong-org/authority cases pass,
**And** fixture employment references prove invariants without depending on later employee
assignment UI or claiming full Leave policy/calendar integration.

**Traceability:** Features §2 optional shared departments/locations; tracker Phase 2
organization structure/shared employment; spine AD-1/2/3/5/12; platform ADR-0012/0013/
0019/0020/0022/0023/0025/0031/0035/0040/0041/0051; shared reference/admin/date UX and
Leave Employment & approval settings. Team management retains its separate existing
scope; no tree hierarchy, chart builder, Graph import or generic HR suite is introduced.

**Impacts/readiness:** Define catalogue fields/bounds/naming semantics, stable scoped
keys/revisions, nullable assignment references and historical label/retirement contracts,
restricted read/write API and current admin authority before readiness. Reuse focused
create/edit drawer on desktop/full-page mobile and explicit shared saving/review controls;
People owns the domain command, shared UI promotes proven generic catalogue presentation.
Scaffold adds opt-in typed reference lookup/edit fixtures, not tables to every application.
Update owner docs/runbook/source-to-test evidence; existing agent rules/accepted ADRs
suffice. Bound supported reference reads/impact review and keep external waits outside
transactions. No department/location, employee, code, schema or deployment changed.


Department/location saving clarification — 2026-10-11: user asks whether direct autosave
without drafts would be better. Recommendation retains accepted ADR-0051 whole-form
explicit saving for shared business configuration. Simple catalogue create/rename needs
one Create/Save action plus Cancel, not an added review screen. Archive retains explicit
consequence confirmation. Unconfirmed text stays local while the form is open; no
server-side administrative draft or typing-time committed rename is needed. This refines
the unapproved Story 2.14's overbroad Review/Confirm wording without changing the accepted
saving convention. Direct personal preferences and autosaved request drafts retain their
separate patterns. The story remains under discussion; no implementation.


### Story 2.15: Assign or clear an employee's department and location

**Scope approved with immediate-save/bundled-load simplification, 2026-10-11; not implementation-ready.** Owner: shared People
employment placement administration with authorized consuming UI. Depends on completed
2.11 employment identity and 2.14 scoped catalogues/history, plus E1 current authority.
No later supervisor/profile/holiday configuration or general bulk editor dependency.

As an administrator authorized to maintain employment placement,
I want to set or clear an employee's department and location when I save,
So that organizational placement stays accurate and historically understandable across
applications without forcing every employee into a department or location.

**Acceptance Criteria:**

**Given** an exact permitted employee relationship in the current organization,
**When** I open its placement settings,
**Then** a single form-load response supplies current employee placement with its labels,
permitted department/location choices, expected employment revision and applicable edit
authority; explicit Unassigned choices and retained change history are available where
authorized,
**And** selectors offer only permitted records from that organization. Accountless employees
are supported; no login/member role is required merely to record employment placement.

**Given** selected department/location or Unassigned values,
**When** I explicitly Save against current reviewed relationship/assignment state,
**Then** the change takes effect on save; People records server-controlled effective UTC
time, preserves earlier references/history and advances
the appropriate owner revision with actor/UTC attribution, required change evidence and
compact operation outcome,
**And** each field has one current value, including null. Record who changed what and
when under the existing effective-history contract; no user-selected effective date,
future schedule or retroactive placement-edit UI is included. Exact current/history
schema and revision aggregate remain pre-story inputs.

**Given** a saved placement change and later catalogue rename/archive,
**When** permitted current/history views read it,
**Then** the current assignment and recorded historical references remain interpretable,
**And** current edits do not silently rewrite old history. Event/effective timestamps are
server-managed evidence, not a scheduling form or independent mutable status.

**Given** an existing archived department/location or an unavailable lookup,
**When** the employee form is opened or another field saved,
**Then** retained references remain visible/resolvable and unchanged values are not silently
cleared; new assignments reject archived or wrong-org targets under the owner contract,
**And** current archived selections remain included for display even when absent from new
selectable choices. If required form data cannot load, show the form-level load failure
and Retry instead of an editable incomplete form. Unassigned means verified null only;
clearing is an explicit user choice confirmed by Save, not a load/cleanup side effect.

**Given** either field is unassigned,
**When** the employee or authorized application reads it,
**Then** the employment record remains valid and authorized filters can select Unassigned,
**And** no Unknown sentinel record or missing-setup blocker is invented for placement.
Employee list/detail can show and filter the current department/location within allowed
scope using the shared collection-filter conventions; no separate reporting module.

**Given** department/location changes,
**When** Leave consumes shared employment,
**Then** its saved work profile, schedule, timezone, holiday calendar, policy overrides and
historical calculations remain unchanged unless a separate authorized Leave action applies,
**And** placement alone grants no business-data/app access and reroutes no pending approval.
Any allowed initial-profile suggestion is presentation under Leave's explicit setup rules,
not an automatic reassignment from this People write.

**Given** stale assignment/catalogue state, wrong org, missing authority,
Cancel, response loss or dependency outage,
**When** the command is resolved,
**Then** explicit whole-form Save/Cancel with appropriate current-impact confirmation
prevents hidden field writes, and safe typed errors preserve useful local input,
**And** uncertain commands use original scoped outcomes before retry. Same-input replay
creates no duplicate assignment/history; changed reviewed state requires fresh review.
Required local evidence failure aborts the local mutation; external waits are outside locks.

**Given** initially failing acceptance and actual People/scoped restricted-role fixtures,
**When** the item is delivered,
**Then** null/accountless assignment, saved change history, concurrent updates, archived and
wrong-org reference handling, history/retry and read/filter privacy have evidence,
**And** existing Leave profiles/overrides are proven unchanged through the delivered
integration contract. Real later work-profile/calendar domain behaviors retain their own
acceptance; no mocked client result is claimed as their implementation.

**Traceability:** Features §2 nullable department/location/history and independent work
profiles; tracker Phase 2 shared employment/structure; spine AD-1/2/3/5/12; platform
ADR-0012/0013/0019/0020/0022/0023/0025/0031/0035/0040/0041/0042/0051; shared collection/
reference/date/admin UX and Leave Employment & approval settings. Team assignments,
supervisor changes and Leave work-profile assignment are separate following work.

**Impacts/readiness:** Complete current nullable assignment/read and server-recorded effective
history, cross-org reference constraints, archived-retained-versus-new selection rules,
exact field/name bounds,
permission/projection, bounded composed form-load response and owner revision/operation
contracts before readiness. Define
actual consuming-impact constraints where shared location is used for policy eligibility;
no user scheduling/backdating or automatic work-profile change is included. Future
historical placement correction needs separate scope. Promote proven optional reference/filter/
conflict/status controls and typed HTTP clients, using a focused drawer/full-page mobile
form; the backend is People, not direct Leave table updates or imported service code.
Scaffold adds opt-in integration/fixtures; owner docs/runbooks/source-to-test commands
update together. Existing agent rules/ADRs remain binding. No assignment, employee, code,
DDL or deployment modified by story planning.


Placement simplicity clarification — 2026-10-11: user challenges user-entered effective
dates, reference archiving and unavailable-versus-null handling. Recommend immediate
application on Save with server-recorded who/what/when history, removing future-date/
backdate UI from unapproved 2.15. Accepted ADR-0041's historical reference requirements
remain; effective history does not require an administrator date picker. Department is
used for organization calendar/list filters; features also include location eligibility
and location-aware calendar applicability. Work profiles still own actual schedules,
timezone and holiday assignments; define the shared-location policy mapping/impact with
its first consumer rather than assume automatic calculation changes.

Archive retains stable references in current/past employment and policy/configuration
where applicable, not because every department drives a calculation. A referenced record
must not disappear or silently clear employees; new selection stops while history resolves.
No new purge engine or generalized time-travel interface is introduced. A minimal future
hard-delete path for truly unreferenced records is not required for this story.

Lookup example: Ana's saved location ID points to Maputo. If the location service call
fails, show Location could not be loaded with Retry and preserve that ID. Rendering
Unassigned and saving it would erase a valid assignment. If the server successfully
returns location_id=null, Unassigned is correct. Failure to load replacement choices
likewise must not reset saved selection or get persisted as null. This is ordinary
error-safe form behavior, not an additional user workflow. Candidate remains discussed;
no new accepted ADR or implementation.


Small catalogue/form-loading preference — 2026-10-11: user prefers a simple active/
archived flag where practical and asks whether department/location options should be
included in the employee load. Recommend one form-specific browser API request returning
current placement labels/IDs plus authorized small scoped option lists and record revision.
Do not add separate per-field calls or a partial-load recovery workflow for this form.
If required data fails, report the whole form-load error and Retry; only verified null
means Unassigned. Include archived current choices for display, without making them
selectable for a new assignment.

The UI-owning API composes HTTP calls to owners when necessary; People bundles its own
placement/catalogue reads and Identity retains person ownership. No direct browser business
DB path, imported service runtime or cross-owner query is added. A composed response is
not a distributed snapshot or reusable authorization grant. Save rechecks current actor,
employment revision and selected reference scope/status; changed options cannot bypass
validation. Declare a bounded catalogue response without silent truncation. Search/paged
option loading is an explicit later need if actual catalogue size requires it, not a
premature feature in this small form.

Use a simple active/archived representation for these reference records with retained
server attribution/change history; no archive engine or automatic employee clearing.
This preference does not remove accepted historical/structural/audit protection or force
all domain lifecycles into one boolean. Candidate 2.15 incorporates the recommendation;
the remaining scope is still under discussion and no code/runtime evidence is produced.


Placement form clarification approved — 2026-10-11: one successful initial form-load API
response includes employee/current department-location labels and options. Loading, success
or whole-form failure/Retry are ordinary request states; no extra retry after success or
independent location lookup workflow. Changes take effect on Save with server-recorded
history. Simple active/archived reference state remains; no user placement date picker.

### Story 2.16: Assign or clear an employee's supervisor

**Scope accepted with attribution/eligibility clarifications, 2026-10-12; not implementation-ready.** Owner: shared People
supervisor relationship administration, with Leave-owned eligibility guidance. Consumes
completed employee/period/optional-reference and shared role/access views from E1/earlier
E2. Focus is one employee's current supervisor; selected bulk replacement is the following
bounded item, not a dependency. No organization-chart/import/approval-queue UI dependency.

As an administrator authorized to maintain supervisor relationships,
I want to set or clear an employee's supervisor,
So that reporting relationships are recorded once and applications can resolve their
own approval routes from that shared relationship.

**Acceptance Criteria:**

**Given** the exact employee and current shared employment-management authority,
**When** I open Employment & approval's supervisor edit,
**Then** the form supplies current supervisor identity/label, Unassigned and permitted
organization-scoped employee choices with the required revision/context,
**And** loading/error follows the approved form-level behavior rather than empty-choice
fallback. Candidate data is minimal and authorized; define bounded list/search behavior
against actual organization size without silently truncating or exposing other organizations.

**Given** a selected supervisor or explicit Unassigned,
**When** I Save the single employee's current relationship,
**Then** People validates exact same-organization employment identities and rejects a
self-reference, then changes the assignment with stable references, server effective
UTC time/actor, required history, revision and compact operation outcome,
**And** prior relationship evidence remains. No user date picker or future schedule is
required for this single-current-edit increment; the approved planned bulk replacement
workflow defines its effective date separately. No inferred recursive manager hierarchy.

**Given** no supervisor or an accountless/ineligible supervisor relationship,
**When** shared employment is saved/read,
**Then** Unassigned remains a valid optional fact and shared employment is not invalidated
merely because a consuming application's approval needs are unmet,
**And** Leave separately shows whether its configured supervisor route can resolve an
eligible approver. A shared relationship alone grants no login/app role or approval power.
Define departed/archived employee-reference retention and new selection rules before readiness.

**Given** a valid configured Employee's supervisor approval route,
**When** Leave later resolves a new submission,
**Then** it checks current membership/capability/self-approval eligibility and snapshots the
resolved supervisor under its own policy,
**And** a relationship change affects new route resolution without silently moving pending
steps or changing completed approvals. This story proves the shared/eligibility contract
with delivered fixtures; E5 owns real request submission/reroute integration.

**Given** the selected relationship needs Leave approval access/setup repair,
**When** the permitted administrator inspects the guidance,
**Then** it identifies the actual eligibility issue and links to the same completed role
assignment drawer or relevant setup surface when that actor has authority,
**And** role granting remains separately reviewed. Missing supervisor eligibility blocks
only the applicable consequential route; useful draft input follows the already approved
lightweight-preservation rules. Provider/Access outage is not confirmed missing permission.

**Given** other apps consume the supervisor relationship,
**When** People persists it,
**Then** it stores shared organization employment facts and history without Leave permission
names or workflow states,
**And** apps retain independent authorization/routing. Existing work profile, department/
location, entitlement and membership are not silently changed by the supervisor write.

**Given** stale review/reference, wrong-org or self target, denied authority, Cancel,
response loss or required dependency failure,
**When** Save resolves,
**Then** typed field/state errors and the existing explicit-save/current-revision contract
preserve useful input and refuse unsafe changes,
**And** matching retry/outcome resolution cannot duplicate history or revive a superseded
assignment. Required local audit/outcome failure aborts the local mutation; independent
HTTP verification stays outside business write locks.

**Given** initially failing acceptance and real People/current-access/restricted-role fixtures,
**When** delivery records evidence,
**Then** same-org/self guards, null/accountless references, history, concurrent updates,
selected eligibility guidance and safe retry/error cases pass,
**And** pending/completed workflow snapshots stay unchanged in contract fixtures. No actual
approval feature or cross-service atomicity is claimed from mocked responses.

**Traceability:** Features §2 manual supervisor/shared employment and §10 supervisor routing;
tracker Phase 2 shared optional assignment, Phase 7 workflow consumer; spine AD-1/2/3/5/8/12;
platform ADR-0012/0013/0019/0020/0022/0023/0025/0031/0035/0040/0041/0042/0049/0051;
Leave ADR-0076/0079/0082 and Employment & approval/settings UX. Supervisor replacement,
temporary cover, deliberate pending reroute and organization chart/import remain their
separate accepted/deferred scopes; no automatic role assignment is introduced.

**Impacts/readiness:** Specify nullable employment-to-employment key/history, current
assignment revision/operation, archived/ended reference rules and People write authority.
Define scoped candidate/name projection and selected Leave eligibility observation without
turning the ordinary `/v2/check` into an arbitrary-account lookup. Declare consumer freshness/
change-impact contracts before activating this writer against consequential workflows.
Promote proven optional-person selector, focused drawer/mobile form, Save/error/guidance
controls and HTTP clients through shared UI/scaffold; keep Leave's route rules in Leave.
Update owner docs/runbooks, source-to-test commands and generated usage guidance where
needed. Exact provider/constraint/API/sizing contracts remain gates; accepted ADRs unchanged.
No supervisor, app roles, employee, code, schema or deployment changed by planning.


Supervisor attribution/eligibility clarification — 2026-10-12: Story 2.16 remains under
discussion. Use ADR-0025's server-managed current-row updated_by/updated_at summary plus
one compact People-owned immutable employment-change record for each supervisor change.
Record organization/employment, old/new supervisor references, verified actor/time and
operation identity atomically with the change. The existing employment_change pattern
is the domain audit/history; do not add duplicate activity and audit tables or full-row
payload snapshots. Last-change fields alone cannot preserve successive supervisor changes.
Exact assignment/event schema remains a readiness contract, not implementation.

Recommendation: shared supervisor selection validates organization/employee reference and
self-reference, independent of Leave role eligibility. A real organizational supervisor
may lack Leave approval access or be accountless; People must not encode Leave permission
names. In Leave, assess the selected supervisor's approval eligibility and show guidance/
access-management shortcut without silently granting a role or hiding the true reporting
relationship. A Leave-specific direct approver picker (as distinct from shared supervisor)
offers only currently eligible approvers under existing features §10. Submission rechecks
current eligibility even if a form previously showed it as eligible.

Replace ambiguous newly resolved wording in user explanation with: when a new leave
request is submitted, its supervisor-based step is resolved and recorded. Example: Ana
submits request A while Pat is supervisor; the administrator later changes supervisor to
Sam. Request A stays assigned to Pat unless explicitly rerouted; a later submission B
resolves Sam if eligible. A draft begun before the change but submitted afterward likewise
uses the current valid route at submission. Completed decisions remain unchanged.
No new activity service, role grant, request transfer or readiness completion introduced.


## Change-history shape clarification — proposed 2026-10-12

**Direction approved by the user, 2026-10-12; scaffold realization and owner schema remain pending.**

User asks whether compact supervisor history belongs in a separate table and whether
`table, record_id, prev_val, new_val, actor, timestamp` should be generic. Recommendation
reuses the existing People-owned employment_change as one history table for meaningful
employment changes (periods, supervisor, department/location), not one table per field.
Common envelope includes scope/target, verified actor/initiator where applicable, UTC
time, operation/revision and event type/version; specific event variants declare bounded
before/after fields. A single confirmed command changing multiple relevant fields creates
one coherent event rather than independent unaffiliated per-field rows.

Share proven writer/types/scaffold/formatting conventions as build-time mechanisms while
each owner keeps its own persistence and atomic mutation/history transaction. Preserve
People's typed employment reference and constrained event payloads; arbitrary text table
names/record IDs and unrestricted old/new blobs weaken reference integrity, meaning and
sensitive-field control. No universal synchronous audit service, automatic whole-row
capture or duplicate generic audit beside employment_change. A broader owner-local
multi-entity event table can be assessed when real consumers need it; this is not a
mandatory separate history table for every entity type.

Performance is not the primary selection rationale here. Scope/target/time indexes and
bounded records support the actual history queries; no measured claim that domain-specific
storage is faster than a generic table has been made. Exact physical columns versus typed
JSON, payload/version validation, immutable role privileges and indexes remain the owning
readiness contract. Existing last-change attribution is retained on current records;
immutable history provides prior changes. Direction remains for discussion; no new ADR
or database implementation.


Common history scaffold pattern approved — 2026-10-12: user explicitly approves generic
mechanics with controlled domain events and owner-local persistence. The builder now
records common envelope/writer/typed event and test/display conventions. First consumers
promote proof and artifacts in the same delivery item; People shares employment-change
history across its relevant changes, not duplicate activity/audit tables. This implements
accepted ADR-0025/ownership/transaction rules without changing accepted decisions. Actor/
scoped reference/payload/retention/index contracts and implementation readiness remain
open. Story 2.16's broader supervisor scope remains in collaborative discussion; no
code, generator, event/history table or runtime service was implemented.


## Structured scaffold-input discussion — proposed 2026-10-12

User approves common history scaffolding and asks whether JSON describing app capabilities,
entities/views/history/saving should guide requirements and enforce reuse. Recommend a
[thin application scaffold configuration](../../platform/builder-cli/README.md#thin-application-scaffold-configuration--proposal-2026-10-12)
with versioned schema, approved pattern/owner/scope choices and source/test references.
Requirements/ADRs/UX remain product authority and BMAD remains sole workflow. The config
is derived engineering input maintained with stories, not another feature specification,
user-grant store, field/table schema copy or universal runtime app engine.

Separate saving semantics (draft/explicit form/preference) from inline/drawer/page layout;
use owner/action-specific history decisions, proven pattern versions and explicit supported
extension mechanisms. Generator/schema checks and actual acceptance/contract/scaffold tests
provide enforcement; AI can propose/configure them but a declared pattern does not prove
it is used correctly. Start with P1's actual inputs and WRITE/REF proof; later consumers
add patterns incrementally. No new story/gate/ADR or implementation is accepted from this
question yet. Existing pre-story and readiness requirements remain binding; 2.16 remains
under discussion while this scaffold direction is considered.


Scaffold-input direction approved — 2026-10-12: [platform ADR-0059](../../platform/docs/architecture/decisions/0059-schema-validated-scaffold-configuration.md)
records the thin versioned JSON/pattern selection approach. Specs/ADRs/UX and BMAD remain
sources/workflow; first consumers prove schema/generator/shared usage. Builder/agent
context updated. Returning to E2 supervisor stories with compact owner history, independent
People facts/Leave eligibility and new-submission snapshot terminology clarified.

### Story 2.17: Replace a supervisor for selected employees

**Scope approved by the user, 2026-10-12; not implementation-ready.** Owner: shared People
supervisor administration, with Leave-owned route/eligibility guidance. Depends on 2.16
single assignment, earlier employee/role/admin projection and established history/retry
foundations. Builds the approved 2026-10-11 focused convenience; no general mass editor.

As an administrator authorized to maintain supervisor relationships,
I want to replace a supervisor for all or selected reporting employees in one reviewed action,
So that staffing changes can be configured without opening each employee individually.

**Acceptance Criteria:**

**Given** a permitted current supervisor/organization and relationship-management authority,
**When** I open Replace supervisor,
**Then** I see the authorized affected employee set and can select all or some,
**And** selection binds exact employment IDs, not a later re-evaluation of a name/filter.
Only selected employees change; an employee joining that reporting list after review is
not silently added. Use the shared bounded employee-list/selection conventions.

**Given** selected employees and a replacement in the same organization,
**When** I choose the effective date and review,
**Then** I see the current/replacement supervisor, exact employees/count and effective date,
**And** the default is an immediate/current change, with planned dates following the
explicit approved replacement scope. Reject self/cross-org references and conflicting
reviewed relationship state. Exact date/instant/consumer interpretation is a pre-story
contract; do not invent a worker or silently apply planned relationships early.

**Given** current authority and reviewed per-employee state,
**When** I confirm,
**Then** People records only the selected dated relationships with guarded revisions,
server attribution and compact history/operation evidence using the approved pattern,
**And** matching retries do not duplicate employee changes. Command/batch identity and
per-item outcome/readiness contracts determine bounded execution, not one unbounded
cross-service transaction or arbitrary table bulk updates.

**Given** a stale employee assignment, denied item, interruption or partial execution,
**When** the action reports/resolves its result,
**Then** it states which selected employees were changed, unchanged or still failed/unresolved
according to the declared commit model,
**And** uncertain changes resolve their original item identities before retry. Do not claim
all employees moved from a batch-start response or automatically overwrite an employee's
newer relationship. Required local history/outcome failure aborts that local mutation.

**Given** the replacement needs Leave approval access,
**When** applicable eligibility guidance is shown,
**Then** selected shared reporting changes grant no role automatically and authorized
administrators can use the existing access drawer for explicit role repair,
**And** actual new Leave submissions resolve the supervisor applicable under the current
policy and recheck eligibility. Existing pending approvals/completed decisions keep their
snapshots. Shared People stores employment relationships without Leave permission rules.

**Given** outstanding approvals exist when E5 reassignment is available,
**When** an administrator wants to transfer them,
**Then** a separate authorized review selects the outstanding steps and records the reason,
**And** the People replacement operation cannot silently transfer request assignments.
E5 owns the actual protected transfer/notification integration; 2.17 uses contract fixtures
and remains independently completable without that later UI.

**Given** invalid input, Cancel, missing authority or required dependency outage,
**When** review/confirmation resolves,
**Then** the shared explicit-save/review/error conventions preserve useful local input and
report unavailable versus denial accurately,
**And** loading data is not mutation authority. Provider/consumer waits occur outside
business write locks; server audit fields cannot be overwritten by the browser.

**Given** initially failing acceptance and actual scoped People/restricted-role fixtures,
**When** implementation is verified,
**Then** selected-only/all selection, effective timing, self/cross-org guards, stale employee
state, retry/partial recovery and compact immutable history have evidence,
**And** old request assignments/profile/permissions are proven unchanged by the relationship
write. No performance guarantee or completed provider/workflow integration is assumed.

**Traceability:** Features §2 approved Replace supervisor and §10 snapshot/selected reroute;
tracker shared employment/structure; spine AD-1/2/3/5/8/12; platform ADR-0012/0013/0019/
0020/0022/0023/0025/0031/0035/0040/0041/0051/0059; Leave ADR-0076/0079/0082; shared
focused supervisor replacement UX. No recursive chart, Graph import or general spreadsheet
mass editor. Employment ending/membership removal/temporary cover retain separate actions.

**Impacts/readiness:** Define bounded selection/preview and per-item expected revisions,
future-date/current-history/reference rules, scalar relationship authority and batch/item
operation/commit/partial-outcome contracts before readiness. Validate consumer freshness/
impact handshakes before activating against consequential workflows. Reuse existing People
single-relationship domain logic, typed HTTP clients and common history; promote proven
selection/review/result controls only where generic. Update scaffold configuration source/
pattern choices when its schema exists, with tests rather than unverified declarations.
Owner docs/agent context/requirement evidence change together; accepted ADRs stay intact.
Exact safe batch size/transaction budget and first-consumer sizing remain open; split
concrete prerequisites before this consumer if needed. No supervisor, roles, accounts,
code, schema or deployment changed through planning.


Work-arrangement ordering — 2026-10-12: proceed to E2 Leave-owned configuration. Place
holiday-calendar setup before work-profile creation because a profile references its
calendar; then profile assignment/defaults and protected profile edits/lifecycle. This
is story decomposition inside approved E2, not a new epic or a completed readiness gate.
Shared People location remains distinct from Leave calendar/profile settings.

### Story 2.18: Configure an organization holiday calendar

**Scope approved by the user, 2026-10-12; not implementation-ready.** Owner: Leave calendar
configuration API/UI/persistence. Depends on E1 generated/current-access/configuration
foundations and established E2 administration. Calendar creation/entry tests need no later
profile editor or entitlement/submission UI; working-time semantics are explicit contract
inputs, with later consumers providing their own real calculations.

As a Leave administrator authorized to manage calendars,
I want to maintain named holiday calendars and their non-working dates,
So that employees with different working arrangements can use the right calendar.

**Acceptance Criteria:**

**Given** current calendar read/manage authority in the organization,
**When** I open Holiday calendars,
**Then** I see permitted named calendars with the year being viewed and dated entries,
**And** read-only access exposes no mutation controls. A legitimate empty calendar/year is
not an outage or assumed missing statutory setup; application errors remain retryable.
Stable calendar identity must not require replacing profile references each year.

**Given** a reviewed named calendar,
**When** I Create/Save it,
**Then** Leave creates only its organization-owned calendar and version/attribution evidence,
**And** no employees/work profiles are assigned automatically. Calendars may be empty;
no country/location lookup silently adds statutory holidays. References to optional People
location/jurisdiction metadata use authorized contracts, never another owner's tables.

**Given** a calendar and current management authority,
**When** I add/edit a named actual holiday or organization closure date,
**Then** I can represent full-day or partial-day non-working time under the declared
calendar-entry contract, including explicitly entered observed dates,
**And** date/bounds/duplicate-overlap rules are validated by API and owner constraints.
Partial-day representation, timezone interpretation, overlapping holidays and zero-work
cases must be specified before readiness, not guessed from a global eight-hour day.

**Given** existing calendar versions or requests refer to an entry,
**When** an entry changes or is removed through reviewed confirmation,
**Then** versioned calculation-relevant calendar meaning and required audit/actor/reason
are retained under the declared historical contract,
**And** recorded request dates/durations/decisions are not silently recalculated, trimmed
or cancelled. Review applicable affected consumers before activation, with changed impact
requiring fresh review. No historical rules reconstructed solely from an audit log.

**Given** a profile/work schedule later uses this calendar,
**When** Leave calculates a date's working time,
**Then** its actual effective schedule, calendar version and employee work timezone govern
full/partial non-working effects,
**And** the calendar edit cannot silently change the employee's schedule, timezone, profile
assignment or override. The later profile/calculation consumer owns end-to-end minutes/
half-day/request tests; this item proves stored calendar/version contract fixtures.

**Given** a proposed change and a stale revision, wrong-org target, missing authority,
Cancel, outage or response loss,
**When** it is saved/confirmed,
**Then** shared explicit saving and review where impact requires it preserve useful input,
with scoped guarded revisions and original-operation recovery,
**And** required local evidence failure aborts its mutation. No typing-time committed
calendar changes, sensitive payload dumps or positive authorization fallback.

**Given** initially failing acceptance and actual restricted Leave persistence/API fixtures,
**When** the item is delivered,
**Then** named/year views, empty calendars, full/partial entry contract, date/overlap guards,
version/history retention, current authority and duplicate-safe recovery have evidence,
**And** cross-org/calendar edit requests cannot affect another organization's data. Do not
claim legal compliance or live provider/holiday correctness from illustrative fixtures.

**Traceability:** Features §3 jurisdiction/holiday calendars, §7 schedule snapshots and
configuration principles; tracker Phase 5 calendars/schedules; spine AD-1/2/3/5/6/12;
platform ADR-0012/0013/0014/0019/0020/0022/0023/0025/0031/0035/0041/0051/0059;
Leave ADR-0003/0023/0086/0112/0113; Leave Holiday calendars/work-profile UX. Actual work
profile assignment, entitlement/request calculation and organization reports remain their
following story/epic owners; no holiday-provider import or statutory rule engine.

**Impacts/readiness:** Define exact calendar/entry schemas, year/date range, partial-day
units/local-time rules, overlap/observed-date treatment, stable identity/version/retirement
and required impact/freshness/confirmation contracts. Actual later consequential consumers
must integrate/prove these writer guards before activation against their records, without
making this item depend on their future UI. Reuse proven list/year/date/explicit-save/
review/status controls; leave calendar domain logic in Leave. Scaffold configuration records
approved choices when its schema exists; promote only domain-neutral mechanisms with tests.
Update owner docs/runbooks, generated API types/source-to-test evidence and usage guidance;
accepted ADRs remain immutable. Bound transaction/dependency waits and versioned migration/
recovery. Exact contract and single-agent sizing remain gates; no calendar/employee, code,
DDL or deployment changed by planning.


### Story 2.19: Create a reusable Leave work profile

**Scope approved with net-hours default/advanced timetable clarification, 2026-10-12; not implementation-ready.** Owner: Leave schedule/
profile configuration API/UI/persistence. Consumes completed 2.18 holiday calendars and
E1 typed/current access/owned config foundations; no later profile-assignment/default/
archive screen or entitlement/submission UI dependency. Only the initial profile/version
is created; modifying an already consumed version is following protected work.

As a Leave administrator authorized to manage schedules,
I want to create a named reusable work profile,
So that employees can share a clearly defined working arrangement without copying its
settings into every employee record.

**Acceptance Criteria:**

**Given** current permitted profile read/manage scope in the organization,
**When** I open Work profiles/Create profile,
**Then** I see the profile name, working days and net daily working hours, with detailed
working-time/break timetables available in Advanced settings,
work timezone, permitted holiday calendar and explicit standard-day conversion duration,
**And** the form uses the approved focused configuration/page/drawer conventions. Loaded
choices and existing form state use declared bounded form APIs; failure is not an empty
calendar selection or a silent country/schedule default.

**Given** a named profile with valid required values and its initial version boundary,
**When** I explicitly Save/confirm the new profile,
**Then** Leave persists its stable organization-owned identity and initial effective
calculation version, server attribution and required change/outcome evidence,
**And** no employees are assigned and the organization default does not change. Current
field/name/timezone/calendar/working-time validity is enforced at API/database boundaries;
matching retries create only one profile/version. Profile ownership stays in Leave.

**Given** working days with different scheduled lengths,
**When** the profile is stored/read under its declared schedule contract,
**Then** actual per-date working time is represented canonically in minutes and breaks
are treated explicitly, with a separately configured standard-day duration for entitlement
conversions,
**And** standard-day duration is not silently substituted for Friday hours or a particular
leave absence. No universal Monday–Friday/eight-hour/country arrangement is assumed.
Complete rounding/odd-minute/partial-holiday/local-time rules before readiness.

**Given** an explicit work timezone and completed same-organization holiday calendar,
**When** the profile's calculation contract is evaluated,
**Then** local leave-day boundaries and actual calendar/non-working time use those effective
settings, independent of where an employee/approver is viewing the app,
**And** another organization's calendar is rejected. An empty configured calendar is allowed;
no external statutory-holiday import is required. Calendar-year/date/partial-time fixtures
complement later real duration/entitlement consumer tests.

**Given** the profile was created but not assigned,
**When** its list/detail are opened,
**Then** it is available to authorized later assignment/default actions with zero assigned
employees and its working-week summary,
**And** People department/location/supervisor or membership changes cannot assign it
implicitly. Initial location/team suggestions do not establish an employee profile merge
or automatic precedence; explicit assignment follows separately.

**Given** a consumer later needs the initial schedule/calendar/version meaning,
**When** it loads this profile,
**Then** stable identity and immutable calculation version references are available under
the declared effective-date contract,
**And** mutable display metadata is distinguished from versioned calculation settings and
consequential audit. Do not reconstruct old working-time rules from a generic change log.
Initial effective version/name/date handling must be concrete before readiness.

**Given** invalid time/units/calendar reference, wrong organization, missing authority,
Cancel, response loss or dependency outage,
**When** Create/Save resolves,
**Then** explicit whole-form saving and safe field/current-state errors preserve useful
uncommitted input, with no hidden field autosave or administrative server draft,
**And** original scoped outcome recovery prevents duplicate profiles/version evidence.
Required local audit/outcome failure aborts creation; unrelated owner calls remain outside
business write locks. Creating unused profiles does not need a fictitious holder-impact report.

**Given** initially failing acceptance and actual restricted Leave/Access/calendar fixtures,
**When** this item is implemented,
**Then** creation/version identity, required fields, variable-day/minute/timezone/calendar
contracts, cross-org/API denial and retry/rollback behavior have evidence,
**And** earlier E1 work-timezone/draft input preservation stays compatible. No profile
creation test is claimed as full entitlement/request calculation or regulatory compliance.

**Traceability:** Features §3 working arrangements/profile identity and §7 duration inputs;
tracker Phase 5 effective schedules/profiles; spine AD-1/2/3/5/6/12; platform ADR-0012/0013/
0014/0019/0020/0022/0023/0025/0031/0035/0041/0051/0059; Leave ADR-0003/0023/0040/0041/
0086/0112/0113; approved Work profiles and employee schedule defaults UX. Assignment,
organization-default changes, employee overrides, protected consumed-profile edits and
archive lifecycle are following bounded stories, not prerequisites for initial creation.

**Impacts/readiness:** Specify schedule shape and minute/break/day-length/rounding bounds,
valid timezone/holiday references, standard-day conversion, initial effective boundary and
immutable version identity/keys/read contract, current authority and actor/history/outcome
schemas before readiness. Resolve E1 minimum timezone-setting adoption so later profile
assignment preserves explicit employee overrides and saved input; no whole-silo reset.
Preserve controlled owned migrations and compatible previous-version release behavior.
Promote proven working-week/date/timezone/input/review/status controls and typed clients
only where domain-neutral; Leave owns schedule interpretation, not a generic HR engine.
Record scaffold configuration/reference examples when supported patterns are proven, with
source/test evidence rather than config claims. Update owner docs/runbooks/generated
usage guidance and actual verification commands; accepted ADRs stay immutable. Exact
contract and single-agent sizing remain gated; no profile/employee, code, schema or deployment.


Work-profile input/wording agreement — 2026-10-12: user approves net daily hours as the
default and detailed working/break timetables as Advanced settings. Features/Leave UX
updated. Say schedule versions: retained effective settings used by calculations, not
versions of computed results. Audit/change history records who/what/when; calculation
versions and submitted snapshots remain independently meaningful. Complete net-only vs
clock-based partial-holiday/DST representation and avoid double-counted breaks before
readiness; no new universal hour defaults or timetable implementation.

### Story 2.20: Assign or change an employee's Leave work profile

**Candidate for discussion — 2026-10-12; not implementation-ready.** Owner: Leave employee
work-settings API/UI/persistence. Consumes completed E1 profile/default/timezone settings,
shared People employment, 2.18 calendars and 2.19 profiles; no later override editor,
default-change UI or request/entitlement UI dependency. E1/controlled fixtures prove
existing overrides/fallback without depending on those later editors.

As an authorized Leave administrator,
I want to assign an employee's work profile and review what will change,
So that their working arrangement is correct while explicit overrides and previous
calculations remain protected.

**Acceptance Criteria:**

**Given** exact permitted employee/organization work-settings context,
**When** I open Work schedule,
**Then** I see the current explicit profile or organization-default source, effective
schedule values and clearly marked existing employee overrides,
**And** the form uses declared bounded complete load responses for current labels/choices
and record revision. Profile choices are organization-scoped; a load failure is not an
empty selection/default or permission to silently erase a configured reference.

**Given** a valid active profile and intended effective date/reason,
**When** I review an assignment or switch,
**Then** I see the old/new profile, date and changed inherited values, with retained
overrides listed separately and applicable affected requests/consumers identified,
**And** future versions/assignment dates use the declared employee-local interpretation.
Profile assignment affects calculations, so date/reason/impact review is deliberate
rather than the simplified immediate-only department/location edit.

**Given** current reviewed references/settings and authority,
**When** I confirm,
**Then** Leave records one applicable explicit profile assignment for the employee/date,
with guarded revision, stable history, server attribution and required audit/outcome,
**And** existing explicit overrides are not silently cleared. Net-hours/advanced schedule
shape and incompatible override handling must be concrete before readiness; conflicting
or invalid input needs explicit resolution under the approved review contract.

**Given** the employee uses the organization default or I choose Use organization default,
**When** the effective settings are resolved under a permitted saved configuration,
**Then** no arbitrary location/team merge or first-profile fallback is inferred,
**And** explicit employee overrides remain. A missing/invalid default is honest setup
state, not an automatic assignment. Existing saved drafts keep the accepted lightweight
preservation rules; missing calculation setup is not a false loss of permission.

**Given** the explicit profile is missing, cross-org or archived,
**When** new assignment/current effective settings are validated,
**Then** the owner refuses invalid new use and identifies the exact setup/reference issue,
**And** it cannot silently substitute another profile or erase the existing choice.
Historical assignment/version references remain readable under appropriate access.

**Given** a shared department/location or supervisor changes,
**When** Leave work settings are read,
**Then** explicit profile/override values remain unless changed through this action,
**And** any initial suggestion is clearly a suggestion, not an automatic profile swap.
People is consumed through current authorized HTTP references; no copied shared facts.

**Given** prior submitted requests and consequential consumers exist,
**When** assignment changes become applicable,
**Then** prior schedule/calendar/timezone/version references and calculated results are
retained and any needed attention follows the existing correction/acknowledgement rules,
**And** no silent request-date rewrite, recalculation, cancellation or unpaid conversion.
Required impact/freshness contracts gate this writer; E3/E5/E6 add real consumer evidence
when delivered without making this E2 item depend on their future UI.

**Given** stale review, invalid date/reference, missing authority, Cancel, outage or response loss,
**When** Save/Review/Confirm resolves,
**Then** useful local input is retained, changed reviewed state needs renewed review, and
same-operation recovery prevents duplicate assignments/audit or a hidden new command,
**And** required local audit/outcome failure aborts the local mutation. External owner/
impact calls remain outside short coordination/write locks. No field autosave or admin draft.

**Given** initially failing acceptance and actual Leave/Access/People fixtures,
**When** delivery records evidence,
**Then** explicit assignment/fallback, retained overrides, effective timing, cross-org/
archive references, stale retry and protected prior versions have evidence,
**And** existing E1 timezone/draft behavior remains compatible. Synthetic override fixtures
prove preservation without a later override-edit UI, and actual request/calculation tests
remain with their consuming stories.

**Traceability:** Features §3 profile assignment/default/override and schedule review;
tracker Phase 5 employee work settings; spine AD-1/2/3/5/6/8/12; platform ADR-0012/0013/
0019/0020/0022/0023/0025/0031/0035/0040/0041/0049/0051/0059; Leave ADR-0003/0023/0041/
0086/0112/0113 and Work profiles/employee schedule-default UX. Changing the organization
default, editing employee override fields and consumed-profile versions are following
bounded work; no new membership/permission or policy/entitlement configuration here.

**Impacts/readiness:** Reconcile E1 minimum profile/timezone records with full schedule/
calendar fields; define stable assignment/effective version scope, exact date/timezone/
DST/net-vs-advanced semantics, override whitelist/validation, current revision/reason/impact
and compatible owner migration contracts. Protected consequential freshness/affected-work
coordination remains binding. Reuse proven reference/time/date/review/conflict/source-label
controls and typed owner HTTP clients; Leave owns effective inheritance. Count reference
configuration demo/scaffold history/input promotion where proven without importing app
servers or claiming a generic HR engine. Update docs/runbooks/source-to-test commands and
agent usage guidance where needed. Contract/sizing/readiness remain pending; no employee
profile/settings, code, schema or deployment changed through planning.

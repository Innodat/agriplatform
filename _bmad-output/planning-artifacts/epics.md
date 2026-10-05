---
project: Leave
status: epic-structure-approved
created: 2026-09-23
stepsCompleted: []
currentCheckpoint: Access split approved; ACCESS-A detailed criteria prepared for discussion; technical contracts remain
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

**Decomposition approved; detailed acceptance criteria for discussion. Not implementation-ready.**
Owner: existing Access service. Depends on ENV and completed ID-B's verified identity,
membership and controlled operator foundation. ACCESS-B supplies runtime enforcement.

As a platform administrator,
I want controlled setup of application availability and exact membership-bound grants,
So that each organization and account receives only its intended application access.

**Acceptance Criteria:**

**Given** an authenticated operator authorized for the exact Access command and target,
**When** explicit application and capability registrations are provisioned,
**Then** immutable app/capability associations are recorded with required attribution,
**And** new applications begin disabled, unknown/conflicting mappings fail, and no
wildcard, implied read grant or user grant is created automatically.

**Given** a verified organization and exact current account/membership,
**When** the operator configures organization enablement or assigns/revokes/regrants a
specific registered capability using expected absence or the current revision,
**Then** the owner commits only that intended target's change,
**And** grants bind the exact membership; retired membership, stale state and wrong
organization fail safely. Rejoining never restores old grants, and an old revoke
cannot retire a replacement grant. Disabling retains grants without deleting them.

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

**Given** the current Access service and supported v1 callers,
**When** Access receives its own locked dependencies/container inputs and compatible
schema expansion,
**Then** characterized intended v1 behavior still passes independently of PtS's dependency
file or a future ACCESS-B implementation,
**And** no new admission control is advertised as effective or activated for consumers
while existing checks ignore it. ACCESS-A's completion proves isolated configuration;
ACCESS-B and coordinated rollout prove enforcement before operational use.

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

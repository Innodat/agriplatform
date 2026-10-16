# Leave Tracker Implementation Plan

**Version:** 0.1  
**Last updated:** 2026-09-23

**Status:** Phase 1 planning in progress — implementation readiness pending  
**Owners:** Platform and Leave application teams

Current planning checkpoint — 2026-10-08: [24-item E1 scope and remaining contracts](../../../_bmad-output/planning-artifacts/epics.md#current-e1-contract-checkpoint--2026-10-08).
The reference test/demo role and minimal draft example are approved. Historical dated
counts below are superseded by the current sequence; implementation readiness remains
pending, and completed architecture consolidation/review is not reopened.

## Purpose

Scope correction, 2026-10-01: [platform ADR-0045](../../../platform/docs/architecture/decisions/0045-expense-preproduction-history-scope.md)
removes historical Expense receipt/purchase migration and old receipt-client compatibility
from the Leave/shared-identity path. Expense is preproduction. Preserve compatibility
for existing shared identities and PtS/Access/Content consumers. Internal operation
outcome records are a separate forward recovery requirement, with no old Leave records
to migrate.

Technical planning refresh, 2026-10-01: the existing Access owner in `services/access`
now implements current PtS checks; Leave must extend it compatibly, not create a
parallel Identity/Access service. The owning contracts below reflect its v1 permission
limits, existing PtS/Content consumers and differing legacy error formats. New Content
and deployment packages are reuse candidates, not evidence of Leave readiness.
The draft contract now supplies a concrete technical baseline (routes, input/counter
representation, coordination and timing). The 4,000-character note limit and retention
of each duration mode’s inputs were approved on 2026-10-01 and synchronized to features
and UX. The identity contract specifies proposed person/account/actor mappings, v2
responses and employment-date reads. Its bounded in-flight draft-only employment
observation rule was approved on 2026-10-01 and generalized in
[platform ADR-0044](../../../platform/docs/architecture/decisions/0044-bounded-shared-input-observations-for-draft-saves.md); existing identity and verification gates
remain open. No live target was inspected or changed.


Planning update, 2026-09-23: all eight epic groupings and their delivery sequence,
including E5, are approved in the [epic planning artifact](../../../_bmad-output/planning-artifacts/epics.md).
Individual stories and implementation readiness remain pending. Apply
[platform ADR-0039](../../../platform/docs/architecture/decisions/0039-organization-neutral-tenancy.md)
for organization-neutral tenancy and
[platform ADR-0040](../../../platform/docs/architecture/decisions/0040-shared-employment-core-and-application-settings.md)
for shared common employment facts. Earlier NGO wording denotes the general
organization tenant. The first slice remains sign in → select organization →
create/resume draft → autosave → close → reopen.

Before E1 readiness, resolve the minimal shared employment reference/read contract
alongside identity/access; before E2 employment writes, resolve the shared owner's
mutation/history contract. Before dependent calculations/confirmations, resolve
freshness and employment-change impact coordination without remote waits under
business locks. Owners: Platform identity/people owner and Leave lead.
The [E1 shared contract discussion](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md)
records current repository evidence and proposed ownership, identity and read behavior;
its open wire, migration and eligibility decisions remain readiness blockers. The E1
work breakdown and revised 20-candidate delivery order are approved; final story
contract validation, sizing and implementation readiness remain pending. The
[draft persistence/recovery contract discussion](./architecture/contracts/e1-draft-persistence-and-recovery.md)
records agreed current/future-employment preparation, ended-employment read-only access,
rehire resumption and preservation after selected end dates pass. Compact replay evidence retention and
discarded-content removal were approved on 2026-09-24. Database lifecycle rows and
separate application-owned operation receipts clarify storage; exact physical design
and stale-start generation checks remain proposed. Remaining wire,
freshness, retention and concurrency details still gate stories. Discussion progress is
not gate completion.
The [shared API error/recovery proposal](../../../platform/docs/architecture/contracts/api-errors-and-operation-recovery.md)
now specifies proposed error identifiers, legacy numeric-code compatibility and
committed/unresolved operation responses. E1 must verify safe framework adapters,
generated clients and commit-then-lost-response recovery; this proposal is not a
completed API contract/readiness gate.
Bounded automatic uncertain-save recovery followed by truthful unresolved feedback
and Retry was approved on 2026-09-24. The draft-input contract now proposes preserving
incomplete typed values across acknowledged save/reopen, also approved on 2026-09-24;
input v1, bounds and execution/recovery timing are now specified in the draft contract;
schema consistency and compatibility fixtures still need validation before readiness.
The [E1 acceptance map](./testing/e1-acceptance-map.md) maps approved behavior to source
requirements and planned browser/API/database/shared-scaffold evidence. This is test
planning, not executed acceptance or a complete requirements coverage assessment.
The [existing identity/Expense review and consolidation plan](../../../platform/docs/architecture/reviews/identity-expense-consolidation-2026-09-23.md)
records shared-schema adoption and legacy-consumer compatibility work. Retain one
employment relationship per person per organization with employment-period history,
as agreed by the user; accountless-person support and the consolidation recommendations are accepted under
[platform ADR-0042](../../../platform/docs/architecture/decisions/0042-person-account-employment-and-legacy-adoption.md). Identity
adoption must characterize existing behavior and repair verification fixtures before
using them as migration evidence; the full Expense API transition is separate from E1.
[Platform ADR-0041](../../../platform/docs/architecture/decisions/0041-shared-supervisor-department-and-location.md)
now places optional department/location assignments and the optional manually maintained
supervisor relationship with shared employment. Resolve null/scoped-reference,
history and retirement contracts before E2; supervisor freshness, eligibility and
workflow snapshot/reroute checks before E5. Leave work profiles remain independent. This does not reopen completed
architecture consolidation or claim its new amendment has passed implementation readiness.

This document is the delivery plan and progress tracker for the Leave Tracker and
the platform capabilities established through it. It should be updated as work is
completed, decisions change, or scope is moved between releases.

The accompanying functional specification is
[`features.md`](./features.md).

Accepted architecture decisions are indexed in the
[platform ADR collection](../../../platform/docs/architecture/decisions/README.md)
and the [Leave ADR collection](./architecture/decisions/README.md).
Delivery follows the installed BMAD workflows and
[platform BMAD decision](../../../platform/docs/architecture/decisions/0010-bmad-as-delivery-workflow.md),
using repository-owned [platform agent context](../../../platform/prompts/README.md).
Delivery uses the platform
[ATDD/TDD loop](../../../platform/docs/architecture/decisions/0009-atdd-and-tdd-development-loop.md).

## Status conventions

Use these values consistently:

- `[ ]` Not started
- `[~]` In progress
- `[x]` Complete and verified
- `[!]` Blocked; add a dated note under **Blockers and risks**
- `[-]` Removed or deferred; identify the destination phase

A milestone is complete only when its implementation, automated tests,
documentation, and acceptance checks are complete.

## Outcomes

1. Deliver an intuitive multi-tenant leave-management application.
2. Establish a repeatable application silo created from the platform scaffold.
3. Establish reusable shadcn-based UI foundations without moving Leave business
   components into the platform layer.
4. Evolve the builder scaffolding continuously as reusable patterns are proven,
   so the next application starts with the current platform conventions.
5. Use BMAD proportionally for planning and delivery while keeping Agriplatform
   context, safeguards, scaffolds, tests, documentation, and code aligned.
6. Use ATDD to make product behavior executable and TDD to implement/refactor in
   small, safe, deterministic increments.
7. Establish common FastAPI content and notification capabilities with clear HTTP
   contracts.
8. Preserve strict NGO isolation across identity, database access, jobs, files,
   calendars, and notifications.

## Confirmed product decisions

| Decision | Outcome |
|---|---|
| Tenant membership | One platform user may belong to multiple NGOs |
| Authentication | Microsoft Entra ID through Supabase Auth for MVP |
| Identity migration | Do not move to ZITADEL or Keycloak for MVP; preserve an OIDC-friendly boundary |
| Leave units | Full day, half day, and hours |
| Hourly increment | 0.5 hour (30-minute) increments |
| Half day | Exactly 50% of that employee's configured scheduled hours for the day |
| Future entitlement | Projected accrual may be used for future requests |
| Visual direction | Calm/practical/low-friction; neutral backgrounds, subtle decoration, primary-action accent, generous space, prominent balances/actions, expandable granular detail, and familiar accessible platform controls |
| Mobile workflows | Full employee request/upload/balance/history/required responses and approver review/decisions on phones; compact month calendar with history list retained |
| Submission confirmation | Confirmed success returns to My Leave with brief confirmation and optional View request, updated dates/status and removed draft indicator; failed/uncertain submissions remain open with duplicate-safe recovery (ADR-0087) |
| Submission summary | Show type/dates/duration/paid-unpaid split and Approval required where applicable, with workflow details on demand; NGO stays in header, switcher only for multiple active memberships; exact unpaid acknowledgement retained |
| Switching while editing | Save in original NGO before opening selected NGO's My Leave; never transfer draft data; on failure use exit-only Stay/Switch anyway under platform ADR-0050, with inline Retry when staying and the saved draft preserved |
| Draft saving | One employee application draft per employee per NGO; Apply for leave resumes it; truthful autosave status and safe Close; confirmed Discard draft; no reservation; submission revalidates (ADR-0075) |
| Role navigation | Start on My Leave; show Approvals/Manage Leave by permission; switch without sign-out or NGO change; section action badges remain separate from unread notifications |
| Leave Manager scope and home | NGO-wide employee scope for MVP, with separate action permissions; prioritize escalations/deficits, affected requests, authorized corrections, organization overview, and configuration/report/audit shortcuts |
| Approver home screen | Current decision queue, short-notice/backdating/override/overdue flags, authorized team availability, own-workspace access, and permitted request calculation/history |
| Employee home screen | Apply action, per-type balances, pending requests/required responses, upcoming approved leave, and year-calendar/history link within the active NGO |
| Employee history and balances | Year calendar with accessible history list; distinguish taken/future/pending leave; per-type available/reserved balances and explanations, with projections in the request form; pilot finding prior-year leave and available balances |
| Language preference | Per user across NGO switches; personal notifications use preferred language when available, otherwise English; language does not change work timezone or policy |
| Approval escalation | Default seven calendar days without required action, configurable per policy; notify authorized Leave Manager without automatic reassignment |
| Language and dates | English default; dates such as 15 Sep 2026; localization-ready implementation with Portuguese planned next for Mozambique and Angola, release date pending |
| Approval reminders | Policy interval defaults to three calendar days; target currently required approvers, stop on action/withdrawal/cancellation, and never automatically decide or reroute |
| Notification read state | Open marks read; mark-all applies only to the user's active NGO; reading never approves leave or acknowledges an unpaid increase |
| NGO notification scope | Bell/inbox show active NGO only; selector shows count-only unread badges for active memberships; switching loads that NGO and opening rechecks permissions |
| Correction notifications | Email and in-app notification link to authorized before/after details, reason, and actor; acknowledgement only for increased requested unpaid leave |
| Overlap and corrections | Submitted/in-approval/approved same-date requests warn and count toward a scheduled-hours daily limit for the same employee/NGO across types; administrative past/current/future corrections require an in-scope Leave Manager with on-behalf permission, reason, history, and existing approval rules |
| Backdating | No fixed cutoff or age-based administrative route; mandatory reason and visible lateness, normal approval/checks, historical schedule/policy calculations, and explained audit corrections |
| Minimum notice | Configurable calendar days per policy, default zero; permit shorter-notice requests with mandatory explanation and approver flag; backdating remains separate |
| Employment end and leave dates | Block submission/final approval after the known end date; the last employment date remains eligible; flag affected existing requests with explanation without silent date changes |
| Departure after upfront grant | Recalculate using policy proration and employment end date; explain audited corrections, retain eligible no-proration grants, and refer spent deficits for authorized review without automatic unpaid conversion |
| End-of-instalment availability | Grants are usable from the start of their grant date in employee work timezone, not deferred to the next instalment |
| Initial monthly grant | Joiners after an instalment starts receive a joining-date grant under start-of-instalment policies using policy proration; normal grants resume at the next aligned instalment start; end-of-instalment policies wait until its final date |
| Leap-day anniversary | February 29 starts resolve to February 28 in non-leap years and return to February 29 in leap years; resolved dates start periods and trigger annual grants |
| Entitlement periods | Per policy: calendar year or employee employment-anniversary year; period basis remains separate from daily/upfront/monthly availability |
| Variable-length schedules | Explicit standard-day duration for entitlement conversions; actual leave consumes the requested date's scheduled working time, with half days at exactly 50% |
| Carry-over day conversion | Use employee's configured standard working-day duration effective at rollover; audit the conversion and retain historical carried amounts after schedule changes |
| Cancellation deficit reviewer | In-scope Leave Manager with balance-adjustment permission; mandatory reason and employee explanation; extra paid entitlement requires an explicit audited grant, with no automatic conversion of approved leave to unpaid |
| Cancellation accrual correction | Recalculate as if the cancelled request never consumed entitlement, preserve other actual transactions, restore consumption and reverse extra accrual with preview/audit entries; spent-entitlement deficits require review, not silent unpaid conversion |
| Reservations and cap | Already-earned reserved entitlement counts toward the cap until final approval consumes it; withdrawal creates no headroom; future-accrual reservations do not change today's balance |
| Future reservations and booking | Fund requested dates from valid entitlement, including projected accrual and permitted carry-over; future accrual is not current entitlement; default booking horizon is 12 months, configurable per policy, covering every requested date |
| Accrual after cap | Resume on the next scheduled date, granting only what fits; no immediate grant or automatic restoration of prior excluded amounts |
| Accumulated balance cap | Optional per policy, separate from carry-over limits; scheduled accrual grants only what fits and explains excluded amounts without removing existing entitlement |
| Reservation priority | New requests cannot displace existing reservations, even for earlier leave dates; new-request shortfalls use the existing override/unpaid process |
| Increased unpaid amount | Authorized changes require an employee-visible actor, reason, previous/revised amounts, and acknowledgement before final approval; retain audit history |
| Pending rollover shortfalls | Reservations do not bypass carry-over limits or expiry; keep requests pending for override/unpaid review and warn employees of the exact amount requested as unpaid leave |
| Non-carried entitlement | Unused amounts excluded by carry-over rules expire at the period boundary with an auditable entry and employee explanation; no automatic payout or cross-type transfer |
| Repeated carry-over | Per policy: once-only or repeated transfer subject to carry-over limits; preserve existing expiry dates without extension |
| Carry-over | Per policy: none, all unused eligible entitlement, or a configured limit; carried entitlement may have a configured expiry or no expiry |
| Accrual dates | Daily earning is available from each eligible day's start; annual upfront grants follow period starts; monthly grants use the start/end of leave-year-aligned instalments with anchored boundaries (ADR-0099/0100); leap-day anniversaries use the agreed fallback |
| Historical calculation corrections | Preserve original decision evidence; recompute corrected balances with subsequent events, actor/reason and affected-request safeguards (ADR-0107) |
| Record attribution | Platform ADR-0025: mutable creation/update actor IDs and UTC times; immutable creation-only attribution; separate audit, verified identity and command/release provenance; scaffold all supported write paths |
| Operational logging privacy | Follow platform ADR-0023: selected structured correlation fields, no sensitive payload/credential leakage, separate authorized audit and optional safe support details; verify error paths |
| External service waits | Follow platform ADR-0022: short transactions, external delivery outside business locks, atomic outbox intent and documented justified exceptions |
| Concurrent-change wait | Bounded coordination wait, fresh state after acquisition, preserved form and duplicate-safe retry; distinguish busy from uncertain outcome, set/test timeout in affected story (ADR-0113) |
| Confirmation input consistency | Revalidate applicable policy/calendar/employment and balance dependencies through commit; re-confirm consequential changes, preserve entered data; concrete concurrency mechanism required in affected stories (ADR-0112) |
| Calculation evidence | Modest Leave-owned snapshot table with searchable context and JSON details, saved atomically with consequential actions; distinct calculation/policy versions, no generic framework (ADR-0111) |
| Same-day balance event ordering | Effective date plus recorded time and stable server sequence; serialize employee/NGO mutations, preserve retry order and backdated correction safeguards (ADR-0110) |
| Accrual boundary ordering | Resolve expiry and prior-period carry-over before new earning; test inclusive dates, post-expiry cap headroom and repeated calculations (ADR-0109) |
| Accrual performance | Direct indexed/history calculation initially; agree workload/targets before affected stories, verify before release, add rebuildable checkpoints only if measured need (ADR-0108) |
| Automatic accrual persistence | Calculate on demand from effective-dated history and immutable actual events; save consequential decision snapshots, with no daily posting dependency (ADR-0106) |
| Monthly cumulative precision | Preserve fractions across partial periods and annual-rate changes within the leave year; no reset or cap catch-up (ADR-0105) |
| Monthly partial employment | New-policy default: Adjust for time employed; full-period alternative retained. Inclusive calendar-day ratio, visible 18 / 12 × 15 / 30 = 0.75-day example (ADR-0104) |
| Prorated grant rounding | Fixed final whole-minute floor (ADR-0103), retaining cumulative precision and exact schedule-based half days; no user-selectable rounding |
| Partial-period proration | Policy chooses no proration or calendar days employed divided by period calendar days, including first/last employment dates; manual grants remain explicit |
| MVP accrual schedules | Annual-target policies choose daily earning, annual upfront at entitlement-period start (with a policy-prorated joining grant), or monthly portions at aligned instalment start/end (ADR-0090/0099); separate manual-only grants require authorized staff and an audited reason. Monthly/upfront partial employment follows policy rules; daily earning accounts for employment dates directly |
| Leave day timezone | Employee's configured work timezone defines leave dates, accrual, and expiry; viewer or approver timezone does not change entitlement outcomes |
| Accrual availability | Usable from the start of the configured effective date, never for earlier leave; policy determines schedule and effective dates |
| Entitlement expiry date | Last usable leave date, inclusive; unavailable from the following date even when the request was submitted before expiry |
| Entitlement allocation priority | Use eligible entitlement expiring soonest first within the selected balance; non-expiring entitlement last; another leave type still requires the agreed override |
| Future balance assessment | Check every requested date using accrual earned by then, entitlement expiry, and existing reservations; carry forward earlier candidate consumption and apply agreed shortfall rules |
| Insufficient balance | Configurable supervisor override, with reason and auditable consequence |
| Approval | Configurable by NGO and leave policy; at least one step, with one-tier and two-tier MVP presets; authorized automatic decisions satisfy only the submitter's own steps |
| Self-approval | Allowed only when explicitly configured |
| Administration | Tenant-scoped Leave Manager and Organization Administrator roles |
| Leave configuration | Leave types are versioned CRUD resources; used types are archived, not hard-deleted |
| Employee entitlement | Effective-dated employee overrides are supported and audited |
| Calendar integrations | Microsoft 365 first, then others; post-MVP |
| Jurisdictions | Store jurisdiction and effective-dated policy metadata now; do not build a statutory rules engine in MVP |
| Attachments | Shared FastAPI Content Service using signed direct-to-provider transfer |
| Attachment limits | 10 MB per file; PDF, JPEG, and PNG initially; maximum 3 files and 20 MB total per request |
| Malware scanning | Deferred from MVP; retain an extensible safety-status hook and strict type/size validation |
| Medical-document retention | Configurable by NGO/jurisdiction; initial default 2 years after request closure, subject to legal/privacy review |
| Cancellation | Approved leave may be cancelled without another approval; audit and reverse its balance effects |
| Approver field visibility | Assigned approvers see sensitive leave types and employee notes through their normal approval role; medical documents require separate permission and resource authorization |
| Approval-history visibility | Employees see decisions, approver names, timestamps, and approval/rejection comments on their own requests; assigned approvers see the same history for requests they handle; no private approver-only comments in MVP |
| Approver medical-document metadata | Without document permission, show only required-document provision and verification status; filenames, previews, and downloads require separate permission and resource authorization; employees retain their own permitted document access |
| Leave Manager field visibility | Leave Managers see sensitive leave types, employee notes, and approval history within authorized NGO/resource scope; medical documents remain separately authorized |
| Leave Manager medical-document metadata | Without document permission, show only provision and verification status within authorized scope; filenames, previews, and downloads require separate permission and resource authorization |
| Changes to approved dates/duration | Employee or scoped on-behalf actor cancels the original and submits a linked new request through approval again; approval authority alone grants no correction rights |
| Capacity warnings | Informational in MVP and do not block submission or approval |
| Leave Manager on behalf | May submit and approve on behalf when separately permitted; action is visibly attributed and audited |
| Balance deficit | Excess is unpaid by default; an authorized exception may allocate a request across discretionary paid leave, another paid balance, and unpaid leave |
| Notifications | Common notification capability; initially modular and asynchronously delivered |
| Email privacy | Request data is limited to employee name, dates, status, and a secure application link; leave types, notes, comments, and document details stay in the authorized application |
| In-app notification privacy | Request data is limited to employee name, dates, status, and a request link; opening the request rechecks current permissions before showing role-permitted details |

## Target architecture

```text
apps/leave/
├── backend/                 Leave FastAPI API and domain rules
├── web/                     React, Vite, shadcn UI
├── backend/migrations/     Planned Alembic revisions for Leave schema and RLS
├── docs/                    Feature specification, plan, decisions
├── tools/
└── CHANGELOG.md

services/content-service/    Shared FastAPI content control plane
services/notification/       Shared notification runtime when delivery is implemented
platform/ui-core/            Owned shadcn primitives and design tokens
platform/ui-business/        Generic AppShell, AppLauncher, tables, calendars, upload UI
services/app-directory/      Cross-app catalog and entitlement discovery
platform/builder-cli/        Versioned app/service templates and convention validation
platform/prompts/            Agriplatform-specific agent context and safeguards
```

### Boundary rules

- Apply [platform ADR-0019](../../../platform/docs/architecture/decisions/0019-current-server-side-authorization.md): current shared membership/permission checks on protected requests plus Leave resource rules; deny revoked access and fail safely when verification is unavailable. [Platform ADR-0021](../../../platform/docs/architecture/decisions/0021-revocation-and-in-flight-operations.md) permits bounded already-authorized execution to finish; subsequent checks observe revocation. Specify execution timeouts and audit fields before affected story readiness.

- The Leave application owns leave policies, schedules, balances, applications,
  approval routing, attachment associations, and attachment visibility rules.
- The Content Service owns provider selection, content metadata, signed operations,
  blob verification, retention operations, and storage-provider adapters.
- The Notification capability owns templates, delivery attempts, retry policy, and
  channel adapters. Leave decides which domain event occurred and who should be
  notified.
- Database transactions carry verified NGO/actor context under [platform ADR-0018](../../../platform/docs/architecture/decisions/0018-transaction-scoped-tenant-context.md); missing tenant context denies NGO-owned data access, and pooled connections must not retain request scope.
- Application frontends use FastAPI for business data. The Supabase browser client
  is limited to authentication and explicitly approved realtime use.
- Cross-app runtime capabilities are called over HTTP; Leave does not import their
  server implementation.
- Backend API contracts are Pydantic/OpenAPI-first and generate or validate strict
  frontend contracts.
- Adopt [platform ADR-0014](../../../platform/docs/architecture/decisions/0014-python-database-access-and-api-models.md): SQLAlchemy/Psycopg database access, separate Pydantic API schemas, workflow-owned transactions, and no parallel Supabase Data API business-data path.
- Adopt [platform ADR-0015](../../../platform/docs/architecture/decisions/0015-alembic-migration-authority.md): Alembic owns project-schema migrations. Transition existing SQL assets and bootstrap/reset/seed/CI commands deliberately; exclude Supabase-managed schemas and prevent dual migration ownership. [Platform ADR-0016](../../../platform/docs/architecture/decisions/0016-owned-migration-histories-and-coordination.md) assigns Leave its own schema, revision files and migration-version table, with dependency-aware shared deployment coordination. Recovery follows platform ADR-0020 and Leave ADR-0119; concrete migration coordination/locking and runbook evidence remain delivery prerequisites.

## Continuous scaffold evolution

The Leave application is both a product and the proving ground for the application
builder. Scaffolding is updated throughout implementation, not reconstructed after
the application is finished.

Every feature or platform change must complete a **scaffold impact review**:

1. Is the pattern domain-neutral and useful when creating another application or
   shared service?
2. Has the pattern been proven in a working Leave vertical slice?
3. Does it belong in an app template, service template, shared UI package, generated
   client workflow, validation rule, example, or documentation?
4. Can an existing generated application adopt it without an unsafe rewrite?

When the answer is yes, the same delivery item must:

- Update or create the relevant `platform/builder-cli` template.
- Update template dependencies, configuration examples, scripts, and generated-file
  banners where applicable.
- Update builder validation rules and generation tests.
- Generate a disposable sample app/service in CI and verify install, type-check,
  test, build, and startup/health behavior.
- Document the generated structure and intended extension points.
- Add a builder/scaffold changelog entry and migration note for existing apps when
  adoption is useful.

When the answer is no, record **No scaffold change — application-specific** in the
feature's completion notes. Leave-domain policy, balance, and approval components
must not enter generic templates merely because Leave was the first implementation.

### Initial scaffold targets

- FastAPI application and shared-service variants
- Required and optional Supabase JWT dependencies and active-NGO context
- Structured errors, correlation IDs, health/readiness, configuration, and logging
- Pydantic/OpenAPI contracts and generated strict TypeScript client workflow
- React/Vite application shell, authentication context, NGO switcher, routing,
  error boundaries, loading/empty states, and test setup
- `ui-core`/`ui-business` integration and shadcn conventions
- Migration layout, RLS conventions, tenant-isolation test harness, audit hooks,
  background-worker/outbox pattern, and service-client pattern
- CI commands, environment examples, documentation skeleton, changelog, and ADR layout

The scaffold provides stable mechanisms and extension points. It may include a
small reference vertical slice, but it does not generate Leave-specific entities or
business workflows for unrelated applications.

## Content Service decision

The existing Supabase Edge Functions are a useful prototype, but the platform
direction is a shared FastAPI service under `services/content-service`.

FastAPI is the **control plane**. File bytes do not normally pass through FastAPI:

```text
Web → Content API: request upload session
Content API → Web: content ID + short-lived signed upload URL
Web → Azure Blob/Supabase Storage: upload bytes directly
Web → Content API: finalize
Content API → provider: verify object, size, checksum and type
Content API → database: activate metadata and audit the operation
Leave API → leave attachment association: link content ID to request
```

This gives applications one auditable authorization boundary while retaining the
scalability of direct blob uploads.

### Content Service MVP contract

- `POST /api/content/upload-sessions`
- `POST /api/content/{content_id}/finalize`
- `GET /api/content/{content_id}` (metadata only)
- `POST /api/content/{content_id}/read-url`
- `DELETE /api/content/{content_id}` (soft delete or scheduled disposal)
- `GET /health`

The service must support Azure Blob Storage and Supabase Storage through provider
adapters. It must preserve tenant-specific provider selection already represented
by `identity.org.settings.content_source_id`.

### Required content protections

- Resolve `org_id` from verified server identity context, never request JSON.
- Verify active membership in the organization.
- Use opaque content IDs and tenant-prefixed, unguessable external keys.
- Permit only configured MIME types and extensions; do not trust the browser MIME
  value alone.
- Enforce the MVP limit of 10 MB per file, 3 files and 20 MB total per Leave
  request. Initial accepted types are PDF (`application/pdf`), JPEG
  (`image/jpeg`), and PNG (`image/png`). Other domains may define their own limits.
- Verify size and checksum during finalization where supported.
- Keep a content-safety status extension point so malware scanning can be added
  later. Malware scanning is not an MVP release gate.
- Do not issue a read URL until domain authorization and all enabled content-safety
  checks succeed.
- Keep medical/supporting files private; never place them in public buckets.
- Use operation-specific signed URLs under platform ADR-0036: private read/download 5 minutes and upload 15 minutes by default; renewal rechecks authorization, preserves form/recovery state and is verified against provider-specific expiry/in-flight behavior.
- Make upload-session creation and finalization idempotent.
- Apply [platform ADR-0038](../../../platform/docs/architecture/decisions/0038-finalized-content-byte-identity.md): bind finalization, verification evidence, reads and associations to fixed file bytes; prove overwrite/replay and finalization-race protection before the attachment story. Replacement requires new identity, verification and authorized audited association change.
- Verify per-attempt document failure/retry behavior: bounded dependency calls, accurate denied/missing/unavailable distinctions, no global frontend offline flag or health preflight, preserved mutation identity and unaffected independent Leave actions.
- Clean up expired, unfinalized objects with a scheduled job.
- Apply platform ADR-0030: distinguish uploaded/finalized content from confirmed domain association, support duplicate-safe attachment retries, and define a race-safe pending/confirmed association versus abandoned-object cleanup contract before implementation; preserve saved drafts and submitted attachments.
- Audit create, finalize, read authorization, delete, scan result, and retention.

The Leave API must authorize a document against the associated leave request
before it asks the Content Service for a read capability. A platform administrator
does not automatically gain permission to read sensitive leave documents.

## BMAD operating model

The installed `_bmad/_config/bmad-help.csv` catalog is authoritative for available
skills and sequencing. Run `bmad-help` in a fresh context at the start and end of
each phase; it inspects configuration and artifacts and recommends only the relevant
next workflow.

| Work size/risk | BMAD path | Required repository gates |
|---|---|---|
| Mechanical, no meaningful behavior risk | Direct engineering | Relevant static checks; test if behavior changes; impact decisions |
| Bounded and well understood | `[BD]` `bmad-build` | Acceptance example/regression first, TDD, built-in review, impact decisions |
| New app/service or high-risk platform/domain change | Full planning baseline then story-sized `[BD]` | PRD/spec, architecture, stories, readiness, ATDD/TDD, security/contract gates |

The full installed planning sequence is:

```text
[PRD] bmad-prd (create/update/validate)
        ↓
[CU]  bmad-ux when user experience is material
        ↓
[CA]  bmad-architecture
        ↓
[CE]  bmad-create-epics-and-stories
        ↓
[SP]  bmad-sprint-planning readiness gate
        ↓
[BD]  bmad-build per bounded story
```

`[CR] bmad-code-review` is an optional additional review after Build and is expected
for identity, tenant isolation, sensitive content, balance logic, and destructive
migrations. `[AE] bmad-advanced-elicitation` may be used at a design checkpoint when
a pre-mortem, first-principles challenge, or red-team pass would materially reduce
risk. Each workflow should run in a fresh context window.

## Delivery plan and progress

**Story 4.9 scope approved — 2026-10-16:**
[attachment action-required notices](../../../_bmad-output/planning-artifacts/epics.md#story-49-notify-me-when-a-document-needs-attention)
use atomic Leave outcome/intent and E3 delivery, privacy-safe templates/current-access
links, deduplicated recovery and accurate resolved state; ordinary active-upload errors
stay inline. Exact event transitions/recipients/relevance/expiry and submitted-request
integration remain binding. Continue Story 4.10 retention configuration in group 6;
all contracts/coverage/sizing/readiness remain open, no notifications or code performed.

**Story 4.8 scope approved — 2026-10-16:**
[editable-draft document removal/replacement](../../../_bmad-output/planning-artifacts/epics.md#story-48-remove-or-replace-a-document-on-my-editable-draft)
preserves original until replacement confirms, new verified identity, guarded atomic local
change/evidence, recoverable Content release, effective limits and retry/concurrency/
cleanup safety. Existing earlier Remove remains functional; submitted-document changes
stay with later domain workflows. Bind temporary capacity and exact protocols before
readiness. Continue Story 4.9 rejection/action-required notices; no code authorized.

**Story 4.7 scope approved — 2026-10-16:**
[authenticated supporting-document reads](../../../_bmad-output/planning-artifacts/epics.md#story-47-open-and-download-an-authorized-supporting-document)
consume shared Content streaming/browser authentication/gateway work with Leave-specific
current user/resource/document checks. Fixed-byte full/partial reads, native PDF/Download,
safe cache/headers, authentication recovery and bounded failure/disconnect apply; exact
transport/wire/resource inputs and actual routed evidence remain gates. Continue Story
4.8 editable-draft removal/replacement in group 5. No implementation authorization.

**Story 4.6 scope approved — 2026-10-16:**
[safe document status/metadata](../../../_bmad-output/planning-artifacts/epics.md#story-46-show-document-status-without-exposing-protected-details)
enforces status-only projection for document-unprivileged approvers/managers, scoped
permitted metadata and own-document access, accurate safe failures and API/UI denial.
E5 integrates real approval/review screens; private streaming follows separately.
Latest user decision retains Expense React Native and implementation priority.
Contracts/coverage/sizing/readiness stay open.

**Story 4.5 latest scope — user decision, 2026-10-16:** Take photo alongside Choose a
file, with review/retake, ordinary attachment checks and retained draft input. Withdraw
the earlier Scan document/shared Expense scanner amendment: no crop/straighten/perspective
correction, OCR, native app or Expense scanner readiness dependency. Prove reusable
capture/upload UI in Leave before promotion. Features/UX/epics/handoff aligned. Stories
4.1–4.6 approved; continue Story 4.7 authenticated private reads. Exact contracts,
source/test coverage, final sizing and readiness remain open; no code authorized.

**Cross-application priority — latest user decision, 2026-10-16:** Retain the existing
Expense React Native mobile application, withdrawing the earlier PWA migration direction.
Finishing Expense still takes implementation priority over Leave. Preserve Leave's
approved internal sequence and original first draft slice, with no readiness waiver.
No Expense migration, implementation or retirement is performed by this note.

Current E1 readiness status is consolidated in
[Remaining E1 gates by timing](#remaining-e1-gates-by-timing--2026-10-05).
That checkpoint supersedes older discussion-status wording below where later accepted
ADR-0049/Leave ADR-0122 or contract refinements resolved it. Historical notes remain
traceable; no unchecked phase exit is silently marked complete.


### E1 pre-story contract checkpoint — 2026-10-01

This is a scoped status update to the existing spine gates, not an SP readiness run
or a competing delivery process. Product agreement does not replace technical
contract completion. Do not require completed Leave application tests as a condition
for writing their implementation stories: define the contract and required evidence
first, then observe acceptance failure and implement/test through authorized BMAD
Build. Existing Phase 1 foundation and generated-slice exit gates remain binding.

| Existing gate | Current design evidence | What remains before dependent story readiness | Owning delivery evidence |
| --- | --- | --- | --- |
| Shared identity/access | Existing Access owner identified; v1 compatibility, v2 fields, actor/person mapping and explicit grant bridge specified in the shared contract | Validate proposed v2 wire schemas and declare owning OpenAPI models in delivery; identity E1-ID and current-check E1-ACCESS boundaries approved; E1-DISCOVERY and E1-LAUNCHER boundaries approved (Scribeswell menu visibility follows ADR-0047); complete schema/baseline ownership inventory and bounded manual three-user PtS transition design; preserve explicit grant/consumer mappings; resolve [application admission scope](../../../platform/docs/architecture/decisions/0046-application-availability-and-access-scopes.md) and approved [Directory filtering/disable behavior](../../../platform/docs/architecture/contracts/application-admission-and-discovery.md) | Characterization, v1/v2 compatibility, restricted-role/revocation and migration tests; no automatic data conversion |
| Shared employment read | One relationship with periods; inclusive dates, work-timezone interpretation, accountless support and ADR-0044 bounded draft observation settled | E1-PEOPLE boundary approved; no-period setup state approved; validate proposed discovery/effective schemas and fixtures, then finalize concrete period/key constraints and owner provisioning design | Same-/cross-organization, period/rehire, changed-input, deadline and unavailable-service tests |
| Draft/API persistence | Routes, input v1, revisions, generation, lock order/timing/retention, structural key/RLS constraints and versioned SHA-256/JCS fingerprint lifecycle now specified | Mutation/read/context/error variants proposed; ordinary validated sign-in return and saved-draft reload agreed; custom recovery record removed; callback and delayed-save ordering evidence still required; validate schema completeness and compatibility fixtures; confirm schema/constraint mapping in the delivery contract; record fingerprint disclosure-risk disposition at the existing pilot security assessment | Concurrent start/save/discard/replay, no-resurrection, cancellation/commit uncertainty and safe log tests |
| Dependency/environment topology | Existing Access/Content/deployment owners are reuse candidates; no Leave deployment exists in scope | Local-first [isolated local/CI topology](./testing/e1-environment-and-dependencies.md) approved 2026-10-02; E1-ENV isolated foundation boundary approved; verify/pin compatible toolchain, real Entra callback target and owner-controlled fixture/bootstrap configuration | Reproducible bootstrap, owned migration filtering and actual environment evidence |
| Browser/performance targets | Current/previous Chrome, Edge, Firefox and Safari approved, including Android Chrome and iPhone/iPad Safari; E1 scenarios mapped | Select exact executable projects/device/OS checks for that policy; qualify the agreed [E1 workload and response targets](./testing/e1-environment-and-dependencies.md#e1-performance-targets--proposal-for-discussion-2026-10-02) at the approved 500/1,000 employee scales; concurrency/history remain declared test assumptions | Browser/keyboard/mobile evidence and measured performance; configured timeout is not a performance result |
| Scaffold and shared UI | Platform-first-consumer work assigned to E1; reusable revision/error/recovery patterns identified | Bounded scaffold scope approved; app-generator E1-P1 boundary approved; authenticated E1-REF boundary approved with earlier Access/identity prerequisites; service-only E1-SERVICE scope approved with explicit API-contract and custom-extension boundaries; E1-WRITE safe owned-write boundary approved before E1-REF; promotion items and exact commands remain | Reference implementation, updated owning templates, generated disposable-app tests and shared control evidence |
| Requirements/stories | Eight epics and E1 work boundaries approved; 18 E1 scenario groups source-mapped | Entry/draft coverage mapped; all five draft boundaries agreed; entry candidate formalized and six user-facing boundaries mapped; finish global FR/NFR/UX coverage, remaining contracts and bounded prerequisite stories, then run SP gate | Requirement-to-test IDs, failing acceptance evidence, exact verification commands/results per owning story |

Contracts: [identity/access/employment](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md),
[shared API errors/recovery](../../../platform/docs/architecture/contracts/api-errors-and-operation-recovery.md),
[Leave drafts](./architecture/contracts/e1-draft-persistence-and-recovery.md).
The [E1 acceptance map](./testing/e1-acceptance-map.md) specifies the required evidence;
no row above is a completed runtime verification claim. E4 byte-identity/provider
and E5 consequential-input gates remain attached to those epics, not waived here.


### Bounded E1 scaffold scope — proposal, 2026-10-02

Scope approved on 2026-10-02, including standard identity/access integration and
optional employment clients; shared owners retain their records/rules. No runtime
implementation or readiness completion is implied.

The builder is not implemented: existing web/backend templates and the owned-service
transaction-context example are inputs, not a working generator. `ui-business` has a
real AppLauncher; `ui-core` and most other shared components remain planned. Inspect
source and tests rather than treating placeholder README lists as delivered features.

Split E1 enabling work into the minimum foundation and promotion within each consuming
item. This is a decomposition within the existing BMAD/Phase 1 gates, not a new phase
or permission to hand-build Leave outside its scaffold requirement.

| Work boundary | Minimum delivery and evidence |
| --- | --- |
| Generator foundation before generating the Leave silo | A supported app/service generation path, names/configuration validation, owner-specific web/API/test/migration layout, reproducible commands and dependencies, environment examples without secrets, linked agent/documentation context and a template version/change record. Generation refuses destructive overwrite. |
| Generated reference acceptance | Generate a disposable domain-neutral app; exercise authenticated organization-scoped read/write with real restricted-role persistence and its service boundary. Observe the acceptance failure before implementing behavior. Verify install, type-check, tests, build, startup/health and local/CI execution. No employee master or Leave policy in this reference. |
| First Leave identity/access consumer | Generate Leave from the verified foundation; extend current Access and add the minimum People read capability through authorized HTTP contracts. Prove real sign-in/org selection and synthetic fixtures. Promote proven typed clients, caller context, safe errors and session-return handling in the same delivery item. |
| First draft persistence/recovery consumer | Implement the agreed Leave draft contract under failing acceptance evidence; promote reusable revision, operation-outcome, transaction/attribution and recovery mechanisms plus generated-sample fixtures. Keep one-active-draft scope optional and domain lifecycle rules application-owned. |
| First shared UI consumer | Reuse existing AppLauncher where the approved shell requires it. Prove accessible organization selection, safe error/status and dialog/form primitives before promotion to the appropriate UI package. Application-specific form composition, leave types, dates/policy and wording remain in Leave. |

A generic reference may use a simple editable example record. It exists only to prove
framework boundaries and commands; do not add a sample HR application, configurable
workflow engine, generic CRUD product or feature-complete template catalogue. Generate
build-time code into its owner; do not import another app/service's server implementation.

Each proven reusable change updates its owning template/package, generation/contract
fixtures, validation, documentation, changelog and any needed existing-app adoption
note together. Generated OpenAPI TypeScript output changes through its generator.
No automatic rewrite of PtS/Scribeswell and no assertion that their existing browser
fixtures prove Leave. Generated context links accepted ADRs and specifications rather
than duplicating a competing product truth or lifecycle.

Worker/outbox, provider/upload and calculation-specific patterns remain tracked in the
existing initial scaffold targets and later consuming epics. E1 does not implement
unused workers or attachment machinery merely to fill every template directory.
Phase 1's generated authenticated vertical-slice exit gate remains binding. Planning
readiness authorizes bounded implementation stories; it does not claim their runtime
exit evidence already exists. Story sizing and dependency ordering still need the
remaining contract/traceability work; these boundaries are not approved story IDs.

Impacts: scaffold and shared UI as above; agent context via generated linked instructions
and existing repository rules; documentation in this authoritative tracker and builder
guidance. No accepted ADR changes. Tests here are required evidence, not executed tests.


Audit gap, 2026-10-02: [E1 security/audit ownership proposal](../../../platform/docs/architecture/contracts/e1-security-audit-ownership.md)
specifies owner events and proposed persistence/export failure behavior for entry,
organization switching and draft lifecycle. Ownership/failure behavior approved;
ordinary own-draft reads need no separate audit event after the user-approved
simplification. Attribution stays on the draft; selection-event schemas remain proposed.
Validate schema/fixture completeness before dependent story readiness; provider
retention/investigation evidence remains an existing pre-pilot operations requirement.

### Phase 0 — Planning and architecture baseline

- [x] Capture initial business requirements
- [x] Confirm multi-NGO membership
- [x] Confirm supported leave units
- [x] Confirm projected-accrual and balance-override behavior
- [x] Confirm configurable approval and self-approval
- [x] Confirm Entra ID through Supabase Auth for MVP
- [x] Decide FastAPI Content Service direction
- [x] Create functional specification and implementation tracker
- [x] Review and approve the role/permission matrix
- [x] Review and approve the state machines
- [x] Resolve the initial product decisions in this document
- [x] Record accepted architecture decisions as platform and Leave ADRs

**Exit gate:** Requirements, scope, roles, states, and service boundaries are
approved; no unresolved question changes the core data model.

### Phase 1 — Platform scaffold and development baseline

- [ ] Add a `leave` entry to the App Directory, initially disabled
- [ ] Generate the Leave silo from `platform/builder-cli`
- [ ] Establish local commands for web, API, database, workers, and shared services
- [ ] Add environment validation and `.env.example` files without secrets; separate restricted runtime and deployment-only migration identities under [platform ADR-0017](../../../platform/docs/architecture/decisions/0017-runtime-and-migration-database-authority.md)
- [ ] Establish CI for linting, formatting, type checks, unit tests, migrations, and builds
- [ ] Add health/readiness endpoints and structured error responses
- [ ] Apply platform ADR-0031 stable error identifiers and typed safe details; agree compatible wire fields, align OpenAPI/generated frontend/framework adapters, and verify localized behavior and unknown-error fallback
- [ ] Add OpenAPI generation and strict Leave web client generation/validation
- [ ] Establish correlation IDs, structured logs, and tenant-aware audit context
- [ ] Add builder generation tests that create a disposable app and verify install,
  type-check, test, build, and API health
- [ ] Establish scaffold changelog and existing-app migration-note conventions
- [x] Run `[PC]` `bmad-project-context` to establish verified repository agent
  instructions linked to specifications, ADRs, tests, and scaffold rules
  - Evidence (2026-09-06): established root `AGENTS.md`, verified against
    `5f1c2d5`; audited repository commands, application/service boundaries,
    authoritative specifications, ADRs, and scaffold state. No Leave application
    implementation was performed.
- [x] Run `[PRD]` `bmad-prd` in validate/update mode against the approved Leave
  feature specification; resolve findings without creating a competing source
  - Evidence (2026-09-20): requirements revalidation and approved [finding dispositions](../../../_bmad-output/planning-artifacts/prds/prd-leave-2026-09-14/review-resolution.md) complete; ADR-0088/0089 resolve product gaps, stale controls corrected, operational targets assigned owners/gates. Architecture and implementation readiness remain pending.
- [x] Run `[CU]` `bmad-ux` because the employee application experience is material
  - Evidence (2026-09-20): approved and finalized [DESIGN](../../../_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/DESIGN.md) and [EXPERIENCE](../../../_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/EXPERIENCE.md), 28 promoted visual references, both final review lenses and resolved findings, required editorial polish, and source checks recorded in the [handoff coverage](../../../_bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/handoff-coverage.md). No Leave implementation or browser/AT compliance claim.
- [x] Run `[CA]` `bmad-architecture` using the existing platform/Leave ADRs as inputs; apply the [operational target ownership and decision gates](./features.md#operational-target-ownership-and-decision-gates) before architecture completion and relevant story planning
  - Evidence (2026-09-23): finalized the [architecture spine](./architecture/ARCHITECTURE-SPINE.md), reconciled requirements/UX, completed independent rubric, adversarial and technology reviews, and passed structural/link/whitespace checks. [Review resolution](../../../_bmad-output/planning-artifacts/architecture/architecture-leave-2026-09-20/review-resolution.md) retains explicit pre-story contracts and the signed-upload provider feasibility gate. Stories/readiness remain pending; no runtime implementation.
- [ ] Run `[CE]` `bmad-create-epics-and-stories`, then `[SP]`
  `bmad-sprint-planning` as the implementation-readiness gate
- [ ] Use `[BC]` `bmad-customize` to add ATDD/TDD, tenant-security, scaffold,
  shared-UI, agent-context, documentation, and ADR impact gates to BMAD workflows
- [ ] Reduce `platform/prompts` from a competing SPDD lifecycle to verified
  Agriplatform-specific context and safeguards; retain useful history
- [ ] Establish the cross-stack ATDD/TDD test layout, commands, deterministic fixtures,
  test IDs, requirement traceability, and concise result reporting
- [ ] Add a builder-generated reference acceptance scenario and focused TDD example
- [ ] Add CI lanes for focused/unit, component, API/integration, contract, database/RLS,
  worker/provider, and critical browser acceptance tests

**Exit gate:** A generated, authenticated vertical slice runs locally and in CI.

### Continuous requirement — applies to Phases 2 through 10

- [ ] Perform and record a scaffold impact review for every completed feature
- [ ] Update app/service templates in the same change when a reusable pattern is proven
- [ ] Update generator tests, validation rules, docs, changelog, and migration notes
- [ ] Verify a newly generated disposable application remains healthy
- [ ] Start and end each phase with `[BH]` `bmad-help` in a fresh context and record
  the recommended/completed BMAD workflows
- [ ] Perform and record an agent-context impact review for every substantial change
- [ ] Update reusable Agriplatform norms, safeguards, context, changelog, validation,
  and generated app context in the same change
- [ ] Synchronize verified implementation facts without silently rewriting approved
  product specifications or ADRs
- [ ] Define acceptance examples and observe the expected failure before implementing
  each user-visible behavior or cross-service contract
- [ ] Use focused red-green-refactor tests and add characterization coverage before
  risky changes to insufficiently tested code
- [ ] Record requirement-to-test traceability and concise commands/results as
  completion evidence

These are recurring controls rather than a one-time phase. A phase cannot pass its
exit gate while applicable BMAD, scaffold, or agent-context work is incomplete.

### First end-to-end delivery slice after readiness

After architecture, stories and relevant readiness gates are complete, the first
working application slice is: **Sign in → select NGO → open a leave draft → enter
details → autosave → close → reopen**. Deliver the minimum prerequisite shared identity,
access, shell and persistence contracts needed for this authorized slice, respecting
existing owner boundaries; this sequence does not waive Phase 1 or dependency gates.

Prove shared shell navigation, current authorization, tenant-scoped database access,
record attribution, safe errors and revision-protected autosaving together. Include
acceptance scenarios for a second tab, expired sign-in with return navigation, failed
save and successful draft resumption. Drafts reserve no entitlement and this slice
does not imply that submission, policy calculations or approval are implemented.

Use the existing ATDD/TDD workflow and update reusable scaffolding in the same delivery
item where proven applicable. This is agreed sequencing, not authorization to begin
Leave implementation before readiness. Keep subsequent stories focused rather than
expanding this initial slice into the entire application.

### Phase 2 — Identity, tenants, organization structure, and authorization

**BMAD path:** Full-flow, high-risk platform work. In a fresh context, begin with
`[BH] bmad-help` to confirm readiness and the next story from sprint status. Execute
each identity/tenancy story with `[BD] bmad-build`. Use `[CR] bmad-code-review` as an
additional independent gate for every story that changes authentication, JWT claims,
membership switching, authorization, or RLS.

- [ ] Confirm `[SP]` sprint readiness is `PASS` for Phase 2 stories; correct
  `CONCERNS` or `FAIL` before implementation
- [ ] Define traceable ATDD scenarios for multi-NGO login, invitation, switching,
  role differences, suspension, and cross-tenant denial before production code
- [ ] Use red-green-refactor inside every identity story and characterization tests
  before changing existing JWT hooks/RLS behavior
- [ ] Configure Microsoft Entra login through Supabase Auth
- [ ] Add secure invitation/onboarding; login alone grants no NGO access
- [ ] Apply platform ADR-0035 structural database constraints in reviewed models/migrations: required/reference fields, scoped uniqueness and local tenant relationship integrity; verify concurrent/alternate writes, restricted-role behavior and safe error mapping alongside RLS
- [ ] Apply platform ADR-0034 database-enforced employee/NGO active-draft uniqueness and atomic create-or-resume; test simultaneous creation, no overwrite, separate scopes and closed-draft retry safety
- [ ] Apply platform ADR-0033 draft lifecycle guards: atomic submission/reservations/draft closure, late save/create-retry protection after submission/discard, explicit new draft and authorized lifecycle-conflict navigation
- [ ] Verify Leave ADR-0118 revision-safe autosave: conflicting tabs pause and retain edits, saved-draft review rechecks access, same-tab saves serialize/coalesce, newer typing survives old acknowledgements and uncertain retries remain duplicate-safe
- [ ] Verify platform ADR-0032 session renewal/re-authentication return to prior NGO/page/request/drawer and recoverable draft, with current access checks, safe account-change/invalid-target fallback and no automatic or duplicate submission
- [ ] Implement NGO switcher and refresh active-org claims after switching
- [ ] Replace enum-only global roles with extensible, tenant-scoped role identifiers
- [ ] Connect Leave role/permission catalog to shared access management and reusable role controls; combine scoped grants without bypassing approval assignment, self-approval, or document rules; define shared runtime HTTP contracts before implementation
- [ ] Implement application-maintained default roles and advanced custom-role copies backed by explicit business permissions; review new grants for custom roles (platform ADR-0011). Include temporary-approver exception capability in Leave Manager by default without granting approval authority
- [ ] Deliver shared custom-role lifecycle: blank creation, separate duplication, holder-impact review, unassigned-only deletion, preserved audit, clickable holders and return-to-origin (platform/EXPERIENCE.md)
- [ ] Add Leave Manager and unified Approver role with relevant business permissions; enforce supervisor/final responsibilities through assigned workflow steps (ADR-0082)
- [ ] Consume shared employment with nullable department/location and manual supervisor assignments under platform ADR-0041; establish authorized shared administration, scoped references and effective-dated history without duplicating an employee master. Use supervisor-based direct-report teams under ADR-0125, with no independent team catalogue; no organization-chart editor or Graph import dependency
- [ ] Deliver approved employee Leave-settings summary and focused edits using shared person identity, visible inherited/overridden values and separate balance actions; enforce action permissions without hiding permitted read-only history
- [ ] Model configured approvers and delegated/acting approvers
- [ ] Provide editable one-supervisor starter approval policy (self-approval off, three-day reminders/seven-day escalation), with client-confirmed entitlement/schedules/holidays and approval-route setup checks
- [ ] Preserve draft and block submission when no eligible approval route is configured; show setup-needed status and flag authorized route repair, distinct from handled absence or applicant coverage gaps
- [ ] Implement optional directional absence policy (ADR-0080/0081): final approver may decide alone for absent supervisor, never the reverse; explicitly authorized temporary final approver may do so when both are absent; recognize fallback coverage and restore outstanding supervisor step on return before final decision; retain reminders while waiting
- [ ] Allow authorized Leave Manager appointment of active NGO members without permanent approval roles; grant only specified temporary responsibilities/dates, preserving membership/self-approval/document boundaries (ADR-0079)
- [ ] Require coverage of applicants' approval responsibilities before final approval, including automatic completion; allow submission with a gap and authorized reasoned exceptions while retaining gap visibility (ADR-0078)
- [ ] Deliver dated approval cover for every step, delegate eligibility/absence/conflict checks, audited rerouting, alternate Leave Manager cover, and visible no-cover cases (ADR-0076/0077); include authorized scheduled return with eligibility recheck, audit, notification, and failed-return handling
- [ ] Add tenant-isolation policies and negative cross-tenant tests
- [ ] Ensure suspended memberships immediately lose access
- [ ] Run `[CR]` after each security-boundary story and resolve all blocking/high
  findings before merge
- [ ] End Phase 2 with `[BH]`, update sprint status/evidence, and record BMAD,
  scaffold, shared-UI, agent-context, documentation, and ADR impacts

**Exit gate:** Sprint readiness passed; a multi-NGO user can switch context safely;
every API/database operation is scoped to the active membership; ATDD, RLS negative,
contract, and focused TDD suites pass; required code reviews and impact records are
complete.

### Phase 3 — Shared design system and application shell

- [ ] Define semantic design tokens, themes, typography, spacing, and status colors
- [ ] Establish owned shadcn primitives in `platform/ui-core`
- [ ] Establish generic AppShell, AppLauncher, tenant switcher, notification inbox,
  forms, tables, calendar shell, file uploader, empty/error/loading states
- [ ] Add a component catalogue and usage guidance
- [ ] Add automated accessibility and visual regression checks
- [ ] Implement responsive Leave navigation and role-aware landing pages
- [ ] Expand the shared libraries incrementally with each Leave feature: implement
  in the Leave silo first, promote only domain-neutral components, and add catalogue,
  accessibility, visual, and interaction coverage when promoted

**Exit gate:** Shared components are accessible, documented, and consumed by the
Leave shell without Leave-specific logic entering the common library. Every
completed feature has reviewed whether newly proven generic components should be
promoted to `ui-core` or `ui-business`.

### Phase 4 — Content Service migration

- [ ] Inventory the current `cs` schema, functions, clients, and providers
- [ ] Define Pydantic/OpenAPI contracts and compatibility mapping
- [ ] Scaffold `services/content-service` using the existing FastAPI service pattern
- [ ] Port JWT validation and tenant-context resolution
- [ ] Port Azure Blob and Supabase Storage adapters
- [ ] Port upload-session creation, direct upload, finalization, and read URL behavior
- [ ] Add MIME sniffing, file/count/total-size rules, checksum verification, and an
  extensible content-safety status (malware scanning deferred)
- [ ] Add authorization/capability contract used by domain APIs
- [ ] Add cleanup, retention, retry, and reconciliation jobs
- [ ] Add unit, contract, provider-emulator, tenant-isolation, and failure-path tests
- [ ] Retire the non-production Edge Function prototype after FastAPI contract and
  provider-parity tests pass; no receipt-consumer migration is required

**Exit gate:** Leave uses the FastAPI Content Service; provider parity, security
tests, telemetry, and replacement of the non-production prototype are verified.

### Phase 5 — Leave configuration foundation

- [ ] Create the tenant-scoped `leave` schema
- [ ] Implement jurisdictions, locations, holiday calendars, and observed holidays
- [ ] Implement effective-dated employee work schedules including breaks and timezone; one explicit work profile with NGO fallback, location suggestions and supervisor-based team grouping without silent reassignment, inherited values and overrides/reset, reason and impact review preserving history
- [ ] Implement versioned leave-type CRUD and archive/restore
- [ ] Design stable configuration identities, archive timestamps, effective-dated calculation versions and request snapshots (ADR-0086); preserve audit separately and enforce work-profile archive dependencies
- [ ] Implement policy versions: units, accrual, carry-over, expiry, limits, notice,
  explicit policy assignment, documentation, privacy, balance behavior, and workflow assignment
- [ ] Implement effective-dated employee entitlement overrides with reason and preview; one Edit employee entitlement action for policy/custom recurrence restricted to leave-period boundaries (ADR-0083), default next boundary, separate one-off adjustment
- [ ] Implement Leave Manager configuration screens and audit history
- [ ] Deliver approved work-profile list/edit/review: profile name, working week and employee count; effective-dated changes with separate inherited effects, retained overrides and existing-request attention; preserve recorded calculations
- [ ] Keep setup checklist focused on application configuration; exclude consultant email status and a standard opening-balances row, preserving consultant-runbook approval and actual balance-issue handling
- [ ] Implement optional period-relative carry-over expiry with last-usable-date preview (ADR-0085/0089); test agreed month-end/leap-day examples, direct multi-month calculation, inclusive eligibility and preservation of earlier expiry
- [ ] Deliver shared date-entry behavior in Apply: calendar/typed range, single-date partial duration, incomplete/reversed-range feedback, and no-working-time explanation without misleading zero calculations
- [ ] Apply shared loading/empty/filtered-empty/retry/export states, preserve filters and valid retained data on refresh failure, and distinguish unavailable team data from no absences
- [ ] Verify shared focus transitions, preserved fields across responsive surfaces, validation-error navigation, consequential status announcements and accessible calendar selection in Leave screens
- [ ] Apply shared administrative Edit → Review → Confirm behavior: no effects before confirmation, changed-form discard guard, related-record return preservation, failed/uncertain confirmation recovery, and refreshed review after concurrent changes
- [ ] Add seed/demo configurations without representing them as legal advice

**Exit gate:** A Leave Manager can configure an NGO without database access and
historical policy meaning is preserved after changes.

### Phase 6 — Balance ledger and accrual engine

- [ ] Implement immutable balance ledger entries
- [ ] Deliver approved employee balance detail: available/remaining/reserved breakdown, pending-request links and return context, expandable hours/history with actor/reason, and history-year filtering that leaves current balance unchanged; avoid double counting reservations
- [ ] Deliver Review then Confirm adjustment, correction by another explained entry, employee notifications and authorized details; renewed acknowledgement only for increased unpaid amounts
- [ ] Deliver history year bounds preserving recorded leave/rehire, muted out-of-employment dates, and per-user/NGO Calendar/List preference
- [ ] Define canonical duration storage in minutes and policy-specific display conversion
- [ ] Verify calculation acceptance scenarios: live daily earning, partial monthly employment, expiry-before-earning, cancellation/correction impact with preserved evidence and cap safeguards, changed confirmation inputs, duplicate submission and concurrent consumption; distinguish backend evaluation from frontend refresh and do not introduce a stored balance total
- [ ] Implement immutable actual opening-balance, adjustment, reservation, consumption,
  reversal and unpaid/negative events; distinguish derived automatic earning, carry-over
  and expiry effects from actual events and decision evidence without double counting;
  retain required auditable carry-over/expiry explanations and evidence under their ADRs
- [ ] Implement front-loaded annual and anniversary accrual
- [ ] Implement monthly accrual and starter/leaver proration
- [ ] Implement projected balance calculation for requested dates; expose consequences in Apply with expandable explanation, deferring standalone calculator/graph (ADR-0084)
- [ ] Implement effective-dated recalculation and adjustment preview
- [ ] Implement authoritative on-demand entitlement for daily/upfront/monthly modes under [ADR-0090](./architecture/decisions/0090-annual-entitlement-availability-options.md), retaining manual grants and reconciliation; apply start-of-day daily availability (ADR-0091) and apply cumulative daily precision (ADR-0092) and historical cap/resumption rules (ADR-0093) with precise cap-before-rounding behavior (ADR-0095) and daily employment boundaries (ADR-0094) plus prospective daily policy-rate segmentation (ADR-0096) and apply complete-month cumulative rounding (ADR-0097) and boundary-only availability-method transitions (ADR-0098) and next-instalment monthly rate changes with effective-date notifications (ADR-0101) and next-period upfront annual changes (ADR-0102) and implement/verify monthly partial-employment and cumulative precision rules (ADR-0104/0105) with aligned, anchored boundaries (ADR-0099/0100); settle physical historical interval/bucket and event/snapshot representation before affected story readiness
- [ ] Add deterministic clock-based and property/invariant tests

**Exit gate:** Actual events reconcile; current/projected balances are reproducible
from effective-dated inputs and immutable actual events. Repeated calculation does
not duplicate earning, and retrying actual mutations does not duplicate their effects.
No automatic accrual posting job or stored current balance is required.

### Phase 7 — Applications, validation, attachments, and approvals

- [ ] Return confirmed submissions to My Leave with preserved context, brief confirmation and optional View request, updated list status and removed draft indicator; keep failed/uncertain forms open and check outcome before retry (ADR-0087)
- [ ] Derive setup-section Not started / Needs review / Ready / Couldn’t check from saved configuration and checks; retry failed assessment independently, keep zero-employee People section Not started and refresh after settings changes without manual completion flags
- [ ] Implement initial unpaid on-behalf response handoff: manager submits, employee alone acknowledges exact current amount in the submitted request, employee draft remains unchanged, final approval/consumption wait even for sole submitting approver; test stale amount and denied proxy acknowledgement (ADR-0088)
- [ ] Implement draft and submission APIs
- [ ] Implement working-time calculation for full day, half day, and hour ranges
- [ ] Implement overlap, schedule, holiday, notice, backdating, eligibility, and
  attachment validation
- [ ] Reserve projected balance on submission
- [ ] Integrate attachment upload, association, scanning status, and secure retrieval
- [ ] Implement configurable workflow snapshots and approver resolution
- [ ] Implement supervisor balance override with mandatory reason and explicit consequence
- [ ] Implement auditable exception allocations that can distribute one request
  across discretionary paid leave, another eligible paid balance, and unpaid leave
- [ ] Implement Leave Manager on-behalf submission/approval with separate permission,
  mandatory reason, original employee attribution, and conflict-of-interest checks
- [ ] Implement self-approval rules and duplicate-step collapse
- [ ] Implement approve, reject, withdraw, resubmit, direct approved-leave
  cancellation, and admin override
- [ ] Add concurrency/version checks and idempotency keys for commands under [platform ADR-0012](../../../platform/docs/architecture/decisions/0012-operation-identity-idempotency-and-tracing.md); verify lost-response retries, concurrent duplicate attempts, changed-payload rejection, tenant/actor isolation and atomic outcome recording
- [ ] Apply [platform ADR-0013](../../../platform/docs/architecture/decisions/0013-explicit-revisions-for-reviewed-changes.md): explicit server-managed revisions, atomic expected-revision checks, stale-review recovery and protected revalidation of related balances/policies across every affected write path
- [ ] Deliver the in-request balance-override → revised unpaid acknowledgement → remaining approval journey, with actor/reason, exact-amount recheck, employee response prompt and approver waiting state
- [ ] Persist complete transition and approval history

**Exit gate:** All state transitions and balance effects pass authorization,
concurrency, audit, and reversal tests.

### Phase 8 — Notifications

- [ ] Implement restricted cross-NGO queue discovery and per-item NGO transactions under platform ADR-0026 and Leave ADR-0115 using one owner-specific worker identity; verify real runtime-role permissions, queue ownership and pooled-context isolation; no per-NGO secrets
- [ ] Implement the Leave-owned PostgreSQL outbox and separate worker under ADR-0114, initially one instance: bounded claims, stale-claim completion protection, restart recovery, HTTP handover and receiver deduplication; no broker/Temporal/custom orchestration engine required for MVP
- [ ] Apply platform ADR-0028 event type/version contracts and queued/failed-event compatibility tests across deployment; retain unsupported work and coordinate producer/consumer rollout and handler retirement; no MVP schema registry
- [ ] Keep outbox schema application-owned and implement ADR-0116 notification relevance: skip obsolete unhanded action requests with reason, preserve audit/payload, distinguish factual notices and accepted/uncertain remote handover
- [ ] Define versioned Leave domain events and transactional outbox with stable event IDs and originating operation links under platform ADR-0012; verify duplicate-safe acceptance and preserved tracing across retries
- [ ] Implement standard shared English notification templates identifying the relevant
  organization, with clear dates and localization-ready content; defer custom logos/colors,
  editable templates and Portuguese delivery under Leave ADR-0130
- [ ] Verify ADR-0117 delayed/reversed notifications: dated event wording, current authorized request links and independent progress of newer messages; no email-ordering mechanism
- [ ] Implement asynchronous email delivery, retries, dead-letter handling, and deduplication
- [ ] Apply notification-only platform ADR-0029: 90-day original-event retry expiry, 90-day terminal detail retention, acceptance-based receiver deduplication retention with unresolved-work protection, expired-event rejection after cleanup and audited new-notification recovery without repeating leave actions
- [ ] Apply platform ADR-0024 to owned handover: classify failures, retain exhausted work, alert operations and provide scoped audited recovery with state/claim checks and stable event identity; shared notification service owns post-acceptance channel recovery
- [ ] Implement in-app notification inbox and read state
- [ ] Implement secure action links that lead to authenticated application pages
- [ ] Add reminders, escalation policy, and delivery-status administration
- [ ] Prevent sensitive leave details from leaking into subject lines or shared channels

**Exit gate:** Domain commits cannot lose notifications; retries do not create
duplicate user-visible messages; failures are observable and recoverable.

### Phase 9 — Calendars, dashboards, and reporting

- [ ] Employee calendar, applications, balances, and ledger view
- [ ] Unified Approvals queue with assigned supervisor/final-step context and permitted calendar/capacity information; no separate permanent approval roles or queues
- [ ] Leave Manager operational dashboard and pending-aging view
- [ ] Privacy-aware shared calendar labels
- [ ] Filters for team, department, location, status, type, and date
- [ ] CSV exports with authorization and audit controls
- [ ] Performance tests for organization-wide calendar ranges

**Exit gate:** Each role sees only permitted detail and common queries meet agreed
performance targets.

### Phase 10 — Hardening, rollout, and operations

- [ ] WCAG 2.2 AA review including keyboard and screen-reader flows
- [ ] Mobile/responsive usability review
- [ ] Threat model for tenant switching, approvals, attachments, signed URLs, and exports
- [ ] Demonstrate Leave ADR-0120 alert thresholds through controlled failures and recovery; verify shared incident grouping, healthy idle worker detection and overdue notification age across retries under platform ADR-0037
- [ ] Demonstrate Leave ADR-0119 recovery targets: at most one-hour loss, essential service within four hours of incident declaration, thirty-day backup retention; consistent DB/document/dependency recovery, outbound work held until replay checks, rehearsal before pilot then quarterly/after major backup changes
- [ ] Verify backup/restoration and migration-failure recovery under [platform ADR-0020](../../../platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md), including previous-version compatibility, blocked activation on failure, migration coordination and explicit recovery; no automatic migration downgrade
- [ ] Deliver the [bounded MVP monitoring scope](../../../platform/docs/operations/observability-and-ai-investigation-direction.md): safe structured logs and operation IDs, health checks, actionable operational alerts, basic OpenTelemetry API/shared-service tracing and one working setup verified with a simple failure; no Loki/OpenSearch comparison or AI workflow gate
- [ ] Verify separate API readiness, worker progress and notification-delivery signals: provider failure preserves unrelated API availability; stuck eligible work is detected; idle empty queues remain healthy
- [ ] Verify platform ADR-0027 shutdown drain, bounded forced termination and recovery; deployment supervisor emits warning/log even if worker cannot; report replacement health/progress truthfully and configure repeated-failure alerts
- [ ] Load, failure, retry, and worker-restart tests
- [ ] Privacy, retention, and jurisdictional configuration review, including the
  proposed two-year default for medical attachments
- [ ] Pilot NGO data import and reconciliation
- [ ] Provide consultant-operated import tooling with templates, authorized import contracts, validation/preview, row errors, duplicate prevention, audit, and client reconciliation summary; defer self-service upload UI
- [ ] Record authorized client email approval against the exact import batch before apply; revised data requires renewed approval, without a separate client confirmation page
- [ ] Validate source balance dates/units and future-leave/reservation inclusion, reconcile transferred requests exactly once, and follow the [migration runbook](./operations/migration-runbook.md)
- [ ] Agree old-system change cutoff and Leave handover; reconcile export-to-cutover changes and obtain renewed approval for revised batches before going live
- [ ] User acceptance testing for every role
- [ ] Operations runbooks, support guide, and release checklist; verify agreed signed-operation lifetimes, recovery objectives through restoration rehearsals, critical alerts, browser coverage and workload/performance targets before pilot
- [ ] Enable Leave in App Directory for pilot memberships

**Exit gate:** Product owner, security reviewer, and pilot NGO sign off; monitoring,
support, backup, and rollback are operational.

### Post-MVP roadmap

- [ ] Content-owned malware scanning hardening upgrade — confirmed 2026-10-16;
  deferred because current hosting lacks memory for a self-hosted scanner. Reassess
  provisioned capacity versus a suitable managed service; no engine/vendor/date selected.
  Scan exact finalized bytes before exposing them when scanning is enabled, retaining
  pending/no-threat-detected/rejected/unscannable outcomes, bounded retry/recovery,
  signature/engine evidence, operational ownership and privacy-safe handling. Bind
  treatment of encrypted/unsupported content, scanner outages and any existing-file
  rollout before delivery. Prove detection/failure paths and no readiness bypass.
  MVP retains extensible safety states and current type/size/checksum/authorization
  protections; this upgrade is not an additional MVP or pilot-readiness gate.

- [ ] Evaluate monitoring investigation usability and Loki/OpenSearch alternatives when operational experience justifies it; future AI diagnosis and approved regression-test/fix/draft-PR workflow follow the platform direction, outside Leave MVP


- [ ] Shared Microsoft Graph reporting-relationship synchronization, separate from calendar integration; preserve authorized overrides, NGO/approval eligibility checks, and explicit handling of changes affecting pending requests
- [ ] Microsoft 365/Outlook calendar synchronization
- [ ] Google Calendar synchronization
- [ ] Teams, Slack, and SMS notification adapters
- [ ] SCIM/directory provisioning
- [ ] Tenant-managed identity providers; reassess ZITADEL/Keycloak
- [ ] Advanced staffing and capacity planning
- [ ] Policy template library by jurisdiction
- [ ] Portuguese for Mozambique and Angola as the next planned language; select release date and validate wording, regional formats, and notification text for both audiences
- [ ] Further localization and additional languages
- [ ] Payroll/HRIS integrations

## Cross-cutting test matrix

Every applicable feature must be tested across:

- Two users in the same NGO with different roles
- One user belonging to two NGOs with different roles and policies
- Two unrelated NGOs attempting cross-tenant access
- Active, suspended, and ended employment/membership
- Standard, non-standard, and timezone-different work schedules
- Current and future-dated policy versions
- Concurrent submissions/approvals
- Retry of commands, jobs, uploads, and notification deliveries
- Sensitive versus ordinary leave types and attachments

ATDD scenarios provide the outer proof of accepted behavior. TDD supplies focused
domain, component, API, persistence, adapter, and defect feedback underneath them.
Use browser tests only for critical journeys that cannot be proved more reliably at
a lower boundary. Before AI-assisted refactoring, establish characterization tests
for relied-upon behavior that lacks adequate coverage.

## Resolved product decisions

- [x] One NGO may contain employees working in multiple countries; jurisdiction,
  location, calendar, schedule, and policy assignments therefore apply below NGO level.
- [x] Hourly leave uses 0.5 hour (30-minute) increments.
- [x] Half-day leave consumes 50% of the employee's configured scheduled hours for
  that day (for example, 4 hours of an 8-hour day).
- [x] A balance deficit becomes unpaid leave by default. An authorized exception
  may distribute the request across discretionary paid leave, another eligible
  paid balance, and unpaid leave.
- [x] A Leave Manager may submit or approve on behalf of an employee under a
  separate permission and complete audit trail.
- [x] Medical-document retention is configurable by NGO/jurisdiction; use two years
  after request closure as the initial default pending legal/privacy review.
- [x] Attachments are 10 MB per file, initially PDF/JPEG/PNG, with no more than 3
  files and 20 MB total per request.
- [x] Malware scanning is deferred from MVP; the design retains a content-safety hook.
- [x] Approved cancellation requires no further approval and reverses balance effects.
- [x] Capacity warnings are informational in MVP.

## Blockers and risks

| Date | Status | Risk/blocker | Owner | Mitigation or next action |
|---|---|---|---|---|
| 2026-09-23 | Open — before attachment story readiness | Standard Supabase signed-upload API documents two hours, while platform ADR-0036 targets fifteen minutes | Content/Platform | Prove a supported provider-enforced adapter path and expiration tests; frontend expiry is insufficient. Otherwise propose a superseding decision; see the architecture spine provider constraint |
| 2026-09-01 | Open | Current role and permission types are PostgreSQL enums, which will become cumbersome as apps and roles grow | Platform | Design an extensible permission catalog before Phase 2 migration |
| 2026-09-01 | Open | The current content upload prefix and authorization are receipt/finance-oriented | Platform | Replace the prototype with a domain-neutral namespace and authorization capability in the FastAPI contract |
| 2026-09-01 | Open | A two-year medical-document retention default may not suit every operating jurisdiction | Product/Security | Require NGO/jurisdiction override and legal/privacy review before production |
| 2026-09-01 | Open | Hour-to-day conversion can corrupt balances if schedules change | Leave | Store calculated minutes and schedule/policy version snapshots |

## Decision log

| Date | Decision | Rationale | Revisit trigger |
|---|---|---|---|
| 2026-09-15 | Use duration-only partial days with same-date warnings and daily limits | Leave precise timing to employee/supervisor while preserving accurate deductions and capacity validation. See Leave ADR-0074 | Need for exact-time scheduling |
| 2026-09-15 | Adopt calm, spacious, restrained visual design using platform controls | Reduce clutter while preserving visible actions, decision-critical information, and accessibility. See Leave ADR-0073 | UX design and accessibility validation |
| 2026-09-15 | Support complete employee and approver workflows on phones | Preserve decision information and accessibility with responsive calendar/list presentation. See Leave ADR-0072 | Mobile UX validation findings |
| 2026-09-15 | Keep NGO context in header and simplify pre-submission summary | Avoid repeated context for single-NGO users and unnecessary approver detail. See Leave ADR-0071, superseding part of ADR-0069 | Submission or multi-NGO UX findings |
| 2026-09-15 | Simplify post-submission confirmation and preserve reliable recovery | Avoid unnecessary workflow detail while showing status and required employee actions. See Leave ADR-0070 | Submission UX findings |
| 2026-09-15 | Require a submission summary and exact unpaid-amount acknowledgement | Make the proposed financial consequence explicit while keeping fully funded submission simple. See Leave ADR-0069 | Submission UX or acknowledgement findings |
| 2026-09-15 | Save original-NGO drafts before switching with explicit failed-save choices | Preserve work and tenant isolation during NGO changes. See Leave ADR-0068 | Switching UX or isolation findings |
| 2026-09-15 | Autosave unfinished requests with truthful save status and explicit Save and close | Preserve entered work without confusing drafts with submitted reservations. See Leave ADR-0067; button wording superseded by Close under ADR-0075 | Draft UX validation findings |
| 2026-09-15 | Use permission-based role sections and separate required-work badges | Support multi-role users without mixing unresolved work with unread notifications. See Leave ADR-0066 | Navigation UX findings |
| 2026-09-15 | Give MVP Leave Managers NGO-wide scope and an administrative home screen | Simplify employee scope while retaining distinct approval, correction, adjustment, and document permissions. See Leave ADR-0065 | Need for department/location-restricted administration |
| 2026-09-15 | Prioritize required decisions and team availability on approver home | Support informed approval with visible exceptions and existing field/privacy permissions. See Leave ADR-0064 | Approver UX validation findings |
| 2026-09-15 | Prioritize applying, balances, and required responses on employee home | Make everyday actions and request progress easy to find. See Leave ADR-0063 | Employee UX validation findings |
| 2026-09-15 | Pair an employee year calendar with history list and per-type balances | Support understanding of past leave and remaining entitlement with accessible detail and pilot tasks. See Leave ADR-0062 | Employee UX validation findings |
| 2026-09-15 | Persist user language choice across NGOs and use it for personal notifications | Keep the experience consistent with English fallback while preserving business rules. See Leave ADR-0061 | Changes to language preference scope |
| 2026-09-15 | Target Mozambique and Angola for initial Portuguese localization | Match the confirmed audiences and validate regional wording and formats for both. See Leave ADR-0060 | Portuguese delivery and regional feedback |
| 2026-09-15 | Escalate unanswered required approvals after seven calendar days by default | Notify authorized Leave Manager while preserving explicit permissioned rerouting. See Leave ADR-0058 | Changes to escalation policy |
| 2026-09-15 | Default Leave to English with unambiguous dates and prepare for Portuguese | Support near-term localization without coupling translated labels to business logic. See Leave ADR-0059 | Portuguese variant/release planning |
| 2026-09-15 | Default approval reminders to three calendar days with policy configuration | Prompt actionable approvers without changing decisions or routing. See Leave ADR-0057 | Changes to reminder behavior |
| 2026-09-15 | Mark notifications read on opening and scope bulk read to the active NGO | Keep read counts useful without conflating reading with business approval or acknowledgement. See Leave ADR-0056 | Changes to notification read behavior |
| 2026-09-15 | Scope notification details to the active NGO and show unread selector badges | Provide count-only awareness across active memberships without exposing other NGO details. See Leave ADR-0055 | Changes to notification or selector scope |
| 2026-09-15 | Notify employees of administrative corrections in both channels | Keep changes transparent while requiring responses only for increased requested unpaid amounts. See Leave ADR-0054 | Changes to correction notification requirements |
| 2026-09-15 | Restrict administrative corrections to scoped Leave Managers with on-behalf permission | Keep organization administration separate from Leave correction authority. See Leave ADR-0053 | Changes to correction permissions |
| 2026-09-15 | Prevent active-request overlaps and support authorized corrections across past, current, and future leave | Avoid duplicate absence while allowing records to match actual events with preserved history. See Leave ADR-0052 | Changes to overlap or correction authority |
| 2026-09-15 | Permit backdated requests without a fixed cutoff, subject to normal review | Avoid an unnecessary age-based restriction while preserving reasons, historical calculations, and audit history. See Leave ADR-0051 | Closed-period requirements or changes to backdating policy |
| 2026-09-15 | Default minimum notice to zero calendar days and permit explained short-notice requests | Support policy-specific notice without blocking explained exceptions. See Leave ADR-0050 | Changes to notice requirements |
| 2026-09-15 | Enforce the known employment end date at submission and final approval | Keep requested dates within employment and route affected existing requests to explained correction/cancellation. See Leave ADR-0049 | Changes to employment-date eligibility |
| 2026-09-14 | Recalculate upfront grants after employment departure under the policy's proration rule | Correct excess grants transparently while preserving no-proration choices and review of spent deficits. See Leave ADR-0048 | Changes to departure entitlement rules |
| 2026-09-14 | Make month-end accrual usable on its grant date | Keep monthly timing consistent with existing effective-date availability. See Leave ADR-0047 | Changes to month-end availability |
| 2026-09-14 | Grant upfront-policy mid-month joiners at employment start; month-end joiners at month-end | Apply policy proration while preserving monthly grant timing and deduplication. See Leave ADR-0046 | Changes to joining-grant timing |
| 2026-09-14 | Configure monthly grants at month start or end, with agreed partial-month proration | Replace independent monthly grant dates with explicit timing choices. See Leave ADR-0045 | Changes to monthly timing |
| 2026-09-14 | Resolve leap-day employment anniversaries to February 28 in non-leap years | Keep period and annual-grant dates deterministic without changing the original anniversary. See Leave ADR-0044 | Changes to anniversary rules |
| 2026-09-14 | Align annual upfront grants with entitlement-period start and grant mid-year joiners at employment start | Simplify annual timing while applying agreed proration. See Leave ADR-0043, superseding the independent annual date in ADR-0024 | Changes to annual grant timing |
| 2026-09-14 | Support calendar-year and employment-anniversary periods per policy | Separate entitlement period boundaries from grant frequency. See Leave ADR-0042 | Changes to period requirements |
| 2026-09-14 | Configure a standard day for conversions separately from date-specific working time | Support variable-length working days without mischarging actual leave. See Leave ADR-0041 | Changes to schedule/conversion semantics |
| 2026-09-14 | Convert day-based carry-over limits using the effective employee standard day | Respect differing schedules without rewriting historical carry-over. See Leave ADR-0040 | Changes to day-limit conversion |
| 2026-09-14 | Assign cancellation-deficit review to authorized Leave Managers | Require scoped balance-adjustment permission, reasons, employee explanations, and explicit paid grants. See Leave ADR-0039 | Changes to deficit-review responsibility |
| 2026-09-14 | Recalculate accrual enabled by cancelled approved leave | Close the booking/cancellation cap loophole while preserving actual transactions and auditable history. See Leave ADR-0038 | Changes to cancellation reconciliation |
| 2026-09-14 | Count already-earned reservations toward the accumulated cap | Prevent pending requests from creating headroom while keeping future accrual separate. See Leave ADR-0037 | Changes to reservation/cap interaction |
| 2026-09-14 | Default advance booking to 12 months with per-policy configuration | Require all requested dates within the window without shortening valid carry-over. See Leave ADR-0036 | Changes to booking defaults |
| 2026-09-14 | Tie reservation funding to leave dates and enforce policy booking horizons | Prevent early booking from preserving expired entitlement or bypassing carry-over limits. See Leave ADR-0035 | Changes to future funding or booking limits |
| 2026-09-14 | Resume scheduled accrual without automatic catch-up after a cap | Preserve normal grant dates and exclude automatic restoration of previously capped amounts. See Leave ADR-0034 | Changes to post-cap accrual behavior |
| 2026-09-14 | Allow optional accumulated balance caps on scheduled accrual | Grant only what fits, explain excluded amounts, and retain existing entitlement. See Leave ADR-0033 | Changes to cap behavior |
| 2026-09-14 | Protect reservations and explain authorized funding changes before renewed acknowledgement | Prevent new requests from displacing existing allocations and make increased unpaid amounts understandable. See Leave ADR-0032 | Changes to reservation priority or acknowledgement requirements |
| 2026-09-14 | Keep rollover shortfalls pending and show the exact requested unpaid amount | Respect entitlement validity while making the proposed unpaid consequence clear to employees and approvers. See Leave ADR-0031 | Changes to reservation or shortfall handling |
| 2026-09-14 | Expire unused entitlement excluded from carry-over at the period boundary | Preserve an auditable explanation without automatic payout or cross-type transfer. See Leave ADR-0030 | Changes to disposition of excluded entitlement |
| 2026-09-14 | Configure once-only or repeated carry-over without extending expiry | Allow policy-specific further transfer while preserving limits and original validity. See Leave ADR-0029 | Changes to repeated carry-over requirements |
| 2026-09-14 | Configure no, all-unused, or capped carry-over with optional expiry per policy | Support different leave-type rollover rules. See Leave ADR-0028 | Changes to carry-over requirements |
| 2026-09-14 | Fall back to the month's last valid day for missing accrual dates | Handle short months and non-leap years without shifting future grants. See Leave ADR-0027 | Changes to calendar scheduling rules |
| 2026-09-14 | Historical decision: selectable grant rounding, superseded by ADR-0103 | Make fractional-minute entitlement deterministic while preserving request-duration rules. See Leave ADR-0026 | Changes to grant rounding requirements |
| 2026-09-14 | Configure no proration or inclusive calendar-day proration per policy | Support different leave-type policies while retaining explicit manual grants. See Leave ADR-0025 | Changes to partial-period rules |
| 2026-09-14 | Support annual upfront, monthly, and manual-only grant schedules per policy | Cover confirmed NGO needs while retaining authorization, audit, and retry protections. See Leave ADR-0024 | Additional schedule requirements |
| 2026-09-14 | Use employee work timezone for leave dates and accrual/expiry boundaries | Keep dates and entitlement outcomes consistent when viewed or approved from another timezone. See Leave ADR-0023 | Changes to employee timezone or business-date rules |
| 2026-09-14 | Make accrual usable from the start of its configured effective date | Permit same-date leave without funding earlier leave; preserve policy-controlled schedules. See Leave ADR-0022 | Changes to accrual availability timing |
| 2026-09-14 | Treat entitlement expiry as the last usable leave date | Base validity on when leave is taken; earlier submission does not preserve entitlement for later dates. See Leave ADR-0021 | Changes to expiry semantics |
| 2026-09-14 | Allocate eligible entitlement by earliest expiry within the selected balance | Use soonest-expiring portions before later or non-expiring portions while preserving cross-type override controls. See Leave ADR-0020 | Changes to allocation priority |
| 2026-09-14 | Assess future-request funding on each requested leave date | Prevent later accrual, expired entitlement, or competing reservations from masking a shortfall. See Leave ADR-0019 | Changes to projection or entitlement-allocation rules |
| 2026-09-14 | Share decision history and approval/rejection comments with request owners and assigned approvers | Make outcomes and attribution visible within authorized scope; exclude private approver-only comments from MVP. See Leave ADR-0018 | Changes to approval-history visibility or private-comment requirements |
| 2026-09-14 | Apply the approver medical-document metadata rule to Leave Managers | Permit in-scope provision/verification status while keeping filenames, previews, and downloads separately authorized. See Leave ADR-0017 | Changes to Leave Manager attachment metadata visibility |
| 2026-09-14 | Limit approvers without medical-document permission to provision and verification status | Prevent filenames and previews from disclosing sensitive information; retain employees' own permitted access. See Leave ADR-0016 | Changes to attachment metadata visibility |
| 2026-09-14 | Apply the email content limit to in-app notifications | Keep notifications minimal and show role-permitted details after current request authorization. See Leave ADR-0015 | Changes to notification content or access behavior |
| 2026-09-14 | Limit email request content to name, dates, status, and a secure application link | Keep leave types, notes, comments, and document details behind application authorization. See Leave ADR-0014 | Changes to notification content or channels |
| 2026-09-14 | Permit Leave Managers to see in-scope leave types, employee notes, and approval history | Support Leave administration while keeping medical documents separately authorized. See Leave ADR-0013 | Changes to Leave Manager visibility or document permissions |
| 2026-09-14 | Permit assigned approvers to see sensitive leave types and employee notes through their normal approval role | Support scoped approval decisions while keeping medical documents separately authorized. See Leave ADR-0012 | Changes to approver visibility or document permissions |
| 2026-09-14 | Show ordinary colleagues Unavailable for all leave types | Preserve availability visibility without disclosing type or supporting details, including through filters and exports. See Leave ADR-0011 | Changes to shared-view privacy requirements |
| 2026-09-14 | Correct approved dates/duration by cancellation and a linked new request with renewed approval | Employee and scoped on-behalf actors may perform the correction; preserve history and separate approval authority. See Leave ADR-0010 | Changes to approved-request correction or on-behalf scope |
| 2026-09-14 | Edit and resubmit the same rejected request, preserving history | Keep request identity and earlier decisions while validating corrected content in a fresh approval cycle. See Leave ADR-0009 | Changes to rejection/correction lifecycle |
| 2026-09-14 | Record an authorized submitting second approver's acceptance immediately and wait for the first | No repeat approval is needed; leave remains reserved until all required steps are satisfied. See Leave ADR-0008 | Changes to approval ordering or automatic-decision rules |
| 2026-09-14 | Require at least one approval step; configure the count per NGO/policy and record authorized automatic decisions on submission | Permitted self-approval and separately authorized on-behalf submission satisfy the submitter's own approval only; consume leave only after all required approvals. See Leave ADR-0007, superseding ADR-0004 | New need for employee recording without approval, or more workflow presets |
| 2026-09-01 | Keep Supabase Auth for MVP | Existing identity FK, JWT hooks, RLS, and frontend integration make migration premature | Tenant-managed IdPs, complex federation, or identity independence becomes a committed requirement |
| 2026-09-01 | Implement Content Service in FastAPI | Matches the platform API direction and centralizes reusable authorization, auditing, provider adapters, and operational controls | None; provider implementations remain replaceable |
| 2026-09-01 | Preserve direct-to-storage uploads | Avoids proxying large files through the API while retaining a secure control plane | A provider or compliance rule requires server-side transfer |
| 2026-09-01 | Use a ledger for leave balances | Provides reproducible balances and complete adjustment history | None |
| 2026-09-01 | Version leave policies/types | Historical applications must retain the rules under which they were submitted | None |
| 2026-09-01 | Evolve scaffolding continuously | Reusable conventions must reach future apps while their implementation context and tests are current | A pattern proves application-specific and is explicitly excluded |
| 2026-09-01 | Adopt SPDD selectively and evolve prompts continuously | Superseded on 2026-09-04 by BMAD adoption; retained as decision history | See platform ADR-0010 |
| 2026-09-03 | Make ATDD/TDD the core development loop | Executable acceptance and focused tests reduce refactoring risk and escaped defects while providing concise agent feedback | Metrics show boundaries or workflow require adjustment |
| 2026-09-04 | Adopt BMAD as the generic delivery workflow | Avoid maintaining a home-grown methodology while preserving project-owned ADR, ATDD/TDD, scaffold, and context gates | Two-epic pilot shows unacceptable overhead or drift |

## Progress summary

Update this section at each planning or delivery review.

| Milestone | Status | Completed | Notes |
|---|---|---:|---|
| Phase 0 — Planning | Complete | 12/12 | Product decisions and architecture baseline approved and recorded |
| Phase 1 — Scaffold, BMAD, and test foundation | In progress | 4/21 | Agent context, requirements validation, UX handoff and architecture consolidation complete; stories/readiness and technical foundation remain; no Leave implementation started |
| Continuous BMAD, scaffold, and context evolution | Not started | Recurring | Required for every Phase 2–10 exit gate |
| Phase 2 — Identity and authorization | Not started | 0/14 | Full-flow; Build per story plus additional Code Review |
| Phase 3 — Design system | Not started | 0/7 | Expanded incrementally as Leave features prove reusable components |
| Phase 4 — Content Service | Not started | 0/11 | Replaces a non-production prototype; no receipt migration required |
| Phase 5 — Leave configuration | Not started | 0/8 | Jurisdiction-ready, not a legal rules engine |
| Phase 6 — Accrual and ledger | Not started | 0/9 | Requires deterministic time tests |
| Phase 7 — Requests and approvals | Not started | 0/12 | Includes secure attachments |
| Phase 8 — Notifications | Not started | 0/7 | Outbox-backed asynchronous delivery |
| Phase 9 — Views and reports | Not started | 0/8 | Privacy-aware details |
| Phase 10 — Release | Not started | 0/10 | Pilot before broad enablement |

Fingerprint security follow-up, 2026-10-01: [keyed fingerprints are logged as a
platform enhancement candidate](../../../platform/docs/architecture/contracts/operation-fingerprint-security-evolution.md).
The E1 baseline uses SHA-256 without fingerprint keys or rotation. Sensitive applications
may require HMAC from initial delivery; Leave’s health-related inputs and retained
outcomes must be considered in the existing pilot security assessment. Deferral does
not waive a finding that stronger protection is required.


Draft navigation clarification, 2026-10-04: E1-D2/D3 adopt
[platform ADR-0048](../../../platform/docs/architecture/decisions/0048-simple-draft-save-failure-navigation.md)
through Leave ADR-0121. Simple warning and Close anyway / Switch anyway replace
technical uncertainty explanations and prior failure-exit labels. Promote the proven
shared UI/scaffold pattern with the first consumer; submission safeguards remain.
Readiness, recovery-reference details and required acceptance evidence remain open.


E1 sequencing checkpoint, 2026-10-04: 18 agreed candidate boundaries now have a
[consolidated dependency order](../../../_bmad-output/planning-artifacts/epics.md#consolidated-e1-delivery-sequence--discussion-checkpoint-2026-10-04).
This includes shared platform prerequisites and the six Leave entry/draft journeys.
It is a discussion checkpoint; granular coverage, contract reconciliation, final story
sizing/numbering and implementation readiness remain incomplete. Existing phase gates
and E4/E5 pre-story contracts are not waived.


### E1 technical contract closure — 2026-10-04

The revised 20-candidate delivery order is approved (ID and D2 splits, 2026-10-05). The acceptance map covers the extracted
12 entry and 20 draft requirements and 18 scenario groups with named story owners.
This is scoped traceability, not completed global FR/NFR/UX extraction, executable
validation or permission to bypass the existing spine/Phase 1 readiness gates.
Product behavior already agreed is not reopened by the technical work below.

| Contract to close | Owner / dependent stories | Required concrete planning output |
| --- | --- | --- |
| Reproducible generation/environment | Platform; ENV/P1/SERVICE then all consumers | Supported generation inputs, package/lock ownership and verified compatibility pins; safe target identity/reset checks; owner bootstrap/validation commands; feasible separate Entra callback target and browser/device evidence plan. No production setup or installs authorized here. |
| Identity/migration/admission baseline | Identity/Access; ID/ACCESS/DISCOVERY/LAUNCHER | Actual object/history/role ownership inventory; bounded manual PtS account transition/recovery; exact capability/service registry and app-admission schema; complete v1/v2 wire compatibility and discovery failure/limit cases. |
| Minimal shared employment | People; PEOPLE then CONTEXT/D1 | Concrete relationship/period keys, nonoverlap/attribution constraints and owner provisioning; discovery/effective response schema and absence/setup/outage fixtures. |
| Minimum Leave settings and choices | Leave; CONTEXT/CHOICES then D1/D2 | Work-profile/default/override-compatible timezone source and revision; minimal versioned type metadata endpoint/schema, active-date selection, authorized retired-choice handling and controlled seed mapping. Do not invent a parallel employee/configuration master or imply submission eligibility. |
| Owned writes and draft wire/schema consistency | Platform/Leave; WRITE/REF/D1/D2/D4 | Exact reference-command canonical input/outcome retention; reconcile declared draft constraints, SQL scope/grants and all request/response/error variants. Preserve atomic effects, revision/lifecycle guards, compact closed rows and no default form backfill. |
| Supported authentication return | Platform shell + Leave; A1/D2/D3/D5/WRITE | Validated destination/account binding through supported auth flow, current access and saved-draft reload; safe fallback when context is missing. No bespoke sessionStorage record/TTL. Verify delayed-save ordering and no automatic lost-write replay. ADR-0050 inline failure and exit-only confirmation remain settled. |
| Coverage, sizing and gate evidence | Planning owners; all 23 candidates | Finish scoped source-to-story cross-check and global inventory; validate independently completable story size/order; assign concrete acceptance/contract test IDs and exact commands as delivery is prepared. Run the established readiness workflow only when its required planning inputs are complete. |

Technical contract outputs precede dependent readiness; implementation subsequently
observes failing acceptance and produces passing runtime evidence. This does not require
pre-implementing Leave to write its stories. Browser/performance policies and 500/1,000
employee targets are agreed; results remain unmeasured. Pilot fingerprint-risk assessment
and operational retention still belong to their existing security/release gates.
E2's employment mutation/history contract, E4's finalized byte identity (platform
ADR-0038), and E5's consequential-action consistency gates remain explicitly open for
their consumers. No later gate is satisfied by this E1 mapping.


Identity inventory progress, 2026-10-04: the
[repository ownership inventory](../../../platform/docs/architecture/contracts/identity-migration-ownership-inventory.md)
now identifies source objects, successor owners, Expense dependencies, both current
migration paths and a proposed separate identity history under Access maintainers.
Composition check-only passed; no SQL or live target inspection occurred. Actual
baseline comparison, restricted grants, Auth hook compatibility and single-authority
clean/adopt rehearsal remain prerequisites for E1-ID/ACCESS readiness. Receipt profiles
are account profiles, not a shared employee master; no historical receipt conversion
or PtS/Scribeswell document ownership migration is introduced.


Access schema progress, 2026-10-04: the
[owning admission contract](../../../platform/docs/architecture/contracts/application-admission-and-discovery.md#concrete-e1-access-persistence-design--2026-10-04)
now proposes application/permission registries, organization enablement and compatible
extension of existing grants, plus explicit service-policy configuration. Discovery
privileges, membership retirement/rejoin binding, audit details and mixed-version
activation remain concrete readiness gaps. No schema or account changed; existing
v1 callers must not bypass new disable controls after activation.


Membership lifecycle design, 2026-10-04: the
[owning Identity contract](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#membership-retirement-and-rejoining--concrete-e1-design-2026-10-04)
selects retained retired membership rows, new IDs on explicit rejoin and one-active-row
uniqueness. Existing grant/member-role bindings cannot silently resume; deliberate
regrant uses the new ID. App suspension and shared employment remain independent.
E1-ID/ACCESS now have a concrete lifecycle choice; exact constraints, legacy lookup/
writer changes, audit schema and migration/activation rehearsal remain before readiness.


Restricted discovery progress, 2026-10-04: the
[Access discovery contract](../../../platform/docs/architecture/contracts/application-admission-and-discovery.md#restricted-discovery-database-contract--2026-10-04)
now defines the minimal membership projection, fully filtered pagination, exact verified
account context and routine privilege boundary. E1-DISCOVERY/ACCESS still require actual
RLS/grant/pool-reuse fixtures and compatible owner migrations. The trusted-backend limit
is explicit; no claim that a database setting authenticates an end user independently.


People schema progress, 2026-10-04: the
[minimum persistence contract](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#minimum-people-persistence-contract--2026-10-04)
now defines employment, scoped periods and immutable owner-change evidence, with one
person/organization relationship, accountless support and database-enforced inclusive
nonoverlap. Department/location/supervisor remain optional shared facts added with E2's
consuming administration/history contracts; none becomes a Leave-owned duplicate.
Exact provisioning/history payloads, date bounds, caller policy and restricted-role/
extension verification remain before E1-PEOPLE readiness. No schema was implemented.


Work-timezone design progress, 2026-10-04: the
[minimum Leave configuration contract](./architecture/contracts/e1-work-timezone-configuration.md)
records profile/default/override precedence, owned minimum records, setup semantics
and E1 versus E2 responsibilities. Effective-version selection must avoid depending on
an as-yet-unresolved timezone; exact applicability and local configuration/date guarding
(including absent rows) remain pre-readiness design work. No new product choice, profile
administration screen or settings change was introduced.


Scope simplification, 2026-10-04: [Leave ADR-0122](./architecture/decisions/0122-lightweight-draft-compatibility-and-setup.md)
removes missing/invalid timezone as a draft-save blocker and permits clearing definitively
obsolete selections with notice and guarded autosave. Full effective timezone/version
and configuration commit guards are not prerequisites merely for E1 preservation; retain
them before dependent calculations/eligibility/consequential actions. E1-CONTEXT/CHOICES/
D1/D2 need corresponding schema/criteria reconciliation; identity/access/ownership,
revision/lifecycle, confirmed restrictions and runtime verification gates remain.

Platform adoption, 2026-10-04: [ADR-0049](../../../platform/docs/architecture/decisions/0049-lightweight-draft-preservation-and-compatibility.md) now owns lightweight non-consequential draft preservation and application-defined obsolete-field handling. Leave ADR-0122 supplies its domain application. Scaffold/shared UX/agent guidance reference the platform rule; pending E1 criteria/schema reconciliation remains required.


Draft reconciliation progress, 2026-10-04: active E1-CONTEXT/D1/CHOICES criteria and draft
read/error contracts now distinguish nonblocking setup_notices from editability. Timezone-
only mutation rejection is removed. Remaining consumer integration is explicit: undated
People discovery must distinguish missing periods without guessing, operation evidence
must allow genuinely undated observations, and obsolete choice reset requires definitive
lookup rather than omission from a paginated list. Full calculation/profile-version
machinery remains outside the simple preservation path. No runtime checks were executed.


Consumer contract closure, 2026-10-05: People discovery now declares `has_periods`,
with no invented effective date/status. Draft observation evidence has explicit discovery
and effective variants. The [choice-resolution contract](./architecture/contracts/e1-draft-choice-resolution.md)
checks a selected type independently of list pagination and defines minimal field-reset,
read-only and stale-response behavior. These close the two identified interface choices;
minimal published type/version schema and executable validation remain before readiness.
No application code, stored input or database changed.


Choice-schema progress, 2026-10-05: the
[owned choice contract](./architecture/contracts/e1-draft-choice-resolution.md#minimum-owned-typeversion-schema--2026-10-05)
now defines stable leave types, published metadata versions, scoped choice-version
references, metadata bounds and keyset cursor contents. E1 provisions one published
example version per type; the selector is not a submission policy/eligibility decision.
E3 retains effective-date policy selection/snapshots and scheduled-publication gates.
Actual migrations, owner-command/audit schemas and executable verification remain open.


### Remaining E1 gates by timing — 2026-10-05

**Status: agreed scope and sequence; contracts partly specified; not implementation-ready.**
This classifies existing spine/Phase 1 gates, not a new workflow. The revised 20-candidate order
and first delivery slice remain unchanged. Product approvals are not waiting for another
round of confirmation merely because technical fields or verification commands need work.

**Already settled in planning:** organization-neutral tenancy; identity/person/employment
separation; accountless employment; access ownership and app-admission rules; new membership
ID on rejoin; shared optional department/location/supervisor; draft input/retry/lifecycle
behavior; platform-simple failure exits; lightweight preservation despite missing timezone;
obsolete-field clearing; undated People has_periods; definitive choice lookup; minimum
People/type structures; local-first tests, browser policy and initial performance targets.
These still need consistent contracts and execution evidence, not rediscovery of user intent.

#### Before the first affected story is ready

| Remaining design/validation | Owning candidates | Concrete completion evidence |
| --- | --- | --- |
| Canonical schema and migration consistency | ID/ACCESS/DISCOVERY/PEOPLE/WRITE/CHOICES/D1 | One coherent set of actor/reference keys, grants, RLS/routine ownership, membership partial uniqueness and legacy writer adoption; complete required read/result/error variants; executable-design fixtures mapped to each invariant. Validate proposed source placement and clean/adopt order against real repository consumers. Target baseline equivalence is required before adopting that target, not assumed from source SQL. |
| Minimal owner provisioning and consequential evidence | ID/ACCESS/PEOPLE/WRITE/REF/CHOICES | Exact controlled command inputs, required actor/reason, operation identity/canonical input/result, bounded safe errors, audit/change row shapes and atomic effects. Reference capability IDs and fixture manifest ownership explicit. No public administration UI or full HR mutation framework in E1. Ordinary draft saves/reads remain free of duplicate business audits. |
| Authentication return and draft restart behavior | A1/D2/D3/D5/WRITE | Supported auth-adapter validated return and account binding; current access and saved-draft reload; safe fallback without context; no custom recovery record/TTL. Validate delayed-save ordering against reopened-editor revision/lifecycle checks; no automatic replay of lost writes. Existing execution/recovery budgets and consequential-action safeguards remain binding. |
| Reproducible tools and configuration | ENV/P1/SERVICE and each dependent consumer | Exact verified compatibility set, lockfile/manifest ownership, generator input/extension rules, safe fixture/reset targets and named local/CI commands. Define actual Entra callback test target and required service credentials. Choose declared catalogue/metadata limits and relevant timeouts where still open. No copying unverified installed versions as proof. |
| Coherent planning and BMAD checks | All E1 owners / technical lead | Finish full source-to-story FR/NFR/UX extraction, reconcile stale active wording and story dependencies/sizing, finalize numbering and explicit acceptance IDs. Complete required BMAD workflow customization and platform-prompt transition work, then use the existing CE/SP sequence and readiness gate. The scoped 12-entry/20-draft/18-scenario map is not a full-product completeness certificate. |

Do not require working Leave code before writing its stories. Conversely, a detailed
Markdown schema is not automatically a validated API/migration contract. Design review
and bounded compatibility investigation close the relevant pre-story questions; BMAD
Build then supplies failing-first implementation and evidence. No installation, live
inspection, test-user provisioning or migration is authorized merely by this table.

#### Evidence produced during the owning implementation

- Observe the affected acceptance failure, implement through ATDD/focused TDD and record
  exact commands and results. Generate actual OpenAPI/client output and run contract fixtures.
- Prove database constraints, least-privilege roles/RLS, connection reuse, atomic writes,
  concurrency and real committed-outcome recovery; mocked success is insufficient.
- Prove clean setup and supported baseline adoption with synthetic rehearsals, migration
  failure preventing activation and explicit recovery. Live cutover remains a separate
  coordinated release action with target verification and permissions.
- Generate fresh app/service output, preserve custom extensions, and exercise the authenticated
  reference locally and in CI. That remains the binding Phase 1 exit gate before Leave
  business consumers; a template-text check or startup health result cannot substitute.
- Execute the Leave sign-in → organization → create/resume → autosave → close → reopen
  journey and its agreed isolation/recovery branches. Add actual Entra, browser/device,
  accessibility and representative-load evidence at their owning qualification points.
- Promote proven shared clients/UI/templates and update docs/changelog/agent links in the
  same item. Existing-app compatibility is tested where a shared contract changes.

#### Explicitly later, before the first dependent consumer

| Later boundary | Work retained there |
| --- | --- |
| E2 shared administration | Invitations/roles and administrative UI; employee mutations and change impacts; department/location/supervisor catalogues and effective history; work-profile/default/override editing and schedule/holiday setup. |
| E2/E3 timezone-dependent behavior | Full effective-version applicability, timezone change boundaries and configuration consistency where calculations or dated decisions actually depend on them. E1 still needs a safe interpretation if it uses a dated restriction, but missing timezone alone cannot block preservation. |
| E3 policy/calculation | Effective-date policy selection, scheduled publication, entitlement/balance rules and explanatory previews. The E1 choice-version pointer is not calculation authority. |
| E4 attachments | Association/cleanup handshake, provider-enforced capability lifetime and platform ADR-0038 finalized byte identity. No E1 upload dependency. |
| E5 consequential workflow | Submission/approval/reservation guards, routing/coverage/acknowledgements, required workers/events and stronger shared-input consistency. No relaxation from the draft-preservation rule. |
| E6–E8 and pilot gates | Correction/report/import consumers, operational/privacy/security assessments, real backup/recovery, release qualification and human acceptance as already assigned. Fingerprint confidentiality-risk disposition remains before pilot. |

#### Result and next technical work

No additional user-facing requirement or new story is proposed by this consolidation.
No implementation gate is passed. The next bounded technical pass is to complete the
minimal owner-command/evidence shapes (especially Identity/Access/People provisioning)
and verify their consistency with the already agreed schemas; then finalize supported authentication return
integration and toolchain contracts. Surface only a genuine product tradeoff for discussion.
Global requirements extraction, story-size validation and the Phase 1 BMAD/prompt tasks
must remain visible while those technical items close; do not call E1 or CE complete early.


Provisioning design progress, 2026-10-05: the [controlled owner-command contract](../../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md) specifies minimal Identity/Access/People setup payloads, expected-state guards, stable retries, compact outcomes and atomic transition evidence. No shared runtime provisioning engine or E1 administration screen is introduced. Operator authority adapter, exact typed schemas/bounds, migration grants and synthetic rehearsals remain readiness inputs.


Sign-in recovery simplification — approved 2026-10-05: the
[saved-draft return contract](./architecture/contracts/e1-draft-persistence-and-recovery.md#saved-draft-sign-in-return--agreed-2026-10-05)
replaces the proposed bespoke recovery record, 4 KiB schema and 30-minute TTL with
supported auth return navigation and fresh authorized saved-draft loading. Unsaved typing
is not guaranteed through interactive sign-in. Generic callback/account safety and backend
delayed-save ordering still need evidence; no automatic replay or consequential confirmation.
Existing platform ADR-0032 applies unchanged. This closes the storage-design choice, not
the runtime validation/readiness gate.


Dependency/command ownership — 2026-10-05: the [E1 environment contract](./testing/e1-environment-and-dependencies.md#dependency-ownership-and-command-contract--2026-10-05) now specifies Leave's standalone npm lock, per-owner Python/uv locks, Access's same-item removal of its PtS dependency coupling, and the planned explicit local/CI command surface. Existing package/workspace files are unchanged. Exact compatibility pins, guarded bootstrap commands, provider callback target and runnable generated-reference evidence remain open; no readiness pass or installation is claimed.


E1 scoped cross-check — 2026-10-05: [findings and proposed sizing](./testing/e1-acceptance-map.md#e1-source-and-sizing-cross-check--2026-10-05) retain the agreed first slice and all existing 12 entry/20 draft/18 acceptance-group mappings. Two splits are proposed, not yet approved: ID baseline then identity behavior; D2 guarded save API then browser autosave/close/reopen. Corrected D2's assumption that prior create/read reference work already proved mutable writes. ENV uses disposable base fixtures without future Identity/Access dependencies. Language, human accessibility/performance evidence and Phase 1 BMAD customization/prompt gates remain explicit. Full-product extraction, final sizing and readiness are still pending.


Sizing approval — 2026-10-05: user approved ID-A/ID-B and D2-A/D2-B. The
[revised sequence](../../../_bmad-output/planning-artifacts/epics.md#approved-revised-e1-delivery-sequence--2026-10-05)
now has 20 candidates; parent IDs remain traceability groupings. The acceptance matrix
is updated with each child's evidence responsibility. ID-A acceptance criteria are
presented for discussion next; child-detail approval, remaining sizing/contracts and
CE/SP readiness are not implied by approval of the splits. First delivery slice unchanged.


ID-A acceptance approved — 2026-10-05. ID-B now has [detailed acceptance criteria](../../../_bmad-output/planning-artifacts/epics.md#candidate-story-e1-id-b-link-accounts-to-people-and-preserve-membership-history) for discussion. It owns verified person/account/actor mapping, membership transitions and controlled synthetic transition evidence. ACCESS retains grant-binding/admission integration; its proof is required before coordinated live activation of changed membership semantics. Independent ID-B completion does not imply production cutover or authorize an incompatible intermediate release. No application code or identity data changed.


ID-B acceptance approved — 2026-10-05, including explicit clarification that membership
replacement preserves the person/employment relationship and Leave history, subject to
current access, and delayed removal targets only the old membership. The three-user
transition is the existing PtS cohort, tested synthetically. No automatic access restoration
or employment termination. D2-A is the next split-story detail; prior ACCESS and other
unchanged scope approvals stand. Implementation/readiness gates remain open.


D2-A detail — 2026-10-05: [save/read acceptance draft](../../../_bmad-output/planning-artifacts/epics.md#candidate-story-e1-d2-a-save-and-read-my-draft-input-safely) specifies exact input preservation, current authority, atomic revision/lifecycle/outcome writes, duplicate-safe recovery, both delayed-save commit orders and coherent authorized reads. It passes through API/database tests independently of D2-B's browser. Missing timezone remains nonblocking; no extra calculation engine, duplicate draft audit, custom sign-in record or discard/submission implementation. Acceptance detail awaits discussion; readiness and runtime evidence remain open.


D2-A acceptance approved — 2026-10-05. [D2-B browser acceptance detail](../../../_bmad-output/planning-artifacts/epics.md#candidate-story-e1-d2-b-edit-autosave-close-and-reopen-my-draft) is now for discussion: exact-input form integration, serialized/coalesced autosave, truthful status, simple safe exits, conflict handling and real persisted reopen. This completes the first usable slice with applicable browser/accessibility/performance evidence; dedicated D3/D4/D5 branches remain next. Existing scope and readiness gates remain binding; no application code or tests run.


Draft failure presentation update — accepted 2026-10-05: platform ADR-0050 partially
supersedes ADR-0048; Leave ADR-0123 adopts it. Use inline Changes not saved with Retry
while editing; no Keep editing button. Prompt Stay / Close anyway only on exit when
bounded saving cannot be confirmed; switching uses Stay / Switch anyway. Confirmed saved
input closes immediately. Existing revision/lifecycle/retry and access protections stay
binding; no rollback or unsent-input survival promise. D2-B/D3 and shared scaffold/UI
fixtures must prove these cases. Earlier three-choice wording is superseded. This does
not decide whether a workflow needs a draft or change accepted draft scope.


Saving convention — 2026-10-05: User accepted platform ADR-0051/Leave ADR-0124 saving conventions. D2-B reflects Draft saved, no redundant Save button and ADR-0050 inline/exit failure behavior. Business administration uses explicit whole-form saving; personal preferences apply immediately separately. Continue E1 source/contract/sizing closure; E2/E3 inherit the convention. No readiness gate passed.


### Current E1 closure checkpoint — 2026-10-05

Active D2/D3 criteria, feature text, draft contract and acceptance groups now use
ADR-0050/0051 and Leave ADR-0123/0124. D3 switches only after saved source input or an
explicit Switch anyway; D4 remains deliberate whole-draft discard; D5 restores current
authorized saved state using ordinary auth return. D3/D4/D5 dependencies name both D2
children. Earlier dated discussion notes are historical; accepted ADRs are unchanged.
No new product approval is required for this reconciliation.

| Remaining work | Concrete next result | Timing / owner |
| --- | --- | --- |
| Requirements completeness | Extract unmapped source FR/NFR/UX requirements, including general UX and operational safeguards, and link them to E1 or the appropriate later epic. Existing 12/20/18 ownership counts are not a completeness claim. | Continue CE; planning owner |
| Remaining story sizing and dependency proof | P1/SERVICE/PEOPLE scopes retained; ACCESS-A/B split approved. Finish child acceptance and concrete contract validation before final numbering; avoid hidden future-story dependencies. | Before finalizing affected stories |
| Identity/Access/People contract consistency | Resolve declared schema/actor/grant ownership, privileged operator adapter, typed command/result limits and supported legacy-writer transition against repository evidence. | Before affected story readiness; owning maintainers |
| Draft/reference contracts | Validate draft/error/schema constraints and delayed-save commit-order fixtures; finish the sample write's own canonical input/retention contract and supported auth-return integration design. | Before affected writer/reference readiness |
| Reproducible baseline | Select/verify exact compatible versions, guarded bootstrap/reset commands and feasible nonproduction Entra callback target. Planned scripts are not working commands. | ENV/P1/SERVICE/A1 readiness inputs |
| BMAD repository integration | Complete existing BMAD customization and platform-prompts transition tasks, then complete CE and use SP at its established gate. | Existing Phase 1, not a competing checklist/workflow |

Runtime tests, generated authenticated reference, migration rehearsals and measured
browser/accessibility/performance evidence are produced during authorized delivery at
their owning gates. Do not require working Leave to finish stories or count planning
text as passing evidence. E4 retains finalized byte identity under platform ADR-0038;
E5 retains consequential consistency. E1 behavior remains the approved first draft slice.


Source coverage progress — 2026-10-05: extracted [22 supplemental permission/UX/NFR
obligations](../../../_bmad-output/planning-artifacts/epics.md#supplemental-source-coverage-permissions-ux-and-operations--2026-10-05)
with explicit E1 owners/evidence and later consumers. Encryption, backend tracing and
visual/localization requirements now have explicit first-consumer or release evidence
assignments. No new draft behavior, epic or product approval. E4 keeps ADR-0038 provider
proof; E8 integrated restoration/alerts remains required. Detailed business catalogue
extraction, remaining story sizing/contracts and CE/SP readiness remain open.


Business/journey coverage — 2026-10-05: [BIZ-01–36](../../../_bmad-output/planning-artifacts/epics.md#business-feature-and-ux-journey-coverage--2026-10-05)
assign concrete source outcomes and all numbered UX key flows to E1–E8. The first
notification producer is E3; shared delivery must precede it. E5 must integrate actual
pending-request impact guards with earlier E2/E3 writers before activation, not defer
those checks to E6. E5 owns rejected resubmission; E6 approved cancellation/replacement.
E4 retains ADR-0038 provider proof; E8 assembles operational release evidence. These are
existing requirements, not additional product scope. §6 arithmetic/example extraction
and detailed source-state coverage remain open; no story/readiness gate passed.


Entitlement extraction — 2026-10-05: [CALC-01–36](../../../_bmad-output/planning-artifacts/epics.md#entitlement-rule-and-acceptance-example-ledger--2026-10-05)
links earning/precision/calendar boundaries/caps/carry-over/funding/confirmation/correction
rules to required examples and E3/E5/E6 owners. ADR-0105 precedence over partial-month
wording in 0097 is explicit. On-demand earning remains authoritative under 0106; physical
rollover/expiry evidence, allocation ties and historical bucket/fraction representation
remain open technical contracts. No configurable rounding, daily accrual worker or new
product defaults. Remaining workflow-state coverage, sizing and CE/SP readiness stay open.


Workflow extraction — 2026-10-05: [FLOW-01–28 and finalization scenarios](../../../_bmad-output/planning-artifacts/epics.md#approval-and-request-state-coverage--2026-10-05)
map route resolution, automatic decisions, exact unpaid responses, coverage/exception,
temporary authority/return, directional fallback, reminders, resubmission and correction.
Step approved does not imply request approved. Missing route blocks submission; applicant
coverage can remain pending until final approval. Effective temporary Access contracts,
interval/transfer concurrency, due-work timing and all finalization trigger contracts
remain before dependent readiness. No new business defaults or runtime evidence.


Privacy/state extraction — 2026-10-05: [PRIV-01–22](../../../_bmad-output/planning-artifacts/epics.md#privacy-notification-and-screen-state-coverage--2026-10-05)
assign API/render/export disclosure, notification recipient/read/count boundaries,
independent section recovery, stale review and overview/report states to their first
owners. Read notifications never complete required employee actions; supporting-panel
failure does not replace required business checks or imply a successful empty result.
E3 remains the first notification consumer; E4 retains ADR-0038 protocol/race proof.
No new product decision or implementation. Continue P1/ACCESS/PEOPLE sizing/dependency
closure and explicit technical contracts; CE/SP and implementation readiness remain open.


Foundation sizing proposal — 2026-10-05: [P1/ACCESS/PEOPLE assessment](../../../_bmad-output/planning-artifacts/epics.md#remaining-e1-foundation-sizing--2026-10-05)
recommends retaining bounded P1, SERVICE and PEOPLE stories and splitting ACCESS into
controlled configuration/provisioning followed by current checks/compatible activation.
This is pending discussion: the approved twenty-item sequence and acceptance map have
not been renumbered. New admission controls cannot be activated before enforcement
works for supported v1/v2 callers. No new product scope or readiness approval.


Access split approved — 2026-10-05: [current E1 sequence](../../../_bmad-output/planning-artifacts/epics.md#access-split-agreement-and-current-e1-sequence--2026-10-05)
now contains 21 delivery items; the acceptance ownership matrix separates ACCESS-A
configuration/adoption evidence from ACCESS-B current-check/activation evidence.
P1/SERVICE/PEOPLE remain bounded as agreed. Detailed ACCESS-A criteria are prepared
for discussion; operator adapter, exact schemas/bounds and compatible-writer transition
remain required inputs. This supersedes the pending status of the preceding sizing
proposal, not readiness gates or the first Leave slice. No code or runtime test execution.


ACCESS-A criteria approved — 2026-10-06. [ACCESS-B detailed criteria](../../../_bmad-output/planning-artifacts/epics.md#candidate-story-e1-access-b-enforce-current-application-and-user-access)
now cover current admission, exact membership-bound grants, service/user separation,
safe typed outcomes and supported v1/v2 transition for discussion. V1 does not acquire
v2's employee person-link prerequisite; both enforce current admission. ACCESS-B tests
are independent of later discovery/launcher/People implementation, while coordinated
consumer activation remains required. The 21-item sequence is unchanged; technical
contracts and CE/SP readiness remain open. No application or live configuration changes.


PtS scope correction — accepted 2026-10-06: [platform ADR-0052](../../../platform/docs/architecture/decisions/0052-pts-account-scoped-access-and-coordinated-adoption.md)
requires individual account access with no organization. Earlier mandatory legacy PtS
response preservation and organization-admission assumptions are superseded. Reconcile
ACCESS-A/B, DISCOVERY/LAUNCHER, Identity transition and reference/scaffold scope variants;
retain Leave organization isolation. Account grant/check/operator contracts and PtS
corpus/Content consumer inventory/transition are explicit readiness gaps. Recheck sizing
after those are concrete; current 21-item sequence is not a new readiness approval.


Capability-scope refinement — accepted 2026-10-06: [ADR-0053](../../../platform/docs/architecture/decisions/0053-capability-scoped-access-in-mixed-scope-applications.md)
requires scope per capability, supporting current individual PtS and future organization
features without implementing those features now. ACCESS-A/B and discovery/scaffold
contracts must not classify an app as permanently single-scope. Update typed grant/check
and discovery contracts, then resolve PtS corpus/Content transition and prerequisite
sizing. Leave remains organization-scoped; the first draft slice and readiness gates stay.


Scope-wire refinement — 2026-10-06: owning [check contract](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#canonical-capability-check-wire--2026-10-06)
and [discovery contract](../../../platform/docs/architecture/contracts/application-admission-and-discovery.md#canonical-discovery-refinement--2026-10-06)
now define typed account/organization requests, minimal variant responses and unique app
rows with eligible scope kinds. Read entry capabilities are explicit; no cross-scope or
manage-to-read implication. PtS corpus/Content transition, account grant/actor persistence
and executable contract evidence remain readiness inputs. First Leave slice unchanged.


PtS resource inventory — 2026-10-06: [owner proposal](../../pts/docs/architecture/contracts/account-access-and-corpus-transition.md)
identifies organization coupling across browser, API, persistence, Content and import.
Discuss application-owned corpus plus individual capability access; preserve source assets
and finalized bytes. Account/corpus grants are not permission to access unrelated Content.
Plan separate bounded PtS adoption work after sizing; do not hide it in ACCESS-B or bypass
shared Content readiness. No change yet to the approved 21-item baseline or application code.


Content boundary accepted — 2026-10-06: [ADR-0054](../../../platform/docs/architecture/decisions/0054-application-authorized-content-and-enforced-ownership.md)
selects application-authorized control-plane calls and Content-enforced service ownership/
resource scope. PtS adoption and Leave E4 inherit it; no callback or duplicate domain
authorization engine. Signed transfers and ADR-0038/provider/association gates remain.
Concrete Content schema/legacy mapping/service identity/attribution and PtS adoption
sizing are next contract work; no application implementation authorized.


Private download decision — 2026-10-06: [ADR-0055](../../../platform/docs/architecture/decisions/0055-authenticated-private-downloads-by-default.md)
requires authenticated app/Content streaming by default; previous five-minute browser
read-link defaults no longer govern private delivery. Signed upload lifetimes, Content
ownership, association and byte identity remain. PtS first-consumer and Leave E4 need
streaming auth/range/cache/resource/deployment contracts and evidence. Future share
links await a concrete requirement; no optional sharing system or implementation added.


Content/PtS decomposition proposal — 2026-10-06: [minimum Content contract](../../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md)
records enforced ownership variants, exact byte/provider identity, attribution, streamed
read boundaries and legacy migration constraints. Propose CONTENT-READ then PTS-ADOPT
after LAUNCHER and before WRITE/REF (23 items if accepted). Current 21-item baseline
remains; actual DDL/proxy/browser/transfer contracts and final sizing remain readiness
inputs. No code, runtime tests or production inspection in this planning pass.


Content/PtS split approved — 2026-10-06: [current sequence and CONTENT-READ criteria](../../../_bmad-output/planning-artifacts/epics.md#contentpts-split-approved-and-current-sequence--2026-10-06)
record 23 delivery items, with CONTENT-READ and PTS-ADOPT after LAUNCHER and before
WRITE/REF. Acceptance-map rows now separate shared service proof from actual PtS
user/resource integration. CONTENT-READ detailed criteria are for discussion; DDL,
streaming/browser/proxy limits and remaining readiness inputs are not approved by this
ordering decision. No code, live changes or runtime tests.


CONTENT-READ criteria approved — 2026-10-06. [PTS-ADOPT detailed criteria](../../../_bmad-output/planning-artifacts/epics.md#candidate-story-e1-pts-adopt-use-pts-through-individual-platform-access)
are prepared for discussion: zero-membership entry, independent current account
capabilities, authenticated private source downloads, preserved corpus/import evidence,
launcher integration and controlled transition. Existing external source references are
not represented as protected private storage or proxied arbitrarily. No future PtS org
features, real account recreation or runtime verification added. The 23-item sequence
and all contract/readiness gates remain.


PTS-ADOPT acceptance approved — 2026-10-07, including permission/download/preservation
clarifications. Current [Access child criteria](../../../_bmad-output/planning-artifacts/epics.md#candidate-story-e1-access-a-configure-application-admission-and-grants-safely)
are reconciled with ADR-0052–0055: independent account/organization grants, typed scope,
coordinated PtS replacement and Content's service/ownership enforcement. Historical
parent v1-preservation/membership-only passages do not override these updates. The
23-item sequence stays unchanged; exact grant/operator/actor and Content transport/
adoption contracts remain before readiness. No code or runtime tests changed.


Individual grant design — 2026-10-07: [Access persistence/provisioning contract](../../../platform/docs/architecture/contracts/application-admission-and-discovery.md#individual-grant-persistence-and-administration--2026-10-07)
now specifies separate account_grants, structurally correct capability scope, current
account reference and revision-guarded operator assignment/revocation/regrant. Organization
grants stay membership-bound. No nullable-org shortcut, account grant inheritance, public
admin API or automatic PtS grant conversion. Actor projection, exact DDL/operator bounds,
Content transport and CE/SP readiness remain open; no application code or tests executed.


Account-only attribution refinement — 2026-10-07: [Identity actor contract](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#account-only-actor-resolution--2026-10-07)
now separates durable account actor setup from optional person/employment/membership.
ID-B controlled account_actor.ensure precedes optional linking; no read-side provisioning.
ACCESS-B/PTS-ADOPT resolve account-only actors, while Leave retains person-required own
scope. Actor preservation never restores grants to recreated accounts. Exact actor DDL/
projection/operator bootstrap and Content transport/mapping remain readiness inputs.
No application code, runtime tests or readiness approval.


Actor registry selected — 2026-10-07: [ADR-0056](../../../platform/docs/architecture/decisions/0056-durable-actor-registry-separate-from-login-accounts.md)
confirms separate durable attribution, while identity.users remains Auth-account profiles.
Retain System/Migrate and service identities without requiring new synthetic Auth users;
preserve old actors/history and transition existing references explicitly. ID-B owns the
schema/bootstrap/projection/writer adoption; no new story/UI or live account removal.
Model choice resolved; exact contracts and implementation readiness remain open.


Actor persistence progress — 2026-10-07: [Identity schema/lifecycle design](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#minimum-actor-persistence-and-lifecycle--2026-10-07)
selects a small actor registry and retained account association, current account checks,
controlled System/Migrate/service registration and explicit bootstrap provenance. Missing
write context never defaults to System. ID-B must still prove old FK/trigger/text-writer
adoption and precise privileges/bounds; no code or deletion executed. Continue Content
browser/streaming contracts; no additional story or readiness pass.


Browser download proposal — 2026-10-07: [Content transport discussion](../../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md#browser-transport-proposal--2026-10-07)
recommends app-specific secure HttpOnly file authentication tied to existing sign-in,
with current authorization per request; exact adapter/logout/renewal remains to choose.
Current bearer fetch alone does not authenticate native file links/viewers. Netlify's
published 26-second proxy timeout requires actual large-file routing feasibility proof;
no proxy or auth changes made. Discuss direction before selecting a session mechanism.


Download ingress direction accepted — 2026-10-07: [direct app gateway route](../../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md#direct-application-download-ingress--direction-accepted-2026-10-07)
bypasses Netlify for file bytes while retaining frontend hosting. Proposed per-app file
hostnames/TLS and cookie-session binding require validation before implementation readiness;
current gateway needs per-host/origin/method/stream configuration in its renderer. Synthetic
long-transfer and browser tests must pass on the selected path before activation. No wait-
for-production-failure approach, automatic signed URL fallback or live DNS change.


File-auth lifecycle proposal — 2026-10-08: [Content browser contract](../../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md#file-authentication-lifecycle-proposal--2026-10-08)
proposes reuse of existing sign-in/refresh and per-request current permission checks,
with explicit expiry/logout/account-switch and viewer behavior. Supabase JWT expiry and
late cookie-response races prevent claiming revocation from UI clearing alone. Select
and verify the minimal adapter before PTS-ADOPT readiness; no second refresh-token owner,
new authentication schema or code implemented. Behavior remains for discussion.


## File lifecycle approval and transfer behavior — 2026-10-08

User approved the file-authentication lifecycle behavior: existing sign-in/refresh,
expiry recovery, logout and account-switch isolation. This supersedes the earlier
for-discussion status; the exact adapter and provider revocation proof remain open.

[Download/preview behavior](../../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md#download-and-preview-behavior--proposed-2026-10-08)
is the next proposal: native download/PDF viewing, single-range support, fixed finalized
bytes and honest interrupted-transfer handling. CONTENT-READ owns shared transport;
PTS-ADOPT owns browser/gateway proof; Leave E4 later consumes it. Existing E1 sequence
and first draft slice remain unchanged. No implementation or readiness pass.


Download acceptance clarification — 2026-10-08: user accepted browser-owned
download/viewer/resume behavior enabled by application headers, partial reads and current
authorization. Record these as technical criteria within CONTENT-READ/PTS-ADOPT; no custom
viewer/download manager or separate browser-feature story.

Next discussion: [concrete PtS adoption mapping](../../pts/docs/architecture/contracts/account-access-and-corpus-transition.md#concrete-adoption-mapping--proposed-2026-10-08)
proposes reviewed legacy-to-target object/association evidence, preserving bytes and
verified IDs without copying per account or implicitly merging unrelated partitions.
Physical schema, deployed inventory and readiness remain open. No application code changed.


PtS concrete adoption mapping approved — 2026-10-08: reviewed selected-object mappings,
application ownership, preserved bytes/associations and verified IDs; existing opaque
provider paths may remain. Physical inventory/schema/rehearsal remain pending.

Next discussion: [operator execution surface](../../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md#operator-execution-surface--proposed-2026-10-08)
proposes protected owner-local command-line entry points for E1 setup, with verified
execution identity and restricted owner writers. This refines the existing command
contract; it does not replace E2 administration or create another story. Concrete
authentication/privileges, other technical contracts and readiness remain unresolved.


Operator execution surface approved — 2026-10-08: protected owner-local CLI setup,
verified execution identity and restricted owner writers; E2 administration remains.
Concrete binding/privileges and technical readiness stay open. Next proposal:
[setup verification boundary](../../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md#setup-verification-boundary--proposed-2026-10-08),
using existing acceptance suites/runbooks to distinguish local command completion from
effective authorization and a working consumer. No new story, product status system,
production mutation or runtime evidence.


Setup verification boundary approved — 2026-10-08. User additionally proposed a test
application in development, staging and production for release/support verification.
[Platform verification app proposal](../../../platform/docs/architecture/contracts/platform-verification-app.md) recommends extending E1-REF
with an explicitly sized hosted scope, real shared-service paths and restricted synthetic
production journeys; application-specific tests remain on their owning apps. Direction
is under discussion; no new story count, production fixture permission, implementation
or readiness pass. Current disposable reset safeguards remain binding.


Platform verification direction approved — 2026-10-08: [approved responsibility split](../../../platform/docs/architecture/contracts/platform-verification-app.md#approved-boundary).
The verification app exercises shared platform features; app-specific synthetic journeys
run in each actual application with dedicated accounts/test data and required org fixtures.
Shared runners/reporting do not duplicate product workflows. Hosted scope still requires
explicit sizing; 23-item sequence, first Leave slice and readiness gates remain unchanged.
No implementation, deployment, production test execution or new schedule authorized.


Hosted verification sizing proposal — 2026-10-08: add E1-VERIFY after REF and before
PEOPLE for the existing reference journey in explicit dev/staging/production environments,
using restricted synthetic fixtures and existing automated reports. This would make 24
E1 items if approved; the current 23-item matrix is not changed yet. PtS retains its earlier
independent adoption checks, and Leave synthetic journeys remain in Leave consumer stories.
See [candidate criteria](../../../_bmad-output/planning-artifacts/epics.md#candidate-story-e1-verify-exercise-the-shared-reference-journey-in-hosted-environments).
No implementation, environment publication or readiness pass.


Hosted verification approved — 2026-10-08: E1 now has 24 delivery items, with VERIFY
immediately after REF and before PEOPLE. One maintained platform reference application:
REF owns the reusable journey and local/CI tests; VERIFY adds hosted configuration,
restricted fixtures and release execution using the same source/scenarios. No duplicated
UI/API implementation or per-environment test suite. Disposable generator checks remain
CI artifacts. The acceptance ownership matrix includes VERIFY; first Leave slice and
all readiness gates remain unchanged. No implementation or deployment executed.


Hosted fixture proposal — 2026-10-08: [verification contract](../../../platform/docs/architecture/contracts/platform-verification-app.md#hosted-fixture-boundary--proposed-2026-10-08)
proposes stable per-environment synthetic accounts/two organizations, known allowed/denied
permissions, bounded run records and exact owner-scoped cleanup. Ordinary production
runners cannot administer accounts/grants or reset environments. Other applications use
their own lifecycle rules for synthetic data. Refines VERIFY only; 24-item sequence and
readiness gates stay unchanged. Concrete retention/limits and invocation remain open.


Hosted fixture boundary approved — 2026-10-08. Stable dedicated identities, known
allowed/denied access, bounded test records and exact ownership-checked cleanup stay
within VERIFY; concrete limits remain to settle. Next discussion returns to ACCESS-B:
[initial service caller matrix](../../../platform/docs/architecture/contracts/application-admission-and-discovery.md#initial-service-caller-matrix--proposed-2026-10-08)
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
Next [current-context wire proposal](../../../platform/docs/architecture/contracts/identity-access-employment-e1.md#people-current-identity-context--proposed-2026-10-08)
uses a restricted Access-owned identity/membership projection for People, alongside
People's service/own-data policy and Leave's independent application authorization.
ACCESS-B supplies the endpoint before PEOPLE; no new service/story or future dependency.
Wire remains for discussion; 24-item sequence and readiness gates remain unchanged.


People API boundary reaffirmed — 2026-10-08: user agrees to independent HTTP ownership;
co-hosting is not a deciding factor. Retain existing API/no-cross-owner-table architecture,
with no accepted ADR change. This does not claim the proposed identity-context endpoint
or its provider verification has been implemented or independently approved in detail.

Initial [reference capability names](../../../platform/docs/architecture/contracts/platform-verification-app.md#initial-reference-capability-identifiers--2026-10-08)
are now concrete: `reference.record.read` and `reference.record.create`, organization
scope, entry by read. Existing setup/Access/WRITE/REF/VERIFY responsibilities share those
identifiers; no extra story or expanded CRUD. Remaining technical contracts/readiness
stay open; 24-item sequence unchanged.


Reference example wire proposal — 2026-10-08: [owning contract](../../../platform/docs/architecture/contracts/platform-verification-app.md#example-record-and-createread-wire--proposed-2026-10-08)
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
and automated fixtures. [Incremental placement proposal](../../../platform/docs/architecture/contracts/platform-verification-app.md#incremental-example-placement--proposed-2026-10-08)
assigns draft examples to D2-B/D3/D4/D5 shared-artifact promotion, explicit Save editing
to the first E2 configuration writer, preference examples to their first real consumer,
and finalization only with E5. Initial REF/VERIFY remains create/read and independently
completable. Additional demo scope must be included in consuming-story sizing; no new
standalone count or implementation authorization. First Leave slice/readiness unchanged.


Reference example placement approved — 2026-10-08: incremental demonstrations join
their first proven consumer as proposed, with explicit sizing and no future dependency
for initial REF/VERIFY. Next [minimal draft example proposal](../../../platform/docs/architecture/contracts/platform-verification-app.md#minimal-draft-demonstration--proposed-2026-10-08)
uses optional title/note, its own account/org ownership and explicit single-active scope,
plus existing autosave/close/discard protections. No Leave business fields or People
dependency. New draft capability registration and hosted checks occur only with their
consumer/cleanup readiness. 24-item sequence unchanged; no implementation or test runs.


Reference draft example approved — 2026-10-08. Consolidated the existing E1 contract
gaps and owners in the linked current checkpoint, distinguishing planning inputs from
future runtime/release evidence. Next focus is ENV/P1/SERVICE reproducibility inputs;
no architecture restart, new epic, application code or readiness pass.
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    

Build ownership proposal — 2026-10-08: [working-tree inventory and PtS integration](./testing/e1-environment-and-dependencies.md#dependency-ownership-and-pts-integration--proposed-2026-10-08)
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
[Publication target and owner mapping](./testing/e1-environment-and-dependencies.md#frontend-publication-target--approved-2026-10-08)
assigns workspace tooling to ENV and coordinated current-app publication adoption to
PTS-ADOPT/deployment, with affected Scribeswell checks. Final sizing/readiness remains
binding; 24-item sequence unchanged. No code, lockfile, hosting or DNS changes executed.


User-story planning resumed — 2026-10-08: naming is parked. E2 discussion begins with
[candidate Story 2.1](../../../_bmad-output/planning-artifacts/epics.md#story-21-enable-or-suspend-leave-for-an-organization):
authorized platform administration enables/suspends organization Leave availability under
ADR-0046; organization administrators later manage user roles within enabled apps. This
uses completed E1 foundations but does not mark E1 contracts/coverage, Phase 1 or
implementation readiness complete. No implementation or new runtime authority.


E2 story progress — 2026-10-11: Story 2.1 organization Leave availability approved.
[Story 2.2 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-22-assign-leave-roles-to-an-existing-organization-member)
covers shared default-role assignment for an existing exact account/membership, explicit
review, combined capability effects and safe revocation/retries. Custom-role editing and
invitations follow separately. Role/catalog/delegation/projection and grant-adoption
contracts remain readiness inputs; E1 gates and first slice stay binding. Planning only.


Supervisor replacement discussion — 2026-10-11: Story 2.2 remains under discussion.
Existing supervisor-based policy resolves eligible supervisors automatically for new
requests, while role assignment alone does not establish reporting relationships.
[Convenience proposal](../../../_bmad-output/planning-artifacts/epics.md#supervisor-replacement-and-approval-routing-discussion--2026-10-11)
recommends a narrow shared Replace supervisor action with selection/effective date/review,
existing setup guidance and separately confirmed E5 transfer of outstanding approvals.
No general bulk editor, silent pending reroute, new approved feature or ADR change.
Batch/history/impact contracts remain binding before delivery; documentation only.


E2 progress — 2026-10-11: Story 2.2 approved with supervisor-routing clarification.
Focused Replace supervisor convenience is accepted and synchronized to features §2/10
and shared/Leave UX; shared batch/history and E5 pending-transfer contracts remain gates.
[Story 2.3 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-23-create-or-duplicate-an-application-specific-custom-role)
now covers blank creation/independent duplication of Leave custom roles, without granting
access until separate role assignment. Assigned-role editing/deletion follow separately.
All current E1/Phase 1 readiness checks remain open; planning only.


E2 progress — 2026-10-11: Story 2.3 custom-role creation/duplication approved.
Assignment entry point is being clarified: current shared UX is the target member's
Application access page; the user's “me view” wording could instead mean their own profile.
No self-service grant change inferred. Existing authorization/readiness gates remain.


E2 UX/story progress — 2026-10-11: role assignment drawer approved, shared/Leave UX
and features synchronized. Same member/app form is opened from People/settings/holders,
with reviewed confirmation and safe return; dedicated pages edit role definitions.
[Story 2.4 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-24-review-and-apply-changes-to-a-custom-role-held-by-members)
now covers holder-impact review and explicit custom-role edits, including stale review
and retained equivalent authority. Role deletion follows separately. Actor/catalog/
assignment-impact contracts and E1/Phase 1 readiness remain open; planning only.


E2 progress — 2026-10-11: Story 2.4 custom-role impact editing approved.
[Story 2.5 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-25-delete-an-unassigned-custom-role-while-preserving-its-history)
covers blocked deletion while assigned, holder-drawer resolution/return, atomic
assignment-versus-deletion protection and historical role retention. Built-in roles
remain protected. Exact lifecycle/retention/writer contracts and implementation readiness
stay open; planning only, with no role or account changes executed.


E2 progress — 2026-10-11: Story 2.5 unused custom-role deletion approved.
[Story 2.6 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-26-invite-a-person-to-join-an-organization-securely)
covers authorized recipient-bound invitations, status/delivery recovery and verified
membership acceptance with no automatic employment/roles. Provider/Entra integration,
expiry/reissue and invitation-delivery foundation must be resolved/sized before readiness;
no future E3 notification dependency or live invitation assumed. Planning only.


Invitation clarification — 2026-10-11: core 2.6 scope accepted, admission-path detail
under discussion. Entra sign-in itself needs no application invitation; membership must
still come from authorized invitation/provisioning. The story is an onboarding option,
not mandatory for every SSO user. No tenant-managed auto-provisioning/group sync or
email-domain admission is added; those need a separate trust/lifecycle contract.


Onboarding policy discussion — 2026-10-11: [refinement proposal](../../../_bmad-output/planning-artifacts/epics.md#organization-onboarding-policy-refinement--proposed-2026-10-11)
recommends invitation-only normal UI when no trusted tenant mapping exists, then explicit
opt-in automatic enrollment offered after verified tenant setup. Controlled E1 bootstrap/
adoption provisioning remains separate. Direction/scope is not yet approved; tenant-managed
onboarding needs its own contract/sizing and ADR-0002 disposition before implementation.


Onboarding amendment approved — 2026-10-11: platform ADR-0057 narrows routine organization
onboarding to invitations until trusted Entra tenant setup and separate explicit automatic
onboarding opt-in. Features/shared UX/agent context are synchronized; arbitrary provider
replacement and Graph/SCIM sync remain deferred. Restricted E1 bootstrap/adoption stays.
Story 2.6 is approved with this policy. [Story 2.7 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-27-verify-a-trusted-microsoft-entra-tenant-for-an-organization)
verifies tenant setup with enrollment off; automatic-join execution is a following bounded
story, not a hidden dependency. Exact provider feasibility/trust/lifecycle contracts and
all E1/Phase 1 readiness gates remain pending. Planning only; no provider/account change.


E2 progress — 2026-10-11: Story 2.7 verified organization Entra tenant setup approved.
[Story 2.8 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-28-explicitly-enable-automatic-onboarding-from-a-trusted-tenant)
adds explicit default-off enrollment opt-in, current eligible admission and policy-off
handling without auto-employment/app grants. Initial proposal prevents automatically
recreating a removed membership, requiring deliberate authorized rejoin. Exact audience/
guest/identity evidence and lifecycle/commit ordering remain pre-story decisions; no
provider/role synchronization or runtime implementation. E1 readiness stays pending.


Advance-access discussion — 2026-10-11: user requests administrator setup before first
sign-in. [Proposal](../../../_bmad-output/planning-artifacts/epics.md#administrator-prepared-access-before-first-sign-in--proposed-2026-10-11)
allows explicit intended roles prepared with onboarding, pending until verified account/
membership binding. Invitations remain the normal route without enabled trusted tenant
enrollment; role approval is separate from automatic membership. Exact pending-activation
scope needs user confirmation and a linked policy refinement; no code/grants executed.


E2 advance-access agreement — 2026-10-11: platform ADR-0058 records explicit prepared
roles before first sign-in with pending verified-target activation. Features/shared UX/
agent context updated; 2.8 automatic enrollment scope approved with this distinction.
[Story 2.9 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-29-prepare-and-activate-application-access-before-first-sign-in)
covers preparation/activation/withdrawal and staged Identity/Access recovery. Exact
identity/role-version/lifecycle contracts and E1/Phase 1 readiness remain pending.
No application code, accounts, grants, invitation or provider setup changed.


E2 progress — 2026-10-11: Story 2.9 approved with automatic activation of already
explicitly reviewed roles in the unchanged valid case; relevant changes remain pending/
Needs review. [Story 2.10 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-210-remove-a-members-organization-access-without-erasing-history)
adds normal membership removal using the earlier exact-membership retirement contract,
preserving employment/history and independent account access. Automatic re-enrollment
cannot undo removal. Admin continuity/self-removal and workflow-impact contracts remain
pre-story gates; no actual accounts, memberships or application code changed.


E2 progress — 2026-10-11: Story 2.10 membership removal approved, including fresh access
membership on re-admission without replacing login/person/employment. [Story 2.11 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-211-add-an-employee-with-an-initial-employment-period)
now covers minimum shared employee/person and initial dates, with accountless support,
scoped uniqueness/history and honest Identity/People recovery. Login/app roles and
Leave-specific work settings remain independent. Authority/profile/create/impact contracts
remain pre-story gates; E1 readiness still pending and no employee/code changes executed.


E2 progress — 2026-10-11: Story 2.11 shared employee creation approved with clearer
person/People employment wording. [Story 2.12 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-212-record-an-employment-end-date-with-reviewed-consequences)
covers inclusive employment end dates, retained history and reviewed consuming effects,
separate from membership/account removal. Existing Leave end-date/proration/correction
rules remain binding with their E3/E5/E6 consumers; no later UI dependency or simulated
calculation success. Shared consequential impact handshake remains a pre-story gate.
No application code, employee, access or provider configuration changed.


E2 progress — 2026-10-11: Story 2.12 employment end-date review approved.
[Story 2.13 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-213-record-a-return-to-employment-without-replacing-the-employee)
adds a nonoverlapping period under the same enduring employment identity, preserving
person/history/settings/drafts subject to current access and revalidation. Organization
re-admission is needed only if membership was retired, with no restored old roles.
Period/tenure/consumer-impact contracts remain pre-story inputs; no record/code changes.


E2 progress — 2026-10-11: Story 2.13 returning employment period approved.
[Story 2.14 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-214-maintain-simple-organization-departments-and-locations)
adds People-owned simple scoped department/location catalogues with stable rename/history
and archive semantics. Employee assignment follows separately; fixture references avoid
that later UI dependency. Location does not change Leave work profiles. Exact catalogue/
reference/history and authority contracts remain gates; planning only, no record/code changes.


Catalogue saving clarification — 2026-10-11: retain ADR-0051 explicit saving for shared
business configuration, with one Create/Save and Cancel for simple department/location
forms. Refined candidate 2.14 to avoid a redundant review screen for simple create/rename;
archive shows its consequences and requires confirmation. No backend administrative draft
or direct typing-time autosave. Story still under discussion; accepted ADR unchanged.


E2 progress — 2026-10-11: Story 2.14 scoped department/location catalogues approved
with one Create/Save and Cancel for simple edits, consequence confirmation for archive.
[Story 2.15 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-215-assign-or-clear-an-employees-department-and-location)
adds optional dated employee placement, Unassigned handling, history and authorized
filters without automatically changing Leave profiles or access. Dated nullable-reference/
retirement/revision contracts remain pre-story gates; no actual records/code changed.


Placement simplicity refinement — 2026-10-11: candidate 2.15 now proposes changes on
Save with server-recorded effective/change history, no user date picker or planned/
backdated assignment UI. Preserve ADR-0041 references through catalogue retirement;
shared location eligibility/calendar consumers remain explicit contracts while work
profiles own schedules/holidays. Failed label/choice loading preserves saved IDs and
shows Retry, not a false Unassigned value. Direction remains for discussion; no code.


Placement form simplification — 2026-10-11: user prefers simple active/archived state;
2.15 now recommends one form-load response bundling employee placement/current labels
and scoped option lists, with form-level Retry if required data fails. Archived current
references display correctly; Save revalidates actual choices/revision. Shared owner HTTP
boundaries remain; no separate per-field recovery or scheduled placement UI. No code.


E2 progress — 2026-10-11: Story 2.15 optional department/location assignment approved
with immediate explicit saving, server history and one complete form-load response.
[Story 2.16 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-216-assign-or-clear-an-employees-supervisor)
adds one current manual supervisor relationship, optional/organization-scoped with no
self-reference, and Leave-owned eligibility guidance. Shared relationship changes grant
no roles and silently reroute no pending work. Bulk replacement follows separately;
reference/eligibility/impact and readiness contracts stay open. Planning only.


Supervisor story clarification — 2026-10-12: 2.16 remains under discussion. Existing
last-change actor/time fields plus compact People-owned immutable change history preserve
who changed each supervisor relationship; no duplicate activity/audit engine. Shared
supervisor facts stay independent of Leave approval roles, with selected eligibility
warning/access-management guidance; direct Leave approver pickers remain eligible-only.
New submission resolves/snapshots the current eligible supervisor; old pending requests
retain assignment until explicit reroute. Exact event/reference/eligibility contracts
stay open; no implementation or employee/access changes performed.


Change-history clarification — 2026-10-12: recommend one People employment-change table
for its related changes, with shared envelope/writer conventions and typed bounded event
payloads. Retain current-row attribution and local atomic history. Avoid per-field history
tables, arbitrary table-name/value dumps or a universal audit service; broader reuse follows
proven consumers. Exact schema/index/payload and readiness remain open; no benchmark claim.


Scaffold history agreement — 2026-10-12: common envelope, controlled event schemas and
transaction-aware owner-local writer approved. [Builder direction](../../../platform/builder-cli/README.md#reusable-owner-local-change-history--approved-2026-10-12)
requires first-consumer templates/types/fixtures/display promotion and proof, preserving
current attribution and avoiding duplicate history/audit or universal runtime capture.
People employment_change is one related-event family. No implementation/readiness pass.


Scaffold-input proposal — 2026-10-12: user asks about structured app metadata for planning/
reuse enforcement. Recommend a thin versioned/schema-validated configuration derived from
approved requirements with selected patterns, owner/scope/saving/history/source/test refs.
[Builder proposal](../../../platform/builder-cli/README.md#thin-application-scaffold-configuration--proposal-2026-10-12)
keeps specs/ADRs/UX authoritative and avoids duplicating DB/API schemas or adding a new
workflow/runtime engine. Initial generator input is P1 scope; patterns join with their
proven first consumer. Direction/format/exact schema still for discussion, not implementation.


E2/scaffold progress — 2026-10-12: thin schema-validated scaffold input direction approved
under platform ADR-0059; exact format/schema/generator implementation remains gated.
Supervisor 2.16 proceeds with the clarified common immutable history/People fact/Leave
eligibility boundary. [Story 2.17 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-217-replace-a-supervisor-for-selected-employees)
formalizes the approved narrow selected replacement action with reviewed effective date,
scoped per-item history/results and separate E5 pending transfer. No general bulk editor;
batch/reference/impact contracts and E1/Phase 1 readiness remain pending. No code/data change.


E2 progress — 2026-10-12: Story 2.17 focused supervisor replacement approved. Work
arrangements now proceed with [Story 2.18 calendar setup candidate](../../../_bmad-output/planning-artifacts/epics.md#story-218-configure-an-organization-holiday-calendar)
before profiles so calendar references have a completed owner foundation. Calendar version/
partial-day/date/impact semantics are pre-story inputs; profile/calculation consumers own
later end-to-end behavior. Shared People location stays separate. Readiness remains
pending, with no calendar/code/data changes performed.


E2 progress — 2026-10-12: Story 2.18 holiday calendar setup approved.
[Story 2.19 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-219-create-a-reusable-leave-work-profile)
creates a named initial version with working days/minutes/breaks, work timezone/calendar
and standard-day conversion, without assigning employees or changing defaults. Assignment,
consumed-profile edits/overrides/archive follow separately. Schedule/version/calendar/
rounding and E1-setting compatibility contracts remain pre-story gates; no code/data change.


E2 progress — 2026-10-12: Story 2.19 approved, with net working hours as default and
detailed working/break times advanced. Features/Leave UX synchronized; schedule versions
retain effective settings independently of audit and computed snapshots.
[Story 2.20 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-220-assign-or-change-an-employees-leave-work-profile)
adds explicit employee profile assignment with dated/reasoned impact review, retained
overrides and default fallback. Net/timetable/partial-holiday and effective-date/override/
impact contracts remain pre-story gates; no profiles/settings/code changed in planning.


E2 progress — 2026-10-12: Story 2.20 employee work-profile assignment approved with
clarified fallback and retained earlier schedule settings/request snapshots.
[Story 2.21 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-221-set-or-change-the-organizations-default-leave-work-profile)
sets/changes the organization default with reviewed effective-date/fallback employee
impacts, preserving explicit profiles/overrides and prior calculations. Exact default/
timezone/override/reference/impact contracts remain gates; no settings/code changed.


E2 progress — 2026-10-12: Story 2.21 organization default work-profile changes approved.
[Story 2.22 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-222-override-an-employees-work-settings-or-restore-profile-inheritance)
adds explicit per-field employee work-setting overrides and Reset to profile, with dated
impact review, preserved sources/history and no shared-profile rewrite. Net/timetable/
inheritance/null/reset/current-effect contracts and E1 readiness stay pending. These are
work settings, not E3 entitlement/balance overrides; no code or records changed.


E2 progress — 2026-10-12: Story 2.22 per-employee work-setting override/reset approved.
[Story 2.23 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-223-review-and-publish-changes-to-a-shared-work-profile)
adds shared-profile edit/impact review and one new effective schedule version while
retaining overrides/old rules/submitted results. Name-only metadata saves do not need a
fictitious calculation version. Current usage/review/freshness/net-timetable/partial-day
and consumer impact contracts remain gates; no actual profile/settings/code changed.


E2 progress — 2026-10-12: Story 2.23 shared-profile version/impact edits approved.
[Story 2.24 candidate](../../../_bmad-output/planning-artifacts/epics.md#story-224-archive-an-unused-work-profile-without-losing-its-history)
archives unused profiles only after current/scheduled/default dependencies are resolved,
retaining version/request history with simple Active/Archived presentation. Assignment/
archive concurrency and current-vs-historical/ended-employee dependency contracts remain
pre-story gates; no employee/profile changes or application code implemented.


E2 progress — 2026-10-12: Story 2.24 profile retirement approved with Active/Inactive
and Deactivate presentation; features/shared/Leave UX synchronized while ADR-0086 storage/
version/dependency rules remain. [Story 2.25 setup guidance candidate](../../../_bmad-output/planning-artifacts/epics.md#story-225-see-actionable-setup-status-from-saved-configuration)
implements delivered E2 section assessments and approved three-area presentation, with
real E3 type/policy predicates integrated by E3 before full readiness claims. No manual
completion/email/opening-balance row; exact predicates/coverage/sizing remain open. No
E2 completion, SP pass or code/status record change implied by this planning item.


Setup clarification — 2026-10-12: 2.25 is Leave setup for the current organization,
not a cross-app readiness record. API derives section status from actual saved owner
configuration/reads and UI renders it; no independently edited status field. Recommend
reusing existing Leave/shared administration forms in the setup navigation/drawers, with
return context. The validation sentence explains that a displayed status can become stale,
not a new workflow requirement. Global overview/embedding remains outside current scope.


E2 progress — 2026-10-12: Story 2.25 Leave-specific setup/derived-status scope approved.
Remaining source reconciliation identified [team meaning/ownership decision](../../../_bmad-output/planning-artifacts/epics.md#remaining-e2-team-meaning--for-discussion-2026-10-12):
features require managed teams and team grouping but also define team calendar as direct
reports; ADR-0041 does not place teams in shared core. Discuss independent named teams
versus supervisor-derived groups before adding/defering any story. No existing team
requirement removed or E2/global readiness/coverage completion claimed.


E2 team scope resolved — 2026-10-12: [Leave ADR-0125](./architecture/decisions/0125-supervisor-based-teams-for-mvp.md)
accepts supervisor-based direct-report teams for MVP. Features/UX reflect derived Team
filters/grouping; independently named/project team administration and team-profile defaults
are deferred. E2 employee/supervisor stories supply facts, E5 availability and E7 reports/
calendar views own authorized temporal queries. No new team catalogue/story/entity;
remaining source coverage/sizing/readiness still requires validation and no code/data changed.


E2 source checkpoint — 2026-10-12: compared features Permissions/§1–3 and approved
employee/profile/setup UX with the 25 agreed scopes; exact atomic source-to-test/sizing
and all readiness gates remain open.
[Story 2.26 summary candidate](../../../_bmad-output/planning-artifacts/epics.md#story-226-view-an-employees-employment-and-leave-work-settings-together)
closes the integrated employee-summary/entry-point gap using real Employment & approval
and Work schedule owner reads plus existing focused edit forms. E3 adds actual Leave
entitlement/balance sections; E5 owns request history/approval consumers. No future UI
prerequisite, fake balance, extra employee master or new code/table implemented.


Planning progression — 2026-10-12: Story 2.26 employee summary/navigation approved.
E2 has 26 agreed discussion scopes; atomic source/UX coverage, concrete technical inputs,
agent sizing and all E1/Phase 1 readiness still pending.
[E3 grouping proposal](../../../_bmad-output/planning-artifacts/epics.md#e3--configure-entitlement-and-understand-available-leave)
orders initial type/policy setup, employee applicability, calculations/projection, required
notification foundation, one-off adjustments, recurring overrides, balance explanation and
used-policy change/lifecycle. Groups will split into bounded individual stories; no code,
calculation/notification/migration execution or passed gate claimed. First Leave slice retained.


Session handoff — 2026-10-12: [E3 handoff and copyable prompt](./planning-handoff-e3.md)
prepared at user's request. E3 groups remain proposed; E1/E2 scopes are agreed but contracts,
source/test sizing and readiness incomplete. First planned new implementation is shared
ENV/scaffold/identity/access foundation after its required approval/gate, then Leave's
first slice. Smaller independent app can follow its own bounded planning/readiness in
parallel, coordinated shared ownership; no app scope, worktree or implementation authorized
merely by the advice. Working-tree planning changes must be carried into a new worktree.

E3 sequence approved — 2026-10-12: user approved the nine
[delivery groups](../../../_bmad-output/planning-artifacts/epics.md#approved-delivery-groups).
Group 2 covers policy applicability and assignment/settings; recurring override mutations
belong to group 7. Every policy/entitlement mutation requiring notification follows the
group 5 business-delivery foundation. Initial configuration must not hide later notified
changes. Individual stories will be detailed collaboratively, starting at Story 3.1;
final numbering/sizing, source/test coverage, pre-story inputs and readiness remain open.
The first slice remains sign in → select organization → create/resume draft → autosave
→ close → reopen. No Leave implementation, migrations or passed gate from this approval.

Story 3.1 scope agreed — 2026-10-12: user approved
[create/view organization leave types](../../../_bmad-output/planning-artifacts/epics.md#story-31-create-and-view-an-organizations-leave-types),
including the clarified ability to select a new type and preserve draft input before
policy/eligibility checks required for submission. Reuse E1 type/version/choice identity;
do not infer policy activation or entitlement from metadata publication. Additional
metadata/API/runtime-writer contracts, test mapping and final sizing remain open.
Continue sequential collaborative E3 decomposition; no code or readiness change.

Story 3.2 scope agreed — 2026-10-12: user approved
[policy summary/version history](../../../_bmad-output/planning-artifacts/epics.md#story-32-view-a-leave-types-policy-and-version-history).
Current/scheduled/previous policy reads use controlled owner fixtures and do not require
a later editor/calculator. Exact version-selection/date/read/disclosure contracts, source
test mapping and final sizing remain pre-story gates. Continue at Story 3.3 discussion;
no readiness, implementation or workflow-completion claim.

Story 3.3 scope agreed — 2026-10-12: user approved
[first-policy configuration/publication](../../../_bmad-output/planning-artifacts/epics.md#story-33-configure-and-publish-a-leave-types-first-policy)
for an unused type, with the four-section editor, review/explicit publication, current
authority, immutable versions and duplicate-safe recovery. Contract terminology retained
after clarification. Full field/ownership/validation/effective-date/publication contracts,
source/test mapping and final agent sizing remain binding before implementation; split
the scope if sizing requires it without future-story dependencies or partially active rules.
No existing employee entitlement effects/required notifications hidden in initial setup.
Continue at Story 3.4 discussion; no readiness or implementation change.

Story 3.4 clarification — 2026-10-12: starter settings use a concise Starter example
label and remain editable; no separate legal-warning panel or repeated disclaimer is
required. User accepted confirmation by the Leave Manager with current policy-management
permission during the existing publication review, covering entitlement, schedules,
holidays and organization-specific rules. No separate client sign-off workflow or role;
E8 import/email sign-off remains distinct. Full Story 3.4 approval, contract/test mapping,
sizing and readiness remain pending.

Story 3.4 scope agreed — 2026-10-12: user approved
[reviewed starter examples](../../../_bmad-output/planning-artifacts/epics.md#story-34-review-starter-examples-before-activating-a-policy)
with a concise Starter example label, editable settings and confirmation by the authorized
Leave Manager in the existing publication review. E1 type identity, approved supervisor
starter defaults and initial-publication protections are retained. No legal-warning panel,
extra sign-off workflow, implicit employee assignment or grant. Continue to group 2 at
Story 3.5 discussion; source/test contracts, final sizing and readiness remain open.

Story 3.5 scope agreed — 2026-10-12: user approved
[employee policy applicability explanations](../../../_bmad-output/planning-artifacts/epics.md#story-35-explain-which-policy-applies-to-an-employee).
Conflicting applicability is rejected when saved, including concurrent writer paths;
required-information outages show Couldn't check / Retry rather than employee ineligibility.
Matching/precedence, employment-type ownership, tenure/period and date contracts remain
open before readiness. No inferred assignment, balance effect or entitlement override.
Continue at Story 3.6 discussion; final source/test mapping and sizing remain binding.

Policy applicability simplification accepted — 2026-10-12:
[ADR-0126](./architecture/decisions/0126-explicit-policy-assignment-with-employee-filters.md)
narrows MVP policy eligibility to explicit assignment after filtered employee selection.
No dynamic eligibility rules; changing filters/facts or adding employees does not silently
alter the reviewed assigned set. Backend enforcement remains current and scoped, with
all other request rules/draft protections retained. Story 3.3's eligibility fields and
Story 3.5's automatic rule/matching wording follow this later decision: resolve explicit
assignment/date/version and reject conflicts, not employment-type/location/tenure rules.
Exact filter fact availability, assignment/version/effective-date/conflict and effect/
notification contracts remain pre-story gates. Notifications/calculation foundations must
precede affected assignment writers; no inferred exemption, implementation or readiness.

Story 3.6 scope agreed — 2026-10-12: user approved
[policy employee list/filter/selection](../../../_bmad-output/planning-artifacts/epics.md#story-36-view-and-select-employees-for-a-policy).
Exact selections are provisional and never assignments; accountless employment and
current organization/resource checks remain binding. Assignment confirmation is a
separate remaining group 2 write obligation after required calculation and notification
foundations. Continue to bounded working-time/calculation stories at 3.7; no claim group
2's assignment mutations are complete. Exact read/filter/date/selection contracts,
source/test coverage, final sizing and readiness remain open.

Story 3.7 scope agreed — 2026-10-12: user approved
[effective-schedule duration calculation](../../../_bmad-output/planning-artifacts/epics.md#story-37-calculate-leave-duration-from-the-employees-work-schedule).
Backend full-day/date, exact-half and 30-minute hourly rules use actual versioned
working time with holidays/breaks; standard-day conversion remains distinct. Bind
partial-holiday/DST/fractional-minute and owner-version/API contracts before readiness.
Preview presentation, funding/reservations and real aggregate concurrent-request guards
retain later owners. Continue at Story 3.8 discussion; no code/tests/readiness claim.

Story 3.8 scope agreed — 2026-10-12: user approved
[daily earning component](../../../_bmad-output/planning-artifacts/epics.md#story-38-calculate-daily-earned-entitlement),
with start-of-local-day inclusion, actual leave-year denominator, inclusive employment
periods, cumulative precision and prospective policy-rate segmentation. No posted daily
earning or snapshots on reads. Exact allowance conversion/period/version/precision inputs
remain pre-story gates; caps/expiry/actual-event replay must be delivered before this
component is presented as available balance. Continue at Story 3.9 discussion; all
source/test/sizing/readiness gates remain open.

Story 3.9 scope agreed — 2026-10-12: user approved
[ordered immutable actual balance history](../../../_bmad-output/planning-artifacts/epics.md#story-39-preserve-an-ordered-history-of-actual-balance-changes).
Internal atomic recording/authorized reads use controlled owner fixtures; effective dates,
recorded times, durable actors, source/correction links and server order remain distinct.
Retry reuses events/sequence; no generic event API, ledger editor or posted daily accrual.
Actual mutation consumers prove domain effects/notification/snapshot obligations later.
Continue at Story 3.10 discussion; event/source/amount/sequence/retry contracts, final
source/test mapping, sizing and readiness remain open.

Story 3.10 scope agreed — 2026-10-12: user approved
[daily accumulated-cap calculation](../../../_bmad-output/planning-artifacts/epics.md#story-310-apply-accumulated-balance-caps-to-daily-earning),
including precise cap-before-rounding, historical headroom/no catch-up, next-day resumption
and earned/future reservation distinctions. Drafts reserve nothing; final approval consumes,
pending release does not create headroom. Bind ordered precise state/event/reservation
contracts and integrate actual expiry/rollover consumers before complete availability claims.
Continue at Story 3.11 discussion; no code/tests/readiness claim, final sizing remains open.

Story 3.11 scope agreed — 2026-10-13: user approved
[upfront annual entitlement calculation](../../../_bmad-output/planning-artifacts/epics.md#story-311-calculate-upfront-annual-entitlement),
including period-start/joining availability, inclusive calendar-day proration versus full
allowance, final whole-minute floor, departure consequences, preserved current-period
allowance after prospective rate change and cap exclusion/no catch-up. Actual mutation
writers retain review/history/request/notification safeguards. Technical inputs/source
tests/final sizing/readiness remain open. User's new upfront-plus-proration default
question is under discussion; existing policies/default decisions unchanged so far.

New automatic-policy default accepted — 2026-10-13:
[ADR-0127](./architecture/decisions/0127-upfront-entitlement-with-calendar-day-proration-default.md)
records upfront annual availability plus calendar-day joining/leaving proration as
editable initial selections. Preserve existing policies, explicit choices and reviewed
example-specific settings. Daily/monthly alternatives and monthly adjustment default
remain; daily mode has no second proration and manual-only remains separate. No annual
amount/period-basis/cap/carry-over default selected. Stories 3.3/3.4 trace form defaults;
3.11 retains existing upfront calculation/departure safeguards. Requirements/spine/UX/
epics/handoff updated; no generic scaffold default, shared-UI or agent-context change.
Continue Story 3.12 discussion; contracts/test coverage/sizing/readiness remain open.

Story 3.12 scope agreed — 2026-10-13: user approved
[complete monthly entitlement instalments](../../../_bmad-output/planning-artifacts/epics.md#story-312-calculate-monthly-entitlement-instalments),
with twelve aligned anchored periods, local start/end availability, cumulative whole-minute
precision and no replenishment of consumption/cap exclusions. Partial employment/rate
changes follow in a separate bounded story using ADR-0105, not superseded standalone
partial rounding. ADR-0127 upfront default unchanged; monthly remains selectable.
Continue at Story 3.13 discussion; exact contracts/source tests/final sizing/readiness open.

Story 3.13 scope agreed — 2026-10-13: user approved
[monthly partial employment and rate changes](../../../_bmad-output/planning-artifacts/epics.md#story-313-calculate-monthly-entitlement-across-partial-employment-and-rate-changes),
including inclusive aligned proration, joining availability, next-instalment policy-rate
changes and cumulative fractions under ADR-0105. Clarified that scheduled instalment
amount comes from policy allowance, not remaining balance; no restoration of capped-out
earning. Recurring overrides keep their separate leave-period boundary. Actual change
writers retain review/history/request/notification obligations. Continue at Story 3.14;
exact contracts/source tests/final sizing/readiness remain open.

Request-impact accountability accepted — 2026-10-13:
[ADR-0128](./architecture/decisions/0128-accountable-request-impacts-of-administrative-changes.md)
records change-authorizer ownership, mandatory impact review, visible pending issues
and human coordination through existing scoped approval/adjustment/correction actions.
No temporary funding-permission transfer or referral workflow. Discretionary administrative
approved-request impacts resolve before commit; necessary factual corrections retain
deficit review, original approval evidence and visible attention. E5/E6 first consumers
integrate/prove real writer impacts, exact acknowledgement/finalization and attention
before activation; earlier fixture stories do not establish this. Requirements/spine/UX/
epics/handoff updated; generic scaffold/UI patterns follow first consumers, existing agent
instructions suffice. No code/data/readiness change.

Story 3.14 scope agreed — 2026-10-13: user approved
[carry-over calculation](../../../_bmad-output/planning-artifacts/epics.md#story-314-calculate-carry-over-at-a-leave-year-boundary)
with no/all/limited transfer, standard-day conversion evidence, carried provenance,
once-only/repeated transfer, no expiry extension and boundary ordering. Preserve
earliest-expiry consumption; annual allowance is not the carry-over limit. Known expiry/
rollover is included in original reservation projections, not a surprise shortfall.
Later changes follow ADR-0128 accountability through existing authorized workflows.
Same-expiry tie-breaking remains open (oldest source period suggested, not separately
accepted). Continue at Story 3.15 expiry discussion; contracts/source tests/sizing/readiness open.

Story 3.15 scope agreed — 2026-10-13: user approved
[entitlement expiry calculation](../../../_bmad-output/planning-artifacts/epics.md#story-315-calculate-entitlement-expiry-dates-and-effects),
with accepted month-end/leap examples, inclusive last usable dates, preserved earlier
expiry, no reservation-based validity extension and expiry-before-earning/cap ordering.
Bind actual portion/date/timezone and auditable effect representation without duplicate
derived/actual effects or write-on-read. Continue at Story 3.16 discussion; exact
contracts/source tests/final sizing/readiness remain open.

Story 3.16 scope agreed — 2026-10-14: user approved
[automatic availability-method transitions](../../../_bmad-output/planning-artifacts/epics.md#story-316-calculate-changes-between-entitlement-availability-methods).
Complete the current period under its existing method; apply the next method at each
employee's next calendar/anniversary boundary, retaining carry-over/expiry/cap/history
and actual request-impact safeguards. Leave-year-basis/manual-only/untracked transitions
remain separate decisions. Continue at Story 3.17 discussion; exact contracts/source tests/
final sizing/readiness remain open, with no code/tests or implementation authorization.

Story 3.17 scope agreed — 2026-10-14: user approved
[authoritative current balance](../../../_bmad-output/planning-artifacts/epics.md#story-317-calculate-an-authoritative-current-leave-balance)
with earning/event/cap/rollover/expiry assembly, separate remaining/reserved/available
and future-funded commitments. Manual-only earns nothing without explicit grants; zero
is valid. Authorized corrected inputs/new correcting events affect current results while
original events/approvals/snapshots remain intact. Bind consistent observations/result/
performance contracts; direct indexed calculation first. Continue at Story 3.18 discussion;
source/test mapping, final sizing and readiness remain open, no code/tests executed.

Story 3.18 scope agreed — 2026-10-14: user approved
[date-by-date funding projection](../../../_bmad-output/planning-artifacts/epics.md#story-318-project-funding-for-every-requested-leave-date),
including candidate consumption carried forward, date-valid earning/expiry, protected
existing reservations, exact shortfalls and no preview mutations/cross-type borrowing.
[ADR-0129](./architecture/decisions/0129-oldest-source-period-for-equal-expiry-allocation.md)
records agreed oldest original source period for equal expiry, with stable final identity
tie-break; exact representation/reconstruction stays open. Requirements/spine/UX/test
traceability updated; existing generic UI/scaffold/agent patterns suffice. Continue at
Story 3.19 discussion; contracts/source tests/final sizing/readiness remain open.

Story 3.19 scope agreed — 2026-10-14: user approved
[Apply request preview](../../../_bmad-output/planning-artifacts/epics.md#story-319-show-a-clear-leave-request-preview-in-apply),
using backend duration/funding with clear paid/requested-unpaid/remaining and current/
selected-date distinctions, expandable source explanations and precise conversion.
Ignore superseded context/input replies; missing/failed calculation is not zero/valid
funding and does not block draft preservation. Binding acknowledgement/submission/
reservations retain E5 ownership. Continue at Story 3.20 discussion; exact contracts/
source tests/final sizing/readiness remain open, no code/tests executed.

Story 3.20 scope agreed — 2026-10-14: user approved
[Apply restrictions/required-input guidance](../../../_bmad-output/planning-artifacts/epics.md#story-320-explain-request-restrictions-and-required-information-in-apply)
including explained twelve-month advance booking, inclusive full-range cutoff, notice/
backdating reasons, employment end dates, active-state aggregate duration and conditional
document guidance. Provisional checks do not block draft preservation; E4/E5 actual
attachment/submission/concurrency checks retain their own proof. Twenty E3 scopes agreed;
continue exceptional funding proposal and remaining notification/mutation/view/lifecycle
decomposition at Story 3.21. Final contracts/source tests/dependencies/sizing/readiness open.

Story 3.21 scope agreed — 2026-10-14: user approved
[exceptional funding proposal calculation](../../../_bmad-output/planning-artifacts/epics.md#story-321-calculate-an-exceptional-funding-proposal),
including default unpaid, separately authorized funding lines/grants, date-valid source
capacity and exact reconciliation/reason/paid-unpaid results. No actual grants/transfers/
reservation/approval or recurring allowance change; E5 owns binding decisions and
acknowledgement. Continue group 5 notification foundations at Story 3.22; source/authority/
grant-validity/result contracts, final tests/sizing/readiness remain open.

Story 3.22 scope agreed — 2026-10-14: user approved
[durable shared notification acceptance](../../../_bmad-output/planning-artifacts/epics.md#story-322-durably-accept-notification-events)
with scope/version/privacy validation, durable receipts, immutable matching-event retries
and ninety-day origin expiry/dedup retention. Changed retry content is explicitly rejected,
not replaced/deleted/redelivered; trusted-producer defects surface to operations. Unexpected
failures protect data/recoverable work and produce actionable logs/alerts, never false
acceptance or hidden skipped work. No blanket process crash or rollback of an already
committed business action for notification failure. Bind receiver/authority/envelope/
error/alert contracts before readiness. Continue at Story 3.23 outbox discussion;
source/test mapping, final sizing/readiness remain open, no notifications/code/tests.

Story 3.23 scope agreed — 2026-10-14: user approved
[atomic Leave notification intent](../../../_bmad-output/planning-artifacts/epics.md#story-323-save-notification-intent-atomically-with-leave-changes),
including operation/event identity distinction, immutable envelope/origin, rollback on
intent-recording failure and pending intent after remote outage. Use Story 3.22's shared
HTTP API plus an internal transactional helper/scaffold pattern; no arbitrary standalone
Leave notification-writing endpoint or cross-owner queue. Promote proven generic helper
with first consumers and tests. Continue at Story 3.24 worker handover; exact contracts/
source tests/final sizing/readiness remain open, no code/tests/notifications performed.

Story 3.28 scope agreed — 2026-10-14: user approved
[initial employee policy assignment confirmation](../../../_bmad-output/planning-artifacts/epics.md#story-328-review-and-confirm-initial-employee-policy-assignments)
after calculation/notification foundations, fulfilling the initial group 2 write obligation.
Exact selected set/effective policy/initial consequences, current authority/review and
atomic attribution/change/calculation evidence/outbound intent remain required. Bind
date/version/initial earning/batch/accountless notification contracts before readiness;
reassignment/ending used assignments remain separate. E5 actual request impacts integrate
before activation against real requests. Continue Story 3.29 one-off adjustment; all
contracts/source tests/final sizing/readiness open, no code/tests/notifications performed.

Story 3.29 scope agreed by continuation — 2026-10-15:
[one-off balance adjustment](../../../_bmad-output/planning-artifacts/epics.md#story-329-review-and-confirm-a-one-off-leave-balance-adjustment)
uses Add/Deduct, mandatory reason/effective date, backend impact review, protected current
confirmation and atomic event/calculation evidence/audit/intent. Minimal email/in-app
notices link to its authorized detail view; correction is another explained adjustment,
not history editing or an automatic undo. Bind validity/conversion/coordination/accountless
notification contracts, actual integration and E5 request-impact activation guards.
Continue Story 3.30 recurring entitlement; all source/test/sizing/readiness gates open.

Story 3.30 scope agreed — 2026-10-15:
[recurring entitlement or return to policy](../../../_bmad-output/planning-artifacts/epics.md#story-330-change-recurring-employee-entitlement-or-return-to-policy)
uses the focused policy/custom editor, mandatory reason and consequential review, with
leave-period-boundary effect defaulting to the next boundary. Overrides continue until
explicitly changed; no automatic end date or balance reset. Confirm versioned change,
required calculation evidence/audit/notification intent atomically and retain historical
evidence. Story 3.29 remains the separate one-off adjustment. Exact allowance/version/
overlap/return-policy/accountless notification contracts, tests, final sizing and readiness
remain open. The user requested preservation of the
[preliminary post-MVP interface discussion](./planning-handoff-e3.md#preliminary-post-mvp-discussion--natural-language-dynamic-ui-and-headless-access)
for later exploration: natural language, constrained dynamic UI and headless access.
No requirements/ADR/vendor decision or MVP scope change was approved. Resume collaborative
planning with proposed Story 3.31 balance details/history; implementation gates remain binding.

Story 3.31 scope agreed — 2026-10-15:
[own balance details/history](../../../_bmad-output/planning-artifacts/epics.md#story-331-understand-my-leave-balance-and-history)
shows remaining/reserved/available separately, authorized request links, expandable
history and backend conversion explanations. History-year filtering leaves current
balance unchanged; future earnings are excluded from today's available amount and
failed reads are never zero. Bind history/read/privacy/date contracts and actual E5
consumer integration before activation. Continue Story 3.32 employee-summary entitlement
integration; exact tests, final sizing and readiness gates remain open. No code performed.

Story 3.32 scope agreed — 2026-10-15:
[employee entitlement summary](../../../_bmad-output/planning-artifacts/epics.md#story-332-view-an-employees-leave-entitlement-settings)
completes Story 2.26's E3 section using actual policy/assignment/override data, current
versus scheduled settings, separately authorized balance/history and existing edit/
adjustment flows with refreshed return. Bind manager read/detail permissions explicitly;
own-balance access does not grant employee administration. Continue Story 3.33 policy/
entitlement setup assessment. Contracts, test mapping, sizing and readiness remain open;
no implementation performed or authorized.

Story 3.33 scope agreed — 2026-10-15:
[policy and entitlement setup assessment](../../../_bmad-output/planning-artifacts/epics.md#story-333-see-policy-and-entitlement-setup-issues)
fulfils Story 2.25's E3 obligation using actual saved policy/approval-rule/assignment
inputs. Derive section status, link permitted issues and refresh after corrections;
unavailable checks are not missing data or Ready. Zero/manual-only balances do not imply
missing opening data. Consequential checks and lightweight draft preservation remain
independent. Continue group 9 with proposed Story 3.34 used-policy version changes.
Exact predicates/contracts/test mapping, final sizing and readiness remain open; no code.

Story 3.34 scope agreed — 2026-10-15:
[used-policy version changes](../../../_bmad-output/planning-artifacts/epics.md#story-334-review-and-publish-a-change-to-a-policy-already-in-use)
reuse the editor with authoritative before/after/employee/request review, method-specific
effective/usable dates, override-aware effects and protected publication. Version,
required calculation evidence/audit/notification intent commit atomically; preserve
historical requests and enforce ADR-0128. Future publication stays visibly Scheduled;
actually affected employees receive privacy-appropriate notices. Continue proposed
Story 3.35 amendment/cancellation of scheduled policy changes. Exact contracts/tests,
final sizing and readiness remain open; no implementation authorized or performed.

Story 3.35 scope agreed — 2026-10-15:
[amend/cancel scheduled policy change](../../../_bmad-output/planning-artifacts/epics.md#story-335-amend-or-cancel-a-scheduled-policy-change)
reviews prior/proposed or cancellation-resulting settings, dates and employee/request
effects. Guard still-future state and current authority/review, commit evidence/audit/
updated-notice intent atomically, retain original history and notices. Bind differing
employee boundaries/partially effective changes explicitly; effective changes use the
appropriate new-version/correction flow. Continue proposed Story 3.36 reassignment/ending
of existing employee policy assignments before retirement. Exact contracts/tests/sizing/
readiness remain open; no code or implementation permission.

Story 3.36 scope agreed — 2026-10-15:
[change/end employee policy assignment](../../../_bmad-output/planning-artifacts/epics.md#story-336-change-or-end-an-employees-policy-assignment)
extends initial assignment with explicit date/reason and authoritative coverage/override/
entitlement/request review. Guard conflicts/current authority and commit history/evidence/
audit/intent atomically; preserve original evidence and no access side effects. Exact
ending/replacement dates, retained entitlement, override and funding semantics remain
binding unresolved contracts, not an assumed transfer/reset/recalculation. Continue
proposed Story 3.37 leave-type retirement. All tests/sizing/readiness gates remain open;
no code or implementation permission.

Story 3.37 scope agreed — 2026-10-15: leave-type deactivation uses Active/Inactive,
retained identity/version/history and accepted ADR-0132's current/scheduled assignment
guard. Features/spine/written UX/ADR index aligned. Resolve assignments separately;
explicit outstanding entitlement/request treatment remains a pre-story contract.
Continue proposed Story 3.38 restoration of an inactive type. Exact tests/sizing/readiness
remain open; no code, migrations or implementation permission.

Story 3.38 scope agreed — 2026-10-15:
[restore inactive leave type](../../../_bmad-output/planning-artifacts/epics.md#story-338-restore-an-inactive-leave-type)
reuses the retained identity/code/settings/history, checks compatibility/current authority
and records restoration/audit atomically. It reinstates no assignments, grants, cancelled
requests or cleared draft selections. Active status does not waive setup or request
validation. Continue proposed Story 3.39 existing type metadata/permitted-unit changes.
Exact contracts/tests, final sizing and readiness remain open; no implementation.

Story 3.39 scope agreed — 2026-10-15:
[existing leave-type details/permitted units](../../../_bmad-output/planning-artifacts/epics.md#story-339-change-an-existing-leave-types-details-and-permitted-units)
uses explicit whole-form saving and immutable metadata versions with guarded published
choice-pointer/revision updates. Preserve stable identity/code and request evidence;
drafts clear only definitively unavailable selections with notice and useful input kept.
Date-aware policy checks remain separate. Thirty-nine E3 scopes agreed; final coverage,
unresolved business/effect contracts, test mapping and agent sizing must be checked before
claiming epic completeness or proceeding through readiness. No code or implementation
permission; first draft slice unchanged.

E3 coverage reconciliation started — 2026-10-15:
[group ownership and open business decisions](./planning-handoff-e3.md#e3-coverage-reconciliation--started-2026-10-15)
map the nine delivery groups to agreed candidate Stories 3.1–3.39. Atomic BIZ/CALC/FLOW/
NFR/UX/test coverage, exact contracts and single-agent sizing are not yet validated.
Used-policy basis restriction now accepted under
[ADR-0133](./architecture/decisions/0133-used-policy-leave-year-basis-fixed-for-mvp.md):
fixed once used for MVP; independent new-type creation does not migrate existing
entitlement. No replacement-assignment/manual-adjustment bypass. Preserve supported
method changes and necessary authorized factual correction. Features/spine/written UX/
ADR index/story obligations aligned. Automatic/manual-only source restriction now accepted
under [ADR-0134](./architecture/decisions/0134-used-policy-entitlement-source-fixed-for-mvp.md):
fixed once used, retaining supported automatic-method changes and authorized adjustments.
Source/UX/story obligations updated. Explicit No balance tracking now accepted under
[ADR-0135](./architecture/decisions/0135-no-balance-tracking-for-mvp.md): retain ordinary
request gates and duration/usage history, show Not balance-limited, independent paid/unpaid
classification, no fictional balance funding effects and no used tracked/untracked migration.
Requirements/spine/written UX/ADR index/epic consumer obligations aligned. Next detail
bounded remaining configuration/read/UI scopes collaboratively; 39 story scopes remain
approved, not a claim that new untracked coverage is complete. Other effect gaps stay open.
No workflow completion, readiness PASS or implementation permission.

Story 3.40 scope agreed — 2026-10-15:
[configure no-balance policy](../../../_bmad-output/planning-artifacts/epics.md#story-340-configure-a-policy-with-no-balance-tracking)
extends initial editor/publication and policy summaries with explicit untracked category,
conditional field validation and independent paid/unpaid/request/approval settings. Retain
guarded version publication; no used-policy tracked/untracked conversion. Forty E3 scopes
agreed. Continue proposed Story 3.41 typed untracked balance/preview backend semantics,
then employee presentation; exact contracts/tests/sizing/readiness remain open. No code.

Story 3.41 scope agreed — 2026-10-15:
[untracked balance/preview backend](../../../_bmad-output/planning-artifacts/epics.md#story-341-calculate-request-previews-without-an-entitlement-balance)
returns explicit not-applicable balance, actual schedule-based duration, ordinary request
guidance and independent paid/unpaid classification, with no fictional funding effects.
Distinguish untracked from zero/missing/unavailable/denied; tracked policies retain normal
funding. Forty-one E3 scopes agreed. Continue proposed Story 3.42 employee/manager/Apply
presentation; E5 actual usage/lifecycle integration and all contracts/tests/sizing/readiness
remain open. No application implementation authorized or performed.

Story 3.42 scope agreed — 2026-10-15:
[untracked employee/manager/Apply presentation](../../../_bmad-output/planning-artifacts/epics.md#story-342-show-untracked-leave-clearly-to-employees-and-managers)
uses Not balance-limited, real duration/classification/guidance and authorized usage history;
omit false funding/shortfall/allowance actions. Keep ordinary request gates and distinguish
errors/missing states. Forty-two E3 scopes agreed; final sizing may split surface work.
Return to unresolved replacement/ending assignment effects before declaring coverage or
readiness. Exact contracts/tests and E5 actual usage integration remain required; no code.

Assignment replacement boundary agreed — 2026-10-15 under
[ADR-0136](./architecture/decisions/0136-same-type-policy-replacement-and-earned-entitlement.md):
same type only, retain earned entitlement/expiry/carry-over and permitted future earning
without duplicate annual grants or reset. Separate type assignments transfer no balance;
category/basis restrictions stay binding. Features/spine/UX/epic obligations/index aligned.
Existing override persistence remains settled; next discuss ending-assignment effects.
Forty-two scopes agreed; exact contracts/tests/sizing/readiness remain open, no code.

Assignment ending agreed — 2026-10-15 under
[ADR-0137](./architecture/decisions/0137-ending-policy-assignment-preserves-earned-entitlement.md):
stop future automatic earning/new out-of-coverage requests, retain earned entitlement/
expiry/history and review existing requests. No upfront clawback or employment departure
implied. Requirements/spine/written UX/Story 3.36 obligations/index aligned. Next discuss
retirement resolution, now accepted under
[ADR-0138](./architecture/decisions/0138-simple-leave-type-deactivation-and-employee-explanations.md):
retain guards, normal reviewed resolution and clear employee-facing reasons in standard
notices/details. Historical-only records do not block; no automatic zeroing or additional
closure/combined retirement/message workflow. Sources/UX/epic obligations/index aligned.
Exact contracts/tests/sizing/readiness remain open.

Scheduled cutoff accepted — 2026-10-15 under
[ADR-0139](./architecture/decisions/0139-scheduled-policy-amendment-cutoff.md):
amend/cancel only before any affected employee effect starts; thereafter use a new
prospective policy version with original entitlement/evidence preserved and actual
employee/date impacts reviewed/notified. Sources/spine/UX/index/Stories 3.34–3.35 aligned.
Protected in-use definition accepted under
[ADR-0140](./architecture/decisions/0140-policy-in-use-from-confirmed-assignment.md):
confirmed current/future employee assignment makes use persistent; unused publication/
draft selection alone does not. Ending/zero balance cannot unlock; immutable versioning
retained. Source/spine/UX/epic obligations/index aligned. Next discuss assignment resumption
without gap earning or duplicate grants. Forty-two scopes agreed; all readiness gates open.

Assignment-gap principles accepted — 2026-10-15 under
[ADR-0141](./architecture/decisions/0141-assignment-gaps-and-resumption-without-duplicate-grants.md):
no gap earning/duplicate upfront grant, preserve prior portions/expiry, authorized adjustment
for extra intended entitlement and reviewed correction for mistaken gaps. Features/spine/
UX/index/epic obligations aligned. Next discuss monthly instalment treatment of partial
assignment coverage; exact formula/timing not approved by these principles. Forty-two
scopes agreed; exact tests/sizing/readiness remain open, no code.

Monthly assignment coverage agreed — 2026-10-15 under
[ADR-0142](./architecture/decisions/0142-monthly-instalments-for-partial-assignment-coverage.md):
reuse partial-period policy choice over employment/assignment intersection; eligible-day
proration or one full nominal instalment, none with zero coverage and no duplicates on
resumption. Requirements/spine/UX/index/epic obligations aligned. Exact availability/
cutoff/correction cases remain contracts. Next discuss first upfront entitlement for
midyear initial policy assignment; not approved by the no-duplicate resumption principle.
Forty-two scopes agreed; no runtime tests/code or implementation/readiness permission.

Initial upfront coverage agreed — 2026-10-15 under
[ADR-0143](./architecture/decisions/0143-initial-upfront-grant-from-policy-coverage-start.md):
existing proration choice uses later employment/assignment start for initial coverage,
eligible remaining-year proportion or full allowance once, no repeated resumption grant.
Sources/spine/UX/index/epic obligations aligned; exact initial-provenance/concurrency/
known-employment-end/cap examples remain gates. Next discuss monthly end-availability
when coverage ends before the instalment's scheduled availability date; not yet agreed.

Monthly scheduled availability accepted — 2026-10-15 under
[ADR-0144](./architecture/decisions/0144-monthly-availability-after-assignment-coverage-ends.md):
covered portion retains original availability even after assignment ending; no early
release, forfeiture solely from ending or uncovered earning. Sources/spine/UX/index/epic
obligations aligned. Next discuss start-available monthly instalment already released
before a new mid-period assignment end: proposed use of existing adjusted/full-period
choice and reviewed consequences, not yet accepted. Forty-two scopes; readiness open.

Already-available monthly reconciliation accepted — 2026-10-15 under
[ADR-0145](./architecture/decisions/0145-reconcile-start-available-monthly-coverage-changes.md):
assignment review applies existing adjusted/full choice, showing actual balance/request
effects with original evidence/safeguards retained. No separate manual deduction or annual-
upfront clawback. Sources/spine/UX/index/epic obligations aligned. Return to E3 atomic
coverage/dependency/sizing reconciliation; 42 scopes agreed, no code or readiness PASS.

E3 calculation/dependency check — 2026-10-15:
[ownership and sizing findings](./planning-handoff-e3.md#e3-calculation-and-integration-ownership-check--2026-10-15)
map CALC-01–36 and applicable BIZ/FLOW boundaries to candidate scopes/real later consumers.
No extra top-level group found in this pass; exact atomic field/test/NFR coverage remains
open. Broad scopes need single-agent decomposition assessment, starting with 3.3's complete
initial-policy API/publication then its actual four-section web editor. Split now approved
as **3.3-A** then **3.3-B**, retaining 3.3 as the agreed traceability parent. Detail each
child collaboratively, starting with 3.3-A; unpresented criteria/final sizing are not
approved. Both precede 3.4. No scope renumbering or implementation/readiness permission.

Story 3.3-A child scope agreed — 2026-10-15:
[initial policy API/review/publication](../../../_bmad-output/planning-artifacts/epics.md#story-33-a-review-and-publish-an-initial-policy-through-the-api)
validates complete automatic/manual-only/untracked configuration, returns stable errors
and effect-free review, atomically publishes immutable policy/evidence with current
authority and protected retries, and reads truthful current/scheduled state. No employee
assignment/access grant. Deliver after 3.2, then 3.3-B, then 3.4; appendix placement does
not change order. Exact field/test contracts and sizing/readiness remain open. Continue
proposed 3.3-B web editor. Forty-two parent scopes retained; no final delivery count/code.

Story 3.3-B child scope agreed — 2026-10-15:
[initial policy web editor](../../../_bmad-output/planning-artifacts/epics.md#story-33-b-configure-and-publish-an-initial-policy-in-the-web-editor)
retains approved four-section/conditional form, field errors/input recovery, API-backed
review/back/publication and confirmed current/scheduled results. Prove actual API/database
browser journeys and accessible mobile/keyboard/exit/recovery behavior. Deliver 3.3-A then
3.3-B before 3.4; no parent acceptance removed. Allocate overlap with 3.40 once at final
decomposition. Split now approved: 3.25-A shared channel processing/in-app delivery then
3.25-B email delivery/provider recovery, retaining parent acceptance. Detail 3.25-A next,
then 3.25-B; unpresented child criteria and final sizing/readiness remain open. Both precede
notice-producing Leave mutations; inbox APIs/UI remain later. No code or implementation.

Story 3.25-A child scope agreed — 2026-10-15:
[shared channel processing/in-app delivery](../../../_bmad-output/planning-artifacts/epics.md#story-325-a-process-channel-deliveries-and-create-in-app-notifications)
uses restricted notification-service/per-item scope, durable deduplicated recipient records,
independent channel outcomes, privacy-safe English/org/date templates, recoverable work
and production-support diagnostics/expiry. Email stays pending until actually processed;
no future inbox UI required for this child's persistence proof. Next detail 3.25-B email
provider delivery/recovery. Exact contracts/tests/retention/sizing/readiness remain open.

Story 3.25-B child scope agreed — 2026-10-16:
[email delivery/provider recovery](../../../_bmad-output/planning-artifacts/epics.md#story-325-b-deliver-notification-emails-and-recover-uncertain-provider-outcomes)
uses actual provider evidence for accepted/failed/uncertain outcomes and safe recovery,
minimal English/org-bound content, independent in-app completion, original retry expiry
and production-support ownership without replaying the Leave change. Both 3.25 children
now have agreed scopes; exact provider contracts/tests/final sizing remain gates.
Story 3.34 split approved — 2026-10-16: **3.34-A** authoritative used-policy impact/
review/publication API, then **3.34-B** existing editor/review UI integration. Retain parent
acceptance, atomic version/evidence/audit/intent, historical/request safeguards and actual-
effect notices. Both precede 3.35. Next detail 3.34-A collaboratively; child criteria,
exact contracts/tests/final sizing and readiness remain open. No code or implementation.

Story 3.34-A child scope agreed — 2026-10-16:
[used-policy impact/review/publication API](../../../_bmad-output/planning-artifacts/epics.md#story-334-a-review-and-publish-a-used-policy-change-through-the-api)
enforces supported/in-use restrictions, effect-free actual impact/date/override review,
request safeguards and protected atomic version/evidence/audit/notice intent. Preserve
prior grants/versions/request evidence; actual E5/E6 integrations remain activation gates.
Continue proposed 3.34-B web editor/review on the completed API. Exact contracts/tests,
single-agent sizing and readiness remain open; no code/notifications/implementation.

Story 3.34-B child scope agreed — 2026-10-16:
[used-policy web editor/review](../../../_bmad-output/planning-artifacts/epics.md#story-334-b-review-and-publish-a-used-policy-change-in-the-web-editor)
integrates complete 3.34-A API review/publication, showing restrictions, old/new/unchanged
settings, overrides, employee dates and authorized request-resolution links/return.
Preserve API blocking, confirmed current/scheduled outcomes and accessible recovery/exit.
Both 3.34 children precede 3.35; exact contracts/tests/final sizing remain open. Next
split now approved — 2026-10-16: 3.36-A assignment-change/ending API review/confirmation,
then 3.36-B focused UI. Detail 3.36-A next; original parent guards/evidence/notice intent
remain binding, both children precede 3.37. Unpresented child criteria, exact contracts/
tests/final sizing/readiness remain open. No code or implementation permission.

Story 3.36-A child scope agreed — 2026-10-16:
[assignment-change/ending API](../../../_bmad-output/planning-artifacts/epics.md#story-336-a-review-and-confirm-assignment-changes-through-the-api)
enforces current authority, coverage/replacement compatibility, authoritative effect-free
review and protected atomic history/calculation evidence/audit/notice intent. Preserve
settled gap/partial-period/provenance/no-duplicate/override/request rules and separate
remedy authority; actual E5/E6 integration remains required before activation. Continue
proposed 3.36-B focused UI, then 3.37; exact contracts/tests/sizing/readiness remain open.

Story 3.36-B child scope agreed — 2026-10-16:
[focused assignment-change editor](../../../_bmad-output/planning-artifacts/epics.md#story-336-b-review-assignment-changes-in-the-focused-editor)
integrates completed 3.36-A review/confirmation with coverage/retained balance/expiry/
override/date/request explanations, authorized resolution links and refreshed settings
return. Preserve API blocking and accessible correction/recovery/exit behavior. Both
3.36 children precede 3.37. Story 3.42 split approved — 2026-10-16: 3.42-A employee
My Leave/Apply/usage presentation, then 3.42-B manager employee-summary/actions. Preserve
parent acceptance and completed 3.41 backend dependency. Next detail 3.42-A; unpresented
child criteria, all exact contracts/tests/final sizing/readiness remain open. No code
or implementation permission.

Story 3.42-A child scope agreed by clarified continuation — 2026-10-16:
[employee untracked presentation](../../../_bmad-output/planning-artifacts/epics.md#story-342-a-understand-untracked-leave-in-my-leave-and-apply)
uses confirmed Not balance-limited, actual duration/classification/guidance and authorized
usage history, without fictional funding/shortfall controls. Clarified failure wording:
show loading/missing/failure/denied states and Retry where applicable; untracked label
requires an authorized successful read. Preserve context isolation/accessibility and
independent draft saving. Continue proposed 3.42-B manager presentation; exact contracts/
tests, E5 actual usage integration and final sizing/readiness remain open. No code.

Story 3.42-B child scope agreed — 2026-10-16:
[manager untracked presentation](../../../_bmad-output/planning-artifacts/epics.md#story-342-b-explain-untracked-leave-in-employee-administration)
uses confirmed policy/coverage/classification and separately authorized usage details,
omitting balance/allowance actions while retaining permitted policy/assignment controls.
Verify refresh/return, failures versus confirmed untracked, context isolation and actual
API/accessibility integration. All five approved split parents now have agreed child
criteria; exact contracts/atomic coverage/final sizing remain open. Next proposed split:
3.17 split now approved — 2026-10-16: 3.17-A calculation composition, then 3.17-B
authorized current-balance API/history integration and representative workload checks.
Both precede 3.18/3.19; UI stays later. Next detail 3.17-A; unpresented child criteria,
exact contracts/tests/final sizing remain gates. No implementation/readiness permission.

Story 3.17-A child scope agreed — 2026-10-16:
[current-balance calculation composition](../../../_bmad-output/planning-artifacts/epics.md#story-317-a-compose-a-reproducible-current-leave-balance)
combines prior earning/events/cap/carry-over/expiry using complete historical inputs,
distinct earned/reserved/available/future commitments and exact provenance/precision.
Preserve correction evidence, legitimate manual-only zero, reproducible effect-free
reads and explicit invalid-input failure. Continue proposed 3.17-B authorized API/input/
workload integration; exact contracts/tests/sizing/readiness remain open. No code.

Story 3.17-B child scope agreed — 2026-10-16:
[authorized current-balance API/history](../../../_bmad-output/planning-artifacts/epics.md#story-317-b-read-an-authorized-current-balance-from-authoritative-history)
resolves complete scoped owner/version/history inputs and calls completed 3.17-A,
returning typed authoritative results/failures with no read effects. Prove current own/
manager authority, correction evidence and real multi-year workload/concurrency targets.
Both children precede 3.18/3.19. Story 3.35 split now approved — 2026-10-16: 3.35-A
scheduled amendment/cancellation API, then 3.35-B web review UI. Detail these two next;
unpresented child criteria remain unapproved. Seven of 42 parent scopes are split, not
all stories. No additional split currently proposed; then consolidate order/overlap/
coverage and remaining contracts/sizing gates. Forty-nine provisional candidates before
overlap consolidation is not a final validated delivery count. No implementation authority.

Story 3.35-A child scope agreed — 2026-10-16:
[scheduled amendment/cancellation API](../../../_bmad-output/planning-artifacts/epics.md#story-335-a-amend-or-cancel-a-scheduled-policy-change-through-the-api)
enforces current authority/first-effect cutoff, accurate resulting policy/employee/request
review and atomic history/evidence/audit/updated intent with retained original versions/
notices. Prove boundary races, request safeguards and duplicate-safe recovery. Continue
3.35-B web child, the final child remaining from seven approved splits; then consolidate
order/overlap/coverage and remaining exact contracts/sizing. No code or readiness PASS.

Story 3.35-B child scope agreed — 2026-10-16:
[scheduled amendment/cancellation web UI](../../../_bmad-output/planning-artifacts/epics.md#story-335-b-review-scheduled-policy-amendments-and-cancellations-in-the-web-ui)
shows authoritative previous/proposed/resulting schedule and employee/request impacts,
permitted resolution/return and protected confirmation/recovery. Preserve first-effect
cutoff/new-version route, original history and accessible discard/mobile/keyboard behavior.
All fourteen children of seven approved splits are agreed. Consolidate order/overlap/
coverage next; no new split proposed, no code/readiness/implementation authorization.

E3 scope/decomposition consolidation prepared — 2026-10-16:
[consolidated order and acceptance allocation](../../../_bmad-output/planning-artifacts/epics.md#consolidated-e3-candidate-delivery-order--2026-10-16)
retain 42 agreed parent scopes and all fourteen agreed split children as 56 traceable
records. Candidate delivery count is 48: seven parents deliver through their children,
and 3.40's already-covered initial policy configuration/summary/used-category guards are
allocated once to 3.3-A/B, 3.2 and 3.34-A/B. Move 3.41 before assignment mutations so
untracked backend behavior is a completed prerequisite. Physical story order reconciled;
no new split proposed or acceptance removed. User approved this consolidated scope/order
checkpoint on 2026-10-16 and agreed to continue E4 planning. Exact atomic field/UX/privacy/test coverage, schemas,
coordination/provider/retention contracts, measurable NFRs and final single-agent sizing
remain gates; actual E5/E6 integration precedes activation. This is no readiness PASS,
workflow completion or implementation authorization. Original E1 first slice unchanged.

E4 handoff refreshed — 2026-10-16: resume with bmad-create-epics-and-stories using
[the current checkpoint, E4 entry and copyable prompt](./planning-handoff-e3.md#resume-point).
Start by proposing/confirming E4's delivery sequence, then detail one story at a time;
no E4 sequence or individual scope is approved yet. Same current working tree, including
uncommitted planning and unrelated platform/KDG work, remains authoritative. No new
worktree, commit, implementation, migration or deployment requested/performed. Preserve
Content/provider/byte/association/privacy contracts and all existing readiness gates.

E4 delivery sequence approved — 2026-10-16: user accepted the
[seven delivery groups](../../../_bmad-output/planning-artifacts/epics.md#epic-4-attach-and-retrieve-supporting-documents-safely).
Continue collaboratively with Story 4.1 in Content migration/provider foundations.
No individual E4 scope or final story count approved. Reuse E1-CONTENT-READ/PTS-ADOPT
without duplicating owner work; association/cleanup, fixed-byte and provider-lifetime
contracts remain gates before affected story readiness, with runtime evidence produced
during authorized delivery. Preserve E3's approved 48-candidate order and the original
E1 draft slice. Source/test coverage, final sizing, release and BMAD readiness stay open;
no code, migrations, provider changes, notifications, commits or deployments performed.

Story 4.1 scope agreed — 2026-10-16:
[authorized Content upload sessions](../../../_bmad-output/planning-artifacts/epics.md#story-41-start-or-resume-an-authorized-content-upload)
cover restricted service/scope, declarations/limits, duplicate-safe operation recovery,
reauthorized renewal and provider-enforced expiry, without claiming verification or
association. PtS limits may be deliberately revised based on actual source/retrieval
needs; no numeric replacement or existing-file deletion/truncation selected. Reconcile
actual existing Content/E1 work and retain owner contracts/consumer compatibility.
Continue Story 4.2 verification/finalization discussion. Source/test coverage, exact
contracts, final sizing and readiness remain open; no code/tests/provider changes or
implementation authorization.

E4 Story 4.2 scope approved — 2026-10-16: see
[verification/finalization](../../../_bmad-output/planning-artifacts/epics.md#story-42-verify-and-finalize-uploaded-content).
Actual byte/type/size/digest verification, fixed identity, outstanding-upload/race safety,
duplicate/uncertain recovery and bounded provider work precede attachment readiness.
Malware scanning remains deferred; the user's subsequent cost/resource question opens
discussion only. Exact contracts, final coverage/sizing and readiness remain pending;
no code, runtime tests, provider changes or implementation permission.

E4 Story 4.3 scope approved — 2026-10-16: see
[configured provider consistency/parity](../../../_bmad-output/planning-artifacts/epics.md#story-43-use-the-organizations-configured-storage-provider-consistently).
Reuse existing shared Content work; trusted provider resolution, Azure/Supabase expiry/
fixed-byte/recovery/private-read parity and stable original locators after default changes
remain binding. No existing-file provider migration or prototype retirement in this item.
Continue Story 4.4 recoverable draft association discussion in group 2. Exact contracts,
source/test coverage, final sizing and readiness remain open; no implementation permission.

E4 Story 4.4 scope approved — 2026-10-16: see
[recoverable draft association](../../../_bmad-output/planning-artifacts/epics.md#story-44-reliably-attach-a-verified-file-to-my-saved-draft).
User requires bounded pending protection: deadlines/recovery reconcile stalled operations,
release genuine abandonment and prevent indefinite retry renewal; unresolved uncertainty
has monitored, restricted audited recovery. Expiry alone cannot delete possibly saved
content; confirmed draft references retain protection and late confirmation cannot revive
released operations. Bind exact protocol/time/retry/alert bounds before readiness; prove
cleanup/confirmation/crash/expiry races during authorized delivery. Continue Story 4.5
draft upload controls in group 3. Final coverage/sizing/readiness open; no code authorized.

E4 Story 4.5 scope approved — 2026-10-16: see
[draft upload controls](../../../_bmad-output/planning-artifacts/epics.md#story-45-upload-supporting-documents-in-my-leave-draft).
Truthful per-file upload/verification/association states, accessible Cancel/Retry/Remove,
preserved input, authorized reopen recovery and existing close/switch/revision safeguards
consume Stories 4.1–4.4. Promote proven neutral UI/scaffold patterns with their tests/docs.
Mobile camera/document scanning and external-app handoff are under discussion only;
no extra capture control, native app or scanner selected. Contracts/coverage/final sizing/
readiness stay open; no implementation permission.

Story 4.5 mobile amendment approved — 2026-10-16: add Take photo beside Choose a file
where supported, image review/retake, camera cancellation/failure/return draft continuity
and existing format/size/count/server verification. Update neutral UI/scaffold patterns
with proven first-consumer behavior. Bind image-format/conversion/compression and actual
Android/iOS browser/installed-PWA evidence before readiness; no OCR, full document scanner,
native app or Expense migration approved. Features and written Leave UX synchronized.

Story 3.24 scope agreed — 2026-10-14: user approved
[recoverable Leave handover worker](../../../_bmad-output/planning-artifacts/epics.md#story-324-hand-over-leave-notifications-through-a-recoverable-worker),
with narrow restricted discovery, per-item verified organization scope, bounded fenced
claims, unchanged-event crash recovery, visible failure classification and truthful
shutdown/recovery evidence. Reuse worker/scaffold implementation with Leave-owned
credentials; shared delivery workers use their own notification records/authority.
Retain accepted PostgreSQL worker/Temporal deferral. Expiry stops new attempts, not
accepted remote delivery. Continue Story 3.25 shared channel delivery; exact contracts/
runbook/source tests/final sizing/readiness remain open, no code/notifications performed.

Story 3.25 rendering scope narrowed — accepted 2026-10-14:
[ADR-0130](./architecture/decisions/0130-standard-english-notification-templates-for-mvp.md)
records standard shared English templates with clear dates/relevant organization identity.
Custom branding/editable templates/Portuguese delivery deferred; localization readiness,
existing preferences and English fallback retained. Retry/failure recovery remains technical
operations under platform ADR-0024, not a business-admin queue review. Full Story 3.25
approval/failure clarification and exact contracts/tests/sizing/readiness remain pending.

Story 3.25 scope agreed — 2026-10-14: user approved
[shared email/in-app delivery](../../../_bmad-output/planning-artifacts/epics.md#story-325-deliver-accepted-notifications-through-email-and-in-app-channels),
with independent channel states, explicit uncertain provider acceptance, minimal standard
English/org-bound templates under ADR-0130, dated events and original retry expiry.
Bounded retries are automatic; contract/provider defects and exhaustion go to production
support for controlled audited recovery, not business-admin technical queue review.
Actual provider duplicate/status evidence and inbox retention contracts remain pre-story
inputs. Continue at Story 3.26 inbox/read APIs; all contracts/tests/sizing/readiness open,
no code/provider changes/notifications performed.

Story 3.26 scope agreed — 2026-10-14: user approved
[scoped inbox/count/read-state APIs](../../../_bmad-output/planning-artifacts/epics.md#story-326-read-a-scoped-notification-inbox-and-manage-read-state),
with selected-org details/bell, count-only permitted selector badges, recipient/org-scoped
read/bulk-read and no business acknowledgement effects. New
[ADR-0131](./architecture/decisions/0131-other-organization-unread-indicator.md) records the
approved discreet dot for another accessible organization's unread notifications and
hidden selector with a single accessible organization. Shared/Leave written UX updated;
actual panel/selector UI follows Story 3.27. Exact API/access/count/pagination/retention/
test contracts, final sizing and readiness remain open; no code/notifications performed.

Story 3.27 scope agreed — 2026-10-14: user approved
[notification panel/selector UI](../../../_bmad-output/planning-artifacts/epics.md#story-327-show-the-notification-panel-and-organization-unread-indicators),
with selected-org details/bell, permitted selector counts/other-org dot, hidden selector
for one accessible organization, scoped confirmed read updates and separate business
responses. Loading/empty/failure and context/revocation/focus/mobile checks remain explicit;
optional notifications do not gate the first draft slice. Continue deferred assignment
confirmation at Story 3.28 after calculation/notification foundations. Exact contracts/
source tests/final sizing/readiness remain open, no code/tests/notifications performed.

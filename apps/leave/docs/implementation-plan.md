# Leave Tracker Implementation Plan

**Version:** 0.1  
**Last updated:** 2026-09-23

**Status:** Phase 1 planning in progress — implementation readiness pending  
**Owners:** Platform and Leave application teams

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
- [ ] Consume shared employment with nullable department/location and manual supervisor assignments under platform ADR-0041; establish authorized shared administration, scoped references and effective-dated history without duplicating an employee master. Preserve separately scoped team requirements; no organization-chart editor or Graph import dependency
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
- [ ] Implement effective-dated employee work schedules including breaks and timezone; one explicit work profile with NGO fallback, team/location suggestions without silent reassignment, inherited values and overrides/reset, reason and impact review preserving history
- [ ] Implement versioned leave-type CRUD and archive/restore
- [ ] Design stable configuration identities, archive timestamps, effective-dated calculation versions and request snapshots (ADR-0086); preserve audit separately and enforce work-profile archive dependencies
- [ ] Implement policy versions: units, accrual, carry-over, expiry, limits, notice,
  eligibility, documentation, privacy, balance behavior, and workflow assignment
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
- [ ] Implement notification templates with tenant branding
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
| Coverage, sizing and gate evidence | Planning owners; all 20 candidates | Finish scoped source-to-story cross-check and global inventory; validate independently completable story size/order; assign concrete acceptance/contract test IDs and exact commands as delivery is prepared. Run the established readiness workflow only when its required planning inputs are complete. |

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
| Remaining story sizing and dependency proof | Inspect P1/ACCESS/PEOPLE against concrete implementation boundaries; retain independently executable tests and avoid hidden future-story dependencies. Final numbering follows this check. | Before finalizing affected stories |
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

# Leave Tracker Functional Specification

**Version:** 0.1  
**Last updated:** 2026-09-23

**Status:** Product scope approved; detailed acceptance criteria remain living documentation  
**Scope:** MVP unless marked otherwise

Implementation consistency rules and owned delivery prerequisites are consolidated
in the [architecture spine](./architecture/ARCHITECTURE-SPINE.md). This specification
remains the product source of truth.

Terminology: **organization** is the general tenant, including nonprofit and
for-profit organizations. Earlier NGO wording below denotes that tenant; new code,
contracts and generic UI use organization and established `org_id` conventions under
[platform ADR-0039](../../../platform/docs/architecture/decisions/0039-organization-neutral-tenancy.md).

Common employment identity and dates/status belong to a shared capability under
[platform ADR-0040](../../../platform/docs/architecture/decisions/0040-shared-employment-core-and-application-settings.md).
Leave owns its domain settings and uses authorized shared contracts. This changes
ownership, not the approved employee workflows. Shared optional supervisor, department and location assignments follow
[platform ADR-0041](../../../platform/docs/architecture/decisions/0041-shared-supervisor-department-and-location.md).
These belong to organization-specific employment, not the global person.

## Product purpose

The Leave Tracker enables employees of multiple NGOs to request and manage leave,
gives approvers reliable staffing visibility, and gives Leave Managers auditable
control over policies, entitlements, balances, calendars, and workflows.

It is also the reference application for the platform's application silo,
FastAPI API pattern, shared shadcn design system, tenant isolation, content handling,
notifications, background jobs, and audit conventions.

The shared shadcn libraries expand incrementally as features are implemented. A
component starts inside Leave unless it is already clearly generic. Once its API is
proven, domain-neutral UI is promoted to `platform/ui-core` or
`platform/ui-business` with catalogue documentation, accessibility tests, visual
coverage, and interaction tests. Leave-specific components remain in the silo.

The same rule applies to application scaffolding. Every implemented feature receives
a scaffold impact review. Proven, domain-neutral conventions are added to or updated
in `platform/builder-cli` during the same delivery item, together with generator
tests, validation rules, documentation, changelog entries, and migration guidance.
A feature is not complete while applicable scaffold work remains outstanding.

The scaffold should teach future applications how to use platform mechanisms—such
as authentication, active-NGO context, FastAPI contracts, the design system,
content-service clients, outbox workers, auditing, RLS testing, and CI—without
generating Leave-specific policy or workflow code.

Delivery uses the installed BMAD workflows under
[platform ADR-0010](../../../platform/docs/architecture/decisions/0010-bmad-as-delivery-workflow.md).
Each substantial slice links to this feature specification and applicable ADRs,
records its acceptance and implementation evidence, and completes BMAD,
agent-context, scaffold, and shared-UI impact reviews. Repository-owned
[platform agent context](../../../platform/prompts/README.md) contains Agriplatform
safeguards rather than a competing generic workflow.

Acceptance examples are agreed and automated before user-visible production
behavior. ATDD provides the outer feature loop; focused TDD drives domain rules,
state transitions, calculations, APIs, UI behavior, integrations, and defect fixes.
AI-assisted refactoring begins with characterization tests wherever relied-upon
behavior lacks adequate protection. See
[platform ADR-0009](../../../platform/docs/architecture/decisions/0009-atdd-and-tdd-development-loop.md).

## Product principles

- Make the employee's next action obvious.
- Explain every leave calculation before submission.
- Preserve historical policy, schedule, workflow, and balance meaning.
- Protect sensitive absence reasons and documents by default.
- Keep each NGO's data and configuration strictly isolated.
- Prefer configurable policies over jurisdiction-specific hard-coded logic.
- Make overrides explicit, exceptional, reasoned, and auditable.
- Never equate platform administration with permission to read employee records.

## Personas and roles

### Employee

A person with an employment membership in an NGO. A single platform identity may
be an employee of multiple NGOs and can switch active NGO context.

### Approver

Reviews requests assigned through the configured workflow and decides the assigned
approval step. Supervisor relationships may resolve who receives a step; final
approver describes a workflow position, not a separate role. Retain one-/two-step
MVP workflows, self-approval rules, policy-permitted insufficient-balance override
authorization, and separate document checks. The role never grants approval over
unassigned requests. See
[ADR-0082](./architecture/decisions/0082-one-approver-role-with-workflow-steps.md).

### Leave Manager

For MVP, Leave Managers have NGO-wide employee scope within each NGO where they
hold that role. Department/location restrictions on this role are deferred. This
does not grant access to other NGOs or remove separate action permissions for
approvals, on-behalf corrections, balance adjustments, or sensitive documents.

Administers leave types, policies, calendars, schedules, entitlements, balances,
workflow configuration, reporting, and operational exceptions for one NGO.
Within their authorized NGO and resource scope, Leave Managers can see leave
types (including sensitive types), employee notes, and approval history through
their Leave Manager role. Sensitive-document access is a separate permission.
See [ADR-0013](./architecture/decisions/0013-leave-manager-field-visibility.md).

### Organization Administrator

Manages NGO membership, roles, structure, and application configuration. This role
does not automatically grant access to medical documents or all employee detail.

### Platform Administrator

Operates platform infrastructure and tenant lifecycle. This role does not
automatically grant business-data or document access inside an NGO.

## Permissions

Use application-maintained default roles backed by explicit business-capability
permissions, with advanced custom roles as defined by
[platform ADR-0011](../../../platform/docs/architecture/decisions/0011-application-roles-and-business-permissions.md).
Default-role setup does not require clients to configure each permission. Custom
roles can begin as copies; new permissions require review rather than silently
expanding custom access. Production grants require an authorized actor.

Each custom role belongs to one application, with multiple custom roles allowed
for Leave. Inherit application context when opening Create custom role; begin with
name, description, and capability selection rather than a required template choice.
Duplicate role on an existing role may prefill the same editor. Do not introduce
cross-application role bundles in MVP.

Combine assigned-role grants within the active NGO while preserving their scopes;
absence of a permission in one custom role does not deny a grant from another.
Approval-step assignment, self-approval rules, and sensitive-document checks remain
independent requirements. Use shared platform access management and reusable role
controls; Leave owns its catalog and enforces request-level checks in its API.
Follow the shared [role lifecycle and return-navigation contract](../../../platform/EXPERIENCE.md): review holder impact, allow deletion only when unassigned, preserve audit history, and link holders to their application access with a contextual return to the role editor.

Recording a justified exception for missing temporary approvers is an underlying
capability included in Leave Manager by default. No additional client setup is
required for that role. A custom role may omit it. This permission does not grant
approval authority, and the explanation, audit, and unresolved-gap requirements
remain. The catalog identifier will be set during permission-contract design.

The role and permission model was approved on 2026-09-01. The permission families
are:

- `leave.request.own.*`
- `leave.request.team.read`
- `leave.request.org.read`
- Unified approval action capability, scoped to assigned workflow steps (replaces
  separate supervisor/final action entries; catalog identifier to be finalized)
- `leave.balance.own.read`
- `leave.balance.team.read`
- `leave.balance.org.read`
- `leave.balance.adjust`
- `leave.balance.override`
- `leave.policy.read|manage`
- `leave.calendar.read|manage`
- `leave.schedule.read|manage`
- `leave.workflow.read|manage`
- `leave.report.export`
- `leave.document.attach`
- `leave.document.sensitive.read`
- `leave.admin.on_behalf` (separate permission for on-behalf actions)

Permissions are evaluated against the active NGO membership and resource scope,
not only the user's role name.
Assigned approvers may see the leave type, including sensitive types, and employee
note for requests within their approval scope through their normal approval role.
No additional sensitive-field permission is required for those two fields. Medical
documents still require `leave.document.sensitive.read` and request-level document
authorization; approval authority alone does not grant document access. See
[ADR-0012](./architecture/decisions/0012-assigned-approver-field-visibility.md).
On-behalf submission requires separate authorization; approval authority alone
does not grant it. Such actions require a reason, visible attribution, and conflict
checks as recorded in [ADR-0007](./architecture/decisions/0007-required-approval-and-automatic-decisions.md).
Within the permitted employee/resource scope, on-behalf permission also permits
cancelling approved leave and submitting a replacement. Approval authority alone
does not grant cancellation or replacement rights over another employee's leave.

## Feature catalogue

### 1. Identity, NGO context, and onboarding

- Sign in with Microsoft Entra ID through Supabase Auth.
- Join NGOs only through an authorized invitation/provisioning process.
- Switch between NGOs without creating separate platform identities.
- Display the active NGO prominently in the application shell.
- Load roles, permissions, employment record, policies, schedules, and reporting
  relationships separately for each NGO membership.
- Block subsequent authorization checks immediately for suspended or ended
  memberships, without waiting for sign-out or token expiry. An already-authorized,
  short executing operation may finish; an open form grants no authority, and
  queued/delayed new execution requires fresh authorization. Follow
  [platform ADR-0021](../../../platform/docs/architecture/decisions/0021-revocation-and-in-flight-operations.md).
- Record security-relevant identity and NGO-context changes in the audit log.

**Rule:** Successful authentication does not by itself grant access to an NGO.

Setup presents a non-sequential checklist for people/supervisors, work profiles/
holidays and leave types/policies. Do not include consultant correspondence,
email-approval status or a standard opening-balances row. Surface an actionable
balance issue only when actually detected; do not infer missing opening data from
a legitimate zero balance.
Derive checklist status from saved configuration: Not started for absent essentials,
Needs review for incomplete/invalid settings, Ready when required checks pass, and
Couldn’t check with Retry when assessment fails. People stays Not started with no
employees; otherwise check active employees’ required employment, work-profile and
approval-route configuration. Reassess after changes without a manual completion
flag or consultant-email tracking. Migration email approval remains in the consultant
process with evidence tied to the exact import batch; no application email workflow
is introduced. Normal authorized balance administration remains available.

### 2. Organization and employment structure

- Manage departments, teams, locations, and employee employment records.
- Assign an effective-dated supervisor and other approval assignments.
- Configure acting/delegated approvers for an effective period.
- Retain historical relationships so old requests retain their original context.
- Use one shared employment relationship per person per organization, retaining
  distinct employment periods for leaving and rejoining without replacing historical
  references (agreed 2026-09-23). Period constraints remain shared-contract work.
- Under [platform ADR-0042](../../../platform/docs/architecture/decisions/0042-person-account-employment-and-legacy-adoption.md),
  shared people/employment may exist without login accounts. Verified account linking
  and access grants remain separate; employee-only acknowledgements still require
  that employee's authenticated participation. E1 needs no accountless administration UI.
- Support employees with non-standard schedules and locations.
- Present employee Leave settings in Employment & approval, Work schedule, and
  Leave entitlement groups, with authorized focused edits and separate balance
  adjustment/history actions. Show inherited values and individual overrides.
- Reuse shared person identity (name and sign-in email) rather than a second
  editable Leave identity. Leave-specific settings refer to that person; this
  places common employment identity and dates/status with the shared employment
  owner under platform ADR-0040. Under platform ADR-0041, the shared owner also
  maintains optional department/location references and a manually maintained optional
  supervisor reference in the same organization. Leave-specific settings remain local.
  Shared edits use authorized service contracts; Leave owns approval policy.
- Department and location may be unassigned (null); neither is required merely to
  create an employee or draft. A supervisor may also be unassigned, but submission
  needs a valid eligible supervisor when its configured route requires one. Resolve
  and snapshot the supervisor at submission; subsequent changes do not silently
  reroute pending requests. Preserve effective-dated assignment history.
- Shared location is separate from the Leave work profile. Changing or clearing
  department/location does not silently change schedules, timezone, holidays or
  explicit profile overrides. Authorized reporting/filtering supports unassigned
  values; an unavailable lookup must not masquerade as unassigned.

### 3. Jurisdictions and workplace calendars

- Store NGO, location, employee, and policy jurisdiction metadata as applicable.
- Configure holiday calendars by country, region, location, or employee assignment.
- Support employees in multiple countries within the same NGO.
- Configure standard and non-standard working weeks.
- Support observed holidays, special NGO holidays, and partial working days.
- Apply timezone-aware, effective-dated employee schedules.
- Preserve the calculated working-time snapshot on submitted applications.
- Assign one explicit work profile per employee, with an NGO default fallback.
  Team/location choices may suggest an initial profile; changing them must not
  silently reassign a profile or merge several profiles.
- Show inherited work-profile values and employee overrides, with a way to restore
  each overridden value to the profile. Preserve explicit overrides when changing
  the assigned profile.
- Review effective date, reason, and affected employees/requests before applying
  schedule changes. Preserve historical request calculations and surface impacts
  through the existing correction and acknowledgement rules.

The MVP does not claim to encode or maintain employment law. Configuration must be
reviewed by each NGO for its operating jurisdictions.

Preserve work-profile identity separately from its effective-dated schedule versions.
Use an archive timestamp to retire a profile, retaining historical versions and
request snapshots. Block archiving while current/scheduled assignments depend on
it or it is the NGO default; provide affected-employee links to resolve assignments.
Creating a profile does not assign employees automatically. Default changes preserve
explicit assignments/overrides and review fallback-dependent employees.
[ADR-0086](./architecture/decisions/0086-archive-markers-and-effective-dated-versions.md)
distinguishes archiving, calculation versions and audit; physical schema design
remains architecture work, without blanket duplicate history tables.

### 4. Leave types and policy management

Provide seeded Annual Leave, Sick Leave, and Family Responsibility Leave examples.
Leave Managers may create additional types and configure them per NGO.

Each versioned leave type/policy supports:

- Name, code, description, color, icon, and active dates
- Paid or unpaid classification
- Permitted units: full day, half day, hours
- Annual entitlement available daily, upfront, or in monthly instalments; manual-only grants remain separate
- Entitlement, proration, carry-over, cap, and expiry, with fixed whole-minute precision
- Minimum/maximum duration and notice period
- Backdated and future-request rules
- Current versus projected balance use
- Negative balance, unpaid conversion, or split behavior
- Supporting-document rules and duration threshold
- Eligibility by employment type, location, tenure, or assignment
- Privacy classification used by calendars and notifications
- Configured approval workflow
- Cancellation and amendment rules

Policy editing uses conditional fields: show carry-over limit only for limited
carry-over, expiry/repetition when carry-over is enabled, cap amount when capped,
final approver for two steps, and a document threshold only
for threshold-based requirements. A requirement for leave longer than 2 days does
not require a document at exactly 2 days; a 3-day request requires it. This is an
illustrative threshold, not a universal or jurisdictional default.

Used leave types and policy versions are archived rather than hard-deleted.

### 5. Employee entitlement overrides

Distinguish one-off balance adjustments from recurring entitlement overrides.
Recurring overrides persist until explicitly changed, rather than lasting only
one calendar year. MVP has no automatic override end date. Recurring changes, including a return to
policy entitlement, take effect only at a leave-period boundary; default to the
next boundary under the applicable policy, not necessarily 1 January. Use a
separate authorized adjustment for an immediate balance change. Do not reset the
current balance to the recurring allowance or introduce automatic midperiod
recalculation on an override end date. One-off grant validity/expiry rules still apply.

- Show policy entitlement and any employee-specific override together.
- Use one **Edit employee entitlement** action to select policy entitlement or a
  recurring custom entitlement. Link to **Adjust leave balance** for a one-off change.
- Add an effective-dated entitlement override with reason and authorizer.
- Preview its accrual/ledger effect before confirmation.
- Support future-dated changes and ending an override at leave-period boundaries.
- Follow [ADR-0083](./architecture/decisions/0083-recurring-entitlement-period-boundaries.md); monthly accrual does not make every month a leave-period boundary.
- Never rewrite historical ledger entries silently.
- Audit every override and resulting adjustment.

### 6. Balance ledger and accrual

Balances derive from immutable actual balance events and automatic entitlement
calculated from effective-dated history, rather than a mutable total.

Employee balance details show a prominent available amount with remaining
entitlement and reservations against that entitlement distinguished. Link pending
reservations to their requests, preserving return context. Use expandable,
plain-language entitlement-history entries for grants, carry-over, expiry,
approved deductions and adjustments, including relevant request context and
adjustment actor/reason. Keep reservations visibly separate so they are not counted
twice. A history-year filter changes history only, not the current balance.
Expandable hours/calculations explain the applicable standard-day conversion;
existing current-versus-projected funding rules remain authoritative.

For manual adjustments, show Add/Deduct, amount, effective date, reason, current
balance, resulting balance, and affected requests. Keep **Review adjustment** then
**Confirm adjustment** so the authorized actor checks consequences before posting.
Correct a mistaken adjustment through another explained adjustment; do not edit
ledger history or introduce a separate correction command. Notify the employee by
minimal email and in-app notification linking to authorized details: amount, date,
resulting balance, actor, and reason. Require renewed acknowledgement only where
an existing request's unpaid amount increases, following the existing safeguards.

Supported transactions include:

- Opening balance
- Automatic accrual (derived; no daily posted transaction required)
- Carry-over
- Expiry
- Pending reservation
- Approved consumption
- Rejection/withdrawal release
- Cancellation reversal
- Manual adjustment
- Negative paid leave
- Unpaid leave allocation

The system presents accrued, used, reserved, currently available, projected on the
leave date, requested, and projected remaining amounts.

Automatic entitlement is calculated authoritatively by the backend for the relevant
date, without depending on a scheduled worker posting grants. Repeated calculations
must not duplicate entitlement. Preserve immutable actual events, effective-dated
inputs and request/decision snapshots; derived accrual and posted entries must not
be counted twice. See [ADR-0090](./architecture/decisions/0090-annual-entitlement-availability-options.md).
Use on-demand accrual rather than daily accrual transactions. Store effective-dated
policy/employment history and immutable actual events; preserve calculation evidence
at consequential submissions, approvals and confirmed changes. Routine balance reads
need no accrual transaction or decision snapshot. Snapshots explain past decisions
without replacing fresh backend validation for a new action. Any future materialized
projection is subordinate to the authoritative calculation. See
[ADR-0106](./architecture/decisions/0106-on-demand-accrual-with-decision-evidence.md).
Historical corrections preserve original approvals and calculation snapshots while
recalculating affected balances from corrected information and subsequent events.
Record the correction actor, explanation and consequences; apply existing protected
request and renewed unpaid-acknowledgement safeguards. Ordinary balance views show
the corrected result. Request history exposes the original **Balance at approval**
and clearly distinguishes later recalculations. A corrected historical balance is
not simply substituted for the current balance. See
[ADR-0107](./architecture/decisions/0107-corrected-balances-preserve-decision-evidence.md).

Initially calculate directly from efficiently queried authoritative history, without
a balance cache, calculation checkpoints or another worker for accrual. Define a
representative workload and response targets before affected story readiness; test
realistic employee counts and several years of history before release. Only add
rebuildable checkpoints if measurements justify them. Corrections invalidate all
affected checkpoints and dependent later results; invalid checkpoints cannot support
confirmation. Checkpoints remain disposable derived results, distinct from preserved
decision evidence. See
[ADR-0108](./architecture/decisions/0108-measure-accrual-performance-before-checkpoints.md).

At each local date boundary, resolve expiry before new earning. At a leave-year
boundary, resolve prior-period carry-over and expiry before new-period entitlement.
Evaluate cap headroom after those effects. Inclusive expiry remains usable through
the stated expiry date. Example: 20 days at cap, with 2 expiring at the end of
31 March, becomes 18 before adding 1 April earning. This fixed ordering applies to
on-demand calculations, historical replay and future projections without waiting
for worker posting or double-counting recorded effects. Existing carry-over limits,
reservation safeguards and no-catch-up rules remain. See
[ADR-0109](./architecture/decisions/0109-expiry-and-rollover-before-new-earning.md).

Store effective date, recorded time and an internal server-assigned sequence for
balance changes. After automatic start-of-day effects, replay otherwise same-day
user changes in their accepted sequence, assigned within the serialized employee/NGO
mutation transaction. Do not rely on timestamp precision or client clocks. Retries
retain the original event order. Backdated changes retain actual recorded time and
follow existing impact/correction safeguards; original approval evidence remains.
User-facing history shows effective date, actor and recorded time, not the internal
sequence. See
[ADR-0110](./architecture/decisions/0110-stable-order-for-same-day-balance-events.md).

Store consequential calculation snapshots in a Leave-owned table linked to the
request or other action, atomically with that action. Use searchable context columns
and structured JSON for relevant inputs/results, allocation and version evidence.
Preserve input values or retained immutable input versions, not mutable references
alone. Record the calculation version separately from the policy version so a code
fix can be investigated without rewriting original evidence. Existing correction
safeguards govern resulting balance changes. Reuse current permission/history patterns;
no generic framework, new administration screen or historical-code execution engine
is required. Routine reads create no snapshot. See
[ADR-0111](./architecture/decisions/0111-modest-calculation-snapshots-and-version-evidence.md).

At consequential confirmation, verify applicable policy, calendar, employment and
other calculation inputs alongside the balance and reviewed record. Recalculate
changed inputs and require renewed confirmation if duration, paid/unpaid allocation
or another consequential reviewed detail changes; preserve entered information.
Changes without consequential effect may proceed after all other checks pass.
Protect final verification and commit against concurrent relevant configuration
changes, with participation by configuration writers; employee locking alone is
insufficient. Preserve submitted-request policy snapshot semantics. See
[ADR-0112](./architecture/decisions/0112-revalidate-calculation-inputs-at-confirmation.md).

Recalculation after a cancellation or historical correction means evaluating updated
authoritative history, not repairing a stored balance total. Evaluate consequential
request/funding impacts before confirmation; after committing the immutable change,
subsequent balance reads use that history and the frontend refreshes its result.
Only if derived performance checkpoints are introduced later must affected ones be
invalidated. Balance consequences must be checked even when no balance screen is open.

Calculation acceptance coverage must include ordinary daily earning without a worker,
partial monthly employment, expiry before same-day earning, cancellation/correction
with original evidence and cap safeguards, changed inputs at confirmation, repeated
submission, and concurrent attempts to consume the same entitlement. Combine focused
arithmetic tests with transaction/integration tests; these are requirements for future
implementation, not a claim of currently passing application tests.

Concurrent changes for one employee use a short bounded coordination wait, then
load fresh protected state. If coordination times out before business effects,
preserve the form and show: **Another change is being completed for this employee.
Please try again.** Retrying follows the existing operation-identity contract;
changed consequential results require renewed confirmation. Distinguish a known
uncommitted busy attempt from an uncertain network outcome, which still requires
operation-status resolution. Define and test the timeout in the affected story.
See [ADR-0113](./architecture/decisions/0113-bounded-wait-for-concurrent-leave-changes.md).

Apply the platform-wide short-transaction principle: check current shared access
before the protected Leave action; validate current Leave eligibility and calculation
inputs inside it, and atomically commit domain effects, audit/snapshots and notification
intent. Release employee coordination before shared-service delivery. Do not wait for
external services while holding business locks by default. Preserve authorization
freshness across delays and document justified exceptions under
[platform ADR-0022](../../../platform/docs/architecture/decisions/0022-short-transactions-and-external-service-calls.md).

Operational diagnostics follow
[platform ADR-0023](../../../platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md):
structured action/outcome/timing/error fields and operation/event/trace links, with
internal NGO/record identifiers only where needed. Exclude employee notes, medical
content, credentials, signed URLs and payload dumps, including error/telemetry paths.
Keep authorized business audit separate. Plain-language errors may offer safe support
references in expandable details, never raw technical errors or sensitive contents.

The MVP operational scope is safe structured logs with operation IDs, health checks,
a few actionable alerts, basic OpenTelemetry API/shared-service tracing, and one
working monitoring setup verified with a simple failure scenario. Telemetry export
is bounded/asynchronous and cannot be a prerequisite for business actions. Browser
tracing may follow backend instrumentation without blocking initial implementation.
Comparative Loki/OpenSearch trials, AI diagnosis/repair and advanced error-management
workflows are not MVP gates. See the
[platform observability direction](../../../platform/docs/operations/observability-and-ai-investigation-direction.md).

Report API readiness, worker health/progress and notification delivery separately.
A delivery-provider outage flags failed/delayed notifications without preventing Leave
submission or approval when their required dependencies are available. Detect a worker
that is running but stuck when eligible work exists; an empty idle queue is not failure.
Required authorization unavailability still fails closed. Health intervals/thresholds
are operational delivery decisions, not administrator settings.

MVP outbound delivery uses a Leave-owned PostgreSQL outbox and a separate worker
process, initially one instance. The API writes intent atomically with business effects;
the worker claims work briefly, releases its transaction before HTTP handover, and
recovers expired claims. Preserve stable event identity and receiver deduplication;
claim ownership protects completion during overlapping attempts. Remote acceptance
completes handover, not final channel delivery. Other services do not read Leave tables.
Keep this a small delivery worker, with no MVP broker, Temporal or custom workflow
engine. Revisit broker fan-out or durable orchestration for concrete multi-consumer
or multi-service workflows. See
[ADR-0114](./architecture/decisions/0114-owned-outbox-worker-without-mvp-workflow-engine.md).

Notification handover follows
[platform ADR-0024](../../../platform/docs/architecture/decisions/0024-durable-delivery-retries-and-audited-recovery.md):
retry temporary failures with bounded increasing delays; stop for correction-required
failures; retain exhausted work and alert operations. Authorized audited recovery
requeues the unchanged event through the normal worker with current state checks and
duplicate safety. It never repeats the original leave action. Failure after shared
notification acceptance belongs to that service. MVP recovery needs a command/runbook,
not a Leave Manager queue-management screen; command hosting is not yet selected.

Apply [platform ADR-0025](../../../platform/docs/architecture/decisions/0025-record-attribution-and-audit-provenance.md)
to Leave persistence: server-managed creation/update actor IDs and UTC timestamps on
mutable business records; creation attribution on immutable ledger/audit/snapshot
records. Preserve human initiation separately from service execution. These summary
fields do not replace consequential audit. Operational audit records command and
release identifiers; source-file line numbers remain diagnostic details. Generated
API inputs cannot override attribution, and all supported write paths must preserve it.

The Leave worker uses one restricted service identity across NGOs, not per-NGO
accounts or keys. A narrow queue-discovery/claim operation supplies authoritative
item ownership. Process each item with explicit transaction-local NGO/service context;
verify ownership and prevent pooled-context leakage. Context scopes access but does
not grant authority or unrestricted cross-NGO employee access. Keep human initiation
separate from service execution. See
[ADR-0115](./architecture/decisions/0115-single-worker-identity-with-scoped-ngo-processing.md).

The shared worker identity/scoping convention is authoritative under
[platform ADR-0026](../../../platform/docs/architecture/decisions/0026-worker-service-identity-and-ngo-scope.md);
Leave ADR-0115 specifies its application here. Apply
[platform ADR-0027](../../../platform/docs/architecture/decisions/0027-bounded-worker-shutdown-and-deployment-reporting.md)
to deployments: stop claims, permit bounded completion, then allow supervisor force
termination with durable duplicate-safe recovery. Report grace-period overruns in the
deployment report and structured logs. Verify replacement health and progress before
claiming recovery; otherwise state that it is unconfirmed. Repeated forced stops or
failed recovery draw operational attention; no dedicated MVP dashboard panel is needed.

Durable Leave events carry explicit type and payload version under
[platform ADR-0028](../../../platform/docs/architecture/decisions/0028-event-payload-versions-and-queued-work-compatibility.md).
New consumers preserve the meaning of versions still produced or present in queued,
in-flight and failed/retryable work. Retain and flag unsupported versions without
silently discarding them or guessing payload meaning. Use explicit models and old-event
compatibility tests; no MVP schema registry. Retire old handlers only after relevant
work and producer versions no longer need them, including rollout/rollback considerations.

Keep the outbox in the Leave-owned schema, not a shared cross-application SD schema.
Reuse proven mechanics/scaffolding per owner. Before handover, Leave determines whether
an action-request notification remains relevant; skip obsolete unhanded work with a
reason while preserving payload and audit. Treat factual updates by their own rule.
Shared notifications own delivery mechanics. Local skip state cannot cancel a remote
accepted delivery or resolve uncertain acceptance; later changes may still race handover,
and links must show current authorized state. See
[ADR-0116](./architecture/decisions/0116-owned-outbox-and-obsolete-notification-intent.md).

Notification retries expire 90 days after original event creation under
[platform ADR-0029](../../../platform/docs/architecture/decisions/0029-notification-retry-expiry-and-retention.md).
Retries never reset that deadline. Mark unresolved delivery expired and retain terminal
completed/skipped/expired outbox details and attempts for 90 further days. Receiver
deduplication lasts at least 90 days after acceptance and while unresolved; receivers
reject expired events even after cleanup. A later communication requires a newly
authorized notification based on current state, a new event ID, reason and original-ID
reference, without repeating the leave action. These limits do not govern business
audit, leave history, calculation snapshots or generic command idempotency.

Notifications describe dated historical events, not guaranteed current status. Do not
guarantee email arrival order or block newer notifications behind failed older work.
Links recheck authorization and show current request state; notification processing
never rolls business state back to an older event. Preserve obsolete action-request
checks and minimal sensitive content. See
[ADR-0117](./architecture/decisions/0117-notification-order-and-current-request-state.md).

Finalized content IDs bind the exact verified bytes under
[platform ADR-0038](../../../platform/docs/architecture/decisions/0038-finalized-content-byte-identity.md).
Outstanding upload capabilities and finalization races cannot change those bytes behind
an existing attachment. Replacement requires a new content identity, fresh verification
and an authorized audited association change, preserving original decision evidence.

Attachments follow
[platform ADR-0030](../../../platform/docs/architecture/decisions/0030-recoverable-content-attachment-association.md):
separate finalized upload from confirmed Leave association, show Attaching until saved,
and retry a failed/uncertain association using existing content and duplicate-safe
operation identity. Validate NGO ownership/permission/readiness; block submission when
a required attachment remains unconfirmed. Coordinate Content Service cleanup with
association lifecycle so saved drafts/submitted attachments and confirmation races
are protected; determine the concrete contract before affected implementation.

Document operations determine success/failure on each attempt via the backend and
bounded dependency calls. Report failure of the attempted action rather than declaring
the Content Service globally offline or promising a temporary outage. Distinguish
connection/timeout/unavailable errors from denied access or missing content; retries
are fresh attempts, preserving identity for uncertain mutations. No MVP frontend
availability polling or per-action health preflight is required. Keep Content Service
and direct-storage failures distinct in diagnostics. Other Leave capabilities remain
available when their own checks pass; required document/authorization checks cannot
be bypassed. See the shared experience dependency-failure guidance.

Leave follows
[platform ADR-0031](../../../platform/docs/architecture/decisions/0031-machine-readable-api-errors-and-localized-presentation.md):
stable error identifiers drive attachment attention, refreshed review, busy retry and
access-denied behavior. Safe typed details and localized messages remain distinct.
Unknown identifiers fall back safely; English/Portuguese wording does not control logic.
Preserve form input and existing uncertain-operation recovery. Evolve the scaffold wire
contract with generated frontend types and backend adapters before implementation.

Session expiry recovery follows
[platform ADR-0032](../../../platform/docs/architecture/decisions/0032-session-recovery-and-return-navigation.md):
try normal renewal, then require sign-in if needed and return the same authorized user
to the prior NGO/page/request and recoverable drawer/draft context. Reload permissions
and calculations before continuing; never automatically submit after sign-in. Protect
prior-user data on account changes and use safe fallback for lost access/deleted records.
Retain existing Leave draft rules and resolve uncertain submissions by operation ID.

Apply [platform ADR-0035](../../../platform/docs/architecture/decisions/0035-database-structural-integrity-and-application-rules.md)
for structural persistence guarantees: required fields, valid owner-local references,
scoped operation/event identity uniqueness, active-draft uniqueness and matching NGO
scope for tenant-owned relationships. Retain RLS and friendly API validation. Complex
leave calculations/approval decisions remain in authorized transactional workflows;
map recognized database conflicts safely without leaking internals. Do not introduce
unapproved cross-service schema dependencies through generated foreign keys.

Daily precision follows ADR-0092 below. Historical interval/bucket treatment and
ledger representation still require resolution before affected calculation stories
are ready.

MVP automatic policies configure an annual entitlement and its availability mode.
Manual grants remain separate:

| Schedule | Behavior |
|---|---|
| Earned daily | Earn annual entitlement proportionally across eligible calendar days in the leave year, including today from its start in the employee work timezone; calculate cumulative earning and floor usable total to whole minutes (ADR-0092) |
| Annual upfront | Grant at the start of the entitlement period; a mid-period joiner receives a joining grant using the policy proration rule |
| Monthly instalments | Release portions of annual entitlement at the start or end of each leave-year-aligned monthly instalment period, as selected by policy; prorate partial employment months under the policy's rule |
| Manual only | Authorized staff grant entitlement with an audited reason; no automatic scheduled grants |

Daily earning precision: calculate annual entitlement minutes multiplied by eligible
days divided by actual leave-year days, retaining fractional precision and rounding
down only the resulting usable total to whole minutes. Do not round individual
daily portions or add to yesterday's rounded balance. With 8,640 annual minutes,
100 eligible days in a 365-day year gives 2,367 usable minutes; all 365 days gives
8,640 minutes, before other effects. The unchanged-input formula does not replace
historical cap/expiry/policy replay. Standalone upfront grants use final-amount
rounding; related monthly partial portions preserve cumulative fractions under ADR-0105. See [ADR-0092](./architecture/decisions/0092-cumulative-daily-entitlement-precision.md).

Daily employment boundaries: include the employee's start and end dates, earning
nothing outside employment. Divide by the full applicable leave year's actual
length, not the remaining employment duration. With 18 annual days and 100 eligible
days in a 365-day period, earn 18 × 100 / 365 before other effects. Do not prorate
the annual amount again for the same partial employment. One-date employment has
one eligible day. Upfront/monthly joining and leaving rules remain separate. See
[ADR-0094](./architecture/decisions/0094-daily-earning-employment-boundaries.md).

Daily cap behavior: calculate earning in effective-date order, adding only what
fits at each eligible day's start. If a current-effective balance deduction later
that day creates room, resume at the next eligible day's start. Do not recover
earning excluded while capped. For example, Ana at her cap Monday morning earns
nothing Monday; a deduction later Monday permits Tuesday's normal portion, not a
catch-up for Monday. Pending earned reservations and cancellation recalculation
retain their existing cap safeguards. On-demand calculation must explain capped-out
earning from historical inputs, without requiring daily posting. See
[ADR-0093](./architecture/decisions/0093-daily-cap-and-prospective-resumption.md).

Apply the daily accumulated cap before whole-minute usability rounding. With a
120-minute cap, 119.8 minutes accumulated and 0.5 minutes newly eligible, accept
0.2 and exclude 0.3. Earned fractions below the cap remain; excluded fractions do
not become a hidden reserve for later recovery. Historical corrections still
follow their existing recalculation safeguards. See
[ADR-0095](./architecture/decisions/0095-precise-cap-before-usable-rounding.md).

Daily policy-rate changes apply prospectively per eligible date. An annual rate
increase from 18 to 24 days effective 1 July uses 18 for earlier dates and 24 from
1 July, preserving prior earning. In an unchanged 365-day calendar year with full
eligibility and no cap/expiry effects, compute 18 × 181 / 365 + 24 × 184 / 365
days, converting under the applicable schedule and combining precise portions
before whole-minute rounding. Do not use the segment length as the denominator.
Individual recurring overrides retain their leave-period-boundary constraint;
request impacts and backdated corrections retain their existing safeguards. See
[ADR-0096](./architecture/decisions/0096-daily-earning-across-policy-versions.md).

Daily availability example: With an unchanged 18-day annual amount and full
eligibility throughout a 365-day calendar year, 1 January includes one day's
portion, 2 January two portions, and 31 December all 365 portions. Apply other
balance rules separately and use actual leave-year length. No worker execution
is required to make the daily portion available. See
[ADR-0091](./architecture/decisions/0091-start-of-day-daily-entitlement.md).

Changes between daily, monthly and upfront availability take effect only at the
employee's next leave-period boundary. Finish the current period under its existing
method; preserve carry-over and existing request impact safeguards. Anniversary
employees may have different effective dates, which must be shown in the preview.
This does not restrict prospective annual-rate changes within a daily policy under
ADR-0096. See [ADR-0098](./architecture/decisions/0098-availability-method-changes-at-period-boundaries.md).

Upfront annual-amount changes begin at the affected employee's next leave-period
start. Preserve the current grant; immediate extra entitlement uses a separately
authorized balance adjustment. For example, an 18-to-24-day change leaves this
year's 18-day grant unchanged and uses 24 days next period, subject to applicable
rules. Communicate actual effective dates under ADR-0101. See
[ADR-0102](./architecture/decisions/0102-upfront-entitlement-changes-next-period.md).

Monthly annual-rate changes start at the next applicable instalment period; leave
the current and prior instalments unchanged. An 18-to-24-day increase during
15 July–14 August changes the nominal portion from 1.5 to 2 days for the period
starting 15 August. Under end-of-period availability it is usable on 14 September.
Show old/new amounts and actual employee effective dates in editing/review, clearly
distinguishing rate start from first availability. Confirmed annual-entitlement
changes notify actually affected employees by in-app message and email; amended
or cancelled scheduled changes notify again. Use generic text and authorized links
for sensitive leave types. Continuing overrides that prevent an effective amount
change must not produce a misleading entitlement-change notice. See
[ADR-0101](./architecture/decisions/0101-monthly-rate-changes-and-effective-date-notifications.md).

For complete monthly instalments with unchanged annual entitlement, floor the
cumulative nominal amount (annual minutes × instalments elapsed / 12) to whole
minutes; each instalment is the difference between successive cumulative nominal
amounts. An 8,550-minute year gives 712 minutes first, 713 next, and 8,550 over twelve
complete instalments. Calculate nominal portions independently of cap exclusions
or leave consumption so neither is restored by later instalments. Extend this precise
running calculation to partial employment periods and effective-dated annual-rate
changes within the leave year. Each portion uses its applicable rate and employment
ratio; changing the rate does not reset earned fractions. Related monthly partial
portions are cumulative, not independently rounded standalone grants. Apply cap and
other balance effects chronologically without recovering excluded amounts. Uncapped
exact portions of 712.5 and 952.5 minutes give 712 initially and 1,665 cumulatively.
Year-end carry-over remains separately governed. See
[ADR-0097](./architecture/decisions/0097-cumulative-monthly-instalment-rounding.md), extended by
[ADR-0105](./architecture/decisions/0105-monthly-precision-across-partial-periods-and-rate-changes.md).

Scheduled grants follow the configured effective dates and the availability rules
below. Manual grants remain subject to existing balance-adjustment authorization,
mandatory reasons, and immutable ledger history. For joining or leaving partway
through a period, each policy chooses no proration or calendar-day proration:
multiply the period's entitlement by the number of calendar days employed within
that period divided by its total calendar days. Include the first and last
employment dates within the period. Manual-only grants remain explicit amounts.
Different leave types may use different versioned policies and proration choices.
For new monthly policies, default to **Adjust for time employed**; retain **Give
the full period allowance** as the alternative without changing existing policies.
Show the illustrative 18-days-per-year example: 1.5 days per complete instalment,
0.75 days for 15 of 30 calendar days employed when adjusted, or 1.5 days with the
full-period choice. Daily earning accounts for employment dates automatically and
hides this selector. Availability timing and joining/leaving corrections remain
unchanged. See [ADR-0104](./architecture/decisions/0104-monthly-partial-employment-default.md).


Acceptance example: Under calendar-day proration, an employee employed for 15
days of a 30-day monthly period receives half that month's entitlement. If the
monthly grant is 480 minutes, the prorated grant is 240 minutes. Under no proration,
the otherwise eligible employee receives the configured 480-minute period grant.
Manual-only grants use the authorized explicit amount without automatic proration.
See [ADR-0025](./architecture/decisions/0025-per-policy-calendar-day-proration.md).

Use one fixed whole-minute rounding convention, without a policy selector. Keep
full intermediate precision and preserve remainders across related cumulative
earning portions; floor usable entitlement only at its defined final boundary.
For a standalone prorated upfront grant, round down once at its final calculated amount.
A 481-minute upfront period grant for 15 of 30 days gives 240.5 minutes and therefore
240 usable minutes; 240.7 calculated minutes likewise gives 240. Record the
calculation in its explanation. Request increments and schedule-based half days
remain unchanged. See [ADR-0103](./architecture/decisions/0103-fixed-minute-rounding-and-plain-policy-language.md),
which supersedes the former configurable rule in ADR-0026.

Policy forms use plain-language labels and contextual examples: 'Leave per year'
explains the full-year allowance, and partial-period settings explain adjusting for
time employed rather than requiring familiarity with 'proration'. Core explanations
are visible or expandable, not hover-only. Rounding is not an administrator setting.

Acceptance examples: An annual-upfront policy grants its configured amount at the start of its
entitlement period, with a joining grant for mid-period employment as defined below. A monthly policy grants its configured portion on its
monthly effective date. Repeated calculation never counts the same automatic earning
portion twice; no posting job is required. A manual-only policy creates no automatic
entitlement; authorized staff can grant an amount with an audited reason, while an
unauthorized actor or a grant without the required reason is rejected. Retrying an
actual manual or correction command must not duplicate its effect.

See [ADR-0090](./architecture/decisions/0090-annual-entitlement-availability-options.md)
and [ADR-0106](./architecture/decisions/0106-on-demand-accrual-with-decision-evidence.md),
which refine the earlier schedules in ADR-0024.

Monthly instalments follow twelve monthly periods aligned to the employee's
leave year. The policy selects the start or end of each instalment period.
Calendar-year policies use calendar months; a 15-July anniversary year uses
15 July–14 August, 15 August–14 September, and so on. Partial employment uses the
applicable instalment period for proration and preserves cumulative fractions across
related monthly portions under ADR-0105.
Use the employee's configured work timezone. Resolve each boundary independently from the original anniversary day and month
offset, clamping only missing dates to that month's end. A 31 January anchor gives
28/29 February, then 31 March and 30 April without drift. Each instalment ends the
day before the next boundary; twelve instalments cover the leave year. This is
separate from inclusive carry-over expiry arithmetic. See
[ADR-0100](./architecture/decisions/0100-anchored-monthly-instalment-boundaries.md). See
[ADR-0099](./architecture/decisions/0099-monthly-instalments-aligned-to-leave-year.md).

Acceptance examples for calendar-year policies: A start-of-month policy grants on 1 April; an end-of-month
policy grants on 30 April, then 31 May. February month-end is 28 February in a
non-leap year and 29 February in a leap year. A 480-minute monthly grant for 15
employed days in a 30-day month is 240 minutes under calendar-day proration.
Repeated calculation must not double-count the monthly earning portion.

See [ADR-0045](./architecture/decisions/0045-monthly-grant-start-or-end.md).

For start-of-instalment policies, an employee joining after the instalment's grant
date receives their initial grant on the employment start date, using the policy's
partial-period proration and rounding rules. Normal grants resume at each subsequent
instalment start. For end-of-instalment policies, the initial grant waits until that
instalment's final date and uses the same applicable partial-period rules.

Acceptance example: An employee starts on 16 April under a 480-minute monthly
policy with calendar-day proration. They are employed for 15 of April's 30 days,
so their initial grant is 240 minutes. A start-of-month policy grants it on
16 April and resumes normal grants on 1 May. An end-of-month policy grants it on
30 April and next grants on 31 May. No duplicate grant is created for April, and
the existing cap and eligibility rules still apply.

See [ADR-0046](./architecture/decisions/0046-mid-month-joining-grants.md).

Month-end grants are available from the start of their grant date in the employee's
configured work timezone, consistent with the general effective-date rule. They
may fund eligible leave on that date; availability does not wait until the next
month.

Acceptance example: A 240-minute grant dated 30 April can fund 240 minutes of
eligible leave on 30 April, subject to cap, expiry, and existing reservations.
It cannot fund 29 April leave. Month-end timing alone must not defer its use until
1 May.

See [ADR-0047](./architecture/decisions/0047-month-end-grant-same-day-availability.md).

If employment ends after an upfront grant, recalculate the affected period's grant
using the policy's agreed proration rule and employment end date. Record any
correction with an employee-visible explanation and new auditable entries rather
than changing prior history. A no-proration policy retains its full otherwise
eligible period grant. If corrected excess entitlement has already been spent,
refer the deficit to an in-scope Leave Manager with balance-adjustment permission
for reasoned, employee-explained review. Do not automatically change previously
approved leave to unpaid. Apply the existing renewed-acknowledgement rule if the
correction increases a pending request's unpaid amount.

Acceptance example: A start-of-month policy grants 480 minutes for April. An
authorized employment update sets the last employment date to 15 April. Under
calendar-day proration, 15 of 30 days earns 240 minutes, so record a 240-minute
correction with the actor and explanation, preserving the original grant. Under
no proration, retain the otherwise eligible 480-minute grant. If the correction
creates a deficit because entitlement was spent, flag it for authorized review;
do not silently reclassify approved leave. Retrying the update does not duplicate
the correction.

See [ADR-0048](./architecture/decisions/0048-upfront-grant-departure-recalculation.md).

Block new submission and final approval when any requested leave date falls after
a known employment end date. The final employment date itself remains eligible
under normal rules. If an authorized end-date change affects an existing request,
flag it for correction or cancellation with the administrator's explanation; do
not silently alter its dates. Preserve existing scoped correction/cancellation
permissions and request history.

Acceptance example: Employment ends on 30 June. A request including 1 July cannot
be submitted or finally approved; leave on 30 June may proceed under normal rules.
If a recorded end-date change to 30 June affects an existing July request, show
the actor's explanation and flag that request for correction or cancellation.
Keep its recorded dates and history until an authorized correction or cancellation
occurs. Do not treat this flag as automatic cancellation or grant new correction
rights to an approver.

See [ADR-0049](./architecture/decisions/0049-leave-after-employment-end.md).

Each policy configures minimum notice in calendar days, defaulting to zero.
Requests with less notice may still be submitted with a mandatory explanation
and a clear short-notice flag for assigned approvers. This does not waive other
eligibility, date, or approval rules. Zero minimum notice does not itself authorize
backdated requests; backdating is a separate policy rule.

Acceptance example: A policy with seven days' minimum notice permits a request
submitted three calendar days before leave only when the employee supplies an
explanation. The assigned approver sees that explanation and the short-notice
flag. Omitting the explanation prevents submission. With the default zero-day
notice, an otherwise eligible same-day request needs no short-notice explanation.

See [ADR-0050](./architecture/decisions/0050-minimum-notice-default-zero.md).

Allow backdated requests without a fixed cutoff. Require a reason and clearly show
assigned approvers how late the submission is. Apply normal approval and existing
employment-date, overlap, and balance rules. Calculate using the historical
schedule and policy applicable to the leave dates, and explain any resulting
balance corrections with auditable entries rather than rewriting history.
Backdating alone does not require a separate administrative submission route.

Acceptance example: An employee submits a 10 September absence on 15 September.
The request may proceed with a mandatory reason, and the approver sees that it
was submitted five calendar days late. A 1 September absence submitted on the
same date is not blocked merely because it is fourteen days late. Both requests
still require normal eligibility, overlap, balance, and approval checks. Missing
the backdating reason prevents submission. A later schedule or policy change
does not substitute today's rules for the historical leave-date rules; explain
and audit any balance corrections resulting from the backdated request.

See [ADR-0051](./architecture/decisions/0051-backdated-requests-without-cutoff.md).

For partial-day requests, collect duration without exact times. Half day uses one
date and exactly 50% of its scheduled working hours, without a first/second-half
choice. Hours uses one date and an amount in 30-minute increments, without start/end
times. The employee may add an optional arrangement note. Full-day date ranges
remain unchanged.

When another submitted, in-approval, or approved request exists for the same employee,
NGO, and leave date, show a potential-conflict warning. Permit submission when the
combined requested duration is within that date's scheduled working hours; block
it when the total exceeds them, including across leave types. Draft, rejected,
withdrawn, and cancelled requests do not count. Concurrent submissions must preserve
this daily limit. This does not waive other eligibility or approval requirements.

Mark the date as having leave in calendars without inventing precise absence times.
Permitted own/request views can show Half day or the requested hours. Colleague
views show Part-day absence without leave type, notes, or document details; retain
Unavailable for full-day entries. Deduct only the requested duration, not a full day.

Acceptance example: On an eight-hour scheduled day, an existing two-hour request
and a new two-hour request may coexist with a same-date warning and four hours of
combined leave. A full-day request plus any positive-duration request is blocked.
A half-day request consumes four hours but does not claim which four hours are
absent. Colleagues see Part-day absence, without the leave type. A concurrent
submission cannot take the active daily total above eight hours.

See [ADR-0074](./architecture/decisions/0074-duration-only-partial-day-leave.md).

Authorized administrative correction must support past, current, and future leave
to match what actually happened. Preserve the actor, reason, original request and
decision history, and resulting balance changes. The correction capability does
not itself waive overlap validation or grant every administrator business-data
access. Existing approved-request cancellation/replacement rules and scoped
on-behalf permissions continue to apply. Administrative corrections require a
Leave Manager with the separate `leave.admin.on_behalf` permission within their
authorized NGO and employee scope. Organization Administrator status alone does
not grant this authority. Require a reason and preserve the full correction history.

Acceptance example: An authorized administrator corrects an absence recorded for
the wrong dates, whether those dates are past, current, or future. The correction
preserves the original record and explains the corrected dates and balance effects.
Approved date/duration changes follow cancellation and linked replacement with
renewed approval. The resulting active requests must respect that employee's daily scheduled-hours
limit within the NGO. Missing correction authority does not become valid through an overlap
error or an administrator title alone.

See [ADR-0052](./architecture/decisions/0052-overlaps-and-administrative-corrections.md).

Acceptance example: An in-scope Leave Manager with `leave.admin.on_behalf` can
initiate an explained correction to past, current, or future leave. Deny that
operation to a Leave Manager without the permission, an actor outside the
authorized NGO/employee scope, or an Organization Administrator holding only that
role. Approved date/duration changes still use cancellation and linked replacement
with renewed approval; correction authority alone does not grant approval rights.

See [ADR-0053](./architecture/decisions/0053-administrative-correction-authority.md).

Notify the employee by email and in-app notification whenever an administrator
corrects their request. Keep notification content within the existing minimal
privacy limits and link to authorized before/after details, reason, and responsible
person in the application. Require acknowledgement only when the requested unpaid
amount increases; other corrections remain visible without requiring a response.

Acceptance example: An authorized Leave Manager corrects a request. The employee
receives minimal email and in-app notifications and can open an authorized view of
the before/after details, actor, and reason. An increase in requested unpaid leave
requires acknowledgement before final approval; a correction without that increase
does not require a response. Notification payloads do not disclose correction notes.

See [ADR-0054](./architecture/decisions/0054-administrative-correction-notifications.md).

The notification bell, its unread count, and the inbox show only the active NGO's
notifications. Switching NGOs loads the selected NGO's inbox. Opening a notification
rechecks active membership and request permissions.

The NGO selector shows a per-NGO unread notification count only for NGOs where the
user has active membership. It exposes counts, not notification details; selecting
an NGO loads that NGO's authorized inbox. Treat these counts as an explicitly scoped
cross-NGO summary, not permission to retrieve another NGO's notification details.

Acceptance example: A user with active memberships in NGOs A and B has two unread
notifications in A and three in B. While A is active, the bell shows two and the
inbox contains only A's notifications. The selector shows A: 2 and B: 3 without
previews or request details. Switching to B shows its three and its authorized
inbox. After B membership becomes inactive, the user cannot retrieve B's count or
notifications; an old link still requires current membership and request access.

See [ADR-0055](./architecture/decisions/0055-ngo-scoped-notifications-and-badges.md).

Mark a notification read when the user opens it. Provide “Mark all as read” for
the user's active NGO only. Update the corresponding unread counts without
changing other NGOs' read state. Reading a notification or marking notifications
read does not approve leave or acknowledge an increased unpaid amount; those
remain explicit, separately authorized actions.

Acceptance example: A user has two unread notifications in active NGO A and three
in NGO B. Opening one A notification marks it read and reduces A's count to one.
“Mark all as read” clears the user's remaining unread count in A, leaving B's
three unchanged. Neither operation changes request approval state or satisfies
a pending unpaid-amount acknowledgement. Another user's read state is unaffected.

See [ADR-0056](./architecture/decisions/0056-notification-read-state.md).

Each policy configures an approval-reminder interval, defaulting to three calendar
days. Remind only approvers whose action is currently required. Stop reminders
for an approver when they act, and stop request reminders when the request is
withdrawn or cancelled. A reminder does not automatically approve, reject, or
reroute a request. Apply the existing notification privacy and recipient checks.

Acceptance example: Under the default interval, an unanswered request whose first
approval is currently required produces a reminder after three calendar days.
Do not remind a later approver whose action is not yet required or an approver
whose decision is already recorded. Once the current approver acts, reminders
for that action stop. Withdrawal or cancellation stops further approval reminders;
delivery never changes the request's decision or routing by itself.

See [ADR-0057](./architecture/decisions/0057-approval-reminder-interval.md).

Escalate an unanswered required approval by notifying an authorized Leave Manager
after seven calendar days without action, configurable per policy. Keep the
request assigned to its current approver unless an actor with existing rerouting
permission explicitly changes the assignment with a recorded reason. Escalation
does not approve or reject the request or grant new rerouting authority.

Acceptance example: A required approval remains unanswered for seven calendar
days under the default policy. Notify the authorized Leave Manager through the
existing privacy-preserving notification flow. The assigned approver and request
decision remain unchanged. A permitted reroute records its actor and reason;
an escalation recipient without rerouting permission cannot change the assignment.

See [ADR-0058](./architecture/decisions/0058-unanswered-approval-escalation.md).

Each policy chooses no carry-over, carry-over of all unused eligible entitlement,
or carry-over up to a configured limit between entitlement periods. It also
specifies whether carried-over entitlement expires and, if so, when. Apply the
existing inclusive-expiry and earliest-expiry allocation rules to carried-over
entitlement. Limits expressed in days must respect employee schedules and the
existing canonical-minute rules, not assume a universal eight-hour day.

Acceptance example: Given 600 unused eligible minutes at the period boundary,
no carry-over transfers zero, all-unused carry-over transfers 600, and a
480-minute carry-over limit transfers 480. If the carried portion expires on
31 March, it may fund eligible leave on that date but not 1 April. A policy with
no carry-over expiry does not introduce an expiry merely because a period ends.
Carry-over must preserve ledger history without duplicating entitlement.

For expiry entry, offer Does not expire or Expires after a configured number of
months from the new period start. Show the calculated inclusive last usable date:
three months from 1 January gives 31 March; from 1 July gives 30 September. These
are illustrative, not defaults. Existing expiry is never extended by repeated
carry-over. See [ADR-0085](./architecture/decisions/0085-period-relative-carry-over-expiry.md);
[ADR-0089](./architecture/decisions/0089-carry-over-month-boundary-expiry.md)
resolves month-end and leap-day arithmetic. Add the configured calendar months
once from the actual period start. If the matching day exists in the destination
month, use the preceding day; otherwise use that month's last day directly.

Acceptance example: One month from 15 January 2026 is usable through 14 February;
from 31 January 2026 through 28 February; from 31 January 2028 through 29 February.
Twelve months from 29 February 2028 is usable through 28 February 2029. The portion
is ineligible on the following day. If an existing portion already expires earlier,
retain that earlier date.

Convert carry-over limits expressed in days using the employee's configured
standard working-day duration effective at rollover. Save that conversion and its
effective schedule context in the audit record. Later schedule changes do not
rewrite the carried amount. Pending rollover reservations are addressed below.
See [ADR-0028](./architecture/decisions/0028-policy-carry-over-options.md).

Each policy also chooses once-only or repeated carry-over. Once-only means a
carried portion cannot transfer into another entitlement period. Repeated
carry-over permits another transfer, subject to eligibility and the policy's
carry-over limit. In either mode, an existing expiry date remains unchanged;
rolling over never extends it.

Acceptance example: At a later period boundary, 120 eligible unused minutes
remain from an earlier carry-over. Under once-only, those minutes cannot transfer
again. Under repeated carry-over with sufficient remaining carry-over capacity,
they may transfer again. If the portion already expires on 31 March, that date
remains 31 March after the transfer; the new period does not restart its validity.
Repeated transfer must not bypass the policy's carry-over limit.

See [ADR-0029](./architecture/decisions/0029-repeated-carry-over.md).

Unused entitlement that cannot carry over expires at the period boundary. This
includes amounts excluded because carry-over is disabled, the limit is exceeded,
or further transfer is prohibited. Record expiry as an auditable ledger entry,
preserving prior history, and explain the amount and reason in the employee's
balance history. Do not automatically pay it out or move it to another leave type.

Acceptance example: At rollover, 600 unused eligible minutes face a 480-minute
carry-over limit. Carry over 480 and record expiry of the remaining 120 with the
reason that the limit was exceeded. The employee's balance history explains both
amounts. If carry-over is disabled, all 600 expire; if a previously carried portion
is barred from further transfer, that excluded unused portion expires. These
events create no automatic payout or transfer to another leave type. Retrying
rollover does not duplicate either carry-over or expiry entries.

These examples concern unused entitlement available for rollover assessment;
pending requests follow the reservation rule below.
See [ADR-0030](./architecture/decisions/0030-non-carried-entitlement-expiry.md).

A reservation does not bypass carry-over limits or extend entitlement expiry.
Pending requests for the new period must be funded by entitlement valid on their
leave dates. If rollover leaves a shortfall, retain the request's pending lifecycle
state and flag it for the existing override/unpaid-leave process; do not silently
approve, reject, or cancel it.

Show the employee a clear warning stating the exact shortfall that will be
requested as unpaid leave, using the request's schedule-aware display units and
canonical minutes. Show the funded and unpaid-requested portions separately, for
example: “2 hours will be requested as unpaid leave.” This is a proposed allocation
awaiting the existing decision process, not already-approved unpaid leave. Include
the warning in the request calculation when the shortfall is known and update it
on the pending request if rollover changes funding. Authorized approvers must see
the same shortfall through the existing override review.

Acceptance example: A pending new-period request needs 480 minutes, but after
carry-over limits and expiry only 360 eligible minutes can fund its leave dates.
Keep its pending lifecycle state and flag the 120-minute shortfall for the existing
override/unpaid process. The employee sees 360 funded minutes and a warning that
2 hours will be requested as unpaid leave. The approver sees the same allocation;
the reservation neither preserves invalid entitlement nor records automatic final
consumption. Any authorized alternative allocation updates the displayed amounts.

See [ADR-0031](./architecture/decisions/0031-pending-request-rollover-shortfalls.md).

Protect existing reservations: a newly submitted request cannot take entitlement
allocated to an existing request, even when its leave dates are earlier. Assess
the new request using remaining eligible entitlement and attach any resulting
shortfall to that new request. Expected accrual, expiry, and carry-over limits
must be included in the original projection; crossing a period boundary alone
must not cause a surprise increase in requested unpaid leave.

If an authorized balance correction, entitlement change, or employment update
increases the unpaid amount on an existing pending request, the person making
the change must provide an employee-visible explanation. Show who changed it,
why, and the previous and revised unpaid amounts. Require employee acknowledgement
of the revised amount before final approval, preserving the explanation and
acknowledgement in audit history. Scheduled processing must carry through the
explanation from the underlying authorized change. This does not let a new request
silently displace an existing reservation or treat a funding change as approved.

Keep this response in the existing request: notify the employee and show Your
response is needed on My Leave; show Waiting for employee acknowledgement to the
approver. After acknowledgement, continue the remaining approval workflow without
treating the response as approval. Unchanged or decreased unpaid amounts do not
require renewed acknowledgement. No separate response workspace is needed.

Acceptance examples:

- An existing future request reserves 240 of 480 eligible minutes. A new request
  for earlier leave needs 360 minutes. Preserve the original 240-minute reservation;
  the new request has 240 funded minutes and a 120-minute shortfall, handled by
  the existing override/unpaid rules.
- An authorized correction reduces funding for a pending request from 480 to
  360 minutes, changing its requested unpaid amount from zero to 120. The employee
  sees the actor, explanation, and both amounts. Final approval is blocked until
  the employee acknowledges the revised amount; acknowledgement alone does not
  replace required approvals. Preserve prior decisions and the change history.

See [ADR-0032](./architecture/decisions/0032-protected-reservations-and-explained-changes.md).

Each policy may set a maximum accumulated balance or leave it uncapped. This cap
is separate from its carry-over limit. Scheduled accrual grants only the amount
that fits below the cap; record any excess as not granted, with an explanation in
the balance history. Applying the cap does not remove existing entitlement.

Acceptance example: With a configured cap of 2,400 minutes and an accumulated
balance of 2,280 minutes, a scheduled 240-minute accrual grants 120 minutes and
records the other 120 as not granted because of the cap. At or above the cap, grant
zero and explain the excluded scheduled amount without reducing the existing
balance. An uncapped policy grants the full otherwise eligible scheduled amount.

Reservations against future accrual are not current accumulated entitlement.
Reservations against already-earned entitlement remain part of the accumulated
balance when measuring the cap. Final approval converts those reservations to
consumption, reducing that balance and creating room for later scheduled accrual.
Withdrawing a pending request releases its reservation without changing the
accumulated balance or creating room under the cap.
See [ADR-0033](./architecture/decisions/0033-optional-accumulated-balance-cap.md).

When the accumulated balance drops below its cap, normal accrual resumes on the
next scheduled effective date, granting only what fits. The balance reduction
does not trigger an immediate grant. Amounts previously excluded because of the
cap are not automatically restored.

Acceptance example: A capped policy excludes a scheduled 240-minute grant because
the balance is already at its 2,400-minute cap. The balance later drops to 2,100.
No grant occurs merely because it dropped. On the next scheduled date, the normal
240-minute grant produces a 2,340-minute balance; the earlier excluded 240 is not
added. If only 120 minutes fit at that date, grant 120 and explain the new excluded
amount under the existing cap rule.

See [ADR-0034](./architecture/decisions/0034-accrual-resumption-after-cap.md).

Allocate reservations from entitlement valid on each requested leave date, not
automatically from today's balance. A year-3 request may reserve projected year-3
entitlement. Year-1 or year-2 entitlement may contribute only when permitted
carry-over keeps it valid on the year-3 leave dates. Advance submission cannot
preserve expired entitlement or bypass carry-over limits. A reservation against
future accrual is not current accumulated entitlement and does not consume today's
balance merely because the request was submitted today. Continue protecting
existing valid reservations from displacement by new requests.

Each policy configures a maximum advance-booking horizon. Validate requested leave
dates against that horizon at submission; reject dates beyond it with a clear
explanation. Projected funding alone does not make a request within the permitted
booking window. The MVP default horizon is 12 months ahead of submission,
configurable per policy. Every requested leave date must fall within that window;
an in-window start date does not permit an out-of-window end date. The booking
horizon does not restrict otherwise valid carry-over.

Acceptance examples:

- A request for year 3 cannot use year-1 entitlement that expires before its leave
  dates, even if submitted in year 1. Projected year-3 accrual and permitted,
  still-valid carry-over can fund it under the existing allocation rules.
- A 60-day year-3 request is funded only if 60 eligible days are available under
  its policy, schedules, expiry, carry-over limits, and existing reservations.
  Early submission does not create that entitlement.
- A request whose dates exceed the policy's configured booking horizon cannot be
  submitted even when its projected balance would be sufficient. The employee sees
  the permitted booking limit and which requested dates exceed it.

See [ADR-0035](./architecture/decisions/0035-leave-date-funding-and-booking-horizon.md).

Acceptance example: With the default horizon, a request submitted on 14 September
2026 may include eligible leave dates through 14 September 2027, subject to all
other rules. A request ending on 15 September 2027 cannot be submitted, even when
it starts within the window and has sufficient projected funding. A policy may
configure a different horizon; permitted carry-over remains subject to its own
validity and limits rather than being shortened by the booking window.

See [ADR-0036](./architecture/decisions/0036-default-twelve-month-booking-horizon.md).

Acceptance example: An employee has 2,400 earned minutes at a 2,400-minute cap.
A pending request reserves 600 of those minutes. All 2,400 still count toward the
cap, so scheduled accrual cannot add entitlement. Final approval converts the
600-minute reservation to consumption, leaving 1,800 accumulated minutes and room
for later scheduled accrual. Withdrawing instead releases the reservation and
leaves 2,400 accumulated minutes. A reservation against future accrual does not
change today's accumulated balance.

See [ADR-0037](./architecture/decisions/0037-earned-reservations-count-toward-cap.md).

When approved leave is cancelled, recalculate affected capped accrual as if that
request had never consumed entitlement, preserving other actual leave and
transactions. Restore the cancelled consumption and reverse only the extra accrual
enabled by that booking. Use new auditable correction entries, never rewritten
history, and preserve original entitlement expiry dates.

Before cancellation, show the employee the restored amount, any extra-accrual
reversal, applicable expiry effects, and resulting balance. If the correction
affects another pending request's unpaid amount, apply the existing explanation
and renewed-acknowledgement rules. If extra entitlement has already been spent,
flag the resulting deficit for authorized review; do not silently convert
previously approved leave to unpaid leave. This review concerns the deficit and
does not introduce another approval requirement for cancellation itself.

Acceptance example (all day amounts use the employee's schedule): At a 20-day cap,
approval of five future days reduces the balance to 15. Two days then accrue and
four other days are taken, leaving 13. Cancelling the original five-day request
restores five and reverses the two days that would not have accrued without that
booking, yielding 16. Preserve the four days actually taken and all original ledger
entries. Show the +5/-2/result-16 calculation before cancellation. A retry creates
no duplicate restoration or accrual reversal.

See [ADR-0038](./architecture/decisions/0038-cancellation-accrual-recalculation.md).

A Leave Manager with `leave.balance.adjust` within the authorized NGO/resource
scope reviews deficits resulting from cancellation recalculation. Require a reason
for the review outcome and explain that outcome to the employee. Any additional
paid entitlement requires an explicit audited grant; review alone does not create
entitlement. Previously approved leave must never be automatically changed to
unpaid leave as a result of this review.

Acceptance example: Cancellation recalculation identifies spent extra entitlement
and flags a deficit. An in-scope Leave Manager with balance-adjustment permission
records an outcome with a mandatory reason, visible in the employee's explanation
and audit history. An actor without that permission or outside the request's
authorized scope cannot resolve the review, and an outcome without a reason is
rejected. If additional paid entitlement is awarded, record a separate explicit
audited grant. The affected previously approved leave is not automatically
converted to unpaid leave.

See [ADR-0039](./architecture/decisions/0039-cancellation-deficit-review.md).

Acceptance example: A five-day carry-over limit converts to 2,400 minutes (40
hours) for an employee whose configured standard day at rollover is eight hours,
and 1,800 minutes (30 hours) for an employee whose configured standard day is six
hours. Carry over no more than the unused eligible amount or that converted limit.
Record the day limit, standard-day duration, effective schedule, and minute limit.
A later change to either employee's schedule does not recalculate that rollover.

See [ADR-0040](./architecture/decisions/0040-schedule-based-carry-over-day-limits.md).

Employee schedules include an explicitly configured standard-day duration for
entitlement conversions, including when scheduled working days have different
lengths. This conversion value does not replace the hours scheduled on a requested
leave date. Actual full-day leave consumes that date's scheduled working time;
half-day leave remains exactly 50% of it, and hourly leave retains its existing
increment and schedule rules.

Acceptance example: An employee has an eight-hour standard day for conversions
and six working hours scheduled on Friday. A five-day carry-over limit converts
to 40 hours, while taking that Friday off consumes six hours; a half-day Friday
consumes three hours. Do not use the eight-hour conversion value to charge eight
hours for the Friday absence. Preserve the effective schedule and calculation
snapshots under the existing historical-integrity rules.

See [ADR-0041](./architecture/decisions/0041-standard-day-for-variable-schedules.md).

Each policy chooses calendar-year entitlement periods or employee
employment-anniversary-year periods. A calendar-year period runs from 1 January
through 31 December. An employment-anniversary period begins on the employee's
employment anniversary and ends the day before the next anniversary. Accrual
frequency is separate: either period basis can use the supported monthly or annual
upfront grant schedule.

Acceptance example: For an employee who started on 1 July, an anniversary-year
policy has a period of 1 July through 30 June, while a calendar-year policy uses
1 January through 31 December. Either policy can grant monthly or annually under
its configured schedule. Use these period boundaries for applicable proration and
carry-over rules rather than inferring the period from accrual frequency.

See [ADR-0042](./architecture/decisions/0042-entitlement-period-basis.md).

Annual upfront grants occur on the first day of the entitlement period: 1 January
for calendar-year policies or the employee's anniversary for anniversary-year
policies. For an employee joining partway through a calendar-year period, grant
on the employment start date using the policy's agreed proration rule. This
replaces the earlier freely configured annual grant date; monthly and manual-only
grant schedules retain their existing rules.

Acceptance example: A calendar-year annual-upfront policy grants on 1 January.
An employee joining on 1 July receives a joining grant effective 1 July, calculated
using the policy's no-proration or calendar-day-proration setting and final-grant
rounding rule. The next annual grant is due on 1 January. Under an anniversary-year
policy, an employee starting on 1 July receives the annual grant at the start of
their 1 July–30 June period. Repeated calculation does not double-count the grant.

See [ADR-0043](./architecture/decisions/0043-annual-grants-at-period-start.md).

For employees whose employment anniversary is 29 February, use 28 February in
non-leap years and return to 29 February in leap years. That resolved anniversary
starts the new anniversary-year entitlement period and triggers any annual upfront
grant. Preserve the original employment start date; the fallback does not change
future anniversary calculations. The prior period ends the day before the new
period begins, without overlapping or missing dates.

Acceptance example: An employee who started on 29 February 2024 begins their next
anniversary period on 28 February 2025. Their 2027 period runs from 28 February
2027 through 28 February 2028; the next starts on 29 February 2028. An annual
upfront policy grants on each resolved period start, once per period.

See [ADR-0044](./architecture/decisions/0044-leap-day-employment-anniversaries.md).

Assess future-request availability on each requested leave date using accrual
earned by that date, excluding entitlement that expires before that date, and
accounting for amounts already reserved by other requests. Carry forward the
candidate request's earlier-date consumption within the projection so the same
entitlement cannot fund multiple days. A multi-date request must remain affordable
throughout its requested dates, not only on its first date. Any shortfall follows
the existing insufficient-balance override and unpaid-allocation rules in §9;
later accrual cannot retrospectively fund an earlier shortfall.

Acceptance examples (all amounts in canonical minutes):

- Accrual boundary: Given 240 available minutes, no other reservations or expiry,
  and 240 minutes accruing between two requested workdays, a request using 240
  minutes on each day is fully funded. A request using 480 on the first day has
  a 240-minute shortfall on that day; the later accrual does not remove it.
- Expiry boundary: Given 480 minutes available on the first requested day, all
  remaining entitlement expiring before the second day, and no intervening
  accrual or other reservations, a 240-minute request on each day is funded on
  the first day but has a 240-minute shortfall on the second. Initial availability
  alone must not classify the entire request as funded.
- Competing reservations: Given 480 projected minutes and another request already
  reserving 240 from that entitlement, a candidate requesting 480 has a 240-minute
  shortfall. Both requests cannot spend the same reserved entitlement.

These examples define date-by-date availability. Proration is specified above;
accrual and expiry date boundaries are specified below. Prorated grant rounding
is defined above and does not alter request-duration rules.
See [ADR-0019](./architecture/decisions/0019-date-by-date-future-balance.md).

Within the selected leave balance, allocate from eligible entitlement in order of
earliest expiry, with non-expiring entitlement last. Apply eligibility and the
date-by-date availability rules before allocation; expired, not-yet-earned, or
already-reserved entitlement cannot become available merely because of its expiry
priority. This ordering does not authorize use of another leave type; that still
requires the agreed override and explicit allocation rules in §9.

Acceptance example: On a requested leave date, the selected balance contains 120
eligible minutes expiring first, 240 eligible minutes expiring later, and 240
eligible non-expiring minutes, with no competing reservations. A 300-minute
request allocates 120 from the first portion and 180 from the later-expiring
portion, leaving 60 later-expiring and all 240 non-expiring minutes. If only 120
eligible minutes remain in the selected balance, a 180-minute request has a
60-minute shortfall even when another leave type has available entitlement; the
system must not silently take that other balance without the agreed override.

Tie-breaking between portions with the same expiry remains an implementation
detail to make deterministic before the allocation story passes readiness.
See [ADR-0020](./architecture/decisions/0020-earliest-expiry-entitlement-allocation.md).

An entitlement's expiry date is its last usable leave date. It may fund leave
taken on that date and is unavailable for leave taken from the following date.
Eligibility depends on when leave is taken, not when the request is submitted;
submitting early does not extend entitlement validity.

Acceptance example: Entitlement expiring on 31 December can fund eligible leave
taken on 31 December, subject to availability and existing reservations. It cannot
fund leave taken on 1 January, even if that request was submitted before
31 December. For a request spanning both dates, assess each date separately and
apply the existing shortfall rules where other eligible entitlement is insufficient.

See [ADR-0021](./architecture/decisions/0021-inclusive-entitlement-expiry-date.md).

Newly accrued entitlement is available from the start of its configured effective
date. Each policy determines its accrual schedule and effective dates. Accrual can
fund eligible leave taken on its effective date or later, subject to expiry,
existing reservations, and allocation rules; it cannot fund earlier leave.

Acceptance example: A policy credits 240 minutes effective 1 February. With no
other entitlement, reservations, or expiry affecting the example, a 240-minute
request for 1 February is funded by that accrual. A request for 31 January cannot
use it and follows the existing shortfall rules. The policy controls the effective
date; this example does not require every policy to accrue monthly or on the first.

See [ADR-0022](./architecture/decisions/0022-accrual-effective-date-availability.md).

Use the employee's configured work timezone to define leave dates and the day
boundaries for accrual availability and entitlement expiry. The viewer's or
approver's timezone does not change those dates or entitlement outcomes. Apply
start-of-effective-date accrual and inclusive expiry in that work timezone.

Acceptance example: An employee's work timezone is Africa/Johannesburg. An
approver viewing the request from America/New_York receives the same leave dates,
duration, and entitlement outcome as a viewer in Johannesburg. Accrual effective
1 February becomes available at the start of 1 February in the employee's work
timezone, regardless of the approver's local date. Entitlement expiring on
31 January cannot fund the employee's 1 February leave merely because it is still
31 January where the approver is located.

See [ADR-0023](./architecture/decisions/0023-employee-work-timezone.md).

### 7. Leave application experience

Automatically save an unfinished request as a draft while the employee fills it
in. Show a truthful “Saved” or “Not saved” indicator and provide **Close**.
Keep at most one unfinished employee application draft per employee per NGO.
Enforce employee/NGO active-draft uniqueness in the database and atomically create or
resume the existing authorized draft under
[platform ADR-0034](../../../platform/docs/architecture/decisions/0034-atomic-single-active-draft-creation.md).
Two initial starts return the same draft; competing creation values never overwrite
it. Existing revision checks protect subsequent edits. Old create retries follow their
recorded outcome and cannot resurrect a closed draft or overwrite a later new one.

Apply [platform ADR-0033](../../../platform/docs/architecture/decisions/0033-draft-lifecycle-and-late-save-protection.md):
autosaves check revision and editability; submitted/discarded drafts cannot be recreated
by stale writes or old create retries. Submission, reservations and draft closure commit
with existing audit/outbox effects in one local transaction. Conflicting tabs stop
saving, retain local edits where practical and show **This draft has already been
submitted.** with **View request**, or **This draft was discarded elsewhere.** with
**Back to My Leave**. Recheck access before showing current details. New draft creation
is explicit, never automatic conversion of unsaved text.

Each autosave carries its starting revision. Atomically reject stale writes, pause
autosaving in the conflicting tab and show **This draft changed elsewhere. Your latest
changes haven’t been saved.** Offer **Review saved draft** after rechecking access;
retain local edits while the user decides, without promising persistence on closure.
No automatic merging or collaborative editing is required. Serialize and coalesce
same-tab saves; apply acknowledged revisions to subsequent writes, preserve newer
typing, and show Saved only for acknowledged edits. Resolve uncertain saves through
the existing operation-identity contract before another save. See
[ADR-0118](./architecture/decisions/0118-revision-safe-draft-autosaving.md).

Draft eligibility and preservation (agreed 2026-09-23): employees with current or
future employment may prepare drafts once explicitly granted Leave access. Ended
employment preserves the draft with read-only access where still authorized; revoked
membership denies access. On rehire, resume the retained draft with refreshed context
and explain invalid inputs. Passing the selected leave end date does not discard or
delete a draft. Reopening preserves entered details and rechecks current backdating
rules and permissions; require date changes before submission only where those rules
require them. Retention/cleanup is a separate explicit policy, not inferred from dates.

On My Leave, **Apply for leave** resumes that draft, with a small unfinished-application
note beside the action. Do not add a Drafts section or notification badge.
Within the form, **Discard draft** requires confirmation before deleting it.
Agreed 2026-09-24: confirmed discard removes the editable form contents, with no
restore-discarded-draft UI. Keep minimal server-side lifecycle and operation evidence
to reject delayed writes/retries; do not retain notes or whole form snapshots in
that evidence. E1 has no automatic expiry of active drafts or compact replay evidence.
Backup retention and any future safe cleanup policy are separate owned contracts.
Submitted requests are separate and may be multiple. Drafts reserve no entitlement until
submission. Submission rechecks all applicable rules; a saved draft is not a
validated or approved request. A failed save must not be presented as successful.
Agreed 2026-09-24: autosave also preserves bounded incomplete typed input, including
partial dates, missing selections and reversed ranges. Reopening after an acknowledged
save restores that input without silently filling defaults, swapping dates or erasing
invalid text. Saved confirms persistence, not request validity. Calculate only when
required inputs are valid; retain input-format context so locale changes cannot silently
reinterpret entered dates/durations. Exact schemas and bounds remain contract work.

Acceptance example: An employee enters a request and sees “Saved” after its draft
is persisted. They can use Close and resume it through Apply for leave in My Leave in the same
NGO. The draft does not reserve balance. If saving fails, show “Not saved” and
preserve entered data under the existing failure-recovery requirement. On later
submission, recheck eligibility, overlap, policy, and balance even if the draft's
earlier preview passed.

See [ADR-0067](./architecture/decisions/0067-automatic-draft-saving.md), partially
superseded by [ADR-0075](./architecture/decisions/0075-single-draft-and-safe-close.md).
Close immediately when saved; finish an in-progress save before closing. If saving
fails, offer Retry, Keep editing, or Discard unsaved changes, retaining previously
saved content. Apply these rules to desktop Escape and mobile Back. Confirm before
discarding an approver’s unsent comment.

When switching NGOs while editing a request, save the draft in its original NGO
before switching, then open My Leave in the selected NGO. Never transfer the draft
or its unsaved data into another NGO. If saving fails, keep the user on the request
and offer **Retry**, **Stay**, or **Discard unsaved changes and switch**. Discarding
unsaved changes leaves any previously saved draft intact in its original NGO.

Acceptance example: While editing a draft in NGO A, the employee selects NGO B.
Persist the edits in A before switching and opening B's My Leave; the draft remains
in A. If saving fails, remain on A's request until the user retries, stays, or
explicitly discards unsaved changes and switches. The discard option does not
delete the last saved draft, and no A request data appears in B's workspace.

See [ADR-0068](./architecture/decisions/0068-ngo-switch-while-editing.md).

Before submission, show a concise summary of leave type, dates, duration, and the
paid/unpaid split, with “Approval required” where applicable rather than approver
names. Keep workflow details available on demand. Show the active NGO in the
application header instead of repeating it in the summary; show an NGO switcher
only for users with multiple active NGO memberships. Requests remain bound to
their NGO regardless of presentation. If any amount is requested as
unpaid leave in an employee’s own application, require their explicit acknowledgement
of that exact amount before submission. Authorized on-behalf applications use the
post-submission employee-response handoff below. Without an unpaid amount, a single **Submit request** action suffices.
Acknowledgement is not approval of the request or authorization of an override.

Acceptance example: A request summary shows 480 minutes requested, with 360 paid
and 120 requested unpaid. Submission requires acknowledgement that 120 minutes
(two hours) are requested as unpaid leave. Acknowledging a different amount does
not satisfy this check. If submission revalidation changes the unpaid amount,
refresh the summary and require acknowledgement of the revised amount before
submitting. A fully funded request needs only Submit request after the summary,
subject to existing validation and required explanation rules.

See [ADR-0069](./architecture/decisions/0069-submission-summary-and-unpaid-acknowledgement.md).

For an initial on-behalf request containing unpaid leave, allow the authorized
manager to submit with the required reason and allocation. Notify the employee
and show Your response is needed on My Leave, linked to this submitted request.
Only that employee may acknowledge its current exact unpaid amount; the manager’s
on-behalf permission cannot stand in for the employee’s response. Preserve any
employee-owned draft unchanged. Keep eligible withdrawal available under existing
pending-request rules.

Final approval remains blocked until the response and all other finalization checks
pass. Intermediate steps may proceed when otherwise authorized. The submitting
approver’s own step can be approved even when it is the sole step, but the overall
request and paid reservation remain pending until the employee responds. When all
conditions are met, finalize with one consumption; do not repeat an already valid
approval solely because acknowledgement arrives later.

Acceptance example: Sofia submits five days for Ana with three paid and two unpaid,
with a reason. Ana’s separate saved draft is unchanged. Ana opens Your response is
needed and acknowledges the current two unpaid days. If Sofia owns the sole approval
step, that step is recorded on submission but the request is not Approved and the
reservation is not consumed until Ana responds and remaining checks pass. If Sofia
is not an assigned approver, her submission does not satisfy an approval step.

Acceptance example: Deny Sofia an attempt to acknowledge as Ana. If an authorized,
explained correction changes the unpaid amount from two to three before Ana’s
response, show the revised allocation and explanation; an acknowledgement of two
days must not satisfy the current three-day requirement. Audit the submission,
correction, employee response and approval separately; retries do not duplicate
requests or consumption.

See [ADR-0088](./architecture/decisions/0088-employee-acknowledgement-for-on-behalf-unpaid-leave.md),
which refines ADR-0069 only for on-behalf acknowledgement timing.


After confirmed successful submission, close the form and return to My Leave,
preserving previous list context and scroll position. Show a brief “Request submitted”
confirmation with an optional View request link, update the request list with dates
and authoritative status, and remove the submitted draft indicator. Do not prominently display a reference number
or next-approver name in this confirmation. Keep stable internal identifiers for
integrity and support, and keep approval history available on demand. When someone
else must act, “Awaiting approval” is sufficient; when the employee must act, state
the required action clearly. Show Approved immediately when authorized automatic
decisions complete approval. Routine progress relies on existing reminders and
escalation, without requiring employees to chase approvers.

If a connection failure leaves submission uncertain, check whether it succeeded
before offering a retry. Retrying must not create a duplicate request or reservation.

Acceptance example: Confirmed submission returns to My Leave without an extra close
action. The request appears with its dates and Awaiting approval,
without a prominent reference number or next-approver name. Its history remains
accessible. An immediately approved request shows Approved instead. A later unpaid
increase clearly asks the employee for acknowledgement. If the submission response
is lost after success, recovery finds the existing request rather than creating
a second request or reservation.

See [ADR-0070](./architecture/decisions/0070-simple-submission-confirmation.md),
partially superseded by [ADR-0087](./architecture/decisions/0087-return-to-my-leave-after-submission.md).

Acceptance example: A single-NGO employee sees the active NGO in the application
header, with no NGO switcher. Their submission summary shows type, dates, duration,
paid/unpaid split, and applicable approval wording without repeating the NGO or
listing approver names. A multi-NGO employee can switch using the header control;
the summary stays concise and the request remains tied to its original NGO under
the existing save-before-switch rule. Workflow details remain available on demand.

See [ADR-0071](./architecture/decisions/0071-concise-summary-and-header-ngo-context.md).

The request page contains:

- Active NGO and employee schedule context
- Leave-type selector with plain-language policy summary
- Full-day, half-day, or hourly selection
- Accessible date controls and duration selection, without exact start/end times
- Optional employee note
- Secure attachment uploader where permitted or required
- Real-time duration breakdown
- Current, reserved, projected, and post-request balance widget
- Warnings and consequences requiring acknowledgement
- Truthful automatic draft-saving status, Close and Submit request actions

Dates remain visible even when non-working; the calculation explains why weekends,
holidays, breaks, or unscheduled time do not consume leave.

Validation covers:

- Invalid or zero-working-time ranges
- Overlap and duplicate requests
- Inactive employment
- Policy eligibility, notice, horizon, and backdating
- Attachment requirements and enabled content-safety state
- Available/projected balance and override eligibility
- Concurrent requests consuming the same projected balance

### 8. Hourly and half-day leave

- Hourly leave is calculated against the employee's effective schedule and breaks.
- Hourly leave is requested in 0.5 hour (30-minute) increments.
  This is an input increment, not a rounding rule for accrued entitlement or the
  ledger balance. Preserve remaining minutes and validate against actual eligible
  entitlement. For example, 137 available minutes can fund a 120-minute hourly
  request, leaving 17 minutes. Full/half days retain schedule-based durations:
  half of a 450-minute working day is 225 minutes, without rounding to 30 minutes.
  Final standalone prorated grants use the fixed whole-minute floor under ADR-0103.
- Half-day leave consumes exactly 50% of the employee's configured scheduled hours
  for that day; an 8-hour configured day therefore consumes 4 hours.
- Canonical consumption is stored in minutes together with the schedule and policy
  calculation snapshots.
- The UI displays the policy's preferred unit and equivalent amount where helpful.
- A global fixed assumption such as eight hours per day is not used.

### 9. Insufficient-balance override

When policy permits it, an employee may submit a request that exceeds projected
availability. The request is marked **Balance override required**.

The authorized supervisor must see:

- Available and projected balance
- Requested amount and deficit
- Relevant pending requests
- Default consequence: the deficit is unpaid leave
- A mandatory reason field

The override decision and its balance consequence are recorded separately from the
ordinary approval decision. An authorized exception can allocate the request across
multiple funding lines, for example existing sick leave, a discretionary paid-leave
grant, annual leave, and unpaid leave. This supports exceptional long-term illness
without rewriting the employee's ordinary policy entitlement. Each line records its
source, duration, authorizer, and reason. Rejection or cancellation reverses
reservations and ledger effects according to policy.

### 10. Configurable approval workflows

For two-step policies, show the employee’s supervisor as Step 1 and require an
explicit searchable final-approver selection for Step 2. Offer eligible people in
the current NGO, with name/team/job-title context where needed; never assume the
CEO. Explain when no eligible person is available, linking authorized access
administrators to access management. Assignment does not itself grant additional
permissions; dated temporary appointment remains its separate authorized flow.


The number of required approval steps is configurable per NGO and leave policy,
with at least one step. One organisation may require one approval and another two.
MVP user-facing presets are one-tier and two-tier workflows; zero-step policies
are not supported.

If no eligible approval route can be resolved, preserve the employee's draft and
block submission until the route is configured. Explain Your approval route needs
to be set up and direct the employee to the Leave Manager; claim Draft saved only
after confirmed persistence. Flag the configuration issue for an authorized manager.
Do not silently skip approval or allow the employee to select an unauthorized
alternative. This concerns a missing/invalid route, not the applicant's own coverage
gap (which permits submission) or an absence handled through the configured fallback
or authorized temporary assignment.

For a new client, provide an editable starter approval configuration with one
employee-supervisor step, self-approval disabled, temporary approvers available,
reminders after three calendar days and escalation after seven calendar days.
The second step and directional absence fallback are optional, not enabled by
default. Setup assists supervisor assignment and flags missing or invalid approval
routes. Require client confirmation of entitlement, schedules, holiday calendars,
and organization-specific rules before activating the starter policy; do not
assume a universal country or NGO allowance.

For two-step workflows, all configured steps remain required by default. An explicit
optional absence policy allows the configured final approver (for example, CEO) to
approve alone when the supervisor is absent. The reverse is not allowed: when the
final approver is absent, appoint a temporary final approver rather than accepting
the supervisor's decision alone. Use recorded applicable absence, not slow response.
Show an omitted step as **Not required under absence policy**, retain its policy
basis and actual decision-maker, and require at least one valid approval. Existing
self-approval, authorization, and other finalization conditions still apply.
If both are absent, temporary approval remains required. See
[ADR-0080](./architecture/decisions/0080-directional-absence-approval-policy.md).
Evaluate approver absence when approval is needed, not during the applicant's
requested leave dates. The applicant's own coverage check still concerns their
absence period. Preserve the snapshotted policy while recording execution of its
absence and return conditions. See
[ADR-0081](./architecture/decisions/0081-absence-fallback-timing-and-return.md).

The temporary approver or final approver may leave a nonurgent request pending to
await the supervisor's return, optionally explaining this in a comment under normal
visibility rules. Keep the request visible and normal reminders/escalation running.
Under the final-approver fallback, restore the outstanding supervisor step when
they return if no final decision has been made; record the transition. A completed
final-approver decision remains valid. Temporary assignments follow their existing
expiry return process. Waiting does not implicitly pause timers.

When both configured approvers are absent, the temporary final approver may decide
alone under this policy if the appointment explicitly includes **May approve
without the supervisor's step when the supervisor is absent**. This is a scoped
temporary responsibility, not an implicit permanent permission. Preserve normal
self-approval and other finalization checks; a second substitute is not required
solely to fill the omitted supervisor step.

Recognize this policy-authorized fallback as valid coverage for the supervisor's
responsibilities when the final approver, or explicitly authorized temporary final
approver, is available to handle them alone. Do not require a duplicate temporary
supervisor for those responsibilities. Other responsibilities outside this fallback
still require eligible cover or an explained exception. Coverage checks must assess
the responsibilities and applicable periods rather than only the existence of a
named temporary-supervisor assignment.

Approvers can be resolved from:

- Direct supervisor assignment
- Configured person
- Configured role or assignment
- Acting/delegated approver
- Fallback approver

The resolved workflow is snapshotted on submission. Later organization changes do
not silently replace an in-flight workflow without an explicit reroute action.

#### Approval cover and planned absence

Allow leave submission when the applicant's approval responsibilities lack temporary
coverage; make the gap visible. Before final approval, require eligible coverage
throughout the absence for those responsibilities, including new requests that may
arrive. Employees without approval responsibilities have no such coverage condition.
The employee need not have permission to appoint a substitute; an authorized actor
arranges the assignment. Existing submission validation and approval-route rules
still apply.

An authorized Leave Manager may record an explicit coverage exception, with a
mandatory reason, for unexpected sickness, emergencies, or other justified cases.
Keep the unresolved gap prominent; the exception does not claim coverage exists,
grant approval authority, or satisfy other approval requirements. Do not falsely
delay or alter the recorded dates of an actual absence because coverage is missing.
This condition applies to final approval, including any path that would otherwise
complete approval automatically. See
[ADR-0078](./architecture/decisions/0078-approval-coverage-before-final-approval.md).

If arranged coverage becomes unavailable after the employee's leave has been
approved, retain that approval. Flag **Replacement approver needed** to authorized
Leave Managers and require reassignment under existing permissions. Do not
automatically cancel the employee's leave or extend another person's authority.

Include effective-dated delegation and authorized reassignment in MVP. An authorized
Leave Manager can appoint any active member of the same NGO for specified approval
responsibilities and dates, including second/final approval. The appointment itself
grants that scoped temporary authority; no permanent Approver role is required.
Record appointing actor, reason, responsibilities, and dates. Apply approved cover
to work requiring action during the covered period. Check active NGO membership,
known absence, and self-approval conflicts. Grant no separate sensitive-document
access, permanent approval role, or unrelated approval/editing powers. Authority
expires with the assignment and cannot be used after membership becomes inactive.
See [ADR-0079](./architecture/decisions/0079-temporary-appointment-grants-scoped-authority.md).

Notify the temporary approver by email and in-app on appointment, changes, and
early termination, with the original approver, assignment dates, and a link to
Approvals. Do not include sensitive request details. No additional acceptance step
is required in MVP; the appointing manager confirms availability beforehand and the
assignment takes effect on its start date. Use the shared notification capability.

Allow authorized early termination with a required reason and a preview of
outstanding requests and their proposed reassignment. Return them to the eligible,
available original approver or appoint another person. End temporary authority on
confirmation even if no replacement is available; preserve completed approvals and
leave outstanding requests pending and flagged. Missing temporary approval coverage
remains flagged to Leave Managers throughout the original approver's absence even
when no requests are waiting. Clear it only when valid coverage is arranged or the
original approver returns eligible to act. Do not cancel already-approved leave.

Allow only one temporary approver for the same responsibilities on any given date.
Sequential assignments are valid. If dates overlap, show the conflicting assignment
and require adjusted dates or explicit authorized replacement; do not silently
choose between assignments. Retain audit and outstanding-request transfer rules.

Keep the workflow snapshot rule: changes to already assigned outstanding steps
require an explicit, permission-checked, audited reroute. Do not silently replace
an assignee when delegation dates or directory relationships change. Preserve
completed approvals. A return transfer explicitly authorized during temporary
assignment setup may execute at the agreed expiry as described below.

During temporary-approver setup, show already-waiting requests and offer
**Include these pending approvals**. Require authorized confirmation of the
selected reassignment and record its reason. Completed approvals remain unchanged.
Use **Temporary approver** in the interface. This confirms the treatment of pending
requests at setup.

Default to an explicitly authorized scheduled return: **When this assignment ends,
unfinished approvals return to [original approver].** At expiry, return outstanding
steps only after rechecking the original approver's eligibility and known continuing
absence. Retain completed approvals, record the transfer, and notify the returning
approver. If checks fail, keep the request pending and flag an authorized Leave
Manager; temporary authority must not automatically extend. An authorized extension
before expiry postpones the return. See
[ADR-0077](./architecture/decisions/0077-scheduled-return-of-temporary-approvals.md).

Flag known approved absence as a coverage concern; do not choose a substitute
automatically from the organization chart or wait seven days to flag known absence.
An authorized Leave Manager can reassign outstanding work with a recorded reason.
Support more than one Leave Manager with the separate reassignment permission so
administrative cover does not depend on a single person. If no eligible cover is
available, existing requests remain pending with a coverage issue. Never bypass or
automatically approve a currently required step outside the explicitly configured
absence policy; a policy-authorized omitted step is not an approved step. The normal seven-day escalation still applies
to unanswered approvals and grants no additional authority.

Acceptance scenarios for delivery: supervisor and final approver both have dated
delegates; the primary Leave Manager is also absent but an authorized alternate can
reroute; missing eligible cover leaves a pending request unresolved and visible;
an ineligible, absent, or self-conflicting delegate is flagged before assignment;
rerouting retains earlier approvals and records the actor and reason.

See [ADR-0076](./architecture/decisions/0076-approval-cover-and-planned-delegation.md).

#### Approval decisions

Self-approval is disabled by default and can be enabled explicitly. If one person
occupies multiple consecutive steps, configured rules determine whether redundant
steps collapse; the same person is not asked to perform an identical decision twice.

For a valid submission, automatically record an approved outcome for the submitting
person's own resolved approval step when they are authorized to perform it. This
applies to explicitly permitted self-approval and to an authorized approver
submitting on behalf of an employee with separate on-behalf permission. Never
automatically satisfy a step assigned to another person. Record the submission
actor, employee, automatic approval outcomes, and their authorization basis in the
audit history.

If these automatic decisions satisfy all currently required steps and the existing
finalization conditions (including approval coverage or an authorized exception,
and any required unpaid acknowledgement), the request immediately becomes approved
and its leave allocation is consumed exactly once. If another
person's approval remains required, the request stays in approval and the allocation
remains reserved until final approval. Automatic outcomes use the existing
`approved` step state (the accepted decision), not a new `accepted` status.

If the submitting approver owns a later step, record their authorized acceptance
immediately even while an earlier step is pending. Do not ask them to approve again
after the earlier approver accepts. Final approval means the decision that satisfies
the last outstanding required step, regardless of that step's position in the
workflow. Until then, retain the reservation and keep the request in approval.

Acceptance examples:

- With one required step assigned to the requester and self-approval enabled,
  valid submission records that step as approved, approves the request, and consumes
  the allocation exactly once. Without explicit self-approval permission, submission
  must not grant that automatic decision.
- With one required step assigned to an approver who is authorized to submit on
  behalf, their valid on-behalf submission records the approval and immediately
  consumes the allocation, with attributed audit history.
- With two required steps assigned to different people, an authorized on-behalf
  submission by the first approver records only their approval. The second step
  remains pending and the allocation remains reserved until the second approver
  approves. Approval authority without on-behalf permission cannot create the request
  on another employee's behalf.
- With two required steps and 480 minutes requested, a valid on-behalf submission
  by the authorized second approver immediately marks step two approved. Step one
  remains pending, the request remains in approval, and all 480 minutes remain
  reserved. When the first approver accepts, both steps are satisfied: approve the
  request and convert the reservation to consumption exactly once, without another
  action by the second approver. If the first approver rejects instead, reject the
  request and release the reservation; retain the second approver's earlier
  acceptance in the audit history without consuming leave.

See [ADR-0007](./architecture/decisions/0007-required-approval-and-automatic-decisions.md)
for the decision superseding zero-step workflows and
[ADR-0008](./architecture/decisions/0008-later-step-acceptance-on-submission.md)
for immediate acceptance of a submitting approver's later step.

Approvers can approve or reject with comments. Rejections require a reason.
Approval email links lead to an authenticated application screen and do not perform
an unauthenticated decision.

### 11. Request lifecycle

```text
Draft → Submitted → In approval → Approved
Submitted/In approval → Rejected
Rejected → edit same request → Submitted (resubmission)
Draft/Submitted/In approval → Withdrawn
Approved → Cancelled
```

An employee can correct and resubmit the same rejected request. Keep the same
request identifier and preserve the previously submitted details, rejection
reasons, approval decisions, and edit/resubmission history. Resubmission is an
action returning the request to the submission flow, not a separate `resubmitted`
application status or a new linked replacement request.

Resubmission validates the corrected request and starts a fresh approval cycle.
Prior decisions remain historical and do not approve the revised request; evaluate
authorized automatic decisions under the same rules as a new submission. Preserve
the earlier workflow snapshot and record the new cycle separately. Rejection has
released the earlier reservation; a valid resubmission reserves the recalculated
allocation once, then follows the ordinary approval/consumption rules.

Acceptance example: An employee's 480-minute request is rejected and its
reservation released. The employee corrects it to 240 minutes and resubmits. The
request identifier stays the same; the original 480-minute submission, rejection
reason, and decisions remain visible in its history. If another person's approval
is required, the corrected request has 240 minutes reserved and a fresh pending
approval cycle. Retrying resubmission must not create a duplicate reservation.

See [ADR-0009](./architecture/decisions/0009-resubmit-rejected-request.md).

Every transition is authorized, version-checked, idempotent, timestamped, and
audited. Approved records are not edited in place; amendment uses cancellation and
a new linked replacement request when dates or duration change. The employee or
someone with scoped permission to log leave on their behalf may perform this
correction. The new request goes through validation and approval again, including
the agreed authorized automatic-decision rules; approvals from the cancelled
request do not carry over. Approved leave
may be cancelled without another approval, immediately reversing the appropriate
reservations/consumption and notifying affected approvers.

Preserve the cancelled request, its original approved dates/duration, decisions,
and balance history. Give the replacement a new request identifier and link it to
the cancelled original. Attribute on-behalf cancellation and replacement actions
to the person performing them, with the required reason and authorization checks.

Acceptance example: An employee cancels an approved 480-minute request and submits
a linked 240-minute replacement. Reverse the original consumption once; validate
and reserve the replacement allocation under the ordinary approval rules. If
another person's approval is required, keep the replacement pending until that
approval, then consume 240 minutes once. A scoped on-behalf actor can perform the
same correction with attribution. A person who has only approval authority cannot
cancel or replace another employee's request.

See [ADR-0010](./architecture/decisions/0010-cancel-and-replace-approved-leave.md).

### 12. Attachments

- Attach files to drafts or requests according to policy.
- Use the shared FastAPI Content Service and signed direct-to-provider uploads.
- Limit files to 10 MB each, 3 files and 20 MB total per request.
- Initially accept PDF, JPEG, and PNG only, using extension checks, MIME sniffing,
  and provider metadata rather than trusting browser-declared types.
- Show upload and verification status. Preserve an extensible content-safety state,
  but do not require malware scanning for MVP.
- Permit download only after Leave-domain authorization and content safety checks.
- Keep attachment names and medical details out of broad calendar/dashboard views.
- Support configured retention and auditable disposal. The initial medical-document
  default is two years after request closure, but each NGO/jurisdiction must be able
  to override it after legal/privacy review.
- Never expose storage credentials or permanent provider URLs to clients.

For medical documents, assigned approvers without
`leave.document.sensitive.read` see only whether the required document was provided
and its verification status. Filenames, previews, and downloads require that
separate permission plus request-level document authorization. Verification status
must not include document contents or revealing diagnostic text. Apply the same
restriction to the request API: hiding filenames or previews only in the UI is
insufficient. Employees retain access to their own permitted documents under
existing ownership and document-authorization rules.

Acceptance example: An assigned approver without document permission reviews a
sick-leave request with a verified medical attachment. The view and API show
“Required document provided” and “Verified”, but no filename, preview, document
contents, or read URL. Direct metadata, preview, and download attempts cannot
bypass the permission check. An approver with the separate permission can access
those details only when request-level authorization and applicable content-safety
checks also pass. The employee can still access their own permitted document.

See [ADR-0016](./architecture/decisions/0016-approver-medical-document-metadata.md).

The same medical-document metadata rule applies to Leave Managers within their
authorized NGO/resource scope. Without `leave.document.sensitive.read`, they see
only whether the required document was provided and its verification status.
Filenames, previews, and downloads require the separate permission and request-level
document authorization, with applicable content-safety checks. Apply this boundary
to both rendered views and API responses, including direct metadata access.

Acceptance example: A Leave Manager without document permission reviews an
in-scope request with a verified medical document. The view and API show only
“Required document provided” and “Verified” as document information. Filename,
preview, and download access is denied. Granting the separate document permission
permits access only within authorized NGO/resource scope and after applicable
content-safety checks; it grants no access to another NGO's document.

See [ADR-0017](./architecture/decisions/0017-leave-manager-medical-document-metadata.md).

### 13. Notifications

MVP channels are email and in-app notifications.

Events include:

- Submission received
- Approval action required
- Supervisor approval complete
- Balance override granted or denied
- Final approval
- Rejection with reason
- Withdrawal or cancellation
- Reminder and escalation
- Attachment rejected or action required

Delivery is asynchronous, retryable, deduplicated, tenant-branded, and observable.
Messages reveal only the minimum necessary information for the leave type's privacy
classification.

Email notifications contain only the employee's name, absence dates, request
status, and a secure application link as request-specific information. Leave types
(including ordinary types), employee notes, approval comments, and document
details remain inside the application. Apply this restriction to email subjects,
bodies, previews, and link text/parameters; do not encode excluded details in the
link or attach supporting documents. Email links lead to the application, where
authentication, active NGO membership, and resource permissions are checked before
details are shown. Possession of the link grants no request or document access.
Existing recipient authorization and colleague privacy rules still apply; this
content limit does not grant new recipients access to request status.

Acceptance example: Approval emails for annual-leave and sick-leave requests show
only the permitted name, dates, status, and application link as request data.
Neither email's subject, body, preview, nor link reveals the leave type, employee
note, approval comments, or document details. An authorized recipient follows the
link and sees only their permitted application details. A signed-out recipient
must authenticate; an unauthorized or wrong-NGO actor cannot use the link to read
the request or obtain a medical-document read URL.

See [ADR-0014](./architecture/decisions/0014-email-notification-privacy.md).

In-app notifications use the same request-content limit: employee name, absence
dates, request status, and a link to the request. Exclude leave types, employee
notes, approval comments, and document details from notification lists, banners,
previews, and their API payloads and links. Deliver and expose notifications only
to authorized recipients within the active NGO/resource scope. Opening the request
rechecks current permissions and shows only the details permitted by the
recipient's role; medical documents retain their separate authorization.

Acceptance example: An assigned approver's in-app notification for sick leave
contains only the permitted name, dates, status, and request link as request data,
including in its API response. Opening the request reveals the sensitive leave
type and employee note under the approver's current permissions, but does not
grant medical-document access. If the recipient no longer has request access,
following an earlier notification link denies access; another NGO's notifications
are not exposed.

See [ADR-0015](./architecture/decisions/0015-in-app-notification-privacy.md).

### 14. Employee workspace

The employee home screen prioritizes an obvious **Apply for leave** action,
balance summaries by leave type, pending requests and anything requiring the
employee's response, upcoming approved leave, and a link to the year calendar
and full history. Keep all content scoped to the employee's active NGO.

Acceptance example: On opening the employee home screen, an employee can start
a request, identify balances by type, find a pending request needing their
acknowledgement, see upcoming approved leave, and navigate to the year calendar
and history. These use the existing authorized request and balance data; a
notification's read state does not dismiss a required employee response.

See [ADR-0063](./architecture/decisions/0063-employee-home-screen.md).

- View leave history in a year calendar with a companion accessible list. Provide
  year selection so employees can find prior years' leave. The list shows dates,
  leave type, duration, and status within the employee's permitted own-request view.
  Clearly distinguish leave already taken, approved future leave, and pending
  requests without relying on colour alone.
- View a balance summary for each leave type showing currently available and
  reserved amounts. Show future-date calculations in the leave application for its
  selected dates; defer a separate future-balance calculator or graph. Open the
  explanation for grants, leave used, expiry, and adjustments using existing ledger
  and schedule-aware unit rules.
- Apply for leave
- Resume drafts
- View request status and approval timeline
- View decisions, approver names, timestamps, and approval/rejection comments on
  their own requests; MVP has no private approver-only comments
- View personal calendar
- View balance summary and ledger explanation
- Download permitted personal documents
- Withdraw eligible requests
- Cancel approved leave without further approval; submit a linked replacement
  through approval again when dates or duration change
- Switch active NGO

### 15. Approver workspace

The approver home screen prioritizes requests currently awaiting that person's
decision, flags for short notice, backdating, balance overrides, and overdue
requests, and team availability alongside the queue. Provide access to the
approver's own employee workspace. Apply this pattern to the unified Approver role
for assigned supervisor and final steps within authorized NGO/resource scope; the layout
does not grant broader team visibility.

Opening a request shows duration, balance effect, employee explanation, and
approval history under the agreed field and document permissions. The actionable
queue excludes steps whose action is not yet required or whose decision is already
recorded. Team availability retains existing colleague privacy where no additional
visibility is authorized.

Acceptance example: An approver opens their home screen and finds requests needing
their decision with applicable short-notice, backdating, override, and overdue
flags. They can compare authorized team availability, open a request's permitted
calculation and history, and navigate to their own employee workspace. A request
awaiting a different approver is not presented as their actionable task. The
screen grants no medical-document access without its separate permission.

See [ADR-0064](./architecture/decisions/0064-approver-home-screen.md).

- View direct-team calendar and availability
- Review assigned requests and conflicts
- See balances needed for the decision
- Grant or deny balance overrides when permitted
- Approve/reject with comments
- View delegated approval work
- Filter and sort the approval queue
- Receive reminders for aging requests

Assigned supervisors can see sensitive leave types and employee notes through their
normal approval role. Medical documents require separate permission and
request-level document authorization.

### 16. Final-step context in the Approver workspace

Use the same Approvals queue and role; these are responsibilities of an assigned
workflow step, not a separate role or navigation section. Calendar visibility
continues to require the appropriate resource scope.

- View organization or assigned-scope calendar
- Review requests that completed earlier steps
- See sensitive leave types and employee notes for assigned requests through the
  normal approval role; medical documents require separate permission
- See prior decisions and comments
- See approver names and decision timestamps for requests within approval scope
- Approve/reject with reasoned comments
- See capacity indicators without unnecessary medical information
- Self-approve only when the NGO explicitly permits it

### 17. Leave Manager workspace

The Leave Manager home screen prioritizes escalated approvals and balance deficits
needing review; requests affected by employment or policy changes; authorized
corrections and on-behalf actions; an organization leave overview; and shortcuts
to policies, schedules, entitlements, reports, and audit history. The overview
covers the active NGO under the MVP NGO-wide role scope. Work queues and actions
remain subject to their separate permissions; Leave Manager status does not
automatically make the actor an approver.

A rejected administrative correction appears as **Correction needs follow-up** in
the Leave Manager attention queue. Show the replacement's rejection reason and
allow authorized edit/resubmission under the existing rejected-request lifecycle.
The original stays cancelled rather than automatically restoring incorrect dates;
retain both linked histories and keep the unresolved correction visible for follow-up.

Acceptance example: A Leave Manager in NGO A can view its organization-wide leave
overview, including employees in different departments, and find the administrative
queues and configuration shortcuts on their home screen. They cannot use that
role to view NGO B. Without on-behalf permission they cannot correct another
employee's request; without balance-adjustment permission they cannot resolve a
deficit through adjustment; approval and sensitive-document access retain their
separate checks. Department/location restrictions are not required for this MVP
Leave Manager role.

See [ADR-0065](./architecture/decisions/0065-leave-manager-home-and-ngo-wide-scope.md).

- View leave types (including sensitive types), employee notes, and approval
  history within authorized NGO/resource scope through the Leave Manager role
- Configure leave types and policy versions
- Configure accrual, balance, documentation, privacy, and workflow rules
- Configure calendars and employee schedules
- Configure employee entitlement overrides
- Adjust balances with preview and mandatory reason
- View organization leave and operational reports
- Reroute/escalate requests under controlled permissions
- Submit or approve on behalf of an employee under a separate permission, with a
  mandatory reason, visible attribution, and a complete audit trail
- Review audit history and failed operational jobs/notifications
- Access sensitive documents only with the separate permission

### 18. Calendars and privacy

- Employees can read decisions, approver names, timestamps, and approval/rejection
  comments on their own requests. Assigned approvers can read the same history for
  requests they handle within their authorized active NGO/resource scope. MVP has
  no private approver-only comments. Apply these rules to request views and API
  responses; they do not expand colleague or notification visibility.
- Leave Managers can read leave types (including sensitive types), employee notes,
  and approval history within their authorized NGO/resource scope. Apply this
  boundary to authorized request views and API responses. Medical documents still
  require separate permission and request-level document authorization.
- Assigned approvers can read the leave type (including sensitive types) and
  employee note for requests in their approval scope, including through the
  corresponding authorized API. This does not grant access to unrelated requests,
  another NGO's data, or medical documents.
- Personal calendar shows the employee's full permitted details.
- Team calendar consolidates direct reports and capacity impact.
- Organization calendar supports department, team, location, status, and date filters;
  leave-type filters require permission to see the corresponding leave types.
- Ordinary colleagues see **Unavailable** for full-day entries and **Part-day absence**
  for partial-day entries, for every leave type including annual
  leave. Shared absence entries may identify the employee and absence interval but
  must not reveal the type, reason/note, approval comments, or attachment metadata.
  This colleague-level rule applies consistently to calendars, dashboards,
  notifications, exports, and their API responses. Hidden types must not be exposed
  indirectly through filters, colours, icons, grouping, or tooltips.
- Being a colleague or having access to an absence view does not grant detailed
  request access. Additional role-specific visibility must be explicitly authorized;
  document access remains separately controlled.
- Attachments never appear directly in calendar views.
- Exports apply the same authorization and privacy transformations as screens.
- Capacity warnings are informational in MVP and never block a request or approval.

Acceptance example: An ordinary colleague views an annual-leave absence and a
sick-leave absence. Both are labelled **Unavailable**, showing only permitted
absence information. Neither their rendered entries nor the colleague's API/export
data reveal type labels, reasons, comments, or attachment metadata. No leave-type
filter or presentation cue distinguishes the two. The employee's own permitted
view continues to show their request details.

Acceptance example: An assigned approver without
`leave.document.sensitive.read` opens a sick-leave request in their active NGO.
The authorized request view and API expose its sick-leave type and employee note,
but deny access to its medical document and any signed read URL. Holding the same
approval role does not grant those request details for an unrelated request or
another NGO. Adding the document permission permits a read only when request-level
authorization and the existing content-safety checks also succeed.

Acceptance example: A Leave Manager without `leave.document.sensitive.read`
opens an in-scope sick-leave request. Its authorized view and API show the sensitive
leave type, employee note, and approval history, but deny the medical document and
any signed read URL. The Leave Manager role grants no access outside the actor's
authorized resource scope or in another NGO. Document permission alone does not
bypass request-level authorization or content-safety checks.

Acceptance example: An approver rejects an employee's request with a comment.
The employee's own request view and API show that decision, the approver's name,
the timestamp, and the full rejection comment. An assigned approver handling the
request can read the same history, including earlier approval comments. There is
no private-comment option or hidden approver-only comment field in MVP. An ordinary
colleague or out-of-scope actor cannot read this history; notification payloads
continue to exclude comments.

See [ADR-0018](./architecture/decisions/0018-approval-history-visibility.md).

See [ADR-0011](./architecture/decisions/0011-colleague-absence-privacy.md),
[ADR-0012](./architecture/decisions/0012-assigned-approver-field-visibility.md), and
[ADR-0013](./architecture/decisions/0013-leave-manager-field-visibility.md).

### 19. Reports and exports

MVP reports include:

- Current and point-in-time employee balances
- Accrual and adjustment history
- Leave used by employee, type, team, and period
- Upcoming absence report
- Pending approval aging
- Override and administrative-adjustment report
- CSV export with tenant scope, authorization, and audit record

### 20. Audit and operational administration

Audit records include actor, active NGO membership, action, resource, timestamp,
correlation ID, before/after or transition detail, reason, and delegated/on-behalf
context where relevant.

Audit coverage includes configuration changes, entitlement overrides, balance
adjustments, workflow changes, request transitions, attachment operations, sensitive
reads, exports, tenant switching, and notification delivery administration.

## State models

The following state models were approved on 2026-09-01. Additive implementation
detail may be introduced without changing their business meaning; new user-visible
states or transitions require product review.

### Application status

```text
draft
submitted
in_approval
approved
rejected
withdrawn
cancelled
```

Approval steps have their own `pending`, `approved`, `rejected`, `skipped`,
`delegated`, and `cancelled` states. Application status must not be inferred from a
single mutable approver column.

### Attachment status

```text
upload_pending → uploaded → verified → available
                       ↘ rejected
                       ↘ failed
upload_pending → expired
available → deleted/retained
```

The state model permits an optional future `scan_pending → clean/rejected` step
without changing Leave attachment associations.

### Balance reservation

```text
submission → reserve
intermediate approval → retain reservation; do not consume
final approval → convert reservation to consumption
rejection/withdrawal → release reservation
cancellation → reverse consumption according to policy
```

For a two-step workflow, leave remains reserved after the first approval and
becomes consumed only after the final approval.

Acceptance example: Given a submitted request with 480 minutes reserved and two
required approval steps, when the first approver approves, all 480 minutes remain
reserved and none are consumed. When the final approver approves, the 480-minute
reservation is converted to consumption exactly once.

## UX requirements

### Visual direction

- **Tone:** Calm, practical, and low-friction.
- **Palette and contrast:** Restrained colour, neutral backgrounds, subtle
  decorative borders, and a single accent colour reserved for primary actions.
  Keep text, interactive boundaries, and focus indicators sufficiently distinct
  to satisfy the existing accessibility requirements; “muted” does not mean
  difficult to read. Communicate statuses and warnings through clear text and
  familiar cues rather than competing accent colours or colour alone.
- **Layout and spacing:** Generous padding and vertical margins provide breathing
  room. Avoid high-density or cluttered views, including on phones.
- **Information hierarchy:** Elevate key balances and primary actions. Mute
  secondary details and place granular explanations in expandable sections.
  Keep decision-critical information, validation errors, and required actions
  visible, including the paid/unpaid split and any required acknowledgement.
- **Components:** Prefer familiar, established platform UI controls and shell
  primitives to custom visual patterns. Use existing components where available;
  establish missing shared components through the approved prove-then-promote
  delivery approach rather than assuming they already exist.

Acceptance example: The employee home makes balances and Apply for leave visually
prominent without a crowded dashboard. Detailed ledger explanations expand on
demand, while required responses remain visible. Submission keeps its paid/unpaid
split and acknowledgement visible. Keyboard focus, text, and controls remain
perceivable against neutral backgrounds; a status never depends on colour alone.

See [ADR-0073](./architecture/decisions/0073-calm-practical-visual-direction.md).

### Interaction and accessibility

On phones, employees can complete the full leave-request process, upload documents,
view balances and history, and respond to required actions. Approvers can review
and decide requests on a phone under the same permissions and validation rules.
The year calendar may use a compact month view on small screens, with navigation
through the selected year's months and the companion history list always available.

Acceptance example: On a phone, an employee can enter a request, upload a permitted
document, review its balance effect, acknowledge any requested unpaid amount, and
submit. They can subsequently view balances/history and respond to a required
acknowledgement. An assigned approver can read the permitted details and approve
or reject. The compact calendar supports month navigation without removing the
accessible history list. Mobile presentation does not bypass document permission
or hide information needed for a decision.

See [ADR-0072](./architecture/decisions/0072-mobile-employee-and-approver-workflows.md).

Use one application with **My Leave**, **Approvals**, and **Manage Leave** sections
shown according to permissions. Everyone starts on My Leave. Switching sections
does not require signing out or changing the active NGO. Section badges show work
requiring the user's attention, separately from unread notification counts.

Acceptance example: A user with employee, approver, and authorized Leave Manager
access starts on My Leave and can switch to Approvals or Manage Leave within the
same NGO. A user lacking those permissions does not receive the corresponding
section or its action-count data; direct navigation still enforces authorization.
Marking notifications read does not clear a section's unresolved-work badge.

See [ADR-0066](./architecture/decisions/0066-role-sections-and-action-badges.md).

The employee experience includes a year-calendar and companion history list plus
per-leave-type balance summaries. Pilot tasks include finding last year's leave
taken and identifying the currently available balance for each leave type.
Bound year navigation by known employment start/end, while extending those bounds
where recorded leave or rehire history would otherwise be hidden. Show full boundary
years with out-of-employment dates muted. Without an employment end date, do not
invent an employment-based upper bound. Remember Calendar/List preference per user
and NGO; reopen at the current year when it is within the available bounds.
Design and implement these views before pilot testing; use observed confusion to
refine the experience and retest. Pilot testing does not replace upfront UX design.

Acceptance example: An employee selects the previous year, finds their recorded
leave in the calendar, and can read its dates, type, duration, and status in the
companion list. They can distinguish it from approved future and pending leave.
For each leave type, they can identify available and reserved amounts and open the
ledger explanation. In a leave draft, selecting dates shows their projected effect,
paid/unpaid allocation and resulting balance without submission or reservation.
Explain the policy-specific consequence of a shortfall rather than only showing a
negative balance. Defer the standalone future-date calculator and balance graph
under [ADR-0084](./architecture/decisions/0084-request-focused-balance-planning.md). Preserve own-request
authorization and existing privacy boundaries; this view grants no additional
access to another employee's history.

See [ADR-0062](./architecture/decisions/0062-employee-history-and-balance-views.md).

Each user chooses their preferred interface language. The preference follows them
when switching NGOs, with English as the fallback when the preferred translation
is unavailable. Personal notifications use the recipient's preferred language
when translations are available, otherwise English. Language selection does not
change work timezone, leave policy, jurisdiction, permissions, or stored values.

Acceptance example: A user selects a supported Portuguese locale and switches from
NGO A to NGO B. The interface retains their language preference, and personal
notifications use it when translated templates are available. Before Portuguese
translations are available, use English without changing their work timezone or
either NGO's policy calculations. Another user's language choice is unaffected.

See [ADR-0061](./architecture/decisions/0061-user-language-preference.md).

Default to English and show dates as **15 Sep 2026** (day, abbreviated month,
four-digit year). Keep user-facing text and notification templates translatable
and use locale-aware presentation so Portuguese can be added soon without changing
business calculations or stored data. Portuguese is the next planned language;
its initial audiences are Mozambique and Angola, with release timing still open.
Validate wording and regional formats for both, reusing shared translations where
appropriate. Locale does not change jurisdiction, permissions, or work timezone.
See [ADR-0060](./architecture/decisions/0060-portuguese-mozambique-and-angola.md).

Acceptance example: The English request view displays 15 Sep 2026 without changing
the employee-work-timezone date used for eligibility and balances. Translation
resources can supply Portuguese labels and messages without changing permissions,
canonical values, or request logic. Portuguese translations are a separate delivery
item, not a completed MVP capability. See
[ADR-0059](./architecture/decisions/0059-default-language-and-localization-readiness.md).

- Meet WCAG 2.2 AA.
- Work well on mobile and desktop.
- Support complete keyboard navigation and visible focus states.
- Never rely on color alone for request status.
- Use plain-language calculation explanations.
- Preserve entered data when validation or a network call fails.
- Provide optimistic feedback only when the command is safely idempotent.
- Clearly distinguish warnings, policy blocks, and actions requiring an override.
- Make destructive or balance-affecting actions explicit and confirm their effect.

## Non-functional requirements

- Strict database, API, job, cache, file, and log tenant isolation
- Encryption in transit and at rest
- Short-lived signed content operations
- Idempotent commands and notification delivery; deterministic repeated automatic-entitlement calculation
- Optimistic concurrency for decisions and configuration
- Structured logs, metrics, traces/correlation IDs, and actionable alerts
- Tested backups, restoration, migrations, and rollback
- Configurable data retention and auditable deletion
- Deterministic date/time calculations and timezone handling
- Performance targets agreed before release testing

Recovery covers database and private document contents, their consistent associations,
and required identity/access/configuration dependencies. Existing hosting is not assumed
to meet the target. Pause outbound notification processing during restore until producer/
receiver recovery evidence has been checked; hold uncertain work rather than blindly
resending after rollback. Verify representative access, requests/balances, documents and
queue handling in the restoration rehearsal under ADR-0119.

### Operational target ownership and decision gates

| Decision | Responsible | Decision gate |
|---|---|---|
| Secure document-link / signed-operation lifetime | Technical architect and security lead | Selected: 5-minute private reads, 15-minute uploads under [platform ADR-0036](../../../platform/docs/architecture/decisions/0036-private-content-signed-operation-lifetimes.md); adapter/renewal verification before pilot |
| Backup recovery objectives | Technical lead and operations owner | Selected under [Leave ADR-0119](./architecture/decisions/0119-initial-production-backup-and-recovery-targets.md): one-hour recovery point, four hours from incident declaration to essential service, thirty-day backup retention; rehearse before pilot, quarterly and after major backup changes |
| Critical alert conditions | Technical lead and operations owner | Selected under [Leave ADR-0120](./architecture/decisions/0120-initial-operational-alert-thresholds.md): API/heartbeat five minutes; overdue notifications warn at fifteen minutes and escalate at one hour; recovery-point age over one hour and confirmed integrity failure alert immediately. Verify before pilot |
| Supported browsers and performance targets under representative workloads | Product owner and technical lead | Relevant story planning |

One person may hold several responsibilities. Record measurable targets and their
verification criteria at these gates. Signed-operation defaults, backup targets (ADR-0119) and alert thresholds (ADR-0120)
are selected and must be demonstrated. Browser coverage and workload/performance
targets remain relevant-story planning decisions.
Delivery verifies the agreed targets before the pilot, including restoration
rehearsals, alert checks, browser coverage and representative performance tests.

## MVP exclusions

- General self-service migration/upload UI. MVP uses a consultant-operated import
  tool with documented templates, validation and preview, employee/row errors,
  duplicate prevention, import audit, and a client-facing reconciliation summary.
  Import through supported application contracts with authorization and audit;
  normal manual employee/opening-balance entry remains available. Consultant emails
  the report to an authorized client contact and records their email approval
  against the exact batch before applying it. Changed data requires a revised
  report and renewed approval. No client confirmation page is required in MVP.
- Microsoft Graph reporting-relationship synchronization: a future shared platform
  directory capability, separate from calendar integration. MVP supervisor assignments
  are maintained manually. Leave continues to own approval rules; future imports
  must preserve authorized overrides, flag missing/invalid managers, check NGO
  membership and approval eligibility, and never silently reroute pending requests.
- Microsoft 365, Google Calendar, payroll, and HRIS integrations
- Teams, Slack, and SMS delivery
- Generic drag-and-drop workflow builder
- Automated statutory compliance or legislative updates
- Tenant-managed identity-provider configuration
- ZITADEL or Keycloak migration
- Advanced staffing optimization and forecasting
- Portuguese translation delivery and further locales beyond the English MVP (localization readiness is included)

## MVP acceptance summary

The MVP is acceptable when:

1. A multi-NGO user can switch NGOs and never see cross-tenant data.
2. A Leave Manager can configure policies, calendars, schedules, workflows, and
   employee entitlement overrides without database access.
3. An employee can submit full-day, half-day, or hourly leave and understand the
   exact current/projected balance calculation.
4. Configured approvers can decide requests, including explicit deficit overrides,
   with correct ledger effects and complete history.
5. Attachments use the FastAPI Content Service, remain private, and require both
   Leave authorization and content safety checks.
6. Calendars and reports enforce privacy rules for sensitive leave.
7. Accrual and notification jobs tolerate retries without duplicate financial or
   user-visible effects.
8. Accessibility, tenant isolation, backup/restore, audit, and operational release
   gates pass.
9. Every completed feature has a recorded scaffold impact decision; all applicable
   builder templates, generation tests, documentation, and migration notes pass.
10. Acceptance scenarios trace to the approved requirements, relevant tests were
    observed failing before implementation where practical, focused and affected
    suites pass, and commands/results are recorded as completion evidence.

## Related documents

- [`implementation-plan.md`](./implementation-plan.md)
- [Leave architecture decisions](./architecture/decisions/README.md)
- [Platform architecture decisions](../../../platform/docs/architecture/decisions/README.md)
- [Platform BMAD delivery decision](../../../platform/docs/architecture/decisions/0010-bmad-as-delivery-workflow.md)
- [Platform agent context](../../../platform/prompts/README.md)
- [Platform ATDD/TDD decision](../../../platform/docs/architecture/decisions/0009-atdd-and-tdd-development-loop.md)
- [`../../../docs/tech-spec.md`](../../../docs/tech-spec.md)
- [`../../../services/app-directory/docs/app-directory.md`](../../../services/app-directory/docs/app-directory.md)

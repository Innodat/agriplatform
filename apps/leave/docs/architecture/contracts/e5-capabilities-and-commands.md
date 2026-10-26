# E5 capability and command bindings

**Status:** Technical catalog/action binding of approved business permissions;
command schemas/final coverage/readiness remain open  
**Date:** 2026-10-23  
**Owner:** Leave capability/API owner with Access registration owner

Sources: Features Permissions; P-0011/0046/0053; L-0011/0012/0013/0149/0150/0153/0161.
This is a closed wire-name mapping, not new roles or a second authorization service.
Access owns current capability grants/admission; Leave enforces actual resource scope.
No live catalog registration, default-role change or grant is made by this document.

## E5 request action/read catalog

Every entry is organization-scoped. Register exact strings, not literal wildcard grants.
Each check uses Access's typed organization authorization scope and current org admission/
membership. Additional action predicates below are mandatory even after capability success.

| Exact capability identifier | Action / read boundary | Required Leave predicate |
| --- | --- | --- |
| `leave.request.own.read` | Existing E1 own read plus own current request/calendar/history | Verified current caller-to-employment ownership; actual permitted own fields only |
| `leave.request.own.manage` | Own draft/submission, pending withdrawal, rejected correction/resubmit and initial unpaid employee response | Actual employee owner, correct current lifecycle/cycle/revision; initial response only actual employee. No on-behalf or E6 cancellation by inference |
| `leave.request.approve` | Unified assigned-step approve/reject and minimum assigned queue/detail/history needed to decide | Currently authorized assigned responsibility/step and current authority, including exact temporary scope; no organization-wide detail or decision right |
| `leave.admin.on_behalf` | Initial on-behalf submission and its minimum authorized employee/source review | Current permitted target employee scope, mandatory reason and actual attribution; no employee draft mutation/proxy response/withdrawal |
| `leave.balance.override` | L-0150's request-specific exceptional allocation and minimum required funding review | Current request/employee scope and permitted funding-source business rules. No unrelated standalone adjustment, recurring override or approval implied |
| `leave.workflow.reassign` | Selected unfinished-step reassignment and its minimum review | Current organization/work scope, eligible authorized target and reason; recipient needs actual approval authority, not role label |
| `leave.workflow.manage` | Existing workflow configuration and scoped appointment/extension/early-end management | Actual configuration/subject/responsibility/period scope and current review; no human decision, funding or document right implied |
| `leave.workflow.coverage_exception` | Reasoned bounded applicant approval-coverage exception | Exact applicant/date/responsibility gap and current scope; records exception without appointing/approving or waiving another gate |
| `leave.request.team.read` | Existing authorized team request/availability projection | Actual current organization-supervisor direct-report scope via People; default colleague view remains Unavailable, not detailed type/note/history |
| `leave.request.org.read` | Existing authorized organizational request/attention/history projection | Current organization scope and explicit admin field model; no action permission inferred |
| `leave.document.attach` | Actual E4-owned attachment action composed by request consumer | Current editable/attachable owned or explicitly allowed record; Content owner/readiness protections |
| `leave.document.sensitive.read` | Separate medical/sensitive document metadata/bytes permission | Both current capability and actual request/document authorization; not supplied by approval/manager/temporary role alone |

The approval string finalizes the already agreed unified business capability; minimum
assigned detail is part of its approved assigned workflow, not another required read grant.
Reassignment/coverage-exception strings finalize their already agreed separate capabilities.
`leave.balance.override` is bound narrowly to the existing request-exception purpose here;
recurring allowance/source operations need their actual separately bound source capability
and cannot inherit it from the word override. No duplicate exception permission or per-line
funding grant is introduced. Closed source-action mappings remain the next C5 item.

Team read never supplies current assigned authority. A temporary appointee may act under
its actual scoped appointment authority without a permanent standard Approver role; its
Access/domain representation must encode that explicit effective right and current app
admission. An appointment label alone or unrestricted org grant is not an implementation.
Exact Access representation of this scoped grant is a consumer contract to bind, not a
permission silently manufactured in a read handler.

## Default-role preservation and action combinations

- Standard Approver includes the unified scoped approval action and scoped initial
  on-behalf capability under L-0149. Temporary appointment alone supplies only its
  appointment responsibilities. Custom approval-only roles may omit on-behalf.
- Standard Leave Manager includes explicit reassignment and coverage-exception capability
  under L-0153 and the existing accepted default; custom roles may omit them. Manager
  status alone does not approve/reject or grant medical documents.
- Funding-only needs the request exception capability. Combined Approve with exception
  needs both exception and actual current assigned approval authority in one atomic
  confirmation. It does not need a permission per permitted source line.
- Employee withdrawal/initial response remain employee-only even when someone else
  submitted the request. Approved cancellation/replacement defaults remain accepted E6
  scope with their own exact action binding; E5 on-behalf/manage does not grant them.

Do not infer role names, wildcard prefixes, supervisor membership or previous receipts as
capability grants. Default versions/new catalog entries must be explicitly adopted without
silently expanding custom roles. This table specifies only defaults already agreed; it
does not guess unresolved role composition or apply production grants.

## Current read and operation recovery selection

One current-request endpoint selects an allowlisted own/assigned/admin projection from
verified current capability plus domain relationship. A caller may have several valid
routes; each field still needs its actual authorized projection. Do not union arbitrary
ORM fields merely because multiple roles are present. Reads never execute finalization.

Operation lookup requires original caller/organization identity plus current permitted
target access/action context. Retained employee/actor/receipt IDs grant no ongoing access.
A denied/inaccessible target follows safe disclosure policy; unavailable authorization
is not a successful unresolved result. Assigned former actor is not entitled to private
history solely because a prior immutable decision names them. Exact command-specific
result/recovery models follow this table in C5; C implements the common mechanism.

## Verification and impact allocation

Actual API/Access consumer tests cover each action with current permitted/denied scope,
wrong organization/employee, role-name-only input, custom omission, temporary-only actor,
funding-only/combined authority, employee-only response/withdrawal and absent medical
permission. Register catalog/default revisions with the actual consuming delivery;
fixtures use real capability/domain decisions, not only mocked role labels.

Apply [focused migration verification](../../../../../platform/docs/development/migration-verification.md)
to catalog/state migrations: ordinary Alembic upgrade/repeat/failure and actual restricted
runtime allow/deny/tenant cases. Do not build a schema-object whitelist or duplicate
Alembic's internal ledger interpreter. Domain keys/lifecycle/immutability checks remain
focused application invariants; a mock or empty migration ledger is not business-table
RLS/rollback proof. No runtime migration/test was performed in this planning pass.

Scaffold uses proven typed Access/HTTP/error and focused migration fixtures with first
consumers. Shared UI consumes actual allowed actions/fields, no new role screen or medical
permission default. Existing agent/ADR rules suffice. C5 still needs exact source/temporary
scope representation and closed command models; C6 final mapping/order/size/readiness open.
No implementation, credential/grant, migration or live setting changed.


## Source actions and temporary appointment authority — 2026-10-23

### Source action capability mapping

Use the existing catalog families below; these are exact organization-scoped checks,
never a generic manager role-name check or permission inferred from a notification.
Minimum source-impact reads accompany the specific permitted source action/context;
they are not a new organization-wide request-detail grant.

| Actual source action | Required Leave action capability | Domain scope / independent checks |
| --- | --- | --- |
| One-off balance adjustment, 3.29 / 5.15-A | `leave.balance.adjust` | Exact employment/type/effective-date/reason/review and affected commitments; request exception authority does not substitute |
| Recurring employee allowance/reset, 3.30 / 5.15-C | `leave.policy.manage` | Exact employee assignment/entitlement and valid period boundary; no new annual grant/balance reset inferred. This is recurring policy entitlement management, not request-specific exception |
| Policy first/publication/schedule amendment/cancel and initial/change/end assignment, 3.28/34/35/36 | `leave.policy.manage` | Actual policy/version/selected employees/source revisions; initial versus replacement preconditions remain source-specific |
| Calendar entry add/edit/remove, 2.18 / 5.15-U | `leave.calendar.manage` | Actual organization calendar/date/version and dependent work; no source-date or affected-set widening |
| Profile/default/employee assignment/override/reset/archive, 2.19–24 / 5.15-M/O/Q/S | `leave.schedule.manage` | Exact employee/profile/default/field/date chain; source capability covers minimum required impact review, not general unrelated request reads |
| Workflow configuration/appointment management | `leave.workflow.manage` | Exact configuration/responsibility/employee/period; does not grant resulting human decision to manager |
| Manual unfinished transfer / coverage exception | `leave.workflow.reassign` / `leave.workflow.coverage_exception` | Existing separate action scope and reason; standard/default mappings already agreed |
| People employment/supervisor source command | Actual shared-owner management authority, independently verified by People | Leave service key or Leave source/approval grant cannot authorize a People fact write. Shared People capability catalog is owned by its source contract, not invented as a Leave permission |

A source capability permits only its declared reviewed domain consequences. It does not
permit independent exceptional grants, another person's approval or medical content.
Combined exceptional funding/approval remains the two-authority L-0150 case. Actual People
impact review additionally verifies its required Leave source/consequence read scope before
private funding/request data is returned; no automatic broad grant from shared employment
administration. Pure supervisor-change disclosure remains limited to its required safe
source/consequence fields. Existing source schemas must not replace mandatory authorized
funding review with an uninformative count.

### Temporary approval: choose the authority path explicitly

L-0082 already permits a current organization member to receive bounded temporary approval
without a permanent Approver role. Represent that explicit delegation in Leave's actual
appointment/responsibility records, not by copying the standard role or provisioning a
permanent unrestricted approval grant in Access.

For ordinary approval, Access `/v2/check` verifies `leave.request.approve` with typed
organization scope; its resource result is `{kind: assigned_workflow_steps}`. This is a
predicate, not a list of every request or a permission to approve all organization work.
Leave must verify the actual current assigned step, self/distinct-person rules and revision.

For the **explicit appointment path**, Access verifies current identity/membership and
Leave global/organization admission; Leave verifies the actual effective authorized
appointment and exact step/responsibility itself. This path is selected from verified actor
context and the actual local appointment before attempting a permanent approval grant
check; a denied grant check is never converted into success via fallback. Denied current
membership/app admission is terminal for either path. An unavailable check is unavailable,
not permission to use a cached role or appointment.

This requires a small restricted Access context extension; it is a declared new consumer
contract, not an existing endpoint. Select `POST /v2/applications/leave/organization-context`
for the Leave API credential with current user bearer and exact `{org_id}` input. Response
is current `account_id`, `actor_id`, nullable `person_id`, `org_id`, `membership_id`,
`observation_id`, `checked_at` after verified session/membership/global/org admission.
It is private/no-store and contains **no granted capability or approval decision**.
It cannot replace `/v2/check` for an action requiring an Access-owned permanent capability.
The actual explicit appointment supplies only its already approved delegated authority.
Do not repurpose People's identity-context endpoint, which checks no application admission.

ACCESS-B/actual Access capability consumer owns the context/resource union extension and
real positive/denied/unavailable cases; 5.21/5.22/5.23 and decision consumers own appointment
create/start/extend/end/expiry/current applicability. Exact actor/account links are verified
through existing identity/People contracts; an accountless employee cannot execute an
interactive approval until actually linked/authorized. No synthetic account or employee.

No general team/request calendar/read, on-behalf, exceptional funding, cancellation or
medical-document permission follows from the appointment. The actor may inspect the
minimum assigned request/decision context only while the appointment/current record
permits it. End/expiry/supersession denies stale actor decisions immediately at the current
check even if a stored queue entry remains. Completed decision attribution stays immutable;
permanent supervisor-boundary timing follows L-0163, not an automatic appointment extension.

### Scope and verification closure

All ordinary source/approval checks remain Access-owned capability checks plus Leave's
actual resource validation. Appointment authority is the already accepted application-owned
explicit delegation, not an employment/membership-derived grant. This contract adds no
new customer role, checkbox or per-appointment Access grant/cleanup protocol.

Required actual cases: permanent approval grant/current assignment, temporary-only actor
with no permanent role, wrong scope/expired/superseded appointment, denied app/membership,
no denial fallback, role revocation independent of still-valid explicit delegation,
minimum assigned read versus broad team/org read, source capability versus exception,
combined action, and denied private source-review data. A revoked permanent grant does not
itself cancel an independent valid appointment; app/membership revocation blocks both.
Actual appointment cancellation remains its authorized workflow.

C5 source/temporary authority paths now have concrete owner/operation allocation. Exact
People source-management catalog names and approved actor-to-target scopes remain in the
shared owner source contract; on-behalf target selection and remaining command schemas
must still close before readiness. No capability registration, account/grant, Access code,
public endpoint, migration or test was changed here.


## Proposed initial on-behalf employee scope — 2026-10-23

**Product scope proposal for user agreement; not yet an accepted catalog/default change.**
L-0149 already supplies the explicit initial on-behalf capability to standard Approver
but leaves its target scope open. Recommend these two closed resource predicates:

| Granted resource scope | Proposed target rule |
| --- | --- |
| `normal_approval_population` — standard Approver default | Employees in the same organization for whom the actor normally holds a configured required approval responsibility: current supervisor direct reports and employees actually covered by a policy's explicitly configured final-approver responsibility. No authority from a final-role label alone |
| `organization_employees` — existing authorized organization-wide administration scope | Organization employees only when the actor explicitly holds initial on-behalf capability with this scope. Leave Manager's organization-wide resource scope does not itself supply a missing action capability |

The explicit capability remains required independently. Reporting/route relationships
only restrict which employees the granted on-behalf action may target; they do not grant
that action or create automatic decisions. A custom role may retain the scoped on-behalf
action without approval action; it submits without a human approval it lacks. A temporary
appointment never enlarges on-behalf population or supplies its capability. Separately
held normal supervisor/final responsibility or administrative grant remains independent.

Use current normal responsibilities, not temporary/fallback absence routing or historical
supervisor membership, for this resource predicate. Actual requested policy/date validation
still applies to submission. Before type/date selection, candidate discovery may show only
the actor's currently permitted population; once values are selected, the command rechecks
exact target/policy relationship and all ordinary gates. A picker result is not continuing
authority. No direct-report/department label or arbitrary employee ID can widen the result.

Examples: a supervisor with on-behalf scope can submit for a current direct report; an
explicit configured final approver can submit for employees covered by that configuration;
being final approver for one policy does not grant all employees/all policies. Organization-
wide administrator targets require an explicit organization-wide action scope. A temporary
stand-in with no independent on-behalf grant cannot submit through that appointment.

This proposal introduces no per-employee allowlist UI, new role, permission-transfer action,
document/funding/correction/cancellation right or employee proxy response. Existing reason,
actor/employee attribution, employee draft preservation and employee-only response stand.
If agreed, record a linked Leave ADR resolving L-0149's target scope and bind Access typed
resource result, target search and actual submit checks together. Until agreement, do not
mark this population rule accepted or implementation-ready. Boundary count stays 80.


## Initial on-behalf scope accepted and lookup binding — 2026-10-23

User accepted the preceding population proposal; [L-0164](../decisions/0164-initial-on-behalf-employee-scope.md)
records it. Earlier proposed/pending text for this choice is superseded. Access's success
for `leave.admin.on_behalf` has a closed resource union:
`{kind: normal_approval_population}` or `{kind: organization_employees}`. Both carry the
already specified organization/account/actor/membership context; no client-selected actor
or role label. The default Approver mapping selects the former; the latter requires the
explicit administrative action grant, not a fallback. Missing/unknown scope fails closed.
Access returns the predicate; Leave resolves actual current employee/policy membership.

Select `GET /api/v1/organizations/{org_id}/on-behalf/employees` for minimum target search.
Parameters: optional `query`, optional `leave_type_id`, `limit` default 25/max 50, optional
opaque `cursor`. Search text is bounded to 100 Unicode code points; reject invalid IDs/
cursors/limits rather than silently exposing unscoped results. Response is `items` with
only `employment_id`, authorized display label and selection context, plus nullable
`next_cursor`. No medical/leave-note/balance/history payload or total-organization export.
Cursor is navigation, never authority; bind it to actual organization/filter context and
recheck current scope on every page. Do not require a new signed-cursor credential system.

Before type selection, query only employees in at least one actual permitted normal
configured population (or explicit organization scope). When `leave_type_id` is supplied,
filter that actual policy context; final command always checks exact selected type/dates/
employment context and ordinary eligibility. Current source unavailability is not an empty
list. Accountless employee identity may be listed when the action permits it; this does
not grant login or allow proxy employee acknowledgement.

The actual on-behalf create command targets `employment_id`, never an employee draft.
Its required operation identity, versioned form input, mandatory reason and typed review
must match the frozen submitted command on retry. It creates actual request/cycle via the
shared core/accounting and leaves any ordinary draft untouched. The exact full form/review
schema is the next C5 binding; scope adoption does not declare that payload completed.

5.12-A owns target-search/current-scope backend tests; 5.12-B owns actual picker/review and
return behavior. Access consumer owns typed resource/default catalog/version fixtures.
Observe permitted supervisor/final/admin and unrelated type/employee denial, changed scope
after lookup, exact cursor context, custom omission/submit-only and temporary-only cases.
No extra role/default medical access or boundary; exact commands/C6 final coverage/order/
size/readiness remain open. No code, tests, registration/grants or migrations changed.


## Initial on-behalf and employee acknowledgement command models — 2026-10-23

**Selected v1 wire/storage binding for approved 5.12-A; no implemented endpoint.**
Use the authenticated `/api/v1/organizations/{org_id}` prefix, exact current actor/scope
checks above and existing C outcome/error/recovery envelope. No administrative draft,
proxy acknowledgement or duplicate core/accounting implementation.

### Shared reviewed summary projection

Bind `summary` as a closed object with `leave_type_id` UUID, `mode` full_days/half_day/hours,
canonical date-only `start_date`/`end_date`, `total_minutes`, `paid_minutes`,
`requested_unpaid_minutes` and `balance_tracking` tracked/untracked. Minutes are canonical
nonnegative decimal-string bigint values; total must be positive and paid + requested
unpaid equals total. Half-day/hour summary uses equal start/end date. Backend derives
these from E3 and the actual selected input, not a second editable date/minute source.
Mixed working/nonworking ranges retain their full requested endpoints.

Untracked summary still reports actual paid/unpaid classification/duration; these totals
are not fictional entitlement/reservation amounts. This is the concise reviewed projection,
not every internal portion/source/version or medical/absence detail. Existing current
checks independently validate date-by-date allocation and gates. Own submission can reuse
this same normalized model; paid/unpaid consequences changed since review require renewed
confirmation under the already selected comparison contract.

### On-behalf creation

`POST /requests/on-behalf` accepts exactly:

| Body field | Contract |
| --- | --- |
| `operation_id` | Original UUID retained across identical retries |
| `employment_id` | Actual target UUID in accepted L-0164 scope; never a selected actor/account override |
| `input` | Existing E1 version-1 input envelope with raw date/format/mode/note groups, interpreted under target employee context. Submission requires complete valid selected mode; inactive values have no calculation effect |
| `on_behalf_reason` | Required nonblank plain text, up to 4,000 Unicode code points, preserved exactly without silent truncation |
| `review` | Closed `{schema_version: 1, summary: <model above>, unpaid_acknowledgement: null}`; caller cannot supply employee consent |
| `attachment_refs` | E4's typed authorized association/reference list, not signed URLs, filenames or arbitrary Content IDs |

Maximum body 64 KiB UTF-8; unknown fields and unsupported envelope versions fail safe
validation. E1 note/date/duration field bounds remain. No draft ID/scope generation is
accepted and employee draft rows are untouched. E4 owns association context for this actual
on-behalf actor/form and submitted-reference continuity; that existing owner contract must
be available before this consumer activates. This model does not invent an attachment
staging/draft mechanism to replace missing E4 integration.

Recheck explicit capability/current target/policy scope, authoritative input and reviewed
summary under the approved protocol. Resolve required steps and only permitted own automatic
decisions; create request/cycle/commitment/evidence/audit/outcome/intent atomically. For this
new-cycle producer, select `in_approval` for any valid pending result and `approved` only
when B actually completes every gate. No separate queued/submitted-routing stage is added.
The supported `submitted` code remains representable for the source model; it is not a
new intermediate commit required to submit. Own submission/resubmission use this same
pending-versus-completed producer mapping when bound, without changing request creation
revision 1 or immutable old cycle evidence.

Add request-target command discriminator `submit_on_behalf`, version 1. Compact result is
`command`, `request_id`, `cycle_id`, `revision`, `request_status` under C's request branch;
creation revision is 1. Initial input fingerprints bind explicit create intent/target
employment and full validated command including review/reason/references, not subsequently
generated request/cycle IDs. A matching retry returns the original actual target/result.
Changed input with the same operation ID conflicts; source unavailability does not become
an empty eligible population or a fabricated submission.

### Employee-only response record and command

The first finalization reader 5.10-B creates the minimum `leave.request_employee_response`
representation and current-gate predicate on actual controlled records. 5.12-A owns actual
on-behalf obligation creation, employee acknowledgement and production lifecycle integration;
it reuses that representation rather than creating another. Fields: UUID identity,
org/employment/request/cycle scoped references, original initial unpaid evidence, state
outstanding/acknowledged/not_required/closed, positive revision and server attribution.
Unique `(org_id,request_id,cycle_id)` enforces one initial obligation per cycle. Initially
fully paid creation has no obligation record. The actual acknowledgement actor/time/current
amount/allocation evidence, when present, are immutable; services cannot fabricate them.
Required branch/null/positive-amount checks and scoped references are actual owner constraints.

`POST /requests/{request_id}/unpaid-acknowledgements` accepts exactly `operation_id`,
`cycle_id`, `expected_revision` (request review revision), `allocation_evidence_id` and
`acknowledged_unpaid_minutes` (positive canonical decimal-string bigint). It requires
`leave.request.own.manage` and actual current employee ownership. There is no actor selector,
on-behalf reason, proxy flag or funding override input. Body cap 4 KiB; path/body cycles and
actual current source evidence must agree before applying anything.

Record the employee's exact current acknowledgement, close the obligation as acknowledged
and invoke B in the same owning transaction. Valid earlier approvals stand; another unmet
gate leaves in_approval, otherwise B completes once. Add request-target command discriminator
`acknowledge_unpaid`, version 1; compact result adds `acknowledgement_id` to C's common
request result. A committed acknowledgement is not necessarily final approval. Replay
returns the original result without a new response, revision or consumption.

L-0162 zero allocation closes an outstanding requirement as not_required with actual
source actor/cause, not employee consent. Later same-cycle unpaid increases do not reopen
it. Reject/withdraw closes an outstanding requirement with actual lifecycle cause; old
response commands cannot resurrect it. Fresh resubmission applies the new cycle's initial
rules. A stale amount/cycle/revision/evidence gives a typed conflict after current access
checks, never a silently revised acknowledgement. No independent generic response workflow.

### Exact failures and verification ownership

Reuse common access/dependency/validation/mismatch/busy errors and the existing
`leave.request_revision_conflict`; use `leave.submission_review_changed` for changed create
summary with safe `{employment_id}` target detail after scope checks (the draft-based own
variant retains its separately typed draft/revision details). Closed/stale response-specific
conflicts expose safe current state/identity only, no other person's amounts/data. C5's
shared error union must discriminate those detail variants; UI never branches on text.

5.12-A owns real source target/create/response/state/role/atomic rollback/outcome tests;
5.12-B owns picker/review/current employee handoff. Verify exact positive/zero/later-change,
proxy denial, lost response, competing allocation/withdrawal/finalization, unchanged ordinary
draft and current read after original commit. E3/8-A/C/B/E4 owner suites remain prerequisites;
5.32-B links composition instead of duplicating them. Planned test paths/commands/fixtures
still bind with the actual packages under C6, no runtime PASS is asserted.

The on-behalf/response shape and required state representation are now bound. Exact E4
reference type is an external owner dependency, not a new C5 attachment design; actual
Access resource and E3 evidence physical references must be synchronized in delivery.
Next bind ordinary approve/reject/withdraw and rejected correction/resubmit command models.
No further story split, new role/default or ADR change. Existing scaffold typed API/error/
form patterns reused; no new UI surface. No code/tests/migration/grant changed.


## Approve, reject and pending-withdraw command models — 2026-10-23

**V1 binding of accepted 5.18-A/5.19-A; no new decision or withdrawal policy.**
All paths use the authenticated organization prefix. Server derives actor and current
resource authority; no employee/acting-for selector or trusted UI capability flag.
Request/cycle/step UUIDs and positive decimal-string revisions are distinct checks.

| Method / request suffix | Closed body fields | Required result extension |
| --- | --- | --- |
| POST `/requests/{request_id}/approve` | `operation_id`, `cycle_id`, `expected_revision`, `steps`, nullable `comment` | Common C request result with `command: approve`, plus immutable `decision_id` |
| POST `/requests/{request_id}/reject` | `operation_id`, `cycle_id`, `expected_revision`, `step_id`, `expected_step_revision`, `reason` | Common C request result with `command: reject`, `request_status: rejected`, plus immutable `decision_id` |
| POST `/requests/{request_id}/withdraw` | `operation_id`, `cycle_id`, `expected_revision` | Common C request result with `command: withdraw`, `request_status: withdrawn` |

`steps` is an ordered nonempty array of closed `{step_id, expected_revision}` objects,
one/two for the supported MVP presets. IDs are unique and order is actual responsibility
order; array order is part of frozen canonical input, not a set the server silently rewrites.
Approval comment is optional/null or plain text up to 4,000 Unicode code points; omission
canonicalizes to explicit null, but empty text remains distinct. Reject reason is required
nonblank plain text with the same limit. Preserve submitted text without silent truncation;
trim only for the nonblank check. Decision bodies are at most 32 KiB UTF-8, withdrawal 4 KiB.
Unknown fields/version/invalid counters fail safe validation. There is no private-comment
flag: comments/reason are visible through already authorized employee/history projections,
never included in notification payloads or compact operation receipts.

### Actual decision coverage and current checks

Backend current assigned detail provides the expected applicable step identities/revisions
for one explicit confirmation. If consecutive steps belong to the same currently authorized
person and configuration permits it, the expected approval set contains both under L-0158.
One confirmation records one immutable decision covering that actual set; do not commit only
one and require an identical second confirmation. Distinct-person configuration or missing
authority for either responsibility remains an invalid/incomplete route, not a hidden skip.

At protected execution, recompute that exact current set and compare request/cycle/step
revisions and current authority. A stale submitted set cannot silently acquire a new
responsibility or partially approve its old subset. Return typed changed-review/conflict
and let the existing confirmation refresh. Normal approval remains actionable-step-only;
L-0008 automatic later-step acceptance is the actual submission exception, not permission
for an ordinary decision to bypass another person's earlier required step.

Rejection identifies its actual actionable assigned step and preserves the prior valid
decisions/history. It rejects the current request/cycle and closes remaining unfinished
work/response with correct cancellation cause, never fabricating approval/rejection decisions
by other people. Manager status, on-behalf or funding permission alone does not authorize
this command. A permanent or explicitly appointed actor follows the already bound current
authority path; step membership, effective expiry and self-approval remain independent.

After a valid approval decision, B rechecks every independent gate. It returns current
in_approval while another decision/coverage/document/response/funding/date gate is unmet;
only actual B completion returns approved and consumes once. Neither `status: committed`
nor `decision_id` is itself final leave approval. A changed allocation needing renewed
consequential review is not silently approved using the older confirmation.

### Pending withdrawal and atomic accounting

Withdrawal requires actual employee owner/current `leave.request.own.manage`, including
on-behalf-created requests. Only submitted/in_approval is pending; approved/rejected/
withdrawn/cancelled are not eligible. No reason textbox, proxy flag, manager shortcut or
automatic conversion to draft/correction is introduced. E6 approved cancellation remains
separate. Ordinary draft and retained document/history references are preserved.

Reject/withdraw use the same 5.8-A release interface exactly once. Approval uses B and
5.8-A consume only on genuine completion; intermediate decision retains reservation.
The owning request/step/response/accounting/audit/receipt/notification-intent envelope is
one local commit. Untracked policies create no fictional entitlement release/consumption.
Competing approve/reject/withdraw/response settle a single valid lifecycle under the shared
current-input/employee/request protection, not last-write-wins state overwrite.

### Recovery and safe error details

Matching committed replay resolves C's original result after current permitted outcome
checks, before stale lifecycle/revision tests for a new execution. Replays do not change
comments/decisions/state or produce a second effect. A different operation against already
closed work is a typed conflict, not a fake new committed receipt for the previous actor.
Keep the original command/version/target/expected revisions/steps/text in fingerprint input;
server-generated decision time/ID and current observations are not new client inputs.

Use `leave.request_revision_conflict` with current request revision after resource access.
Bind HTTP 409 `leave.approval_steps_changed` with `{request_id, current_revision}` for stale
step set/revision; HTTP 409 `leave.request_not_pending` with `{request_id, request_status}`
for authorized current closed lifecycle. Confirmed authority loss is access_denied; failed
verification is authorization_unavailable/dependency_unavailable. Unauthorized targets
follow the non-disclosing missing/inaccessible resource policy; safe details never include
another employee's notes/medical content or a replacement actor identity outside scope.

Browser recovery uses original operation lookup first. Confirmed decision/mutation with
failed detail/queue refresh retries reads only; unknown outcome cannot trigger a fresh
operation or another decision. Current reads expose the permitted actual latest state,
separate from original receipt revision/status.

### Verification allocation and next model

5.18-A owns actual assigned scope, one-/two-step coverage, distinct/self/temporary authority,
reason/comment visibility, immutable decision and real all-gate/effect/rollback integration.
5.19-A owns employee-only pending withdrawal, response/task closure, preserved draft/history/
associations and release races. Their browser partners own exact confirmation/retained text/
current result/Retry and navigation. C/E3/5.8-A/B owner suites are reused, with 5.32 adding
only missing composition proof. These are testable contract cases, not runtime PASS.

Ordinary decision/withdraw body/result/error shapes are now bound. Next close rejected
correction save/resubmission models under L-0159 using the same form/cycle/recovery contracts.
No new permission/default/states, story boundary, shared UI surface or ADR change. Existing
typed API/error/current-review patterns suffice. No implementation/tests/migration ran.


## Rejected correction and resubmission command models — 2026-10-23

**V1 binding of accepted 5.20-A/L-0159; request identity and original history preserved.**
Use the same organization prefix, own-read/own-manage capabilities and current employee
ownership. Initial on-behalf capability cannot edit another employee's rejected request.
No new Drafts section, administrative draft or resubmitted request status.

| Method / suffix | Closed request / minimum response binding |
| --- | --- |
| GET `/requests/{request_id}/correction-context` | Read actual current request/base cycle/revision, permitted immutable rejection/prior submission and existing correction summary/input if present; does not create correction |
| POST `/requests/{request_id}/corrections/start` | Body `operation_id`, `base_cycle_id`, `expected_revision` (request). Create or resume that cycle's correction without overwriting current input |
| PUT `/requests/{request_id}/corrections/{correction_id}/input` | Body `operation_id`, `base_cycle_id`, `expected_correction_revision`, full versioned `input` envelope. Save permitted unfinished input only |
| POST `/requests/{request_id}/resubmit` | Body `operation_id`, `base_cycle_id`, `expected_revision` (request), `correction_id`, `expected_correction_revision`, `review`. No second full form payload |

IDs are UUIDs and revisions positive decimal-string bigints. Start/resubmit bodies max
8 KiB; save uses E1's 32 KiB body and field bounds. Versioned review/summary and exact own
unpaid acknowledgement use the existing own-submission model. Unknown fields/versions
fail safe validation. Explicit resubmit reads the saved correction, not unsaved browser
input or the employee's unrelated ordinary draft.

### Correction state and lifecycle guard

Select `leave.request_correction`: UUID id, org/employment/request/base-cycle scoped
references, state open/closed, positive correction revision, versioned nullable input,
nullable `resubmitted_cycle_id`, server creation/update and closure attribution.
Unique `(org_id,request_id,base_cycle_id)` supplies one correction per rejected cycle.
An open correction requires actual rejected current base cycle and non-null input; a
closed row has SQL NULL editable input and an actual new-cycle reference/closure actor/time.
Scoped local FKs prevent different-request/cycle/employment links. No automatic purge.

Initialize first correction from the permitted immutable rejected submitted input through
the existing form adapter, preserving actual date/format interpretation and useful note/
mode values. A resumed start returns its current correction revision without resetting
input. Keep the original rejection, submitted evidence and decisions unchanged. No new
cycle, allocation, reservation or request status/review-revision advance from start/save.
Correction revision starts at 1 and advances once per accepted save; matching replay
advances none. Saved corrections survive Close/reopen under ordinary accepted save UX.

Current ownership, correction revision and current request rejected/base-cycle identity
are checked together under short local request-then-correction row protection. A correction
save needs no funding/calculation/approval setup merely to preserve input, and does not
acquire ordinary draft_scope or create business commitments. It takes no later earlier-
phase business lock. Consequential resubmit follows complete dependency/employee protection
before locking request/correction in that same row order. No HTTP under those locks.

### Resubmit creates a new cycle once

After explicit current review, validate saved selected-mode input and all current ordinary
submission gates. Keep request ID; create a new cycle and fresh required decisions/route/
allocation, use 5.8-A for its commitment and B for eligible immediate completion. Prior
cycle decisions never satisfy this cycle. The old rejected cycle's commitment remains
released; do not release it again or reserve until explicit valid resubmission.

Close and clear the correction in the same local transaction as current-cycle pointer,
once-per-command request revision, accounting/evidence/audit/outcome/notification intent.
Pending result is in_approval; approved only through actual B completion. Closed correction
retains the old base and new submitted-cycle link permanently. Current rejected result
remains until resubmit commits; validation/changed review failure leaves open saved input.

This employee-owned resubmission uses **own initial unpaid acknowledgement** for the exact
new amount during confirmation, including a request originally submitted on their behalf.
It does not carry old acknowledgement forward or let a manager respond. New-cycle initial
rules apply; L-0151 later-change notice is not permission to skip initial acknowledgement.
Only actually authorized fresh own automatic decisions are recorded.

Historical and current correction attachments use actual E4 association/retention/context
interfaces. New-cycle required readiness is checked, old cycle associations retained and
cleanup protects current/in-flight references. Do not rewrite E4 mechanisms, detach history
or invent a new upload context to hide an unavailable owner contract.

### Outcome branches and stale execution

Extend C's existing request-target allowlist with `correction_start`, `correction_save`
and `resubmit`, version 1. Results keep common request/cycle/revision/status fields and add
`correction_id`, `correction_revision`; start also has disposition created/resumed, save
saved, resubmit resubmitted. Start/save result cycle is the actual rejected base; request
revision may stay unchanged while correction revision changes. Resubmit result cycle is
the actual new one and correction revision is its closed value. No third polymorphic
receipt target or second outcome store; the protected insert validates scoped correction
references and actual result/effect correspondence.

Canonical input binds submitted request/base cycle/correction identity and expected
counters/review or input as applicable, not generated new cycle/closure time. Matching
committed replay resolves before new lifecycle checks after current permitted access.
A delayed start/save from the old base cannot create input for a later rejected cycle;
a new edit uses its explicit current base/revision. Late save after resubmit cannot reopen
closed input or overwrite a new current cycle. A stale ordinary draft retry cannot target
these correction routes.

Use 409 `leave.correction_revision_conflict` with `{current_correction_revision}` and
409 `leave.correction_closed` with `{request_id, base_cycle_id}` after actual current scope
checks; current request revision conflict retains its common identifier/details. Invalid
current base/rejected state is a safe lifecycle conflict, not implicit new correction.
Unknown resubmit outcome retains the original operation/input and uses existing Retry;
confirmed resubmit with failed detail refresh retries only read. Re-authentication never
automatically resubmits. Correction save/exit uses existing inline Retry and exit-only
Stay/Close anyway; saved input closes without an extra confirmation.

### Verification and remaining C5 work

5.20-A owns actual create/resume/save/read/closure/cycle/state/recovery/atomicity and ordinary
draft isolation. Verify previous rejection/decisions unchanged, no pre-resubmit reservation,
current own acknowledgement, new-cycle accounting, late old start/save, competing saves,
rollback and lost-response replay; independent ledger/head/cycle/correction oracles.
5.20-B owns autosave/reopen/explicit review/confirmation and existing failure/navigation UX.
E4/C/8-A/B owner suites reused; 5.32-C adds only missing real producer composition.

Correction models are bound; external E4/evidence/Access consumer types and C6 executable
mapping remain required. Next remaining exceptional-funding and coverage/assignment/
appointment command models. No new policy, role/default, story split or shared screen.
Focused actual migration/role/lifecycle tests follow updated AGENTS; no schema whitelist
or mock substitute. No implementation/tests/migrations/grants occurred.


## Exceptional allocation and combined approval command models — 2026-10-23

**V1 binding of accepted 5.13-A/L-0150, with E3 proposal/ledger and existing C/8-A/B.**
Use the same organization prefix. Funding-only requires `leave.balance.override` and
actual request/employee scope. Combined action additionally requires current assigned
approval authority through the ordinary or explicit appointment path. No permission per
funding line, standalone balance-adjustment permission or actor selector is added.

| Method / suffix | Closed body / effect |
| --- | --- |
| POST `/requests/{request_id}/funding-exception-preview` | `cycle_id`, `expected_revision`, nullable `allocation`; no operation ID. Null asks E3 3.21 for its default proposal; supplied plan calculates that proposal. Read/calculation only, no reservation/grant/decision |
| POST `/requests/{request_id}/funding-exceptions` | `operation_id`, `cycle_id`, `expected_revision`, `allocation`, `reason`, `review`; funding-only actual command |
| POST `/requests/{request_id}/approve-with-exception` | Same fields plus closed `approval: {steps, comment}` using ordinary approval's current-step schema; one combined actual command |

The plan is an ordered array of closed `{leave_date, minutes, source}` lines. Minutes are
positive decimal-string bigints. Source is one of `{kind: balance, leave_type_id: UUID}`,
`{kind: discretionary_paid}` or `{kind: unpaid}`. No client authorizer/grant/portion ID,
negative amount, recurring allowance update or arbitrary source type. Per date/source kind/
balance type contribution is unique; backend verifies sum equals actual requested working
minutes on each date and whole request, with no contribution on nonworking dates. Mixed
working/nonworking requested ranges remain valid. Full body cap 256 KiB, no silent trimming
of lines; E3 actual policy/source rules decide which branches are permitted.

A balance line selects an allowed balance type/amount, not arbitrary internal entitlement
portions. The same authoritative E3 allocator chooses current valid portions in its existing
expiry/source-period/stable order and protects other reservations. Cross-type use must be
explicitly permitted; exception capability alone cannot override a disallowed source.
Discretionary paid is request-specific only and creates its actual authorized grant/effect
with provenance; unpaid is classification, not negative borrowing or an entitlement source.
Untracked policies retain their actual applicability/paid-unpaid semantics and create no
fictional entitlement effects to make this endpoint fit.

`reason` is required nonblank plain text, up to 4,000 Unicode code points, one reason for the
whole exception. Optional approval comment retains ordinary visibility/bounds; it is not
another required reason per line. E3's calculation/effect evidence records actual source,
amount, actor and the reason reference. Text alone cannot create or balance a funding effect.

### Preview and reviewed evidence

Preview returns current request/cycle/revision, current `allocation_evidence_id`, eligible
source summaries, proposed normalized allocation/paid-unpaid summary and `proposal_digest`.
It uses the same E3 source classifier and allocator as commit, without writing a snapshot/
reservation. Capability/action scope gates these financial details; no medical metadata
or unrelated employee balances are disclosed.

`review` is closed `{schema_version: 1, allocation_evidence_id, proposal_digest, summary}`.
Summary is the already bound normalized request summary, now reflecting proposed funding.
Digest is backend SHA-256 hex over the versioned normalized proposed consequential plan,
not a browser authority token. Recompute under protected current source/employee/commitment
inputs before commit. Preserve original request dates/mode/duration and independent gates;
funding action is not a date correction. Changed consequential plan requires fresh existing
review; source unavailability is neither zero entitlement nor an approved default unpaid plan.

### Replace active allocation once, then optionally approve

5.13-A extends the existing commitment interface with its actual reviewed active-allocation
replacement. The same commitment identity/cycle remains active until B genuinely settles
it. Retain old allocation evidence, append actual new immutable evidence/effects and advance
current commitment/request revisions once for the owning command. Do not edit historical
reserve lines, settle/recreate the cycle or create another balance/commitment store.

The E3 request extension adds explicit `request.reallocate` effect with previous/revised
allocation evidence and actual released/reserved contribution roles; both line amounts
remain positive. Request-specific discretionary paid grant uses its actual immutable E3
grant source/event, with causal identity and ownership tying it to this request decision.
Neither effect counts derived earning twice or silently changes recurring entitlement.
This source-specific reallocation/grant extension is owned here, not retroactively added
to 5.8-A's original three effects or a parallel generic funding engine.

Funding-only records no human approval decision. It may nevertheless allow B to complete
from already valid decisions when this is the last real gate under L-0154. Combined action
records one actual permitted ordinary decision alongside funding effects; stale approval
scope/steps or invalid source fails the entire combined transaction. Never commit funding
then return approval denial as partial combined success. B still checks all independent
gates; outer committed or funding result does not necessarily mean Approved.

Current previous/revised paid/unpaid consequences, actor/reason and required employee notice
are retained under L-0151. A genuinely outstanding initial response remains employee-only
and uses current amount; L-0162 zero closes without consent and later same-cycle increase
never reopens it. Existing valid decisions and approved-request protections are not rewritten.
This command operates pending requests; E6 corrections remain separate.

### Outcome, errors and evidence ownership

Add request-target `funding_exception` and `approve_with_exception`, version 1, to C's closed
command/result union. Both return common request/cycle/revision/status plus immutable revised
`allocation_evidence_id`; combined also returns `decision_id`. Receipt carries no reason,
full allocation, private source balances or copied employee acknowledgement. Canonical input
binds exact submitted plan/reason/review/steps/comment, not generated grants, timestamps or
current observations. Matching replay returns original distinct effect references with no
new grant/reallocation/decision, even if current request status later changes.

Use existing request/step/closed lifecycle errors and HTTP 409 `leave.funding_review_changed`
with `{request_id, current_revision}` after permitted access for changed allocation evidence/
proposal. Invalid/disallowed source/amount/date is safe validation with allowlisted field/
rule identifiers; it is not another permission-per-source check. Unknown outcome retains
original frozen operation; no fresh funding action or retry plan edit until resolved.

5.13-A owns actual source/plan/authority/typed preview, active replacement/grant effects,
combined rollback, conserved date/minute allocation, duplicate/race/initial-response and
current B integration. 5.13-B extends existing decision detail/review/browser, no separate
referral or funding-permission transfer UI. E3/C/8-A/B/ordinary decision suites remain their
owners; 5.32 adds only missing composition. Exact E3 event-role/source schema synchronization
and C6 acceptance paths/order/size remain required; this model is not runtime evidence.

No new business source, role, approval tier or story boundary. Existing typed review/reason/
transaction/error patterns reused; accepted ADRs unchanged. Next coverage exception and
reassignment/appointment command models. No implementation/tests/migration/grant changed.


## Coverage exception and selected reassignment models — 2026-10-23

### Coverage exception: bounded gap, no assigned approval

Bind approved 5.5-A to `POST /requests/{request_id}/coverage-exceptions` under the existing
organization prefix. Closed body: `operation_id`, `cycle_id`, `expected_revision`, `reason`
and `review: {schema_version: 1, coverage_digest}`. Reason is nonblank plain text up to
4,000 Unicode code points; total body max 32 KiB. Current capability is
`leave.workflow.coverage_exception` plus actual applicant/request/organization scope.
No approver selector, policy-disable flag, client accepted=true or proxy decision field.

Current authorized coverage review supplies the existing 5.3 rule result: actual applicant
responsibility identities, affected absence periods and uncovered gaps. Backend digest
binds that versioned exact scope and current request/cycle to the review. Recalculate under
actual dependency/employee protection; changed gap/scope/revision requires renewed existing
review. A failed check cannot become an exception over unknown future gaps. No extra
human appointment/acceptance workflow or unbounded bypass token.

Record an immutable Leave-owned coverage-exception record with UUID/org/request/cycle,
actual authorizer/time, reason and retained exact responsibility/period/gap evidence.
Scope linkage is actual source responsibility, not merely pending step IDs: future work
that may arrive during that covered absence remains part of the established coverage rule.
The exception does not appoint anyone, approve another step, hide the gap or waive funding/
response/employment/doc checks. A different cycle/responsibility/period is not authorized
by a historical exception. Applicable recorded exception is evidence of an actual prior
authorized action, not a live permission transferred to the employee.

Actual command reassesses B through L-0154; prior valid decisions may complete only if
all current gates now pass. Add request-target `coverage_exception`, version 1, returning
C common result plus `coverage_exception_id`. The original immutable receipt cannot be
rewritten if a later command finalizes or changes gaps. Changed review uses HTTP 409
`leave.coverage_review_changed` with safe `{request_id, current_revision}`; unavailable
verification remains retryable, not definite missing cover. Existing current access/
revision/unknown recovery semantics apply. 5.5-A owns real scope/evidence/B/rollback tests;
5.5-B consumes existing review/detail surface, with no extra permission screen.

### Manual reassignment: exact request/step scope

Bind a per-request command `POST /requests/{request_id}/reassign-approver`. Closed body:
`operation_id`, `cycle_id`, `expected_revision`, `steps` (ordered closed step ID/revision
objects), `target_membership_id` (positive opaque decimal string), `reason`, and
`review: {schema_version: 1, transfer_digest}`. Reason max 4,000 code points; body max 32 KiB.
Require current `leave.workflow.reassign`, actual selected unfinished scope and target's
current explicit approval eligibility. Resolve target membership/account/actor through
its authorized owner API; a client target ID or reporting relation grants no right.
No implicit temporary appointment or permanent role/grant mutation.

Review binds actual selected request/cycle/unfinished step revisions, current source/
target assignment and current permitted outcome. Reload under protected coordination;
completed/closed/stale step or authority change is conflict, not partial reassignment of
only the still-valid selected subset. A matching per-request command moves its exact
selected steps atomically with revisions/audit/receipt/required recipient intent.
Unselected/completed steps, independent final responsibilities, policy/funding/decisions
and required gates remain. Same unfinished step preserves its waiting clock/escalation;
new recipient gets existing assignment notice, not a fresh escalation. No duplicate
reassignment log or another human approval decision.

Add request-target `reassign_approver`, version 1, returning C common request result and
permitted current assignment reference through actual current read; do not copy the full
selected request/detail list or reason into a compact receipt. Same identity with changed
steps/target/reason is mismatch. Use `leave.approval_steps_changed` or request revision
conflict as appropriate; target verification unavailable is not no eligible people.
Actual 5.24-A owns common protected transfer, reused by appointment/return/source consumers;
those producers retain their own real causal/effective integration tests.

### Multiple selected requests: proposed per-request outcome rule

**User agreement pending for this remaining batch consequence.** Recommend preserving
atomicity within each request, with a distinct retained operation identity per selected
request. Across the selected group, report each committed/conflicted/unresolved item rather
than promise one cross-employee all-or-nothing transaction. One stale/closed request does
not roll back already committed valid transfers. Retry only the original failed/unresolved
items after resolving their original identities; never retransfer successful items.

Keep the exact reviewed selection; later filter/list changes cannot add employees or
requests. Present a concise result on the existing selection/detail surface with the items
needing attention, not a background-job/progress dashboard. Completed transfers remain
truthful when a later item fails. This proposal concerns multiple selected requests only;
all selected steps in one request still commit together or not at all.

The per-request schema above is a technical baseline; do not mark multi-request result
behavior accepted or its exact batch orchestration complete until this checkpoint is
agreed. If accepted, 5.24-A/B bind group/item correlation and recovery against these
per-request commands without a second outcome store. No new boundary proposed; count 80.
Coverage exception schema is bound independently of this open batch choice. Appointment
create/extend/end models follow after it. No implementation/tests/migrations/grants.


## Selected manual reassignment outcomes accepted — 2026-10-23

User agreed the preceding batch proposal; [L-0165](../decisions/0165-per-request-outcomes-for-selected-reassignment.md)
records it. Earlier pending agreement text is superseded for manual selected reassignment.
Per-request command schema stays unchanged. Each frozen reviewed item binds request/cycle/
steps/target/reason/review and a distinct original operation ID; a changed filter cannot
alter that item list. A group correlation ID is diagnostic/navigation context, not a new
business authority, transaction or separate outcome store.

The existing browser selection result has item states `committed`, `conflicted`, `denied`,
`unresolved` or `not_attempted`. Committed includes its exact C acknowledgement; other
states include only permitted safe errors/references. `not_attempted` describes a selected
item never sent in this execution, not proof that a previously sent operation failed.
Timeout/unparseable/connection loss remains unresolved. API responses continue to use C's
committed/unresolved envelope and normal typed HTTP errors; these item presentation states
do not become request lifecycle or operation-receipt statuses.

Use serialized per-request execution initially, bounded by each actual command deadline,
with the existing selection surface showing accumulated actual results. Stop sending new
items on whole-context authentication/admission loss; preserve prior successes and safely
record remaining not_attempted. An item-local conflict may leave other selected items
eligible. No cross-request DB transaction or unbounded server request covers the whole list.
This is not the withdrawn local-setting impact worker/progress-screen design.

On interruption, recover each sent unknown item's original operation before any reissue.
Keep frozen item identity/input in the already supported same-user/organization form and
operation recovery context; do not store business reasons in return URLs or promise survival
of arbitrary unsaved browser state. If input is unavailable, do not invent its payload or
issue a replacement action while original outcome is unknown. Confirmed successful items
retry only current detail/list reads. Rejected stale items require actual refreshed review
before a changed operation. No repeated assignment notice or rollback of completed items.

5.24-A owns per-request atomic transfer and real outcome/race contracts; 5.24-B owns bounded
selected-item orchestration/result/return and re-auth scope handling. Existing operation
recovery owns its persistence limits; exact supported context/test paths remain C6 binding.
No mandatory server bulk-job/manifest table or parent outcome is introduced. Other command
families do not inherit these batch semantics automatically. Next actual appointment
create/extend/end/current expiry schemas. Count remains 80; no implementation/tests/grants.


## Temporary appointment creation and lifecycle models — 2026-10-23

**Binding approved 5.21/5.22/5.23 and their real 5.24 transfer consumers.** Use existing
organization prefix and current `leave.workflow.manage` plus exact responsibility/subject
scope. Chosen original/appointee identities are current organization memberships, not
necessarily employments or permanent Approver roles. No automatic candidate recommendation,
appointee acceptance or extra absence-fallback checkbox.

### Creation and period

`POST /approval-appointments` accepts `operation_id`, `principal_membership_id`,
`appointee_membership_id`, `responsibility_ids`, `starts_at`, `ends_at`, `reason`,
`selected_pending_steps`, `return_authorization` and `review` only. Membership IDs are
positive decimal strings; responsibility/request/cycle/step IDs are actual verified UUIDs.
Reason is required nonblank plain text, max 4,000 Unicode code points. Body cap 256 KiB.

`responsibility_ids` names actual normal configured responsibilities of the original
approver from the completed rule/coverage contract, not arbitrary role strings or only
current queued step IDs. It covers new work arriving for those responsibilities during
the interval. Current configured membership/source changes remain protected; L-0160
permanent replacement removes only its superseded responsibility, not unrelated cover.

The effective interval is half-open `[starts_at, ends_at)` using explicit UTC instants;
start must precede end. Existing date-based UI normalizes the chosen inclusive end date
to the next local date's start under its declared coverage/work-timezone review context,
retaining original dates/zone/version and resulting instants. No browser/UTC fallback or
new universal organization-timezone setting. Backend eligibility checks actual interval,
known absence, self/conflicting scope and overlap; sequential appointments may jointly
cover a larger absence. These checks cannot declare a candidate eligible on unavailable
membership/absence evidence.

`selected_pending_steps` is an exact list of closed request/cycle/step IDs and their
expected request/step revisions, grouped by request. Empty is legitimate: future work
still uses the bounded appointed responsibility. Selection cannot expand from a refreshed
queue/filter. `return_authorization` is the closed disclosed `return_to_principal` intent,
subject to actual eligibility/continuing-absence/source precedence at return. It is not
an unconditional transfer order or another permission flag. `review` binds schema version 1,
normalized interval/responsibility/selection/return consequence digest and current source
revision evidence. The actual current reviewed source facts are rechecked before creation.

### Appointment and selected work have truthful separate progress

Creation atomically records appointment identity/scope/interval/reason, reviewed selection,
conditional return authorization, current outcome/audit/notice and durable start/expiry
intent. It does not claim every future selected step is already transferred. This is the
already approved creation/start contract, **not automatic inheritance of manual batch
L-0165**. No distributed Access grant is committed; explicit Leave appointment is authority.

Actual effective-start processing belongs to 5.21-A. At applicable start it rechecks each
selected request's current unfinished responsibility/source and applies its protected
within-request transfer or records truthful no-longer-applicable/needs-attention. Closed
work is not reopened; a new unrelated assignee/source is not overwritten. Persist durable
causal item progress and original selection so restart cannot retransfer completed items
or silently add new pending work. The appointment can remain valid for its other/new
responsibilities when one selected old request no longer qualifies.

For an effective-now creation, the API may execute bounded start work before returning,
but its compact committed creation result must remain truthful if some selected effect
still needs recovery. The existing detail/result surface distinguishes created/scheduled
appointment from actual selected-work results, without a new job dashboard. At an effective
boundary, actual decision checks cannot authorize a superseded old assignment merely
because start/return work is delayed. Appointee also needs actual valid assigned work;
future/expired interval never supplies early/late rights.

### Actual owned state and service work

The first actual eligibility/authority reader 5.2 introduces the needed
`leave.approval_appointment` representation and current interval/overlap reads on controlled
valid records. 5.23-A adds actual due-work/expiry/conditional-return integration; 5.21-A
later proves actual production creation/start integration. Record UUID/org/principal membership and
verified actor/appointee membership and actor, scoped responsibility identity references,
starts/ends, optional actual early-ended instant, positive revision and server attribution.
Retain immutable initial appointment/selected-return evidence and actual later change
history through existing activity, not duplicated assignment logs. Approval visibility
and decisions record whom the temporary actor acted for.

Use actual owner-specific due work for start/expiry/return with appointment ID/revision,
closed work kind, protocol version and stable causal identity/item progress. It is not a
notification transport event falsely performing business actions or a universal task engine.
Old due items recheck current revision/source applicability and cannot extend/revive rights.
No separate stored active flag can override effective instants/early end/current membership.

Approval-subject guard identity must support the approved nonemployee member case: bind
kind 09 `approval_subject` to the verified durable account actor UUID, **superseding its
earlier employment-UUID description**. Resolve current member/actor identity through owner
HTTP; keep employee mutation/earning/date guards keyed by employment separately. No synthetic
employment/person or universal key is created just to lock an appointee. Actual original/
temporary actor and old/new responsibility memberships share the corrected guard protocol.

### Extension, early end and expiry

| Command | Closed body / effect |
| --- | --- |
| POST `/approval-appointments/{appointment_id}/extend` | `operation_id`, `expected_revision`, `new_ends_at`, `reason`, `review`; current unexpired appointment, later end, revalidated extended interval/overlap/absence/return consequences |
| POST `/approval-appointments/{appointment_id}/end` | `operation_id`, `expected_revision`, `reason`, `review`; end now using server effective instant, even if no eligible return destination exists |

Extension preserves identity/original start and replaces current expiry/return due evidence
under a newer revision; old worker intent cannot end it prematurely. An already expired
appointment needs the actual permitted new appointment workflow, not silent revival.
Early end terminates specified authority immediately in current checks, then uses actual
conditional original or separately appointed valid replacement scope; no free target/grant
selector or automatic substitute. Unresolved return remains pending/attention, not continued
temporary power. Preserve prior valid decisions, unrelated cover and permanent replacement.

Expiry derives from actual interval independent of worker lag. 5.23-A rechecks authorized
return destination, membership, continuing absence, current supervisor and appointment
revision; transfers only still-applicable unfinished work or records recoverable attention.
L-0156 waiting clocks/escalation remain unchanged for the same step. Empty queue does not
prove continuing uncovered responsibilities are resolved. No auto extension or cancellation
of already approved leave. All local effects/history/outcomes/intent retain their atomic
owner envelopes and original causal recovery, with current rechecks after restart.

### Typed receipt target and models

Add explicit `approval_appointment` branch to existing Leave receipt union in the actual
first human appointment consumer. Require non-null scoped `appointment_id`, null draft/
request target fields, and nullable `employment_id` only for this branch because a member
need not be an employee. Existing draft/request branches retain non-null scoped employment
and their original FKs; do not weaken them globally or create a synthetic target. The
appointment FK is actual local `(org_id,appointment_id)` with retained identity/deletion
protection. Caller/organization/operation unique key and immutable receipt behavior stay.

Commands `appointment_create`, `appointment_extend`, `appointment_end`, version 1 return
compact `{command, appointment_id, revision, disposition}` with created/extended/ended
respectively; no copied dates/selection/authority claims. Current GET
`/approval-appointments/{appointment_id}` supplies permitted actual interval/revision/
responsibility/selected-result/return attention separately. Source input canonicalization
binds original exact selection/period/review/reason and expected revision; server-generated
appointment/end/effect IDs and clocks are not changed retry input. Matching receipt survives
later expiry/change without reapplying its original action.

Safe errors reuse shared access/dependency/mismatch/busy/validation, with 409
`leave.appointment_revision_conflict` `{current_revision}` and
`leave.appointment_review_changed` `{appointment_id, current_revision}` after actual access.
Creation changed review has a separately closed principal-membership detail variant; no
candidate sensitive absence or medical data is leaked. Worker unresolved states stay actual
owner work outcomes, not fabricated public committed appointments.

### Verification and next C5 closure

5.23-A owns actual expiry/current deny/conditional return and obsolete-work cases first;
5.21-A owns create/start/selected-scope/receipt producer integration, 5.22-A/C their actual
extension/end race/fencing. Browser partners consume those typed current/result models.
Test chosen member without employee/permanent role, interval boundaries, normal fallback,
current selected versus completed/reassigned work, source replacement during cover,
extend-versus-expiry, early end with no destination, lost response/restart and actual
receipt branch integrity under restricted roles. E3/C/transfer owner cases reused; 5.32-I/J
add missing composition. No broad schema whitelist or mock-only permission/rollback proof.

Appointment action shapes are bound; exact rule responsibility/interval source models and
actual Access/People/worker adapters remain owned predecessor interfaces to synchronize.
Next consolidate remaining read/query/source-model references and C5 closure gaps before
C6 final atomic coverage/order/sizing. No new role, user workflow, story boundary, ADR
policy change or implementation. No tests, grants, migrations or live settings changed.

## Read/source contract consolidation — 2026-10-23

[e5-read-models.md](e5-read-models.md) owns residual query/detail/history/source mapping,
common bounded pagination and the finite C5 G1–G6 gate register. It extends current request
GET instead of replacing first-use reads, introduces no new product surface and does not
claim a complete OpenAPI artifact. Remaining material choice: 5.17 team temporal grouping;
query unions, preference adapter, upstream types and worker/event adapters remain explicit
technical owner work. Current appointment and manual selection contracts unchanged.

## E5 availability grouping adoption — 2026-10-24

L-0166 and e5-read-models close current-versus-as-of grouping for 5.17. Current People
reporting facts do not supply read authority, broaden temporary scope or change approval
routing. Absence-state inclusion proposal remains open in the read contract; no capability
or command schema changes. Other C5 technical gates and C6 remain open.

## Collection and simple preference binding — 2026-10-25

Read contract now binds remaining queue/own-history/My Leave/attention collection fields,
filters/order and minimal Leave-owned per-account/org Calendar/List preference. The latter
uses current own-read/admission and revision-protected desired-value PUT, not consequential
receipt/action authority. Existing request commands, role defaults and medical permissions
unchanged. G1/G2 planning design bound; G3–G6 and C6 remain open.

## G4 owner type synchronization — 2026-10-25

Access owning admission contract now types explicit Leave context and assigned/on-behalf
resource branches; membership IDs remain positive decimal strings. Content owning contract
now defines exact E4 `attachment_refs` association ID/revision and draft/on-behalf-input/
correction/submitted-cycle targets, with real 5.12/20 extension ownership. Own submission
uses actual saved draft associations; no second client form truth or Content pipeline.
Shared identity/People contract selects `people.employment.manage` with organization-
employments resource scope for existing E2 authority; it remains independent from Leave
permissions. G4-P shared catalog/app-admission registration is explicitly unresolved and
requires a compatible owner design before adoption. No default grant/new app toggle is
inferred. G5/G6/C6 remain open; no implementation or actual wire-generation claim.

## G4 shared admission adopted; reuse correction — 2026-10-25

P-0063 accepted. Existing KDG/platform Access registry/owner registration/org admission
mechanics are already implemented and must be reused. Current KDG-specific HTTP/SQL
check does not yet implement People authority. Keep only actual People check/resource/
consumer/adoption deltas in predecessor sizing; no duplicate foundation or new grants.
G4 design bound, runtime consumer verification remains delivery work. Next G5/G6/C6.

## G5 actual timed-work and error models — 2026-10-25

Owning e5-timed-work-and-errors now specifies typed due-work payload/claim/result, actual
appointment revision fencing, reminder/escalation occurrence clocks and coverage gap IDs.
It constrains safe error detail variants without renaming existing command errors. Shared
notification owner binds explicit organization-scoped Leave timed-event acceptance, not
implicit adoption of the account-only Scribeswell branch. No new command/role/UI or worker
engine. G5 design bound, exact runtime/generated artifacts and C6 final sizing remain.

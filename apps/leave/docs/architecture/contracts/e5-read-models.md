# E5 read models and remaining contract gates

E7 consumer proposal, 2026-10-25: the
[E7 read/report/audit contract](e7-overview-reports-and-audit.md) reuses these audience,
source, pagination and current-detail interfaces. It adds only the wider organization
overview and report/audit consumers, retaining E5 ownership of personal history,
approval availability and actual waiting/coverage facts. Its proposed temporal report
choices do not change accepted E5 current-team grouping. No runtime implementation.

**Status:** Consolidated technical read baseline; explicitly listed gates remain open.  
**Date:** 2026-10-23  
**Owner:** Leave API, with Access/People/E3/E4 source owners

This contract binds existing read consumers to their actual sources. It adds no product
screen, permission, history store, worker or implementation authorization. Product truth
remains Features and accepted ADRs. This is not a claim that complete OpenAPI or runtime
adapters exist. [Command models](e5-capabilities-and-commands.md) own mutations and receipt
results; [core state/read](e5-request-command-and-finalization.md) owns current request
identity. Later extensions below must preserve first-use minimum reads.

## Common read contract

All browser business reads pass through the authenticated Leave API under
`/api/v1/organizations/{org_id}`; private, `Cache-Control: no-store`. Current Access
admission plus actual resource predicates apply on every request, including pagination.
Temporary approval uses the explicit appointment/admission path in the command contract,
not a failed permanent-capability fallback. Query parameters select within permitted
scope; they never choose an audience or grant it.

Use UUID identities, positive decimal-string bigint revisions, ISO civil dates and UTC
instants from the owning contracts. Required local request/cycle/decision/allocation
fragments come from one consistent committed read. Remote owner observations occur outside
write locks and carry their source revision/observation evidence internally. A query is
not an atomic snapshot across services; required verification failure returns a safe typed
failure, rather than silently mixing unknown authority with cached business data.

A collection response is `{items, next_cursor, empty_reason}`. `next_cursor` is an opaque
nullable continuation. `empty_reason` is null with items, otherwise `no_items` or
`no_matches`; the latter requires a verified nonempty unfiltered authorized collection.
Do not expose unfiltered counts or existence outside current scope. Default page size 25,
maximum 50. Stable ordering ends in actual resource UUID as tie-breaker; continuation binds
organization, current actor, route, filter/sort values and last order tuple. It confers no
read authority. No promise of a frozen multi-page snapshot under concurrent writes:
clients deduplicate by identity and refresh to obtain current ordering. Invalid/mismatched
cursor yields typed invalid-query response without business contents.

Empty, denied and unavailable remain distinct. No empty or zero substitutes for failed
Access/People/source checks. Supporting panels load independently where contracts permit;
failed advisory team data alone does not add an approval blocker. Read retry never repeats
a confirmed command. Reads have no reserve/consume/release, approval or finalization effect.
Do not hold database transactions across remote HTTP calls to manufacture read consistency.

## Existing detail and formal history

`GET /requests/{request_id}` retains the existing common fragment: request ID, current
cycle ID, revision and actual lifecycle status. Use server-selected allowlisted models:

| Projection / first consumer | Source and permitted extension |
| --- | --- |
| Own minimum, 5.11-A; residual detail, 5.30-A | Current cycle's normalized summary from command contract, submitted note, current funding evidence, concise outcome, direct rejection reason and currently applicable employee actions |
| Assigned minimum, 5.18-A; residual inspection, 5.16-A | Same actual request/cycle, permitted calculation/allocation, explanation, formal history and provision/readiness flags; actual current assigned authority required |
| Administrative, actual source/attention consumer | Only that consumer's current explicit action/read scope and minimum consequence/context projection; source-management authority does not become broad unrelated request read |

Action availability is an array of closed command identifiers from the command contract,
with the actual current target/cycle/revision. It is presentation evidence, not permission
for a later mutation. Do not infer E6 cancellation from request status or own.manage.
Own status distinguishes `awaiting_approval` and `response_required` from actual current
response evidence; routine approver absence/cover diagnostics are not in that projection.
Medical metadata/bytes never become ordinary queue/calendar fields. Sensitive reads use
E4 routes and both actual request authorization and separate sensitive capability.

Select `GET /requests/{request_id}/history`, first residual consumer 5.30-A. Optional
`cycle_id` restricts to an actual cycle of that request, never an arbitrary submitted ID.
Use the collection envelope ordered by cycle sequence, decision time, decision UUID.
Each formal decision entry carries decision ID, cycle ID/sequence, actual outcome, actual
actor ID/display attribution, UTC decision time, recorded comment and nullable acting-for
attribution from immutable decision evidence. No fabricated employee attribution or hidden
approver deliberation. Distinguish step acceptance from overall request approval through
actual step responsibility evidence and actual cycle outcome, not a second inferred state.
One L-0158 decision appears once with its covered responsibilities, not once per linked
step. Retain earlier cycle submission/rejection evidence through actual immutable records;
cycle selection cannot reinterpret it as the current submission. History is not an activity
log substitute for all source actions; existing source activity/audit remains its owner.

## Query and composition ownership

Routes below are selected technical names for already approved surfaces. Unresolved
semantics in the next section are explicit readiness gates, not frontend discretion.

| Existing consumer | Selected read surface | Actual source / retained boundary |
| --- | --- | --- |
| 5.16-A/B actionable queue | GET `/approval-queue` | Current required approval steps and current authority; exclude completed/omitted/later steps. Ordinary and temporary rows unified. Longest-waiting default, optional earliest-leave ordering; L-0156 clock. Employee search/type/date/exception filter exact fields in G1 |
| 5.17-A/B advisory availability | GET `/requests/{request_id}/team-availability` | Authorized request dates, People-owned supervisor grouping over HTTP, Leave absence records and privacy-safe date/duration-only projection. Temporal grouping/state/count semantics in G1 |
| 5.27-A/B manager attention; 5.28-A/B extends | GET `/attention` and `/attention/{kind}/{id}` | Closed kinds `approval_escalation` and `coverage_gap`. Actual retained escalation occurrence or coverage issue identity. Separate kind branches, not fake requests or new task engine. Current scoped request references/actions, historical escalation retained after active resolution |
| 5.29-A/B own calendar/list | GET `/own-requests` with required year and view `calendar` or `list` | Same actual own request inclusion for both; request intersecting selected year appears with original identity/full interval. No duplicated full history response; calendar attachments excluded. Year bounds extend for retained records/rehire and no invented end bound |
| 5.31-A My Leave | Extend `/own-requests` with approved pending/upcoming section queries | Actual request/current response sources; required response priority. Independent request/balance/draft loading, existing E3 balances and E1 draft routes, no combined availability requirement or new dashboard truth |
| 5.29-A/B presentation preference | Existing simple preference owner, exact adapter in G2 | Calendar/List per current account and organization, immediate preference saving. Not an administrative Save form or draft. Reopen current year when within known bounds |

Rows/detail reuse normalized summary, current request/cycle/revision and current action
mapping rather than raw ORM objects. Queue adds only permitted employee/type/dates/duration,
current waiting evidence, acting-for/end and applicable notice/backdating/override/overdue
flags. Generic colleague entries omit type/note/comment/document and revealing style/filter
keys at the API boundary, even when a browser would hide them. Detailed colleague fields
require separate actual detailed-request authority. No exact time-of-day is inferred from
half-day/hour duration. Attention actions map to existing capabilities/commands; gaps remain
visible despite an exception or empty queue. No new dismiss or automatic substitute action.

## Source-model reference map

| Source fact / consumer | Authoritative model or contract / delivery owner |
| --- | --- |
| Request/cycle/step/decision/current authority and coordination guards | e5-request-command-and-finalization.md; actual 5.10-A, rule owners and protected source/assignment writers. Guard 09 uses durable actor UUID; no employee assumption for appointed member |
| Commitments, reserve/consume/release and funding evidence | e3-request-accounting-interface.md; E3 ledger/calculation first, actual 5.8-A extension, 5.13-A reviewed reallocation/grant extension; no second balance store |
| Corrections, employee response, appointments and original operation results | e5-capabilities-and-commands.md and referenced first consumers; correction input distinct from immutable cycles, appointment target not fake employment/request |
| People employment periods and supervisor facts/changes | Platform identity-access-employment-e1.md and people-leave-change-coordination.md, adopted P-0062; People HTTP owner, no direct database access. Shared grouping facts confer no Leave authority |
| Access current grants/admission and explicit appointment context | Platform application-admission-and-discovery.md plus C5 capability models; actual Access consumer owns compatible context/resource/catalog extension |
| Policy/version/assignment, employee work overrides/default/profile/calendar inheritance | Actual E2/E3 source models and C3 source-writer matrix in core E5 contract. 5.15-I includes initial 3.28 assignment; K includes period-add/rehire consequences. No copied employee master or alternative effective chain |
| Attachments/provision/readiness/private bytes | E4 association/read contract and 4.4/4.13; 5.9 policy checks and actual submit/correction consumers. No E5 upload/cleanup pipeline |
| Reminder/escalation/coverage current facts and delivery | Actual 5.23/25/26/27/28 and E3 notification contract. Durable due work distinct from outbound delivery; retain identities and current relevance, not rebuild an outbox on recovery |

References here do not certify an upstream contract as complete merely because a document
exists. The actual interface and consumer test ownership are tracked below and in C6.

## Finite remaining C5 gates

| Gate | Remaining concrete result / owner | Closure evidence |
| --- | --- | --- |
| G1 — query semantics and final field unions | Leave 5.16/17/27/28/29/31 owners: exact filters/date matching, team temporal grouping and included request states, deduplicated counts, own status/date categories and attention branches | Bind the explicit 5.17 temporal choice with user; then closed query/response examples and privacy/empty/failure cases. Reuse agreed rules rather than re-review all story ACs |
| G2 — preference adapter | 5.29-A existing application preference pattern: exact storage owner/key, write/read/error contract and fallback | Verified current pattern or explicitly minimal Leave-owned implementation with account/org isolation; no assumed nonexistent shared settings service |
| G3 — source/rule interfaces | Actual E2/E3/5.1–9 owners: exact responsibility IDs, interval/source revisions, effective inheritance/date allocation and impact projections consumed by E5 | Link concrete owning schema/operation/variant for each C3 source family; list missing upstream fields there, not duplicate their specification in E5 |
| G4 — cross-owner types | People management capability names/actor-target scope, Access context/resource extension and E4 on-behalf/correction association types | Actual owning contract edits, current action predicates and producer/consumer acceptance allocation; a service key or existing file is not proof |
| G5 — timed work/events/errors | Actual appointment, reminder, escalation and source worker owners: closed event payload version/causal identity/claim/result/retry variants, attention issue identity, safe error-detail unions | Bind to real E3 worker/notification contract; retain supported queued versions and actual restricted worker scope, no generic engine |
| G6 — complete wire artifact ownership | Each first API consumer: OpenAPI schema fragments/generated client/error adapter ownership covering above selected models | Exact production artifact/package generation/check strategy in C6; no assertion that schemas/code generation or Leave packages already exist |

G1–G6 are contract closure tasks inside existing delivery boundaries, not six new stories
or product features. C5 is not closed. After the material G1 choice, technical items may
be consolidated without requesting repeated approval of settled policy. C6 still owns
atomic requirement-to-acceptance allocation, real package/command strategy, external and
internal delivery order, duplication reconciliation and final single-agent sizing. Runtime
failing-first acceptance belongs to authorized delivery, not a requirement to implement
Leave merely to finish planning. No runtime tests, migrations or grants performed here.

## Current team adopted; absence-state proposal — 2026-10-24

User accepted [L-0166](../decisions/0166-current-team-for-approval-availability.md).
G1 temporal grouping is closed for E5 5.17: current effective employee supervisor group
from People, requested dates for absence intersection, actual current permitted scope.
Keep source revision/observation evidence, with no persisted team snapshot or inferred
future membership. This supersedes the earlier pending temporal-choice notes only.

**Proposed next G1 choice, not yet accepted:** Include approved absences and pending
submitted/in-approval requests as distinct approved versus pending categories, so reviewers
can see both confirmed and competing planned absences without treating a pending request
as approved leave. Exclude unsent drafts and rejected/withdrawn/cancelled requests, and
exclude the request under review from its own colleague comparison. Preserve generic
colleague labels and existing field permissions; a pending marker must not expose type,
reason, documents or unrelated request detail. Do not assume acceptance or publish final
state-union/count examples until the user responds. Other G1–G6 gates and C6 remain open.

## Availability state and summary binding — 2026-10-24

User accepted L-0167; the preceding state-inclusion proposal is now adopted. This closes
5.17 temporal grouping and included lifecycle categories in G1, not the other G1 consumers
or upstream People/work-profile interfaces. Actual 5.17-A/B retain API/browser ownership.

### Query scope and response

`GET /requests/{request_id}/team-availability` accepts only the common `limit`/`cursor`
options. Resolve current request/cycle/revision and its actual requested dates server-side;
no caller-supplied employee/team/date range can widen this request-review query. Check
actual review and team scope, then current People grouping under L-0166. Temporary-only
review access does not itself grant team visibility. A denied team read returns the safe
panel denial, not an empty group or a newly inferred grant.

Approved request -> category `approved`; submitted/in_approval -> `pending`. Other lifecycle
states and drafts excluded. Select each request's current cycle exactly once, and exclude
the reviewed request ID. Intersect eligible requested leave dates with the review dates;
non-working dates alone are not an absence. Use the owning normalized per-date duration
from 5.6/current cycle evidence, including unpaid/untracked leave, not just funded balance
lines. No inference from ledger deductions, notice state or an unsent correction.

Response adds `request_id`, `current_cycle_id`, `revision` and a `summary` to the common
collection envelope. Items are one per permitted colleague employment, ordered by stable
employment UUID, with permitted display name and `dates`. Each date element contains its
civil `date` and a nonempty `categories` array. Each category element contains `kind`
(`approved`/`pending`) and `extent` (`full_day`/`part_day`). Sum actual eligible minutes for
that employee/date/category and compare with that person's effective working capacity to
classify extent. Multiple part-day requests can therefore account for a full working day;
this does not invent morning/afternoon/time placement. Both categories may coexist on the
same date; do not call the pending portion approved. If required duration/capacity evidence
cannot be verified, return typed retryable panel failure rather than guessing extent.

The generic colleague projection contains no leave type, note, reason, medical/document
fields, approval comments, colour/type-derived key or request IDs. One item per person
and per-date/category aggregation avoid leaking the number or identity of that person's
requests through raw rows. Any detailed-request link is an independently authorized
extension; absence projection alone supplies no navigable detailed request authority.

Summary fields are nonnegative integer person counts: `people`, `approved_people`,
`pending_people`. Each is a distinct employment count over the full permitted filtered
result, not merely the current page. `people` is the union, not the sum of categories;
one colleague with both kinds counts once in the union and once in each applicable
category. Do not expose all-team size or names of people without permitted absence rows.
Count and items derive from the same local request observation and verified group scope.
Paging carries the original query context, but remains subject to fresh current access;
refresh when the reviewed request revision or effective grouping changes. It cannot be
used to keep reading an old group after loss of current scope.

### Concrete oracles for actual consumer acceptance

- Two approved requests for Ana and one pending request for Ben: `people=2`,
  `approved_people=1`, `pending_people=1`; no third person or duplicated Ana item.
- Ana has approved and pending portions on one review date: `people=1`, both category
  counts 1, two date categories; no implied exact time overlap or automatic blocker.
- A rejected older cycle followed by a pending current cycle: pending once, not both
  rejected history and a second absence. A withdrawn current request disappears.
- A range spanning a weekend includes actual eligible leave days; the weekend itself
  does not create an additional absence/person. A wholly disjoint request is excluded.
- All included work belongs only to the reviewed request, or all other relevant records
  are excluded states: verified empty with zero summary. Failed owner checks instead
  return failure with no fabricated zero summary. Counts cannot include denied colleagues.

These are planned acceptance oracles, not executed tests. Actual People temporal grouping,
current review/field permission and normalized working-capacity source contracts remain G3/
G4 integration dependencies. Existing generic query/error semantics and L-0166 failure
behavior are reused, not separate approval rules. Remaining G1 work is queue/attention/
own-history/My Leave unions; next bind those alongside G2 view-preference ownership.

## Remaining collection contracts and preference adapter — 2026-10-25

This technical baseline binds approved UX controls to existing owners. It closes G1 read
selection/presentation semantics and G2 preference design at planning level. Concrete G3–G6
upstream types, event identities and generated wire artifacts remain explicit gates. It
does not certify APIs implemented, all atomic requirements covered or stories finally sized.

### Approval queue — 5.16-A/B

GET `/approval-queue` accepts common `limit`/`cursor`, optional `query` (trimmed employee
name search, at most 100 Unicode characters), repeated `leave_type_id` UUIDs, optional
`from_date`/`to_date` inclusive civil dates, repeated `flag`, and `sort`.
`sort` is `longest_waiting` (default) or `earliest_leave`. Dates require from <= to when
both present. Range matching is request interval intersection, not containment or submission
date. A missing endpoint is open on that side. Search is literal case-insensitive name
substring matching, not a raw SQL pattern, fuzzy directory search or a broader employee
listing. Values within each type/flag dimension are OR; dimensions combine with AND.
Duplicate values are normalized once for cursor binding. Unsupported fields/values fail
stable typed invalid-query validation, not silent filter removal.

Closed flags: `short_notice`, `backdated`, `funding_exception`, `overdue`. Actual rule/
funding/waiting evidence determines them, not client calculations or translated labels.
`overdue` uses the current required step's configured escalation threshold, preserving
L-0156 waiting identity; it does not wait for successful notification delivery. No type
filter options outside current permitted actionable work/type visibility. No medical
metadata, notes or reason search is introduced.

Return one item per actionable request, with its current request/cycle/revision, permitted
employee identity/name and normalized summary, ordered currently actionable step references
and revisions, current waiting start, nullable acting-for/end evidence and flag array.
The step set must match L-0158 review requirements; one person covering consecutive steps
gets one row with the covered set, not duplicate requests. Default order: waiting start
ascending, request UUID ascending. Earliest-leave order: leave start date ascending, waiting
start ascending, request UUID ascending. Waiting reflects the actual current action, never
notification unread time or a new assignment timestamp that resets the same step.

The API returns no row approval mutation. Action counts, when shown, count actionable
request rows, not linked steps/notices. Detail/action rechecks independently; an old queue
row never supplies authority. Current eligibility/admission failures use the shared safe
failure/denial contract, not a successful empty queue.

### Own calendar/list and My Leave — 5.29-A/B, 5.31-A

Refine the earlier `/own-requests` selection to a closed `section` discriminator:
`history`, `pending`, `upcoming`. Missing section defaults to `history`. This refinement
allows My Leave sections without inventing a required year for the dashboard. Fields
valid only for another section are invalid, not silently ignored.

| Section | Parameters / selection | Order |
| --- | --- | --- |
| history | Required `year` integer 1–9999; `view` calendar/list, default calendar; optional repeated permitted `leave_type_id` and actual lifecycle `status`; common limit/cursor | Leave start date descending, request UUID ascending |
| pending | No year/view/history filters; actual current submitted/in_approval own requests; common limit/cursor | Outstanding initial employee response first, then current cycle submission time ascending, request UUID ascending |
| upcoming | No year/view/history filters; actual approved own leave whose end date is today or later, including currently ongoing leave; common limit/cursor | Leave start date ascending, request UUID ascending |

History includes actual submitted request records of all supported lifecycle states unless
filtered; drafts are separately E1-owned. No new lifecycle state is introduced. Match a
year by inclusive interval intersection with Jan 1–Dec 31. A spanning-year request remains
one identity/full original interval, and calendar clips drawing only; list retains the
whole interval. Calendar/list use the same query selection/filters and exhaust available
pages to show the requested year's complete results; a first page cannot be labelled the
whole year's empty/complete calendar. Calendar links identifiable entries directly to
existing detail; a chooser is only for genuinely ambiguous grouped entries.

Each row has current request/cycle/revision/status, permitted leave-type identity/label,
normalized summary, concise status and current own action mapping. `response_required`
means actual outstanding initial employee response, not unread notices or a later unpaid
increase. Direct rejection reason remains in detail; no approver absence/cover diagnostics
are added. Reuse E3 balance and E1 draft routes as independent sections, not new dashboard
copies or an all-or-nothing aggregation endpoint.

GET `/own-requests/history-bounds` returns `min_year`, nullable `max_year`, actual retained
employment intervals and `presentation_clock`. Derive lower bound from earliest employment
or retained request; upper bound from known employment end extended by later retained
requests. Open employment/no known end yields max_year null, not a fabricated end date.
Retain previous employment periods and whole boundary years, including out-of-employment
records. Muted non-record dates use actual intervals. If no employment or records establish
bounds, return explicit `no_history`, not an invented zero year. Source outage is failure,
not no_history. Year navigation and This year obey these bounds.

`presentation_clock` is a closed union: `available` with actual current work `timezone`
and civil `today`, or `unavailable` with safe retryable reason code. Derive today under the
employee's configured work timezone, not browser/approver/UTC fallback. History's verified
raw dates/statuses remain usable when this relative-date context alone fails: do not falsely
label approved leave as past/future or choose a fabricated current year. Use `approved`
without a relative category until that context is restored. The upcoming section needs
today and returns its own retryable failure if unavailable; pending/history/balances need
not all fail together. Past/upcoming approved categories derive from end_date < today
versus end_date >= today; pending stays pending regardless of date. No date classification
changes request outcome or authorization.

### Manager attention — 5.27-A/B, 5.28-A/B

E5 extends the existing manager attention surface with its two owned branches; it does not
claim to own E3/E6 balance deficit/correction attention or replace those consumers' models.
GET `/attention` in this E5 contract requires `kind=approval_escalation` or `coverage_gap`,
plus common limit/cursor. Existing other attention categories remain independently owned
and loaded. No broad untyped all-kind union is silently introduced.

An escalation item contains stable actual occurrence identity, current request/cycle/
revision, permitted employee/dates/current assigned step/actor, original waiting start,
threshold due instant and current scoped action mapping. Order by threshold due instant
ascending then occurrence UUID. Return only unresolved required work; a transfer alone
neither resets clock nor resolves escalation. Historical event remains in the actual
owner's history after removal from the active list.

A coverage item contains the actual stable scoped gap identity (wire binding G5), affected
principal/responsibility references, uncovered date intervals, permitted waiting request
references, nullable recorded exception explanation and current scoped actions. Order by
first uncovered date then stable issue identity. A valid recorded exception does not
mean cover exists; a known gap with no waiting requests remains eligible. Clearing requires
verified actual valid cover or eligible available principal, not empty queue/worker failure.
Do not expose an unbounded nested request list: waiting references use the common bounded
page representation, with authorized continuation scoped to that issue. Detail GET uses
the same kind/identity/current scope; no new dismiss/assign/approve command is added.

Unavailable required current evidence is a retryable branch failure rather than zero active
attention. Existing independently loaded tools and successful attention groups remain usable.
Scoped permission/action mapping never upgrades a manager to approver or temp to team reader.

### Minimal Leave-owned history preference — G2, first consumer 5.29-A

Inspection found no reusable preference owner/adapter in the relevant current contracts,
shared UI packages or service inventory. The observed PtS localStorage return-context
code is session navigation, not an application preference service. Use one small Leave-
owned record rather than assume a shared runtime settings capability exists.

Select `leave.history_view_preference` with primary key `(org_id, account_id)`, closed
`view` calendar/list, positive bigint revision, server creation/update actor IDs and UTC
timestamps under P-0025/0056. Account ID comes from verified caller identity; actor attribution
uses its verified durable actor. Current org admission and own-read apply. Use actual owner
account reference conventions, not a browser-supplied account or fake employment. Scoped
restricted-role access must prevent cross-account/organization reads and writes. This is
not a policy/workflow/source record and has no request, reservation, notification or audit-
event side effects. Retaining a preference never retains effective application permission.

GET `/me/preferences/history-view` returns `{view, revision}`, revision a nonnegative
canonical decimal string. With no row return `{view: calendar, revision: "0"}` without
creating a row. PUT same path accepts exactly `{view, expected_revision}`; body at most
1 KiB. Apply immediately, no separate Save/Cancel or draft. For expected 0, atomically
insert only if absent; for positive revision, update only matching existing row. Successful
new/changed choice advances revision once and returns the current pair. An unchanged view
with matching revision returns that pair without a fabricated update. A stale expectation
returns `leave.preference_revision_conflict` plus permitted current pair; validate expected
revision before treating equal values as an unchanged write.

This idempotent desired-value preference does not use consequential operation receipts,
review confirmation, funding/source guards or a background worker. Serialise/coalesce
rapid choices in the browser so an old response cannot overwrite the current selected view.
On uncertain PUT result, GET the current pair: desired value present confirms persistence;
otherwise show not-saved feedback and explicit Retry using the freshly observed revision.
A conflicting other-tab choice is not silently overwritten without that retry. Keep the
current screen usable in its selected view even if persistence fails, with truthful notice
that the choice could not be remembered. Retry concerns only the preference, never a request.

Initial load failure uses the current in-session choice, else calendar, with bounded Retry
and safe failure feedback; never read another account/org's cached value. No new browser
storage promise. Saved view persists across visits; selected year/mobile month are existing
navigation context, not silently durable preferences. A new visit opens the current year
only if known and within bounds, else a valid known history year. Switch/reset session scope
on account/org change and recheck current access. Losing access does not expose the record
or authorize retries; re-enable restores only still-valid authority.

### Planned verification and remaining gates

5.16 owns exact search/filter/order and unified row/task counts, stale cursor/current scope
and privacy. 5.27/28 own their current branch/detail and false-resolution cases; G5 binds
actual occurrence/gap wire identity. 5.29 owns year intersection, both-mode inclusion,
complete paginated rendering, bounds/history, typed clock failure, preference first-create/
stale/unchanged/unknown/retry and actual account/org database isolation. 5.31 owns independent
section order/failure and real completed command/read refresh composition. Reference existing
owner tests instead of rebuilding action/authorization/worker suites.

Concrete oracles: one two-step same-person actionable request is one queue row/count;
Dec 30–Jan 3 appears under both selected years with one identity; a history read remains
usable when only relative-date clock is unavailable; ongoing approved leave appears in
upcoming, rejected leave does not; two concurrent expected-0 preference creates produce
one row and a conflict, not two records; late old-tab writes cannot overwrite a newer
revision. No runtime tests executed. G1/G2 design is bound; G3 source/rule, G4 cross-owner,
G5 timed work/error wire and G6 exact artifact/generation ownership remain. C6 atomic
coverage/dependency reconciliation/final agent sizing/readiness remains open.

## G3 source/rule reference reconciliation — 2026-10-25

[Owning E2/E3/rule input contract](leave-configuration-and-rule-inputs.md) now binds exact
source reference projections, per-date working-capacity/override origin, stable configured
responsibility identity plus actual principal scope and rule-specific result discriminators.
5.17 consumes actual normalized duration/work evidence; current team grouping is distinct
from mandatory 5.3 approval responsibility coverage. G3 remains open only for deterministic
E3 allocator/evidence provenance and source-family impact projection contracts. G4–G6/C6
remain open; selected models are planning interfaces, not implemented adapters.

## G3 allocator/evidence and source-impact design bound — 2026-10-25

[E3 owner interface](e3-request-accounting-interface.md) now selects deterministic portion
provenance/key, actual date/source allocation output and immutable calculation evidence.
[Configuration/source owner interface](leave-configuration-and-rule-inputs.md) binds exact
review/digest and family-specific consequence fields for each 5.15 source writer. Original
E3 rule/tie-order and C3 writer inventory reused. G3 planning design bound; no claim runtime
adapters, source tests or all constraints exist. G4–G6 and C6 remain explicit gates.

## G4 Access/Content alignment; shared registry gate retained — 2026-10-25

Actual shared Access, Content and Identity/People owner contracts now contain selected
E5 context/resource types, confirmed association references/target lifecycle and exact
People management action/resource naming. Current actor/account/member identity is not
employment and no permission crosses an owner implicitly. G4-P remains explicit: compatible
shared-service capability catalog/admission binding before registering People management.
Do not mark G4 complete or copy that authority into Leave to avoid the gate. E4 actual
source lifecycle/protection and G6 artifacts remain owned first-consumer work.

## G4-P proposed internal registration — 2026-10-25

Proposed platform P-0063 reuses Access's actual application/permission/org-admission
mechanics for internal People management; no launcher/extra customer toggle/automatic
human grant or coupling to Leave disable. Source inspection confirmed existing registry
and protected owner command structure, but actual People current-check consumer remains
undelivered. G4-P is pending user adoption, not closed. After agreement, record adoption
then G5 timed-work/event/error contracts and G6/C6 evidence/order/sizing.

## G4-P adopted with implementation reuse — 2026-10-25

User accepted P-0063; G4 design is bound. Current KDG/platform registry and protected
registration/org-admission commands are implemented foundations, not additional E5 work.
Actual current organization HTTP/SQL is KDG-specific; People check/resource/caller and
management consumer/provisioning remain actual deltas. Owning shared contracts record
source evidence and limits. G5 timed work/error wire next; G6/C6 reconcile actual delivered
substrate, consumer contracts/test artifacts and final coverage/order/sizing. No runtime
PASS, deployed-state inspection or Leave implementation.

## G5 timed identity/error design bound — 2026-10-25

[e5-timed-work-and-errors](e5-timed-work-and-errors.md) binds closed due variants, claim/
revision fencing, action-clock/slot/occurrence identity, coalesced catch-up, retained gap
identity and safe typed detail unions. Shared notification owner now has an explicit
Leave organization/timed-event variant, separate from Scribeswell account events. Actual
E3/5.23/25/26/27/28 owners retain tests/artifacts. G5 design bound; G6/C6 remain open.

## G6 artifact and command ownership bound — 2026-10-25

[e5-verification-and-artifact-map](e5-verification-and-artifact-map.md) records current
implemented KDG/Access/API-client/Auth/scaffold reuse, exact owner artifact/generation
responsibility, existing versus planned commands and per-interface acceptance ownership.
No Leave package/runtime or generated OpenAPI exists from this document. G1–G6 C5 design
mapped; C6 atomic coverage/order/duplication/final sizing remains open. Existing proof is
not a fresh test run or complete Leave integration.

## C6 allocation correction: pending source-issue attention — 2026-10-25

Original 5.15 AC4 already requires unresolved pending consequences visible in manager
attention. The prior two-kind E5 attention contract omitted that minimum source-owned
branch. Extend GET `/attention` and `/attention/{kind}/{id}` with
`kind=pending_request_issue`, first actual read owner 5.15-A and minimum existing-surface
presentation/detail entry 5.15-B. This supersedes only the previous two-kind exclusivity;
escalation/coverage scopes, other-owner attention and current permissions remain unchanged.
No independent issue store/worker, grant, dismiss/referral workflow or new dashboard.

Use actual request UUID as id plus current cycle/revision in the response; one active item
per scoped pending request with nonempty typed current issue list. Preserve source issue
identity/evidence through actual request/cycle/current calculation/source-impact refs, not
an unrelated generic task record. Items contain permitted employee/type/date/normalized
summary and actual unresolved funding/eligibility issue codes, source-change actor/reason
and prior/revised amounts only under current authorized detail/source visibility. A pending
request with several issues is one item, not multiple absent people/tasks. Default order
is current cycle submitted_at ascending then request UUID. Common bounded paging applies.

Authorization requires current org admission and actual organization request-read/resource
scope for the manager attention read. Source-management permission separately permits its
minimum authorized impact review; it does not become broad request read or gain sensitive
metadata. Current action mapping uses existing permitted remedies. A stale denied/failed
source read is not an empty issue list, and opening this GET never finalizes or changes it.

Actual API(F) source commit records current unresolved funding/eligibility results with
retained evidence and links, preserving valid decisions and independent gates. Recheck/
clear only through real authorized source/remedy/finalization/terminal changes after current
validation; a later no-op notification or generic view refresh cannot clear a known issue.
Resolved request leaves the active list; immutable previous evidence remains. People source
commit/consequence-pending recovery remains explicit under P-0062. Existing 5.28 owns
approval coverage gaps, not duplicate funding issues. Actual browser partners reuse the
first source-issue presentation; later manager composition adds only its missing layout.

C6 detailed source-family ledger owns producer/test allocations. Added minimum branch is
existing scope, with final boundary size still pending. No runtime test or implementation.

## Minimum gap attention extraction adopted — 2026-10-25

User accepted 5.28-C. It introduces the actual scoped stable gap representation/current-
evidence read/update interface and minimum existing manager list/detail presentation.
Real source/request/appointment producers update it in their own protected transactions;
reads create no source facts or approvals. It precedes B/first actual producers using
completed 5.3 and core state/read. 5.28-A/B now own only residual source/assignment/remedy/
attention enrichment/navigation; reuse C's minimum/privacy/loading/Retry once. No new
policy/grant/screen. Pending-source-issue branch remains 5.15-A/B, escalation 5.27. Exact
native/current source/UI acceptance belongs to actual owners, not a planning PASS.

## First-read storage allocation — 2026-10-25

5.28-C's one scoped gap representation includes the already required nullable exception
reason/actor/time and applicability evidence needed by its minimum authorized read and
5.3/B coverage gate. Absence of a recorded exception never waives coverage. This is not a
second exception store or authority to create one through a read. 5.5-A owns the actual
reasoned authorized exception command, protected update and finalizer integration. Real
producer integration must be proved there; controlled storage fixtures prove only C's read.

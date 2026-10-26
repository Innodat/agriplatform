# E7 overview, reports and audit — owning technical proposal

**Status:** E7 planning accepted by user on 2026-10-25; not implemented or readiness-approved
**Date:** 2026-10-25
**Owners:** Leave read/report owners; Access/Identity, People, Content and notification owners for their own evidence

Authority remains [Features](../../features.md) §6/17–20, accepted ADRs, the architecture
spine and approved DESIGN/EXPERIENCE. This contract allocates query/wire/evidence work;
it is not a duplicate feature specification, a new reporting service or authorization
to implement. The two temporal choices are in
[accepted ADR-0169](../decisions/0169-reporting-time-basis-and-derived-team-grouping.md).
[E7 review/size/dependency register](../../../../../_bmad-output/planning-artifacts/e7-planning-review.md)
and [source allocation](../../../../../_bmad-output/planning-artifacts/e7-coverage-audit.md)
map each consumer and its future evidence.

## Existing mechanisms and exact owner boundaries

Reuse [E5 read models](e5-read-models.md), [actions](e5-capabilities-and-commands.md),
[E3 accounting](e3-request-accounting-interface.md), [source models](leave-configuration-and-rule-inputs.md),
[E6 corrections](e6-corrections-and-consequences.md),
[E5 artifact strategy](e5-verification-and-artifact-map.md) and
[E1 audit ownership](../../../../../platform/docs/architecture/contracts/e1-security-audit-ownership.md).
E3 owns arithmetic/replay/history/provenance; E5/E6 own request/approval/correction
producers and first-use evidence; E7 owns only its read/query/presentation/export consumers.
No new mutable balance total, ledger, employee master, persisted reporting engine,
per-render audit log, automatic accrual job or report worker is required.

All browser business data uses the authenticated Leave API at
`/api/v1/organizations/{org_id}`. Current Access admission/capability and Leave domain
scope apply on every query, page, detail and export, with private/no-store responses.
Query/route IDs cannot choose an audience. Authorize rows and allowlisted fields before
filtering, searching, grouping, counting and serializing. Existence, inaccessible filter
options, hidden type-specific style keys and aggregate differences are also disclosure.

Proposed exact catalog names extend existing owner mechanisms, without live registration:

| Capability | Predicate and boundary |
| --- | --- |
| Existing `leave.request.org.read` | Explicit current organization-scoped overview/detail fields under accepted manager visibility; no approval/correction/document power |
| Existing `leave.request.team.read` | Existing permitted absence-only team projection; no new organization overview admission or detailed request fields inferred |
| `leave.report.read` | Current explicit organization/employee-scoped reporting access for the selected allowed report; standard manager report scope follows accepted L-0065 |
| `leave.report.export` plus report read | Same report/row/field/filter scope as reading, additionally permitting audited CSV; export alone never grants read |
| `leave.audit.read` | Current organization-scoped permitted business-audit list/search/detail; each private field/linked resource still requires its source/domain read rule |

Bind actual Access typed resource results to scoped report keys/employee sets and
allowed field categories; report.read cannot be translated to an unrestricted SQL query.
Default manager adoption preserves accepted reporting/audit visibility; restricted custom
roles may omit read/export/audit. Organization Administrator, platform operations, a past
actor or temporary approver has no automatic reporting/audit power. The ordinary manager
field projection includes permitted sensitive type/note/history under L-0013 but never
medical metadata/bytes by default. Report row schemas omit notes/comments/documents unless
the approved report actually needs them; no report here needs medical documents.

## Common bounded query and source observation

Use UUID identities, ISO date-only fields, UTC RFC3339 instants, canonical decimal-string
bigint counts/minutes and existing safe typed error adapters. All six report owners expose
one allowlisted definition: report key/version, permitted filters, normalized query,
row schema/identity, order, aggregation rules and CSV serializer. These are concrete
Leave code adapters, not database-configured executable report definitions. 7.7 supplies
only the first actual report plumbing; each later owner supplies its specific adapter.

A response adds `report_key`, `query_version`, normalized applied query/fingerprint,
`generated_at`, basis/grouping labels, source coverage and permitted totals to the existing
collection envelope. Page size 25/max50 and opaque actor/org/route/filter/sort-bound cursors
reuse E5. A cursor grants no authority. Interactive pages are current reads, not a frozen
cross-service dataset; clients deduplicate identities and refresh when data changes.
No snapshot table or durable saved-report collection is created for ordinary reads.

Capture `now` once per query. Current calculations use each employee's work-local basis;
absence intersections preserve recorded civil dates. Current month is a viewer presentation
choice, not conversion of the employee's leave interval. Accepted ADR-0169 governs current
versus date-effective People grouping and corrected point-in-time balances. Current access
is always current. Unknown historical facts do not become Unassigned or today's team.

Get required People/Access source observations outside DB transactions. References/values
retained by existing Leave source/consequence protocols support local consistent calculation;
where actual owner verification is required, preserve its revision/interval/observation
context. These reads are not one distributed snapshot. If relevant People consequences
are pending or required observations cannot be reconciled, return typed unavailable/source-
incomplete rather than a falsely authoritative total. No business write locks are held
for reports. Short local consistent reads and bounded in-memory assembly use one declared
source set. A source unavailable for a required calculation cannot be silently omitted.

## Organization overview query

Select `GET /overview` with required inclusive `from_date`/`through_date`, bounded
employee-name search, optional permitted department/supervisor-team/location/type IDs,
status set `approved`/`pending`, and `show_all_employees` boolean. `pending` maps exactly
to submitted/in_approval. Defaults: current month, both statuses, no attributes and Show
all off. Server still validates arbitrary IDs and date bounds. No hidden leave-type
selector or count for a colleague field projection.

Return bounded employee rows plus per-request ID, current status, full original date
range, intersecting date markers, permitted duration/category and safe allowed detail
reference. Names and request IDs appear only where that audience already permits them;
a request ID never grants detailed access. Preserve one identity per request and distinct
employee counts where needed. Do not add a capacity percentage or inferred staffing
minimum: existing capacity warnings remain informational and Show all changes rows only.

Include actual employee per-date work/nonwork context and permitted location/calendar
holiday labels. A holiday in one selected location does not mark all employees off.
Continuous multi-date bars are calendar span, not charged amount; partial markers have
no invented exact times. Manager projection can expose current permitted type details;
absence-only projection supplies only Unavailable/Part-day absence and no type-revealing
filter/style/grouping/tooltip keys. Calendar payload has no attachments.

7.4 extends the existing account/org preference record/API with bounded applied overview
attribute filters and Show all. It reuses current revisions and immediate preference
saving on a separate surface. No provisional mobile edit is persisted until Apply;
no new settings service or administrative draft. Date-window and view persistence are
not added: overview reopens the current month and mobile defaults to List. Invalid or
forbidden saved IDs are cleared safely; failed lookup is not proof they were retired.

## Six report definitions and concrete date/count semantics

Routes are selected design names, not existing executable endpoints. Use
`GET /reports/{report_key}` with a closed registered key, its own validated filter model
and stable default sort ending in canonical row identity. Never accept a SQL/group-by
expression or arbitrary field name from the browser.

| Key / owner | Date and row semantics | Ordering / aggregation oracle |
| --- | --- | --- |
| `balances`, 7.7 | Current or one selected historical effective date; one employment/type row with E3 remaining/reserved/available, typed tracking and actual conversion basis | Employee display sort then employment/type UUID; aggregate canonical minutes only for compatible fields, retaining untracked count separately rather than treating null as zero |
| `accrual-adjustments`, 7.9 | Inclusive effective-date window; derived automatic earning by actual source/earning period plus immutable actual adjustments/carry-over/expiry explanations; retain original validity and corrected evidence | Effective date, employment/type, source/occurrence identity; derived history is not a newly posted grant or duplicate of an actual event. Allow drilldown to existing E3 explanation, not millions of new daily rows |
| `leave-used`, 7.11 | Approved current actual usage intersecting selected leave dates, split by employee/type/date and effective supervisor/department/location; pending proposed usage is not used | Leave date then employment/type/request/contribution identity; sum each normalized requested minute once, independent of funding-source lines. Distinct request count is a separate non-additive measure across groups |
| `upcoming`, 7.13 | Requested future/remaining date-window intersection, approved and distinctly pending by default; normalized window cannot silently include past work-local dates for selected employees | First intersecting date then employment/request identity; full original range remains in row while selected-window minutes/counts are distinct. Current grouping per ADR-0169 |
| `approval-aging`, 7.15 | Current submitted/in_approval requests, current actionable required steps and preserved E5 waiting-clock facts at captured now; optional selected leave-date intersection | Oldest current actionable waiting start, then request UUID. One request summary with nested step evidence; consecutive same-person collapse/transfer never duplicates request totals or restarts the clock |
| `override-adjustments`, 7.17 | Actual adjustment/recurring-override or reset/request exceptional-funding actions with effective-date filter; both recorded UTC and actual owner-effective date displayed | Effective date, owner action kind, immutable action ID. One owning action with child allocation/event lines, not a sum of repeated ledger/step/correction copies; mixed kinds do not invent one numeric total |

A historical balances row reconstructs actual dated reservation/consume/release/reallocation/
cancellation interpretation under E3 replay; today's mutable commitment head is not its
historical truth. Known later corrections change corrected history without overwriting
old decision evidence. Future projection is not silently presented as historical balance;
validate the selected date against selected employees' work-local current dates.

Used reports exclude cancelled original requests and show replacement only under its actual
current approved state. Rejected/pending administrative replacement stays explicit follow-up;
it does not become used because it corrected a taken absence. Show relevant unresolved
correction/source coverage with no falsely complete economic explanation. Historical former
employees with retained matching records remain reportable within current org authority.

Aging includes any remaining initial employee response/funding/document/coverage blocker
separately from the actual step-waiting clock. A request with no currently actionable human
step has no invented zero or age clock; show its real blocker and nullable step age.
Compare to E5 step facts, never rebuild reminder/escalation scheduling in a report.

Recurring/action/report grouping uses actual effective dates supplied by source owners;
backdating restrictions stay binding. Per-date normalized minutes are canonical across
employees/types. Displayed days use the actual retained conversion and cannot be blindly
summed across incompatible standard-day contexts. Untracked usage has duration but no
fabricated entitlement balance. Rounding/allocation/replay remain E3, not report arithmetic.

## Audited CSV without a new export subsystem

7.19 selects `POST /reports/{report_key}/csv` with exactly the registered normalized query
and its version/fingerprint, excluding pagination/cursor. A browser cannot submit trusted
rows, totals, fields or arbitrary output filenames. Verify current report **and** export
scope, normalize independently, and reject incompatible query/version rather than quietly
exporting another filter set. One export produces all matching authorized rows, never just
a page. It uses the report's allowlisted serializer and query/filter/privacy transformation.

Export obtains its own current observation/snapshot at generation, which may differ from
an older interactive page after concurrent changes. Preserve query identity and disclose
generated-at context; do not promise the earlier page is an immutable dataset. Read the
required local result consistently and materialize bounded rows/CSV in memory after
external observations. Release DB transactions before serialization/streaming/network
backpressure; no business locks, temp shared directory, Content bearer link or export queue.

Selected initial bounds: overview max 366 inclusive days; interactive report history up to
five years per query with navigation to additional retained years; audit window up to
366 days per request; CSV max 25,000 data rows/10 MiB encoded output and 30-second total
execution, with local transactions at most five seconds and dependency reads at most
three seconds. Check bounds before releasing response bytes. These are initial technical
limits to prove with actual representative data, not retention cutoffs or employee limits.
Use typed `query_too_large`/verification/busy errors and preserve the report for narrower
query/Retry. No silently truncated success or automatic switch to background processing.

Use fixed headers, UTF-8, RFC4180 quoting/CRLF and canonical numeric/date fields. Neutralize
untrusted text beginning (including after leading control/whitespace) with `=`, `+`, `-`,
`@`, tab or carriage return using the chosen explicit apostrophe text escape; numeric
schema fields serialize as canonical numbers and are not treated as untrusted formulas.
Quote commas/newlines/double quotes correctly; test actual Excel/LibreOffice CSV behavior
with representative Unicode/escaping during delivery. Never export a free-form expression.

Persist immutable `leave.report_export_authorized` v1 evidence before sending any bytes:
organization, current actor/membership, command/export UUID, report/query version, allowed
normalized filter references or safe digest, generation/basis/source context, row/byte
count and checksum of the actual bounded generated file, UTC time and correlation/release
reference where applicable. No file contents, notes, sensitive query text or read URLs in
technical logs/receipt copies. Reuse existing audit writer/actor/schema, introduced by the
actual export consumer. No successful release when required evidence cannot commit.
This evidence means generated and authorized for release, not a fully received client file.
Connection loss/retry does not repeat a business mutation: a retry generates a fresh current
export and a fresh audit record. No sensitive export artifact is retained by a new library.

## Audit sources, source limits and protected search

All producers already own required immutable evidence before E7 UI. E7 does not add a second
record per ordinary autosave/own-draft read or backfill imaginary missing historical events.
Use real record categories, stable owners/IDs, UTC recorded times, actual durable actors,
membership, action/resource, safe before/after/reason and on-behalf initiator/executor links.
Failed attempts are not committed business changes; diagnostic logs remain separate.

7.21–24 add bounded **read** projections with the actual source owners, plus Leave HTTP
consumer adapters. Existing Access/Identity and Content implementations are credited only
for inspected event infrastructure; no generic audit query endpoint is assumed. People and
shared notification runtime remain planned. Read policy must verify calling Leave service,
user/current org scope and exact Leave-associated event context. A source key cannot read
other apps, unrelated account-scope events or arbitrary tenant history.

Source API design is a versioned `audit-window`/`audit-event` projection in each owner's
existing authenticated internal namespace, with allowed action families, current context,
UTC recorded-time bounds, normalized safe search/filter model, upper bound and bounded
cursor. Owners use their own actual event/model/role and return only projected permitted
fields. Actual source route names/credential adapters/exported schemas bind in each 7.21–24
consumer item; they are not fabricated existing public endpoints. No source database import
or shared credential grants browser access. This is application-specific federation, not a
platform-wide write/audit service or persisted reporting warehouse.

Leave `GET /audit` and `/audit/{owner}/{event_id}` are read surfaces. 7.25 provides its local
projection; 7.26 merges a bounded page from authorized source pages, ordered recorded_at
newest first then owner and event UUID. Continuation binds caller/org/query/owner cursors,
fixed recorded-time upper bounds and order tuples under the existing opaque cursor scheme.
No DB transaction spans HTTP. Current authority applies on every page/detail. As in E5,
there is no frozen multi-page snapshot guarantee: clients deduplicate identities and
refresh to see new or late-committing evidence. Never claim upper timestamps imply a
cross-service atomic snapshot. Unknown versions/source retention/failed sources yield
explicit coverage-limited/unavailable state; do not present a partial union as complete or
invent exact global totals. Previously permitted data may remain marked stale under current
access while the failed source retries; other tools remain usable.

Search permits bounded employee/action/actor/recorded-time and allowlisted authorized
summary/reason text only. Enforce field permission before SQL/search matching, snippets,
highlights, counts or remote query forwarding. No raw JSON search or whole event payload
viewer. Medical-document metadata/bytes retain E4 permission/private authenticated reads;
audit.read never grants them. Linked details reauthorize at the actual owner. Durable actor
identity remains when logins change; do not join by mutable email or manufacture employment.

## Performance, fixtures, release and the five impacts

Accepted E7 planning validation targets: at 100 expected/1000 safety-factor employees, five years of
representative earning/request/source history, 5 concurrent readers and 1 exporter, target
p95 at most two seconds for one overview/report page and five seconds for multi-year balance
calculation; bounded CSV/audit aggregation within declared 30-second execution. Record row/
request/event density, measured query/dependency/local transaction/memory costs and exact
hardware before claiming qualification. These are proposed technical acceptance targets,
not measured results or a reason to create speculative checkpoints. Large queries fail
safely with ordinary filter/navigation recovery; index only actual measured queries.

Every API/source/export item owns its actual unit/contract/restricted-role/concurrency proof
and generated OpenAPI/client updates. Browser partners prove real response states, keyboard,
mobile and supported-browser behavior. 7.28–31 fill only composition/release gaps. ATDD
failure-before-code occurs after readiness/implementation authorization, not by implementing
Leave now to manufacture planning evidence. Use E5's actual-versus-planned artifact/command
map: future Leave API pytest/export checks, generated client checks/type checks and actual
Playwright runner are not passing scripts until the actual package/fixtures exist.

Scaffold: reuse/prove neutral scope/query/cursor/CSV/native fixtures and update templates,
managed copies, preservation tests/docs in the same consumer if applicable. Shared UI:
prove report/collection/filter controls in 7.8 and promote only domain-neutral components;
report definitions and audit/privacy content stay Leave-owned. Agent context: existing
instructions suffice; generated package guidance updates with actual new commands. Docs:
source contracts, source-to-test IDs and exact test/release evidence in owning items. ADR:
accepted 0169 binds the two approved temporal choices; accepted predecessors unchanged.
Controlled compatible schema/index/default-role adoption must prove previous readers,
least privilege and migration failure/activation/recovery under P-0020 and focused migration
verification. No DB migrations on startup or automatic downgrade. No live app/grant/provider/
recipient/deploy/commit or completed readiness is authorized by this planning proposal.

## Exact work/calendar precision binding — planning candidate 2026-10-26

The [work/calendar and minute contract](work-calendar-and-minute-precision.md) owns the
selected closure shapes, nominal local-clock DST quotas, effective-date interpretation
and exact half-minute consumption. Its MinuteAmount mapping supersedes integer-only
amount wording in this technical candidate; integer counts/revisions and entitlement
floor rules remain. Existing accepted ADRs and original acceptance criteria are unchanged.
Actual writer/consumer fixtures must use that contract before this interface is delivered.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0171-work-calendar-precision-and-retention.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.

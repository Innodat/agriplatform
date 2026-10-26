# Leave configuration references and rule inputs

**Status:** Selected E2/E3/E5 owner interface baseline; remaining accounting/evidence and
cross-owner wire gates explicitly open. No runtime implementation claim.  
**Date:** 2026-10-25  
**Owners:** Actual Leave configuration publishers/readers and first rule consumers

This narrow contract specifies reference/projection fields between existing owners. It
is not another feature specification, configuration engine, generic rules service or
instruction to create all future tables. Features and accepted ADRs own business policy.
The first real source story creates only its required records; consumers use those actual
records and source adapters. JSON representations follow the E1/E5 UUID, civil-date,
UTC-instant and canonical decimal-string bigint contracts.

## Source references and empty slots

A present mutable source reference is `{kind, id, revision}` with stable UUID id and
positive revision. Immutable version references additionally identify their actual owning
source UUID and version UUID. `kind` is a closed model-specific code, not a table name or
client-selected database path. Every local reference is organization-scoped through the
actual owning keys; an ID/revision alone never supplies authority or completeness.

Selectable source families below define their own closed projections. An unconfigured
slot returns `{state: unconfigured}` plus its actual stable selection-scope identity and
revision, not a fabricated source UUID. A configured slot returns `{state: configured}`,
its selection revision and actual reference(s). Empty and configured outcomes must be
verified under the same source slot protection. Missing verification is a typed failure,
not unconfigured. Guard slot identity/creation/modes remain in the E5 coordination contract;
this projection does not introduce another revision/lock table.

| Owner / selected projection | Fields E5 must receive from the actual source |
| --- | --- |
| E1 stable type, extended by E3 3.1/3.37–39 | `leave_type_id`, actual type `revision`, active/archive/admission state and explicit published metadata `version_id`; existing leave_type/leave_type_version model remains owner |
| E3 date-effective policy selection, 3.28/3.34–36 | `employment_id`, `leave_type_id`, employee assignment identity/revision, policy identity/revision, immutable policy version identity, inclusive effective date interval, tracking mode and applicable rule projection; all date segments needed by request, not just one current pointer |
| E3 recurring employee entitlement, 3.30 | Actual employee/type override identity/revision and effective interval or verified inheritance, selected immutable policy/rate source reference and effective amount representation; not request-specific exceptional funding authority |
| E2 2.20/2.22 employee work selector | `employment_id`, selection/timeline revision, explicit-profile versus organization-default selection, effective interval, explicit override presence and values per supported field, selected source refs |
| E2 2.21 organization default | Actual organization default slot identity/revision and selected profile ref or verified absence; no synthetic profile for an empty slot |
| E2 2.19/2.23/2.24 work profile | Stable profile identity/revision, selected immutable effective version, active/archive state, named weekly schedule fields, work timezone, standard-day minutes and actual calendar reference with effective interval |
| E2 2.18 calendar | Stable calendar identity/revision, applicable version/entry references, inclusive date and full/partial closure minute data; verified no entry remains protected by calendar identity |
| People employment/supervisor | Exact shared-owner reference/projection under identity-access-employment-e1 and adopted people-leave-change-coordination; never read or copy People tables to satisfy this local interface |

Source-specific rule fields are exposed by their source adapter, not an arbitrary JSON
bag interpreted by E5. Assignment/profile/calendar revisions denote those actual sources,
not request revisions. Existing source schema names remain their owner's responsibility;
this interface does not claim nonexistent migrations or automatic generator support.

## Date-aware selection and work resolution

E1's `choice_version_id` is offered form metadata, not the governing policy version.
Resolve the requested dates through actual employee policy assignments and effective
published policy versions under E3's existing transition rules. Return all relevant
segments and exact versions/assignment revisions. Reject ambiguity/unsupported transition
through the existing typed rule result rather than choosing MAX(version_number), browser
"today" or the draft-choice pointer. A consequential command rechecks selected source
references and reviewed consequences; retained submitted evidence stays immutable.

For each actual requested leave date, the E2 work resolver returns:
`leave_date`, `work_timezone`, `working_minutes`, `standard_day_minutes`, actual selected
profile/version ref, actual selection/default refs, field-level origin (`employee_override`
or `profile`) and applicable calendar/entry refs. Working minutes are nonnegative integer
minutes after the actual weekly schedule and closure rules. Standard-day minutes use the
actual effective source; no float day conversion becomes authoritative. Field-level
origin distinguishes an explicit override from a coincidentally equal inherited value.
An employee with one overridden field can still inherit the remaining profile/calendar
fields and must remain in their actual reverse dependency sets.

No derived resolved-profile row is a new source of truth. Resolve actual explicit profile
or current applicable default, then actual field overrides and calendar rules, retaining
source evidence. Reset means restoring inheritance, not copying current inherited values
into an override. Missing required configuration and source unavailability remain distinct.
Shared department/location do not implicitly change Leave work settings. A source edit
must protect old and new referenced source membership under the existing global guard
order; recalculating a row after an unprotected reference change is insufficient.

5.6 consumes these dates and the submitted selected mode. Return a normalized duration
projection with `mode`, original requested `start_date`/`end_date`, ordered per-date
`requested_minutes`/`working_minutes`, total minutes and contributing work refs. Mixed
working/nonworking ranges remain valid; zero eligible requested time is invalid. Capacity
checks combine actual active leave minutes for each absence date, across request types,
under employee mutation protection. Do not count submissions made on the current date.
Half-day/hour conversion and historical work-date behavior remain the accepted source
rules, not new hard-coded eight-hour or morning/afternoon assumptions.

## Stable approval responsibility interface

5.1 first introduces actual configured route-position identities; configuration publishers
retain each position's UUID while that logical position continues. A different replacement
position has a different identity. Do not use a translated role name, pending request step
ID or appointee identity as the configured responsibility ID. Existing route configuration
owner creates/versions these positions; E3 need not reference future E5 request/step tables.

A route-position projection contains `responsibility_id`, actual configuration ID/revision,
immutable governing configuration/policy version ref, ordered `position`, kind (`supervisor`
or `final`), principal binding (`employee_supervisor` or explicit configured actor), and
actual self/distinct-person/absence-fallback rule fields from that configuration. Only
supported one-/two-step shapes are exposed; no workflow graph or arbitrary expressions.
If policy owns approval configuration in the same row, reuse its actual identity/guard,
not a duplicated approval settings store.

A resolved responsibility adds verified `principal_actor_id`, principal membership
reference where applicable, current authority evidence and the actual affected employee/
policy scope. The bound unit is `(org_id, responsibility_id, principal_actor_id)`; the
same configured supervisor position can bind different principals for different employees.
Appointment input already supplies the principal membership plus selected responsibility
IDs. Revalidate that each position genuinely belongs to that principal's current normal
responsibilities and permitted population. Selecting a position does not authorize all
principals, policies or organization employees, and no pending step is required for a
valid responsibility to exist.

5.3 enumerates actual configured supervisor/final responsibilities occupied by the applicant
and their relevant scope from current local configuration plus authorized People facts.
Include possible incoming work throughout the absence, not just existing assigned steps.
5.2 validates the human-selected appointee/current member and exact interval; no candidate
ranking or permanent Approver-role requirement is introduced. 5.4 evaluates only the actual
configured directional fallback. 5.3 composes that real fallback with selected appointments;
a temporary-final label alone supplies no coverage and needs no extra fallback checkbox.

Coverage output contains the exact scoped responsibility/principal pair and ordered
covered/uncovered interval segments with the actual source appointment/fallback references.
Use half-open UTC intervals for appointment authority and exact civil-date/work-timezone
normalization evidence from the appointment contract. Sequential intervals may cover the
whole period without a single appointment covering everything. Keep unverified input
separate from a definitive gap. An authorized 5.5 exception references that actual bounded
gap; it does not rewrite covered intervals, grant approval or remove other responsibilities.

Source supervisor changes coordinate under P-0062/Leave transfer rules and update actual
unfinished responsibility/coverage consequences; source configuration and appointment
writers participate in the existing actor-key dependency protection. 5.17 current-team
view semantics do not replace this broader mandatory approval-responsibility assessment.

## Rule-consumer result and evidence obligations

Rule-specific return types share only these result discriminators: `satisfied`,
`not_applicable`, `blocked`, `verification_failed`. Each has typed rule-specific details,
required source references and intended action stage. `not_applicable` requires verified
facts (for example no approval responsibilities), never a failed lookup. Definite blocked
results use stable issue codes; verification_failed is safe/retryable and cannot be treated
as eligible. These are internal adapter contracts, not new public runtime rule endpoints
or a persisted universal rules-result table. Public failures map through existing API
error contracts; requester and internal audience projections remain separate.

| Actual first rule owner | Consumed inputs / minimum retained result |
| --- | --- |
| 5.1 route | Governing policy/position refs plus current verified People/Access; ordered required positions/principals and definite setup issue versus verification failure |
| 5.2 selected member eligibility | Actual member/actor, selected principal/responsibilities and half-open interval; current membership/authority/absence eligibility evidence, not recommendation output |
| 5.3/5.4 coverage/fallback | Full scoped responsibility set and actual interval arrangements; covered/gap segments and actual configured fallback basis |
| 5.6 duration/capacity | Date-effective work projection and other active request minutes; normalized requested minute lines and protected per-date capacity result |
| 5.7 eligibility/dates | People employment periods, actual effective policy assignments/versions and normalized dates; exact failed eligibility/notice/backdating rule or current validity |
| 5.8 funding | E3 deterministic date/source/portion allocation under existing accounting interface; explicit paid/unpaid/source evidence and valid prior commitments |
| 5.9 document policy | Governing document policy plus actual E4 association/readiness observation; provision/readiness gate only, not private metadata/bytes or proof a human read it |

Preview references are observations, not approval/reservation authority. Consequential
execution reloads/protects actual inputs with existing budgets/guard and cross-owner
protocols, then compares materially reviewed consequences before applying. No earlier
read transfers ownership of Access, People or Content checks to a client or ledger row.

## Remaining G3 and planned verification

This binds source reference/date-work/configured-responsibility/rule-adapter shapes.
Remaining G3 is E3 deterministic allocator portion/evidence provenance and exact impact
projection contracts for all actual source families. G4 still owns shared management/
Access/E4 wire synchronization; G5 timed work/error details and G6 concrete artifact checks.
Exact model/constraint/migration identifiers are actual source first-consumer work, not
proof created by this document. No interface is declared implemented because its fields
are listed here.

Observe actual first-consumer acceptance failures during authorized delivery. Cases:
draft choice versus future governing version; partial override retaining profile/calendar
membership; empty default then assignment under guard; changed old/new reference set
restarts; two principals sharing one configured supervisor position cannot share a cover
grant; responsibilities with no pending steps still need coverage; sequential cover with
one gap; ordinary member appointee without employment; failed source observation never
eligible. Reference real source/owner tests and verify concrete consumer composition once.
No runtime tests, schema changes, grants or implementation authorization here.

## Source-change impact projection interface — 2026-10-25

This binds the remaining local G3 source-family consequence projection. E3's
[evidence/portion contract](e3-request-accounting-interface.md) now owns deterministic
allocation identity and retained values. The C3 matrix in the E5 core contract remains
the writer inventory; it is not replaced by a new impact service.

### Read-only review result and protected comparison

Each existing source review adapter returns `version:1`, its actual typed proposed change,
current expected source references/revisions, exact old/new reference membership evidence,
`affected_requests` and a backend `review_digest`. Affected items identify actual request/
current cycle/revision, employment/type, previous evidence reference and the proposed
normalized result: duration/paid/unpaid amounts, current eligibility/funding/coverage issue
codes, required existing remedy/attention and whether current finalization gates would
clear. Include previous/revised fields required to explain the actual material difference;
no generic untyped JSON diff or unnecessary employee medical/note data.

Digest is lowercase SHA-256 of RFC-8785 canonical v1 source change and material consequence
projection. Sort affected items by request UUID and nested dates/responsibilities by their
canonical owner order. Purely diagnostic observation time and newly generated preview IDs
are excluded; actual expected revisions, identities, before/revised amounts/classifications,
issue/action/gate results and source normalization enter comparison. Digest is not a
permission, reservation or signature; actual actor/source/target authorization is rechecked.
Unchanged material results can use refreshed verified observation evidence, but no source
revision or reviewed source change is silently overwritten in the command.

Source preview creates no source event, request revision, commitment, calculation-evidence
row, audit event or notice. Consequential execution protects the exact relevant source/
reference/employee set and re-enumerates under the existing guard order. Changed affected
membership/revisions/material outcomes require refreshed review; an incomplete protected
set restarts the protected attempt, not a late out-of-order lock. Unknown source facts
return retryable verification failure, never `affected_requests: []` as a successful answer.

The existing review surface receives the complete mandatory affected selection within its
execution bound. It must not silently truncate at a UI page size or claim an unreviewed
remainder has no consequences. Display pagination may partition one exact reviewed set;
its backend comparison still covers the whole set. If the synchronous bound cannot be
met, abort without source mutation and return the existing typed retryable failure; do
not quietly create a local background-impact workflow or publish partial success.

### Actual source-family binding

| Source operation / existing writer owner | Specific projection inputs and consequences |
| --- | --- |
| One-off Add/Deduct, 3.29 -> 5.15-A/B | Exact source type/date/minutes/direction and original event ordering; recompute affected pending commitments through funding history, including later request dates, previous/revised allocation and funding issues |
| Recurring entitlement/reset, 3.30 -> 5.15-C/D | Exact effective rate source/version/interval and inheritance transition; recompute affected earning periods and later dependent funding, preserve original request policy/evidence |
| Used policy publish and scheduled amend/cancel, 3.34/35 -> 5.15-E/F/G/H | Actual old/proposed policy versions/schedule identity/effective intervals and selected holders; exact earning/eligibility/funding consequences under accepted transition rules, not relabel every request to the newest policy |
| Initial/change/end employee policy assignment, 3.28/36 -> 5.15-I/J | Employee/type assignment timeline before/after, both old/new policies and effective gaps; distinguish a genuinely empty initial scope from existing relevant pending work |
| People period-add/rehire/end, 2.11/12/13 -> 5.15-K/L | Actual shared source attempt/change and employment interval; affected Leave date eligibility/funding before/after. Prepared-change protocol owns source/gate/reconciliation; genuinely new employee does not imply rehire has no impacts |
| Employee overrides/reset, 2.22 -> 5.15-M/N | Effective changed fields and explicit/inherited origin; date minutes/timezone/calendar/earning dependencies, including unchanged override values versus genuine reset |
| Employee profile assignment, 2.20 -> 5.15-O/P | Effective old/new explicit/default profile membership and field inheritance; duration/date eligibility and later funding consequences |
| Organization default, 2.21 -> 5.15-Q/R | Exact default slot and old/new profile refs; actual fallback followers with each overridden/inherited field, not all organization employees |
| Shared profile publish, 2.23 -> 5.15-S/T | Old/new immutable version, effective changed fields, explicit holders and default followers including partial overrides; actual request and funding-history effects |
| Calendar add/edit/remove, 2.18 -> 5.15-U/V | Calendar identity, entry identity or verified absent slot, date/full/partial minutes; direct/profile/default inherited users and later earning/funding, not only intersecting request dates |

Other C3 paths retain their actual narrow contracts: unused type/profile creation or
archive has verified no-holder/non-impact preconditions; type metadata does not recalculate
historical requests; activation/restoration supplies no implicit grants/assignments.
Request lifecycle/exception writers use actual accounting/gate contracts. Appointment/
transfer/supervisor-return writers use exact step/responsibility changes, not the 5.15
funding-source projection. No generic source-change endpoint supersedes their APIs.

### Commit consequences and failure boundary

Local source writer, source event/version, actual pending request allocation/evidence/
revision/response-state changes, audit/original operation result and required notice intent
commit in the declared owner transaction. Source validity/impact that changes another
request must not be recorded as source success while those promised local effects are
missing. People cross-owner commits use P-0062's truthful source-committed/consequence-
pending recovery instead; do not claim one distributed transaction or roll People back.

Later pending paid/unpaid changes record previous/revised amounts and explanation/employee
notice, without renewed acknowledgement under L-0151. An outstanding initial on-behalf
response remains applicable while needed; reaching zero follows L-0162, not fabricated
consent or automatic reopening on a later increase. Valid prior human decisions remain.
Reassess B when the last gate resolves; unresolved funding/eligibility/coverage stays
truthful attention, without automatic reject/cancel/trim/grant. Separate remedies need
actual independent authority. Preserve approved records and original evidence; any ongoing/
past approved correction remains the separately authorized E6 owner.

### G3 closure and acceptance allocation

G3 design is now bound by this contract plus the E3 allocator/evidence interface. Actual
source APIs/storage and rule adapters are first-consumer deliverables, not existing code.
G4 shared Access/People/Content types, G5 timed work/error wire, G6 artifact/generation and
C6 final atomic coverage/order/sizing remain open.

Each 5.15 API family verifies its own actual source adapter and protected side effects;
its browser partner proves exact review/explanation and original-outcome recovery. Reuse
common calculator/guard/receipt primitives and owner tests, while retaining one real
producer integration case per source variant. Concrete oracles: historical calendar edit
changes a later pending allocation outside edited request dates; partial override retains
calendar dependence; new holder races protected shared-profile publish; unchanged labels
produce no allocation effects; membership/revision drift cannot hide an extra affected
request; crash before commit leaves source/request/evidence/intent unchanged; actual
People commit with interrupted Leave consequence remains recoverable under its gate.
These are planned tests, not executed evidence or permission to implement Leave.

## Exact work/calendar precision binding — planning candidate 2026-10-26

The [work/calendar and minute contract](work-calendar-and-minute-precision.md) owns the
selected closure shapes, nominal local-clock DST quotas, effective-date interpretation
and exact half-minute consumption. Its MinuteAmount mapping supersedes integer-only
amount wording in this technical candidate; integer counts/revisions and entitlement
floor rules remain. Existing accepted ADRs and original acceptance criteria are unchanged.
Actual writer/consumer fixtures must use that contract before this interface is delivered.
Calendar/profile publishers 2.18/2.19 and duration consumer 3.7 implement their own
bounded portions; E5 source guards and immutable historical evidence remain binding.

## Consolidated adoption — accepted 2026-10-26

The user explicitly approved the completed consolidated planning package. The reviewed
choices and bounds in this contract are adopted under [the acceptance decision](../decisions/0171-work-calendar-precision-and-retention.md).
Earlier candidate/pending-review wording is historical and superseded for these choices.
Actual implementation and provider/database/browser/recovery proof remain delivery work.
The user requires a new Codex session before implementation; no runtime action here.

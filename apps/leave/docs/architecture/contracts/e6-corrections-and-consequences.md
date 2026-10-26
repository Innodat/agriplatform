# E6 corrections and consequences — owning contract proposal

**Status:** Complete E6 technical planning proposal for one user review; not accepted or implemented
**Date:** 2026-10-25
**Owners:** Leave request/accounting/source owners; People, Access, Content and notification owners for their actual HTTP boundaries

Product authority: [Features](../../features.md) §6/7/11/13/14/17/20 and accepted
L-0010/0038/0039/0048/0049/0052/0053/0054/0107/0111/0112/0128/0135/0151/0152/0159/0162.
Read their supersession chains. Historical acknowledgement wording does not override L-0151.
The user accepted the two cancellation refinements on 2026-10-25 in
[ADR-0168](../decisions/0168-cancellation-date-boundary-and-management-scope.md).
This contract supplies technical allocation, not a duplicate feature specification.
The [review package](../../../../../_bmad-output/planning-artifacts/e6-planning-review.md)
contains candidate owners, dependencies, evidence and remaining readiness gates.

## Reuse and limits

Reuse [E5 command/finalization](e5-request-command-and-finalization.md),
[E5 actions](e5-capabilities-and-commands.md), [E3 accounting](e3-request-accounting-interface.md),
[source projections](leave-configuration-and-rule-inputs.md),
[E5 reads](e5-read-models.md), [timed work](e5-timed-work-and-errors.md) and
[artifact strategy](e5-verification-and-artifact-map.md).
E6 extends their real first consumers; no new ledger, request kernel, receipt store,
impact service, universal task engine, transport, balance cache or employment master.
Planned Leave API/web, People and notification services are not established runtimes.
Content is an existing service; exact Leave/Expense shared delivery remains with E4.

## Authority and time binding

Every action checks current Access identity/member/admission and actual organization,
request/employment and action scope. Use typed organization scope with no account fallback.
The proposed catalog extension is explicit, never a live grant or wildcard:

| Exact capability / predicate | Proposed action boundary |
| --- | --- |
| `leave.request.own.cancel` | Employee's own future approved cancellation/Change leave; owner verified against enduring employment/person, not client ID |
| `leave.request.cancel` | Standard Approver's future target cancellation within ADR-0168 current ordinary management population; reason required |
| `leave.request.correct` plus `leave.admin.on_behalf` | Scoped Leave Manager administrative cancellation/replacement and rejected administrative correction input/resubmit, including started/past leave; represents the accepted manager correction authority explicitly |
| `leave.balance.adjust` with scoped Leave Manager review authority | Deficit review/handling; actual grant still a separate E3 adjustment |
| Existing source capabilities | Existing policy/schedule/calendar/People changes only; no independent approval, grant, medical document or correction right inferred |

Employee Change leave requires own cancellation plus own submission predicates. Other-employee
future replacement requires applicable cancellation **and** initial on-behalf authority;
started/past or administrative correction requires the manager correction combination.
A cancellation-only grant cannot create a replacement. Custom approval-only roles can omit
cancellation. Standard role catalog versions adopt L-0152 explicitly; custom-role expansion
requires existing reviewed adoption. No role-name string supplies runtime authority.
Access owns representation and current-check registration; Leave owns domain predicates.

For cancellation/Change leave use ADR-0168's accepted date boundary and management population.
Started requests are cancelled as whole records through correction authority, with any
retained actual absence represented by a linked replacement. No partial original edit.
New rejected administrative resubmit uses the same current correction combination;
original employee may use their existing own rejected lifecycle instead. Preserve independent
approval, funding and sensitive-document checks. Accountless employment can be a correction
target; lack of a login never creates an account, response or grant. Employee response
unavailability follows the existing E5 rule, never proxy consent.

## Read-only correction projection

6.1 extends the existing v1 reviewed source projection with a typed `correction` branch.
Carry actual source/command kind, expected revisions, request/cycle identities and retained
source references; the caller cannot submit trusted accounting lines or an authoritative
factual/discretionary flag. The existing specific source adapter classifies permitted intent.
A reason alone does not turn an illegal policy backdate into a factual correction.

For every affected employment/type/request preserve:

- original decision evidence reference and original approved dates, duration and allocation;
- recalculated result at the historical decision basis, distinctly labelled;
- current result through the chosen current basis including subsequent actual events;
- proposed per-date restored consumption, dependent earning reversal, expiry consequences,
  pending allocation and current deficit/eligibility differences, with typed tracked/untracked;
- current issue/remedy classification and actual independently authorized actions.

Use integer minutes/string bigints, ISO dates, UTC instants and typed not-applicable fields
from existing interfaces. Never present zero as an untracked pot or unavailable balance.
Read-only preview creates no snapshot/event/issue/receipt/notice. Extend the existing RFC-8785
SHA-256 review digest with these material facts and complete sorted affected membership,
including replacement input digest and original expected revision where applicable. Retain
no whole sensitive request payload in the receipt. Display paging does not truncate review.
Fresh inputs with identical material consequences may proceed only under the existing
revision/source protection contract; changed consequential details require renewed review.

## Cancellation accounting and protected execution

6.4 adds one pure owner-side cancellation replay adapter over E3 dated history. Its two
comparable histories differ only by cancellation of the target approved consumption, with
all other actual events, accepted source corrections, original period/expiry and stable
server event order retained. Evaluate cap/expiry/rollover/earning under original applicable
history, not the latest policy for every date. Restore the consumed source contributions
once; reverse only enabled extra earning. Do not persist daily derived accrual as new grants.
Compare effective current replay, not a replay that forgets earlier cancellation corrections.

6.5 extends the existing E3 event representation with versioned `request.cancel` effects:
scoped original request/cycle/consumption references, originating operation, immutable
before/after evidence and typed positive amount lines distinguishing restored consumption
from enabled-earning correction. Signed meaning is the closed line role, not a negative
amount accepted from the browser. Enforce one cancellation per original approved request
and scoped causal/effect uniqueness using actual request/event references. An original
consumed commitment remains historically consumed; it never becomes active or released.
Entirely unpaid and untracked cancellations preserve usage/history without fictional grants.
No new authoritative mutable balance total is introduced.

The replay adapter folds the original consumption and its cancellation into the
counterfactual effective history once. Restoration lines explain neutralization of the
original consumption; dependent-earning reversal lines explain the difference in derived
earning. They are not a second additive credit/debit on a result already calculated from
that folded history. Preserve their typed accounting-versus-reconciliation meaning in
the actual event schema and query adapter. Repeated cancellation, cancellation of another
request afterward and historical replay through both events must reproduce the same
result without restoring consumption or reversing derived earning twice. 6.4/6.5 own
these explicit conservation oracles; prior cancellation evidence remains immutable.

The protected command uses E5's actual dependency/reference/employee lock order and
complete-set reload/restart. Cancellation may change another approver's absence/coverage:
include real responsibility/gap/return dependencies, recompute current coverage and invoke
existing 5.25/5.10-B reassessment or record its required durable intent. It never manufactures
a human decision or prematurely restores authority before effective absence ends.
Other pending requests retain protected reservations and L-0151 changes/notice; initial
response remains governed by L-0162. Permitted factual/cancellation deficits are recorded
with attention, not a new cancellation approval gate. Discretionary source changes affecting
approved leave still block until actual authorized resolution under L-0128.

One Leave transaction owns request lifecycle, cancellation effects, evidence, local issue
updates, immutable audit, receipt and required notice/reassessment intent. Rollback removes
the entire new envelope. External HTTP/delivery occurs outside business locks. No external
notification failure undoes committed cancellation. Actual owner-specific initiator/executor
attribution and minimal structured diagnostic references remain separate.

## Commands, input and result contracts

Proposed routes below are app API design names, not currently runnable endpoints. Existing
E5 prefix/envelope conventions apply; export schemas and generate clients at actual delivery.

| Route suffix under existing `/requests/{request_id}` | Versioned input / effect owner |
| --- | --- |
| `POST /cancellation-review` | Existing read-only review envelope, no operation receipt; 6.4/6.5 |
| `POST /cancel` | `cancel_approved.v1`: operation UUID, expected request revision, review digest and reason where required; 6.5 |
| `POST /replacement-review` | Proposed replacement fields through existing E5 typed request input plus original revision; 6.9 |
| `POST /replace` | `replace_approved.v1`: operation UUID, original expected revision, current review digest, bounded typed replacement input, own initial acknowledgement or on-behalf reason as applicable; 6.9/6.11 |
| existing rejected correction GET/save/resubmit | Extend existing E5 endpoints with administrative context/authority, expected correction revision/rejected cycle and explicit resubmit; 6.13 |
| existing attention GET and issue detail | New typed deficit/approved-impact/correction-follow-up branches; 6.2/6.7 |
| `POST /correction-issues/{issue_id}/review` under app prefix | `review_deficit.v1`: operation UUID, expected issue revision/current digest, allowed outcome, reason, optional actual verified remedy reference; 6.15 |

Canonical fingerprints include all submitted expected revisions, target, command version,
reason/input and reviewed acknowledgement. Same identity with changed input conflicts.
One parent operation/receipt governs a combined replacement; internal cancel/submit helpers
never create competing user operations. Existing receipt structure gains constrained
command/result/issue branches under 6.5/6.9/6.15, preserving old rows and typed FKs. Each
consumer owns its exact enum/schema/constraint extension, not one speculative all-entity
migration. Recovery lookup rechecks current original actor and permitted target context.

Results extend the existing compact acknowledgement with typed `cancelled_request`,
`linked_replacement` (original and new request/cycle IDs), or `deficit_review` references
and committed revision(s). They distinguish local committed operation from current
request approval or later People consequences. No copied note/reason/document in receipts.
Current authorized reads return permitted current detail/history and allowed actions.
Safe typed error details distinguish inaccessible/denied, invalid input, not-approved/not-
future, stale review, known-uncommitted busy, verification unavailable and unresolved
original operation. Final `error_id` enum/HTTP/OpenAPI adapters bind to the established
shared error contract during delivery; never branch on messages or reuse draft-only IDs.

## Atomic replacement and input lifecycle

6.9 composes cancellation and actual E5 submission in the **same** Leave transaction.
Before committing, validate the original, target authority, complete replacement input,
historical schedule/policy, daily totals, funding, coverage, documents and fresh route.
Compute candidate balances/capacity after the planned original reversal; exclude only
that original from the protected candidate daily total. Keep it approved until the whole
transaction succeeds. Another employee/type/request commitment is never excluded.
Only the new request receives fresh decisions, initial own acknowledgement or initial
on-behalf employee-response requirements. Original decisions never transfer.

Commit cancellation, reversal, linked new ID/cycle, reservation or allowed immediate
finalization, both histories, operation result and required notice/issue intents together.
Validate E4 associations before commit through its existing exact observation/association
protocol. The new request has its own authorized association references to reusable verified
Content identity, never a move/delete of historical associations or unchecked blob copy.
Rollback leaves the original intact; finalized unassociated upload recovery follows E4.
Replacement rejection later leaves the original cancelled. Administrative rejection creates
follow-up at the real E5 rejection producer, not on a read or later reconciliation screen.

Initial Change leave input uses the existing task/form controls, with input preserved during
failed validation/review. It does not silently consume an ordinary new-application draft or
promise a new server-side administrative draft. Existing unsaved-edit/session behavior applies.
Rejected administrative replacement input **does** reuse L-0159's request/cycle correction
record and autosave, extending its current authorized writer predicate. Employee and manager
share its revision protection; no second per-actor record can silently overwrite it.
Old save/start/retry cannot resurrect a resubmitted/closed cycle. P-0050/0051 inline Retry
and exit-only Stay/Close anyway behavior apply through existing E1/E5 patterns.

## Issue identities, follow-up and deficit handling

6.2 creates only the first-used owner records/predicates: UUID issue ID, organization,
employment/type, typed cause kind and stable originating command/event/request reference,
immutable before/after evidence, current revision, current economic/eligibility result and
review status with server attribution. Scoped unique cause/discriminator prevents duplicate
issues on replay; scoped references prevent wrong employee/type/request links. Extend current
attention APIs, not a universal task table. Historical causes/review outcomes are immutable.
Newly observed independent cause or a material changed deficit cannot be dismissed by an
old reviewed revision. Store the actual source evidence boundary and invalidate/re-evaluate
current projection on relevant source/ledger/lifecycle changes; a screen read never applies
business consequences. Unknown verification is not resolution.

6.7 adds actual original/replacement links, administrative provenance and rejected-cycle
follow-up evidence at first use. New replacement ID is unique for one winning combined
operation/original; serial correction chains link their actual predecessor and cannot cycle.
Resubmit uses the same replacement ID, a new approval cycle and current follow-up projection.
Pending-again is in progress; approved or another explicitly verified domain resolution may
complete follow-up. Separate unresolved deficits/eligibility remain visible. Do not invent
a Dismiss button or auto-restore the original when a replacement is rejected/withdrawn/cancelled.
Terminal replacement without a valid corrected absence remains explicit unresolved attention.

6.15 records Keep open, Correct source information, Grant additional entitlement, or Record
decision without adjusting balance, with mandatory reason and employee-visible explanation.
Source/adjustment selections are handoffs: no source write, credit or completed remedy is
implied until its actual independently authorized operation is verified. Keep the actual
linked outcome and re-evaluated current issue revision. Record decision without adjustment
can finish the review while the economic deficit remains; present those facts separately.
No payroll/debt rules or automatic paid-to-unpaid rewrite. Current `leave.balance.adjust`
and manager scope are required for the review; source authority is separately checked.

## Source-family integration, not a historical editing engine

6.19–40 are the eleven real source-family API/browser pairs in the E6 story register,
matching E5 F01–F11. Each extends its existing actual source adapter/guard/review/result;
E5 pending/all-writer protection is an inherited prerequisite, not redelivered E6 work.
Discretionary approved-impact safety is already required on earlier writer activation.
These items add only actual permitted approved/historical correction consequences and
resolution/read integration, not permission to bypass existing effective-date/cutoff rules.
A family with no legal historical mutation proves the existing rejection and permitted
prospective remedy; it does not gain a backdate endpoint to justify this story.

6.41/42 specifically bind recorded employment-start/historical-period factual corrections
to People, which earlier scopes do not make a generic Leave edit. Use P-0062's existing
prepare/commit/cancel/outcome/participation barrier and recovery, with exact corrected
period revision, actor and reason. People owns interval structural integrity and retained
employment/person identity; Leave never accesses its tables. No merging, identity replacement,
employment deletion, automatic app grant or provider sync. Source commit and Leave consequence
commit remain separate, durable and truthfully reported. Accountless targets remain valid;
notifications use the shared actual recipient rules without synthetic accounts.

## Delivery verification and impact obligations

First actual owners introduce only required schema/event/API changes with controlled
compatible migrations. Test ordinary upgrade/repeat/failure, previous supported consumers,
real runtime DDL/immutability/RLS/cross-owner denials, scoped uniqueness, reversal conservation,
rollback at each local effect and concurrent alternate paths. Follow
[focused migration verification](../../../../../platform/docs/development/migration-verification.md).
6.46 composes E6 release evidence; it does not postpone first-consumer security or compatibility.

Use inherited 30-second execution, 3-second fact reads, 1-second lock acquisition inside
5-second local transactions and 35-second browser wait; existing bounded recovery budgets
apply. Do not hold transactions during human review or external requests. Large synchronous
historical replay exceeding budget fails without business mutation; retain input for review.
Select concrete multi-year source/request/concurrency fixtures and response targets with
actual consuming packages before readiness; 100/1000 employee baselines are not measurements.

Exact artifact/command strategy is inherited from E5's artifact map: owning API tests and
OpenAPI export/check, generated clients/check, focused type/browser checks, native DB and
coordinated release checks. Planned Leave paths/commands are not passing executable tests.
ATDD observes real relevant failures after implementation authorization, then focused TDD
and affected suites. E6-xx-ACyy IDs in epics are stable scenario references; record actual
fixture/test node, red/green command/results and evidence limits in each delivery item.

Scaffold: reuse/prove neutral reviewed-command/recovery/native fixture patterns with first
consumers; update template/installer/managed copies and preservation tests if changed.
Shared UI: reuse existing controls and only promote proven neutral additions; Leave owns
all correction content. Agent context: existing rules suffice; update generated guidance
only if commands/contracts actually change. Docs: source specs/UX/tracker/contracts/test
mapping remain synchronized with accepted decisions. ADR: accepted 0168 binds the approved boundary/scope choices;
accepted ADRs unchanged. No runtime work, migration, grants, deploy or readiness approval.

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

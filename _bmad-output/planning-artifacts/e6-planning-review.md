# E6 planning — one review package

**Prepared:** 2026-10-25. **Status:** Both E6 boundary/scope choices accepted by the user;
remaining delivery-item proposal status is unchanged. E5 planning is already closed.
This is BMAD step 03 work, not approved stories or implementation readiness. The user
requested planning first and one review afterward, superseding prior guided-story cadence.
E5 stays closed at 88 assessed items and 230 source criteria; E7/E8 and global validation
remain separate unfinished work.

## What to review

The plan delivers approved cancellation, linked replacement, administrative/historical
correction, deficit handling and visible follow-up. It reuses E3 accounting and E5 request,
review, recovery, coverage and notification foundations under their actual owners.
There are **46 proposed delivery items in eight groups**, with **138 story-specific
acceptance criteria** plus explicitly shared security/recovery/UI obligations. The number
reflects API/browser splits and eleven actual source families, not 46 new product features.

The user accepted both product refinements on 2026-10-25, recorded in
[ADR-0168](../../apps/leave/docs/architecture/decisions/0168-cancellation-date-boundary-and-management-scope.md):

1. **Future cancellation ends at the start of the first requested date in the employee's
   work timezone.** This covers full/half/hour requests without inventing absence times.
   Started/past requests use existing Leave Manager correction authority. The same cutoff
   applies to Change leave; a multi-date request is not partly edited in place.
2. **Standard Approver cancellation uses their current ordinary responsibility population,**
   aligned with the established initial on-behalf population, rather than old decision
   authorship or temporary/fallback cover. Cancellation and replacement creation still
   require their separate explicit capabilities. Manager correction scope stays as accepted.

Both choices are accepted and synchronized to Features, spine, written UX and the owning
contract. The user's approval concerns these choices; it is not silently expanded into
approval of every delivery-item detail. E5 has been closed since explicit agreement on
2026-10-25 and needs no repeat review. No story-by-story review is required.

## Navigation

- [Proposed stories and acceptance criteria](epics.md#e6--correct-leave-and-resolve-its-consequences)
- [Owning technical contract](../../apps/leave/docs/architecture/contracts/e6-corrections-and-consequences.md)
- [Source-to-scenario allocation and verification limits](e6-coverage-audit.md)
- [Inherited E5 graph and actual external owners](e5-delivery-graph-reconciliation.md)

## Delivery groups and outcomes

| Group | Candidates | Result and boundary |
| --- | --- | --- |
| 1/8 Consequences and attention | 6.1–3 | Read-only original/revised/current projection and minimum real deficit/affected-request attention before any new correction producer |
| 2/8 Cancellation | 6.4–6 | Authoritative reversal and earning/expiry consequences, one protected command, existing confirmation UI; no extra approval |
| 3/8 Linked replacement | 6.7–10 | First-needed follow-up lifecycle support then atomic cancel-and-submit; invalid replacement leaves original approved |
| 4/8 Administrative correction | 6.11–14 | Scoped past/current/future correction and rejected administrative replacement editing/resubmit, with separate rights and fresh response/approval |
| 5/8 Deficit handling | 6.15–16 | Four existing review outcomes, reason and employee explanation; only a separately authorized actual remedy changes facts/entitlement |
| 6/8 Historical explanation | 6.17–18 | Residual linked history/calendar and original Balance at approval versus revised history/current balance; no duplicate current absence |
| 7/8 Actual source integration | 6.19–42 | Eleven existing source-family API/browser deltas plus narrow People recorded-date correction; no new history editor or blanket backdate permission |
| 8/8 Composition and release evidence | 6.43–46 | Own cancellation/replacement, administrative follow-up, historical/deficit journeys and focused migration/event compatibility/performance evidence |

## Dependency and first-use reconciliation

Each row below is a proposed executable candidate, with **only earlier internal
predecessors**. E1–E5 external owners must actually deliver the relevant artifact before
this candidate starts. A source/UI item inherits its existing owner's API/browser baseline;
those are not hidden inside the E6 size. Evidence items fill composition gaps, never defer
required transactional/security/notification proof until the end.

| Item | Internal prerequisites | Actual bounded delta and single-agent assessment |
| --- | --- | --- |
| 6.1 | None | Extend the existing source-impact projection with approved evidence, historical recalculation and deficit classifications; reuse E3 replay and E5 review digest. **Retain one candidate**, conditional on actual predecessors. |
| 6.2 | 6.1 | First-needed scoped issue identity, revision, cause/evidence links and current read/update interface, extending existing attention infrastructure; no resolution command yet. **Retain one candidate**, conditional on actual predecessors. |
| 6.3 | 6.2 | Small existing-list/detail integration with truthful load states and permitted existing remedy links; no new dashboard. **Retain one candidate**, conditional on actual predecessors. |
| 6.4 | 6.1 | One E3-owned counterfactual replay adapter and typed reversal plan, including source provenance; no second calculator or ledger. **Retain one candidate**, conditional on actual predecessors. |
| 6.5 | 6.2, 6.3, 6.4 | Actual cancellation producer, E3 reversal event extension, existing operation/result target extension, minimum current detail/history/notification and coverage reassessment integration. **Retain one candidate**, conditional on actual predecessors. |
| 6.6 | 6.5 | Existing request action/dialog and generated API client integration, reason on behalf, effect rows, unknown-outcome recovery. **Retain one candidate**, conditional on actual predecessors. |
| 6.7 | 6.2 | First-use correction link metadata and follow-up predicate; extend actual E5 reject/resubmit/finalization producers and minimum current detail before replacement activation. **Retain one candidate**, conditional on actual predecessors. |
| 6.8 | 6.3, 6.7 | Existing attention/detail branch with prominent rejection reason, linked original and gated resubmit navigation. **Retain one candidate**, conditional on actual predecessors. |
| 6.9 | 6.5, 6.7, 6.8 | One local cancel-and-submit composition over E5 submission/finalization and E3 reversal; no second request engine or ordinary draft mutation. **Retain one candidate**, conditional on actual predecessors. |
| 6.10 | 6.6, 6.9 | Reuse Apply controls and existing attachments/review; local task input is not a new persisted administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.11 | 6.9 | Administrative mode of the same replacement command; current manager/on-behalf authorization, reason, initiator/executor attribution, fresh initial response and employee-notice integration. **Retain one candidate**, conditional on actual predecessors. |
| 6.12 | 6.10, 6.11 | Approved desktop drawer/mobile surface with original/revised/restore/reserve comparison; no permission or approval bypass. **Retain one candidate**, conditional on actual predecessors. |
| 6.13 | 6.7, 6.11 | Narrow administrative access adapter for existing per-rejected-cycle correction input and E5 resubmit; shared revision with employee edits, not a second draft store. **Retain one candidate**, conditional on actual predecessors. |
| 6.14 | 6.8, 6.12, 6.13 | Existing rejected edit/autosave UI with scoped administrative entry; inline Retry and exit-only Stay/Close anyway. **Retain one candidate**, conditional on actual predecessors. |
| 6.15 | 6.2 | Existing issue outcome command/revision/audit/notice extension; actual adjustment/source actions stay with their existing owners. **Retain one candidate**, conditional on actual predecessors. |
| 6.16 | 6.3, 6.15 | Complete the existing deficit preview with reason, source/adjustment links and current outcome feedback; no new adjustment editor. **Retain one candidate**, conditional on actual predecessors. |
| 6.17 | 6.9, 6.11, 6.13, 6.15 | Residual E5 history/balance projection enrichment only; each prior producer already owns its minimum result/detail/history link. **Retain one candidate**, conditional on actual predecessors. |
| 6.18 | 6.10, 6.12, 6.14, 6.16, 6.17 | Residual Calendar/List/detail composition over existing E5 collections; no second calendar or new preference store. **Retain one candidate**, conditional on actual predecessors. |
| 6.19 | 6.1, 6.2, 6.3, 6.15 | Only the one-off balance adjustments API delta over actual 3.29 / 5.15-A/B; permission leave.balance.adjust; variants: Add and Deduct, including a correction of an earlier adjustment through another explained entry. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.20 | 6.19 | Only the existing one-off balance adjustments browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.21 | 6.1, 6.2, 6.3, 6.15 | Only the recurring entitlement changes API delta over actual 3.30 / 5.15-C/D; permission leave.policy.manage; variants: explicit recurring allowance and return to policy at an actual leave-period boundary. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.22 | 6.21 | Only the existing recurring entitlement changes browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.23 | 6.1, 6.2, 6.3, 6.15 | Only the used-policy publication API delta over actual 3.34-A/B / 5.15-E/F; permission leave.policy.manage; variants: allowed used-policy transitions with actual holders, dated versions and approved request snapshots. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.24 | 6.23 | Only the existing used-policy publication browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.25 | 6.1, 6.2, 6.3, 6.15 | Only the scheduled policy amendments and cancellations API delta over actual 3.35-A/B / 5.15-G/H; permission leave.policy.manage; variants: both amend and cancel before the first affected effect; already-effective changes use the existing prospective path. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.26 | 6.25 | Only the existing scheduled policy amendments and cancellations browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.27 | 6.1, 6.2, 6.3, 6.15 | Only the employee policy assignments API delta over actual 3.28/3.36-A/B / 5.15-I/J; permission leave.policy.manage; variants: initial, replacement and end assignment, including gaps and original earned-period/expiry provenance. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.28 | 6.27 | Only the existing employee policy assignments browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.29 | 6.1, 6.2, 6.3, 6.15 | Only the employment periods and departure API delta over actual 2.11/12/13 / 5.15-K/L; permission People owner authority plus separately authorized Leave consequences; variants: initial verified empty case, period-add/rehire and employment end, including spent upfront grants and after-end requests. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.30 | 6.29 | Only the existing employment periods and departure browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.31 | 6.1, 6.2, 6.3, 6.15 | Only the employee work-setting overrides and resets API delta over actual 2.22 / 5.15-M/N; permission leave.schedule.manage; variants: each explicit field and real reset to inheritance, including timezone, calendar and standard-day changes. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.32 | 6.31 | Only the existing employee work-setting overrides and resets browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.33 | 6.1, 6.2, 6.3, 6.15 | Only the employee work-profile assignments API delta over actual 2.20 / 5.15-O/P; permission leave.schedule.manage; variants: initial/change/end explicit profile selection and actual fallback-to-default users. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.34 | 6.33 | Only the existing employee work-profile assignments browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.35 | 6.1, 6.2, 6.3, 6.15 | Only the organization-default work profiles API delta over actual 2.21 / 5.15-Q/R; permission leave.schedule.manage; variants: empty/default replacement, actual followers and partial overrides without touching unrelated explicit settings. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.36 | 6.35 | Only the existing organization-default work profiles browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.37 | 6.1, 6.2, 6.3, 6.15 | Only the shared work-profile publication API delta over actual 2.23 / 5.15-S/T; permission leave.schedule.manage; variants: explicit holders, default followers, partial overrides and concurrent new holders of actual published versions. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.38 | 6.37 | Only the existing shared work-profile publication browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.39 | 6.1, 6.2, 6.3, 6.15 | Only the holiday-calendar changes API delta over actual 2.18 / 5.15-U/V; permission leave.calendar.manage; variants: add/edit/remove, absent slots, full/partial closure and downstream earning effects outside directly intersecting request dates. Reuse the common projection, guards, replay, outcome and notice machinery. **Retain one candidate**, conditional on actual predecessors. |
| 6.40 | 6.39 | Only the existing holiday-calendar changes browser review/result delta; no new source editor, permissions screen or administrative draft. **Retain one candidate**, conditional on actual predecessors. |
| 6.41 | 6.29 | Narrow People date-correction extension of E2 employment history/attempt contracts and 6.29, covering start/end historical errors; no employment merge/delete/provider sync. **Retain one candidate**, conditional on actual predecessors. |
| 6.42 | 6.30, 6.41 | Narrow date correction edit/review mode over existing People period UI, with separate source/Leave access and no new HR catalogue. **Retain one candidate**, conditional on actual predecessors. |
| 6.43 | 6.6, 6.10, 6.18 | Bounded actual API/DB/browser composition evidence; fill integration gaps only, no replay of every foundational test. **Retain one candidate**, conditional on actual predecessors. |
| 6.44 | 6.12, 6.14, 6.18 | One actual returned-early administrative journey through reject, saved correction, explicit resubmit, employee initial response and finalization where required. **Retain one candidate**, conditional on actual predecessors. |
| 6.45 | 6.16, 6.18, 6.20, 6.22, 6.24, 6.26, 6.28, 6.30, 6.32, 6.34, 6.36, 6.38, 6.40, 6.42 | Bounded composition of source correction plus one deficit handling journey; reference each family’s own producer tests rather than retesting all variants here. **Retain one candidate**, conditional on actual predecessors. |
| 6.46 | 6.43, 6.44, 6.45 | E6-specific compatibility/failure/native-permission and representative replay evidence in existing release tooling; no new release framework or pilot activation. **Retain one candidate**, conditional on actual predecessors. |

The qualitative assessment counts real schema/model/API/adapter, focused native/contract
proof and the minimum feedback named in the item. API and browser for each source family
remain separate, as in E5; People recorded-date correction is also split from ordinary
employment-end integration. A pure replay adapter does not carry UI or shared-service
implementation. No measured hours, guarantee of one sitting, or runtime PASS is claimed.
If the actual predecessor contract is missing or the implementation reveals a wider delta,
resolve that prerequisite or split the concrete excess before delivery; do not hide it in
an omnibus integration story.

First-use findings already incorporated:

- 6.2/3 provide minimum issue storage/read/display before 6.5 cancellation can create a deficit.
- 6.7/8 provide administrative-link/follow-up schema, real rejection/resubmit/finalization
  producer hooks and minimum attention before 6.9/11 can create linked corrections.
- Every actual command provides its own minimum outcome/current detail/history link,
  generated types and notification intent. Residual 6.17/18 cannot be a prerequisite for
  truthful early results. Source pairs extend their existing editor, not a later omnibus UI.
- 6.9 owns **one** transaction for original cancellation plus new submission. It invokes
  completed E5 internal helpers; there is no public cancel call followed by a submit call.
- 6.13 extends current rejected correction input for administrative authority and shared
  revision handling. It does not reuse initial on-behalf authority as historical authority.

## Concrete external predecessors and delivered credit

The full P01–P12 register remains in the E5 graph. E6 adds no parallel foundational stories.
Read current owner status at delivery; repository implementation is not deployed-state proof.

| E6 consumers | Real predecessor owners | Delivered evidence credited / actual work still required |
| --- | --- | --- |
| All API/browser | E1 ENV/P1/SERVICE/WRITE/REF/VERIFY; ID-A/B; ACCESS-A/B; A1/CONTEXT; operation/session consumers | Existing scaffold bootstrap/managed Auth/API-client/Access/KDG native fixture candidates are reusable. Leave still has only README/docs; no Leave api/web package is inferred. Full public generator is undelivered. |
| 6.1/4/5/9 and source adapters | E3 3.7–18, 3.21, actual 3.29/30/34/35/36, evidence/portion interface | E3 owns deterministic calculation, cap/expiry/rollover/order/source periods and immutable event/evidence representation; E6 adds cancellation/approved-history adapters, not this foundation. |
| Request lifecycle/authority | E5 5.10-A/B/C, 5.8-A, 5.11-A/B, 5.12-A/B, 5.18-A/B, 5.19-A, 5.20-A/B, 5.30-A/B, 5.29-A/B | Use actual core/current result/receipt/submit/response/reject/resubmit/history interfaces. These are planned Leave deliverables, not existing runtime services. |
| Source variants | Existing E2/E3 source items and all actual 5.15-A–V consumers | E5 owns pending consequences and activation safeguards for approved impacts. E6 owns only approved/history correction integrations and additional read/remedy surfaces described here. |
| 6.29/30/41/42 | E1-PEOPLE; E2 2.11–13; 5.15-K/L; P-0062/63 People/Access owners | Existing Access organization/grant registry is implemented; People current source/attempt/participation/management/admission contracts still need actual delivery. Extend that owner for recorded dates, never another People service. |
| Cancellation authority/role adoption | E1-ACCESS-A/B, E2 2.2–5, E5 exact current scope; proposed ADR-0168 | Existing Access catalog/assignment/admission mechanics are credited. E6 actual capability strings, typed resources/check adapters and deliberate default/custom-role adoption remain new consumers. |
| All notice-producing commands | E3 3.22/23/24/25-A/B/26/27 | Shared transport/acceptance/channels/inbox plus Leave outbox/worker are predecessors. E6 owns only versioned correction/cancellation/deficit events and exact recipient/content/intents. |
| Replacement attachments | E4 4.4/4.7/4.13 and dependent provider/private-read owners; E5 5.9/12/20 | Content exists; Leave app-target/reference/cleanup/fixed-byte integration is still actual E4 work coordinated with Expense. No E6 upload service or unchecked association copy. |
| Absence/coverage consequence | E5 5.28-C, 5.25-A, 5.10-B, related authority/coverage/source producers | Reuse actual gap/return/reassessment and due-work primitives; cancellation integrates a real absence-ending producer, not a new timer/approval kernel. |
| Native and release evidence | Existing platform migration helpers, owning E1/E3/E5 migrations, API-client and release tooling | KDG proves its limited initial-ledger native behavior. Actual E6 business RLS/rollback/previous-version/event/adoption evidence is still required; no mock stands in for it. |

## Duplicate-work disposition

| Existing owner | Retained ownership / E6 delta |
| --- | --- |
| E1 ordinary draft/autosave/session/receipts | New replacement task does not consume or overwrite the ordinary draft; E6 rejected input uses the actual E5 cycle extension and common outcome model. |
| E2 People and working arrangements | All source facts/settings stay there; E6 introduces no source-owned table copy or new unrestricted retroactive editor. |
| E3 calculation/adjustment | Correct a wrong adjustment by another explained adjustment using 3.29. E6 deficit review references that real outcome rather than adding a credit command or mutable balance repair. |
| E5 finalization/commitment | Original consumed head stays consumed. E6 appends cancellation reversal; new replacement has a fresh request/cycle/commitment. Old decisions never approve it. |
| E5 pending changes | L-0151 later changes notify without renewed acknowledgement; any required initial on-behalf response remains current. New replacement initial response is a new submission case. |
| E5 source guards/approved-impact safety | Already binding before real writer activation. E6 does not delay or reimplement that safeguard; actual historical/approved-resolution adapters extend it. |
| E5 rejected resubmit | Employee path stays E5. E6 adds only the explicitly authorized administrative replacement context, preserving the same ID/cycle-input revision mechanism. |
| E5 attention/calendar/history | Extend the existing typed branches; minimum first-use evidence is in each producer, residual enrichment in 6.17/18. No new dashboard, preference store or absence calendar. |
| E7/E8 | Wider overview/search/report/export, imports, consultant email approval and pilot/UAT stay there. E6 provides compatible correction facts and release evidence, without importing or activating pilot data. |

## Impact decisions for every candidate

These decisions apply to each of the 46 rows; actual delivery records any changed impact
beside its AC/test evidence rather than starting another lifecycle or spec.

| Candidate class | Scaffold | Shared UI | Agent context | Documentation | ADR |
| --- | --- | --- | --- | --- | --- |
| 6.1/4 calculation/projection | Reuse owner-local typed evidence/fixtures; promote only proven neutral gaps | No new shared domain widget | Existing instructions suffice | Owning accounting/source contract plus test map | Existing calculation ADRs; no policy change |
| 6.2/5/7/9/11/13/15 and source APIs | Reuse/prove scoped writes, receipts, native fixtures and generated API-client maintenance; update owning template/installer/preservation tests if generic behavior changes | Existing review/error adapters only | Update generated owner guidance if actual commands change | Owning schemas/contracts, exact source-to-test and rollout notes | Proposed 0168 for cancellation boundaries; others existing accepted rules |
| All browser items, including source editors | Maintain generated client/template sources through their owner | Reuse proven accessible drawer/dialog/review/error/list controls; keep Leave content local | Existing instructions suffice | Approved UX implementation evidence and permission/state cases | No extra UX policy decision |
| 6.41/42 People source correction | People-owned HTTP/history/attempt adoption with same-item neutral fixes | Existing employee task/review controls | Existing ownership rules suffice | People source/Leave consequence contract and consumer proof | Existing P-0042/0062 and L-0107/0128; no identity/grant change |
| 6.43–46 proof | Promote only demonstrated neutral fixtures; domain journeys stay in Leave | Actual keyboard/mobile/focus evidence | Record actual package commands when created | Requirement/test/result and recovery/release evidence | No gate closed by planning |

No accepted ADR, product requirement or approved UX rule is silently changed in this pass.
ADR-0168 is now accepted and synchronized to Features, spine and written UX. Actual Access
consumer/default-role adoption remains with its authorized implementation item before
affected readiness.
Other proposed implementation details remain reviewable here and in the owning contract.

## Verification and remaining gates

The coverage audit allocates E6 source obligations and records exact selected source hashes.
Story IDs/AC IDs, prior E5 source hashes, graph order, links, and whitespace are checked as
**documentation evidence only**. It is not proof that proposed acceptance scenarios pass.
No Leave code, migration, grants, providers, production mutation, commit or deployment ran.

Each actual item must observe its relevant acceptance failure before implementation,
then focused TDD and affected contract/native/browser tests. Reuse the exact command
strategy in E5's artifact map once the actual owner package exists. No root dev/build
or fabricated test filename is presented as a working Leave test command.
Before affected readiness, bind real migration/constraints/OpenAPI/generated artifacts,
actual fixture/test-node paths and red/green commands, independently authorized service
consumers, representative multi-year histories and numeric performance targets, plus
compatibility/recovery evidence. Existing 30-second execution/5-second transaction budgets
and the 100/1000 employee baseline are reused, not claimed measured.

After this single E6 review, reconcile accepted changes and close only E6 story planning.
Then plan E7/E8 and complete whole-product atomic requirement/UX/NFR coverage and BMAD
readiness. Step 04 has not been loaded. The first implementation slice remains sign in →
select organization → create/resume draft → autosave → close → reopen.

### Recorded planning checks — 2026-10-25

- `python3 /tmp/check-leave-e6-planning.py` — PASS: 46 ordered unique story IDs,
  138 AC IDs, exact 46-row dependency/size register, 116 edges and 11 acyclic layers,
  50 obligation clusters, eleven source families, sixteen unchanged Features paragraph
  hashes, nineteen relative links/anchors, proposed ADR status and unchanged step status.
- `python3 /tmp/leave-e5-final-check.py` — PASS: existing 81 suffixed E5 items plus
  seven foundations, 88-node/304-edge/21-layer graph, existing size set, all 230 original
  E5 criterion hashes unchanged and twelve external owner clusters retained.
- `git diff --check -- _bmad-output/planning-artifacts/epics.md apps/leave/docs/architecture/ARCHITECTURE-SPINE.md apps/leave/docs/architecture/decisions/README.md apps/leave/docs/implementation-plan.md apps/leave/docs/planning-handoff-e3.md`
  — PASS, no whitespace errors in the scoped tracked diff. New E6 files separately
  checked for trailing whitespace and final-newline consistency.

The temporary scripts are document audits, not repository product tests or new generic
workflow tooling. These results establish document integrity within their stated scope;
no acceptance, native database, runtime service, migration or release check was executed.

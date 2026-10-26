# E7 planning — one review package

**Prepared:** 2026-10-25. **Status:** E7 planning closed by user approval; both ADR-0169 choices accepted.
E5 is closed and needs no further review. Both E6 choices in ADR-0168 are accepted.
The user directed “next”; this package prepares the next approved epic without another
story-by-story discussion. It does not silently change earlier delivery-item approval
status. E8 and global validation/readiness remain open; BMAD step 03 continues.

## Accepted choices

E7 adds the wider organization overview, six report families, matching audited CSV and
searchable protected audit history. Existing arithmetic, request decisions, corrections,
source facts, privacy and notification engines keep their current owners.

[Accepted ADR-0169](../../apps/leave/docs/architecture/decisions/0169-reporting-time-basis-and-derived-team-grouping.md)
records the two choices accepted with this package:

1. **Historical balances show corrected history known when the report is generated.**
   The selected balance date and generated-at context are explicit. Original Balance at
   approval evidence stays separately available; MVP adds no “what the system knew then” mode.
2. **Staffing views use current teams; historical reports use the relationships effective
   for their facts.** Overview/upcoming/aging use current supervisor groups. Dated balance
   uses its balance date; used leave is attributed on each leave date, splitting minutes
   across a mid-request team change without duplicating totals. Other effective-dated
   report rows use their own effective date. Current permission always restricts access.

Everything else implements the accepted Features/ADRs/UX. The exact read/export/query
limits and performance targets are proposed technical baselines to prove during delivery,
not claims about current performance or retention. No new implementation is authorized.

## Navigation and scope

- [31 proposed stories and 124 specific acceptance criteria](epics.md#e7--understand-organization-absence-and-report-with-privacy)
- [Owning query/export/audit contract](../../apps/leave/docs/architecture/contracts/e7-overview-reports-and-audit.md)
- [Source allocation and verification limits](e7-coverage-audit.md)

| Group | Delivery candidates | Result |
| --- | --- | --- |
| 1/4 Organization overview | 7.1–6 | Scoped query, desktop Timeline/mobile List, approved filters/preferences, accessible management navigation and existing authorized details |
| 2/4 Six report families | 7.7–18 | Current/dated balances, accrual/adjustment history, used leave, upcoming absence, approval aging and override/administrative-adjustment reports |
| 3/4 Matching CSV | 7.19–20 | All matching permitted rows, safe CSV text and audited generation with bounded execution, clear progress/Retry export |
| 4/4 Audit and evidence | 7.21–31 | Actual owner-specific evidence reads, protected local/federated chronology/search/detail, real composition and release/performance proof |

## Dependency and single-agent size register

Rows are executable candidates, not new standalone product features. Internal dependencies
always reference earlier items; actual external artifacts below remain prerequisites.
Size counts focused contract/native/client/UI tests, current authorization, truthful
response states and the same-item five impacts. No measured duration or runtime PASS.

| Item | Internal predecessors | Actual bounded delta and assessment |
| --- | --- | --- |
| 7.1 | None | One existing Leave read-model extension for scoped employee rows, intersecting requests, source observations, allowed filters and schedule/holiday context; no second request or calendar store. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.2 | 7.1 | Desktop timeline over 7.1 with fixed names/headings, selectable bars, date navigation, visible legend and inherited drawer; no calendar editing engine. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.3 | 7.1, 7.2 | Mobile date-grouped list plus Timeline/List choice and existing provisional filter controls; no third month view. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.4 | 7.1 | Extend the existing minimal E5 account/org preference owner with a versioned overview-filter branch; no settings service, saved-report system or date-window persistence. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.5 | 7.3, 7.4 | Wire immediate applied preferences and invalid-selection notice into the existing desktop/mobile controls; not autosave of provisional mobile selections. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.6 | 7.2, 7.3 | Residual existing home composition only: heading overview action and permitted Records destinations; existing attention engines stay E5/E6. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.7 | None | Report-specific read adapter and CSV row serializer over completed E3 balance replay/evidence, with current and historical variants; no new calculator or stored report balance. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.8 | 7.6, 7.7 | First actual Leave reporting shell/table/date/pagination consumer and balance renderer; prove neutral shared pieces here, without a separate reporting service. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.9 | None | Only the accrual-adjustments query/typed rows/totals and CSV serializer over actual 3.9/3.17/3.29/3.31; date basis effective_date; no duplicate source model. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.10 | 7.8, 7.9 | One report renderer/control adapter in the completed 7.8 shell, reusing approved table/filter/empty/paging patterns; no new report framework. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.11 | None | Only the leave-used query/typed rows/totals and CSV serializer over actual 3.7/5.30/6.17; date basis leave_date; no duplicate source model. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.12 | 7.8, 7.11 | One report renderer/control adapter in the completed 7.8 shell, reusing approved table/filter/empty/paging patterns; no new report framework. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.13 | None | Only the upcoming query/typed rows/totals and CSV serializer over actual 5.29/5.30/7.1; date basis leave_date; no duplicate source model. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.14 | 7.8, 7.13 | One report renderer/control adapter in the completed 7.8 shell, reusing approved table/filter/empty/paging patterns; no new report framework. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.15 | None | Only the approval-aging query/typed rows/totals and CSV serializer over actual 5.16/5.18/5.26/5.27; date basis current_actionable_wait; no duplicate source model. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.16 | 7.8, 7.15 | One report renderer/control adapter in the completed 7.8 shell, reusing approved table/filter/empty/paging patterns; no new report framework. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.17 | None | Only the override-adjustments query/typed rows/totals and CSV serializer over actual 3.29/3.30/5.13/5.15/6.17; date basis effective_date; no duplicate source model. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.18 | 7.8, 7.17 | One report renderer/control adapter in the completed 7.8 shell, reusing approved table/filter/empty/paging patterns; no new report framework. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.19 | 7.7, 7.9, 7.11, 7.13, 7.15, 7.17 | Bounded synchronous CSV endpoint over the six completed query/serializer adapters, scoped export audit and safe output; no export queue, object-store link or second snapshot service. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.20 | 7.10, 7.12, 7.14, 7.16, 7.18, 7.19 | Shared permitted toolbar/download client plus actual wiring on all six report renderers; no native file access or persisted export library. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.21 | None | One bounded owner-local read projection plus its Leave HTTP adapter over existing services/access actor/member/grant/organization event infrastructure and E1/E2 owner contracts; no event rewriting, credential widening or common audit-write service. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.22 | None | One bounded owner-local read projection plus its Leave HTTP adapter over planned E1-PEOPLE and E2 employment/supervisor/department/location history with P-0062; no event rewriting, credential widening or common audit-write service. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.23 | None | One bounded owner-local read projection plus its Leave HTTP adapter over existing services/content-service and actual E4 app-owned association/private-read adoption; no event rewriting, credential widening or common audit-write service. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.24 | None | One bounded owner-local read projection plus its Leave HTTP adapter over planned E3 shared notification acceptance/channels and existing Leave recovery contracts; no event rewriting, credential widening or common audit-write service. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.25 | None | Typed local audit read/search/detail adapter and necessary existing-event indexes over actual producer records; no capture-backfill or per-autosave logging. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.26 | 7.21, 7.22, 7.23, 7.24, 7.25 | Bounded Leave read-only merge adapter over five completed owner projections, independently authorized detail links and source-coverage status; no central writable audit warehouse. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.27 | 7.6, 7.26 | Existing Records destination, filters/table/expandable before-after and owner-linked detail using completed query adapters; no audit export screen or support queue. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.28 | 7.8, 7.10, 7.12, 7.14, 7.16, 7.18, 7.20 | Bounded report/export composition fixtures, referencing each family’s own arithmetic/query tests; no first implementation of required field/security rules. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.29 | 7.5, 7.6 | One actual overview journey plus focused API/audience/keyboard/mobile assertions using earlier source fixtures. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.30 | 7.27 | Bounded actual owner producer → HTTP projection → merged list → permitted-detail journey; earlier owner APIs retain own contract/native proof. **Retain one candidate** conditional on actual predecessor delivery. |
| 7.31 | 7.28, 7.29, 7.30 | E7-specific measured query/export/audit and native restricted-role/schema/client compatibility in existing qualification tooling; no pilot activation. **Retain one candidate** conditional on actual predecessor delivery. |

The largest algorithmic integration is 7.26: it only merges bounded read pages from four
already-delivered HTTP projections and the local adapter. It does not implement those
owners, their event capture, cross-service snapshot isolation or a new warehouse. Each
source projection is a separate actual item (7.21–24); each of the six report queries and
its browser renderer is likewise split. 7.19 reuses completed report serializers rather
than defining all reports inside the export endpoint. 7.31 uses completed owner native/
release tooling, not a new deployment framework. If actual missing owner work expands a
delta, resolve or split that concrete prerequisite before delivery; don't assume it exists.

First-use reconciliation:

- 7.1 owns minimum scoped query/audience/context before either overview presentation.
  Current detail/correction/approval actions use real E5/E6 owners, not new handlers.
- 7.7/8 own the first concrete report adapter/layout. Later report pairs add only their
  query/serializer/renderer; there is no speculative framework pre-story.
- Every report's API owner includes its permitted CSV row schema. 7.19 introduces actual
  generation/export-audit evidence; it does not depend on the later searchable audit UI.
- Earlier producers already retain business evidence. 7.21–25 add reads, not delayed
  capture. Shared read source and actual field scope precede federated chronology.
- 7.6 shows only delivered/authorized destinations; each report/audit browser item makes
  its completed destination reachable. No forward dependency on undelivered screens.
- 7.28–31 fill actual composition/qualification gaps; they never postpone privacy,
  required evidence, failure behavior or native security from first real consumers.

## Actual external owner prerequisites and delivered credit

The E5 P01–P12 register remains the baseline. These are existing owners, not a new
parallel set of platform stories. Repository code/contract evidence is not deployed proof.

| E7 consumers | Actual predecessor items | Existing evidence credited / remaining consumer work |
| --- | --- | --- |
| All APIs/browsers | E1 ENV/P1/SERVICE/WRITE/REF/VERIFY, ID-A/B, ACCESS-A/B, A1/CONTEXT and actual Leave package | Implemented neutral bootstrap/Auth/API-client/Access and KDG native fixtures are reuse candidates. Leave still has README/docs only; actual api/web/domain packages remain planned. Public generator is not assumed delivered. |
| Overview and source grouping | E1-PEOPLE; E2 2.11–23/26; E5 5.17 current team/source adapters | People HTTP facts/history/current/as-of scoped queries must actually exist. E7 extends their real history selector, never a duplicated Leave team/employee table or employment-based authorization. |
| Current/dated balances and history | E3 3.7–18/3.29/3.30/3.31 and actual evidence/portion interfaces; E5 5.8-A | Actual authoritative replay and immutable event provenance/current sources are prerequisites. E7 adds only report/query/serializer adapters, no alternate arithmetic or new snapshot store. |
| Used/upcoming/aging/overrides | E5 5.10-A/B/C, 5.13/15/16/18/26/27/29/30 and E6 6.5/9/11/13/15/17/18/source integrations | Actual current request/cycle/waiting/evidence/correction facts and lifecycle histories are required. Report reads never finalize, restore or resubmit a request. |
| Manager navigation/preferences | Existing E1 shell/session and E2 tools; E5 read preference owner; E6 current attention composition | Reuse existing account/org preference branch and actual UI shell. 7.4 adds only overview filters; 7.6 does not recreate escalation, deficits, business tools or action badges. |
| Shared audit sources | E1 identity/access/audit; E2 actual People writes; E4 Content actions; E3 shared notification/Leave worker; E5/E6 actual writers | Access operator/event infrastructure and services/content-service audit migration exist. Exact app/user-scoped audit read APIs are not inferred. People and notification runtime remain planned; 7.21–24 count their real bounded read/consumer delta. |
| Private sensitive links | E4 4.4/4.7/4.13 plus E1 Content private-read foundations | Existing Content is credited; exact Leave ownership/fixed-byte/association/private-read adoption remains E4 coordinated with Expense. E7 creates no signed private download or second content pipeline. |
| Schemas/clients/security/release | Actual source OpenAPI exporters; platform/api-client, builder neutral/native fixtures; owning migrations/qualification | Export/check/generated-client and runtime-role/previous-version proof are actual consuming deliverables. KDG initial-ledger evidence is not proof of E7 business scope or report performance. |

## Duplicate-work disposition

| Existing work | E7 residual scope |
| --- | --- |
| E3 current/own balance and history | Multi-employee report query/aggregate/CSV only; own calculation explanation remains E3. |
| E5 personal history/calendar and advisory team availability | Wider organization overview with current allowed filters and role projection only; no second own calendar, preference service or approval queue. |
| E5 reminders/escalation/wait clocks | Read current aging facts, not another timer, scheduling worker or reassignment engine. |
| E5/E6 manager attention and correction | Residual navigation/read context only; no new deficit/coverage/follow-up workflow or report-based action authority. |
| Every earlier writer's audit | Read/search permitted actual evidence, not a duplicate audit event at render or a retrospective full-payload logger. |
| Shared owner history | Explicit HTTP read contracts and small Leave projection adapters; no source database joins, universal credential or central synchronous audit-write service. |
| E8 imports/pilot/operational runbooks | E7 supplies report/audit/native/performance evidence; no import tool, client-email flow, UAT signoff, provider change, recovery rehearsal or pilot activation is moved here. |

## Five impact decisions for every candidate

| Candidate class | Scaffold | Shared UI | Agent context | Documentation | ADR |
| --- | --- | --- | --- | --- | --- |
| 7.1/4/7/9/11/13/15/17 | Reuse/prove neutral scoped query/cursor/preferences/client fixtures; keep definitions in Leave | No generic report engine | Existing instructions suffice; generated commands updated when actual package exists | Owning query/schema, exact source/test mapping and generated-client maintenance | Existing privacy/source rules plus proposed 0169 temporal choices |
| 7.2/3/5/6/8/10/12/14/16/18/20/27 | Same-item owner template/managed-copy parity if neutral code changes | Prove/promote existing collection/report/filter/CSV feedback primitives; domain rendering remains Leave | Existing guidance suffices | Approved UX implementation and browser/accessibility evidence | No new screen or saving policy |
| 7.19 CSV | Promote only proven neutral safe serializer/evidence/stream fixtures with consumer tests | Existing export control | Record actual scoped export command/runtime checks | File/query/audit contract, safe errors and exact tests | Existing export/audit/privacy decisions |
| 7.21–26 audit | Source-owned read projections/HTTP adapters and immutable fixture reuse; no audit writer/warehouse | Existing table/detail controls | Existing owner-boundary rules suffice | Each source contract/OpenAPI/client and source availability/retention evidence | Existing P-0023/0025/0056 and accepted read policy |
| 7.28–31 proof | Neutral fixtures promoted only with actual evidence; domain journeys stay local | Actual mobile/keyboard/browser evidence | Actual package verification commands recorded | Traceable red/green, native, release and performance results/limits | No readiness closed by documentation |

## Validation and remaining gates

The planning audit checks 31 story headings, 124 unique ACs, exact graph/size sets,
acyclic earlier-only prerequisites, all six report families, four actual shared audit
source adapters, coverage rows, selected exact source fingerprints and local links.
It also compares earlier E5/E6 story bodies before/after this turn and reruns the
existing E5 source-criterion/graph audit. These are documentation checks only.

Each item still needs actual source schema/endpoint/credential/field contracts, exact
fixtures/test nodes, acceptance failure then focused TDD results, generated artifacts,
real native permission/compatibility proof and proposed workload/target validation during
authorized delivery. Use E5's actual-versus-planned artifact command strategy; do not
pretend future Leave scripts exist, and do not run root dev/build as verification.

After the single E7 review, reconcile accepted choices once. E8 decomposition and
whole-product atomic FR/UX/NFR coverage plus BMAD readiness remain before implementation.
Step 04 has not been loaded. No code, DB migration, live role/grant/provider/recipient,
commit or deployment was changed. The first implementation slice stays sign in → select
organization → create/resume draft → autosave → close → reopen.

### Recorded planning checks — 2026-10-25

- `python3 /tmp/check-leave-e7-planning.py` — PASS: 31 unique ordered candidates,
  124 AC IDs, exact 31-row size/dependency set, 52 edges/9 acyclic layers, 48 source
  clusters, six report pairs, four audit sources, nine unchanged authority-section
  fingerprints, eighteen local links/anchors and unchanged prior E1–E6 story bodies.
  Proposed ADR/workflow status and new-file whitespace checks also pass.
- `python3 /tmp/leave-e5-final-check.py` — PASS: existing 88-node E5 graph/size
  allocation, all 230 original criterion hashes and twelve external owner clusters.
- `git diff --check -- _bmad-output/planning-artifacts/epics.md apps/leave/docs/planning-handoff-e3.md apps/leave/docs/implementation-plan.md apps/leave/docs/architecture/ARCHITECTURE-SPINE.md apps/leave/docs/architecture/decisions/README.md platform/docs/architecture/contracts/e1-security-audit-ownership.md`
  — PASS, no whitespace errors in the scoped tracked diff.

Temporary scripts check documentation, not Leave business behavior. No API/browser/native
DB/performance/migration/release test was run and no runtime-readiness claim follows.

### E7 planning closure accepted — 2026-10-25

The user replied “happy, nezxt”, accepting the complete E7 package and directing
progress to E8. All 31 candidate boundaries and the two ADR-0169 choices are now
the accepted E7 planning baseline. Earlier proposed/awaiting-review wording is
historical. Features/spine/UX/contract/index are synchronized. This closes E7 story
planning only: E8, global coverage and executable readiness/release evidence remain
open. Do not reopen E5 or start implementation.

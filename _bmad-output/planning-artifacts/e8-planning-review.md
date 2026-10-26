# E8 planning — one review package

**Prepared:** 2026-10-25. **Status:** E8 planning closed by user approval; both ADR-0170 choices accepted.
E7 and both ADR-0169 choices are accepted and its story planning is closed. E5 stays
closed; accepted E6 choices remain binding. E8 is the last epic in the approved list.
This package is not a global coverage/readiness PASS or permission to operate a live target.

## Accepted import choices

[Accepted ADR-0170](../../apps/leave/docs/architecture/decisions/0170-imported-pending-work-and-resumable-employee-units.md)
collects the two material choices left by the existing migration runbook:

1. **Imported pending requests start a fresh verified Leave approval cycle at activation.**
   The client-approved report discloses the new route, employee response and waiting
   consequences. Source decisions remain historical evidence. Completed historical records
   do not replay old notices; only current pending actions notify after approved activation.
2. **Apply atomically per employee and resume explicitly.** All one employee's Leave
   openings/requests/effects commit together. Another employee's failure does not undo
   successful units. No selected imported work becomes ordinarily visible/actionable until
   the exact approved selection reconciles and its activation is authorized.

Existing recovery, privacy, browser and alert policies are reused; no new operational
business choice is required. Actual client data, source meaning, authorized contacts,
credentials/provider capability and target-specific evidence are future delivery inputs,
not questions to answer while approving generic planning. No email was sent and no
import, backup, restore, migration, role/grant/provider change or deployment was run.

## Scope and navigation

- [30 proposed stories and 120 specific ACs](epics.md#e8--reconcile-pilot-data-and-operate-leave-recoverably)
- [Owning import/cutover/qualification contract](../../apps/leave/docs/architecture/contracts/e8-import-cutover-and-qualification.md)
- [Source allocation and verification limits](e8-coverage-audit.md)
- [Existing consultant migration runbook](../../apps/leave/docs/operations/migration-runbook.md)

| Group | Candidates | Outcome |
| --- | --- | --- |
| 1/5 Import and cutover | 8.1–14 | Exact source/mapping/convention preview and email approval, bounded owner adapters, per-employee apply/status/reconciliation, cutover and held-notice activation proof |
| 2/5 Integrated safeguards | 8.15–20 | Actual threat/privacy/retention/accessibility/browser and worker/monitoring/alert qualification over completed first owners |
| 3/5 Recovery and release | 8.21–25 | Verified recoverable DB/private bytes/dependencies, timed restore, notification replay reconciliation, controlled migration recovery and actual workload measurements |
| 4/5 UAT and handover | 8.26–28 | Representative human UAT, verified support/recovery guide and exact-release go/no-go dossier |
| 5/5 Pilot activation | 8.29–30 | Existing scoped Access/Directory/release activation and actual-target health/reconciliation/handover, only during later authorized delivery |

## Dependency and single-agent size register

Each row is one bounded candidate **conditional on real predecessor delivery**. A missing
first-owner service/tool is not silently included in a small integration item. Each row
counts focused actual-role/contract/rollback/failure/client evidence and its five impacts.
Qualitative fit is a planning assessment, not a measured number of hours or runtime PASS.

| Item | Internal predecessors | Actual bounded delta and assessment |
| --- | --- | --- |
| 8.1 | None | Offline CLI/input-schema and manifest validation with source-file hashes, canonical identifiers and safe row diagnostics; no server import/state mutation. **Retain one candidate** with actual predecessors complete. |
| 8.2 | 8.1 | Read-only cross-owner preflight/mapping references through existing authorized Identity/Access/People/Leave contracts; no duplicate employee master. **Retain one candidate** with actual predecessors complete. |
| 8.3 | 8.1, 8.2 | Pure import normalization/reconciliation adapter over actual E3 replay and source portions, with before-request versus net-source conventions and supported history boundary. **Retain one candidate** with actual predecessors complete. |
| 8.4 | 8.3 | Consultant report/evidence artifact plus minimal immutable server manifest registration for later protected apply; no email sending, client login or confirmation screen. **Retain one candidate** with actual predecessors complete. |
| 8.5 | 8.3, 8.4 | E3-owned internal opening/reconciliation adapter, staged-source economic-read eligibility and scoped source-key/effect constraints, only inside the actual employee import envelope. **Retain one candidate** with actual predecessors complete. |
| 8.6 | 8.2, 8.4, 8.5 | E5-owned internal settled-request import branch, staged-source read eligibility and source mapping, including historical/approved/closed source records and reconciled accounting links; no ordinary approval bypass endpoint. **Retain one candidate** with actual predecessors complete. |
| 8.7 | 8.2, 8.4, 8.5, 8.6 | E5-owned internal pending-request import adapter over actual request/reservation/route/response interfaces, with explicit approved mapping and activation-held current notices. **Retain one candidate** with actual predecessors complete. |
| 8.8 | 8.2, 8.4 | Bounded consultant source-byte ingest/target adapter through actual E4/Content APIs and existing pending-association lifecycle; no provider direct write or new content pipeline. **Retain one candidate** with actual predecessors complete. |
| 8.9 | 8.4, 8.5, 8.6, 8.7, 8.8 | One actual app-owned import command/CLI composition with minimal unit manifest/outcomes, existing guards and internal 8.5–7 adapters; not HTTP calls to separate local commits. **Retain one candidate** with actual predecessors complete. |
| 8.10 | 8.9 | CLI status/resume plus existing owner receipt extension for batch/employee targets and source uniqueness; no workflow engine or autonomous retry daemon. **Retain one candidate** with actual predecessors complete. |
| 8.11 | 8.10 | Read-only actual-state reconciliation report over imported maps, E3 balances and E5/E6/E7 records; no mutation to make expectations pass. **Retain one candidate** with actual predecessors complete. |
| 8.12 | 8.11 | Consultant cutover/delta artifact and exact revised-batch comparison through existing preview/approval flow; no client application page. **Retain one candidate** with actual predecessors complete. |
| 8.13 | 8.7, 8.10, 8.12 | Narrow import intent/activation-generation integration with existing outbox/clock/source owners; no second transport or universal notification pause. **Retain one candidate** with actual predecessors complete. |
| 8.14 | 8.11, 8.12, 8.13 | Bounded disposable actual-API/native/Content import journey using representative source fixtures and adversarial repeats; actual adapters own their focused tests. **Retain one candidate** with actual predecessors complete. |
| 8.15 | None | Cross-epic threat-model and focused integrated native/API/HTTP abuse evidence, referencing completed owner suites rather than adding first protections late. **Retain one candidate** with actual predecessors complete. |
| 8.16 | None | Focused existing Leave retention form/Content disposal qualification and per-client review record; no new legal rule or blanket purge. **Retain one candidate** with actual predecessors complete. |
| 8.17 | None | Cross-epic representative actual-browser/accessibility matrix referencing completed feature tests, exact versions/OS and visible remediation gaps. **Retain one candidate** with actual predecessors complete. |
| 8.18 | None | Actual first-owner worker/supervisor failure/restart composition with completed claims/leases/timeouts and truthful recovery report. **Retain one candidate** with actual predecessors complete. |
| 8.19 | None | E8 composition/installation verification of actual first-owner telemetry and one approved existing operational setup; no vendor bake-off or AI repair framework. **Retain one candidate** with actual predecessors complete. |
| 8.20 | 8.18, 8.19 | Actual probe/routing/incident threshold and recovery qualification over completed owner signals; no messages sent in this planning task. **Retain one candidate** with actual predecessors complete. |
| 8.21 | None | Actual target capability/configuration/usable-point inventory and isolated backup evidence over required DB/Identity/Access/config/private-byte owners; no custom backup engine. **Retain one candidate** with actual predecessors complete. |
| 8.22 | 8.21 | Actual disposable restoration rehearsal over completed owner backup mechanisms, timed from incident declaration with cross-owner usable-point reconciliation. **Retain one candidate** with actual predecessors complete. |
| 8.23 | 8.18, 8.22 | Cross-owner restore/replay evidence over actual producer/receiver/provider dedup facts; bounded held-work procedures, no new delivery engine. **Retain one candidate** with actual predecessors complete. |
| 8.24 | None | E8 release composition over actual owner manifests/migration histories/qualified deployment tools; missing shared orchestration remains its existing first owner work. **Retain one candidate** with actual predecessors complete. |
| 8.25 | None | Representative full-app/source/import measurement on actual isolated deployment-equivalent tooling, reusing each owner’s algorithms/indices; no speculative cache/worker. **Retain one candidate** with actual predecessors complete. |
| 8.26 | 8.14, 8.15, 8.16, 8.17, 8.25 | Human UAT script/evidence over the completed E1–E7 app and representative scoped pilot-like fixtures; no repeated planning approval substituted for UAT. **Retain one candidate** with actual predecessors complete. |
| 8.27 | 8.20, 8.22, 8.23, 8.24 | Concise app-owned runbook/support/ownership package linking actually rehearsed tools, safe errors/correlation and scoped recovery; no support administration screen. **Retain one candidate** with actual predecessors complete. |
| 8.28 | 8.11, 8.12, 8.14, 8.15, 8.16, 8.17, 8.18, 8.19, 8.20, 8.21, 8.22, 8.23, 8.24, 8.25, 8.26, 8.27 | Evidence-only release gate composition referencing actual source tests/contract/adoption/migration/import/UAT/recovery artifacts; no duplicate universal lifecycle. **Retain one candidate** with actual predecessors complete. |
| 8.29 | 8.13, 8.28 | Narrow actual rollout action using existing release/Access enable/grant/Directory contracts and approved import activation generation; no alternate admission system. **Retain one candidate** with actual predecessors complete. |
| 8.30 | 8.29 | Bounded actual-target smoke/monitoring/reconciliation and handover evidence over the approved release, without inventing automatic production mutation. **Retain one candidate** with actual predecessors complete. |

The largest integration, 8.9, composes completed **internal** 8.5/6/7 adapters in one
Leave employee transaction; it does not implement their math, request models or Content
preparation. Source eligibility is already counted in the E3/read/pending adapters before
staged data can exist. 8.10 owns retry/status rather than hiding it in a second batch engine.
8.21 is capability/usable-point evidence; 8.22 is the actual timed restore; 8.23 separately
handles cross-owner external delivery uncertainty. Platform release orchestration remains
with its existing first owner: 8.24 verifies actual Leave composition, not a new platform.

First-use/graph reconciliation:

- Templates/source conventions and mapping preflight precede preview. Exact approved
  report/manifest precedes all actual apply; no data writes to manufacture a preview.
- 8.5/6/7 introduce only first-used typed source/effect/request extensions and current
  economic/read/action eligibility. 8.9 is the first complete public apply envelope.
- Actual scoped migration operator views support post-apply reconciliation while staged
  records remain outside ordinary end-user visibility. No new application status is added.
- 8.13 handles only the selected import's actual activation/notice intent. It is delivered
  before import qualification and actual pilot activation; no historic notice replay or
  global notification pause is hidden in a late test.
- Backup capability precedes timed restore, which precedes restored-delivery reconciliation.
  Native/security/worker/telemetry protections remain obligations of earlier first owners.
- 8.28's actual no-go evidence precedes 8.29 activation; 8.30 records verified outcome
  afterward. Planning approval cannot substitute for live release or client signoff.

## Concrete external owners and delivered credit

| E8 consumers | Existing actual owner items | Delivered evidence credited / remaining prerequisite |
| --- | --- | --- |
| All tool/API/native paths | E1 ENV/P1/SERVICE/WRITE/REF/VERIFY and exact actual Leave api/web/roles | Neutral bootstrap/Auth/client/native helpers and platform deployment tools exist in bounded scopes. No Leave API/web implementation or public complete generator is inferred. |
| Identity/source mapping | E1 ID-A/B/ACCESS-A/B/PEOPLE and E2 2.1–23/26 | Access current registry/grant/admission implementation is credited. Actual People HTTP reads/history/management and Leave source setup remain planned owner deliverables. Explicit source mappings and operator grants remain necessary. |
| Import accounting/reconciliation | E3 3.7–18/3.29 and actual event/portion/evidence interfaces; E5 5.8-A | Actual E3 replay/provenance and E5 commitments are prerequisites. 8.3/5 add only source-convention normalization and reviewed import effects/eligibility. |
| Recorded/pending requests | E5 5.10-A/B/C, 5.11/12/18/19/20, rule/route/response owners and E6 corrections | Completed normal workflow/receipt/history/finalization protections are reused. 8.6/7 are narrow authenticated import adapters, not unrestricted status setters or forged human decisions. |
| Documents | E4 actual fixed-byte/association/cleanup/private-read/retention items, especially 4.4/4.7/4.13 | services/content-service exists. Exact Leave ownership/read/association adoption and Expense-coordinated shared work remain first-owner prerequisites; 8.8 is only the import consumer delta. |
| Notice/activation/recovery | E3 3.22/23/24/25-A/B/26/27 and E5 due/claim/clock/source owners | Shared notification runtime is planned. Use actual outbox/receiver/provider/claim fencing and relevance contracts, not an invented import transport. |
| Reports/audit/target comparisons | Accepted E7 7.1–27 plus E6 history/deficit/source consumers | Actual E7 report/scope/evidence queries remain delivery work. Import reconciles with actual results, not mocked preview numbers or a second report engine. |
| Security/browser/performance | All earlier first-consumer APIs/native/browser suites and accepted E7 7.28–31 | E8 extends representative cross-epic coverage/UAT and measures the actual target; it cannot postpone or claim missing earlier authorization as already proven. |
| Worker/monitoring/release | E1 release/observability foundations, actual E3/E5 worker owners and platform/deployment | Existing deployment manifests/qualified helpers are reused. The current README registers other apps and explicitly does not deploy Leave. No actual Leave monitoring/backup/target readiness is inferred. |
| Pilot Access/Directory | E1 DISCOVERY/LAUNCHER/ACCESS, E2 enablement/membership/default-role owners | Existing owner mechanics are reused with actual scoped pilot inputs and compatible release/adoption; importing employment or receiving client email does not grant application admission. |

## Duplicate-work and scope disposition

No second ledger/employee master/content pipeline/notification transport/workflow engine,
custom backup engine, monitoring vendor bake-off, AI repair workflow or general self-service
migration screen. E8 uses actual approved E1–E7 contracts and app-owned operations.
Correct bad data via reviewed source/import plans or existing E6/adjustment commands;
never edit old events, auto-delete successful units or manufacture source history.

The accepted first implementation slice stays sign in → select organization → create/
resume draft → autosave → close → reopen. E8 import/qualification/activation comes later.
Naming, independent teams, external calendar/payroll/HRIS/Graph sync, Portuguese translation
delivery and malware-scanner hardening remain deferred. Retention/default review follows
existing accepted configuration scope; no jurisdiction-specific legal answer is invented.

## Five impacts for every candidate

| Candidate class | Scaffold | Shared UI | Agent context | Documentation | ADR |
| --- | --- | --- | --- | --- | --- |
| 8.1–4 preview/evidence | Reuse versioned input/canonical identity/safe error helpers; domain templates remain Leave | No client approval/import UI | Existing rules suffice; actual CLI guidance when implemented | Versioned template/manifest/report/approval provenance and source test map | Proposed 0170 only; accepted email process unchanged |
| 8.5–13 actual import | Same-item neutral owned-write/receipt/HTTP/association/native fixture promotion and generated preservation checks if applicable | Existing scoped operator/support controls only | Generated commands updated through owner templates | Actual schema/API/current eligibility/canonical input/retry/rollout and client-approved batch evidence | Proposed 0170 pending/atomic-unit semantics; existing source/safety rules |
| 8.14–20/25–26 qualification | Reuse first-owner fixtures; promote only proven neutral failure/browser/native scenarios | Real accessibility/mobile evidence; no new monitoring screen | Actual commands/limits recorded | Requirement/AC/test/red-green/result/target evidence and role/UAT gaps | Existing security/privacy/browser/alert targets; no new generic gate |
| 8.21–24/27 recovery/release | Actual owner backup/native/deployment hooks; no custom engine | No new business recovery screen | Existing least-privilege/target rules suffice | Exact verified restore/replay/release/support procedures and schedules/owners | P-0020/0027/0028; L-0119/0120 unchanged |
| 8.28–30 pilot | Reuse actual existing release/Access/Directory adoption tools | Existing admission/launcher only | Existing authorization rules suffice | Exact dossier/signoffs/target/release/import/activation/outcome and recovery references | Planning approval does not authorize live execution |

## Evidence and remaining planning

This package has 30 candidates, 120 specific ACs and source-obligation allocation in the
linked audit. Document checks compare IDs, complete dependency/size rows, earlier-only
acyclic order, source hashes, links and unchanged pre-E8 story bodies. They are not
acceptance/native/runtime/performance/provider or pilot evidence. E7 acceptance is recorded
separately and its source fingerprint refresh reflects the approved source adoption.

Actual delivery must bind exact fixtures/commands/target credentials and observe relevant
acceptance failure before implementation, then focused TDD and affected native/API/HTTP/
browser/compatibility tests. Record real results/limitations rather than invented test
filenames or root dev/build as repository proof. Concrete operational target actions
require their actual reviewed authorization; no live resource was inspected or changed.

After this single E8 review, the next work is whole-product source/atomic FR/UX/NFR
coverage and dependency/contract/readiness reconciliation under BMAD. No repeat E5 review
is required. E8 preparation is not step-03 completion: global extraction/coverage and
applicable planning acceptance remain unfinished. Do not load step 04 or claim a sprint
readiness PASS prematurely; do not implement Leave. No workflow completion flags or
implementation tracker checkboxes are set by planning.

### Recorded planning checks — 2026-10-25

- `python3 /tmp/check-leave-e8-planning.py` — PASS: 30 unique ordered E8 candidates,
  120 AC IDs, exact 30-row size/dependency set, 62 edges/17 acyclic layers, 48 source
  clusters, ten E8 and nine accepted E7 authority hashes, twenty local file/heading
  links and unchanged pre-E8 story bodies. All 31 E7 approval markers/accepted
  ADR-0169 and proposed ADR-0170/workflow status checks pass; new-file whitespace clean.
- `python3 /tmp/leave-e5-final-check.py` — PASS: existing E5 88-node graph/size
  allocation, 230 original source-criterion hashes and twelve external owner clusters.
- `git diff --check -- _bmad-output/planning-artifacts/epics.md apps/leave/docs _bmad-output/planning-artifacts/ux-designs/ux-leave-2026-09-15/EXPERIENCE.md`
  — PASS, no whitespace errors in the scoped tracked diff.

These temporary scripts audit documentation only. No application, import, native database,
provider, restore, monitoring, migration, release, UAT or pilot qualification was executed.

### E8 planning closure accepted — 2026-10-25

The user explicitly approved E8 and both import choices and directed next. All 30
boundaries/120 ACs and ADR-0170 are the accepted E8 planning baseline. Earlier
proposal/review language is historical. Product/spine/UX/runbook/contract/index adopt
the decision. Next is whole-product coverage/dependency/size/contract validation;
this closes no executable runtime/release or Phase 1 readiness gate.

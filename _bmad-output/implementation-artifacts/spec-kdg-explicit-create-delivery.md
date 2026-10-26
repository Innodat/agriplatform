---
title: 'Explicit saved-create delivery and receipt recovery'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: '54f6e9c9d97c4c0542076951a3c535872b6b943f'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/LOCAL_CREATE_SAVE_EVIDENCE.md'
  - '{project-root}/apps/kdg-capture/docs/EDIT_DELIVERY_EVIDENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Completed local captures have frozen create commands but cannot consume their original server receipts or explicitly deliver/reconcile them.

**Approach:** One unmounted explicit consumer performs original-operation recovery, at most one exact POST, durable receipt consumption and authorized current readback. Reuse existing transports, Auth and storage primitives.

## Boundaries & Constraints

**Always:** Original account/org/capture/operation, command version, bytes, questionnaire, device time and eligibility reference remain immutable. Current own-read gates retained intent/recovery; POST independently checks current authority server-side. Honor known local creation denial until explicit newer verification; original setup expiry or absence from today's child list alone must not veto delayed delivery. Prior eligibility permits ordinary child inactivity under existing server checks. Receipt consumption does not fabricate server content/audit. Readback alone never acknowledges an uncertain operation. Preserve newer local work and independently usable records.

**Never:** UI/editor/Leave, automatic sender/queue/claim/scheduling/browser/service-worker/default-startup activation, unfinished typing, real accounts/Auth/Access, native PostgreSQL/Docker work, provisioning/migration execution, deployment/production/pilot/cleanup, installs/dependency changes or fingerprints/HMAC. Preserve TypeScript7.0.2, concurrent work and historical evidence. Never read/run/copy/hash the preexisting untracked migration fixture; selected-source capsules only. No push.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure handling |
|---|---|---|---|
| First delivery | Actual saved create, unresolved GET | One exact POST, durable matching receipt, current GET/readback | No DB transaction held during HTTP |
| Lost outcome | Committed POST response lost or receipt write uncertain | Next explicit invocation recovers original receipt without repeat POST | Keep original IDs/bytes |
| Authority | Create expired/denied, read denial, assignment loss, inactive child | Read-only receipt recovery survives creation loss; server checks every new POST; scoped rejection preserves read when verified | No inferred grant or new reference |
| Exact reconciliation | Wrong receipt/target/version; read revision equal/newer than original receipt | Reject mismatches; equal revision requires saved answers/date; newer detail may contain later edits, retaining original receipt revision | No substitution or false Synced |
| Partial completion | Receipt saved but readback unavailable, quota/abort/completion failure, history-only baseline | No false current-content acknowledgement; original receipt survives; history existence alone remains unacknowledged | Retry under original identity |
| Rejection/version | Safe known rejection, transient outage, unsupported durable version | Retain attention versus retryable pending; stop this invocation after rejection, no internal retry loop; unsupported retained/blocked | Independent records continue |
| Execution/concurrency | Competing calls, account/org change, slow storage/headers/body | One Auth lease and total30sec maximum/default including publication; HTTP phases at most10sec/remaining; cancellation aborts queued IDB | No dependent work after expiry; lease released |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/web/src/history-store.ts`: LocalCreateIntent already freezes pending/serialized/content. Add scoped point lookup, versioned mutable delivery metadata outside immutable intent, idempotent receipt consumption and receipt-bound reconciliation via existing importBaseline/reconcileBaseline/importCurrentDetail. Reuse readAccess/editOperation/transaction/lock and supportedCreate; retain unknown metadata. Save retry must still recover original result after delivery. No new local DB version unless required by an actual store/index change.
- `web/src/create.ts`, recovery.ts, read.ts: existing strict generated transports. Create recovery request intentionally has no capture selector; store/consumer must bind returned target to saved capture. Backend creates at revision1; current detail may already be revision2/3. Match immutable owner/child/version/device facts and original definition; compare answers/date only at receipt revision. Keep local_capture as original evidence and preserve overlays/actions. Only actual detail supplies server attribution/baseline; mark the exact create synchronized after receipt-bound readback.
- `web/src/edit-delivery.ts`, edit-delivery-entry.ts: reuse bounded single-invocation pattern, no generic engine. Add create-delivery.ts/create-delivery-entry.ts with closed result unions. Recovery precedes POST; only unresolved can send. Recovered receipt remains consumable after creation loss. Do not reuse initial-Save createAuthority: its original expiry/current-child requirements are inappropriate for delayed sync.
- POST access_denied: latch creation denial before bounded current own-read probe; use existing getCurrentContext (entry.ts), since an uncreated capture can legitimately be404. Do not fabricate observation renewal. Confirmed read denial locks; probe unavailable conservatively locks within execution fence. Assignment/eligibility/version/validation rejection affects selected action, not all read/create rights. Distinguish operation_busy/outages/auth renewal. Explicit later invocation is not an automatic retry; future automatic consumers must skip attention. Unsupported/contradictory work cannot send.
- `web/tests/edit-delivery-proof.mjs`, edit-delivery-http-proof.mjs, persistence-http-fixture.py and local-create-save-proof.mjs: reusable selected-source real Chromium/actual synthetic HTTP patterns. Root owns final HTTP integration/docs/broad qualification. Agent owns store, consumer, focused proof/types and necessary selected-source capsule additions; do not change historical fixture behavior merely to dismiss a failure.

## Tasks & Acceptance

**Execution:**
- [x] `web/tests/create-delivery-proof.mjs` and types — observe behavioral RED, then matrix cases with real IndexedDB and controlled transport/deadlines.
- [x] `web/src/history-store.ts` — narrow lookup/receipt/attention/creation-denial/readback persistence with original identities.
- [x] `web/src/create-delivery.ts`, create-delivery-entry.ts — explicit Auth consumer under one total execution budget.
- [x] `web/tests/create-delivery-http-proof.mjs` — root: actual synthetic API→Auth→IDB Save/delivery/recovery/readback proof.
- [x] `apps/kdg-capture/docs/`, web README — root: source-bound evidence, append contracts/prepend handoff, five impact decisions.

**Acceptance Criteria:**
- Given each matrix row, when registered proofs execute, then expected behavior passes with command/source custody.
- Given real local Save and synthetic API, when creation commits but response is lost, then next explicit delivery recovers one original create receipt and current baseline without another POST.
- Given existing history/edit/setup consumers, when affected regression runs, then compatibility and scaffold parity remain intact.

## Implementation Notes

Technical consumer subset of approved Story1.6, not full story/queue readiness; story_key unset. No intent gaps or irreversible effects. Standing authorization continues across routine checkpoints. Root preserves baseline at `platform/deployment/.local/kdg-explicit-create-delivery-20261026/baseline.json` and owns review/qualification/scoped commit.

Impacts: domain orchestration stays KDG; reuse builder-owned IDB/Auth primitives and promote only demonstrated neutral fixes. Shared UI/context unchanged; docs updated; existing ADRs suffice. Native issuance/browser-update/device qualification remain existing release gates, not prerequisites to synthetic consumer work.

## Spec Change Log

## Review Triage Log


| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 optional durable metadata presence | medium / patch | Falsy delivery/receipt values bypassed structural validation and could reach sending. Check property presence and reject malformed envelopes without deleting them. |
| B2 failed creation-denial persistence | medium / patch | denyCreate could fail opening/reading IDB before installing its process latch; the consumer ignored failure. Latch verified scoped denial before fallible storage and retain original-observation freshness floors; surface failed persistence honestly. |
| B3 ignored attention retention result | medium / patch | Ignored failed attention transaction left record Pending while reporting only business rejection. Return safe retention failure and preserve original action. |
| B4 receipt plus attention | low / patch | attentionCreate could add current rejection metadata after a competing receipt/readback committed. Make receipt-complete attention a no-op and reject contradictory durable envelope combinations. |
| B5 proxy privacy header masking | low / patch | New HTTP proxy synthesized private,no-store instead of forwarding actual API header. Preserve actual header so API regressions are detectable. Root owns proof change. |
| B6 actual HTTP duplicate invocation | low / patch | Controlled transport concurrency proved client bytes, not actual handler deduplication. Add two explicit calls forced through unresolved recovery, verifying one persisted create; fixture remains non-native. Root owns case. |
| B7 Auth entry lifecycle coverage | low / patch | Direct coordinator fences do not exercise new wrapper lease through SDK account/logout/disposal changes. Add focused entry boundary tests and release/reuse evidence. |
| B8 deadline side effects | low / patch | Timeout kind alone did not establish phase budget/late effect suppression. Add controlled time/phase budget and late release assertions without fragile host-load thresholds. |
| B9 independent action isolation | low / patch | Add same-partition rejected create followed by successful different create; selected attention remains. Root owns actual HTTP case. |
| B10 retained receipt fallback | low / patch | Distinct unresolved-recovery plus durable receipt branch was uncovered. Add read-only recovery with creation denied, no POST and exact current readback requirement. |
| E1 empty-chunk denial probe deadline | medium / patch | Existing getCurrentContext body loop lacks monotonic checks; new denial probe exposes immediate empty-chunk starvation that prevents total timer settlement. Reuse existing bounded stream pattern in this KDG-owned adapter, no generic request engine. |
| E2 attention retention failure | medium / patch | Same ignored-result root cause as B3; failed IDB transaction left Pending. |
| V1 final readback denial coverage | medium / patch | Filed verified gap: existing403 tests stopped at recovery. Add committed receipt→detail403, inaccessible protected history and durable original receipt/intent after reopen. |

## Verification

Approved retained Node26.11.1/TS7.0.2/modules/Chromium/Python paths are documented in owner evidence; no installs. Unique selected-source proofs under `platform/deployment/.local/kdg-explicit-create-delivery-20261026/`. Root prior15-job runner: `platform/deployment/.local/kdg-local-create-save-20261026/root-verify/qualified.json`. Reuse342 backend tests only if85 effective source hashes remain unchanged. No actual native permission/rollback claim.

Initial root qualification:17 source-bound commands PASS;116 focused checks and32 integrated HTTP groups. All affected regression/parity passes. Source-bound evidence and traceability reside in owner machine record.

Review completion: all13 findings addressed through the patch route; no deferrals. Final18 source-bound commands pass:219 focused checks,40 actual synthetic HTTP groups,127 direct entry consumers, existing Auth/storage/setup/edit suites and five scaffold parities. All85 unchanged backend sources reconfirmed before reusing342 backend tests. Requirement-to-test traceability and exact results are in `apps/kdg-capture/docs/evidence/create-delivery-20261026.json`.

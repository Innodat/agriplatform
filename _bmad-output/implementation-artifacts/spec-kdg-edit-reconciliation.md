---
title: 'KDG ordered local edit reconciliation'
type: 'feature'
created: '2026-10-26'
status: 'done'
baseline_commit: '7597d7cb37460f546157b0bd7b77c978892e5be7'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '/home/ck/repos/innodat/agriplatform/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/AGENTS.md'
  - '/home/ck/repos/innodat/agriplatform/apps/kdg-capture/docs/LOCAL_EDIT_SAVE_EVIDENCE.md'
---

<frozen-after-approval reason="continued KDG implementation authorized without routine internal approval stops">

## Intent

Saved server-backed own edits now exist, but cannot yet freeze ordered commands or
consume committed outcomes. Implement inert local command preparation and receipt/
conflict/readback reconciliation so original action identities survive retries and
late acknowledgements preserve newer local work. This is Story2.2 storage behavior,
not activation of a sender or completion of the whole story.

## Boundaries & Constraints

Prepare only supported Pending actions under valid current scoped read/edit evidence.
Atomically freeze the complete exact PUT command before returning it. First actions
use their reviewed revision; successors require their exact predecessor's committed
receipt, including unchanged outcomes. Never substitute the latest downloaded revision.
Repeated preparation returns identical bytes/identity across tabs/reopen. Unknown
outcomes remain unresolved; nothing creates replacement IDs or assumes a send occurred.

Receipt/conflict consumers accept only exact supported adapter contracts, pinned to
the prepared action/account/org/target. Receipts acknowledge only that sequence and
cannot regress or contradict retained evidence. Preserve immutable intent/snapshot/base;
store versioned delivery metadata separately. Use current own-read for outcome/readback
consumption; it must not renew edit authority or enable new preparation after edit denial.
No network wait occurs inside an IDB transaction. Preserve existing expiry, clock,
namespace/generation/session fences and completion-boundary uncertainty semantics.

Readback alone never acknowledges a write. Authoritative detail plus its already
matched receipt may retire only the corresponding latest overlay and confirm status.
Never synthesize server actor/timestamps from local changes. Preserve newer overlays,
reviewed bases and attention proposals. Normal new saves after acknowledged readback
must work; unresolved descendants may continue their own acknowledged predecessor
chain without treating that own progress as an unrelated remote edit. Unrelated
remote revisions and stale local forms still require attention, never automatic rebase.
Conflict retains attempted frozen command, reviewed proposal/base and safe current
revision; descendants stay blocked, preserved and readable, with no resolution action.

Synthetic local/CI only. No sender/claim/scheduling/queue activation, UI/editor/Leave,
pending-create producer/setup, service-worker/browser/default-startup activation,
real accounts/Auth/Access, PostgreSQL/native-driver/Docker qualification, provisioning/
migrations, deployment/production/pilot or cleanup. Preserve concurrent changes,
historical evidence/resources and dependencies including TypeScript7.0.2.
Fingerprints/HMAC deferred. Never read/run/copy migrations/tests/schema_fixture.py.

## I/O & Edge-Case Matrix

| Scenario | Required behavior |
|---|---|
| First action, successor, unchanged receipt | Freeze reviewed command; successor waits then uses exact parent result revision |
| Two tabs, repeat preparation, reopen, unknown outcome | Same frozen command/ID; no guessed receipt or fabricated send claim |
| Valid/duplicate/late receipt with newer local Save | Acknowledge only original sequence; preserve newer overlay/action; duplicate is harmless |
| Foreign/malformed/contradictory outcome or unsupported intent version | Refuse safely without destructive changes; retain evidence and block unsafe descendants |
| Receipt then readback / readback without receipt | Only paired receipt permits confirmation; original provenance comes from detail, not receipt |
| Own predecessor progress versus unrelated remote change | Continue own ordered chain, including a third Save after parent readback; unrelated revision remains conflict |
| Conflict then descendant preparation/readback | Preserve attempted command/proposal/base/current revision, retain descendants, no automatic replay/resolution |
| Denial/expiry/account change/abort/quota/late completion | No stale success or partial state; preserve original IDs/work; valid reads survive edit-only denial |

</frozen-after-approval>

## Code Map

- `web/src/history-store.ts`: extend existing v2 owner minimally; expose explicit prepare/receipt/conflict methods and optional versioned delivery metadata. Reuse transactions, read/edit authority, bounded action retrieval and importBaseline. Existing saveEdit/openEdit assume original saved base; account for acknowledged own progress without mutating unresolved bases. No generic sync engine.
- `web/src/edit.ts`, `recovery.ts` and generated edit/recovery types: existing exact command/receipt/conflict contracts; no wire change needed. Receipt revision may equal expected revision for unchanged saves. Readback is current state, not operation lookup.
- `web/src/read-validation.ts`, `edit-context.ts`: existing original-detail/observation validators. Preserve immutable facts and original definitions.
- `web/tests/local-edit-save-proof.mjs`, `history-store-proof.mjs`: real isolated IndexedDB characterization (92/61 checks). Add `edit-reconciliation-proof.mjs` and type fixture using explicit selected sources and approved retained toolchain. Never copy the entire silo.

## Tasks & Acceptance

- [x] New proof — observe missing preparation/order acceptance RED before code; characterize touched92/61 cases first and retain exact source/log hashes.
- [x] Store owner — implement frozen preparation, idempotent receipt/conflict consumption and receipt-bound baseline reconciliation; preserve version1 pending actions and all prior methods.
- [x] Focused tests — execute every matrix row in real Chromium IndexedDB, including three-action own-chain progress, stale form, cross-tab/reload, unsupported versions, malformed outcomes, rollback and independent authority.
- [x] Root — inspect diff, audit matrix, run affected checks and independent BMAD review; publish exact contracts/evidence/handoff and scoped local commit.

Given two completed saved edits, when only the first has a committed receipt, then
only its exact successor can prepare using that receipt revision. Given a late receipt
or current readback, when newer local work exists, then it remains intact; confirmation
requires the actual matched receipt and never implies current server content equals an
older acknowledged snapshot.

## Implementation Notes

No intent gap or irreversible external action. Root owns docs/spec/review/commit;
implementer must not stage/commit. Private evidence under
`platform/deployment/.local/kdg-edit-reconciliation-20261026/`, unique logs/capsules,
exact argv/cwd and source hashes. Root already activated BMAD; implement this dispatch
without starting a second lifecycle. Reuse supported generated IDB/Auth/schema owners.
Scaffold: domain ordering stays KDG, promote only a demonstrated neutral fix with its
owner/tests. UI/context: none. Docs: append contracts/prepend handoff and preserve
history. ADR: inherit accepted decisions, no accepted edits.

## Spec Change Log

## Review Triage Log

## Verification

New isolated proof plus all92 local Save and61 history checks; strict TypeScript7.0.2,
compiled Auth/client regression and five scaffold parities. Reuse unchanged backend/
wire proof only with matching hashes. No native or physical durability claims.

All three independent review layers completed before triage; no scope/intent change or additional workflow halt is required.

| Finding | Verdict / route | Evidence |
|---|---|---|
| B1 unsupported-action clock anchors | medium / patch | Missing/unsupported action returns unchecked now/tick and editOperation installs them. Validate own-read/clock on this path before accepting anchors. |
| B2 retained delivery receipt unchecked | medium / patch | prepared validates pending bytes but nested persisted receipt can carry unsupported version/target/revision and still drive readback or descendants. Reuse closed exact receipt validation before consuming retained delivery; preserve unsupported metadata. |
| B3 predecessor chain bound | low / reject | Traversal is finite, cycle-detected and contains no network wait. No measured long-chain failure was demonstrated. Adding an arbitrary chain cap or another progress index could reject legitimate saved work and adds complexity; preserve exact ancestry until evidence justifies another approach. |
| B4 retained proof prerequisites | low / patch (root docs) | Ignored approved npm/Playwright/Chromium capsules are prerequisites; publish exact argv/paths and clean-checkout limitation, without installing or changing the baseline. |
| B5 failed custody exits zero | low / patch | New launcher writes passed:false but command can exit0 on source drift. Fail process status after retaining the receipt; propagate the same proven correction to existing local Save/history proof launchers and exercise isolated custody canaries. No builder-owned browser-proof template exists to edit. |
| B6 competing first preparations absent | medium / patch | Existing cross-realm check reuses already frozen metadata. Add concurrent first preparation and competing receipt/conflict/import ordering to prove one durable supported result and preservation. |
| B7 current contract/impact docs | low / patch (root docs) | Runtime review excluded root final docs; append actual new APIs/result/traceability and all five impact decisions while retaining historical text. |
| E1 missing-action drift bypass | medium / patch | Same concrete path as B1; existing anchors must not be refreshed by an unchecked lookup. |
| VG1 equal-revision mismatching readback | medium / patch | Preverified: removing matches still passes current suite. Add independent answers/date mismatch at receipt revision from an older baseline, preserving proposal and non-Synced status. |
| R1 new ancestry await before writes | medium / patch | saveEdit and unprepared prepareEdit await ownProgress after their prior authority check, then may write without revalidation until postcommit. Revalidate immediately before affected writes; prove expiry during ancestry cannot commit a new action or attention marker. |

Final requirement mapping and evidence: `apps/kdg-capture/docs/EDIT_RECONCILIATION_EVIDENCE.md` and its machine record. All30 final jobs pass with unchanged sources;313 backend proof reused after matching77 server source hashes. Eight protected hashes and every historical hash match baseline; concurrent additive PtS lock metadata/entries are preserved and documented with existing resolutions and root/KDG TypeScript7.0.2 unchanged. Contract prefix and handoff suffix preserved. Scoped local commit only, no push.

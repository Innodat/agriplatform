---
title: 'Complete retained own-proposal resolution paths'
type: 'feature'
created: '2026-10-26'
status: 'done'
route: 'dispatch'
baseline_commit: 'cd41aea6b72593c9352e3cd67845df7e2fdce70f'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/apps/kdg-capture/AGENTS.md'
  - '{project-root}/apps/kdg-capture/docs/LOCAL_CONFLICT_RESOLUTION_EVIDENCE.md'
  - '{project-root}/apps/kdg-capture/docs/CONFLICT_RESOLUTION_EVIDENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Retained proposals cannot yet resolve confirmed pending-create edit409, active unsent work stale after server progress, or explicitly reconsider paused descendants.

**Approach:** Complete these own-proposal persistence paths using existing local choices, authorized current reads/edit contexts and conditional edit delivery. Preserve earlier decisions and original work; every reconsidered replacement is a fresh ordinary action.

## Boundaries & Constraints

**Always:** Preserve immutable creates, original definitions/owners, action content/bases/commands/receipts/predecessors and historical decisions. Use-current needs own-read, no server write or invented revision. Replacement needs applicable original and current own-edit observations and complete validated input. Local review uses actual chosen phone state and actual typed predecessor; server review uses actual authorized current state/revision. Unknown outcomes resolve before competing work. Decisions, fresh intent/overlay and dispositions commit atomically under snapshot/head/baseline/generation CAS. Reconsideration never unpauses/replays old actions or invalidates exact recovery of an earlier decision. Original reviewed expiry, account/org/generation, cancellation/deadline and safe errors remain binding. Current own-read alone recovers committed decisions after reopen, edit loss, original expiry and legitimate progress.

**Never:** UI/editor/Leave, new HTTP endpoint/service/override/merge engine, active sender/claims/queue/scheduling/browser/service-worker/startup activation, real accounts/Auth/Access, native PostgreSQL/Docker, provisioning/migrations, deployment/production/pilot/cleanup, installs/dependency changes, fingerprints/HMAC or push. Preserve concurrent work, resources, historical evidence and TS7.0.2. Never read/run/copy/hash `apps/kdg-capture/migrations/tests/schema_fixture.py`.

## I/O & Edge-Case Matrix

| Scenario | State/input | Expected behavior | Failure behavior |
|---|---|---|---|
| Confirmed v2 conflict | Actual original create/ancestor receipts, prepared v2 edit409, authorized current | Explicit adoption or fresh server-backed replacement at reviewed revision | Retain original local base/bytes; fabricate no provenance |
| Active unsent stale work | Undisposed unprepared active branch, current server progress beyond actual original predecessor/base | Explicit server-current decision; retire source/pause affected descendants; optional fresh replacement | Own receipt progress alone is not unrelated staleness; no bypass of unresolved ancestors |
| Paused proposal | Explicit selection of previously paused v1/v2 action | Re-review against permitted chosen local state offline or actual server state; adopt or save fresh ordinary replacement | Earlier decision/disposition remains truthful/recoverable; never resume old UUID |
| Unknown or competing work | Prepared uncertain create/edit, incomplete/contradictory graph, disposed active ancestry | Safely refuse competing decision and retain evidence | No inferred noncommit or automatic merge |
| Authority/freshness | Current/new versus exact committed decision, refreshed observations, denied read/edit | Original review still expires; independent permissions; recovery before new-write authority | New decision cannot borrow renewed expiry or cross scope |
| Retry/progress | Exact/changed identities, later saves/receipts/resolution, corrupted effects | Exact immutable result only with validated retained effects and lineage | No false success, lost proposals or resurrection |
| Atomic/bounded | Independent connections, quota/abort/completion ambiguity, valid99/100/101 actions | Complete atomic effect or honest unavailable; accepted decisions remain recoverable within100 bound | No partial insertion, deletion or unbounded execution |

</frozen-after-approval>

## Code Map

- `apps/kdg-capture/web/src/history-store.ts`: reuse `captureGraph`, `originalLocalBase`, `checkedPrepared`, `ownProgress`, observation fences, normalization and `editOperation`. `conflictBranch`/server effects assume v1 prepared409 and active descendants; local branch assumes off-head unprepared Needs attention. Add explicit validated classifications for newly supported states, retaining old v1 server/v2 local decision interpretation. Require actual acknowledged create/parent lineage for v2 server decisions; compare known immutable local origin without inventing missing creation audit.
- Preserve historical disposition equality. Re-review must not replace an earlier paused disposition with retired and silently break old lookup. Add a distinct recognized decision version/linkage in existing schema4 when needed, with complete exact source/selected/effect validation and strictly later bounded generation relationships. No new stores/indexes or schema upgrade; unknown formats refuse safely. Reconsidered originals remain disposed; the fresh chosen intent alone may deliver. Any unresolved ancestor/outside branch which could overwrite the choice must block or be explicitly covered by the reviewed atomic disposition, never silently bypassed.
- `web/src/conflict-resolution.ts`, `conflict-resolution-entry.ts`: reuse bounded Auth/read/edit-context coordinator; lookup committed decision under own-read before fresh write authority/HTTP. Pure local paused choices reuse local store methods without network. Privately retain original current-review own-read, as local review already does. Keep HTTP/OpenAPI/command versions unchanged; evolve TypeScript additively with strict discrimination.
- `web/tests/retained-proposal-resolution-proof.mjs`, `.types.ts`, `web/tsconfig.retained-proposal-resolution.json`: selected-source strict real-IDB ATDD/TDD; reuse existing conflict/local/pending-create fixtures and capture capsules, never whole-silo copying. Implementation child owns store/coordinator/entry/new focused proof/types/config; parent owns integration/docs/broad qualification.

## Tasks & Acceptance

- [x] `web/tests/retained-proposal-resolution-proof.mjs`, `.types.ts`, `web/tsconfig.retained-proposal-resolution.json` — observe relevant missing-behavior RED before code; cover every matrix row and old decision compatibility.
- [x] `web/src/history-store.ts`, `conflict-resolution.ts`, `conflict-resolution-entry.ts` — implement explicit classifications, atomic choices, immutable linked recovery and current-review expiry.
- [x] `web/tests/retained-proposal-resolution-http-proof.mjs` — parent: actual synthetic create/remote advance/v2 conflict/decision/delivery/recovery, stale unprepared branch, paused re-review, real403 and no duplicate PUT after response loss.
- [x] `web/tests/create-delivery-proof.mjs` — parent: characterize real20ms deadline expiring before the intended storage phase; select that phase with controlled time while retaining cancellation/no-commit outcomes.
- [x] `docs/RETAINED_PROPOSAL_RESOLUTION_EVIDENCE.md`, `docs/evidence/retained-proposal-resolution-20261026.json`, `docs/contracts.md`, `docs/next-session.md`, `web/README.md` — parent: contracts, exact source-bound evidence and impacts.

**Acceptance:** Given each retained state and existing consumers, when explicit decisions and ordinary delivery execute, then original and later decisions recover truthfully, every proposal remains retained, only fresh selected actions deliver, and all prior affected suites/scaffold parities pass. No full Story2.3/UI/release claim.

## Implementation Notes

Technical completion subset of approved Story2.3; story_key unset. No product questions or irreversible effects. Standing user authorization covers dirty-tree preservation, cohesive scope/size and routine checkpoints. Keep KDG domain behavior local; no proven neutral template defect yet. Shared UI/context/accepted ADRs unchanged; documentation updated. Reassess scaffold impact if a neutral defect is demonstrated.

Implementation reuses existing coordinator/entry signatures; their only edits are
accurate descriptive comments. Store adds optional retained/reconsideration metadata,
versions3/4 decisions, strict legacy decoding, original own-read pin, complete effect/
lineage checks and separate action/decision bounds. Registered REDs cover missing stale
review, paused v2 server review, strict old descendant interpretation, mixed linked
recovery and restored disposed overlay. Finite per-transaction linked validation checks
every member and refuses all results after any failed member. Source-bound focused687 and actual HTTP70 pass; all26 commands execute fresh after
review patches. Three demonstrated review REDs precede their minimal production fixes.

## Spec Change Log

## Review Triage Log

All three layers reported before classification. No public API or frozen-intent changes are required.

| Finding | Verdict | Route | Evidence |
|---|---|---|---|
| B1 | medium | patch | Normal A→B→C plus stale D from B, local retirement D, then confirmed-v1 ancestor resolution preserves D=retired but emits legacy1 which rejects it. Emit existing retained3 for this demonstrated mixed-history state; keep legacy decoder strict. |
| B2 | medium | patch | After a valid retained server choice pauses B/C while preserving D=retired, local reconsideration of B writes version4 with D=retired; its all-paused decoder rejects the committed row. Validate exact preserved snapshot dispositions. |
| B3 | medium | patch | Server3 checks snapshot head ID but never compares snapshot saved_edit base/changes to that retained head, unlike local effects. A contradictory historical reviewed overlay can pass; add exact linked-head check and regression. |
| B4 | low | patch | Server3 effect validation actually calls captureGraph twice. Reuse creates from the first result to delete redundant work; no new cache or production optimization without a demonstrated failure. |
| B5 | medium | patch | New version3/4 bound cases exercise100 actions and100 decisions separately. Add a combined valid retained graph with bounded measured review/recovery; do not infer a performance failure or add optimization before measurement. |
| B6 | medium | patch | Confirmed v2 tests use direct create predecessor. Add actual intermediate v2 receipt lineage, unresolved/mismatched ancestor refusal and paused review over that lineage. |
| B7 | medium | patch | New local4 paths currently have positive/reopen coverage; atomic failure/CAS cases use stale server choices. Add local4 quota, queued abort, completion ambiguity and independent-connection coverage. |
| B8 | medium | patch | New prior ID/generation, retained source and historical snapshot lack independent negative cases. Test their exact dependency failures; earlier lookup need refuse only where it depends on the corrupted later explanation, not independent valid history. |
| B9 | low | patch | New HTTP compilation/assertions precede try/finally, so compiler failure lacks normal result publication. Move compilation into the existing bounded recorded lifecycle and inject a compiler failure to qualify it. |
| B10 | low | reject | Opaque branded reviews are produced only by validated store methods; no current caller constructs metadata or relies on the invalid combinations. Runtime paused links already require exact IDs/generations; confirmed reviews carrying optional links are not actually rejected by the parser. Tightening into unions would add producer/type branches without a demonstrated consuming defect. |
| E1 | medium | patch | Independently traced the normal mixed-retirement sequence in B2; local4 writer and decoder disagree on preserved D=retired. |
| E2 | medium | patch | Independently traced B1: confirmed-v1 writer chooses legacy1 despite already-retired descendant, making exact lookup refuse its own commit. |
| E3 | medium | patch | The cited frozen recovery claim is violated by the demonstrated B2 sequence; preserve every existing disposition while using a compatible local4 decoder. |
| V1 | medium | patch | Preverified regression gap: local4 lookup requires exact prior pause decision, but no test deletes that prior record while retaining source/dispositions/replacement. Add a real-IDB missing-prior refusal case. |

## Verification

Use retained Node26.11.1/TS7.0.2/modules/Chromium/Python, no installs. New focused RED→GREEN, actual synthetic HTTP, then the24 commands in `platform/deployment/.local/kdg-local-conflict-resolution-20261026/root-verify/review-qualified.json`; legacy99-decision proof needs660sec process allowance. Parent runs broader checks after stable code, repeating only for justified changes. Reconfirm179 protected files and85 unchanged backend sources before reusing342 backend tests; contracts append/handoff prepend only. Private custody: `platform/deployment/.local/kdg-retained-proposal-resolution-20261026/`. Proof harnesses need bounded owned-resource shutdown, no real services.

First broad run passed8 jobs then reproduced preexisting create-proof late-storage
phase timing failure. Controlled30ms pre-phase delay confirms receiptPhaseReached=false
before the20ms deadline. Retain failure/probe; replace only test timing control with
phase-selected ten-second expiry and await actual late consume. All original outcomes
stay unchanged, plus explicit phase-reached assertion. Unaffected first8 proofs may be
reused only after their effective captured sources match final files; run corrected
create proof then remaining17 jobs. No production source changes for this correction.

Pre-review candidate qualification completed26 passing commands:568 focused/70 actual HTTP checks,
220 create-proof checks after its characterized timing correction, all24 prior jobs
and five scaffold parities. Eight successful unchanged-effective-source proofs reused;
remaining18 executed on current262-source map. All179 protected and85 backend hashes
reconfirmed. Every matrix row had executed coverage; subsequent review patches and final results follow below.

Final review qualification:26 fresh passing source-bound commands,687 focused and70
actual HTTP checks, five scaffold parities. All179 protected/85 reused backend source
hashes remain unchanged. Review13 addressed, one low-impact refinement rejected, none
deferred. Combined100/100 review/recovery/refusal operations meet30-second fences.
Compiler-failure evidence publication is independently qualified without starting a
fixture/browser. No schema/public-method/HTTP/command change or runtime optimization.

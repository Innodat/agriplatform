---
title: 'Story 3.1 own capture workspace and foreground synchronization'
type: 'feature'
created: '2026-10-29'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'ac5499b2bea045db59260150c554cb94ecceb0b0'
context:
  - apps/kdg-capture/AGENTS.md
  - apps/kdg-capture/docs/EXPERIENCE.md
  - apps/kdg-capture/docs/DESIGN.md
  - apps/kdg-capture/docs/contracts.md
  - apps/kdg-capture/web/README.md
  - apps/kdg-capture/docs/STORY31_OWN_API_EVIDENCE.md
  - platform/docs/development/bmad-codex-usage.md
---

<frozen-after-approval reason="user authorizes successive necessary local Story3.1 delivery and routine BMAD checkpoints">

## Intent

Ordinary `/` still shows setup status, so Story3.1 AC2/4/5 cannot exercise saved own
work through synchronization and administrator refresh. Mount the actual own capture /
My observations workspace using existing guarded storage and delivery owners, with a
real revisioned offline shell. `/admin` keeps separate current online all-read admission.

## Boundaries & Constraints

Follow existing E1/E2/Story3.1 contracts; no new business/API authority. Capture uses
explicit Save/Cancel, pinned original definitions, local date and atomic completed-save
acknowledgement. No unfinished-input persistence, autosave, fabricated server receipt,
duplicate action on uncertain retry, routine audit in own UI or administrator editing.
Question controls follow actual definitions: unanswered ratings, valid 1/false, initial
Nee, multiline details buffered only in memory and excluded when false. Keep values on
failed Save; stable IDs/frozen input resolve uncertainty before a changed attempt.

Use one current session/execution owner. Online protected work uses existing current
own admission/SDK. Persist an account/org selector only after verified same-account
admission and validated committed provision; it selects a partition, never grants access.
Offline reopen never scans partitions or trusts decoded JWT authority: require exact
unlocked selector plus existing store expiry/clock/denial fences. Token expiry alone
does not erase the valid seven-day local window. Explicit logout/account change/known
entry denial clears visible content immediately, invalidates executions, durably locks
the affected partition and removes its selector. Failure blocks active use with truthful
storage guidance. Ordinary closure closes handles without locking data. Same-account
restoration needs fresh current evidence. Preserve all pending/conflicting/unsupported
work and historical database version4 data; never clear/reset stores.

Foreground open/resume/reconnect/Save/Sync now triggers coalesce into bounded serial
cycles with transactional expiring claims across tabs and original-outcome recovery.
Creates precede dependent edits; rejected/conflicting work cannot block independent
records. Existing consumers alone reconcile receipts/current readback and Synced.
No background-sync reliance, rights from retained data, unbounded retries or bypass of
known denial. Expose safe attention state; automatic conflict resolution is excluded.

Only revisioned public shell assets and own navigation enter CacheStorage. Never cache
API/Auth/provider/business responses or `/admin` navigation/fallback. Setup readiness
requires separate confirmed shell readiness and atomic provision commit. Updates wait
for unsaved-form Save/Cancel and bounded executing work, retain queues, and require an
explicit safe reload; no forced reload or deletion of historical caches/resources here.
Generated neutral changes go through builder templates/tests/sync, never hand edits.

Fresh isolated synthetic local resources only; coordinator owns native/browser provider
execution and credentials. Reuse pinned installed tools, no installs/upgrades. Preserve
all concurrent work, retained resources and historical evidence. Never access/run/copy/
hash `apps/kdg-capture/migrations/tests/schema_fixture.py` or recursively copy app trees.
No production, push, real credentials/accounts, destructive cleanup, external provider/
release claims or physical-device/assistive-technology substitution. Story3.1 incomplete.

## I/O & Edge-Case Matrix

| Scenario | State | Expected | Failure |
| --- | --- | --- | --- |
| Actual own journey | Current setup, offline Save/reopen, reconnect | Own details retained; bounded delivery then current admin refresh | No server claim before receipt |
| Original form | Published update, false details, repeated Save | Pinned labels/answers; one immutable attempt | Accessible correction, values retained |
| Lost response / two tabs | Same saved action, interrupted claim | Original IDs/outcome, one effect, recovered claim | Durable Pending, bounded exit |
| Account/access change | Logout/B login/late response/current denial | Immediate fence, persisted lock, no prior-account rendering | No deletion or implicit restore |
| Offline expiry / outage | Valid or expired own observation | Valid local own use; expired locks; outage distinct | No seven-day all-read |
| Cache/update/storage | Offline shell, active typing/queue/schema4 | Public-only cache, safe explicit update, old saved work retained | Honest incomplete/storage states |

</frozen-after-approval>

## Code Map

- `web/src/startup.tsx`, `LocalEntryRoute.tsx`, `EmailCodeEntry.tsx`, `AuthEntry.tsx`:
  ordinary startup currently refuses offline and ends at EntryScreen. Preserve accepted
  email-code account fence and `/admin` behavior; add application-owned own composition.
- `history-store.ts`: schema4, existing setup import/create/edit/receipt/denial/clock
  owners. `read()` returns unknown internals; add guarded typed choices/presentation and
  recoverable delivery claims here, never raw IndexedDB reads in React. Preserve immutable
  action chains/conflicts and existing observations. Characterize risky changes first.
- `setup-download.ts`, `history-download.ts`, `create-delivery.ts`, `edit-delivery.ts`:
  reuse underlying existing consumers with one current lease; wrappers each own a
  lifecycle, so do not mount seven separate Auth owners. Existing history default30days.
- New own controller/React form/list/detail/sync modules may own presentation, selectors
  and scheduling. Reuse DESIGN tokens and accessible record patterns. Own UI displays
  date/answers/status without server audit. Role-appropriate administration link stays
  separate; never derive read.all from own admission or cached stronger observations.
- `web/local-host.config.ts` currently only context/admin GET. Builder template
  `platform/builder-cli/templates/application/web/local-host-tools/local-entry-host.mjs`
  hardcodes GET. Extend explicit route methods and bounded streamed JSON writes through
  owning template/tests and sync-kdg-local-host; no arbitrary generic proxy.
- `web/index.html`, new manifest/service-worker/build integration: no current shell.
  Actual build uses retained Vite8/React19/TS7 tools described in README. Keep selected
  public config injection safe and test the real built shell, not dev-module caching.
- Actual final qualification exposed a necessary existing producer repair in
  `write-candidate/provision.py:ProvisionHandler.authorize`: four sequential current
  checks can age the first verified observation past the unchanged one-second
  transaction-entry window before any database work. Correct the bounded orchestration,
  keeping exact mandatory own-read/optional edit/create semantics, consistent
  account/actor/membership, oldest successful monotonic observation, three-second
  total Access budget, cancellation/unwind and no network under business locks.
  Characterize and observe concurrent orchestration RED before the repair in existing
  selected provision tests; actual direct HTTP RED already records
  authorization_observation_expired at 1.8–2.4 seconds. No deadline/freshness relaxation,
  migration, Identity reimplementation or new owner contract. Coordinator owns actual
  native/HTTP replay. Existing own_proxy implementation agent owns only this backend
  function and its focused existing tests for this repair; own_workspace retains UI/store.

## Tasks & Acceptance

- [x] Observe missing ordinary own workspace acceptance RED; characterize affected store.
- [x] Implement guarded typed setup/records/claims and actual mounted workspace/form.
- [x] Integrate existing setup/history/create/edit consumers and foreground cycles.
- [x] Extend bounded generated proxy through template, tests and consuming adoption.
- [x] Add real built public-only shell, readiness and safe update handling.
- [x] Run focused store/controller/browser/proxy/shell/affected Auth checks and parity.
- [x] Coordinator actual SDK/GoTrue/SQL/browser saved-offline→sync→admin refresh proof;
  native boundaries, retained-work invalidation and safe machine evidence.
- [x] Independent three-lens review, fixes, final checks and evidence matrix/handoff; scoped local commit records this completed delivery.

Given actual configured local owners and authorized synthetic users, when ordinary own
UI saves offline, closes/reopens and later synchronizes, then only the owning partition
retains and sends the original work; current administrator refresh sees it after commit.
Given logout, account switch, current loss or stale work, no inaccessible data renders
and existing saved/attention/conflict work survives unchanged for authorized recovery.

## Implementation Notes

No unresolved intent gap: existing contracts settle behavior. Footprint is cross-layer
frontend/storage/build/proxy integration; changes are locally reversible, with retained
synthetic browser/API records. User approves keeping coherent scope/checkpoints without
routine confirmation. Implementation selected gpt-6.1-sol/high with no history; actual
model-only usage/timing unavailable. Coordinator handles actual provider/native proof
and documentation; implementation must report exact source ownership and test results.
Keep the agent available for repairs. Escalate missing inputs/tool denials immediately
to coordinator; do not wait silently for approval or stop at internal slice boundaries.

## Spec Change Log

## Review Triage Log

Three context-free reviewers completed before triage; no lens was skipped. All findings
are implementation/test corrections within the approved contracts, routed to patch.

| ID / lens | Verdict | Verified evidence and route |
| --- | --- | --- |
| B1 blind: offline expiry | high | Offline resume/pageshow calls sync, whose trigger returns without guarded local reading. Already-rendered records remain visible across expiry. Patch existing local guard into resume/view expiry handling; preserve retained work. |
| B2 blind: failed/partial history | medium | cycle ignores downloadOwnHistory's normal failure return and replaces its notice with Offline setup complete. Patch truthful incomplete/unavailable feedback and Retry without deleting earlier pages. |
| V1 verification: paging coverage | medium | Neither mounted nor store proof exercises after/next_key or more than100 records. A null continuation mutation is undetected. Patch multipage and mounted continuation verification. |
| V2 verification: mounted update | medium | Shell proof calls a separately imported helper; no test clicks the product update action. Removing its handler is undetected. Patch genuine waiting-revision/mounted typing/safe-click/retained-work verification. |
| V3 verification other: concurrent paging | medium | Two more calls capture the same next_key before either await resolves and append the same page; button has no loading guard. Patch bounded coalescing and deduplicated continuation publication. |
| E1 edge: concurrent paging | medium | Same reachable double-click path as V3, verified independently in more/button wiring. Patch with the same paging correction; retain this separate finding row. |
| E2 edge: offline expiry | high | Offline resume does not call the store, as B1. Patch existing authority recheck/expiry handling; retain this separate finding row. |
| E3 edge: logout marker | high | OwnWorkspace listens only for selector storage events. A successful negative marker plus failed selector removal leaves another offline tab displaying prior data. Patch account-bound marker invalidation independent of selector removal. |
| E4 edge claim: nonavailable continuation | high | more silently ignores expired/denied store results and leaves ready data visible after observing loss. Patch the negative presentation fence without deleting original actions. |
| R1 independent repair review: persistent quota | high | A continuing partition-write failure makes the new authority poll/resume map unavailable to locked, then clear the failed-save editor and original retry attempt. Mounted RED browser-1d491e67-0adf-4318-9c45-f0e8e26d5012 reproduces it. Patch storage failure versus known-negative handling while preserving expiry/denial/account locks and exact retry input. |
| R2 independent repair review: unreadable store at expiry | high | If transaction/read failure prevents authority validation, storageUnavailable retains the editor beyond the controller's last confirmed expiry. Enforce that already-known deadline when renewed authority cannot be established; add focused read-failure/expiry RED and preserve pre-expiry exact retry. Patch. |
| A1 actual API qualification: aged setup observation | high | Direct real API transport-green-ea98be797b114330817966419a5eaa9c records provision503 authorization_observation_expired while contexts200; four sequential current checks age the first observation before transaction entry. Correct bounded capability orchestration under unchanged budgets/freshness and prove actual stable producer use. Patch within existing contracts. |
| F-B1 final blind: pending offline-open sign-out | high | While local awaits open(pin), account/lastAccount are unset and partitionChanged ignores negative events. Pending work then publishes without rechecking selector/marker. Reviewer reproduced ready/private data after sign-out on the actual controller. Patch pending-account/generation and post-await selection/marker fences; add acceptance RED. |
| F-B2 final blind: later-page details | medium | Save and ordinary synchronization call local(n), replacing loaded records with page1. A selected/edited capture beyond100 disappears from record lookup, dropping detail after Save/refresh. Patch bounded refreshed selection/page retention with mounted later-page Save and synchronization assertions. |
| F-E1 final edge: removed selected child | medium | Component child state survives setup refresh; after selected A is removed and only B remains, the selector is hidden while openNew still selects A. Patch selection to a currently eligible child; test setup removal without reloading. |
| F-V1 final verification: failed shell at consumer | medium | Helper failed-install proof does not exercise successful provision plus failed prepare at the mounted consumer; treating false readiness as true is undetected. Patch mounted failed-resource setup/retained-data/no-selector/incomplete-feedback assertions. |
| F-V2 final verification: positive details | medium | Mounted proof saves Nee (details excluded) or cancels Ja; deleting positive details serialization is undetected. Patch Ja details Save/offline-reopen/synchronized exact-text assertions. |


| P-E1 independent final patch review: captured prior lock | medium | Reviewer executed isolated current helper: B replaces A selector between observeOwnAccount and invalidateOwnSelection; helper reports locked with no A deny, then verified B acceptance clears A marker. B routing/bound A controllers still block rendering; no exposure established. Patch durable target from captured trusted A independent of routing reread, preserving B. |
| P-A1 actual final journey: verified B stalls | high | Source-bound actual own-browser-e776cb0d-1889-4adf-a175-0b126e12fc95 passes8 checks then verified B stays Checking access for40s; no503/browser errors, source unchanged and static normal0. Preserved A routing hint reaches new controller's negative account fence before accepted B admission. Patch explicit verified transition and mounted regression while retaining unexpected-account locks. |

Patch groups: guarded local expiry/negative read (B1/E2/E4); truthful download status
(B2); paging concurrency and coverage (V1/V3/E1); cross-tab negative marker (E3);
mounted update coverage (V2). No finding is rejected or deferred. Independent repair
review and current affected qualification follow before completion.

Repair review: the tool refused to restart the third reviewer with `agent thread
limit reached`. The original three-lens review remains complete. Two independent
reviewers inspected repairs, including executed paging/update assertions; the blind
reviewer found R1 above, accepted as a sixth patch group. No denied reviewer restart
is claimed successful. A bounded follow-up concern about stale SDK session completion
was not supported through the configured SDK's storage-change guard; no speculative
runtime guard was added.

After capacity became available, a fresh complete three-lens pass accepted the five
F findings above. All are direct implementation/test corrections within the approved
contracts; no frozen intent changed, no finding is rejected or deferred. Prior native16,
load3, coordination3 and configured HTTP11 now pass with the A1 correction. Final
whole-source frontend/provider qualification follows these remaining repairs.

Final patch review closed all nineteen supported findings with direct corrections;
none were rejected or deferred. The last two have isolated RED/GREEN evidence:
helper capture/reread/acceptB b6c8ff38→2393e87d and mounted explicitB admission
672f34bf→624f2d50. Unexpected active-A account change remains locked (9294aea0),
and no-selected/captured all-only sign-out opens no database. Both independent
reviewers rechecked the final repairs and current source-bound receipts and returned
no supported remaining findings. Final coordinator current-entry/actual-provider qualification now passes; affected
store39/1398 sources remain unchanged.

## Verification

Final current-source checks pass: actual provider/browser13, mounted47, guarded store39,
history61/local-save141/pending216/create220/edit73/retained687 (1398), Auth575 tests/
71 checks, local-admin9/local-host10, proxy/static15 and unchanged shell helper8. Producer46
and affected430/101subtests, actual native16/load3/coordination3, actual transport10 and
configured HTTP11 pass with unchanged backend bindings. Own/admin exports, generated
client freshness, four scaffold parities and composition check-only pass. Final entry
aggregate last-frontend-checks-fd7ee7e93c784832b5f55f248d9a2e40; final actual journey
own-browser-bd4d7c0e-366e-489a-80b4-e873e699c208. All19 findings repaired; independent
final patch reviews clear, none deferred. Exact paths/commands/hash custody and AC matrix
are maintained in docs/STORY31_OWN_WORKSPACE_EVIDENCE.md and its machine evidence.

The first RED was store-level; no mounted ordinary-route RED preceded implementation.
Late baseline RED explicitly records false chronology. This remains an ATDD process
limit. All independent ready local work is complete. Story3.1 remains incomplete only
for AC-4 installed Android/iPhone extension and AC-6 true browser zoom, real assistive-
technology usability and installed-device results, requiring external equipment/operator
and controlled synthetic trusted HTTPS. No physical/provider/release simulation is
substituted. This spec is done for its local delivery, not the whole Story3.1.

Use pinned Node26.11.1/Python3.15 and existing proof harnesses, strict TypeScript/build,
real IndexedDB/Chromium and focused tests after observed RED. Builder auth/offline/write/
local-host parity for affected generated files. Actual provider/database/browser proof
is coordinator-owned; no fixture stand-in counts as actual runtime evidence. Record
commands/results, failed attempts and source bindings without sensitive values. Never
discover migration tests or copy forbidden sources. Update AC1–6 in existing evidence
and handoff; actual installed Android/iPhone and assistive technology remain separate.

Coordinator dispatch note: three Sol High implementation agents share this coherent
delivery: own_workspace owns guarded store/controller/UI/Auth/mount; own_proxy owns
builder template/proxy/local API routes and bounded built static host; own_shell owns
revisioned build/worker/manifest/readiness/update. Coordinator owns actual provider/
native/browser execution and evidence. This division avoids overlapping source edits.
Actual current resources remain held, with exact ready files under retained fresh frame;
no preparer rerun or hardcoded historical port. Protected synthetic administrator
read.own was explicitly restored using the existing owner helper for dual-role proof.
Model-only usage/time unknown.

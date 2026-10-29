# Story 3.1 own workspace and synchronization — 2026-10-29

Status: implemented, locally qualified and independently reviewed. Story 3.1 remains
**incomplete** for actual installed-device, true-zoom and assistive-technology evidence. This follows
`ac5499b2bea045db59260150c554cb94ecceb0b0` and consumes the committed Identity/native
prerequisite unchanged and the existing configured own-API contracts. This record supersedes their remaining
local integration items, while retaining their evidence and limits.

## Delivered behavior

Ordinary `/` now offers explicit observation Save/Cancel, My observations and own editing
using the existing original-definition, guarded storage and delivery owners. Ratings
start unanswered, boolean questions start Nee, hidden details remain in memory and are
excluded when false. Failed local saving retains values and the original uncertain
attempt. Own presentation contains date, answers and Pending/Synced/Needs attention,
without routine administrator attribution or audit.

The store remains schema 4. Guarded presentation and transactional 40-second delivery
claims use existing partition metadata; immutable actions and retained proposals are
preserved. Foreground cycles coalesce open/resume/reconnect/Save/Sync triggers, retain
original operation IDs, order creates before dependent edits and let independent work
continue past attention/conflict items. One cycle is bounded to 30 seconds and 100
attempted actions. Interrupted claims recover on a subsequent trigger after expiry;
there is no background-sync or automatic successful-delivery promise.

The selected account/organization is persisted only after committed provision and
separately confirmed offline shell readiness. It selects a guarded partition and grants
no authority. Actual SDK observations, explicit sign-out, current denial, generations
and cross-tab changes fence the prior account and durably lock its work. Portal
sign-out/account changes apply this negative fence even when the own component is not
mounted. Negative account/peer observations lock the captured prior partition while preserving
another tab’s new routing selection. Explicit sign-out independently attempts its marker,
selection removal and durable lock; a storage failure blocks use and displays truthful Retry guidance. Known denial never
deletes saved work. Token expiry alone does not erase an otherwise valid own offline
window. All-record review always uses separate current online read.all.

Blocked IndexedDB upgrades now return bounded Close other KDG windows / Retry guidance.
Abandoned opens abort late upgrades or close late handles; newer unsupported schemas
are refused without resetting data. An old version-3 sentinel and version-5 stores are
retained by actual IndexedDB checks.

The actual production index/main builds a revisioned public-only shell and own-root
offline fallback. API/Auth/provider responses and administrator navigation are never
cached. Safe explicit updates retain old caches/assets, pending/conflict data and
other-tab input. The generated bounded proxy adds only exact existing own routes and
POST/PUT, through its builder template/tests and consuming sync. The immutable loopback
host serves selected built files only. See [shell](OWN_SHELL_EVIDENCE.md) and
[proxy](STORY31_OWN_PROXY_EVIDENCE.md) evidence for focused commands and limits.

## Actual local provider/database/browser journey

Final current-source receipt:
`platform/deployment/.local/kdg-story31-20261028/fresh-8f3e984596bb453a902adb8710b4860d/own-browser-bd4d7c0e-366e-489a-80b4-e873e699c208/result.json`.

All **13 checks pass**, all selected runtime/build/qualifier sources remain unchanged,
and the owned static host stopped normally with exit 0. This used real local GoTrue,
emailed one-time codes through SMTP/Mailpit, the selected SDK, current Access and
Identity over trusted TLS, configured KDG HTTP owners and restricted PostgreSQL. All
accounts, credentials and observations are synthetic. Password sign-in is confined to
the independent qualification oracle; the ordinary UI uses emailed codes.

The built UI saved offline with no server effect, fully closed its persistent browser
profile and reopened offline with the original own record. Two tabs competed for one
durable claim. A real POST committed successfully, its real response was deliberately
dropped, and the interrupted claim recovered its original outcome after **34.73 seconds
of real waiting** for the existing expiry. Exactly one POST was sent; Synced required
the existing receipt/readback owner. An independently admitted administrator then
refreshed and reviewed the synchronized record and its server audit.

A dual-role administrator retained own pending work while offline portal rendering
cleared, direct offline `/admin` navigation failed and cache entries remained public
only. Protected read.all revocation cleared the portal while independent own access
and pending bytes survived. A second tab signed into account B by an actual emailed
code: prior A portal data cleared, A's partition was durably denied and B selected its
own partition. Explicit A reauthentication restored only freshly verified access.
Portal sign-out followed by a full cold offline reopen exposed no own records and
retained pending bytes.

An independent same-owner HTTP edit raced a saved offline proposal and produced a real
409/Needs attention without losing the proposal. Protected own-read revocation locked
the mounted DOM with original pending/conflicting content intact. After protected
restoration, explicit Retry reverified access. Offline sign-out, full profile reopening
and an actual B email-code sign-in preserved A's immutable work without displaying it.
The qualifier restored the deliberately revoked synthetic grants; resources/data remain.

The retained private command is `browser_own_actual.mjs` under the proof root's parent;
the receipt retains its executed bytes, exact source bindings and build reference.
Invocation uses pinned Node 26.11.1 and the current own-server/owner ready directories,
not historical ports or tokens. Credentials, private profiles and raw work stay ignored.

## Failure history and acceptance chronology

Pre-implementation store characterization passed before the missing `workspace()`
acceptance failed (`ordinary_own_workspace_guarded_view_exists`). The original capsule
`store-601ebbd8-4657-44cb-b8fa-c3b2dd75a947` has no result JSON because that initial
harness emitted only success; the tool-observed failure is not a passing receipt.
There was **no mounted ordinary-route acceptance RED before implementation**. That is
an ATDD chronology gap. A later actual-provider baseline check of selected web/contracts
from `ac5499b2bea045db59260150c554cb94ecceb0b0` confirms the missing New observation /
My observations route, but explicitly records `run_before_implementation: false` at
`baseline-own-red-d3cd0967-9ed8-4b26-92b3-49fd2ffc02c9/result.json`. It does not repair
or retrospectively claim the missing chronology. Shell and proxy pre-implementation
failures are recorded in their focused evidence.

Mounted REDs exposed quota failure discarding unsaved input, cold-offline SDK acquisition
remounting the form, stale A callbacks removing B's selector, simultaneous negative-lock
confirmation, blocked upgrades and cross-surface sign-out/account-change failures. Each
was corrected before the final mounted47 and actual13 passing receipts.
Failed frames and their original results remain retained.

Earlier actual runs remain failed/partial. An early claim check ran before expiry and
correctly observed Pending; the driver now waits the declared real expiry. One async
route assertion crashed before finalization and has an explicit abnormal receipt, with
no normal-stop claim. Another failed a coordinator focus assertion after the coordinator
had already moved focus into a radio; assertion ordering was corrected. No product
expectation or timeout was relaxed to dismiss these failures.

Intermittent actual 503s were reproduced as a **private fixture transport-lifetime
defect**: several owner clients borrowed one real HTTP pool and per-request client
closure closed it during another request. Sequential 4/current concurrent 6 transport
checks produced one concurrent 503 before correction; all 10 pass afterward. The
fixture now explicitly owns pool lifetime around owner lifespans. Production's default
per-client transport ownership, authorization and deadlines were unchanged. Retained
frames are `transport-red-9f2bfee3694e414a978cd69e42ae416e` and
`transport-green-f2ea43777b824e6491f51616a4af6946`. The preceding configured API stopped
normally with unchanged sources. The current corrected API and owner resources remain
held; no old/failed container, volume, capture or evidence was deleted.

A later actual replay exposed a separate producer freshness defect. Direct current API
probe `transport-green-ea98be797b114330817966419a5eaa9c` remained failed: context calls
returned200, while four provision calls returned503 `authorization_observation_expired`
at1.8–2.4seconds. Sequential current capability checks aged the first successful
observation past the unchanged one-second transaction-entry limit. The local proxy's
generic503 presentation did not identify this original code; direct API evidence did.

`ProvisionHandler.authorize` now retains mandatory own-read first, then overlaps the
three independent optional checks under the original shared three-second Access budget.
It preserves exact capability/principal binding, the oldest successful monotonic
observation, existing one-second freshness rejection and cancellation/drain before SQL.
No deadline, freshness, migration, wire DTO or Identity implementation changed. Two
focused REDs first demonstrated missing overlap and deterministic stale entry. Final
46 focused tests and430 affected tests/101 subtests pass. Actual refreshed native16,
load3, coordination3, direct sequential4/concurrent6 and configured HTTP11 pass. Final actual13 below also passes after the producer and UI repairs.

One native replay committed setup, then failed ConnectError because the retained
qualifier referenced an old API address for its original-record check. The coordinator
corrected that qualifier to use the current ready directory; the failed frame remains
retained. Native fixtures now explicitly borrow their real TLS pools for the whole
phase, close them on the owning event loop, and acquire fresh synthetic provider
sessions without changing credentials. HTTP role qualification explicitly revokes and
restores the synthetic administrator's own-read grant to verify all-only behavior,
since this delivery had already prepared its dual-role proof. No old403 expectation was
silently changed to match a new fixture. The current API ready directory is
`own-serve-c9920b804b02451898acc78ec334d8d3` in the retained fresh frame.

A final actual replay `own-browser-e776cb0d-1889-4adf-a175-0b126e12fc95` passed eight
checks, then remained Checking access after B's actual emailed-code sign-in. It remains
failed, with unchanged source bindings, no browser errors or503s, and normal static
host exit0. Independent patch review also demonstrated an earlier selector interleaving
that reported a durable A lock without executing it; no private-data exposure was
established because B selection and bound A controllers still fenced rendering. Both
are accepted corrections within the existing account/retention contracts. Both direct REDs preceded the repairs; current-source focused controls and final actual13
now pass, with both independent patch reviewers clear. Failed frames remain unchanged.

## Verification and review

Final current-entry aggregate:
`platform/deployment/.local/kdg-story31-20261028/last-frontend-checks-fd7ee7e93c784832b5f55f248d9a2e40/result.json`.
All four commands pass: mounted **47** (strict TS7 and actual built index/main), Auth
**575 tests/71 browser checks**, local-admin **9** and local-host **10**. Runtime/test
source bindings are unchanged. Final mounted receipt: `platform/deployment/.local/kdg-own-workspace/browser-5c94cf46-3ce1-4738-beea-37e1023109fb/result.json`.

Guarded store **39** and affected history61/local-save141/pending216/create220/edit73/
retained687 (**1,398**) pass in
`platform/deployment/.local/kdg-story31-20261028/final-workspace-checks-7b9520070c1648488bc9e532390366d0/result.json`.
Their bound sources remain current after the last controller-only repairs. That earlier
aggregate also retains the preceding mounted42/Auth/admin/host passes; final47 above
supersedes its whole-entry scope. Guarded-store receipt: `platform/deployment/.local/kdg-own-workspace/store-0726d99b-1711-4106-9def-91ac3c2f6519/result.json`.

Commands use the selected Node26.11.1 executable followed by these existing scripts:

```sh
"$N" apps/kdg-capture/web/tests/own-workspace-proof.mjs
"$N" apps/kdg-capture/web/tests/own-workspace-store-proof.mjs
"$N" apps/kdg-capture/web/tests/auth-proof.mjs
"$N" apps/kdg-capture/web/tests/history-store-proof.mjs
"$N" apps/kdg-capture/web/tests/local-create-save-proof.mjs
"$N" apps/kdg-capture/web/tests/pending-create-edit-proof.mjs
"$N" apps/kdg-capture/web/tests/create-delivery-proof.mjs
"$N" apps/kdg-capture/web/tests/edit-delivery-proof.mjs
"$N" apps/kdg-capture/web/tests/retained-proposal-resolution-proof.mjs
"$N" apps/kdg-capture/web/tests/local-admin-entry-proof.mjs
"$N" apps/kdg-capture/web/tests/local-host-proof.mjs
```

Exact argv, timings, logs and per-proof source hashes are retained in those aggregates
and referenced result files. The actual13 invocation uses that same pinned Node with
`platform/deployment/.local/kdg-story31-20261028/browser_own_actual.mjs` and the current
own-server/owner ready directories recorded in the handoff.

Producer46/affected430 tests with101 subtests, actual native16/load3/coordination3,
transport10 and configured HTTP11 pass. Final native binding audit confirms all four
native/HTTP frames still match their66–67 source bindings. Exported own/admin OpenAPI,
configured generated-client freshness, four scaffold parities and database composition
check-only pass. Focused proxy/static15 remains source-current. Earlier shell8 covers
unchanged shell/build helpers; its old whole-entry build is historical. Current mounted47
and actual13 cover the final actual main, genuine failed precache and mounted waiting
update with real schema4 Pending/409-conflict data. No historical whole-entry receipt
is represented as current after later edits.

Three context-free review lenses completed, followed by independent repair review and
a fresh complete three-lens pass. All **19 supported findings** were corrected; none
were rejected or deferred. Final two independent reviewers inspected the last repairs,
RED/GREEN evidence and current source bindings and found no remaining supported issue.
The spec retains every finding and the actual thread-limit denial; no denied reviewer
restart is claimed successful. The initial mounted-RED chronology gap remains explicit.

Scaffold impact: neutral bounded-write proxy behavior and emitted tests changed in the
builder and were synchronized; guarded domain storage, routing, shell and UI stay local.
Shared UI: existing record patterns inform the consuming view; no unproven generic
pattern was promoted. Agent context: current guidance suffices; unrelated AGENTS changes
are excluded. Documentation: this record, safe machine evidence, README, existing
readiness and handoff are maintained together. ADR: existing saving, ownership,
authorization, attribution, session, retention and release-safety contracts apply;
no new decision or migration. Pinned tools were reused without installs/upgrades.
Delegated implementation selected Sol High; repairs reused those agents. Actual model-only
usage/time are unavailable; measured command waits are retained separately in receipts.

## Current AC-1–AC-6 matrix

| Criterion | Established evidence | Remaining acceptance evidence |
| --- | --- | --- |
| AC-1 current all-read | Actual current role/native/API matrix, foreign-org denial, final portal and real all-read loss; no own fallback | None locally |
| AC-2 responsive review | Exact original labels/author/details; truthful failed/partial history and paging; actual offline producer appears only after sync and current admin refresh; simple own date/answers/status | None locally |
| AC-3 administrator audit | Actual committed create/edit/no-op/retry attribution; final synchronized record opens read-only online audit; own projection excludes audit | None locally |
| AC-4 portal/PWA split | Actual cold offline own route, guarded data/foreground delivery/public-only cache; dual-role offline portal refusal retains own pending work | Separately recorded actual installed Android/iPhone extension |
| AC-5 invalidation | Actual expiry/membership/app/outage evidence plus final all/own loss, second-tab verified account change, portal/own sign-out and retained pending/conflicts; late-open/read fences | None locally |
| AC-6 accessible review/boundaries | Keyboard/focus/labels/48px targets, paging/loading/failure,1440/390/320 layouts and actual role/HTTP boundaries; automated/native evidence separate | True browser zoom, real assistive-technology usability and actual installed Android/iPhone extension |

Every independent ready local item is complete. Story3.1 stays incomplete. The headless
shell's zoom keystroke did not change actual zoom metrics and is not a passing zoom
check. Current equipment observation finds no full Chrome/Chromium/Firefox, Orca,
Android or iPhone command/device access; no physical or assistive-technology result
is claimed. The smallest external next step is a controlled synthetic, reachable
trusted-HTTPS target plus an operator with installed Android/iPhone and a full browser/
screen reader. Qualify history/details/audit and the offline own/online admin boundary,
recording device/browser/OS, exact source/build and results separately. The retained host
binds loopback and supplies no phone or release evidence. Production, push, real-account
changes and destructive cleanup remain excluded. Safe artifact hashes, checks, source
custody and machine-readable matrix: [evidence](evidence/story31-own-workspace-20261029.json).

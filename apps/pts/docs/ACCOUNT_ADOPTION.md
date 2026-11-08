# Account access, corpus adoption and native private files

## Production release handoff — 2026-11-01

[E1-PTS-ADOPT](../../../_bmad-output/implementation-artifacts/spec-1-15-e1-pts-account-corpus-files.md)
is done within its reviewed local implementation scope. Its code, owner contracts,
runbooks and source-bound evidence feed the existing Scribeswell/PtS production
adoption delivery; production activation remains separate. Follow the
[cross-release ownership handoff](../../scribeswell/docs/OWNER_READINESS_HANDOFF.md#leave-e1--scribeswell-pts-release-alignment--2026-11-01)
for candidate reconciliation and execution ownership. Identity0030 is still a controlled
prerequisite; frozen Studies0026 proof cannot establish that compatibility. Leave E1
closure and hosted Reference VERIFY do not gate this PtS release. Historical progress
notes below retain their original checkpoint limits.

## Asynchronous logout and account replacement — loopback5, 2026-10-31

Review feedback added one maintained actual-App initialization failure case.
Root observed desktop/mobile RED (two failures, 8.804180s) before correction:
a thrown pts-auth read occurred, but no honest incomplete/Retry message appeared.
Logout initialization now runs inside the existing try/finally. A missing initialized
operation uses the established incomplete/Retry state, and the flag always resets;
existing successful operations keep their const callback scope and custody/auth guards.
Current focused GREEN passed 2/2 in 3.075327s with all 24 bindings unchanged;
full SDK/custody bytes remain unchanged during the fault, and first Retry completes
after storage recovery. This is UI/provider-double evidence, not native proof.

Copied-owner tests now execute the actual head30 activation postcondition alongside
supported head29. Untouched copies accept; changed historical migrations and six
predecessor references reject through the real inherited-source validator. Catalog/
role I/O remains explicitly stubbed for this source-only check. The initial run
passed 26 cases but failed the untouched head30 copy because its stub supplied the
head29 catalogue. Supplying the correct additive head30 catalogue fixed that fixture;
source-integrity expectations and real inherited-source validation stayed unchanged.
The initial output remains in the implementation tool transcript; no separate log
artifact was saved. All 27 tests then passed
(5.67s pytest, 6.132172s driver); no historical migration or production policy changed.

Current frontend attempt 8 passed 46 named tests, zero skips, TypeScript 1.969539s,
build 2.521117s and composition 0.064472s. Full HTTPS UI attempt 8 passed 162/162
in 94.968914s driver with all 24 source/test bindings unchanged. Fresh full native
cleanup attempt 8 passed all 21 browser checks, eight owner observations and 18
umbrella checks in 465.537514s driver, with all 500 source bindings unchanged. Five
owned PIDs stopped without force; five containers exited 0 without OOM. Session
attempt 2 passed five actual browser proof rows and 17 umbrella checks in
150.801633s driver, also with 500 unchanged bindings and clean owned shutdown. Sole
existing SDK refresh, bounded renewed cookie/native reads, actual delayed cookie
overwrite/refusal/repair and closed-App 60-second expiry denial passed. Final
coordinator artifact/task/matrix audits and three-review acceptance passed. The earlier frontend7/focused40/UI160/native7/session1 and
coordinator audits below are passed historical checkpoints with their exact pre-patch
bindings. No new 42-case focused run was executed. Fresh corpus16/48 remains current;
resource reconciliation final10 records 486 unchanged bindings, 14 deltas, seven exact
executed inputs and one conditional input, without a new timed measurement. Independent
review outcomes remain fixed: three filed findings in two patch groups were fixed
(L5-B1/L5-E1 logout latch, L5-V1 head30 tests); low L5-E2 was rejected because its
rare recoverable cookie-ordering interruption did not justify added guard/serialization
complexity. The isolated leaf is complete; E1 and production activation remain separate.

Each cleanup operation observes its original provider session, private custody
revision and the sole auth owner's persisted SDK pair. These observations only
reject stale work; they never authenticate a user or grant file authority. The
existing SDK's supported fetch/storage adapters refuse stale selection, writes
and removals across awaits. Independent active claims scopes retain separate
snapshots, so a newer call cannot hide an obsolete request. Only explicit nested
SDK scopes hand off their own mutation. Provider-verified original/captured
replacement rotations may advance recovery; independent later sessions cannot.
No private SDK methods, extra auth client/subscription/refresh owner or auth lock
was added. Private Web Locks remain bounded and storage-only.

Account-change notifications clear prior rendered content/actions and invalidate
in-flight results before awaited verification. Failed claims and unreadable custody
leave safe UI and Retry. Recovery does not restore an obsolete replacement over
a later SDK session. Scoped clear 401 recovery checks freshness before and after
owner waits and inside private writes; accepted own revisions hand off correctly.
Direct original cleanup and provider attempts remain independent of private faults
or unrelated held claims. Generic SDK logout always has an original-owner scope,
including an empty-original sentinel that refuses any later selected token.

Final provider/SDK cleanup checks auth freshness; private completion separately
checks custody. SDK-null recovery marks only fresh matching original account/session
custody pending under the existing lock, preserving foreign later custody. Final
logout observes the sole SDK and verifies selected original account/session claims.
Only typed missing-session error with its own guarded SDK removal may complete
naturally through SDK Sign out with no remaining session. Generic provider errors
and expired-session SDK refresh 400 retain their error/Retry contract. No provider completion or
response is fabricated.

Maintained actual-App RED preceded each behavior correction: the three filed
outcomes, SDK-internal delayed logout response, SDK-only supersession during
automatic switching, profile 401/403 SDK removal, and independent original provider
attempts during held claims or SDK observation. Module RED covered stale custody
and clear 401 recovery. All exact commands, named cases, timings, source bindings,
failed attempts and current results are referenced by the evidence manifest.
The additional named adapter cases cover parsed-profile-error removal after fetch
returns and empty-original SDK selection of a later token.

Fixture limits remain explicit. Historical onmessage-only notification wrappers
did not intercept the installed SDK's addEventListener delivery; earlier physical
SDK/custody assertions ran, but withholding was not established. The maintained
helper captures native dispatch, preserves listener/removal semantics and requires
actual held notifications before delivery. Early snapshot/overlap attempts failed
preconditions and are non-proving. Full UI attempt 1 passed 132/138; four reader
failures used a malformed literal token and now keep all original assertions with
the existing valid session fixture. Full UI attempt 3 passed 144/146; its automatic
rotation fixture edited SDK expiry JSON during an awaited request. Coherent browser
clock stimuli now preserve real JWT/session expiry and SDK refresh behavior without
editing SDK storage. Expectations were retained; no product fix dismissed these
fixture failures. All older passing UI/frontend checkpoints remain source-bound.

The first three fresh full native cleanup attempts failed and remain preserved. Attempt 1
failed after 16 umbrella prerequisites (90.268172s), with Sign in/SDK absence but
pending cleanup credentials after first receipted Retry. Attempt 2 passed seven
private browser checkpoints and 16 prerequisites (119.424698s), then final logout
left SDK/custody absent with an ordinary error. Its selected profile 403/
session_not_found and exact absence 200 observations corroborate the guarded removal
correction; uninstrumented attempt 1's exact cause remains an inference. Attempt 3
passed eight browser checkpoints and 16 prerequisites (118.525956s), then never
observed the expected ordinary provider request. Its exact pre-request cause was
not logged and remains an inference; subsequent App RED established the relevant
await/private-supersession failure. Every failed run retained 500 unchanged source
bindings, five PIDs stopped without force and five containers exited 0 without OOM.
None establishes all 21 browser cases and eight owner checks. New selected native
diagnostics contain status/error identifiers and safe state fields only.

Native cleanup attempt 4 passed nine browser checkpoints and 16 prerequisites,
then failed 108.400120s into the first new delayed-original case: Node route.fetch
could not resolve the browser-only fixture hostname. This was no product failure.
The fixture now holds an actual upstream clear 200 response in its existing ingress
gate, then requires the real TLS/browser response to arrive 200 and finish after
release. Exact old absence, later session/custody, no wrong logout and actual Open
assertions remain. All 500 source bindings stayed unchanged during the failed run;
five PIDs stopped unforced and five containers exited 0 without OOM. Its unhandled
Node failure had printed four sensitive request-header lines into private stdout.
That stdout was sanitized without retaining another secret copy; explicit redaction
provenance preserves original/current hashes and original execution/source/shutdown
receipts. It is not byte-exact original output. Future waiter failures use safe
identifiers; fresh full native proof passed in attempt 7 below.

Native cleanup attempt 5 passed 11 browser checkpoints and 16 prerequisites before
failing 205.772298s into the later same-account case's final logout. Both new core
cases passed actual held browser 200 arrival, retained later session/custody, no
wrong logout and authorized Open. Final logout then retained pending credentials
with SDK absent. All 500 source bindings stayed unchanged; five PIDs stopped
unforced and five containers exited 0 without OOM. Its exact cause remains an
inference; selected final-logout diagnostics were added for fresh qualification.

Maintained App RED then failed two cases (3.528598s) after another real App's
profile 403 removed the same original SDK session. Exact final provider-absence
proof, byte-unchanged original private custody and actual held notifications were
established before release, yet credentials remained. The candidate converges only
AFTER completed exact-original absence proof: previously owned pending recovery
for that same account/session must retain its entire original base, without any
replacement. Only revision and verified rotation credentials may differ; fresh
private observation and SDK-null freshness are rechecked inside final writes. A
fresh sole-SDK observation must be null without error and remain current. SDK nil
alone proves no provider absence. Foreign/new custody, replacement recovery,
private faults and expired-session SDK refresh 400 feedback retain their protection.
A paired peer-owned revision RED passed both unchanged-private cases but failed
two peer-retention cases (5.082956s); only the explicitly allowed revision and
verified original revocation token changed. The correction now preserves the
original base while accepting that recovery-only handoff after exact absence.
Pre-review-patch full native/session and coordinator audits passed below under their original bindings; current requalification and independent review acceptance remain pending.

Native cleanup attempt 6 failed 203.374072s after 10 browser checkpoints and 16
prerequisites. The different-account core and its later normal logout completed;
selected provider 204/peer profile 403/session_not_found/exact absence 200 observations
corroborate current original-only nil convergence. The same-account case then timed
out waiting for a popup during later authorized Open, before its core checkpoint.
Safe state had a fresh SDK pair and matching, non-pending custody; document/control/
native response statuses were not yet instrumented. No failed 200 assertion or
product cause is inferred. All 500 bindings stayed unchanged; five PIDs stopped
unforced and five containers exited 0 without OOM. New selected metadata/control/
GET/HEAD/range-status observations and closed document-error booleans retain the
original Open/200/206 assertions and budgets. An observation-only window.open
counter preserves the actual call via Reflect.apply and records no arguments or
URL. Fresh full native proof passed in attempt 7 below.

Native cleanup attempt 7 then passed all 21 browser checks, eight owner
observations and 18 umbrella checks in a fresh genuine-provider/native-database/TLS
fixture using the current immutable images. The existing browser budget completed;
no timing assertion or product timeout changed. Original-only cleanup, private
faults, delayed response/custody races, expiry/recovery, owner permissions and
outage recovery all passed. Selected native provider 204/peer profile 403/exact
absence 200 observations corroborate guarded same-original convergence. This does
not assign a cause to attempt 6's uninstrumented popup timeout. Execution receipts,
proofs, source binding, safe progress and clean-shutdown audit are hashed in the
manifest. The separate fresh session-races fixture also passed below.

Fresh image-session-races attempt 1 passed five genuine native browser proof
rows and 17 umbrella checks in 155.178469s driver. Desktop/mobile real login,
Directory/native PDF/download hash, host-only cookie and local logout/denials passed.
The existing sole UI SDK performed a real refresh preserving account/session;
renewed cookie lifetime stayed bounded by its actual credential and native GET 200,
range 206 and HEAD 200 passed. An actual delayed cookie overwrite was refused for
new/old mismatched contexts, then repaired. With the App closed, genuine 60-second
credential expiry denied fresh viewer GET/HEAD/range without a new refresh owner.
Three owner baseline refresh observations remain synthetic prerequisite support,
separate from the browser renewal proof. All 500 source bindings stayed unchanged;
five PIDs stopped without force and five containers exited 0 without OOM. Final
coordinator artifact/task/matrix audits passed; independent review acceptance remains
pending; no production activation or physical-device qualification is claimed.

Fresh current corpus qualification passed all 16 native checks in 17.432447s,
with all 48 proof source hashes verified current and the native container stopped
exit 0 without OOM or force. Migration failure/rollback/predecessor compatibility,
restricted rights, replay/concurrency/FKs, history/attribution, binding/context and
reclamation proofs passed. The earlier reuse audit was valid when captured; final
artifact audit attempt 1 later found the response-gate fixture had changed (47 exact,
one changed), so that retained snapshot is historical. The failed audit is preserved;
this fresh run replaces the current corpus claim. Retained timed resource run
(21 checks) is reconciled against 486 unchanged
source bindings, 14 explicit deltas, seven exact executed sources and one cleanup-only
conditional budget. The new one-shot clear-response gate is inactive on the
retained resource path; that explicit judgment is recorded with current hashes.
This is no new timed measurement. Exactly 261 artifact files,
77 inputs across four verified owner bundles, five generated outputs and five
immutable image IDs/users were checked before reuse. Fresh full native/browser qualification is recorded separately above. Generic production-CI, hosted/A1/Reference,
physical-device and activation limits remain explicit.

Five impacts: neutral shared HTTP transport/scaffold ownership stays unchanged;
no application-specific auth/custody policy or UI is promoted. The maintained
notification fixture is reused by PtS UI/native tests. Existing agent context
suffices; owner and Leave documentation record exact evidence boundaries. Accepted
ADR history remains unchanged; no new architecture decision is required.


## Private custody failures and provider logout — loopback4, 2026-10-31

Current implementation checks passed within the approved isolated boundary.
This section supersedes earlier “current”
wording only for the loopback4 browser correction; prior receipts retain their
original source/image bindings. Current full native cleanup and session races passed. Coordinator
artifact/task/matrix audit passed; independent review remains open.

Ordinary authorized readers who never prepared native authentication retain the
existing SDK provider-local Sign out when private Web Locks are absent, acquisition
fails or times out, or private storage writes fail. Available shared invalidation
still runs. Known native cleanup instead keeps its original/replacement distinction:
private mutation failure does not prevent an exact original-token provider attempt,
and failed persistence cannot trigger an unsafe SDK session load or refresh. Exact
original provider absence and local file invalidation remain mandatory; incomplete
cleanup is visible and Retry remains available. Unreadable custody is unknown,
never proof that no cleanup exists or that logout completed. An ordinary final
clear refuses native custody another tab prepares during provider logout; it keeps
that cleanup visible and recoverable through Retry. With healthy private storage,
that refusal records pending state under the same lock so its notice survives reload.

Failed writes may retain cleanup-only credentials in the loaded tab, anchored to
its exact shared raw revision and generation. This gives no file authority or
reload-durability promise. Another tab's mutation/clear supersedes that memory.
The latest verified original/replacement rotation wins even behind a held lock.
All actual custody writes retain the bounded shared Web Lock protocol; external
owner/auth waits stay outside it.

A delayed preparation also checks the existing auth owner's configured persisted
account/access-token and optional refresh-token pair synchronously inside its
final storage-only callback. This negative freshness check grants no authority and performs no SDK load, refresh or network
operation. It prevents stale durable and volatile credentials even while another
tab's ordinary logout cannot write private custody and auth notifications are held.
An earlier asynchronous SDK-load candidate failed the genuine 60s provider fixture;
maintained actual-App 60s RED also lacked custody. The installed SDK's 90s load
margin supports the refresh-feedback inference, but the failed native attempt lacks
safe response counts and its exact cause is not independently observed. Its receipt
remains unchanged; the later full cleanup result below supplies current proof.

Current root frontend qualification passed 39 individually named cases with zero
skips, TypeScript 1.971s/build 2.773s and composition 0.065s. Focused concurrent
new-custody/reload App cases passed 2/2 in 3.4s. Current full HTTPS UI passed
120/120 desktop/mobile cases in 69.192s driver, with source/test hashes unchanged.
Full native cleanup and session races passed. Earlier frontend37/UI118
and previous120 results retain their checkpoint bindings.
Focused repository-owned actual module/App RED preceded each correction, including
ordinary faults, exact-original cleanup/replacement, failed-write rotations, queued
mutation/final-write races and short-lived SDK behavior. Exact commands, logs and
source/image hashes are in the [evidence manifest](../../leave/docs/testing/evidence/e1-pts-adopt-20261031.json). Initial native7
passed at an earlier candidate; later native8 attempt2 failed at custody readiness,
with clean recorded shutdown. Neither is substituted for current full qualification.
The retained timed resource boundary has 489 unchanged source bindings, 11 explicit
frontend/fixture deltas, seven byte-exact executed sources and one inspected
cleanup-only conditional budget (final5 reconciliation, including the latest
fixture retry-helper hash). It retains executed stream proof, not current
browser proof; resource/session stays at 300s while expanded cleanup alone uses
390s. All 261 artifact files, 77 owner bundle inputs, five images/users and five
owner-generated outputs were verified unchanged before reuse.
Fresh native corpus3 passed 16 checks in 18.269s with all 48 source bindings exact
after the fixture gate change; its PostgreSQL stopped0/noOOM. The first
pre-acceptance PostgreSQL startup
failure (exit137/noOOM) retains an unknown cause. Existing hosted, A1/Reference, physical
mobile and generic production-CI limits remain explicit. E1 remains unfinished.

The first full cleanup attempt failed after 111.902s with all 500 source bindings
unchanged and clean recorded five-process/five-container shutdown. Its first seven
new private-fault checkpoints passed; the eighth failed before owner-response
release, and an unhandled pending browser-response promise masked the primary
cause during teardown. The next fixture-only change immediately handles that
promise and records selected safe state while preserving the original error.
No product, timeout or assertion changed to dismiss that unexplained failure.
A subsequent targeted diagnostic failed at the strict other-tab no-custody
precondition: a valid nonpending record already matched the live SDK recovery pair
before the first held response was released. One delayed response could not hold
all valid preparations from the real SDK. Fixture-only sequencing now initializes
the ordinary fault tab first and separately holds every actual owner200 for the
exact verified pair. It uses an actually held bearer privately for cleanup proof;
old single-response modes, SDK behavior, TTL and strict absence remain unchanged.
At that checkpoint, fresh targeted/full native cleanup and session qualification
remained open; the later targeted result is recorded below.

The next targeted attempt passed the strict queued-write, physical SDK clear,
exact original absence, credential absence before notifications, later outage-entry
and actual Open assertions. Its final subsequent ordinary SDK logout then remained
visibly failed with SDK/custody absent; the whole attempt failed (131.600s), with
500 unchanged bindings and clean five-process/five-container shutdown. Its exact
native cause remains unobserved. The fixture now reuses the existing separately
characterized bounded recovery: require fresh actual200/exact-pair/absence and
strict SDK/custody absence before one actual Sign out retry, then require the final
Sign in heading and no alerts. It records whether retry occurred. This preserves
the failed receipt and makes no product, TTL or false-completion change.

Fresh targeted private5 passed all nine browser checkpoints and eight owner
observations (18 umbrella checks, 157.030s), with 500 unchanged bindings and clean
five-process/five-container shutdown. It includes strict queued-final-write and
physical SDK clear before delayed notifications, later outage-entry/Open/logout,
and new native custody during ordinary logout with honest failure/Retry. The
subsequent logout completed normally: retry_observed:false. Selected genuine
refresh400(refresh_token_not_found) accompanied normal completion; this does not
explain the prior failed cause or establish native execution of its conditional
retry branch. The existing controlled actual-App characterization remains separate.
This run explicitly selected private-only coverage. The full cleanup result below
is separate from this targeted selection; current session proof is recorded below.

Five impacts: the existing shared neutral HTTP client/fixtures remain; private
custody and session policy stay PtS/auth-owner local. No new scaffold engine or
app-specific shared UI is promoted. Existing agent instructions suffice; owner and
Leave evidence record exact outcomes, and accepted ADR history is unchanged.

Historical loopback3 implementation qualification passed within its approved isolated leaf:
27 named TAP cases with zero skips, 86 HTTPS UI cases, TypeScript/build/composition,
16 native corpus checks, full cleanup (18 fixture checks/10 browser checkpoints/
seven owner observations) and session races (17 checks/five browser cases).
Coordinator artifact/task/matrix audit passed; subsequent independent review
completed with three medium findings that required loopback4.
Earlier results retain their original source/image bindings.

Root verified all 77 unchanged bundle inputs across four owners, five image IDs/users
and five generated outputs before reuse. The previous 21-check timed stream/resource
proof is retained only for its unchanged executed boundaries: 493 of 500 source bindings
match, with seven explicit frontend/native-fixture deltas. Its prior browser proof
is historical and is replaced by current cleanup/session qualification. No hosted,
human-device, production-CI or production-activation completion is implied.

Current cleanup contracts are documented in the
[Identity runbook](../../../services/access/IDENTITY-MIGRATIONS.md) and
[native-file contract](../../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md).
Identity0030 remains a separate controlled prerequisite checked with the restricted
runtime credential before PtS migrations/activation.

Current FULL cleanup2 passed all 18 umbrella checks, 19 browser journeys (nine
new private/concurrent plus ten retained) and eight owner observations in
391.091984s, with both targeted selection flags false and scrubbed from the child
environment. All 500 source bindings remained unchanged. Five source processes
were absent without forced termination; five containers stopped with exit 0 and
no OOM. The owner proof includes three exact provider-account/session absences
and seven restricted-role denials; actual pending upload, PUT, finalization and
ready replay preserved all 650 bytes, content identity and one association. Both
private8 and the retained two-tab case completed their subsequent logout normally
with retry_observed:false. This full run does not establish execution of the
conditional native retry branch or explain earlier failed causes.

Fresh image-session-races attempt2 passed 17 umbrella checks and all five genuine
browser journeys in 160.786322s, with all 500 source bindings independently matching
current source and clean five-process/five-container shutdown. Desktop/mobile real
login, native PDF/Download and provider-local logout passed. Genuine existing-owner
refresh preserved the provider pair, renewed a bounded cookie and enabled native
GET 200, range 206 and HEAD 200. A real delayed cookie physically overwrote a newer
cookie; old/new context isolation and authorized repair passed. With the app closed,
the genuine 60s credential expired and new viewer GET/HEAD/range reads were denied
without another refresh owner. Attempt1 was rejected before fixture creation because
the coordinator supplied the unsupported phase session-races: exit 1 in 1.117s,
zero checks, no resources and unchanged source. Its command-error receipt is retained.

The current manifest maps all eight requirement rows to exact completed result
keys. Current frontend39/UI120/corpus16/cleanup19browser/session5browser are qualified
within their recorded boundaries. Coordinator artifact/task/matrix audit passed;
independent BMAD reviews remain open; E1 and production activation remain separate.

## Shared browser cleanup custody — loopback3, 2026-10-31

Cleanup custody belongs to the application's shared browser storage across real
tabs. `fileTransport.ts` keeps the existing private `pts-file-cleanup-v1` record
and accepts valid existing version1 original/replacement recovery records. Every
preparation observation, original/replacement rotation, pending transition and
completed clear writes a fresh private revision. Completed logout replaces the
record with exactly `version`, `cleared: true` and a random `revision`; it contains
no account/session identity or original, replacement, refresh or revocation token.
This marker means neither pending cleanup nor file authority.

Each storage read/compare/write runs synchronously inside one short same-origin
Web Lock with a two-second acquisition deadline. Owner HTTP and existing auth
work run outside that lock. Preparation captures its persisted revision before
the owner wait and compares it again under the lock before retaining credentials.
A newer mutation in any app tab, including completed cleanup from an initially
empty record, supersedes an older response. Storage events and module-local
epochs are not the shared synchronization mechanism. Local auth observations
still guard newer credential rotations. Lock/storage failure refuses native
custody safely; ordinary authorized corpus reading does not wait for it. The
existing auth client, subscription and refresh owner are unchanged.

Focused actual-module and actual-App acceptance failures preceded this change.
Root-owned current results and exact source bindings live under
`platform/deployment/.local/e1-pts-adoption/review-loopback-3/`; earlier loopback2
proofs keep their original bindings. Fresh native qualification additionally
holds an actual owner200 background preparation in one real app tab while a
second completes file cleanup and provider-local logout, verifies the exact
original session absent before release, then checks credential absence, ordinary
authorized entry during a file-control-origin outage and old/new file isolation.
Exact command/source/image receipts are linked in the delivery evidence; final
coordinator audit passed; independent review remains open.

All five impact decisions remain unchanged: reuse the proven neutral shared HTTP
client and fixtures; keep browser custody and corpus/session policy in PtS and
its existing owners; add no scaffold/session engine or app-specific shared UI;
retain existing agent guidance; update owner/Leave evidence without editing
accepted ADR history. Backend, Identity, migration and stream contracts are
unchanged. Their existing immutable artifacts may be reused only after exact
owner-input and image verification, without relabeling historical receipts as
new executions or weakening hosted/human-device/production-CI limits.

Full cleanup4 passed in 356.481 seconds with all 500 source bindings unchanged;
five PIDs are absent/unforced and five containers stopped0/noOOM. The real two-tab
case completed exact original absence before delayed owner200 release, strict
credential absence, rendered authorized entry during the control-origin outage,
old-context denials and new actual Open. Subsequent authorized logout completed
without retry (`retry_observed: false`). The existing visible SDK-error retry is
covered by the controlled actual-App2/2 characterization; native3's exact error
remains unknown. No product change or native retry observation is inferred.
Current-image session-races1 also passed 17 checks/five browser cases in
163.476 seconds with all 500 source bindings unchanged and normal5-PID/5-container
shutdown. It proves genuine existing-SDK renewal (+31 seconds), exact UI setup/
cookie/new-context provenance, delayed cookie overwrite with revoked/crossed denial
and repair, and closed-App60-second expiry denying new GET/HEAD/range without a
viewer refresh owner. Exact receipts are under `loopback3` in the Leave manifest;
coordinator audit passed; independent review remains open.

## Historical loopback2 qualification

The packaging evidence combines the preserved interrupted
`loopback2-clean-source-attempt1/clean-source-proof.json` with its separate
`coordinator-build-completion.json`. The coordinator verified all twelve recorded
stage logs, 261 source files, four current owner bundle-input inventories and five
immutable images, then completed the missing thirteenth import smoke in a NEW
UID10001/read-only/network-none migration container. Its actual 0003 migration bytes
also matched. The original interrupted driver remains interrupted; the completion
receipt does not rewrite it. No database was configured or migrated by that smoke.
The focused desktop/mobile cleanup UI-double run passed 10/10 in 5.9 seconds
(6.603 seconds driver), with web source unchanged. Genuine provider/current-image
journeys remain a separate qualification boundary.

Loopback2 frontend verification passed 21 individually named actual-module TAP cases
with zero skips, PtS TypeScript/build and migration composition dry-run. The final
HTTPS UI-double suite passed 78/78 in 49.6 seconds (50.017 seconds driver), with web
source/test bindings unchanged. The selected loopback2 PtS regressions passed 84 tests
plus the owner DTO check. These checks do not replace genuine provider/browser or
restricted native database evidence. The historical loopback2 resource/session proofs below
retain their own source/image boundaries.

Loopback2 current-image cleanup5 passed 18 checks in 332.900 seconds with all 500
source bindings unchanged. Nine real browser checkpoints include independent
same-account login/recovery, delayed original preparation, outage/reload/Retry,
password return/save and repeated Open. Original-session expiry/refresh and exact
absence plus replacement refresh beyond provider reuse grace/reload/Open passed.
Seven restricted native owner observations passed. The actual successor uploader
PUT/finalize/attach and ready replay retained identical 650 bytes/Content identity
and one association. Five processes were absent unforced and five containers
stopped 0/noOOM. Both PtS and Access used the current immutable images; Content
and Directory were source processes. Resource and session-race proofs are recorded
below. Exact proof/source/image/cleanup receipts are in the Leave evidence manifest;
all failed predecessors remain unchanged.

Fresh `loopback2-image-resources-attempt2` passed 21 checks in 479.598 seconds,
with all 500 source bindings unchanged. Its 495 samples retained no monitor failure.
The exact 128 MiB transfer took 128.001 seconds at 1 MiB/s; every measured owner's
single-stream/all-phase RSS growth stayed below 64/192 MiB. All eight account/global
admission and reacquisition observations passed. Storage interruption produced an
incomplete response in 30.670 seconds, followed by authorized same-ETag range
recovery; final disconnect reached zero idle business transactions by 2.047 seconds.
SIGTERM drained all 128 MiB in 4.762 seconds, exit0 without force; a NEW instance
served the authorized same-context range. Four source processes were absent unforced
and six containers stopped0/noOOM. PtS and Access ran the qualified frozen images;
Content and Directory were source processes. Exact resource/sample/source/image/
gateway/shutdown/audit hashes are in `loopback2.completed.resources` in the evidence
manifest. Session-race proof is recorded below; coordinator audit and independent
reviews remain open.

The first loopback2 current-image resource attempt was interrupted by a host
restart. Its original driver exit is unknown and its receipt remains incomplete;
partial browser/uploader/large-object observations are not a resource pass.
Independent inspection found all four recorded processes absent and all five
containers stopped 255 without OOM, with restart disabled. Graceful shutdown is
unverified. All 500 source bindings still matched; no retained fixture was restarted
or reset. The separate `review-loopback-2/resource-attempt1-host-interruption.json`
retains this audit. The fresh resource2 result above supplies resource closure;
separate session-race proof is recorded below.

Fresh `loopback2-image-session-races-attempt1` passed 17 checks in 171.404 seconds,
with all 500 source bindings unchanged. Five browser observations cover desktop and
emulated-mobile genuine login, native Open/Download and current-session denials;
one actual existing-SDK refresh extends the same account/session by 31 seconds and
proves exact Sources setup/cookie provenance. The delayed old Set-Cookie physically
overwrites after provider-local logout/new login, yet revoked/crossed contexts are
denied and current transport repairs. With the app tab closed, genuine 60-second
credential expiry denies new native GET/HEAD/range. Five source processes were absent
unforced and five containers stopped0/noOOM. Both qualified immutable images were
used; Content and Directory were source processes. Exact proof/source/image/gateway/
cleanup hashes and eight-row coverage pointers are in `loopback2.completed.session_races`
and `loopback2.requirement_matrix` in the evidence manifest. Final coordinator audit
and independent reviews remain open.

## Historical loopback1 qualification

Historical loopback1 qualification included the actual existing gateway smoke
(`python3 platform/deployment/tests/gateway_smoke.py`): exit0 in32.60seconds,
with unchanged hashes for its eight bound sources and no remaining owned
containers/networks. Dedicated private methods/CORS/host denials passed across
API-certificate rotation; the separate file certificate stayed unchanged.
Chain rotation, idempotence and failed-candidate recovery also passed. Earlier
failed attempts are retained, including the real multi-certificate incompatibility
and the fixture trust-bundle correction. Receipt:
[gateway attempt5](../../../platform/deployment/.local/e1-pts-adoption/review-loopback-1/gateway-smoke-attempt5.json).

The clean-source proof completed13stages: explicitly network-enabled preparation
from an empty dependency cache, four offline owner packages/verifications, five
network-disabled image builds and five nonroot, read-only, network-disabled import
smokes. It used a new source-only copy and preserved retained bundles/containers;
all four owner bundle inputs matched current root source. This exercises the CI
preparation commands locally, not a hosted GitHub Actions execution. Receipt:
[clean-source proof](../../../platform/deployment/.local/e1-pts-adoption/loopback1-clean-source-attempt1/clean-source-proof.json).
Fresh combined PtS/Access image cleanup qualification passed in
`loopback1-image-cleanup-attempt10`: exit0,17checks,289.27seconds. Six browser
checkpoints and seven native owner observations cover file/provider outage and
reload recovery, external revocation, original expiry/refresh, durable rotation,
second expiry and verified same-session recovery before real local revocation,
exact absence and replacement-context isolation. Ordinary no-actor/no-grant auth
logout remains available. All499bound sources stayed unchanged; the coordinator
confirmed five source processes absent unforced and five containers stopped0/noOOM.
PtS and Access/Identity both used the current immutable images; Content/Directory
were actual source processes. That checkpoint's audit/review state is historical;
current coordinator audit and independent reviews remain pending.
Import smokes alone do not establish those boundaries. Earlier failed/interrupted
attempts remain retained.
Fresh `loopback1-image-resources-attempt1` passed20checks in427.285seconds with
both frozen images. The128MiB transfer completed in128.000seconds at1MiB/s with
exact bytes; both account/global admission and full reacquisition cycles passed.
Single-stream/all-phase growth remained below64/192MiB per measured owner.
Upstream idle failure ended with incomplete bytes in30.788seconds; authorized
same-ETag range recovery passed. SIGTERM drained the full transfer in6.806seconds
without forcing, and a new instance served the same context. All499sources were
unchanged at closure; four source processes were absent unforced and six containers
stopped0/noOOM. These isolated observations do not promise production capacity.
The original resource proof's static Access-source description is inaccurate;
its Access image binding proves the frozen image used. Original proofs remain
unchanged. Three later description-only edits in `resource_acceptance.py`,
`image_acceptance.py` and `integration_fixture.py` now report the actual selected
Access mode; the manifest reconciles those deltas for cleanup and resources.
Reusing an immutable image preserves its original receipt description; consult
the new gateway/Access bindings for the actual owner mode in that new run.
Fresh `loopback1-image-session-races-attempt1` passed16checks in178.425seconds
with both frozen images and all499sources unchanged. Desktop/emulated-mobile
genuine auth, native Open and exact Download passed. Two genuine SDK refresh
responses support exact Sources setup/cookie provenance with31seconds later
expiry. A delayed cookie physically overwrote the current cookie after local
provider logout and replacement login; crossed contexts were denied and current
transport repaired. Closed-app60second expiry denied new native GET/HEAD/range.
Five source processes were absent unforced and five containers stopped0/noOOM.
The twelve-check `loopback1-corpus-attempt1` retains its captured source binding.
Two later fixture-only changes in `integration_fixture.py` and
`native_acceptance.py` add baseline refresh and fresh TLS observations. Fresh
`loopback1-corpus-attempt2` now establishes current-source closure:12checks passed
in6.787seconds, all47bound sources match, and its new PostgreSQL container stopped
0/noOOM. Original attempt1 results remain separate. Final fixture guards16 and
shared native-client3actual named TAP tests also passed without skips.
The historical loopback1 full HTTPS UI-double suite passed64/64 in49.4seconds with all24web
source/test bindings unchanged. The earlier63/1 and unchanged isolated1/1 results
remain separate historical observations; no failure cause is inferred.
Full production unittest discovery has no passing result: its interrupted run
and isolated generic CLI resource-supervisor failure are recorded in the
[evidence manifest](../../leave/docs/testing/evidence/e1-pts-adopt-20261031.json).
Relevant generic sources match captured pre-PtS bytes; no pre-task passing
execution or unrelated CLI repair is inferred from that equality.

Browser file recovery retains one original receipted credential for the exact
session and the latest verified credentials needed by the existing auth owner to
finish local revocation. Save this custody before cookie setup and before any
post-refresh revocation attempt. Cleanup failure remains visible, survives reload
and prevents replacement contexts. Both cleanup owners receive bounded attempts
even if one is unavailable. Ordinary auth logout remains available to accounts
that could not establish native file authentication; missing proof/401 never
establishes successful file cleanup or provider absence. Cleanup evidence never
authorizes metadata or bytes. Do not log credential or full proof material.

Recovery writes observe the current auth preparation before awaiting the owner.
A late preparation cannot overwrite a newer same-session refresh credential;
verified auth-claim recovery also rechecks that its original observation is still
current before writing. Logout/switch and confirmed custody removal supersede
older work. These guards protect browser recovery custody; each native read
still performs the unchanged current-session and exact-capability checks.
An incomplete cleanup message remains visible across account/password/login views
and reload; Retry Sign out invokes the existing recovery path. Collection and
launcher reloads stay suspended during this unresolved state so they cannot
erase its recovery message or refresh an expired original account opportunistically.

Before explicit original-session revocation, the existing auth owner obtains its
current SDK session and verifies the exact original account/session with trusted
claims. When it matches, retain and revoke that fresh pair directly. The SDK can
refresh stored credentials while loading a session, even before an explicit old
refresh-token operation; reusing the old token after that rotation can fail.
A foreign or absent current session uses the existing explicit-original recovery
path with exact session verification. The existing App subscription supplies the
observation epoch; recovery adds no extra SDK subscription or refresh owner.

Clean production CI acquires exact uv0.13.1 and standalone Python3.15.0, explicitly
prepares each registered frozen owner's dependency cache with network allowed,
then invokes the existing owner packagers offline and verifies every bundle before
Docker. `platform/deployment/prepare-runtime-bundles.py` inventories PtS, Access,
Content and Directory from the production registry. Existing bundles refuse
replacement; preserve them separately before a new local package. No installer or
implicit version fallback is added to Docker/runtime. Reference/People frozen
bundles are outside this production registry and retain their own build contracts.

All five delivery impacts remain in this item: shared HTTP native-file transport
and its first PtS consumer cover shared UI; the executable preparation/ingress and
existing builder identity fixtures cover scaffold/build reuse; existing agent
instructions already express the owner/current-authority boundaries; owner
contracts/runbooks/evidence provide documentation; existing ADR0020/0022/0025/0055/
0056/0064/0065 govern the implementation without editing accepted decisions.

E1-PTS-ADOPT implements the [approved owner contract](architecture/contracts/account-access-and-corpus-transition.md)
and the [shared Content/native-file contract](../../../platform/docs/architecture/contracts/content-ownership-and-authenticated-read.md).
Coordinator audit and reviews remain in progress; production activation,
DNS/certificate/provider configuration and production mutations are separate.

## Current boundaries

Access checks the account capability matching each action: `pts.poetry.read`,
`pts.poetry.export` or `pts.poetry.documents`. None implies another. No browser
organization selector/header, employment record, synthetic membership or account
copy selects the corpus. The owner-controlled singleton binding retains one
reviewed legacy partition as storage provenance. Other partitions, composite
foreign keys, payload order, import/conflict history and recorded attribution
remain intact. An absent verified binding returns unavailable and blocks release.

Predecessor organization consumers retain their own restricted roles during the
coordinated transition. Successor reader/import roles cannot inherit predecessor
authority. Imports derive the binding server-side and share the predecessor's
partition advisory lock, retaining replay/conflict behavior. Runtime cannot
replace the binding or mutate the corpus. Do not merge partitions by counts.

Every stored document resolves a current PtS-owned source association. The
server calls Content over HTTP with exact `pts`/application ownership and bounded
account/actor/operation attribution. Content checks its service policy, stored
owner, readiness and immutable provider representation. PtS never queries Content
tables or accepts browser provider locators/content IDs as authority. External
references remain explicit original links and do not become stored objects.

## Controlled release and recovery

1. Inventory and reconcile the selected PtS partition, all Content associations,
   global identifier collisions, finalized versions, source rights and sealed
   provider byte identities. Historical read-only inventory is evidence to recheck
   at activation, not indefinite readiness. Retain private locator/credential
   custody and publish only safe references/digests.
2. Verify restricted credentials and previous consumer compatibility. Provision
   successor roles through the reviewed owner bootstrap, never through runtime.
   Back up the selected target and record the explicit recovery point and release
   identifier. Coordinate or stop predecessor importers before incompatible work.
3. Run controlled owner migrations before activation. Content's closed adoption
   manifest must agree with an independently exported PtS association inventory.
   The migration owner verifies candidate bytes outside database locks and
   preserves content identity/history. Runtime cannot adopt or transfer ownership.
4. Supply `apps.pts.tools.bind_corpus` with the reviewed input under
   `PTS_MIGRATION_DATABASE_URL`: schema version, legacy partition UUID, executor
   actor UUID, inventory/snapshot hashes, release reference and exact table counts.
   A repeat with the same binding is unchanged; replacement or inventory drift is
   refused. Retain input and outcome with the release.
5. Assign explicit account grants through Access and verified account/actor
   ownership through Identity's existing operator procedures. Do not create a
   PtS organization, require membership, grant by email alone or infer document
   access from read/export. Preserve the previous running version until the
   coordinated activation checks pass.
6. Bind the dedicated file origin, exact frontend origin and certificate/SNI in
   the gateway configuration inputs. Match these against PtS runtime and
   `PUBLIC_PTS_FILE_ORIGIN`/web build inputs. Missing/mismatched inputs or migration
   failure block activation. Never route private bytes through a frontend proxy,
   relax cookie attributes or fall back to signed reads.

A failed migration keeps activation blocked. Reconcile actual owner revisions,
preserve applied migrations and correct forward with a new evidence/release
reference. Never automatically downgrade, reset retained data or reverse adoption.
Application startup performs no migration. Deliberate byte finalization recovery
belongs to the existing Content owner procedure and its stopped-executor evidence.

Successor canonical import has no organization argument:

```bash
apps/pts/.venv/bin/python -m apps.pts.tools.import_library --source apps/pts/reference/poetry-library/library.json
apps/pts/.venv/bin/python -m apps.pts.tools.upload_sources --library apps/pts/reference/poetry-library/library.json
```

Use the importer configuration example and explicit authorized actor; do not
source all environment catalogues into an API. Repeated imports preserve existing
values; conflicts retain incoming evidence and exit nonzero for deliberate review.

## Native file transport

The dedicated file hostname carries a host-only `__Host-pts-file` Secure,
HttpOnly, SameSite=Lax cookie containing only the existing short-lived access
credential. Exact-origin bearer-authenticated POST establishes/renews it; ambient
cookies, unknown origins, body identities and cross-site setup are refused. This
transport is qualified only for the selected same-site HTTPS layout.

Opaque file contexts bind account, actual provider session, application document,
presentation and expiration. They grant no authority. Every GET/HEAD/range checks
the current Identity session, exact Access capability, current PtS association and
Content ownership/readiness before metadata or bytes. Logout clears contexts and
confirms provider-local revocation before a completed switch. A delayed old
Set-Cookie response may overwrite the browser cookie, but cannot revive a revoked
session. Reopening from the app repairs current same-session transport safely.

Open uses the native PDF viewer where supported; Download uses the browser's
normal flow. Other media download. The app adds no viewer, download manager,
independent refresh owner, bearer URL or whole-file JavaScript buffer. Expiry or
denial never turns a binary response into successful login HTML; return to the
app and reopen after recovery. Delivered bytes cannot be recalled.

Supported requests are GET, HEAD and one bounded/open-ended/suffix range with
stable strong ETag and If-Range semantics. Private responses are no-store, nosniff
and allowlisted/sanitized. Before headers, typed errors permit safe retry; after
streaming starts, failure aborts incomplete bytes without appending JSON or
silently restarting. Both owner hops close resources on failure/disconnect.
Private errors also expose `X-PtS-Error-Code` for bodyless HEAD responses, through
the existing exact frontend-origin CORS policy. Typed failures keep the existing
JSON `detail.code`; structural validation uses `validation_failed` while retaining
its validation details. Database failures use `collection_unavailable`. The native
OpenAPI contract declares these headers without buffering binary responses.
Declared budgets: 1 MiB application buffers, 16 streams per API instance and two
per verified account; 5-second connect, 30-second upstream idle, 60-second gateway
idle and 15-minute whole-response ceiling. These are qualification inputs, not
measured RSS or a new business size limit.

## Evidence and impacts

Private attempt outputs live under `platform/deployment/.local/e1-pts-adoption/`.
Each fresh run needs the approved isolated target/guard, retained credential-role
custody and genuine provider baseline. Never access the prohibited KDG fixture.
`--phase owners` establishes only the owner-startup checkpoint. `acceptance` adds
real adoption/corpus/owner HTTP assertions. `browser` also exercises isolated TLS,
generated gateway policy, real Directory and the built frontend/native browser.
Its current owner matrix also exercises a genuine never-granted account, wrong
Content caller/application, an unrelated finalized object, associated pending
content and explicit external links. The TLS phase pauses only its fresh genuine
provider to verify the current-session HEAD deadline, typed outage and recovery.
Use a NEW output path and inspect result/cleanup/source bindings before claiming
its scope. Historical failed attempts remain unchanged.

`session-races` adds a real response-arrival gate after the owner has issued its
Set-Cookie response, genuine provider-local sign-out and a second account login.
It verifies the old cookie physically arrives, fails current-session enforcement,
and can be repaired by the current account's existing auth owner. A fresh provider
uses 60-second access credentials for the closed-app expiry case; ordinary fixture
phases keep the provider helper's existing 3600-second default.

`resources` adds the actual128MiB transfer at1MiB/s, sampled owned process trees
and TCP occupancy, two-per-account/sixteen-global admission and full reacquisition,
Storage idle failure, same-representation range recovery and bounded graceful
drain into a new process instance. A bounded HTTP reader can expose a truncated
response through a positive remaining declared Content-Length without raising an
exception; the fixture records actual received/remaining bytes and elapsed time
before judging incomplete transfer. Failed attempts remain failures.

`image-resources` preserves the previous bundle, packages from the frozen offline
Python3.15 lock, builds the PtS image and repeats this matrix as nonroot with a
read-only filesystem. A NEW resource or session-race fixture may instead use
`--runtime-image-binding` from an earlier image build: the driver verifies every
current bundle/source fingerprint and provenance digest, inspects the exact
immutable image ID/nonroot user, and creates a NEW container. It never restarts
a retained container. `image-session-races` uses the same image with a fresh
60-second provider for the separate expiry matrix. Other owners remain actual
source processes; the receipt must retain that limit.
The separate fresh `qualify_corpus` rehearsal includes
successor snapshot consistency, alternate-write FK checks and catalogue/attachment
conflict protection alongside migration, RLS, compatibility and import recovery.

Native PDF navigation requires headed Chromium on the isolated Xvfb display:
[Playwright documents that headless mode does not support PDF navigation](https://playwright.dev/docs/api/class-page#page-goto).
The earlier headless attempt5 establishes inline PDF response headers, matching
native downloaded bytes and cookie/logout behavior. It does not establish rendered
PDF viewer content. Attempt6 reached its expiry-viewer navigation but failed there;
its earlier assertions are not a completed session-race qualification. Keep these
limits distinct from subsequent headed viewer evidence and human device testing.

Source `resource-acceptance-attempt5` completed18named checks, including the full
128MiB/1MiB-per-second transfer in128.001s, digest verification, both account/global
capacity cycles, incomplete Storage failure in30.625s, authorized same-ETag range
recovery and bounded full graceful drain into a new process. The retained429
samples show single-stream growth below64MiB and all-phase growth below192MiB for
each measured owner. These are isolated workload observations, not production
capacity promises. New stream observations had no idle business transactions;
the final disconnect cleanup permits the measured bounded2s owned audit lifecycle.
The source session-race proof is `native-acceptance-attempt10`. Fresh
`image-resource-acceptance-attempt3` repeated the full resource/native matrix
against the verified frozen PtS image as UID65532/read-only, completing19named
checks,463samples and the same128.001s transfer. All measured single/concurrent
growth stayed below64/192MiB, both capacity cycles passed, incomplete upstream
failure ended within30.7s and a new image instance recovered authorized ranges
after complete graceful drain. Access/Identity, Content and Directory remained
actual source processes. Fresh `image-session-acceptance-attempt1` repeated the
declared delayed-cookie/logout/switch/repair/closed-app-expiry matrix with15named
checks against the same image. Its lack of an explicit provider-refresh assertion
was identified by the coordinator's matrix audit. Fresh
`image-session-acceptance-attempt3` closes that gap through the existing UI auth
owner: an actual provider refresh, same account/session and later expiry, then
real Sources Open with the exact refreshed setup credential/cookie and authorized
native GET/HEAD/range. It also repeats the full delayed-cookie/logout/switch/
closed-app-expiry matrix. Its 476 captured source bindings matched at that
pre-loopback closure; later loopback changes require their separate qualification.
Do not infer renewal from current-cookie repair or the long-lived resource fixture.

Fresh `migration-artifact-attempt2` separately built the migration image offline
and imported its frozen toolchain, migration entry point/binder/helpers and
three Alembic graphs as UID10001/read-only/network-none. No database or migration
command ran in that artifact smoke. The preceding actual interpreter-permission
failure led to assigning the existing migration user ownership of the frozen
Python/site-packages inputs while retaining their private modes. Source-native
database migration/recovery and migration-image importability are separate proofs.

Fresh `corpus-attempt-2` passed11native checks under restricted PostgreSQL roles,
including failed-upgrade rollback/retry, predecessor compatibility, exact selected
data/history/association preservation, cross-partition and privilege denials,
import concurrency, alternate-write foreign keys and consistent successor snapshots.
The corpus receipt binds44source files; later fixture custody-only changes are
recorded separately. The dispatch spec retains exact evidence/cleanup observations
and tracks outstanding coordinator audit/reviews. UI doubles and source processes
alone do not establish packaged-runtime qualification. Human mobile
devices and hosted configuration require their own observations.

All five delivery impacts remain explicit: scaffold promotion is limited to proven
neutral session/stream clients and fixtures; shared UI retains native Open/Download
and safe recovery; existing agent-context boundaries suffice; current owner docs
and Leave dependency evidence must record exact results and limits; accepted ADRs
remain unchanged. PtS corpus/storage policy stays application-owned.

## Loopback2 lifecycle/owner reclamation and historical proof — 2026-10-31

A fresh login or recovery can replace a provider session without changing account
ID. The existing auth owner verifies the new credential's account/session claims
before distinguishing that replacement from ordinary refresh. Original-session
cleanup remains mandatory before creating replacement file authority. Its durable
private browser record retains the original receipted bearer/latest recovery
rotation and the verified replacement credential/session separately. Cleanup may
refresh the original through the existing SDK; it preserves/restores the replacement
rather than treating temporary SDK storage replacement as the new login. Pending
cleanup remains visible after failure/reload; Retry Sign out completes the original
cleanup and resumes the preserved replacement. Recovery/password return context
stays bound to the same account. No second client, subscription or refresh loop is
introduced. Every actual setup/context/read still verifies current owners.

A genuine native recovery attempt exposed a further SDK ordering case: loading
stored credentials for original cleanup rotated the replacement twice while UI
transitions were held, then restored its older retained refresh pair. After the
provider reuse window, actual replacement renewal failed with
`refresh_token_already_used`. The existing sole auth callback now awaits trusted
explicit-token claim verification and a durable exact-replacement write during
cleanup. Temporary original-session notifications do not supersede that matching
rotation. A failed durable observation keeps cleanup pending rather than falling
through to original revocation and stale restoration. Confirmed original absence
cannot hide that stable replacement-custody failure: both cleanup owners still
receive attempts and the final absence check runs, then this one recovery error
remains visible. Ordinary failed revocation with exact absence keeps its existing
completion semantics. In automatic switching, this same stable observation failure
also preserves the newer pair already in SDK storage for verified reload/retry;
it must not restore the older durable pair over it. Other partial-order failures
retain existing restoration. Pending state still blocks replacement file authority.
This adds no subscription,
client, refresh owner or relaxed current-session authority. Current provider/browser
qualification is recorded above; failed receipts retain their original bindings.

PtS migration0003 adds a no-argument, fixed128-row expiry-reclamation routine. The
existing restricted PtS schema owner defines it; FORCE RLS limits its rows to
`expires_at <= clock_timestamp()`. PUBLIC has no execution permission; only the
successor runtime can execute it. Direct runtime SELECT/INSERT/DELETE retain the
exact account/session policies. Neither caller nor routine receives Content/Auth
access, a live-context selector or a new table privilege. An expiry index and
`FOR UPDATE SKIP LOCKED` bound each batch and permit concurrent retry.

Each already-authorized file-context creation invokes one batch in its own short
transaction, with a one-second statement deadline and100ms lock deadline, before
the exact-session insert. Active use drains departed-session expiry backlogs at
up to128rows per creation; another invocation retries remaining/skipped rows. No
background worker or claim of cleanup while the application is idle is introduced.
Failure is unavailable and retryable, never a widened file session. This routine
reclaims only expired PtS transport contexts, never Identity's immutable cleanup
receipts or live contexts. Ordinary controlled migration/release ordering applies;
0002's live-context consumer remains supported after the additive migration.

The existing ten-second corpus query timeout now precedes the initial singleton
binding SELECT. The consistent collection transaction and snapshot remain unchanged.
The native exclusive-lock check observes57014 within that budget, release to the
pool and subsequent usable connection. External owner checks remain outside local
business locks.

The native corpus fixture now executes the actual deployment adapter's PtS stage:
real Alembic success with no binding must retain complete=false/status=failed;
reviewed binding input must succeed and emit its inventory/release evidence. The
fixture isolates other owners and production-host validation explicitly; it does
not substitute a synthetic complete=true result. Identity30 remains a separately
controlled prerequisite. The native Content fixture additionally invokes the actual
successor upload/attach command for new pending synthetic bytes and ready replay,
checking finalized metadata, exact bytes/Content identity and one persisted PtS
association. Legacy adoption and upload mocks do not cover that case.

Current root-owned final native corpus qualification passed 16 checks in 19.001 seconds
on a NEW database,
including the exclusive-lock failure budget, adapter gate,0002→0003/repeat,260expired
departed-session contexts drained across fixed128-row batches, live foreign-row
preservation, direct scope denial and the earlier corpus/import invariants. The
final cases additionally prove native 42501 predecessor/importer routine-execution
denials and the 100 ms exclusive-table-lock deadline, pool release and retry. All
captured source stayed unchanged at closure; the fresh PostgreSQL container stopped0/noOOM.
Its native proof binds 48 files. The later synthetic-uploader title change affects
only `native_acceptance.py`, which the corpus qualifier records but does not execute;
all 47 other bindings still match. The evidence manifest links the exact one-line
preimage reconstruction instead of claiming a new corpus run. Exact
RED/GREEN commands, source hashes, logs and independent stopped0/noOOM audit are
under `platform/deployment/.local/e1-pts-adoption/review-loopback-2/`. These results
do not replace the separate current-image resource/session matrices. Cleanup5,
resources2 and session-races1 all passed as recorded above; coordinator audit and
independent reviews remain pending.
All prior receipts retain their original source/image bindings.

Five delivery impacts: the shared native-file HTTP transport remains unchanged;
session lifecycle and expiry storage policy stay with their existing owners. No
new scaffold/session engine or app-specific shared UI is promoted. Existing agent
instructions suffice; this runbook and Leave evidence record exact proof and limits.
Accepted ADRs are unchanged. Hosted activation and human-device observations remain
separate from this isolated implementation scope.

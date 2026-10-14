# Acceptance and device evidence plan

Planning evidence only: scenarios below are not executable tests and have not run.
Story links are assigned during BMAD epic confirmation/detailing. Before authorized
implementation, bmad-build must run the smallest relevant acceptance scenario and
observe its expected missing-behavior failure; focused TDD then affected suites follow.

## Requirement → acceptance boundary

| Test ID | Requirements | Observable scenario / expected outcome | Boundary |
| --- | --- | --- | --- |
| KDG-A01 | FR-1,2; NFR-1 | Sign-in resolves Khula only; wrong org, absent membership, disabled app/org, missing capability denied; no org switcher or People dependency | Auth/Access consumer contract + API + one browser journey |
| KDG-A02 | FR-2,8,12; NFR-1 | Capturer reads/edits own only, including after unassignment with current access; administrator creates for every active Khula child and reads/edits all within Khula; altered owner/org/role inputs rejected; admin preserves owner and records editor | API + actual runtime-role PostgreSQL/RLS |
| KDG-A03 | FR-3,11; NFR-5 | Targeted synthetic bootstrap yields exact child/version/assignment; same replay no duplicate, wrong operator/target rejected; partial-owner recovery | Owner command integration |
| KDG-A04 | FR-4,13,16 | Provision installed app online, disconnect, cold reopen offline within window; questionnaire/child available; missing initial setup blocks | Browser + Android/iPhone physical |
| KDG-A05 | FR-5; NFR-3 | Rating 1/5 labels exact, integer five options, no initial selection, 0/6/fractions rejected; Nee initially selected; Ja shows details; toggles retain editing buffer, false saves no details; required rating/text validation | Component + API |
| KDG-A06 | FR-6 | Editable observation date independent of timestamps; two child/date captures accepted; local known prompt Edit/Add, unavailable server duplicates not claimed | Domain/API + component |
| KDG-A07 | FR-7,13,15; NFR-2 | Offline Save acknowledged only after local transaction; close/reopen shows same capture+pending operation; no unfinished-input recovery promised; hidden in-memory buffers excluded from saved answers | IndexedDB real-browser integration |
| KDG-A08 | FR-7; NFR-2,3 | Explicit Save failure/unknown outcome keeps visible input with useful guidance; resolve original attempt; no false saved status or unfinished-entry persistence | Component + browser controlled storage |
| KDG-A09 | FR-14,15; NFR-2 | Server commits then connection drops; same operation lookup/retry returns one effect/history/receipt; changed payload ID reuse rejected; concurrent duplicate sends safe | API/DB + browser fault injection |
| KDG-A10 | FR-8,14 | Offline create and successive edits queue in order; interrupted drainer recovered; two tabs cannot corrupt claims; old ack/download never overwrites later local edit | IndexedDB/browser + API |
| KDG-A11 | FR-8,9; NFR-2 | Facilitator and administrator edit same base revision; one commits, other conflicts with local/base/server retained; explicit resolution, repeated conflict, descendants paused for re-review | Concurrent API/DB + browser review |
| KDG-A12 | FR-10,11 | Publish V2 while phone offline on V1; V1 capture sync accepted; open form remains V1; next new capture after download V2; history edit uses V1 exact label/scale | API contract + browser version fixtures |
| KDG-A13 | FR-10,12 | Capturer admin APIs denied; admin Save/Cancel no partial writes, Publish immutable; reorder/retire/type-ID rules; assignment does not grant access | API/domain/component |
| KDG-A14 | FR-1,2,13,17; NFR-1 | User/org partitions, unauthorized direct UUID, pooled transaction after rollback, late response after account switch; no prior-user data rendered/submitted | Real runtime DB roles + browser |
| KDG-A15 | FR-16,17 | Token expiry inside 7-day local window permits local use but fresh server auth required; exact window expiry/logout/known denial locks; different-account login sees no pending data; same account reauth recovers | Fake clock + browser/auth integration |
| KDG-A16 | FR-12,16 | Membership/grant removed while phone offline; device cannot know; next affected sync denied and proposal retained. Unassignment denies capturer new creates, retains own history, and does not deny admin create-all; unrelated success cannot renew old stronger cached capability | Access contract + API/browser |
| KDG-A17 | FR-18; NFR-2,5 | Quota abort never Saved; failed/interrupted local migration retains pending captures/actions/conflicts; new shell update does not reload unsaved form; old queue payload supported | Browser fault/update fixtures |
| KDG-A18 | FR-8,13,18 | Partial/approved 30-day download labeled, never-downloaded history unavailable; refresh retains pending overlay; prune acknowledged cache only, keep referenced versions | API pagination + IndexedDB/browser |
| KDG-A19 | FR-4,5,7,9,10; NFR-3 | Keyboard, focus, radios, details expansion, Retry and resolution accessible; 320px/zoom/touch; screen reader save/local/synced announcements | Automated accessibility + physical AT |
| KDG-A20 | FR-14,15,18; NFR-4 | Open/resume/reconnect/manual each attempt sync; server unavailable yields bounded retry/state; other records continue around attention item | Fake-clock queue + real browser |
| KDG-A21 | FR-2,8; NFR-1 | Spoof author rejected; server UTC attribution preserved; device capture time separately labeled; revisions immutable; injected sensitive text absent from diagnostics/error adapters | API/DB/log-safety fixtures |
| KDG-A22 | NFR-5 | Disposable upgrade/prior-version behavior, failed migration blocks activation, explicit recovery, queue compatibility | Existing release-tooling integration + KDG migration tests |

## Requirement → story linkage in progress

All 19 stories are approved. E1–E4 planning closure is approved; E5 completion and
final BMAD validation remain pending. Each requirement is allocated to explicit story
scopes; pilot-wide evidence in 5.4 complements rather than replaces feature tests.
Scenario detail and intended boundaries are in the linked draft; no tests have run.

| Story | Requirements / UX | Acceptance tests | Status |
| --- | --- | --- | --- |
| [1.1 authorized entry](epics.md#story-11-sign-in-and-enter-the-authorized-khula-context) | FR-1; entry FR-2/4; NFR-1/3/4; UX-DR1/2/7/12/13 | KDG-A01.entry-allowed/entry-denied, A14.entry-scope, A15.entry-return, A19.entry-accessible | Planning-approved; shared prerequisites unresolved |
| [1.2 initial questionnaire](epics.md#story-12-provision-and-retrieve-the-initial-published-questionnaire) | FR-3 questionnaire setup, FR-5 definition, FR-11 initial immutable version; read FR-1/2; NFR-1/2/5 | KDG-A03.questionnaire-initial/operator-denied/replay, A12.questionnaire-immutable, A01.questionnaire-read, A14.version-scope, A21.questionnaire-attribution | Planning-approved; owner-write/operator prerequisites unresolved |
| [1.3 initial child/assignment](epics.md#story-13-provision-the-initial-child-and-facilitator-assignment) | Child/assignment FR-3/12, scope FR-1/2, eligible-choice FR-4; NFR-1/2/5 | KDG-A03.child-assignment-initial/replay, A02.child-eligibility, A14.assignment-target-scope, A16.assignment-authority, A21.assignment-attribution | Planning-approved; owner target-verification contract unresolved |
| [1.4 installed offline setup](epics.md#story-14-install-kdg-capture-and-provision-authorized-setup-for-offline-opening) | FR-4/13, setup FR-16/17/18, scope FR-1/2; NFR-1–5; UX-DR1/2/4/7/11–14 | KDG-A04.setup-offline-open, A07.setup-local-commit, A15.setup-window, A14.setup-partition, A16.setup-scoped-renewal, A17.setup-storage-update, A19.setup-accessible | Planning-approved; setup DTO/PWA toolchain/device validation pending |
| [1.5 explicit local Save](epics.md#story-15-explicitly-save-an-observation-on-this-phone) | FR-4–7/13/15, local FR-8/14/16–18; NFR-1–5; UX-DR2–8/11–13 | A05.form-answers, A06.same-day-captures, A07.saved-capture-reopen, A08.explicit-save-failure, A09.local-repeat-save, A14.capture-partition, A15.capture-window, A17.capture-storage-update, A19.capture-accessible | Planning-approved; local command/schema delivery gates remain |
| [1.6 create synchronization](epics.md#story-16-synchronize-a-saved-capture-and-view-its-server-backed-record) | FR-1/2/11/14–17; initial server FR-8; NFR-1/2/4/5; UX-DR4/7/8/11/13 | A09.create-replay/lost-response, A20.foreground-sync, A10.create-claim-recovery, A02.create-authority, A14.server-capture-scope, A15.sync-reauth, A16.create-rejected, A12.create-original-version, A21.server-attribution/logs, A22.queue-release-compatibility | Planning-approved; create/outcome/read/fingerprint schema validation pending |
| [1.7 installed first-slice proof](epics.md#story-17-prove-the-first-capture-slice-on-installed-android-and-iphone-pwas) | UJ-1/E1 create-read scope; NFR-1–5; UX-DR12–14 | A01/02/04–09/14–17/19–22 in E1 scope; actual installed Android/iPhone protocol | Planning-approved; physical delivery/run evidence not executed |
| [2.1 own history](epics.md#story-21-browse-my-capture-history-online-and-offline) | FR-2/8/11/13, history FR-15–18; NFR-1–4; UX-DR4/7/8/11–13 | A18.history-window/partial/reconcile, A08.history-storage-failure, A14.history-owner-scope, A15.history-read-window, A16.history-unassignment, A12.history-original-version, A19.history-accessible | Planning-approved; history/cursor/cache DTO validation pending |
| [2.2 own editing](epics.md#story-22-edit-my-captures-offline-and-synchronize-explicit-changes-safely) | FR-2/6–9/11/14, scoped FR-13/15–18; NFR-1–5; UX-DR5/7/8/9/11–13 | A02.own-edit, A10.edit-order/reopen, A09.edit-replay/lost-response, A11.own-revision-conflict, A12.edit-original-version, A16.edit-after-unassignment, A14.edit-owner-scope, A15.edit-window, A21.edit-attribution, A19.edit-accessible | Approved scope/A-6; concrete edit DTO/schema/queue/permission fixtures gate Build |
| [2.3 own conflict resolution](epics.md#story-23-review-and-explicitly-resolve-conflicting-saved-changes) | FR-2/8/9/11/14/15, scoped FR-13/16–18; NFR-1–4; UX-DR4/5/7/8/9/11–13 | A11.own-conflict-use-current/replacement/intervening/descendants, A09.resolution-lost-response, A10.resolution-local-cas, A14.resolution-owner, A15.resolution-session, A12.resolution-original-version, A19.resolution-accessible | Approved scope; concrete resolution/retention fixtures gate Build |
| [2.4 simple history and E2 proof](epics.md#story-24-prove-simple-offline-capture-history-and-editing) | FR-8/9/11; E2 FR-2/6/13–18; NFR-1–5; UX-DR4/7–9/11–14 | A21.detail-attribution/immutable-evidence, A14.detail-owner-scope, A18.current-record-cache, A12.detail-original-definition, A15.detail-read-window, A09/10/11/16/17/19 E2 integration; installed Android/iPhone extension | Approved simplified scope; no revision-browser/archive; existing record/queue contracts and device evidence gate delivery |
| [3.1 administrator history/audit](epics.md#story-31-view-authorized-khula-observations-and-administrator-audit-details) | Admin FR-2/8, FR-11/13/15–17; NFR-1–4; UX-DR4/7/8/10–13 | A02.admin-read/own-denied, A14.admin-read-org/account, A15.admin-online-session, A16.admin-read-role-loss, A18.admin-history-partial, A12.admin-original-definition, A21.admin-audit-attribution, A19.admin-review-accessible | Approved online-only scope; current all-read/actor-display/audit DTO fixtures gate Build |
| [3.2 online administrator editing](epics.md#story-32-correct-authorized-observations-online-without-overwriting-another-editor) | FR-2/8/9/11/15–17; NFR-1–5; UX-DR5/7/8/9/10/12/13 | A02.admin-edit, A11.facilitator-admin-both-orders/repeated, A09.admin-lost-response/replay, A14.admin-edit-org/account, A15.admin-edit-session, A16.admin-edit-role-loss, A12.admin-edit-original, A21.admin-owner/editor, A17.no-all-record-offline-cache, A19.admin-edit-accessible | Approved in-memory scope; all-edit/conflict/outcome fixtures gate Build; no conflict drafts |
| [4.1 questionnaire draft editor](epics.md#story-41-edit-and-save-a-questionnaire-draft-online) | FR-10; draft/stable-ID FR-11; editor FR-5/2/12/16/17; NFR-1–5; UX-DR5/7/10/12/13 | A13.editor-role/Save-Cancel/reorder-retire-types, A12.editor-stable-IDs/published-unchanged, A09.editor-save-replay, A11.editor-concurrent-save, A14.editor-org/account, A15.editor-session, A21.editor-attribution, A19.editor-accessible-reorder | Approved scope; working-draft lifecycle/limits/DTO fixtures gate Build |
| [4.2 publish/version compatibility](epics.md#story-42-publish-a-questionnaire-without-changing-older-observations) | FR-10/11; scoped FR-2/5/8/9/13/14/16–18; NFR-1–5; UX-DR5/7/10–14 | A13.publish-role/immutable/lifecycle, A12.actual-publish-offline-V1/open-pinned/new-V2/historical-edit, A09.publish-replay/lost-response, A11.publish-concurrency, A14.publish-org/account, A15.publish-session, A17.version-retention-upgrade, A21.publish-attribution, A19.published-controls-accessible; actual installed Android/iPhone | Approved scope; publication lifecycle/DTO and actual producer/consumer/device proof gate delivery |
| [5.1 child management](epics.md#story-51-manage-children-online-without-losing-their-observations) | Child FR-12; scoped FR-2/4/8/13/16; NFR-1–5; UX-DR2/7/10–13 | A13.child-manage-role/Save-Cancel, A02.child-admin-create-all, A16.child-inactive-pending-accepted/historical-edit/reactivate, A09.child-replay/lost-response, A11.child-concurrent-save, A14.child-org/account, A21.child-attribution, A19.child-admin-accessible | Approved revised policy; child-management/prior-eligibility DTO and coordination fixtures gate Build |
| [5.2 facilitator assignments](epics.md#story-52-assign-children-to-verified-facilitators-online) | FR-12; scoped FR-2/3/4/8/13/16/17; NFR-1–5; UX-DR2/7/10–13 | A13.assignment-manage-role/Save-Cancel, A03.assignment-target-verification, A16.assignment-added/removed/rejoin-renewal, A02.assignment-no-grant/admin-create-all, A09.assignment-replay/lost-response, A11.assignment-concurrent-save, A14.assignment-org/account, A21.assignment-attribution, A19.assignment-admin-accessible | Approved renewal policy; shared target/lifecycle contract closure gates Build |
| [5.3 storage/update reliability](epics.md#story-53-protect-saved-observations-through-storage-failures-and-app-updates) | FR-18; reliability FR-7/8/13–17; NFR-1–5; UX-DR4/7/8/9/11–14 | A08.quota-transaction-recovery, A17.failed/interrupted-local-migration/deferred-update/pending-upgrade, A09/10 upgrade delivery, A12.original-definition, A14.partition, A15.session, A18.disposable-cache-only, A21.storage-log-safety, A22.release-payload-compatibility; installed Android/iPhone updates | Approved update-first scope; supported schema/build/payload pairs and fault/device fixtures gate delivery |
| [5.4 controlled pilot readiness](epics.md#story-54-verify-the-complete-workflow-and-prepare-a-controlled-khula-pilot) | FR-1–18 integrated evidence; operating FR-16–18; NFR-1–5; UX-DR1–14 approved scope | A01–A22 story-linked evidence; emphasized A14/15/16/17/21/22; final installed Android/iPhone and release recovery | Approved scope; named Khula operating policies and real delivery/device/dependency evidence gate pilot |

Full completeness/sizing/consistency validation remains pending. Approved Story 1.1
covers online entry/return only, not complete offline expiry/account partition behavior.

## Shared tests, separately owned

Platform owners retain P-AUTH: verified token/current membership and typed scope denial;
P-ACTOR: durable account/service actors and attribution mapping; P-ACCESS: org/app/grant
admission, revocation/outage, scope-specific consumer schemas; P-SCAFFOLD: invalid recipe,
non-destructive generation, extension preservation, generated install/type-check/build/API;
P-WRITE: tenant context/RLS/pool reuse, atomic operation/revision/audit, restricted authority;
P-RELEASE: dependency ordering/migration failure/activation block/recovery; P-ERROR:
safe framework envelopes/legacy adapters; P-SESSION: same-user validated return.

First-consumer offline additions: P-OFFLINE transaction/claim/version fixtures;
P-UPDATE prompt/connection/migration compatibility; P-STATUS accessible local/remote/error
states; P-DEVICE generic disconnect/reopen/resume/lost-response utilities. KDG-A scenarios
remain KDG-owned even when they consume shared helpers. Do not put questionnaire wording,
child assignment or administrator capture semantics into shared test libraries.

## Physical device protocol — execute only after planning approval

Early proof precedes full editor/history build. Use synthetic child/answers/accounts on
an isolated reachable HTTPS environment; no real child record in screenshots/traces.
Record exact device model, OS/browser version, installed/tab mode, app/API/service builds,
test ID, date, outcome and safe operation IDs. Playwright WebKit emulation is not an
iPhone installed PWA result; desktop Chromium emulation is not Android installation.

### Early E1 protocol — required installed-device proof

On Android Chrome and iPhone Safari home-screen PWAs, inside each installed context:

1. Sign in and complete setup; verify fixed Khula/current access/eligible child/version.
2. Disconnect, fully close/reopen, enter the form and explicitly Save; verify local status.
3. Fully close/reopen offline and read that saved capture's local details and pending state.
4. Reconnect/resume/Sync now; read the same server-backed record through normal authorized API.
5. Lose response after commit, interrupt/retry and verify one capture/revision/receipt.
6. Record same-account reauthentication and pending-work logout/different-account isolation;
   automated controlled clocks prove seven-day expiry, with physical scope clearly labeled.
7. Apply a nonproduction deferred shell update with a pending create and prove retained
   IDs/version/local record; quota/migration failures use controlled browser/DB fixtures.
8. Check TalkBack/VoiceOver, keyboard/safe-area, text zoom and Ja/Nee/details behavior.

### Later feature extensions — not E1 dependencies

- E2: offline existing-capture edits, ordered create/edit chains, original-version history,
  30-day downloads and local/base/server resolution.
- E3: organization-wide administrator reads/edits and facilitator/admin conflicts.
- E4: actual editor publication while a phone remains offline, new-entry vs open-form version
  selection and historical editing under earlier definitions.
- E5: normal assignments/onboarding changes and full app/schema/pilot reliability protocol.

Re-use the same actual KDG app/fixtures/helpers and extend scenario assertions in those
consuming stories. Earlier isolated typed version/fault fixtures prove only their named
consumer boundary, not an editor/portal that has not been delivered.

Document unsupported/private browsing and normal uninstall/clear-site-data risk without
claiming a save can survive deletion. Power-loss/filesystem durability is best effort;
the normal close/reopen proof does not establish a guaranteed backup.

## Commands and evidence

Executed during planning: git status, read-only rg/source reads, BMAD configuration
resolvers, memlog.py, architecture lint and document checks recorded in readiness.
No application tests, migrations or dependency installation executed. There is no KDG
package yet, so no runnable test command is invented. Delivery owns exact test commands
after the shared generator/environment exists. Root npm build/dev are not valid repo
verification. Runtime source checks were not used as evidence that deployed Auth works.

For each built story, append requirement/story/test ID, initial failing command/result,
focused passing command/result, affected acceptance/contract suites, device protocol
result where applicable, and remaining limitation. Planned/scaffold-only/skipped/manual
checks must never be reported as automated passing evidence.

Scope amendment, 2026-10-13: unfinished observation autosave/close/crash recovery and
draft-specific flush/merge tests are removed. Explicit failed/uncertain Save and completed
capture durability remain. Questionnaire configuration draft/version tests remain required.

Engineering refinement fixtures: A05 rejects rating 0/6/fractions and U+0000 without
normalizing input; A09 proves canonical key-order equality/changed-content mismatch,
no-op receipts and concurrent duplicates; A14 operation command discriminator and
foreign eligibility references; A16 verifies ordinary-inactivity pending sync; A18
checks scoped cursors; A17 proves update-first and supported schema/payload migration.
These remain planned tests, not executed software verification.


## Successor shared-contract fixtures — 2026-10-14

[Shared prerequisite acceptance](shared-prerequisites.md) references existing owner
items, not runnable KDG tests. A01/A02 consume exact organization own_account/all-org
checks with account actor/no person, explicit capabilities/read.own entry and fixed-org
caller binding. A03 covers target membership replacement, restricted setup identity,
wrong session_user/runtime credential and partial owner outcome recovery. A14/A16 cover
retired/rejoined membership with no old assignment/eligibility resurrection; renewed
current own-read/edit remains tied to the same original account. A09 adds full JCS/HMAC
canonical retry, independent key identity, overlap/rotation/rollback/restore and fail-closed
missing verification key. A17 update-first protection remains; unchanged formats need
no adapters. See owning shared/fingerprint contracts for exact selected models.

Owners run the smallest relevant failing acceptance before implementation, then focused
unit/contract suites and affected browser/device checks. Exact commands/results and
requirement-to-test cases land with existing owner/consuming delivery items; no new
passing test or generated OpenAPI/client is inferred from these fixture declarations.

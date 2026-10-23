---
title: 'Create, write and reopen personal Studies'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'a0436ea675145f2449645eeb2849d90c837e8882'
context:
  - '{project-root}/apps/scribeswell/docs/PERSONAL_NOTES_V1.md'
  - '{project-root}/services/access/STUDIES-ENROLLMENT.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Studies has wire contracts but no create/write/reopen journey. Access enrollment/current personal authority are now delivered by f02bf84b1a3d3281fb06e91aba01f0057216511c.

**Approach:** Deliver explicit enrollment, study creation, ordinary note autosave and reopening persisted text through the agreed Studies/Analysis surfaces.

## Boundaries & Constraints

**Always:** Preserve public reading, standalone signup, dirty work, UX and ADRs. Check Access over HTTP before local locks on every protected request. Use existing DTO/saving bounds, ATDD/TDD and native isolation/concurrency tests. Production stays disabled pending migration/integration qualification.

**Never:** Implement Access/Identity, Leave or app factory; import owner code/tables; auto-enroll on signup/read; deploy or mutate real/retained environments. References/highlights, sharing/private responses, copy/delete/search and expanded workspace tabs remain later slices; reject unsupported richer values.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Verified reader explicitly starts a study | Enroll through Access; create supplied or atomically allocated Untitled study; create no study on registration alone. |
| Note edited/reopened | Preserve Hebrew, direction, paragraphs/lists/marks/safe links; persist the aggregate/revision. Draft saved acknowledges only current input. |
| Response lost / same operation retried | Resolve original operation; block later snapshots while unknown; never infer rollback or create duplicates. |
| Stale revision, closed resource or changed operation payload | Refuse overwrite/resurrection; retain current input and safe conflict state. |
| Save fails / editor is exited | Inline Changes not saved / Retry; exit-only Stay / Close anyway, switching Stay / Switch anyway. |
| Account changes or access fails | Invalidate late responses, clear prior-account private state; keep public reading usable. |

</frozen-after-approval>

## Code Map

`A=apps/scribeswell`, `B=A/backend`, `W=A/web/src`; expand these path prefixes.
Existing note DTO/exporter owns wire; Access runbook owns authorization/errors.
`B/main.py` currently exposes validation input: contain private errors separately.
`W/pages/ReaderPage.tsx` and `components/bible/WordStudy.tsx` own reader/analysis;
`W/context/AuthContext.tsx` and `components/layout/Topbar.tsx` own sessions/sign-out.
Corpus history stays unchanged; a separate app-owned private history shares its release entry.

## Tasks & Acceptance

- [x] `A/tests/test_personal_notes_api.py`, `A/web/tests/personal-notes.spec.cjs`: observe journey acceptance failure first.
- [x] `B/{personal_notes_access,personal_notes_router,personal_notes_contract}.py`: bounded Access client, explicit `/api/studies/enrollment` proxy and note routes; exact response binding, safe codes/no-store errors. Server-only credentials.
- [x] `A/studies-alembic.ini`, `A/studies-migrations/{env.py,versions/0001_personal_notes.py}`, `A/tools/sql/prepare_personal_notes_roles.sql`: private study/note/receipt tables, structural account scope, FORCE RLS, immutable attribution/receipts and restricted roles; no foreign-owner FKs.
- [x] `A/tools/sync_personal_notes_database.mjs`, `A/studies-database-tools/`: consume existing builder installer/templates for migration helper/tests; never hand-edit managed outputs.
- [x] `B/{personal_notes_storage,personal_notes_cursor}.py`: bounded async transactions, title/operation serialization, parent-before-child locks, revision/lifecycle/no-op checks, atomic receipts and owner-bound cursors.
- [x] `W/lib/personal-notes.ts`, `W/context/StudiesContext.tsx`, `W/components/studies/{StudiesPanel,NoteEditor}.tsx`, `W/App.tsx`, mapped reader/auth surfaces: typed client, structured editor, account/note save lane, IME, responsive outline/reopen and guarded exits. No private-body browser cache.
- [x] `A/tests/test_personal_notes_storage.py`, `A/studies-migrations/tests/qualify_personal_notes.py`: native restricted identities, upgrade/repeat/failure/retry, isolation/concurrency/no-op, stale/closed writes, unknown commit and public-reader compatibility.
- [x] `A/deployment/{manifest.json,migrate.py,Migrations.Dockerfile}`, `platform/deployment/{registry.json,release.py,host-release.py}`, their tests: opt-in configuration/routes, ordered migrations, failure-blocked activation and forward recovery.
- [x] `A/tools/py/export_personal_notes_contract.py`, generated contracts/client, `A/docs/PERSONAL_NOTES_V1.md`, canonical companions: synchronize wire, actual behavior and evidence.

Given native storage, when the browser journey reloads, then saved content returns.
Given another account or revoked authority, when any private read/write/lookup executes,
then it discloses nothing and has no unauthorized effect. Given migration failure,
when release runs, then activation remains blocked and acknowledged data survives recovery.

## Implementation Notes

- User `next` approved the complete dispatch spec; frozen intent unchanged. Baseline captured before runtime edits. Existing dirty/concurrent work remains excluded. No live activation or retained-resource mutation authorized.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Route | Evidence |
| --- | --- | --- | --- |
| Blind 1 | medium | patch | openNote reuses the Map lane after leave; confirmed conflict input remains cached. Explicit confirmed discard must evict it before reading latest. |
| Blind 2 | medium | patch | create retains creation.current after definite input-invalid; a corrected title resends the same rejected payload. |
| Blind 3 | medium | patch | openStudy/openNote validate only account epoch; reversed same-account responses can override the later selection. |
| Blind 4 | medium | patch | moreNotes appends without comparing the captured parent/cursor and permits concurrent duplicate page reads. |
| Blind 5 | medium | patch | exit loops while composing; flush immediately resolves and the microtask loop starves composition until its deadline. |
| Blind 6 | medium | patch | inlines unconditionally continues for BR; supported Shift+Enter text is silently concatenated. |
| Blind 7 | medium | patch | NoteEditor note-ID effect resets only invalid/draw; link URL, range and direction remain from the prior note. |
| Blind 8 | medium | patch | safeUrl accepts underscore DNS labels while normative _url rejects them; align that direct validation check and preserve correction. |
| Blind 9 | medium | patch | call_next exception bypasses response header handling and reaches generic outer 500; contain private exceptions at the existing boundary. |
| Blind 10 | false | reject | notes.id already has CHECK(id<>zero UUID) on its CREATE TABLE first column; alternate zero-note insert is rejected. |
| Edge 1 | medium | patch | Same confirmed invalid-title frozen-attempt defect as Blind 2. |
| Edge 2 | medium | patch | Same confirmed cached conflict recovery defect as Blind 1. |
| Edge 3 | medium | patch | Same unconditional BR omission as Blind 6. |
| Edge 4 | medium | patch | Same unbound pagination parent/cursor response as Blind 4. |
| Edge 5 | medium | patch | Same immediately resolving composition-exit loop as Blind 5. |
| Verification 1 | medium | patch | Pre-verified: route-only fixture never installs main middleware; add enabled mounted application error cases. |
| Verification 2 | medium | patch | Pre-verified: only check adapter has negative responses; add enrollment operation/status/permission/identifier rejection tests. |
| Verification other 1 | medium | patch | Confirmed cached-conflict defect as Blind 1; reopening has no fresh GET when lane exists. |

All surviving groups are direct corrections at demonstrated existing states; no public surface or intent/spec change is needed. Duplicate claims are retained above before grouping.

### Review patch evidence

All eleven surviving root-cause groups were patched by the original implementation
agent; the eighteen individual findings above remain independently recorded. No
findings were deferred. The nil-note-ID claim was disproved by the existing SQL CHECK.
Parent inspection confirmed corrected-title attempts reset only after definite input
rejection, explicit conflict discard evicts the stale lane while Stay retains input,
resource responses bind to navigation/parent/cursor, pending pages deduplicate, IME
exit uses the existing prompt, and meaningful BR becomes supported newline text.
Transient note controls reset; hostname/link-selection checks give local correction.
Mounted private unexpected failures now use the safe503/no-store envelope while the
public500 behavior remains unchanged. Negative enrollment acknowledgements are refused.

Targeted patch commands: `P -m pytest apps/scribeswell/tests/test_personal_notes_api.py -q`
passed5; `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'review:' --workers=2`
passed18 desktop/mobile cases18.7s. Logs: `/tmp/scribeswell-notes-review-api.log`,
`/tmp/scribeswell-notes-review-browser.log`. The first added browser run had12passes4failures
from duplicate fixture notes and a GET-only fixture intercepting PUT; fixtures were
corrected without weakening assertions. `/tmp/scribeswell-notes-review-initial-summary.txt`
retains this chronology; no pre-patch behavioral red is claimed for these review additions.
The refreshed250941byte scoped diff excludes unrelated initial/concurrent work and the
claims artifact, which only the edge reviewer received. Parent audited the actual
implementation and patched test bodies; frozen intent matches its approval snapshot.

## Design Notes

No human intent gaps. Broad footprint requires dispatch. Only isolated synthetic migrations are planned. Dedicated migrator owns the private schema; runtime/importer lack DDL/ledger/owner rights. No catalogue fingerprint framework.

Scaffold: consume helper, no engine change. Shared UI: promote only proven neutral saving pieces. Agent context/ADRs: unchanged. Docs distinguish native, intercepted and physical-device evidence.

## Verification

Run focused pytest/native qualification before affected regression. Run `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs`, retained reader/account/session suites, app build, generated checks, composition dry-run and deployment tests. Record exact commands/results. Intercepted browser tests do not prove SQL/Access. Physical devices, live activation and owner verification limits remain open.


### Implementation handoff — 2026-10-23

Implementation is ready for the parent agent's independent diff/acceptance audit and
review. Frozen intent, baseline commit and unrelated dirty work are preserved.
Production/host activation remains refused. No deployment or retained-environment
migration was run. Canonical companion updates are append-only working-tree evidence;
the parent will reconcile them through bmad-spec before finalization.

**Observed reds:** Before behavior implementation,
`python3 -m pytest apps/scribeswell/tests/test_personal_notes_api.py -q` failed
collection with missing `personal_notes_router` (TDD/collection red, not HTTP proof).
The repository `.venv` lacked pytest. Before UI implementation,
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --project=desktop`
failed waiting for the absent Studies button. TestClient stalls inside the process
sandbox were resolved by running unchanged tests through the existing qualified
interpreter outside that sandbox; no test transport was substituted to hide the stall.

**Pre-review implementation-source verification:** `P` below is
`/tmp/scribeswell-host-tests-312/bin/python`. Native admin URLs identify only the newly
owned disposable fixture, not retained or real environments. Logs are temporary local
evidence, not release-readiness artifacts.

| Command | Result / retained log |
| --- | --- |
| `P -m pytest apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_release.py apps/scribeswell/tests/test_reader_integrity.py platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_host_profiles.py -q` | 204 passed, 49 subtests; `/tmp/scribeswell-notes-python-final.log` |
| `SCRIBESWELL_NOTES_TEST_ADMIN_URL=postgresql://postgres@127.0.0.1:32768/postgres SCRIBESWELL_NOTES_BROWSER_QUALIFY=true P apps/scribeswell/studies-migrations/tests/qualify_personal_notes.py` | 10 passed, no skips; `/tmp/scribeswell-notes-native-final.log`. Includes one desktop browser scenario over real HTTP/private SQL, synthetic Access-owner HTTP and intercepted public corpus. |
| `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs reader.spec.cjs account-entry.spec.cjs lexicon.spec.cjs --workers=2` | 188 passed; 2 optional native browser cases skipped in this intercepted run; `/tmp/scribeswell-notes-browser-final.log`. Native desktop case ran/passed separately above; native mobile and physical devices are not claimed. |
| `npm exec --workspace=apps/scribeswell/web -- playwright test --config playwright.session.config.cjs` | 12 passed; `/tmp/scribeswell-notes-session-final.log` |
| `npm run build --workspace=apps/scribeswell/web` | Passed; existing >500kB bundle warning; `/tmp/scribeswell-notes-build-final.log` |
| `P apps/scribeswell/tools/py/export_personal_notes_contract.py --check`; `node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs --check`; `P apps/scribeswell/studies-database-tools/test_owned_migration.py` | Passed; shared helper 11 tests; `/tmp/scribeswell-notes-tools-final.log` |
| Existing qualified Node26.11.1 API-client CLI `--schema /home/ck/repos/innodat/agriplatform/apps/scribeswell/contracts/personal-notes-v1.openapi.json --output /home/ck/repos/innodat/agriplatform/apps/scribeswell/web/src/generated/personal-notes --check` | `api_client_current`; `/tmp/scribeswell-notes-generated-final.log`. Executable: `platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`; source-identical retained CLI/dependencies: `platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs`. No dependency baseline changed. |
| `python3 tools/py/run_compose_supabase.py --check-only` | Passed, no changes; `/tmp/scribeswell-notes-compose-final.log` |
| `git diff --check` | Passed. No root build/test claim. |

**Matrix and acceptance traceability:** browser names below are in
`apps/scribeswell/web/tests/personal-notes.spec.cjs`; native names are in
`apps/scribeswell/tests/test_personal_notes_storage.py`. Every listed covering test
ran/passed in the corresponding current-source command above.

| Frozen row / acceptance | Covering executable evidence |
| --- | --- |
| Explicit verified enrollment/create; registration creates nothing | `explicitly enroll, create, write Hebrew and reopen saved text after reload`; retained account `session signup updates shared storage without protected requests`; API `test_explicit_create_current_authority_safe_error_and_no_store`; native `test_concurrent_default_titles_and_same_operation`. |
| Unicode/direction/paragraphs/lists/marks/safe links; acknowledge current generation only | `editor toolbar actions persist direction marks lists and safe links` uses real controls and reload; `rich paragraphs directions lists marks and safe links survive saving and reopening`; `delayed old acknowledgement cannot mark newer text saved`; `composition defers autosave until IME completion`; native `test_native_create_write_reopen_noop_replay_and_isolation`. |
| Lost response, same operation, no duplicates/later snapshots | `unknown response blocks newer snapshots and recovers the original operation`; native `test_native_unknown_commit_outcome_resolves_same_receipt`, `test_native_receipt_survives_lost_response_and_scope_constraints`, `test_concurrent_default_titles_and_same_operation`. The commit-loss test commits to PostgreSQL, injects the lost commit response, then resolves the original receipt. |
| Stale/closed/changed-payload refuses overwrite/resurrection, retaining input | `revision conflict preserves input and guards study switching`; native `test_native_create_write_reopen_noop_replay_and_isolation`, `test_native_restricted_roles_constraints_and_closed_resource`, `test_native_revision_race_and_deadline`. Race proves exactly one revision2 acknowledgement and one conflict. |
| Inline Retry and exit-only guards, including saved immediate close | `failed saves use inline Retry and exit-only Stay / Close anyway`; `revision conflict preserves input and guards study switching`; `unsupported current editor input stays unsaved and exit guarded until corrected`. |
| Account/access failure clears prior private state, public usable | `account replacement discards prior private UI and late saves`; both `account replacement clears local study title input` / `...link URL input`; `same-account reauthentication preserves input and requires explicit retry`; API `test_authentication_denial_happens_before_storage_and_input_is_never_echoed`; native owner read/list/lookup/create/replace denials; retained reader/account/session suites. |
| Native browser reload returns saved aggregate | `test_native_browser_create_write_reopen` runs `native PostgreSQL browser reload returns the acknowledged aggregate` against real restricted SQL through the real app HTTP adapter; synthetic Access HTTP is explicitly not owner-auth proof. |
| Migration failure blocks activation and preserves acknowledged data | Native `test_native_migration_failure_rollback_retry_and_owner_force_rls`, `test_unknown_alembic_history_refuses_without_reversing_acknowledged_data`; release `test_actual_entry_orders_histories_and_private_failure_blocks_complete` (success/failure), affected host tests. Fixture reads actual pre-existing corpus rows through unchanged BibleService/Database before/after upgrade/repeat and all private operations. |

**Failures investigated, not erased:** An obsolete broad deployment run was stopped
by SIGINT after current focused affected checks passed: 731 passed, 3 failed, 2 skipped,
5251 subtests, 597.21s. Two failures were the earlier contract-only metadata and exact
registry-input assertions; both expectations were updated for implemented behavior
and pass in the final focused suite. The untouched 150ms synthetic network test
`NetworkAcceptance::test_one_operation_deadline_spans_version_and_network_requests`
saw one rather than two events under load; its exact unchanged isolated rerun passed
(1 test, 1.93s), `/tmp/scribeswell-notes-isolated-network.log`.
`/tmp/scribeswell-notes-broad-interrupted-summary.txt` records this partial run; it is
not a full-regression pass. An earlier combined browser run had 162 passed/26 failed/2
skipped, retained at `/tmp/scribeswell-notes-browser-pre-final.log`. It exposed a hidden
duplicate WordStudy renderer and an observer counting Vite source-module requests as
protected API calls. The duplicate was removed; the observer still requires zero
actual private API requests. Current-source combined browser results above pass.
The actual-toolbar red exposed Chromium's DIV-wrapped ordinary list; the serializer
now flattens block containers while refusing true nested/unsupported wire nodes.

**Impact and limits:** Existing builder installer/templates supply managed migration
helpers unchanged. The editor/lane remains app-owned; no generic engine/shared UI
promotion or agent-context/ADR change is justified. Private Alembic history is additive
and separate from corpus; optional corpus-then-private release execution blocks on
failure, with forward recovery and immutable receipts. Physical iOS/Android,
native-mobile browser qualification, live Identity/Access/provider integration,
backup/restore and production release activation remain unqualified; this delivery
keeps activation refused. Wider D1–D5 and all explicitly deferred features remain open.

**Fixture ownership:** The only created Docker resource was
`scribeswell-notes-synthetic-20261023-implementation`, ID
`6b07924515ec0c5ea0e1fe53696051473f709067a945a068655a67027fc9735a`, image `postgres:17`,
labels `agriplatform.owner=scribeswell-personal-notes-runtime` and
`agriplatform.environment=synthetic-disposable`, loopback port32768, no bind mounts. The image created anonymous volume
`06d4ee58b3c55001fc7d2f0741f22ba4c3d485e8a92167d726028e0dd1c61375`;
its sole consumer was verified as the exact owned container before cleanup. Both the
container and this exclusively attached anonymous volume were stopped/removed after
qualification. A first cleanup guard safely refused the incorrect no-volume assumption
before any cleanup action, then ownership was checked explicitly.
Native fixtures allocated/dropped only their own random databases and previously
absent roles in this cluster. Final owned-container lifecycle is recorded in
`/tmp/scribeswell-notes-fixture-final.log`; no retained environment was changed.

**Source handoff:** `/tmp/scribeswell-notes-final-sources.json` lists the scoped final
files and SHA256s. Pre-existing untracked canonical companions are separately identified
as append-only parent reconciliation and are excluded from the scoped commit list.
The parent owns the independent review, final diff audit and any commit.


### Parent final acceptance — 2026-10-23

All task and frozen-matrix rows were audited against the scoped diff and executed
test bodies/results. Every row has passing coverage; no skipped test is counted as
its sole proof. All review corrections are complete, no findings deferred.

The exact commands in the handoff verification table were rerun after patches, with
these superseding final results and logs:

| Check | Parent final result |
| --- | --- |
| Focused Python/API/contract/reader/release/host command | 206 passed,49subtests6.35s; `/tmp/scribeswell-notes-parent-python.log` |
| Native qualifier, with admin URL `postgresql://postgres@127.0.0.1:32769/postgres` and browser opt-in | 10 passed,no skips19.27s; `/tmp/scribeswell-notes-parent-native.log` |
| Combined browser command with two workers | 206 passed,2optional native skips5.3min; `/tmp/scribeswell-notes-parent-browser.log` |
| Shared-session command | 12 passed50.2s; `/tmp/scribeswell-notes-parent-session.log` |
| App build | passed; existing bundle warning; `/tmp/scribeswell-notes-parent-build.log` |
| Contract/helper checks and helper tests | passed,11helper tests; `/tmp/scribeswell-notes-parent-contract.log`, `/tmp/scribeswell-notes-parent-helper.log`, `/tmp/scribeswell-notes-parent-helper-tests.log` |
| Qualified pinned API-client generation check | `api_client_current`; `/tmp/scribeswell-notes-parent-generated-qualified.log` |
| Composition dry-run | passed; `/tmp/scribeswell-notes-parent-compose.log` |
| Whitespace and frozen intent | passed; exact frozen snapshot matches |

The generator first returned `api_client_generation_failed` inside the process
sandbox (`/tmp/scribeswell-notes-parent-generated.log`); the unchanged read-only command
passed outside that sandbox. No generator/source/dependency change was made.
Parent native proof used a fresh, explicitly owned PostgreSQL17 container
`18e033b74dd73be4bde193a7b6ad96968d52fa26ada6d54176777f604f503d38`,
name `scribeswell-notes-review-20261023`, loopback32769, tmpfs data, no attached
volumes/bind mounts. Exact labels/ID/storage were checked before creation use and
cleanup; it was stopped/removed after qualification.
`/tmp/scribeswell-notes-review-fixture.log` records its lifecycle. No retained stack
was used. Synthetic Access, physical-device and production limitations above remain.

The47-file local commit excludes pre-existing README/AGENTS/Leave changes, concurrent
KDG changes and the pre-existing untracked canonical tree. Canonical status is
reconciled through bmad-spec events239–241 in that preserved working tree; this
commit does not adopt the whole planning folder. Production stays disabled.

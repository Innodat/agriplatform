# Personal Studies owner integration qualification

**Actual local HTTP/domain integration passed on 2026-10-25** in one fresh native
run, `21c6a0b8-957b-4623-9462-fabd63264275`. Both real-provider browser scenarios,
independent SQL observations and exact-run normal stop passed. This does not qualify
standalone signup, default Access startup/readiness, production activation, coordinated
release/backup/restore or physical devices. Wider Studies scope remains unchanged.
Three independent reviews completed; all13 findings were individually triaged and addressed, with no deferrals. Only the two omitted-source findings shared a root cause; the other corrections remain distinct.

The approved source of intent is
[spec-scribeswell-owner-integration.md](../../../_bmad-output/implementation-artifacts/spec-scribeswell-owner-integration.md).
All three frontmatter context files were loaded before implementation. Owner code,
migrations, generated references and provider configuration were preserved. The actual
Access app uses its existing database-injection seam in a separate process; default
release-artifact startup validation is explicitly outside this HTTP/domain proof.

## Final executed native proof

```sh
/tmp/scribeswell-host-tests-312/bin/python apps/scribeswell/tools/py/qualify_studies_owner_integration.py --run-id 21c6a0b8-957b-4623-9462-fabd63264275 --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase --proof /tmp/scribeswell-owner-integration-final-21c6a0b8
```

Result: **exit 0**. Private evidence remains in the explicit proof directory; no
credentials, signed links, sessions or private content are reproduced here. The
fixture records 222 source hashes at entry and refuses success if those sources
change. Independent inspection confirmed all 222 still match. `browser.log` records
one passed case (12,331 ms); `browser-denied.log` records one passed case (3,497 ms).
No owner integration case was skipped. All owned app groups stopped gracefully;
no forced termination occurred in this successful run. `wrapper-stop.log` records
exit 0 for this exact new project/run. Native data and private evidence are retained.

The wrapper performs prepare/up/verify before ordinary Identity21, Access16 and
Scribeswell private-head migrations. Fixture principal setup uses the actual owner
migrator logins. App/permission registration and later disable use the existing
protected Access operator; no user grants are seeded. Auth admin creates only fresh
local synthetic accounts, with undelivered generated magic links. Browsers follow
actual provider verification redirects to the supported reader root and use SDK-created
sessions. No protected HTTP/Auth interception or session-storage injection is used.

| Frozen matrix row | Executed evidence and result |
| --- | --- |
| Fresh verified reader: actual profile, zero memberships/grant/study; protected refusal; public reading | `before-enrollment.json` and `after-protected-check.json`: two profiles; zero memberships, grants, studies, actor bindings, notes, enrollment/setup outcomes, assignment/setup events and app receipts. Actual callback confirmed and public Hebrew rendered. The actual fresh check returned503 `studies_access_unavailable`, matching the owner's missing-actor contract; check creates nothing. Browser pauses on a bounded fixture-only file checkpoint until independent SQL confirms zero effects, then may enroll. **Passed.** |
| Explicit enrollment/create, Hebrew/combining marks, autosave/reload/reopen, durable attribution | Actual Start a study / Create study controls perform initial enrollment/create through app→Access→Identity/Auth and restricted app SQL. UI autosaves `בְּרֵאשִׁית — é שָׁלוֹם`; reload/reopen returns identical text. `after-browser.json` SQL oracle compares the full acknowledged aggregate, creation/update actor and durable `identity.account_actor` binding. One note, two intentional owner studies (UI creation and separate original-operation replay scenario), zero memberships. Both account actor bindings plus study/note/receipt attribution are asserted. **Passed.** |
| Second account isolation; no browser service credentials | Second real callback/session/enrollment; foreign study/note/list reads plus note creation/replacement each404, foreign operation lookup unresolved, own list empty. URL/header/body, all-origin response and WebSocket sentinel checks across both contexts found neither service credential. Complete owner-table snapshots match before/after denied foreign operations. **Passed.** |
| Completed enrollment/create reply discarded, original operation retried after current checks | Real completed replies are discarded, original operation/payload retried. Independent SQL confirms one receipt per original create operation, four total app receipts, two grants/assignment events, three Access enrollment outcomes and two Identity setup outcomes. Checking an already prepared actor does not repeat Identity setup. Disabled original-operation replay later403. **Passed.** |
| Protected operator disables authority; subsequent read/write/lookup deny; public reading works | Existing `application.set_enabled` command with current revision; separate real browser phase proves list/detail/write/lookup and original enrollment replay403, while authenticated and anonymous public Hebrew remain available. Complete protected table rows, including revisions/timestamps/receipts/outcomes, match exactly before/after disabled requests; the intentional operator disable precedes its baseline. **Passed.** |
| Preparation/migration failure, occupied ports, interruption; no premature startup/adoption | Actual failed native preparations and actual collision refusals below started no apps. Focused tests prove interrupt/exact-stop ordering, cleanup failure propagation and real command-descendant termination on timeout/SIGINT. Only owned process groups and exact newly created runs are stopped. **Passed within those stated scopes.** |

Selected helper HTTP observations: eight200, six403, five404 and the initial503; UI requests are additionally observed directly by the browser scenario. Diagnostic
logs contain only safe stage/source references, endpoint paths, status and allowlisted
closed error identifiers. Traces, screenshots, video, automatic DOM snapshots, raw
errors and browser console payloads are disabled/suppressed. SDK session snapshots and
private proof values are designated0600 evidence/configuration, never diagnostic dumps.

## Preparation and acceptance failures retained

Earlier native invocations used the same executable/CLI arguments with their listed
`--run-id` and `--proof /tmp/scribeswell-owner-integration-<prefix>`. The final parent invocation uses the exact `final-21c6a0b8` proof path above. Every started
owned native run received its own successful exact normal stop; none was resumed,
reset, adopted or automatically reversed. Collision attempts performed no wrapper
operation and no cleanup. Earlier attempts are diagnostic failures, not final proof.

| Run ID | Proof suffix | Actual result |
| --- | --- | --- |
| `07d59362-a27f-4ecd-9dc4-bc020bf0389e` | `07d59362` | Native prepare/up/verify passed; Identity preflight refused `identity_authority_role_unsafe`. Native extension diagnostic views exposed inherited PUBLIC reads. Fixture now records/revokes only those PUBLIC table reads inside its own fresh database. No app startup. |
| `dfa62b33-3682-48a2-90e4-29ec47333e04` | `dfa62b33` | Identity0020 refused `identity_catalog_mismatch:role_memberships`. No app startup. |
| `ff78d96e-a4ef-49ea-b73b-51a10963f61d` | `ff78d96e` | Fresh reproduction retained selected role metadata/source hashes; same refusal. Fixture had omitted the trusted native ADMIN-only Identity migrator bootstrap edge. Exact existing native Access ADMIN-only/SET-only edges were also prepared; the later Access Studies edge is staged after its existing reader helper. No owner implementation/reference was changed. |
| `b07d615c-dd38-4ea7-8878-4652beb91347` | `b07d615c` | Actual55481/55482 collision refused before wrapper prepare. Retained foreign run left untouched. |
| `5f322229-d7db-4601-aa60-52b77d7df650` | `5f322229` | All ordinary owner/app migrations passed; fixture principal insertion under superuser refused42501. Fixture corrected to use the actual owner migrator logins. No app startup. |
| `d421ca22-8e0c-4011-90ab-f5c71b08fa68` | `d421ca22` | Migrations/owner-login principal setup passed; protected operator import refused missing `rfc8785` in the selected interpreter. Installed the owner's existing pinned0.1.4 dependency in that isolated interpreter; no repository dependency baseline changed. No app startup. |
| `7ef9008d-a72b-47ad-b81e-b84679db7f71` | `7ef9008d` | All setup, provider profiles and initial SQL passed; actual services/app started. Browser failed while last stage label was first-provider-callback. Original diagnosis remains provisional because this attempt lacked the later safe callback sub-stages. It is not proof of an Auth defect. |
| `2e9f1f64-1951-4fa0-b28f-1d020ec66c6b` | `2e9f1f64` | Actual55482 collision refused before wrapper prepare; read-only follow-up confirmed active55481/55482 listeners. Foreign run left untouched. |
| `d4ef1f59-d9f5-4225-99d6-d98ece9648c2` | `d4ef1f59` | Safe callback failure observer was not entered: login completed; the following public Hebrew assertion failed. Fixture had omitted `display_he`, which the actual reader renders. Minimal corpus sample corrected; no Auth/product change. |
| `18c32e46-e361-4cd8-933d-599650b0f085` | `18c32e46` | Explicit callback-confirmed/public-reader stages passed; fixture incorrectly expected403 for a fresh account check. Existing owner `studies_access.py`54–55 and `STUDIES-ENROLLMENT.md` specify missing-actor503 without implicit setup. Expectation corrected to that documented safe contract; final run records the actual503/code before assertion and independently checks zero effects. |
| `41b8351e-bcc4-4128-ac22-d7ef3dc561b3` | `41b8351e` | Pre-review qualification passed with173 source hashes and browser6.484s/1.865s; exact stop passed. The later review strengthened source, oracle, UI/isolation/privacy and cleanup assertions. |
| `21c6a0b8-957b-4623-9462-fabd63264275` | `final-21c6a0b8` | Parent final patched-source qualification passed with222 unchanged sources, both browser cases, complete denial-state comparisons, anonymous reading and confirmed process termination; exact stop0. |

The first two attempts predate source snapshot capture and cannot supply source-bound
success. The first test attempt using `.venv/bin/python` lacked pytest; the existing
isolated interpreter was then used. Initial missing-capability acceptance observed
five `ModuleNotFoundError` failures before the fixture was implemented. The signed-link
redaction harness initially failed because its wrapper did not meet Playwright's
fixture-destructuring contract; that fixture-only wrapper was corrected.

A real-process acceptance test first demonstrated that `subprocess.run(timeout)` left
an owned TERM-ignoring descendant executing. Command/status capture now use new process
groups and bounded TERM/KILL cleanup before outer exact-run stop. An immediate `/proc`
check also observed a killed process before kernel signal delivery completed; the
unchanged stopped-state expectation is now observed within a bounded500 ms window.
Real timeout and SIGINT cases both retain forced-termination evidence; cleanup failure
still makes qualification fail. Exact red/green commands:

```sh
/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_studies_owner_integration.py -q -k timed_out
/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_studies_owner_integration.py -q
```

Initial focused process result: one failure (live descendant). Final focused result:
**11 passed**, including real timeout/SIGINT, safe signed-callback failure diagnostics,
collision/ownership refusal, failed preparation, exact-stop failure and exited launcher
cleanup. Doubles establish orchestration only; native proof above supplies actual SQL,
provider and HTTP evidence. No skipped case is counted as proof.

## Retained regression checks and limits

```sh
/tmp/scribeswell-host-tests-312/bin/python -m pytest apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_personal_notes_release.py -q
/tmp/scribeswell-host-tests-312/bin/python -m pytest services/access/tests/test_studies_identity.py services/access/tests/test_studies_access.py services/access/tests/test_studies_readiness.py -q
node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.session.config.cjs
```

The app command passed142 tests before the two real-process cases were added;
subsequent final focused execution passed all11 cases. Owner characterization passed56;
retained session checks passed12. Existing Starlette TestClient deprecation remains.
The session configuration now selects exactly `session.integration.cjs`, preserving its
suite while preventing accidental collection of the separately configured owner test.

```sh
node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.config.cjs --grep-invert 'native PostgreSQL browser reload'
node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.config.cjs --project desktop --workers 1 --grep 'late chapter responses cannot replace the chosen chapter|callback recovery scrubs secrets and preserves prior session: incomplete'
node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.config.cjs --project mobile --workers 1 --grep 'occurrence pages survive tabs, filter resets, errors retry and new words clear old results'
```

Broad desktop/mobile result: **203 passed / 3 failed** under six workers. Those exact
unchanged failing desktop cases passed2/2 at one worker; the exact unchanged mobile
occurrence case passed1/1 at one worker. No expected result/product source was changed.
The original broad invocation remains failed; the cause of its three failures has not been established.
The existing opt-in synthetic-owner native browser case was explicitly filtered out;
it is not counted as integrated evidence. No regression browser run overlapped the
successful final native qualification.

`npm run build` in `apps/scribeswell/web` passed with the existing553.75 kB chunk
warning. Python compilation and `node --check` on new CJS files passed. These checks
also passed and wrote no generated/composed changes:

```sh
/tmp/scribeswell-host-tests-312/bin/python apps/scribeswell/tools/py/export_personal_notes_contract.py --check
node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs --check
python3 tools/py/run_compose_supabase.py --check-only
```

Scaffold: reuse existing wrapper/migration/role helpers; no generic lifecycle or
provisioner. Shared UI: unchanged. Agent context: unchanged. Documentation: this evidence
and the consuming contract distinguish actual local proof from remaining gates. ADRs:
unchanged. Canonical reconciliation/review is owned by the parent BMAD workflow. There
is no root repository-wide verification claim.

## Final review corrections and parent verification

All13 independent findings were retained individually in the delivery spec;12 distinct correction groups were addressed, none deferred. The fixture now rediscovers consumed SQL/config/migration/schema/source inputs, reserves run UUIDs with create-only retained fixture reservations, bounds SQL statements/locks, and confirms no executing owned group members remain after TERM/KILL before declaring stopped. The reservation coordinates fixture invocations; it does not add a platform environment lifecycle.

Complete rows from all Identity, Access and private Studies tables are compared around denied foreign and disabled requests. Initial checks assert no account outcome/event/receipt effects. Both account bindings and study/note/receipt actors are asserted. The actual UI path, missing foreign list/create paths, anonymous post-disable reading and additional credential channels now run in the native scenario. Local focused tests demonstrate detector refusal using an occupied real socket, concurrent same-UUID refusal, omitted/new source invalidation, changed protected-state rejection, wrong attribution rejection, SQL timeout options and confirmed/unconfirmed process cleanup.

Child final focused verification passed37 tests9.93s; parent affected app command above passed170 tests11.26s. Owner characterization passed56 tests3.38s; app build passed8.99s with the existing bundle warning. Generated contract/helper/composition checks passed. Default-sandbox focused execution first passed29 and failed one real-socket test with PermissionError; unchanged socket-enabled execution passed30, then final37. A parent sandboxed owner characterization stalled at TestClient and was interrupted; the unchanged socket-enabled rerun passed56. These environment failures remain disclosed. No broader browser regression was rerun after the fixture-only corrections; its original203/3 and unchanged isolated successes remain the stated limit.

Final parent retained-session rerun:12 passed20.7s using the exact session command above.

## Dedicated isolated owner fixture — 2026-10-27

Implementation follows
[spec-scribeswell-isolated-owner-fixture.md](../../../_bmad-output/implementation-artifacts/spec-scribeswell-isolated-owner-fixture.md).
Both frontmatter context files were loaded before changes. The selected closed target
is now `scribeswell-local`, with owners Identity/Access/Scribeswell, independent
`.local/scribeswell/<new canonical UUID>` state, project prefix `agri-scribeswell`
and exact-run network labels. Its fixed ports are web5192, API8192, AccessHTTP8193,
shadow55490, Auth55491, DB55492, Studio55493, mail15494 and TLS8447; its explicit
subnet is `10.254.27.0/24`. Existing full-UUID encoding makes the project identity
**39 characters**, rather than the spec's arithmetic description of38; the required
prefix and existing UUID-preserving encoding are retained within the vendor's40
character limit.

The fixture derives its run path, ports, server URLs and Auth redirect from the
validated target. Browser references use the selected web5192 origin. A wrong
status database (including KDG55482) raises fixed `unexpected_native_database`
before owner preparation; collision refusal still precedes wrapper preparation.
Actual HTTP/browser/SQL assertions and exact-run cleanup are unchanged. This is
fixture isolation, with no signup, sharing, device or release acceptance claim.

Acceptance was observed red before implementation:

```sh
/tmp/scribeswell-implementation-python/bin/python -m pytest apps/scribeswell/tests/test_studies_owner_integration.py -q -k 'dedicated_target or wrong_database'
PYTHONPATH=platform/deployment /tmp/scribeswell-implementation-python/bin/python -m pytest platform/deployment/tests/test_native_cli.py -q -k scribeswell_namespace
```

Results: app **2 failed / 68 deselected** (KDG target still selected; dedicated
wrong-database guard seam absent); platform **1 failed / 29 deselected** (dedicated
target absent). An initial platform invocation without `PYTHONPATH` failed collection
with missing `dev`; the exact corrected command above reached acceptance. The first
combined green attempt exposed the38/39 character arithmetic mismatch; the assertion
was corrected to39 after checking the unchanged full-UUID encoding.

Final focused command:

```sh
PYTHONPATH=platform/deployment /tmp/scribeswell-implementation-python/bin/python -m pytest platform/deployment/tests/test_native_cli.py apps/scribeswell/tests/test_studies_owner_integration.py -q
node --check apps/scribeswell/web/playwright.owner-integration.config.cjs
node --check apps/scribeswell/web/tests/studies-owner.integration.cjs
```

Socket-enabled result: **102 passed in16.09s**; both syntax checks exited0. The first
sandboxed combined run had99 passed and one real-listener `PermissionError`; no test
or expected result was weakened. The unchanged real-socket collision test passed in
the host-enabled rerun. Traceability: dedicated target/namespace/configuration and
fixed DB port refusal → `ScribeswellNativeAcceptance`; exact subnet and foreign
owner labels → `ScribeswellNetworkAcceptance`; owner port separation →
`test_dedicated_target_and_namespace_are_isolated` and
`test_port_preflight_ignores_running_kdg_and_leave`; wrong DB before owner writes →
`test_wrong_database_refuses_before_owner_writes`; real collision and exact cleanup →
retained fixture acceptance tests. Concurrent-owner preflight coverage uses a socket
double; actual native/provider qualification remains a separate parent execution.

The deployment renderer is byte-identical to the preexisting dirty baseline in
`/tmp/scribeswell-isolated-before`; KDG's configuration hash assertion and existing
Leave lifecycle cases pass. Shared native changes extend only target/schema
selection, namespace and explicit subnet checks. Source inventory covers the new
target, all deployment Python and schema inputs, and existing consumed owner/app
sources. No unrelated working-tree hunks were changed or checkpointed here.

Impact decisions: scaffold reuses the existing native lifecycle with one closed
owner target/schema; no generator/factory work. Shared UI unchanged. Agent context
unchanged. Documentation updated here. ADRs unchanged; disposable fixture isolation
does not change product or owner contracts. Parent owns immediate host port/subnet
preflight, fresh actual integration and scoped checkpoint; those are not established
by the102 focused tests. No full browser regression was repeated for this fixture
change.

Fixture assertion correction: run `03b7fb1b-25cd-4d4f-a50c-25ef751e2fbe` reached
`before-note-restored-study-confirmed` after confirming the Studies tool active.
The newly added Notes-list visibility assertion then timed out before any notes
existed: the empty list has no visible height. It now checks attachment; selected
study heading visibility, Studies pressed state and original action/content checks
remain. This introduced fixture assertion failure is distinct from the earlier
unexplained navigation timeout. The changed browser scenario passes `node --check`;
fresh actual qualification remains separate.


### Final isolated real-owner result

**Passed2026-10-27**, fresh run `d32a2c3b-715a-4783-b356-8a46356499a7`, exit0 in94.52s. [Exact command, selected events and result](evidence/isolated-owner-fixture-20261027/native-final/result.json), [source comparison](evidence/isolated-owner-fixture-20261027/native-final/source-comparison.json), browser logs/stages, wrapper logs and exact parent runner are retained. All284source hashes still matched at completion. The full real-provider/browser workflow passed34045ms and disabled-access denial passed4927ms, with original HTTP, retry, privacy, actor/ownership, isolation, saved content, rename, passage, deletion and independent SQL assertions. This remains HTTP/domain integration through the owner's existing injected database seam, not default Access deployment readiness.

The fixture consumes current Identity25→Access18 preparation: the existing preferences role helper and documented private capability-reader role/sole SET-only edge. The later edge is temporarily removed/restored around the historical reader helper's exact prior-membership check. No Access/Identity implementation or migration was edited. Browser navigation follows actual workspace restoration; linked-note preview is scoped separately from reference buttons. The URL oracle now uses the existing reader parser and proves the full valid Genesis1:31–2:3 target rather than the superseded legacy book query field. All original data checks remain.

Parent final focused regression: **113passed20.59s**, runner21.89s, [command/source pair/log](evidence/isolated-owner-fixture-20261027/parent-final/results.json); all10selected source hashes unchanged. Safe diagnostic JS oracle and both browser CJS syntax checks passed. The reporter forwards only closed, bounded source/name/line/column events; no arbitrary worker output, messages, signed URLs, DOM or private payloads.

[Cleanup/coexistence observation](evidence/isolated-owner-fixture-20261027/native-final/cleanup-coexistence.json) confirms all nine Scribeswell ports released, its exact empty network removed and no forced termination. KDG55481/55482 remained occupied at final check; KDG and Leave target files are byte-identical across the observation window. Other owners were active:21foreign containers were observed during an earlier isolated run and15of those still ran at final observation. This does **not** claim every foreign process remained running or attribute their changes; our commands target only new Scribeswell run identities.

The failed attempts remain separate: first local Alembic visibility; second safe generic Identity migration refusal; third explicit capability-reader preparation refusal; fourth restored Python missing distribution metadata; fifth missing API pool dependency; sixth old reload navigation timeout; seventh newly introduced empty-list visibility assertion; eighth/ninth legacy URL expectation. First/second/fourth/sixth/seventh/eighth/ninth selected raw evidence is retained under the dated evidence directory. Third/fifth lost their raw `/tmp` proofs on session continuation and are clearly labelled observed summaries, not reconstructed raw logs. The sixth timeout's exact earlier cause remains unproved; current explicit navigation passes. No failures were relabelled green or expected data weakened.

Persistent private Python/fixture evidence now lives under ignored `apps/scribeswell/.local/owner-integration-20261027/`; offline dependency packages/metadata were RECORD-verified, and full API imports passed before the final run. [Provisioning summary](evidence/isolated-owner-fixture-20261027/offline-provision.json) contains no credentials. Account/session/database snapshots remain private there. The test environment is stopped: `http://localhost:5192` is the selected web address, **not a currently running manual-test link**. Signup/confirmation, recipients/Notification, physical devices and coordinated release-report/activation remain separate gates.

Shared native lifecycle files already contained foreign Leave/platform edits. The [additive Scribeswell platform patch](evidence/isolated-owner-fixture-20261027/shared-platform-changes.patch) records only this slice's extension for their owner's coordinated checkpoint; whole foreign files are not staged into the Scribeswell checkpoint. Root README, canonical derivation and unrelated owner edits remain preserved. No Content-service implementation changed; the separately pasted Content review awaits routing clarification.

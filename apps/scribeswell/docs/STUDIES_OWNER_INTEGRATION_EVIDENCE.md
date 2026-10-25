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

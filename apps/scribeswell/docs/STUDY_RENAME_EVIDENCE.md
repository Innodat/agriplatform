# Ordinary study-title rename qualification — 2026-10-25

**Final result:** approved bounded rename delivery verified after three independent
reviews. All13 findings were triaged;12 were corrected in10 groups, one low/rare
recovery suggestion rejected, none deferred. Final notes94/session12/native13,
app172/Access56/public-release73+49subtests and real-owner integration passed.
Production activation, default owner startup, actual standalone signup, physical
devices and manual-user acceptance remain outside this qualification.


The bounded development/test opt-in now supplies Rename with explicit Save / Cancel,
strict `study.rename` commands, independent metadata revisions and immutable operation
receipts. The additive private migration `scribeswell_studies_0002` widens only the
receipt command/correlation CHECKs. History 0001, restricted grants, public reading,
notes and production activation policy are unchanged.

## Executed verification

`P=/tmp/scribeswell-manual-python/bin/python`. Tests initially could not run because
this existing interpreter lacked pytest; `uv pip install --python P -r
apps/scribeswell/tests/requirements.txt` installed the declared test dependencies.
The first rename acceptance test then failed because `study.rename` was unknown.
After implementation:

| Exact command | Result |
| --- | --- |
| `P -m pytest apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py -q` | 130 passed; one framework deprecation warning. |
| `SCRIBESWELL_NOTES_TEST_ADMIN_URL=postgresql://postgres@127.0.0.1:32768/postgres SCRIBESWELL_NOTES_BROWSER_QUALIFY=true P -m pytest apps/scribeswell/tests/test_personal_notes_storage.py -q` | 13 passed, no skips; `/tmp/scribeswell-rename-native-qualified.log`. Fresh owned `postgres:17` container `scribeswell-rename-native-20261025`; random test database and roles removed by fixture. `docker stop scribeswell-rename-native-20261025` completed normally after final proof; stopped container/data retained. |
| `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep 'rename:' --workers=2` | First matrix 12 passed; expanded account/access matrix 18 passed in `/tmp/scribeswell-rename-browser.log`. Final navigation/dirty-note and unchanged-toolbar rerun26 passed; see below. |
| `P -m pytest apps/scribeswell/tests/test_personal_notes_release.py apps/scribeswell/tests/test_studies_owner_integration.py -q` | 42 passed; `/tmp/scribeswell-rename-owner-tests.log`. |
| `P -m pytest services/access/tests/test_studies_identity.py services/access/tests/test_studies_access.py services/access/tests/test_studies_readiness.py -q` | 56 passed; `/tmp/scribeswell-rename-access-regression.log`. |
| `P -m pytest apps/scribeswell/tests/test_reader_integrity.py platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_host_profiles.py -q` | 73 passed, 49 subtests; `/tmp/scribeswell-rename-release-regression.log`. |
| `P apps/scribeswell/tools/py/export_personal_notes_contract.py --check` | Passed. |
| `node --experimental-strip-types apps/scribeswell/tools/sync_personal_notes_database.mjs --check` | Passed; shared helper current. |
| `python3 tools/py/run_compose_supabase.py --check-only` | Passed; dry run, no files changed. |
| `npm run build --workspace=apps/scribeswell/web` | Passed; existing bundle-size warning only. Final build log `/tmp/scribeswell-rename-build-final.log`. |

The pinned generated TypeScript check uses Node
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`
and CLI
`platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs`
with `--schema /home/ck/repos/innodat/agriplatform/apps/scribeswell/contracts/personal-notes-v1.openapi.json
--output /home/ck/repos/innodat/agriplatform/apps/scribeswell/web/src/generated/personal-notes --check`.
The final check returned `api_client_current`. Generation initially failed inside the process sandbox; the same pinned generator
succeeded with sandbox escalation. Generated files were never hand-edited.

## Matrix traceability

| Requirement | Behavior evidence |
| --- | --- |
| English/Hebrew title, same ID, attribution, reload, unchanged notes/reader | Native `test_native_rename_noop_replay_conflict_attribution_and_independent_note`; browser `rename: explicit Save Cancel and reload preserve independent note and reader`. |
| Cancel sends nothing; identical title preserves revision/time | Browser explicit Save/Cancel case; native no-op case compares the full study before/after. |
| Invalid/null/forged input, typed errors, no-store | `test_rename_title_wire_and_correlated_outcome`, `test_rename_boundary_fresh_authority_safe_conflict_and_input`; browser invalid-title correction. |
| Metadata conflict retains candidate; explicit current reload and new Save | Native metadata race/CAS; browser conflict case asserts no second command before explicit Save, new operation/base revision afterward. |
| Note writes independent of rename | Native `test_native_rename_and_note_races_preserve_both_and_metadata_cas` races both, then verifies note value. |
| Lost committed response, same operation, mismatch, stale replay | Native no-op/replay and `test_native_rename_lost_commit_and_overflow`; browser unknown outcome freezes original across Cancel/reopen and retries the identical payload. |
| Current ownership/lifecycle/access on replay and lookup | Native wrong owner/closed rename and lookup; API authority-before-storage; browser 401/403 and delayed account replacement. |
| Late response/navigation and current metadata after old receipt | Browser executing-Cancel case refreshes a newer current title; departed editor/account response cases; current metadata update compares revisions. |
| Failed rename migration blocks completion; previous consumer and rows survive | Native setup first applies the frozen 0001 history, writes with frozen baseline SQL consumer, injects failure after actual 0002 ALTERs, proves old ledger/CHECKs/data survived, retries real 0002 and repeats head. Frozen previous storage then reads, looks up its old receipt and writes its original note command. Public BibleService/Database stays open throughout. |
| Restricted permissions, receipt immutability, overflow | Native suite executes restricted actual logins for DDL/ledger/foreign-owner/creation-attribution/receipt denials; metadata overflow refuses. |

The previous storage SQL consumer fixture is copied from commit
`837e580409494d97a38546924ce850e8cd6c76ff`, with its original imports satisfied by
compatible current DTO/helper interfaces. This qualifies its actual SQL operation
behavior, plus unchanged previous public-reader code, rather than a separately
deployed previous application binary.

## Actual owner qualification

The browser fixture now includes explicit UI rename/reload through actual Auth,
Access/Identity and Scribeswell, with independent before/after SQL snapshots of
complete acknowledged note rows, immutable creation attribution and one rename
receipt. Foreign-owner rename/lookup and disabled-authority replay are included.
Fresh runs must pass before this actual-owner rename proof is claimed.

The previously owned manual run `65a01b23-44b1-4ac4-9830-ca7bad95be68` stopped normally;
its `manual-stopped.json` confirms cleanup and retained data. Fresh attempts
`3abcdf01-7d5b-4864-b3e4-0feee3589df7`,
`64c18c35-b4de-469e-a410-4de386846942` and
`e4924b6c-9b6f-4cec-9ed2-f11a1c76df3d` safely refused occupied ports before provisioning.
Private failure/result evidence remains in matching `/tmp/scribeswell-rename-owner-*`
directories. A separate foreign KDG environment owns shared native ports; it was
not adopted, changed or stopped. The owner subsequently stopped it; the successful fresh execution is recorded below. Intercepted tests and the synthetic-Access native browser do not replace this
proof. Manual-user acceptance, physical devices, standalone signup, production and
default owner startup/readiness remain deferred.

## Reuse decisions

Scaffold: consume the existing controlled migration helper; no generator changes.
Shared UI: retain this app-specific title form/lane; no promotion without another
consumer. Agent context: unchanged. Documentation: owning wire contract, this evidence
and delivery record updated; canonical memory reconciled by the delivery workflow.
ADRs: no new or changed accepted decision.


## Additional regression observations

`node node_modules/@playwright/test/cli.js test --config
apps/scribeswell/web/playwright.session.config.cjs` reported 11 passed and one timeout
waiting for the unchanged Password field in `existing PtS session and sign-out
synchronize across both readers` (line21); `/tmp/scribeswell-rename-session.log`.
An unchanged isolated rerun with `--grep 'existing PtS session and sign-out synchronize'`
passed1 in11.7s; `/tmp/scribeswell-rename-session-rerun.log`. The cause is unestablished;
this is not a full session-suite pass. Earlier broad browser failures recorded in
[the actual-owner evidence](STUDIES_OWNER_INTEGRATION_EVIDENCE.md) remain historical
unexplained failures; isolated successes do not erase them.


The broad command `npm run test:browser --workspace=apps/scribeswell/web --
personal-notes.spec.cjs reader.spec.cjs account-entry.spec.cjs --grep-invert
'native PostgreSQL' --workers=2` reported170 passed/2 failed in5.1min;
`/tmp/scribeswell-rename-browser-regression.log`. Existing desktop cases
`review: invalid DNS link remains correctable without changing note text` timed out
waiting for Draft saved, and `review: More notes deduplicates its page and ignores a
changed study parent` timed out on a detached Leave study control/navigation. This
run overlapped final source edits and is not a frozen-source full pass. The complete
affected note suite is rerun separately against frozen source; these failures remain
reported rather than erased.

An intermediate native rerun reported12 passed/1 failed because its optional browser
found port5182 occupied by that concurrently running broad suite;
`/tmp/scribeswell-rename-native-final.log`. Sequential final native qualification
then passed13; `/tmp/scribeswell-rename-native-qualified.log`. Initial native execution
inside the network sandbox could not connect to the owned loopback database; native
qualification with sandbox escalation succeeded. The initial previous-version
fixture attempted a non-head Alembic destination and was correctly refused by the
controlled entry; it now copies the frozen0001 history and upgrades its head without
weakening the production migration wrapper. No expected business result changed to
dismiss a failure.


Final frozen-implementation affected command:

```sh
npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep-invert 'native PostgreSQL' --workers=2
```

Result66 passed/2 failed in3.1min; `/tmp/scribeswell-rename-notes-final.log`. Both
unchanged desktop/mobile `editor toolbar actions persist direction marks lists and
safe links` cases hit the30s timeout during keyboard input. All22 then-present rename
cases passed. The prior broad invalid-link and More-notes cases passed in this run.
No production source changed during this full affected run.

After adding a specific failed-dirty-note independence scenario (test-only change),
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs
--grep 'rename:|editor toolbar actions persist' --workers=2` passed26 in31.4s;
`/tmp/scribeswell-rename-focused-final.log`. This includes24 rename cases and both
unchanged toolbar cases, with original expectations. The new scenario proves rename
can succeed while a failed note lane retains dirty text, then retries the identical
original note operation independently. Timeout causes remain unestablished; neither
isolated success nor focused success turns the complete affected run into a pass.
The earlier actual-owner blocker is resolved by the continuation below; manual acceptance and workflow reviews remain incomplete.


## Real-owner continuation

After the KDG owning session stopped its environment, fresh run
`c948174c-86a7-4816-b3d5-736ca930428b` passed:

```sh
/tmp/scribeswell-manual-python/bin/python apps/scribeswell/tools/py/qualify_studies_owner_integration.py --run-id c948174c-86a7-4816-b3d5-736ca930428b --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase --proof /tmp/scribeswell-rename-owner-c948174c
```

`result.json` records `passed`, both browser phases exit0, controlled migrations
through private0002, confirmed normal process termination and exact wrapper stop0.
`after-rename.json` records independent SQL observation; the fixture compared complete
note rows unchanged, study ID/creation attribution unchanged, title/revision/update
attribution changed, and exactly one new rename receipt. Foreign rename returned404
and its outcome remained unresolved; disabled original rename replay/lookup returned403.
Protected-table snapshots remained unchanged across denied requests. Real Auth,
Access/Identity HTTP and restricted Scribeswell SQL were used; no intercepted business
routes. Public/anonymous reading and credential inspection passed. Data is retained.

Earlier run `f6a5d238-1b36-4cbd-bd99-3545c30b2988` failed before rename because two
misplaced duplicate denial checks referenced `result` before declaration. Only those
stray assertions were removed; actual disabled-scenario checks remain and passed.
Its owned processes stopped normally and wrapper stop returned0. Intermediate
`f9cc7c88-a0a6-4243-ad32-17e14fb473ac` refused occupied5188 before provisioning.
All three private proof directories retain their distinct results; no failure erased.
This qualifies HTTP/domain integration, not default startup/readiness or deployment.


Final frozen-source complete affected browser command
`npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep-invert 'native PostgreSQL' --workers=1`
passed **70 tests** in1.7min, exit0; `/tmp/scribeswell-rename-notes-sequential.log`.
This ran after the real-owner fixture correction, with no overlapping browser suite.
Native browser behavior is independently covered by the executed opt-in native suite.
Previous failures remain historical observations; their causes are not established.

Complete session regression
`node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.session.config.cjs --workers=1`
passed **12 tests** in14.2s, exit0; `/tmp/scribeswell-rename-session-sequential.log`.
Previous session timeout and isolated rerun remain disclosed above.


## Post-review final verification

The review corrections reconcile same-study metadata after note navigation, retain
confirmed outcomes across refresh failures, preserve scalar Unicode titles, reject
superseded reloads/errors and older library metadata, warn on unresolved title exits,
restore focus and give bounded loading feedback. Initial patch regressions observed
10fail/1pass (`/tmp/scribeswell-rename-patch-red.log`); the already-present revision
guard test passed. Busy cleanup follow-up failed before correction. Focused patch24
and existing rename24 passed; deleting the heading revision guard temporarily made
the overlap test fail (`/tmp/scribeswell-rename-patch-mutation.log`), then restoration
was verified. No matrix expectation, authorization rule or owner implementation changed.

| Final exact command | Result |
| --- | --- |
| `npm run test:browser --workspace=apps/scribeswell/web -- personal-notes.spec.cjs --grep-invert 'native PostgreSQL' --workers=1` | 94 passed2.4min; `/tmp/scribeswell-rename-post-review-notes.log`. |
| `node node_modules/@playwright/test/cli.js test --config apps/scribeswell/web/playwright.session.config.cjs --workers=1` | 12 passed22.7s; `/tmp/scribeswell-rename-post-review-sessions.log`. |
| `SCRIBESWELL_NOTES_TEST_ADMIN_URL=postgresql://postgres@127.0.0.1:32769/postgres SCRIBESWELL_NOTES_BROWSER_QUALIFY=true /tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_personal_notes_storage.py -q` | 13 passed8.33s; `/tmp/scribeswell-rename-final-native/pytest.log`. Fresh `scribeswell-rename-final-20261025b` postgres17 stopped normally, retained. |
| `/tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_personal_notes_release.py apps/scribeswell/tests/test_studies_owner_integration.py -q` | 172 passed14.36s; `/tmp/scribeswell-rename-final-app.log`. |
| `/tmp/scribeswell-manual-python/bin/python -m pytest services/access/tests/test_studies_identity.py services/access/tests/test_studies_access.py services/access/tests/test_studies_readiness.py -q` | 56 passed3.05s; `/tmp/scribeswell-rename-final-access.log`. |
| `/tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_reader_integrity.py platform/deployment/tests/test_release.py platform/deployment/tests/test_host.py platform/deployment/tests/test_host_profiles.py -q` | 73 passed12.78s+49subtests; `/tmp/scribeswell-rename-final-public-release.log`. |
| `npm run build --workspace=apps/scribeswell/web` | TypeScript/build passed; existing bundle warning; `/tmp/scribeswell-rename-post-review-build.log`. |

Exporter, pinned generated TypeScript, scaffold helper and composition commands above
were rerun and passed. An initial combined Python invocation of all three groups
reported300pass/1fail (`/tmp/scribeswell-rename-final-python.log`): Access tests import
`from main import create_app` before public reader tests import `from main import app`,
so Python reuses Access's top-level module and the Bible route incorrectly returns404
in that test process. Separate unchanged process invocations above passed; no owner
or application behavior was changed to accommodate this harness collision. Earlier
browser/session failures remain disclosed rather than attributed to this different issue.

Final real-owner command:

```sh
/tmp/scribeswell-manual-python/bin/python apps/scribeswell/tools/py/qualify_studies_owner_integration.py --run-id a1952f79-4db3-46eb-9c84-3aa3f8813c29 --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase --proof /tmp/scribeswell-rename-owner-a1952f79
```

Passed with223source hashes, both actual-owner browser phases exit0, independent
complete note/creation-attribution preservation, one rename receipt, foreign and
disabled denials, public/anonymous reading and complete credential inspection.
`result.json` confirms all process stops and wrapper stop0. Data retained. A subsequent
Docker/listener check found neither running container nor listener on55481/55482;
the user was told KDG may resume. No further shared-port use remains for this slice.

All seven approved matrix rows have executed passing coverage. This is complete for
the bounded development/test opt-in and does not close the broader Studies gates.

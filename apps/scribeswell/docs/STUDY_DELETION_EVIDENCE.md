# Whole-study deletion component delivery — 2026-10-26

CAP-10/ST-24–25 follows [the adopted bounded contract](STUDY_DELETION_V1.md).
Component delivery is implemented; final native SQL, actual-owner and session
qualification remains deferred under direction266. No migration, provider setup,
production activation or production deletion ran. Delivery remains in-review.

## Implemented scope

The strict `study.delete` version1 command accepts only operation ID and expected
metadata revision. Its DELETE route and original-operation lookup recheck current
Access before local storage. The existing **study_revision_conflict** identifier
remains the metadata conflict contract. Under operation→parent locking, overflow is
preflighted before erasure. Active notes receive the exact empty format1 value and
one revision/attribution advance; inactive note tombstones stay unchanged. Passage
entries and their header are removed before the study receives `Deleted study`,
inactive lifecycle, one metadata revision and one compact immutable receipt.
Original study.delete and note.delete receipts recover without new writes against
retained owned tombstones; earlier create/replace/rename/collection receipts refuse.

Migration0005 preserves0001–4. Ordinary receipt/title constraints, a narrow collection
header DELETE grant and small invoker parent-insert/parent-closure guards are prepared.
The controlled migrator temporarily removes FORCE inside its DDL transaction, with
RLS still enabled, to see all owned closed-parent violations; it restores FORCE before
commit. Violations fail instead of being adopted or erased. Restricted native tests
prepare rollback, overflow, raw alternate-write, concurrency, previous-f6 writer and
original-receipt proof. The actual f6b33ac6fb20a433f7b3ed72af82f9b8bc6694be DTO/storage
bytes are frozen in a new fixture with SHA256 manifest; prior frozen fixtures remain.
The next synthetic failed revision is0006. Old fixture closures now use the owned
command, and default-name preparation preserves earlier overflow rows.

The browser captures a study target, pauses target timers/new writes and retains all
unsent input, including final composition events. One preparation interval is at most
five seconds across note/title/title-read/collection/create/child-delete lanes.
Unknown prior originals recover first; a separate explicit confirmation follows.
Known creation acknowledgements survive follow-up-read failure without an extra POST.
Executing/unknown study deletion freezes the editor/formatting, retains one original
operation across navigation and exposes distinct recovery. Conflict requires current
metadata review and a fresh explicit confirmation. Acknowledged eviction is scoped
to that study; live account/lane/tombstone guards protect success and failure
continuations. Focus provenance includes the dialog's restored private trigger and
never overrides deliberate public focus. Long unbroken titles wrap inside the dialog.

## Observed test-first chronology and corrections

1. Before route/behavior implementation,
   `/tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_study_deletion.py -q -k route`
   observed the runnable missing DELETE route: **1 failed,405**. TestClient needs the
   authorized local-process escalation here; an earlier sandbox invocation stalled.
2. Before DTO/storage behavior,
   the same module with `-k 'dto or locked'` observed **2 failed** because study.delete
   was unsupported. After DTO admission alone, rerunning observed **1 passed,1 failed**:
   storage incorrectly reached the note branch and accessed the absent `payload.value`.
   Only then was the study cleanup branch implemented. Initial component completion
   passed6 cases; subsequent strict authority/replay/baseline cases passed17.
3. Before browser action implementation,
   `npm run test:browser --workspace=apps/scribeswell/web -- --grep 'whole-study deletion confirms' --workers=1`
   observed **2 failed** on desktop/mobile, missing Delete study action. The initial
   implemented confirmation check then passed2.
4. The first expanded browser iteration had **16 passed,8 failed** and included watched
   source changes, so it is not frozen verification evidence. The next iteration was
   interrupted to correct test setup synchronization: firstNote returned before its
   editor appeared, allowing tests to open deletion while creation was still finishing.
   Its partial output is `/tmp/scribeswell-study-delete-browser-2.log`.
5. Frozen focused runs reproduced acknowledgement focus failure and a mobile test
   targeting an occluded reader control. The focus correction tracks the captured
   dialog and its restored private trigger; desktop/mobile dirty acknowledgement and
   deliberate public focus passed **4 cases** in
   `/tmp/scribeswell-study-delete-focus-5.log`. Earlier failures are retained in
   `/tmp/scribeswell-study-delete-focus-3.log` and
   `/tmp/scribeswell-study-delete-safety-4.log`. A temporary diagnostic printed only
   focus provenance booleans/tag names and was removed before final verification.
6. Additional frozen tests passed6 late-read/other-study cases and reproduced **2 title
   overflow failures** plus2 test-locator failures (an alert also contains Retry).
   Anywhere wrapping corrected the actual title overflow; the locator now asserts
   the alert's contained text. `/tmp/scribeswell-study-delete-additional-6.log`.

## Verification and requirement traceability

Frozen focused browser verification:

```sh
npm run test:browser --workspace=apps/scribeswell/web -- --grep 'whole-study deletion' --workers=2
```

**50 passed,1.2min**, desktop/mobile; `/tmp/scribeswell-study-delete-browser-final.log`.
Runtime/browser test source remained unchanged during this final run. The parallel
build and generated-client check passed; only app documentation was edited while
verification was running. Earlier failing/partial iterations above are superseded
for the covered component behavior, not erased from the chronology.
Affected Python component verification:

```sh
/tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_library_search.py apps/scribeswell/tests/test_note_passage_links.py apps/scribeswell/tests/test_passage_references.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_release.py apps/scribeswell/tests/test_note_deletion.py apps/scribeswell/tests/test_study_deletion.py -q
```

**335 passed,21.84s**, one existing Starlette/httpx deprecation warning;
`/tmp/scribeswell-study-delete-python.log`. The owner-integration-named module runs
fixture/control/oracle unit checks here, never an owner environment. Its first sandbox
run had67 passed/1 PermissionError binding an ephemeral socket; the identical authorized
component command above passed outside that sandbox.

| Contract row | Executed component evidence | Prepared final-integration proof |
| --- | --- | --- |
| Cancel/confirm and owned erasure | Strict route/DTO; ordered cleanup method assertions; browser dirty and IME preservation | Restricted exact row/attribution/receipt erasure and unchanged old tombstone/non-target copy |
| All target lanes and bounded preparation | Browser executing note/title/collection/create/child-delete and five-second total wait; original save recovery | Actual local SQL owner/service request boundaries |
| Original outcomes, mismatch and uncertainty | DTO/method receipt replay/mismatch/no-write checks; lost reply and same-payload retry | SQL original study/delete note receipt recovery after closure; no duplicate effects |
| Metadata conflict, late effects and navigation | Fresh review/new confirmation; late collection success/denial; another selected study/input retained | Parent/child races, previous f6 producer, final tombstone and receipt counts |
| Current denial/account replacement/public focus | DELETE+lookup auth before storage; browser401/403, late account replies and public focus | Real owner/session denial and recovery |
| Overflow/alternate writes/old consumers | Frozen old DTO/storage hashes; compile and collection only for native paths | Parent/child overflow, receipt-failure rollback, insert/closure guards, preexisting violation rollback/FORCE restoration, old actual writer refusal |

`npm run build --workspace=apps/scribeswell/web` passed TypeScript/Vite with the existing
large-bundle advisory; `/tmp/scribeswell-study-delete-build.log`.
Owning OpenAPI export/check, reference catalogue check, shared migration-helper check,
and `python3 tools/py/run_compose_supabase.py --check-only` passed. Composition is a
read-only plan, not execution of the private Alembic history.

The generated client was produced and checked through the existing pinned owner:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node platform/deployment/.local/scaffold-application/proof-yc4xuk/root/platform/api-client/src/cli.mjs --schema /home/ck/repos/innodat/agriplatform/apps/scribeswell/contracts/personal-notes-v1.openapi.json --output /home/ck/repos/innodat/agriplatform/apps/scribeswell/web/src/generated/personal-notes --check
```

Result `api_client_current`; generated artifacts were never hand-edited.

Native preparation only:
`/tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_personal_notes_storage.py --collect-only -q`
collected **26 cases,0.45s**; `/tmp/scribeswell-study-delete-native-collect.log`.
`py_compile` passed storage, native fixture/tests, owner fixture and migration0005;
`node --check apps/scribeswell/web/tests/studies-owner.integration.cjs` passed. The
owner browser and independent oracle now prepare whole-study erasure after own-note
deletion; matching synthetic oracle inputs/tamper cases were updated together.
No SQL, actual-owner/browser/session, physical-device, backup/restore or release
qualification is established by syntax/collection/component doubles. Parent broad
browser regression and reviews are separate final evidence.

## Impact decisions

Scaffold/shared UI: reuse existing app command/error/save/focus patterns; no unproven
shared deletion engine or reusable UI promotion. Agent context: unchanged. Accepted
ADRs: unchanged; controlled-release, attribution and lifecycle rules remain binding.
Documentation: this evidence and app wire/adopted contracts record component delivery
and deferred integration. Canonical memory/spec/status and commit remain parent-owned.
Unrelated README, Leave, platform planning, KDG resources and frozen history were
preserved. No new Access/Identity/sharing/notification owner or provider/deploy path.


## Independent review corrections — 2026-10-26

All three context-free same-model BMAD review layers completed. Parent individually
triaged13 findings before grouping:12medium/1low,11 independent patch roots. Only
premature creation/ack retirement findings B3/E1/V2 share one root. No intent gap,
spec loopback, actionable defer or rejected finding. The triage record is the delivery
spec; no unrelated/private source was altered to dismiss a failure.

The same implementer corrected bounded explicit recovery and late-result checks,
definitive original child-delete/create failures, paired creation acknowledgement
materialization/retirement, acknowledged previews, explicit post-reauth preparation
restart, ordinary dirty Cancel assertions, simultaneous-lane/deadline coverage and
prepared deterministic native both-order/foreign-account proof. Back to Studies is
a tool toggle, not a flushing exit; this was corrected in the parent triage evidence.

Four desktop reds reproduced the unbounded recovery and three child-deletion traps
before correction (`/tmp/scribeswell-study-delete-review-red.log`). Focused corrected
browser24 desktop/mobile cases passed35.0s
(`/tmp/scribeswell-study-delete-review-focused.log`); expanded next-Create-study
coverage then2 passed3.2s
(`/tmp/scribeswell-study-delete-review-creation-green.log`). Native32 cases collected
0.34s and syntax passed (`/tmp/scribeswell-study-delete-review-native-collect.log`),
never executed. Source changes are limited to StudiesContext, its browser acceptance
suite and prepared native tests. Prior50/335/build evidence is pre-review; parent
broad component qualification follows. No SQL/actual-owner/session/activation claim.

The pinned client command above records the installation actually used. For portable
prerequisites and the repository-owned generator entrypoint, see
[the API-client documentation](../../../platform/api-client/README.md) and
[the existing reproducibility instructions](NOTE_DELETION_EVIDENCE.md).

## Parent regression timing failures and controlled-clock correction — 2026-10-26

The parent's frozen full regression **did not pass**:

```sh
npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --workers=2
```

The log records **488 passed,2 skipped,2 failed,9.4min** out of492 cases:
`/tmp/scribeswell-study-deletion-parent-final-browser.log`. Desktop preparation's
Node elapsed assertion received8247ms; mobile original-save recovery received8421ms,
both against `<6500`. Both had already observed the recovery control; the failures
were the subsequent elapsed assertions. Earlier isolated passes do not supersede
this failed full run, and no full rerun is claimed here.

The old assertions started Node `Date.now()` before a browser click and stopped it
after Playwright's visibility polling. That interval includes automation transport,
actionability, browser scheduling/rendering and assertion polling. The log contains
no browser timer-fire timestamp, so it cannot establish exactly when the application
callback fired in those historical failures. Source inspection found one browser
`Date.now()+5000` deadline, remaining-budget timers and a deadline recheck after each
await. Scheduling delay can still postpone observation on a loaded real host; these
component tests must measure the coordinator's total timer budget separately from
host/automation latency.

Only browser tests and this evidence changed for the correction. The application
runtime is unchanged. The two flagged tests and the related metadata-handoff case
now install Playwright's browser clock before navigation and pause it before editing.
They execute the real autosave/coordinator timer callbacks using `clock.runFor`:

- At4999 browser milliseconds, confirmation remains disabled and recovery is absent.
- At5000, recovery appears and browser elapsed time equals5000 exactly.
- The metadata case releases both prior save/collection lanes at3800, then advances
 1199+1; metadata gets only the remaining1200ms, exposing any renewed five-second
 budget at the handoff.
- Late HTTP replies are explicitly completed while the clock remains paused. They
 cannot make the expired preparation ready or issue deletion. Recovery still requires
 an explicit next action and uses the identical original operation/payload; Cancel
 preserves writing.

The parent failures above are the observed reds for this timing correction. No new
isolated reproduction of the old host-load elapsed failure is claimed. The corrected,
frozen focused command was:

```sh
npm run test:browser --workspace=apps/scribeswell/web -- --grep 'whole-study deletion preparation has one five-second|study deletion review recovery has one deadline|study deletion review metadata shares' --workers=2
```

**6 passed,5.0s**, desktop/mobile;
`/tmp/scribeswell-study-delete-controlled-clock.log`. No expected timeout was increased.
The controlled-clock result establishes the scheduled total deadline and late-result
safety under these component scenarios; it does not guarantee real-host rendering
latency. Parent full verification remains separate. No wider regression, native SQL,
actual-owner/session integration, provider setup, activation or KDG resource ran here.


## Parent final component qualification

After independent review repairs and the controlled-clock timing correction, the
parent ran the complete reader/notes suites on unchanged157-file sources:

```sh
SCRIBESWELL_TEST_PYTHON=/tmp/scribeswell-manual-python/bin/python npm run test:browser --workspace=apps/scribeswell/web -- reader.spec.cjs personal-notes.spec.cjs --workers=2
```

**490 passed,2 expected native-browser skips,9.0min**, exit0;
`/tmp/scribeswell-study-deletion-parent-corrected-browser.log`. SHA256 of the
identical before/after inventory: **17fec41877e9c00dcc07acfecf1de5ded2a479d765bfb11e189fb6ae074a8548**.
The only source changed since the parent Python/build/owning checks was the
browser test file (controlled-clock tests); runtime/migrations remained identical.

Parent affected Python command:

```sh
/tmp/scribeswell-manual-python/bin/python -m pytest apps/scribeswell/tests/test_library_search.py apps/scribeswell/tests/test_note_passage_links.py apps/scribeswell/tests/test_passage_references.py apps/scribeswell/tests/test_personal_notes_contract.py apps/scribeswell/tests/test_personal_notes_api.py apps/scribeswell/tests/test_studies_owner_integration.py apps/scribeswell/tests/test_personal_notes_release.py apps/scribeswell/tests/test_note_deletion.py apps/scribeswell/tests/test_study_deletion.py -q
```

**335 passed,22.72s**, one existing Starlette/httpx warning;
`/tmp/scribeswell-study-deletion-parent-final-python.log`. The owner-integration-named
module exercises fixture/control/oracle units, not actual owner integration.
`npm run build --workspace=apps/scribeswell/web` passed, existing chunk-size warning;
`/tmp/scribeswell-study-deletion-parent-final-build.log`. Owning exporter, catalogue,
pinned generated client, helper, composition dry-run, owner syntax/py_compile and
`git diff --check` passed;
`/tmp/scribeswell-study-deletion-parent-final-owning.log`.

Native **32 collected only**. No migration/SQL, actual Auth/Identity/Access/app or
session integration, physical-device qualification, activation or KDG resource use.
The earlier488/2/2 failure is retained above, not replaced with a claim of an
uninterrupted green run. All13 review rows/11 roots are addressed; delivery remains
in-review for the explicitly deferred final integration gates.

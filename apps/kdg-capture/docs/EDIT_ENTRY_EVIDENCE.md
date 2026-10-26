# Candidate own-edit execution entry — 2026-10-26

`web/src/edit-entry.ts:createEditEntry` combines createAuthEntry/acquireExecution with
editCapture. The consuming entry hides lease acquisition, pins configuration and checks
pending account/organization against current admitted session/context and configured org.
The adapter synchronously captures the original nested command before awaiting, preserving
its exact original operation/capture binding, generated revision/conflict types, single
same-origin PUT, strict 16 KiB safe response,131072-byte request ceiling and maximum 10-second
adapter deadline. Its budget starts inside editCapture, after the wrapper pending spread.
Synchronous wrapper capture and adapter serialization cannot be preempted; this is not an
end-to-end wall-clock bound. Every acquired lease releases in finally; every return rechecks current execution.
Ready receipts/errors replaced during cleanup become superseded. Results never update
Auth state/publications, input, saved state or queue and confer no future authority.

Refresh, account/session replacement, retry, sign-in/out, password recovery and disposal
abort old work, including late headers/body and A→B→A. Offline is qualified through prior
owner disposal and an online:false replacement using the existing host convention.
Organization changes require disposal/replacement of the fixed-organization owner.
Concurrent completion/deadline and invalid-input release preserve other current work.
Configuration mutation, nested input mutation and reentrant throwing accessors are covered.

Acceptance first ran against an explicit non-dispatching wrapper stub: strict compilation
passed and 19 behavioral tests failed, one passed. The first fixture accidentally retained
an extra recovery-only top-level operation_id; the first implementation safely refused it.
After correcting the fixture, the same retained stub was rerun:19 failures/one pass, then
all 20 cases passed with the implementation. The pre-review expanded suite passed 31. All original
attempts remain retained; no failed expectation was changed to dismiss an unexplained result.
Initial sandbox child-process EPERM was an infrastructure failure, excluded from behavioral
RED. Approved synthetic execution enabled compiler/test children without network/listeners.

Exact commands, exit codes, source and log hashes, requirement mapping and immutable
capsule copies are in [the record](evidence/edit-entry-20261026.json), retained under
`platform/deployment/.local/kdg-edit-entry-20261026`. The following results are historical pre-review observations; their sources/logs remain
unchanged. Commands use pinned Node26.11.1 at
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`:

- `node apps/kdg-capture/web/tests/auth-proof.mjs --edit-entry-only`:31 passing synthetic consumer cases; strict TS7.0.2 and compiler negative control pass; browser/listeners skipped.
- `node apps/kdg-capture/web/tests/auth-proof.mjs --unit-only`:230 pass (31 new consumer,19 recovery consumer,118 generated lifecycle,62 prior Auth/config); strict compiled source and negative control pass.
- `node --test --test-isolation=none apps/kdg-capture/web/tests/edit.test.mjs apps/kdg-capture/web/tests/recovery.test.mjs apps/kdg-capture/web/tests/entry.test.mjs`:124 pass.
- Pinned Node plus retained TypeScript compiler, `--project apps/kdg-capture/web/tsconfig.edit.json` and `tsconfig.recovery.json`: both exit0.
- Pinned Node plus `platform/builder-cli/scripts/sync-kdg-{auth,write,database,native-database}.mjs --check`: all exit0.

Post-review focused verification runs only
`node apps/kdg-capture/web/tests/auth-proof.mjs --edit-entry-only --acceptance-only`:
**38 executed, 38 passed, zero skipped**; strict TS7 compilation and its negative control
also pass. Edit-only selection takes precedence over the legacy acceptance name filter.
The result records selected mode, selected files and total/executed/pass/fail/cancelled/
skipped/todo counts, refusing success when no tests execute. The consuming cases now
prove admitted replacement-organization success, pending/denied/unavailable admission
with no PUT, a combined held-edit/offline/late-response sequence, and invalid timeout
boundaries with preserved admission and unaffected independent valid work. Runtime
wrapper/adapter remain unchanged. [Post-review proof](evidence/edit-entry-post-review-20261026.json)
retains separate source/log metadata under the existing post-review directory. The earlier
31/230 results and all prior sources/logs are historical; broader final verification is
completed by root after these corrections: **237 compiled Auth cases**, **124 direct
edit/recovery/entry cases**, strict TypeScript7.0.2 adapter configurations and all four
scaffold parity checks pass. The legacy acceptance-only invocation also passes its one
selected case. All three review layers completed; seven findings addressed, none deferred.

The capsule captures new source/types/tests and edit generated contracts while preserving
existing unit/browser options, dependency checks and source-bound results. Five expected
consumer typing failures prove hidden acquisition, required capture, string revision,
conflict-only current_revision and immutable receipt. Upstream skipLibCheck remains the
existing Auth proof limitation; application source is strict. No dependency was installed.

Scaffold impact: existing neutral lifecycle reused unchanged; no template/generated or
neutral behavior correction. No shared UI, agent-context or ADR changes. Documentation:
this evidence, machine receipt, appended contracts and prepended handoff; historical
prefix/suffix bytes verified and retained. Synthetic local/CI only: no actual Auth/accounts/
Access, backend/native, Docker, browser/editor/startup activation, migration, provisioning,
deployment/production/pilot or cleanup. Preexisting untracked migration/schema_fixture.py
was never read/run/edited. Existing concurrent changes/resources/dependencies and historical
evidence remain intact; fingerprints/HMAC deferred. Cancellation/deadline may still commit;
there is no automatic retry, refresh/sign-in, recovery, new operation, Synced feedback or
rollback/absence claim. Synchronous JSON preflight retains the adapter's existing
non-preemptible serialization limitation.

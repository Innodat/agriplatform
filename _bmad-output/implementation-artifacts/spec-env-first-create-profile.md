---
title: 'ENV: validate the complete first-create invocation'
type: feature
created: '2026-10-16'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 38767f699b6b3fe4724c665cc654349e3db0f088
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing bounded shared-foundation implementation approval; user requested next">

## Intent

**Problem:** The current first-create proof checks selected fields but accepts arbitrary
option values, environment names and shell content. Immutable image substitution alone
cannot qualify a request for eventual execution.

**Approach:** Validate the complete selected Supabase PostgreSQL create profile and its
container-input environment at the existing private executable boundary. Preserve the
validated request through digest substitution, then refuse creation as before.

## Boundaries & Constraints

**Always:** ATDD failure first, focused TDD, existing ENV owners and exact dependency pins
including TS7.0.2/CLI2.120.0. Preserve concurrent Leave/PtS work and existing receipts.
Compare every argv operand with the source-backed supported Linux/PG17 profile; only
run-derived identity/path/network/port and owner-qualified image vary. Exact ordered
profile is acceptable for this pinned CLI. Require exactly its four key-only container
environment names and expected synthetic values in memory. Validate relevant Docker
client routing against the private invocation; do not mistake arbitrary inherited
process variables for container inputs. Snapshot inputs once, validate before and after
transformation, change only the image operand, and reject mutation before a positive
create event. Fixed public upstream bootstrap bytes may have a source-derived digest;
never hash/log secret-bearing runtime input. No raw argv, environment values, SQL,
response dumps or credential hashes in events/results/errors. Source-bind the profile
and validators. New source binding requires fresh qualification, never receipt repair.

**Never:** Execute shell/SQL or containers; real Docker mutations/pulls, account/grant
changes, migrations, provisioning/deployment/pilot. No live secrets or general command
proxy/parser, generator or offline service. Do not enable up, implement Leave/KDG or
advance Identity/Access/WRITE. This proves source/profile conformity and custody only
through refused dispatch, not bootstrap semantic safety, secret-file delivery, image/
resource continuity during execution, complete startup or runtime readiness.

## I/O & Edge-Case Matrix

| State | Expected result |
| --- | --- |
| Actual pinned CLI, exact supported create and inherited inputs | Profile accepted, immutable image only changed, create refused |
| Missing/extra/duplicate/reordered/changed flags or operands | Refuse before positive create event |
| Changed/appended bootstrap bytes, SQL/path/interpolation | Refuse without executing or exposing content |
| Missing/extra container env name, inline value, changed inherited value/routing | Refuse safely; unrelated process variables do not become container inputs |
| Input mutation or transform changes another operand | Refuse; original caller inputs preserved |
| Stale/changed profile/source/owner evidence | Existing guards refuse; no evidence repair |
| Sensitive canaries in any invalid input/error | Safe codes/events only; no canary or derived secret digest |
| Existing valid/negative startup paths | Remain bounded, first-create refusal and runtime_ready=false |

</frozen-after-approval>

## Code Map

- `platform/deployment/startup.py:create_facts,immutable_first_create,fixture_command,
  fixture_main,install_fixture,synthetic_probe`: selected-field checks at272 currently
  permit arbitrary final script and optional values. Keep owner provenance/resource and
  process-parent guards. Pass an explicit in-memory environment snapshot from the wrapper;
  direct unit fixtures supply explicit synthetic environment, never an implicit bypass.
- New small `platform/deployment/create_profile.py` owns only this pinned profile.
  Reuse fixed identity/selection validation; require complete argv and four container
  inputs (POSTGRES_PASSWORD, POSTGRES_HOST, JWT_SECRET, JWT_EXP). Published synthetic
  defaults come from pinned upstream, not user credentials. Docker routing derives from
  fixture workdir/clean invocation. Preserve safe selected_facts; add precise proof flag.
- Profile authority under `platform/deployment/fixtures/`: retain reviewed public bootstrap
  bytes or a documented exact digest with independently constructed test fixture. No
  runtime learning/auto-approval from observed CLI output. Bind in dev.SOURCES and
  test_dev.FILES; source_snapshot already includes these. Do not hand-edit generated files.
- Primary source commit `753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4` at github.com/supabase/cli:
  `apps/cli/src/command-internal/db-bootstrap/postgres.service.ts` fixes PG17 script,
  healthcheck10s/2s/3, restart unless-stopped, aliases db/db.supabase.internal;
  `docker-create-args.ts` fixes option ordering; `container-lifecycle.ts` adds project/
  workdir labels and inherits four env values; `local-container-inputs.ts` adds Linux
  host.docker.internal:host-gateway. Public script templates are
  `db-bootstrap/templates/db-{schema,webhook,supabase}.sql.ts`; empty settings append
  the fixed configuration header. `packages/stack/src/Defaults.ts` supplies public local
  password/JWT defaults; config owns JWT expiry. Sources downloaded for investigation
  are `/tmp/env-next-{1,args,lifecycle,inputs,schema,webhook,supabase,defaults,values}.ts`.
  Verify resulting bytes against actual pinned CLI; do not substitute captured output as
  authority. Root can assist fresh owner qualification after bound sources freeze.
- `tests/test_startup_adapter.py` currently accepts invented script/minimal argv: replace
  those profiles with explicit complete synthetic inputs while preserving prior assertions.
  New `tests/test_create_profile.py` supplies independent expected requests and mutations.
  Extend existing `tests/qualify_startup.py` only as needed for public profile-negative
  controls, through the same process boundary. No new public real-daemon entry point.

## Tasks & Acceptance

- [x] Observe unsafe-request acceptance RED; implement full profile and environment custody.
- [x] Prove every matrix row, including process-boundary handoff and mutation tests.
- [x] Run affected tests then full deployment suite; fresh pinned CLI positive/negative
  proof with unchanged retained evidence. Run public qualification and full suite serially
  because owner revalidation reserves target ports.
- [x] Update DEVELOPMENT.md, ENV_FIRST_CREATE_PROFILE_EVIDENCE.md, KDG next-session/memlog;
  record requirement/test and scaffold/UI/context/documentation/ADR impacts.
- [x] Independent review, fixes, final verification and scoped local commit.

**Acceptance:** Given qualified owner evidence and the supported invocation, when the
actual pinned CLI reaches the private wrapper, then the complete request is validated,
only the image is transformed and create remains refused. Given any unsupported input,
when the boundary is reached, then no positive create event, execution or sensitive
output occurs.

## Implementation Notes

No user intent gap or irreversible action. Implementer owns code/tests/runbook; root
owns evidence/navigation/memlog, final public qualification and commit. Static upstream
bootstrap SQL conformity does not authorize its execution or repository migrations.

## Spec Change Log

## Review Triage Log

All three layers returned before triage. Each finding is recorded separately; B1/E1
share the environment-override root cause. All surviving fixes are local corrections
or focused proof additions, with no public surface or new intent. No deferrals.

| Finding | Verdict / route | Verified evidence |
| --- | --- | --- |
| B1 missing DOCKER_TLS | medium / patch | ROUTING_KEYS omits it; exact valid inputs plus this override pass. Docker CLI documents its TLS effect. Reject it and other documented request-affecting overrides. |
| B2 tuple inconsistency | low / patch | fixture_command admits tuple then compares slices to lists; valid tuples miss create handling. Direct recognition correction, retain mutation checks. |
| B3 unvalidated negative-control baseline | medium / patch | install_fixture changes original argv/env before validation; existing bad input can produce the same qualifying rejection. Validate baseline before injection. |
| B4 fixture reproduction | low / patch | Authority gives source/hash but no exact extraction/assembly command; whitespace/escape regeneration cannot be repeated from instructions. Add documented commands only. |
| B5 circular test helpers | low / patch | test_startup_adapter imports test_create_profile; latter manually calls BoundaryControls.setUp. Shared fixture lifecycle can diverge when setup gains cleanup. Extract existing helpers. |
| B6 validator boundaries | medium / patch | New type/count/length/environment guards have no focused boundary cases. Add cases to prevent silent guard regression. |
| B7 stale safe-output assertion | low / patch | Previous invented script marker is absent from all new requests, making the assertion vacuous. Assert actual script absence/safe schema. |
| B8 wrapper event assertion | medium / patch | Real wrapper tests check only last event kind; extra events/fields pass. Assert complete records. |
| E1 missing DOCKER_TLS | medium / patch | Same verified omission as B1; group for one correction while retaining this finding row. |
| V1 negative-control prerequisite proof | medium / patch | Reviewer verified removal of branch validate_observations remains undetected; inject missing/duplicate/reordered prerequisites and preceding positive create through synthetic_probe. |


## Verification

Focused create-profile/startup tests, affected test_dev/image/resource suites, then
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`.
Fresh prepare/tool/image owner qualification; actual pinned CLI public startup positive
and existing/new exact negative controls. Preserve thirteen evidence files/source
bindings. Compile, scoped whitespace and local links; real up must remain gated.

Initial verification: acceptance RED observed; six create-profile and38 startup tests pass. Root read implementation/test changes and independently verified public fixture bytes. Eight matrix rows have focused or existing guard coverage; fresh public proof and full sequential regression remain pending, not claimed complete.

Initial actual pinned CLI positive control passed on run `d73e4702-9e0e-474e-a1b6-46093ed46011`, with nine observations and complete profile proof, create refused. Review fixes change bound sources; retain this run unchanged and use a fresh final run.

Final verification: post-review profile10/startup38 focused tests pass. Fresh final run
`dd2afb69-8065-4304-ba71-e244a1539bc9` passes prepare/tools/images and eight public controls,
with thirteen retained files and source bindings unchanged. Protected record SHA-256
`08fbfdd287f51b0ccb8082db0ccf23e20dbbcc3b72a3a62e80ef3311753fb5f5`.
Full deployment suite:325 tests,72.060s,OK,no skips. Real up:exit2/docker_28_required.
Public derivation independently reproduces9642 bytes and expected hash. Python compilation,
scoped whitespace and local links pass. All ten review instances fixed (nine distinct
corrections), none deferred; final review diff refreshed. See owner evidence for exact
commands, results and requirement traceability. Scoped local commit excludes Leave/PtS.

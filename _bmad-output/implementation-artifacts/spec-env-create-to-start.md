---
title: 'ENV: qualify the PostgreSQL create-to-start sequence'
type: feature
created: '2026-10-16'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: fa21c3637d2d6cdba5d1856ee0c7b5a2568d6f41
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing bounded shared-foundation implementation approval; user requested next">

## Intent

**Problem:** Refusing the first create prevents the pinned CLI proof from reaching its
required secret-file transfer and start boundary. That leaves a concrete startup
sequence unqualified despite complete create-profile validation.

**Approach:** Extend the existing synthetic startup fixture to acknowledge one validated
PostgreSQL create, validate the source-backed stdin archive transfer to that synthetic
container, then refuse its first start. Preserve existing refused-create controls.

## Boundaries & Constraints

**Always:** ATDD failure first, focused TDD; exact approved pins including TypeScript7.0.2
and Supabase2.120.0. Reuse existing profile/image/resource/owner evidence and protected
process fixtures. Keep simulated create distinct from actual container creation. Validate
exact sequence and synthetic identity, bounded stdin and one permitted archive member,
content/metadata in memory only. No extraction, archive persistence or secret hashes.
Events/errors/results contain safe facts only, never raw transfer bytes, secret values,
argv/environment dumps or untrusted member names. Kill only the proven pinned parent
at terminal refusal, preventing CLI cleanup; existing time/output/ancestry guards remain.
Fresh qualification after source changes; never repair receipts. Preserve concurrent work.

**Never:** Real Docker dispatch, mutations, pulls, containers, shell/SQL execution,
production migrations/access/accounts/provisioning/deployment/pilot; Leave/KDG domain
or Identity/Access/WRITE. No generic proxy, archive extractor, offline service or new
public generation workflow. No claims of bootstrap safety, real secret installation,
volume freshness or execution continuity. dev.py up remains gated, runtime_ready=false.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Actual pinned CLI exact create → archive → start | Simulated identity returned, transfer validated, start refused; no execution |
| Invalid create/profile/environment/image | Existing safe refusal; no lifecycle success |
| Wrong container/destination, extra or unsupported operation | Refuse before start; no cleanup dispatch |
| Missing, duplicate or reordered create/transfer/start | Refuse; incomplete evidence cannot qualify |
| Wrong content/path/type/mode/ownership, extra members, links/traversal/extended headers, malformed/truncated/oversized/compressed/trailing archive | Refuse safely without extracting or retaining input |
| Slow/nonclosing stdin, wrong parent, source/evidence mutation or interruption | Bounded failure, no proof/replay claim |
| Sensitive sentinel in invalid archive/errors | No output/event/hash disclosure |
| Existing eight controls | Same results and evidence integrity |

</frozen-after-approval>

## Code Map

- `platform/deployment/startup.py`: reuse fixture_command/main, install_fixture,
  synthetic_probe/qualify, validate_observations, parent_identity and event_file.
  Current create always returns125; add explicit synthetic lifecycle mode only.
  Wrapper may consume stdin only for exact allowed cp invocation, with byte/time bounds
  before parsing. Preserve lock serialization and exact prerequisite event oracle.
- Small `platform/deployment/startup_lifecycle.py` may own bounded archive/profile and
  sequence checks. Reuse create_profile.validate/immutable_first_create, never duplicate
  create argv authority. Synthetic container ID is fixed/derived safe64hex, never daemon
  authority. Compare transfer contents to public pinned local root-key default in memory.
- Pinned source commit753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4:
  `apps/cli/src/command-internal/db-bootstrap/container-lifecycle.ts` creates, copies
  secretFiles via `docker cp - <returnedID>:/`, then `docker start <returnedID>`.
  `postgres.service.ts` supplies exactly `/etc/postgresql-custom/pgsodium_root.key`.
  `apps/cli/src/shared/functions/functions-docker.ts:containerArchiveBytes` strips leading
  slashes and uses Bun.Archive, documented0644. `packages/stack/src/Defaults.ts` owns
  DEFAULT_POSTGRES_ROOT_KEY. Retained investigation files `/tmp/env-next-lifecycle.ts`,
  `/tmp/env-next-1.ts`, `/tmp/env-next-defaults.ts`, `/tmp/env-lifecycle-functions-docker.ts`.
  Verify actual pinned archive format/metadata rather than infer them. Characterization
  may emit safe metadata only, never input bytes or contents. Source-backed authority
  note goes in fixtures; no captured secret artifact becomes authority.
- `tests/qualify_startup.py`: extend existing controls with lifecycle positive and
  wrong-target/archive/order negatives; no real endpoint flag. Negative injection must
  first validate the original input, so preexisting invalid requests cannot qualify.
- `tests/test_startup_lifecycle.py`, existing startup/profile helpers: independent tar
  fixtures, process-boundary/order/timeout/canary tests and actual pinned CLI proof.
  Do not increase existing command deadlines to hide a failure. If size format needs
  a bounded adjustment, justify from primary source/observed synthetic metadata.
- Bind new production/source authority in dev.SOURCES/test_dev.FILES. Preserve prior
  startup APIs/default controls. No Docker transport changes needed.

## Tasks & Acceptance

- [x] Observe lifecycle acceptance RED; implement bounded sequence/transfer validation.
- [x] Cover every matrix row with focused tests and preserve old controls.
- [x] Fresh prepare/tool/image qualification; actual pinned CLI lifecycle and old controls,
  unchanged retained evidence; full deployment regression sequentially afterward.
- [x] Update DEVELOPMENT.md, ENV_CREATE_TO_START_EVIDENCE.md, KDG next-session/memlog,
  requirement/test links and all five impact decisions.
- [x] Independent review, fixes, final checks and scoped local commit.

Given current qualified evidence, when the pinned CLI reaches post-create delivery,
then exact synthetic transfer is validated and first start refused without execution.
Given unsupported input or incomplete sequence, when qualification evaluates evidence,
then it fails with no sensitive output or false success.

## Implementation Notes

No unresolved intent choice or irreversible action. Implementer owns code/tests/runbook;
root owns evidence/navigation/memlog, final public qualification and commit. Record real
runtime gates together: helper inventory, bootstrap/secret policy, daemon/resource session
continuity and volume reuse, lifecycle/recovery/health, target PG compatibility and later
owner migrations. P1/SERVICE/provider/device proof stays separate. Do not implement them
inside this slice. Standing approval covers this bounded scope without another checkpoint.

## Spec Change Log

## Review Triage Log

All three layers returned before triage. Runtime agent capacity required sequential
reviewer launches; no layer was skipped. Each finding has its own verdict below.
B1/B2/E1 share injection-evidence failure; B3/E2 share numeric/header parsing mismatch.
All corrections are local, demonstrate current states, add no public surface and route
to patch. No intent gap, decision change or deferred work.

| Finding | Verdict / route | Verified evidence |
| --- | --- | --- |
| B1 premature original start qualifies order control | medium / patch | The negative oracle accepts ten events ending with the ordinary early-start rejection; it does not require actual baseline validation/injection. Add explicit safe injection evidence. |
| B2 invalid-baseline sequence coverage missing | medium / patch | Tests mutate archive contents only; missing transfer/premature start bypasses that path. Add original sequence/target/duplicate cases to qualification tests. |
| B3 header alternatives exceed stated profile | medium / patch | number strips leading NUL; root reproduced validator0644 versus standard tar0000 with valid checksum. Narrow numeric syntax and regular type; document accepted padding. |
| B4 independent malformed numeric/header cases absent | medium / patch | Matrix lacks recomputed-checksum numeric/base256/device/magic/prefix cases. Add independent header mutations so checksum failure cannot mask parser gaps. |
| B5 total deadline lacks trickle proof | medium / patch | Existing tests stall after one chunk; resetting deadline per chunk would pass. Add bounded continuously supplied input proof. |
| B6 repeated event boundaries | low / patch | New oracle repeats9/10/11 across create/copy/start/public checks; future prerequisite edits can diverge. Direct shared boundary constant/derived offsets, no generic state machine. |
| B7 documentation spacing and padding | low / patch | Owner docs conflate9216 bytes after padded block with total padding; actual member contributes448 additional zero bytes. Correct prose/spacing. |
| E1 premature start qualifies negative control | medium / patch | Same verified missing-injection evidence as B1; retain separate row, grouped correction. |
| E2 leading NUL numeric interpretation differs | medium / patch | Independently reproduced using TarInfo.frombuf after recomputing checksum: mode0000 versus validator0644. Reject syntax with ambiguous termination. |
| V1 transfer refusal cleanup not proved | medium / patch | Reviewer verified CLI fixture exits voluntarily on cp failure before cleanup sentinel. Add sentinel immediately after cp returns, before exit handling, and prove parent termination prevents it. |


## Verification

Focused lifecycle then startup/profile suites; exact commands/results in evidence.
`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'` after public
qualification, never concurrently. Fresh owner qualify and existing public startup
entry point; preserve thirteen evidence files and source hashes. Compile, scoped
whitespace/local links; real up must still refuse. Five impacts: ENV scaffold extension;
no shared UI/context change; owner docs updated; existing ADRs apply unchanged.

Initial matrix audit: eight lifecycle tests plus38startup/10profile tests pass; root read the staged diff and verified matrix coverage. Fresh public/full regression and final documentation remain pending; independent review evaluates implementation while those final checks are prepared.

Final verification: 338 deployment tests passed (131.579s), twelve public controls
passed on frozen-source run `26c17c4a-9896-4940-b712-be9d1c80be0f`, thirteen retained
file identities/source snapshots unchanged. All ten review instances fixed, none
deferred. Real up refuses `docker_28_required`; runtime remains unqualified. Compile,
whitespace and local links passed. Exact commands, failed attempts, test traceability,
record hash and five impacts are in
[owner evidence](../../platform/deployment/ENV_CREATE_TO_START_EVIDENCE.md).

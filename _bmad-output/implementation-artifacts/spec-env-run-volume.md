---
title: 'ENV: acquire and verify the run-owned database volume'
type: feature
created: '2026-10-15'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 8462b3b6d2d6241d795c66627a2a65daa1117c7b
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing bounded shared-foundation implementation and synthetic verification approval; user requested continue">

## Intent

**Problem:** Preparation reserves a database-volume name different from the pinned CLI,
and the startup fixture invents a volume without proving ENV ownership. Startup needs
a reusable acquisition adapter before activation can safely consider persistent storage.

**Approach:** Align the reserved identity with supabase_db_<project>; acquire and inspect
only that run-owned local volume through the existing bounded Docker transport. Prove
the adapter and startup descriptor handoff through private synthetic fixtures, keeping
real startup disabled.

## Boundaries & Constraints

**Always:** Preserve approved dependency pins, prior immutable receipts, concurrent
Leave/PtS changes and owner boundaries. Observe behavioral acceptance red before code;
use focused TDD. Require valid protected preparation/source bindings and Linux Docker
>=28 before volume API operations. Fixed /var/run/docker.sock only in the adapter;
internal synthetic injection has no CLI/environment endpoint override. Inspect exact
reserved name; POST only after404, then validate returned descriptor and reinspect.
Require Name exact, Driver=local, Scope=local, exact four ENV owner/target/run/project
labels plus com.supabase.cli.project and com.docker.compose.project, and no driver
options (Options must be present and null or empty object). Reject cluster-volume
metadata. Preserve selected observation continuity before handoff; CreatedAt, when
present, is a bounded string checked for changes. Never follow or publish Mountpoint.
Use existing protected same-run lock, total deadline, bounded HTTP framing and safe
codes. Recheck preparation/source/run/lock before mutation and handoff. Foreign
collisions or unsafe responses refuse without repair/deletion. Ambiguous POST has no
retry/delete; later explicit attempts inspect first. Docker may return201 for existing
volumes: report verified profile and whether POST was attempted, never newly created.
Validate the acquired descriptor at the existing startup fixture boundary; maintain
first-create refusal and exact volume/mount-name coherence.

**Never:** Real Docker mutations, containers, pulls, SQL/migrations, accounts/access,
infrastructure/deployment or real-data pilot. Do not activate dev.py up or dependent
Identity/Access/WRITE/Leave/KDG work. No new transport, generic proxy/generator/offline
service, accepted ADR edits or receipt repair. No immutable-volume-ID, empty/unused/
unattached, kernel isolation or runtime readiness claim; Docker local volumes are
name-addressed and ordinary inspection does not prove use. Keep runtime_ready=false.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Prepared run, volume absent | Exact POST and independent reinspection; verified name handed to startup, no execution |
| Owned existing volume | Reuse verified descriptor without POST; null/empty options admitted |
| Foreign existing or racing foreign POST winner | Refuse; no adoption/repair/delete |
| Wrong name/labels/driver/options/cluster metadata | Safe refusal; no unsafe handoff |
| Lost/malformed/oversized/slow/error response | Bounded safe failure; at most one POST |
| Changed preparation/source/run/lock or observed descriptor | Refuse before mutation/handoff as applicable |
| Same-run concurrent operations | Bounded serialization on existing run resource lock |
| Missing preparation/old daemon | Refuse before volume API; real up stays gated |

</frozen-after-approval>

## Code Map

- `platform/deployment/dev.py:expected_inventory,docker_exchange,SOURCES`: fix reserved
  volume name to actual CLI convention; add only exact v1.48 volume inspect/create
  routes. Include new adapter/qualifier in source binding. Keep network/gate behavior.
- New `platform/deployment/volumes.py`: reuse preparation, protected paths, UUID checks,
  shared transport and `networks.run_lock`. Existing .network-UUID.lock now serializes
  both resource adapters; document this reuse rather than building another lock system.
- `platform/deployment/startup.py:fixture_command,install_fixture`: validate a complete
  volume descriptor and return it on synthetic inspect; preserve volume-create refusal,
  PostgreSQL mount identity and all guarded immutable-create/probe behavior. Avoid
  circular imports; shared descriptor checks belong in one owning location.
- `tests/test_dev.py:FILES`, new `tests/test_volumes.py`, `tests/qualify_volumes.py`:
  reuse fixture infrastructure where suitable, with independent literal request oracle
  and complete ordered API observations. Extend startup focused tests for handoff.
- Docker28 volume router/store return existing volumes via201 unchanged; no volume ID.
  API types document Options and optional CreatedAt, Mountpoint and ClusterVolume.

## Tasks & Acceptance

- [x] Add failing behavioral acceptance and characterize changed existing boundaries.
- [x] Implement reserved identity, bounded acquisition and startup descriptor integration.
- [x] Execute private public positive/negative controls and affected tests; actual pinned
  CLI still reaches refused first-create with the verified expected volume name.
- [x] Record requirement/test evidence and five impacts in new
  `platform/deployment/ENV_RUN_VOLUME_EVIDENCE.md`, runbook, KDG navigation and memlog.
- [x] Independent review/fixes, final focused then regression checks, scoped local commit.

**Acceptance:** Given a current prepared disposable target, when private-daemon volume
qualification runs, then only the exact owned local volume is acquired/verified and
its descriptor is accepted by the startup boundary. Given unsafe or changed evidence,
when acquisition runs, then it refuses safely with no unverified handoff. No public
command executes a real volume/container mutation and real up remains gated.

## Implementation Notes

No unresolved intent gap or irreversible action. Multi-file owner extension uses
dispatch. Implementer owns code/tests and appended runbook section; root owns evidence,
navigation, spec finalization and memlog. Preserve other files. Fresh source changes
invalidate old preparations; never rewrite old run evidence.

## Spec Change Log

## Review Triage Log

All three layers completed; edge-case layer returned no findings. Each finding
instance was classified before grouping. B7/V1 share the forwarding-verification gap.

| Instance | Verdict / route | Evidence and action |
| --- | --- | --- |
| B1 | medium / patch | volume_descriptor permits bounded arbitrary CreatedAt and qualifier serializes result.volume; omit this text from public diagnostics, retain internal observation and add marker regression. |
| B2 | low / patch | public qualifier closes its private daemon and acquisition lock before separate startup proof. This is descriptor transfer, not continuous locked handoff; clarify the documented boundary. |
| B3 | medium / patch | racing-owned currently uses the same initial/POST descriptor as positive; distinguish winner observation and assert preservation so fixture actually proves the claimed case. |
| B4 | medium / patch | same-run lock cases exist but no two-run adapter/cross-descriptor regression. Add independent acquisitions and cross-run rejection to protect run isolation. |
| B5 | medium / patch | negative descriptor tests reach inspect only; create has a separate new guard. Exercise valid create argv with unsafe descriptor and assert no create event. |
| B6 | low / patch | synchronous internal callback cannot be preempted by the subsequent deadline check. Document trusted immediate nonblocking constructor precondition and checked, non-preemptive deadline; no public arbitrary callback or real startup is present. |
| B7 | medium / patch | public entry forwarding is unprotected by automated integration; removing it falls back to invented valid fixture. Add an end-to-end descriptor observation assertion and acquisition-refusal guard. |
| V1 | medium / patch | pre-verified regression gap: either forwarding hop can be removed without failing current tests/manual success checks. Same root cause as B7; independent acquired CreatedAt observation must reach process fixture. |


All eight instances are fixed; none deferred. The implementation worker was re-engaged
for patches but stopped responding, including after restart; root applied the minimal
patches under the workflow fallback. The CreatedAt marker regression failed before
redaction. Both forwarding-removal mutations independently produced one expected
assertion failure (`boundary_not_proven`), no errors; repository source bytes were
not mutated by that experiment. Restored focused suites: volume 19/19 (10.688s),
startup 38/38 (11.367s).

## Verification

Focused `python3 -m unittest discover -s platform/deployment/tests -p test_volumes.py`,
affected dev/network/startup tests, then `-p 'test_*.py'`. Fresh prepare and public
`tests/qualify_volumes.py` controls against private Unix daemon only. Repeat pinned
CLI startup proof with fresh existing tool/image qualification. Record exact results,
source/evidence preservation, compilation, scoped whitespace and local-link checks.

Initial root regression: 294 deployment tests passed in 58.221s, no skips. All 15
volume and five startup public controls passed; retained 13 evidence files unchanged.
See owner evidence for command matrix and protected record hash. Independent review
and final documentation/commit remain in progress.

Final regression first ran 299 tests in 115.729s with one error in the existing
detached-process cleanup test: `/proc/<pid>/stat` disappeared between existence
check and read (`ProcessLookupError`). The test now accepts FileNotFoundError or
ProcessLookupError as observed termination; its live-process failure remains.
Focused cleanup regression passed (1 test, 0.467s). No bound proof source changed.

The next full run (299 tests, 108.277s) exposed the identical `/proc` read race
in the other existing grandchild-cleanup test. Applied the same narrow termination
handling there; its focused test passed (1 test, 0.306s). Neither change alters
production cleanup, deadlines, or the assertion against running descendants.

Final result: 299 deployment tests passed in 96.309s, no skips; all 20 public controls
passed on 3d701a44-6ed0-4dba-9eef-e851dc957a51, retained evidence/source bindings
unchanged. Eight review instances fixed, none deferred. Two observed pre-existing
cleanup-test races corrected with focused passing checks. Compilation, whitespace
and local links pass; real up still refuses docker_28_required. Five impacts and
remaining runtime/scaffold gates recorded in owner evidence and KDG navigation.

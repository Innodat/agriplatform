---
title: 'ENV owned disposable Kong lifecycle'
type: 'feature'
created: '2026-10-19'
status: 'done'
route: 'dispatch'
baseline_commit: 'd21e24b171ebd03648f32aa987e4d2758c710dcd'
review_loop_iteration: 0
---

<frozen-after-approval reason="standing bounded ENV implementation and isolated synthetic verification approval">

## Intent

The validated Kong profile cannot yet execute through its retained owner. Add one
opt-in `pinned-cli-postgres-kong-execution` qualification: existing guarded setup,
then owned Kong create/three-file transfer/start/health/stop/disposal and complete
normal cleanup. Prove this lifecycle with private synthetic peers before actual
Docker qualification; retain runtime_ready/fresh_setup_completed=false.

## Boundaries & Constraints

Always use existing profile/archive/resource/transport/qualifier owners. Extend the
completed tail/boundary chain; original CLI stays terminated. Consume attempts before
checks/mutations, require all previous proofs, exact selected image ID/platform/Config,
current fixture/tail/PG custody and healthy same PG. Preserve existing boundary and
ordinary controls, including both default classifier refusals.

Only the new owner supplies private per-exchange `_kong_fixture` through existing
DockerSession.exchange/_docker_request. Persistent-only, exact fixture-derived
canonical disposable create or exact name GET; complete typed profile comparison.
No retained session flag, boolean bypass, public option or generic route expansion.
Without this operand both Kong creates remain refused. Existing binary archive and
ID inspect/start/stop/delete routes suffice. Recheck the fixed API port before create.

Require name absence, mark creation uncertain before dispatch, accept only canonical
unique ID/clean warnings; never adopt/retry uncertain resources. Inspect exact created
container, transfer validated three-file archive once, inspect again, start once,
then observe healthy same running instance. Bind image/name, full expected effective
Config (Env/labels/user/workdir/command/ports/health/stop), Path/Args, safe HostConfig,
empty mounts, own network/known aliases, restart count and typed state/timestamps.
Permit only explicitly identified Docker empty/default normalizations, not arbitrary
inherited data. `_joint` may allow only retained PG/Auth/Kong IDs; volume references
remain PG-only. No generic container or image-default trust.

Keep create/copy/start/health within the original120s execution deadline. Shutdown
of Kong then PG shares one15s deadline; never reset it between services. Cleanup is
one10s attempt: Kong first, then existing PG/volume/owned bridge; verified normal
exit uses non-force deletion plus404. Failure cleanup requires current known ownership;
uncertain creation, closed session or ownership loss preserves resources. Never
reconnect/replay or delete storage/network under uncertain/live Kong. Publish separate
Kong lifecycle facts only after complete cleanup/final custody. New result must not
misrepresent default refusal as refusal of its executed scoped create.

Never add SQL, native-token minting, generic service/generator tooling, runtime/Auth
routing readiness, real Docker execution in this increment, production/accounts/
access/infra/deployment/data/push work. Preserve current pins incl TS7.0.2/mail15484,
concurrent work/index, historical receipts/evidence and uncertain Docker resources.
Transfer content/Env/logs/health payloads must not enter diagnostics, hashes or evidence.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected result | Failure |
| --- | --- | --- | --- |
| Positive lifecycle | All proofs/current profile/image/resources | Exact ordered lifecycle, shared budgets, normal cleanup then fact | Readiness false |
| Bad profile/transfer/order/replay | Changed input or repeated/premature call | No later mutation or success | Safe existing refusal |
| Unknown create | Existing name, malformed/colliding ID or lost response | No adoption/replay; uncertain resources retained | No PG/storage/bridge deletion |
| Custody/state change | Wrong identity/config/network/mount/instance or unhealthy/failed exit | No success; current-ownership cleanup only | No payload disclosure |
| Expiry/cancellation/cleanup fault | Any lifecycle boundary fails | Original error/no replay; no success facts | Preserve uncertainty |
| Ordinary/boundary controls | No execution opt-in/operand | Same behavior and default Kong refusals | No added authority |

</frozen-after-approval>

## Code Map

- `platform/deployment/resources.py`: FreshGuard enable/execute/owned/stop/remove
  methods, _joint, finish_execution, cleanup_execution. Reuse Auth/PG patterns but
  keep Kong state/attempts/uncertainty separate. stop_instance must retain the shared
  shutdown deadline when Kong execution opts in; ordinary budgets unchanged.
- `platform/deployment/dev.py`: private per-exchange fixture validation/admission;
  no ordinary allowlist widening. `create_profile.py` and `startup_lifecycle.py` own
  canonical disposable request, closed image Config, archive and shutdown_state.
- `platform/deployment/startup.py` and `tests/qualify_startup.py`: opt-in mapping,
  owner dispatch after boundary and honest post-cleanup result; no resumed CLI.
- `platform/deployment/tests/test_pinned_execution.py`: extend existing private
  daemon with independent Kong rows/transitions; owner failure/custody/budget tests.
- `platform/deployment/tests/test_resources.py`: existing real private Unix peer/CLI
  supervision acceptance, ordered success and fault/privacy/cleanup controls.
- `platform/deployment/tests/test_docker_session.py`, `test_create_profile.py`,
  `test_startup_adapter.py`, `test_dev.py`: scoped transport/profile/mapping regressions.
- `platform/deployment/DEVELOPMENT.md`, ENV_KONG_EXECUTION_EVIDENCE.md,
  `apps/kdg-capture/docs/next-session.md` and .memlog.md: root-owned evidence/impacts.

## Measured prerequisite correction

Root ordinary process verification exposes existing five-second acquisition and Auth
handoff liveness failures before Kong (retained root-ordinary-process and
root-api-isolated logs). One instrumented unchanged synthetic API run passes21.424s:
217337 dev.read calls8.465s,1731 evidence checks14.177s,1691 fixture custody5.124s,
1216 exchanges0.953s (inclusive/nested; never add these durations). Alarm causation
and original failure attribution remain unproved. Preserve the logs, not just passes.

Make a bounded implementation correction through the existing filesystem/source
owners: reuse securely opened parent directory descriptors only within each fresh
source_evidence/source_snapshot/file_snapshot invocation. Freshly open/read/check
and hash every file on every call, preserve each existing logical observation and
file signature before/after check. Rewalk each parent path using existing nofollow
directory traversal and verify held/current device+inode before returning a snapshot.
No cached bytes/hashes/descriptors/authority across invocations, no removed repeated
observations, no relaxed existing checks/deadlines or broader read authority. All
fds must close on success, rejection and cancellation; active errors remain primary.
Maintain per-file order and duplicate semantics. Scope to dev.py private directory
helper, existing source_evidence/startup.source_snapshot/daemon_images.file_snapshot;
source callers must keep their existing error contracts. No general service/generator.

Add characterization tests BEFORE runtime refactoring for ordinary/fresh repeated
content and inode/mode/signature mutations, parent replacement/symlinks, failed reads
and cancellation/fd closure; add focused acceptance showing fewer parent walks with
fresh per-file reads and post-read parent identity checks. Existing mutation/custody
suites remain required. Record the observed optimization result without claiming an
unreproduced original failure is explained. Root owns docs and broader serial checks;
implementation delegate owns this code/test correction and runs no overlapping suites.

## Tasks & Acceptance

- [x] Existing owner/process tests: meaningful acceptance RED before runtime edits;
  retain raw log. Focused TDD for each new contract; never relabel an assumption failure.
- [x] Existing code/test owners: implement lifecycle and matrix negatives; characterize and apply the measured snapshot directory correction above.
- [x] Affected owner/transport/process/ordinary controls: exact commands/results,
  no mutation authority in ordinary calls and no duplicate inherited test runs.
- [x] Evidence/handoff: source bindings and scaffold/UI/context/docs/ADR decisions.

**Acceptance Criteria:**
- Given the opted-in current owner, when qualification runs, then one Kong lifecycle
  completes and normal cleanup precedes its separate fact, with readiness false.
- Given any matrix fault, when the owner acts, then no replay or unsafe cleanup occurs,
  no success leaks and the original safe error/uncertainty is preserved.

## Implementation Notes

bmad-help selects Build. Delegated read-only investigation settles existing seams;
no intent gap or irreversible effect (synthetic verification only). Dispatch footprint
crosses owner/transport/router/tests. Root owns docs/spec/evidence/review/commit;
delegate owns code/tests. No nested agents/workflow rendering in implementation.
Checkpoint: platform/deployment/.local/kong-owned-lifecycle/checkpoint.json preserves
17 concurrent files,52 historical prerequisites,17 prior transport and30 prior profile
evidence files plus index. Standing approval covers dirty-tree continuation.

## Verification

PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v,
smallest failing acceptance first, focused tests then affected modules and selected
process controls. Preserve exact IDs/counts/commands/source/log hashes and failures.
No runtime-content hashes/full-suite/actual-Docker qualification claim.

## Review Triage Log


All three context-free review layers completed: blind10 findings (floor10), edge[],
verification-gap1. Every finding is individually verified/graded below before grouping.
Three projection acceptances reproduced without payload output in
.local/kong-owned-lifecycle/review-projection-demonstration.json; original47-file frame
remains unchanged. No intent gap, loopback or review deferral is needed.

| ID | Verdict | Route | Verification evidence |
| --- | --- | --- | --- |
| B1 proc paths | medium | patch | validate_kong_container explicitly treats empty MaskedPaths/ReadonlyPaths as defaults. Synthetic descriptor with both empty is accepted; that does not prove the identified filesystem protections. Require the known protected defaults and model them independently in the peer. |
| B2 effective ports | high | patch | NetworkSettings.Ports is unread. Synthetic running inspect with 0.0.0.0 binding is accepted despite the approved loopback-only policy; requested HostConfig does not disprove contradictory effective publication. Check the effective projection and mutations. |
| B3 endpoint config | medium | patch | Only aliases/NetworkID are checked; nonempty Links and IPAMConfig are accepted by direct demonstration. Reject unrequested endpoint options while preserving permitted dynamic observation fields. |
| B4 shutdown expiry | medium | patch | Budget test compares equal deadlines without consuming them; no test crosses15s during Kong stop or before PG stop. Add deterministic expiration assertions before subsequent normal mutations/facts. |
| B5 process cancellation | medium | patch | Current cancellation injection is archive-only in the direct owner. Add real private-process cancellation after start with known-current cleanup and lost-custody preservation, no output/success and verified child termination. |
| B6 double error | false | reject | Existing lost-create process scenario closes DockerSession and sets creation uncertainty while PG ID remains. Startup finally calls cleanup_execution, which raises execution_cleanup_unresolved on that state. The test asserts original docker_response_invalid; removing the new error-preservation branch would mask it and fail that assertion. This already exercises concurrent lifecycle/cleanup refusal. |
| B7 lost stop/delete | medium | patch | Existing process disconnect is create-only; explicit HTTP errors do not cover accepted stop/delete followed by lost response. Add private-wire cases proving no reconnect/replay or PG/storage/bridge disposal after uncertainty. |
| B8 protected fields | medium | patch | Full Config/HostConfig comparisons exist, but response mutations omit labels/workdir/stop signal, restart/resources/host port bindings. Expand the independent mutation matrix to protect those comparisons and latch custody loss. |
| B9 main guard | low | patch | KongScopedTransport is declared after unittest.main; direct execution exits before defining it. Moving the existing guard to the end is a direct correction with no added complexity. |
| B10 status wording | low | patch | Evidence appends completed process results after an unlabeled pending statement; memlog/handoff are not explicit about checkpoint versus current status. Label earlier pending statements historical and reconcile current delivery status without deleting results. |
| G1 pre-stop health | medium | patch | Preverified gap: stop_kong rechecks current health but tests only unhealthy during initial startup. Removing the stop-time guard would leave existing tests passing. Add finish_execution health-deterioration refusal before normal stop/fact. |

Survivors have separate root causes, so no findings are merged. Existing pre-review
medium-unverified timing investigation remains separately recorded in deferred-work;
no passing repeat is treated as its explanation. Root retains final evidence/status
and serial verification ownership; implementation agent applies the small corrections.

## Final verification and completion

All ten surviving review findings are patched and verified; B6 remains rejected
with evidence above. Root final 190 methods PASS295.620s, no skips,47 unchanged
bindings;427 distinct passing method IDs across the five retained root source frames.
Exact commands, results, manifest/log digests, semantic deltas, requirement-to-test
mapping and five impact decisions are in ENV_KONG_EXECUTION_EVIDENCE.md.
No review deferral or loopback. The separate pre-review medium-unverified timing
investigation remains; original failures are retained without a causal or speedup claim.
Checkpoint audit preserves 17 concurrent files, 52 prerequisite files, 17 prior transport
and 30 prior profile evidence files, initial index and final 47 source bindings.
This synthetic-only increment is done; actual qualification and remaining enclosing
ENV/scaffold gates precede dependent work. Runtime/fresh-setup readiness remain false.

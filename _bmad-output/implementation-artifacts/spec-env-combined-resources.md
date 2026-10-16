---
title: 'ENV: acquire run resources together on one guarded daemon session'
type: feature
created: '2026-10-16'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 87ef3d15be6e369721652fc7364492a212287024
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing bounded ENV implementation approval and user continuation">

## Intent

**Problem:** Network, volume and image acquisitions independently release the run lock
and daemon connection. No existing operation constructs a candidate startup handoff
from all three under the same guarded acquisition scope.
**Approach:** Compose the existing owner checks and acquisition algorithms under one run
lock, one daemon connection/version check and one total daemon deadline. Recheck the
joint observations before a constructor-only handoff; retain standalone adapters.

## Boundaries & Constraints

**Always:** Characterize before extraction, acceptance RED before implementation, focused
TDD. Reuse exact routes, error/descriptor policies, locks, protected evidence and
no-reconnect/no-replay transport. Verify image/tool evidence before daemon work; inspect
images before any resource POST. Recheck current evidence before every mutation and
handoff. Owner tool probes stay outside the five-second daemon phase. Bind new sources
and use fresh preparation/receipts. Preserve concurrent Leave/PtS and exact pins,
including TypeScript7.0.2. Only isolated synthetic verification is authorized here.

**Never:** Real Docker mutations/pulls/containers, SQL/migrations/accounts/access changes,
provisioning/deployment/pilot, dependent Identity/Access/WRITE/KDG/Leave implementation.
No new generator/service, alternate workflow, public daemon selector, arbitrary proxy
or automatic cleanup/retry/rollback. Keep up gated and runtime_ready=false. A connected
acquisition does not reserve resources, prove volume freshness/exclusivity, bootstrap/
secret policy or continuous container execution. No future peer-liveness guarantee.

## I/O & Edge-Case Matrix

| State | Expected outcome |
| --- | --- |
| Prepared run, current qualified images, absent or matching owned resources | Single lock/connection/version, ordered checks and exact joint descriptors; constructor handoff only |
| Missing/stale tool/image/preparation, changed run/source/receipt or lock | Specific safe refusal, no unauthorized daemon call or later POST/handoff |
| Image absent/foreign, network replaced/unsafe, volume changed/foreign | Refuse at boundary, no later mutation/handoff; no automatic cleanup |
| Lost create response, disconnect/truncation at any stage or socket replacement | No reconnect/replay; original peer or refusal, never replacement endpoint |
| Individually fast phases exceed total deadline | Refuse under one daemon budget, no reset per adapter |
| Concurrent acquisition, callback exception or final evidence change | Lock/refusal/cleanup protections hold; no successful result after failure |

</frozen-after-approval>

## Code Map

- `platform/deployment/networks.py`, `volumes.py`: extract validated algorithms accepting
  target/run/session/current callback; standalone wrappers reuse them without policy changes.
- `daemon_images.py`: factor anchored receipt/source/run/file custody and pre/post owner
  verification for reuse; probes remain before opening/after closing daemon connection.
- `resources.py`: small ENV coordinator. One lock/version/connection. Check qualified
  images before network/volume acquisition, then recheck child/config images, network
  name/ID and volume using existing validators. Optional trusted immediate nonblocking
  constructor handoff, never execution. Joint result carries network/volume/images;
  source/evidence postchecks gate return. Reuse startup.invocation if constructing argv.
- `dev.SOURCES`, `tests/test_dev.py:FILES`: bind new production file(s), keep up gated.
- `tests/test_resources.py`, `tests/qualify_resources.py`: compose existing private fixture
  oracles; independently count connection/version and exact ordered requests/bodies.
  Literal failure controls, no configurable endpoint. Characterize standalone behavior.
- `DEVELOPMENT.md`: commands, guarantee and limits. Root owns evidence/navigation/memlog,
  review and final verification/commit; implementer owns code/tests/runbook.

Pinned source trace: PG17 db-setup.ts's Auth migration reuses GoTrue; disabled Realtime/
Storage helpers add no identity. Record evidence only; execution/SQL remains unqualified.

## Tasks & Acceptance

- [x] Observe combined acceptance RED and characterize standalone algorithms.
- [x] Extract/reuse owner algorithms and implement guarded joint acquisition/handoff.
- [x] Prove every matrix row with focused tests, including final failures and no later POST.
- [x] Fresh preparation/tool/image qualification; public combined controls and affected
  standalone positives; then sequential full deployment regression and static checks.
- [x] Record requirement/test and five impacts; independent review/fixes and scoped commit.

Given current prepared owner evidence, when resources are acquired together, then one
connection and lock covers their checks and constructor handoff with unchanged policies.
Given any failed guard or uncertain mutation, when acquisition continues, then no later
mutation/handoff or successful result occurs, and no connection/request is replayed.

## Implementation Notes

No product gap or irreversible execution. Root runs socket tests: write initial tests,
message root with commands and wait for RED/GREEN before extraction. No child escalation;
compile/whitespace locally. Stay available for review fixes. Five impacts: existing ENV
scaffold; no UI/context change; owner docs updated; accepted ADRs unchanged.

## Spec Change Log

## Review Triage Log

## Verification

Root runs affected unittest suites: test_resources, test_networks, test_volumes,
test_daemon_images, then fresh public combined qualifier and standalone positives;
full `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
sequentially afterward. Compile, scoped whitespace/local links, real read-only up
refusal. Exact commands/results, record hash and impact decisions in owner evidence.

## Review disposition — first pass

All three layers reported before triage; edge-case layer returned no findings. Individual
verdicts below precede grouping. B2/V1 share the public projection verification gap.
All retained fixes are local, guard demonstrated states and add no runtime/public
interface; use a private conflict fixture case rather than expanding public controls.
No intent gap, changed decision or deferred finding.

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| B1 observable EOF reaches constructor | medium / patch | Root injected read EOF during final evidence after last exchange; constructor still ran. Check session immediately before/after handoff and cover the boundary. |
| B2 public qualifier untested | medium / patch | Combined tests invoke acquire directly, not main; exit/projection regression would pass. Add captured public main cases. |
| B3 lost-response same-run recovery unproved | medium / patch | Immediate refusals covered but next explicit acquisition is not. Reuse synthetic post-created state and prove inspect/reuse without duplicate POST. |
| B4 conflict joint path missing | medium / patch | Standalone network conflict works; combined sequence has no conflict case. Private fixture/test proves owned409 recovery and final volume/joint checks, no new public switch needed. |
| B5 identical-byte/restore custody unproved jointly | medium / patch | Existing standalone identity checks retained, but combined mutation-boundary tests only change bytes. Add retained-image/tool replacement and restore cases at those boundaries. |
| B6 final negative validation coverage incomplete | medium / patch | Final network/volume code uses owner validators, but tests cover only ID/timestamp change there. Add final foreign/unsafe/missing/error cases and no handoff. |
| B7 missing delivery evidence | false / reject | Root-owned ENV_COMBINED_RESOURCES_EVIDENCE.md already has RED/GREEN commands, test mapping and all five impacts, excluded from code-review diff and finalized after qualification. |
| V1 public status/JSON projection gap | medium / patch | Verified review gap: tests bypass main's parser/refusal projection; same cause as B2, retain own row. |

Final verification: combined 16 passed in 32.894s; stronger same-byte/original-mtime custody
case passed 1 in 1.414s; all 374 deployment tests passed in 157.842s. Frozen-source run
`32ea0b48-b882-464a-b5ce-e5544af648b3` passed all 16 public checks with thirteen retained
file identities/source snapshots unchanged. Seven review instances fixed, one disproved,
none deferred. Compile/whitespace/local links passed; real up refuses docker_28_required.
Exact attempts, commands, traceability, record hash and five impacts:
[owner evidence](../../platform/deployment/ENV_COMBINED_RESOURCES_EVIDENCE.md).

---
title: 'ENV: acquire and verify the disposable run network before startup'
type: feature
created: '2026-10-15'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 2388df73a38e4648479b7e77ff64deff260fb74d
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing bounded shared-foundation implementation and isolated synthetic verification approval; user requested next">

## Intent

**Problem:** Startup currently consumes a synthetic network descriptor. It cannot acquire
or verify the actual run-owned bridge that must constrain the selected CLI's publishing.

**Approach:** Implement the existing ENV owner's guarded Docker network acquisition,
inspection and startup-ID handoff, with end-to-end verification against a private
synthetic Unix-socket daemon. Keep real lifecycle activation blocked.

## Boundaries & Constraints

**Always:** Require current protected preparation before daemon access; preserve approved
pins and concurrent Leave/PtS work. Use ATDD and focused TDD. Require stable Linux
Docker>=28 before network calls. Production adapter uses only /var/run/docker.sock,
ignores ambient hosts/contexts and exposes no remote socket option. Synthetic proof
may inject its private endpoint internally; no real daemon mutation in this item.
Use the prepared network name and existing owner/target/run/project labels, local
bridge, IPv6/ingress/attachable disabled, exact loopback-default publishing option and
no attached containers. Validate relevant actual Docker inspection fields before
projecting the closed startup descriptor. Require canonical full Docker network IDs.
Fresh creation uses exact controlled input and verifies returned ID by inspection.
Existing foreign, misconfigured or attached networks refuse without repair/deletion.
Serialize same-run operations with protected bounded locks; handle creation conflict
by verifying the winning network. Reinspect by immutable ID immediately before
handoff, reject replacement and recheck preparation/source bindings. Timeout/uncertain
create never triggers blind retry/delete; a later explicit invocation inspects first.
Bound total operation time, request/response bytes and framing; no redirects, arbitrary
API paths, Docker CLI or child processes. Return safe codes and selected metadata only;
never log daemon error bodies, credentials or whole responses.

**Never:** Activate dev.py up, create a real network/container/volume, pull images,
execute SQL/migrations, alter accounts/access or provision/deploy infrastructure. No
Identity/Access/WRITE/Leave/KDG domain work, extra generator, generic offline service,
accepted ADR edits or kernel-isolation/runtime-readiness claims. Existing image/tool
receipts are immutable; source changes require fresh preparations, never receipt repair.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Prepared run, supported daemon, absent network | Create only exact run network; inspect returned ID, reinspect and hand off validated ID; runtime_ready=false |
| Matching existing empty network | Reuse verified ID without POST; no mutation |
| Foreign collision, unsafe option/IPv6/labels, attachments | Refuse, no repair/delete |
| Create conflict or lost create response | Inspect matching winner on conflict; timeout refuses and preserves uncertainty; next invocation inspects first |
| Network replacement, changed preparation/source, concurrent same-run call | Reject changed evidence/ID; serialize or bounded refusal |
| Docker27, missing preparation, malformed/oversized/slow/error response | Safe nonzero, no positive proof; old daemon/missing preparation cause no network call |

</frozen-after-approval>

## Code Map

- `platform/deployment/dev.py:docker_prerequisite`: extract bounded exchange in this
  same module; preserve gate behavior, socket patching and version/framing rules.
- New `platform/deployment/networks.py`: reuse dev preparation/protected paths/IDs and
  startup labels/validate_network/invocation. Validate actual inspect fields before projection.
- `tests/test_docker_gate.py`: retain characterization expectations. `test_dev.py:FILES`
  copies source dependencies; keep transport in dev.py to avoid another import.
- New `tests/test_networks.py`, `tests/qualify_networks.py`: private Unix daemon and
  exact controls; no CLI socket override. Startup handoff is construction only.

## Tasks & Acceptance

- [x] Tests: observe missing acquisition acceptance first, preserve gate characterization,
  then cover every matrix row through actual private Unix socket and focused units.
- [x] dev.py/networks.py: reuse one bounded transport, implement acquisition/inspection,
  bounded protected run lock and before/after evidence checks with safe failures.
- [x] Qualifier/runbook/evidence/KDG navigation: execute synthetic positive and negative
  cases; record source identities, requirement-to-test links and five impacts.
- [x] Run focused then affected owner regression; independent review, fix findings,
  scoped checks and local conventional commit; no push.

**Acceptance Criteria:** Given a valid prepared disposable target, when the synthetic
public qualifier runs, then the real acquisition adapter creates or verifies only its
run-owned network and supplies the same validated ID to startup invocation construction.
Given unsafe state or failed controls, when it runs, then it returns safe failure and
performs no unauthorized API operation. Real up remains runtime_adapter_unqualified
on supported Docker and docker_28_required on the current host.

## Implementation Notes

Initial missing-module red was observed before code. The availability-only test was
replaced with behavioral acceptance. ConfigFrom create-input and repository-relative
public subprocess checks each had an observed behavioral failure before their fixes.
Existing 15 Docker gate tests passed before and after shared transport extraction.
Final initial matrix: 20 tests pass in 13.194s; affected deployment: 265 pass in 41.063s.
Actual public 15 controls pass on fresh run 95708946-49ef-4981-ab3c-65017a97a624;
missing-preparation uses unprepared run 32829b7a-c151-419d-9fdf-3ed68c091af8.
Actual dev.py up returns docker_28_required without network mutation. Protected
initial evidence is .local/network-qualification/initial-95708946.json.
Source-bound preparation now includes network/startup/qualifier sources. Earlier
preparations and image/tool receipts remain immutable and become stale; fresh run
qualification is required before repeating those older proofs.


## Spec Change Log

## Review Triage Log

All three independent layers completed before triage. The third was launched once a
transient thread limit cleared, before acting on any findings. Edge review returned
no findings. Each instance is classified before grouping; B=blind, V=verification,
R=root inspection. No intent gap or irreversible action is introduced by these patches.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | Reproduced shared create-input/oracle mutation to EnableIPv4=false being accepted by descriptor verification. Make synthetic expected request independent of networks.create_input so qualification detects wrong production choices. Patch. |
| B2 | medium | Reproduced validate_events accepting version/name/create with every post-create inspection absent. Assert complete ordered successful observation sequences. Patch. |
| B3 | medium | Existing replacement fixture changes every later ID response, failing before the name-continuity branch. Add retained-original-ID/name-replaced case and prove handoff is not called. Patch. |
| B4 | medium | Reproduced a nonempty held lock passing check(), despite next-call refusal. Repeat complete initial lock owner/type/mode/link/size/identity validation. Patch. |
| B5 | medium | EXPECTED mismatch and match both re-raise the same refusal. A public negative control cannot distinguish an expected rejection from broken qualification. Return a distinct mismatch code and test it. Patch. |
| B6 | low | Malformed UUID raises native ValueError; parseable noncanonical UUID reaches invalid_run_id. Normalize the adapter and qualifier to the safe specific code. Direct correction, patch. |
| B7 | low | Reproduced GET /version with a body reaching socket creation. Enforce no body for read-only routes and reject before connect. Direct correction, patch. |
| B8 | low | Changed documentation contains joined words/numbers, reducing evidence readability. Correct spacing in this delivery's changed passages. Direct correction, patch. |
| V1 | medium | Preverified regression gap for reserved name changing while original ID remains inspectable. Same cause as B3; retain separate verdict and one targeted regression. Patch. |
| R1 | low | Public conflict control reports created=true even though its POST receives 409 and verifies another winner. Report created=false for conflict and assert that result. Direct correction, patch. |


## Verification

Run test_networks.py acceptance red/green, existing test_docker_gate.py characterization,
then all deployment test_*.py sequentially. Run opt-in qualify_networks.py against its
private daemon using fresh prepared source evidence. Inspect full API event allowlist,
positive handoff and exact negative codes. No real Docker write. Document scaffold
(ENV adapter only), UI (none), context (root rules suffice), docs and ADR (unchanged).

Final verification: 26 focused tests passed in 13.711s; all 271 deployment tests passed
in 40.675s, no skips. All 15 public controls passed on fresh prepared run
 e7af1eef-e0a9-49da-970c-d690ba3347f4; actual up refused docker_28_required.
All 11 source/preparation file identities remained unchanged. Final protected record:
platform/deployment/.local/network-qualification/final-e7af1eef.json, SHA-256
18f31487b61df837469cb4241356d88395a135cc2560494cde83589c2458308e.
All 10 triaged instances are fixed; none deferred. New regressions were observed red
before fixes. Requirement traceability and all five impacts are recorded in
platform/deployment/ENV_RUN_NETWORK_EVIDENCE.md. Runtime readiness remains false.

---
title: 'ENV: prove guarded Supabase startup invocation at the Docker process boundary'
type: feature
created: '2026-10-15'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: b6637eb43cab8840f6d6e675635d1691a5c9a133
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
  - '{project-root}/platform/deployment/DEVELOPMENT.md'
---

<frozen-after-approval reason="Standing bounded ENV implementation and isolated synthetic verification approval; user requested next">

## Intent

**Problem:** Qualified tools/config/base-image metadata do not provide an executable
startup invocation. The pinned CLI trusts preexisting networks and publishes ports
without host IPs, so ENV must establish its own invocation and network constraints.

**Approach:** Add the existing ENV owner's reusable startup-invocation construction
and an opt-in actual pinned-CLI proof at a synthetic Docker process boundary. Verify
the first PostgreSQL create command and stop there; real startup remains blocked.

## Boundaries & Constraints

**Always:** Preserve concurrent Leave/PtS/install changes and approved pins. ATDD
first, focused TDD. Require unchanged existing preparation/tools/image evidence;
missing/changed evidence refuses without installation, registry refresh or repair.
Reuse existing owner verification; qualification may take transient owner locks/run
probes and must not be called read-only. Build private workdir/config/state/cache with
no repository SQL, dotenv or linked overrides. Force legacy backend, slim off, ECR
registry and explicit run network/workdir. Validate a run-owned local bridge descriptor
with exact reserved name, nonempty ID, owner/target/run/project labels, loopback-default
publishing and no foreign attached containers before constructing the invocation.
Network metadata supplied by the synthetic proof is a fixture, not real isolation.

The proof must intercept every container executable through private PATH fixtures,
set a nonexistent private Docker endpoint, reject Podman/fallback/unexpected commands,
and never dispatch a real Docker executable. Return controlled synthetic inspect
responses only as needed to reach first PostgreSQL create; refuse that create rather
than execute it. Assert safe selected image/network/name/port/mount/SQL-input facts.
Bound subprocess time/output/process groups and fixture input/state; discard child
output and never retain full argv, environment values, payload dumps or credentials.
Retain only selected safe fields, source identities and explicit proof limits.
Record requirement-to-test evidence and all five impact decisions.

**Never:** Wire real startup into dev.py up, mutate the real daemon/network, pull
images, run containers/SQL/migrations/accounts/grants/provider/infra/deploy/real data,
implement Identity/Access/WRITE/Leave/KDG domain/editor, create another generator or
generic service. Do not change source-bound dev.py/toolchain.py/images.py merely for
this item. Do not claim complete startup/helpers, actual digest enforcement, image
execution/libc, deployment PostgreSQL compatibility or runtime/provider/device readiness.

## I/O & Edge-Case Matrix

| Input/state | Expected behavior |
| --- | --- |
| Existing qualified run and valid fixture network | Actual pinned CLI reaches first PostgreSQL create through private docker fixture; selected safe launch fields match; runtime_ready=false |
| Missing/changed preparation/tools/image receipt | Safe nonzero before CLI start; no install, metadata fetch or repair |
| Foreign/wrong network/options/labels/attachments | Refuse before invocation execution |
| Hostile ambient env, workdir contamination or unexpected container command | Isolate or refuse; no real Docker/fallback or sensitive retained output |
| Hanging/output-flooding child, malformed/oversized fixture input, interrupted execution | Bounded safe refusal and no live descendants; no positive proof |

</frozen-after-approval>

## Code Map

- New deployment/startup.py, tests/qualify_startup.py, tests/test_startup_adapter.py.
- Reuse dev configuration/identity/protected validation, images.bounded_command and
  images.qualify repeat-only on existing receipt. Require receipt first and unchanged
  afterward; no raw retained() call (it expects a lock). Existing qualified run:
  b3b805d5-adc6-4168-a79c-5945547d3320. Keep dev/toolchain unchanged. A necessary
  images.py existing-only seam prevents a renamed evidence path entering collection;
  preserve default qualification, test the race, and use a fresh final qualified run.
- Pinned command-internal/container-cli.ts shells names docker/podman. Intercept both;
  wrapper uses absolute Python shebang. db-bootstrap/docker-create-args.ts builds
  first PG create. Private config parser fixture: tests/qualify_supabase_config.py.
- Force SUPABASE_EXPERIMENTAL_STACK=0, SUPABASE_USE_SLIM_IMAGES=0,
  SUPABASE_INTERNAL_IMAGE_REGISTRY=public.ecr.aws; start --agent no --workdir
  <private> --network-id <validated>. No dry-run. Network bridge option:
  com.docker.network.bridge.host_binding_ipv4=127.0.0.1. Define/document closed ENV labels.

## Tasks & Acceptance

- [x] `tests/test_startup_adapter.py`: acceptance red, then focused coverage for all matrix rows.
- [x] `startup.py`, `tests/qualify_startup.py`: implement guarded invocation and bounded
  synthetic Docker boundary; prove first create uses selected PG reference/run scope.
- [x] `DEVELOPMENT.md`, `ENV_STARTUP_INVOCATION_EVIDENCE.md`: exact commands/source
  identities, traceability, five impacts and partial-proof limits; update KDG navigation.
- [x] Execute actual pinned CLI positive/negative controls, focused/affected owner suite,
  independent review, scoped checks and local conventional commit; no push.

**Acceptance Criteria:** Given a qualified synthetic run, when the opt-in proof runs,
then it reaches and refuses first PG create solely through the private fixture and
reports bounded invocation proof with runtime_ready=false. Given unsafe inputs or
failed controls, when invoked, then no positive proof or real container action occurs.

## Implementation Notes

Agent owns code/tests/runbook; root owns actual proof, evidence/navigation/review/commit.
Implementation investigation found a genuine owner verification race: holding an old
receipt FD does not stop qualifier path recreation/registry fetch after rename. The
existing-only seam is required by the frozen no-refresh invariant, not an incidental
owner rewrite. No dev/toolchain change or new CLI option. Source-bound image evidence
must be requalified through a deliberately fresh prepared/tool-qualified UUID.
Known run-scoped volume-create attempts get a synthetic duplicate-volume refusal;
only inspect commands can succeed. First PG create records safe facts then stops only
its verified private CLI process, before cleanup. No container executable dispatch.

## Spec Change Log

## Review Triage Log

B=blind, E=edge, V=verification-gap. Classify each instance before grouping.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | Reproduced invocation accepting a0777 workdir root with private children. Root ownership/mode/identity need validation and anchoring. Patch. |
| B2 | medium | events.json open lacks regular/private/single-link checks; FIFO or lock waiting is unbounded. Same state gate as E1/E2. Patch. |
| B3 | medium | Actual Docker fixtures detach into separate sessions; group-only cleanup cannot cover a stalled fixture. Add parent-death/lifetime ownership and a separate-session cleanup regression. Patch, coordinated with E2. |
| B4 | false | The result qualifies only selected image/name/network/port/mount facts and explicitly reports first_postgres_create_only=true, runtime_isolation=false. It makes no security-option/restart-policy qualification claim; allowing opaque unqualified options does not invalidate those selected facts. No runtime is executed. |
| B5 | medium | Replacing shell text with cat /repo/owned.sql still reports repository_sql_inputs=false. Narrow that assertion to actually checked private configuration/files/mounts and state that shell SQL is unqualified. Patch. |
| B6 | medium | The positive synthetic CLI test omits all prerequisite inspections yet passes; it cannot prove the stated inspected-network/existing-volume path. Require its prerequisite observation sequence and test missing/duplicate/out-of-order events. Patch. |
| B7 | medium | Source is hashed only after execution; changed bytes can be misattributed to the completed proof. Capture/compare the owner and fixture dependency identities before/after execution. Patch. |
| B8 | medium | Direct reject-command control accepts generic failure without asserting the expected rejection event and does not exercise a CLI issuing an unexpected command. Assert the exact controlled rejection and add a synthetic CLI negative path; label direct versus pinned controls accurately. Patch. |
| E1 | medium | Reproduced hardlinked events.json rewriting/truncating another isolated file. Validate held state inode/type/owner/mode/link count before writes. Patch, same state gate as B2. |
| E2 | medium | FIFO/held lock in detached fixture can outlive CLI group timeout. Bound file admission/lock waiting and tie detached lifetime to its private parent. Patch, coordinated with B2/B3. |
| E3 | high | pidfd_open occurs after UID/session/argv/exe observations; parent death/PID reuse can retarget the descriptor. Open descriptor first, validate/recheck direct parent, and close it on every refusal. Patch. |
| V1 | medium | Preverified gap: no test calls full qualify across evidence changes during probe. Add unchanged success and post-probe receipt/payload/preparation mutation refusals. Patch. |

## Verification

Run focused acceptance red/green, opt-in actual CLI controls, then affected deployment
tests sequentially after owner probes. Record commands/results and matrix coverage.

Acceptance red: missing startup module, before implementation. Final focused30 tests pass
3.265s; existing33 image tests pass; full affected suite245 pass28.573s. Actual public
CLI positive9events/firstcreate refusal passes on fresh9d5d990f-e627-4fcb-bb0a-65a9e8c1570f;
invalidnetwork/contamination/unexpectedcommand controls all refuse as expected.
Initial fixture shape/session assumptions failed safely before corrected controls.
Matrix coverage and five impacts are in [owner evidence](../../platform/deployment/ENV_STARTUP_INVOCATION_EVIDENCE.md).
Independent review complete:11 instances fixed, one false, none deferred. All three
layers finished before triage; same implementation agent applied the patches. Final
positive and all three exact negative codes pass after hardening, including direct
expected_command_rejected. Image receipt hash/inode/mtime/mode remain unchanged.
Compilation, scoped whitespace and local documentation links pass. Local conventional
commit records this bounded increment; no push. Runtime readiness remains false.

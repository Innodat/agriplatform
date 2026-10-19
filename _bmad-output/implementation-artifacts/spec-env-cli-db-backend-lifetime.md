---
title: 'ENV CLI database backend lifetime'
type: 'feature'
created: '2026-10-18'
status: 'done'
baseline_commit: '05dd515782c26d036dffd7373b9759f9e101199e'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing approval for bounded ENV implementation and isolated synthetic verification">

## Intent

**Problem:** Auth catalog verification checks job results but leaves the earlier host-facing database backend's presence and departure unobserved. Later CLI setup must not be attempted from an assumed session lifecycle.

**Approach:** Add one explicit qualifier that independently observes the expected external PostgreSQL backend before the existing blocked CLI group is terminated, then verifies its departure before the existing catalog/job sequence. Reuse retained owners and preserve all preceding controls.

## Boundaries & Constraints

**Always:** Source-pinned Linux disposable fixture, existing FreshGuard/DockerSession, exact immutable images/resources and current healthy PG/start/fixture custody before/after exchanges. TypeScript7.0.2/mail15484 unchanged. While the actual CLI is blocked at the validated Auth-job request, a closed detached psql read-only predicate requires exactly one non-loopback TCP client backend besides the observer, with user/database postgres, positive client port and idle state. Exclude background workers, Unix sockets and loopback health probes. Terminate/reap the same proven CLI group using the existing single termination; only then require zero external client backends. Departure may poll read-only inside one bounded SQL invocation for at most3s, within existing statement5s/lock1s/idle-transaction5s and total execution120s. Consume each exec attempt/ID before uncertain mutation; exact typed request/config/state checks, no replay/reconnect/adoption. Missing/extra/wrong/NULL states fail. After verified departure, unchanged Auth precondition/job/catalog and normal PG shutdown/disposal must pass. Acquisition5s, shutdown15s, cleanup10s, fixture5s remain. Only selected verification booleans, no backend/query rows, credentials, payload or logs.

**Never:** Exact OS-process/backend attribution, password-method proof, continuing CLI-session identity, job success ACK/CLI continuation/later setup SQL, accounts/grants/owner migrations/seeds, arbitrary SQL/exec forwarding, new runner/client/proxy/generator/service, public up admission, Identity/Access/WRITE/server KDG, Leave/editor or production/pilot. fresh_setup_completed=false/runtime_ready=false remain. Session observation is separate from full Auth/schema/runtime readiness.

## I/O & Edge-Case Matrix

| State | Behavior | Failure |
| --- | --- | --- |
| One expected backend before kill, none afterward | Verify lifetime then existing catalog/job/cleanup | Report distinct facts only after successful exits |
| Absent/duplicate/wrong-role/database/non-idle/external endpoint invalid | Refuse before job | No false readiness from observer/health worker |
| Backend lingers after group kill | Bounded read-only departure wait, then refuse | No job dispatch or deadline extension |
| Changed custody, lost/malformed exec/start/inspect, interrupt/deadline | Refuse, consumed attempt | Existing bounded owned cleanup/preservation, no replay |
| Existing controls/public lifecycle | Original behavior | Public up still unqualified |

</frozen-after-approval>

## Code Map

Paths relative to platform/deployment/. Existing AuthCatalogDaemon/ExecutionSupervisor are extension points; no broad refactoring.
- startup_lifecycle.py: closed presence/departure SQL builders and exact validators, alongside auth_catalog_exec.
- dev.py: existing detached-exec allowlist accepts only those closed bodies.
- resources.py: FreshGuard mode/one-shot facts and detached exec custody/state checks; reuse auth_pg_current and existing finish/job gates. Before observation requires validated job input and live CLI; departure requires terminated flag.
- startup.py: guarded_fixture_command phase5 terminal branch runs presence before existing kill/wait, departure afterward, before catalog/job; wire one literal qualifier/facts without ACK. Existing installed fixture wrapper must route its unchanged five-second alarm through caught TimeoutError so a held verified parent pidfd is stopped rather than allowing CLI continuation. No new runner or timeout extension.
- tests/qualify_startup.py: existing control list and closed internal20/4-case, late-initial-zero and forced occupied→timely/late-zero fixtures (27 SQL cases).
- tests/test_pinned_execution.py: no-socket ATDD/TDD for new matrix and compatibility, generated-wrapper alarm handler and closed temporal-fixture characterization; root applies review patches after the earlier worker becomes unavailable.
- tests/test_resources.py: root owns actual private-socket/process ordering, refusal, omitted-termination mutation oracle and six-second presence-delay alarm regression proving no marker/job and bounded owned cleanup.
- fixtures/supabase-pg17-profile.md, ENV_CLI_DB_BACKEND_EVIDENCE.md, DEVELOPMENT.md, this spec, KDG next-session/memlog: root owns source/requirements/impacts/results. Retained pinned CLI db-setup.ts runFreshDbSetup connects host postgres before Auth-job creation; later setup modifies privileges and remains forbidden.

## Tasks & Acceptance

- [x] Owning code/no-socket tests above — observe missing-interface acceptance RED, focused TDD for matrix, preserve original controls.
- [x] Root process and fresh source-qualified actual control — prove presence→group termination→departure→catalog/job→normal cleanup ordering. Existing prior controls and full deployment discovery pass serially; no unobserved claim from test doubles.
- [x] Profile/evidence/runbook/spec/handoff/memlog — exact commands/hashes and requirement-to-test mapping; scaffold/shared-UI/context/docs/ADR decisions and concurrent preservation.

Given source-qualified fresh target, when the new qualifier succeeds, then both selected backend observations, prior catalog/job and normal cleanup have independent evidence. Given either backend predicate or custody failure, when execution refuses, then no later job/readiness claim or uncertain replay occurs.

## Implementation Notes

ATDD missing-interface RED precedes implementation. Visibility, request-size,
late-zero deadline and held-parent alarm regressions each observe RED before their
corrections. Existing owners, typed closed requests, one-shot custody and all approved
bounds remain. Review adds forced two-observation temporal cases and tracked-only
reproduction; the rollback-safe ordinal oracle preserves production conditions/exits.

Final133 no-socket tests PASS2.563s;4 process tests PASS36.297s. Source-identical14cf6356
and237696d7 verify13 controls and27 SQL cases, including all four exact documented
commands. Final unchanged full629 PASS801.123s, no skips. The earlier no-eof witness
failure and its unchanged focused PASS are retained without claiming a cause.
Three independent reviews complete; four patch groups verified, two concurrent Leave
findings rejected/preserved, four medium-unverified investigations deferred. Runtime
and dependent work remain gated. See [evidence](../../platform/deployment/ENV_CLI_DB_BACKEND_EVIDENCE.md#final-acceptance).

## Spec Change Log

## Review Triage Log

All three resumed layers complete: blind10, edge0, verification-gap0. Original
workers ended without final results; resumed reviewers read the same181382-byte diff.
Each finding is graded before grouping; no frozen intent or concurrent Leave edit.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | maybe-false | Alarm is armed before startup import; no verified parent handle exists there. A real later CLI action after expiry in that window is not demonstrated. Medium if true; defer pre-handle alarm investigation, preserve trusted-identity rules. |
| B2 | maybe-false | parent_identity closes its local pidfd on BaseException before fixture_main receives it. The acquisition/return interruption and later CLI action remain unproved. Medium if true; same pre-handle alarm investigation, require exact identity/signal evidence. |
| B3 | maybe-false | Departure uses wall-clock clock_timestamp; the qualified host has no observed backward step during execution. A step could invalidate the inner3s elapsed claim while SQL5s remains. Medium unverified; defer isolated clock-step evidence without changing host time or accepted bounds. |
| B4 | medium | Tracked fixtures force empty or permanently nonempty activity, never nonzero then timely zero. A polling regression could escape those fixed-input cases. Patch a closed deterministic two-observation success fixture. |
| B5 | medium | Late-zero fixture delays only its first observation. Later-zero rejection is documented but not forced by a test. Same missing temporal-matrix root cause; patch a nonzero-first then late-zero fixture retaining original predicate and limits. |
| B6 | medium | Actual semantic commands invoke an ignored private verifier absent another checkout; tracked fixture functions alone give no complete invocation. Patch a self-contained documented command using existing qualification entrypoint and closed fixture choices, no new runner/public SQL surface. |
| B7 | low | Evidence tables give mode/hash/UUID but do not explicitly map each private result to its full relative path. Direct documentation correction: add artifact-location/source/command mapping and safe verification command. |
| B8 | medium | Leave copyable prompt's E5 instructions lag its own newer checkpoint. Reject: user explicitly excludes Leave implementation/changes and requires preserving concurrent owner documents; no edits or implementation authority inferred. |
| B9 | low | Historical Leave handoff entries retain latest wording and older continuation instructions. Reject under the same explicit user intent exclusion; preserve concurrent planning bytes. |
| B10 | low | New runbook qualifier references fresh prerequisites without an immediate executable sequence/link. Direct documentation correction: show existing prepare/toolchain/images commands and link their owner sections. |
| R1 | maybe-false | Original ecc22e64 docker_timeout31.748s lacks exact failing exchange/phase; later diagnostic PASS does not settle cause or change attribution. Medium unverified operational refusal; defer capture of safe phase/timing with retained resource IDs, no blind cleanup/replay. |
| R2 | maybe-false | Full629 fails unchanged private-handoff no-eof case at missing witness after correct timeout/prefix/elapsed checks; the intended malicious request is not confirmed. Exact unchanged nine-case diagnostic passes, including witness and deadline enforcement. Original admission timing/current-change attribution remain unobserved. Medium unverified; defer exact scenario/phase/PID-start evidence without relaxing assertions or the2s setting. |

Patch groups: P1=B4+B5 (missing forced multi-observation matrix); P2=B6
(reproducible closed semantic invocation); P3=B7 (artifact map); P4=B10
(prerequisite sequence). Defers: D1=B1+B2 (alarm before verified handle publication),
D2=B3 (backward clock), D3=R1 (uncaptured Docker timeout), D4=R2
(unconfirmed no-eof fixture admission). No intent_gap/bad_spec;
all code semantics remain as approved. The original implementation worker is no
longer available after turn resumption, so root applies these minimal patches.

## Verification

Commands and per-control hashes are in the linked evidence ledger. Root runs:

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k cli_db_backend
python3 platform/deployment/.local/pinned-cli-execution-qualification/verify-local.py tests 237696d7-4564-4e00-84f1-e38892354cc8
```

The unchanged full rerun writes deployment-tests-2.json/log:629 tests801.123s, no
skips, exit0; record SHA2569cf089f13e8ed329bbe35d4c62e92af8d9ca61593fcaa93802885b864f6f63ea.
All frozen matrix rows have executed passing tests. Thirteen source-qualified controls
and27 real PostgreSQL SQL cases pass across the two source-identical UUIDs. The exact
tracked runbook Python invocation has SHA256
183e85de1004c2ebe9d1ef4aadf734a8dcb1c929aaac9f12ae0ff71a2b516738.
Public up expected2/runtime_adapter_unqualified0.055s; runtime/setup remain false.

All13 receipts/config files unchanged per control; one unrelated Deals inventory
addition is retained without interference. Audit25 proof sources, seven code/test
hashes, target/script identity, frozen intent, full diff including untracked, original
deferred-log prefix and concurrent six files/index before the scoped local commit.
Preserve original failed/incomplete records and uncertain resources; passing reruns
do not explain their causes. No push/deployment or production/account/real-data work.

Scaffold: existing lifecycle/transport/resource/startup/qualification owners, including
its wrapper template, only. Shared UI/context unchanged; existing guidance suffices.
Documentation: source profile, evidence, runbook with tracked reproduction, Build,
KDG handoff/memlog and append-only defers. Accepted ADRs unchanged/no new decision;
ADR0020 controlled owner release gates and ADR0023 sensitive-diagnostic rules retained.

---
title: 'ENV Auth migration catalog verification'
type: 'feature'
created: '2026-10-18'
status: 'done'
baseline_commit: 'c4b163037f6c5c0074089a6dd8cee8fa218e50ba'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="standing approval for bounded ENV prerequisites and isolated synthetic verification">

## Intent

**Problem:** The completed ENV Auth job proves execution/exit/disposal but does not independently verify its database result. This leaves a migration prerequisite unqualified.

**Approach:** Add one explicit qualifier that checks a source-defined fresh precondition before the existing job, then its exact migration ledger and selected structural postconditions on the same owned PostgreSQL instance. Retain existing execution-only controls unchanged.

## Boundaries & Constraints

**Always:** Retain FreshGuard/DockerSession, source-qualified run/immutable images, TypeScript7.0.2/mail15484, CLI termination before owner work, original six Auth inputs and job/PG disposal. Pre/post checks use closed detached psql execs, current healthy PG/start identity and fixture/resource custody before/after each exchange; attempts/IDs consumed before uncertain mutation, no replay/reconnect/adoption. Total execution120s, acquisition5s, shutdown15s, single cleanup10s and fixture5s unchanged. Transaction is read-only with bounded SQL timeouts and false/NULL causing SQL error. Source authority is Authv2.197.0 commit4eee58f296d9698a1c2c0ae14d7a0b379c7622d3: all75 up-migration versions including literal00 through20260831180000. Preserve seven source-defined PostgreSQL17.11.0.004 bootstrap markers (commitcf90815413819eb057a9916c1598692c160ebeb4): exact seven before the job, exact82-version union afterward, with no missing/extra/null/duplicates. Check real auth.users/identities/sessions/one_time_tokens/mfa_recovery_code_sets/mfa_recovery_codes tables and latest expires_at as nullable timestamptz. Before job, latest ledger version, recovery tables and expires_at must be absent; distinguish the pre-existing PG baseline from the job outcome. Report selected verification booleans only, no query/catalog rows or logs.

**Never:** Full schema equivalence/Auth service readiness, prior CLI host-session identity, success ACK/CLI continuation/later setup SQL, accounts/grants/owner migrations/seeds, arbitrary SQL or generic exec forwarding, another generator/service, public up admission, dependent Identity/Access/WRITE/KDG, Leave/editor, production/pilot/deployment. fresh_setup_completed=false and runtime_ready=false remain.

## I/O & Edge-Case Matrix

| State | Behavior | Failure handling |
| --- | --- | --- |
| Exact fresh precondition → successful job → exact catalog | Verify pre/post predicates and same PG, then normal disposal | Separate catalog fact only after verified post-exec exit0 |
| Already-current/unexpected baseline, missing/extra ledger or malformed objects | Refuse qualification | No job dispatch after failed precondition; no readiness claim |
| Changed PG/image/fixture/resources or duplicate attempt | Refuse before next mutation | Preserve uncertainty, no adoption |
| Lost/malformed exec create/start/inspect, nonzero/deadline/interruption | Consume attempt, never replay | Existing bounded owned cleanup; closed/lost custody preserves |
| Existing execution-only/legacy/public commands | Original behavior and facts retained | Public up remains unqualified |

</frozen-after-approval>

## Code Map

Paths below are relative to `platform/deployment/`.
- `startup_lifecycle.py`: closed pre/post SQL/validator and source-derived75-version constant; reuse persistence_exec flags/error semantics. Pinned Auth/Pop source and versions retained in `.local/auth-catalog-qualification/`; Popv6.1.1 preserves literal filename versions.
- `dev.py`: extend detached exec allowlist with exact bodies only.
- `resources.py`: one-shot pre/post gates and custody, reusing persistence_sql pattern without enabling persistence or generic refactoring.
- `startup.py`, `tests/qualify_startup.py`: new literal control/success facts; existing execution control unchanged.
- `tests/test_pinned_execution.py`: independent no-socket AuthJobDaemon/ExecutionMatrix acceptance. Child owns code and no-socket tests only, no process/socket/Docker checks.
- `tests/test_resources.py`: root owns process acceptance via ExecutionSupervisor.
- Root owns `fixtures/supabase-pg17-profile.md`, `ENV_AUTH_CATALOG_EVIDENCE.md`, `DEVELOPMENT.md`, this spec and KDG next-session/memlog. Preserve concurrent files/index and retained diagnostics/resources.

## Tasks & Acceptance

- [x] Owning code/tests above — observe catalog acceptance RED first, focused TDD for every matrix row; implement one literal qualifier through retained owners.
- [x] Root process tests and source-qualified actual pre/post control — verify real SQL semantics, including rollback-isolated catalog corruption cases, and existing controls.
- [x] Evidence/profile/runbook/spec and KDG handoff/memlog — record exact commands/results/hashes, requirement-to-test matrix and five impacts.

Given a source-qualified fresh target, when the new control succeeds, then the precondition, job, exact ledger/selected structure and same-PG cleanup are independently verified. Given any predicate or custody failure, when the control refuses, then it cannot claim catalog/setup/runtime readiness or replay uncertain work.

## Implementation Notes

ATDD RED precedes implementation. The first actual postcheck exposed seven historical
publisher PostgreSQL markers missing from the initial75-version criterion; source
diagnosis and the explicit user-approved correction preserve exact7 before and82 after.
Original failure and diagnostic receipts remain; no database history is removed.

Reviewed-source run2fc0da48-8839-410c-a06b-464e7722707b: root118 focused tests
PASS2.180s,3 process tests PASS21.491s, actual catalog PASS67.145s and109 rollback-only
corruptions PASS67.636s. All seven legacy controls pass with13 receipts and running
Docker inventory unchanged; public up refuses as expected. Full610 deployment tests
PASS508.504s, no skips. All25 source/target bindings, test hashes, approved frozen
intent and concurrent files/index remain current. Evidence records exact commands/hashes.

Three independent review layers complete. All six patch groups are verified; two
concurrent Leave findings rejected under explicit user scope. No new deferrals;
six prior investigations and diagnostics remain. Existing owners only, UI/context
unchanged, evidence/runbook/profile/handoff updated, no accepted ADR edit/new decision.
Setup/runtime/dependent/production gates remain closed.

## Spec Change Log

2026-10-18 — User approves publisher-baseline correction after explanation: preserve seven historical PostgreSQL Auth markers, require exact7 before and exact82 afterward. Applies the reviewed patch without deleting/changing database history. Original refusal and separate diagnostic remain evidence. All other boundaries and75 current Auth versions unchanged.

## Review Triage Log

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | Root injected Running=true/ExitCode=0 followed by terminal success still verifies. Patch running exit-code invariant with E1. Reject proposed blanket running-Pid0 prohibition: Moby sets Running before assigning Process, so that transient is source-valid and cannot itself qualify. |
| B2 | medium | 109 SQL corruptions exist only in ignored private helper, preventing repeatable checkout verification. Patch by moving closed fixture construction into existing tracked qualification test tooling, no new CLI/runner/public surface. |
| B3 | medium | Independent publisher inventory is private-only, leaving reviewed version provenance unavailable in a checkout. Patch a source-referenced test fixture under existing deployment fixtures. |
| B4 | medium | Committed tests check75/count00 but do not independently assert seven historical/82 union versions; source correction lacks a persistent oracle. Group with B3; test constants against the independent publisher fixture. |
| B5 | medium | Existing custody mutations invoke pre only. Patch equivalent post-job-disposal checks so changed PG/fixture/image/network/volume cannot qualify the postcondition. |
| B6 | medium | Concurrent Leave copyable E5 prompt is stale against latest checkpoint. Reject out of scope: user explicitly excludes Leave work and requires concurrent documents preserved. |
| B7 | low | Concurrent Leave handoff has multiple historical latest labels. Reject under same explicit preservation/exclusion; do not edit the other owner's handoff. |
| B8 | low | Runbook verification-in-progress wording trails completed606 check while review is pending. Root direct prose correction distinguishes verified tests from review and runtime gates. |
| B9 | low | Reproduction heading can suggest reusing the recorded UUID after source changes despite current fresh-run warnings. Root labels historical commands and links fresh prepare/toolchain/image sequence; refusal rules unchanged. |
| B10 | low | Aggregate114 references require reconstructing exact test mapping. Root adds named test identifiers beside requirements; existing executed coverage remains. |
| E1 | medium | Root injected terminal Running=false/ExitCode=0/Pid0 verifies, without process evidence. Moby inspect takes PID from Process; failed starts use nonzero exit. Group with B1 and require positive PID for successful completion; retain source-valid starting window. |

All three layers reported before grading/grouping; verification-gap layer found none.
Six patch groups: exec states(B1/E1), tracked corruption fixture(B2), independent inventory/oracle(B3/B4), post custody(B5), runbook/command wording(B8/B9), exact test IDs(B10). Two concurrent findings rejected; no new deferred investigation. Frozen approved intent unchanged.

## Verification

No-socket acceptance RED, focused tests, root process suite, fresh prepare/toolchain/images, actual new/negative SQL controls. Serial legacy Auth/boundary/initialized/persistence/first-start/bootstrap/guarded controls, expected public up refusal, full deployment discovery. Root uses existing private verifier. Audit frozen intent, source/receipts, matrix, concurrent files/index and scoped diff/commit. Scaffold: existing owners only; UI unchanged; agent context existing rules sufficient; docs updated; accepted ADRs unchanged/no new decision. ADR0020 release/owner migrations remain separate gates; ADR0023 no sensitive diagnostics. No irreversible production action or unresolved user-visible choice.

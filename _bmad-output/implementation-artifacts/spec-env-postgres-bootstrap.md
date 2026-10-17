---
title: 'ENV selected-image PostgreSQL bootstrap qualification'
type: 'feature'
created: '2026-10-17'
status: 'done'
route: 'dispatch'
baseline_commit: '28683c396b82fb5854ec5811c2d4f188d3f8e416'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/deployment/fixtures/supabase-pg17-profile.md'
  - '{project-root}/platform/deployment/fixtures/supabase-pg17-lifecycle.md'
---

<frozen-after-approval reason="standing user authorization for bounded ENV implementation and isolated synthetic local verification">

## Intent

**Problem:** ENV validates the pinned CLI's bootstrap inputs but cannot yet prove the selected PostgreSQL image executes them correctly. Docker host maintenance has removed the version blocker; runtime admission remains unfinished.

**Approach:** Extend existing deployment qualification tooling with one opt-in, bounded, disposable selected-image bootstrap proof. Demonstrate actual initialization and public synthetic key installation, reporting safe observations while retaining `runtime_ready=false`.

## Boundaries & Constraints

**Always:** Use existing image pins, source-bound owner receipts and exact public bootstrap/key fixtures. Select Linux/amd64 by immutable child digest and verify actual local image config identity before execution. Use explicit target/run, fresh run-labelled container, network none, no published ports, fresh tmpfs database storage and no host bind mounts. Refuse existing names. Bound commands/output/total initialization; execute only fixed commands, closed environment and fixed local socket. Only root agent runs Docker tests serially. Clean up only the recorded, re-inspected matching owned container ID; uncertain creation is never replayed/adopted/deleted. Return selected booleans and safe stage/code, never credential/environment/SQL/log dumps. Preserve existing Docker transport restrictions and short resource guard deadlines.

**Never:** Start KDG/Supabase stacks, attach existing volumes/containers, execute repository SQL/seeds/Alembic, provision app grants/accounts, enable `up`, alter live services, deploy, or use real data. No new generator/generic service. Preserve exact dependency baseline including TypeScript7.0.2 and all unrelated Leave/PtS changes. Tmpfs qualification does not prove durable-volume freshness, reuse, full runtime request, networking, recovery or scaffold acceptance.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|---------------------------|----------------|
| Fresh bootstrap | Qualified selected image; isolated fresh storage | Actual SQL/catalog/settings/password/key checks succeed; cleanup verified; runtime false | Safe selected result only |
| Invalid prerequisites | Invalid target/run, missing/stale receipt, wrong image identity | Refuse before container start | Stable safe code |
| Existing or replaced resource | Name collision or changed ID/labels/image/isolation | Refuse ownership-dependent execution/deletion | No adoption or replay |
| Failed execution | Bootstrap/query/command fails, timeout or oversized output | No success/readiness receipt | Bounded failure and owned cleanup; unresolved cleanup explicit |
| Sensitive output | Child emits credentials/payloads | Nothing raw escapes public output/evidence | Safe code only |

</frozen-after-approval>

## Code Map

- `platform/deployment/tests/qualify_startup.py`: existing opt-in startup qualification entrypoint; add explicit real bootstrap control without changing existing synthetic defaults.
- `platform/deployment/startup_lifecycle.py`: owns root-key archive validation; extend owner-specific execution qualification here or a focused adjacent helper, retaining input validation.
- `platform/deployment/create_profile.py`: closed public environment and exact source-backed bootstrap bytes; reuse, do not regenerate SQL.
- `platform/deployment/images.py`: pins, qualified metadata and bounded subprocess runner. Reuse/extend rather than add a competing generic runner.
- `platform/deployment/startup.py`, `dev.py`, `tests/test_dev.py`: owner source bindings, qualified prerequisite checks and fixture copy lists; keep default `up` refusal and DockerSession container-route refusal.
- `platform/deployment/tests/test_startup_lifecycle.py`: independent archive fixtures; add meaningful qualification tests using command/transport doubles for refusal paths.
- `platform/deployment/DEVELOPMENT.md`, `apps/kdg-capture/docs/next-session.md`, `.memlog.md`: current status and handoff; append accurate bounded evidence.

## Tasks & Acceptance

**Execution:**
- [x] `platform/deployment/tests/test_postgres_bootstrap.py` -- add acceptance test first; implementation agent stops and reports RED command to root before production edits. Then use focused TDD for matrix rows. No socket tests in agents.
- [x] `platform/deployment/startup_lifecycle.py`, `images.py`, `tests/qualify_startup.py` and necessary owner bindings -- implement bounded bootstrap qualification using existing owners. Inspect selected immutable image's initialization semantics; expected SQL facts must derive from pinned bootstrap, not guessed readiness.
- [x] `platform/deployment/ENV_POSTGRES_BOOTSTRAP_EVIDENCE.md` -- record exact RED/GREEN, actual synthetic image run and cleanup, requirement-to-test mapping and limits; run affected acceptance then deployment regression.
- [x] Runbook/handoff/spec -- record scaffold, shared UI, agent context, documentation and ADR impacts; update status without expanding scope.

**Acceptance Criteria:**
- Given qualified selected image and fresh isolated storage, when the public bootstrap and key execute, then SQL completion is demonstrated by expected role password checks, JWT settings, `supabase_functions` migration markers, `_supabase` schemas and actual key bytes/path/mode/owner checks.
- Given failed or ambiguous execution, when qualification returns, then it cannot report initialized/runtime readiness and cannot touch unowned resources.
- Given completion, when reviewing evidence, then actual observations and remaining lifecycle/scaffold gaps are explicit, and existing guarded CLI/unit behavior remains passing.

## Implementation Notes

Standing authorization covers this bounded synthetic local proof; no further host upgrade or infrastructure provision is needed. Root coordinates actual image pull/execution and retains any failed attempts. Implementation agent must pause after acceptance test creation for root's observed RED, then await resumption. No remote operations or commits by agents.

2026-10-17: Initial source-bound run `2dbb8d67-baff-426c-8126-7221f992bfa8` passed preparation/toolchain/images and executed bootstrap through matching seven-role catalog verifiers, then refused `execution_failed_password_authentication`; owned cleanup completed. This exposed an incorrect test assumption, not an unexplained failure. Immutable selected image's `/etc/postgresql/pg_hba.conf` (SHA256 `a925911753f4975548eb4079177441c886aa22b6dd69f2b0cff98f779fb0b66a`) explicitly trusts loopback at lines87–88; other host rules require SCRAM. Preserve exact image/input profile. Characterize its actual loopback policy separately; password installation is proven by catalog verifiers, not authentication on a trust connection. No requirement or pinned bootstrap is weakened. Source audit used two never-started disposable containers; both removals verified.

2026-10-17: Focused19 tests PASS (0.231s); actual fresh selected-image proof PASS (30.603s),13 retained files unchanged, runtime false. Deployment regression448 tests PASS (278.610s). The suite message about staging run42 belongs to isolated fixtures, not a deployment. All five impact decisions and remaining enclosing ENV/scaffold acceptance are recorded in ENV_POSTGRES_BOOTSTRAP_EVIDENCE.md.

2026-10-17 final: All review patches verified with26 focused tests PASS (0.227s) and455 deployment tests PASS (270.685s), exit0, durably recorded after the preceding final-suite session result was unavailable. Fresh run `46880d40-9483-4485-96c6-ca5b211d21f7` passes preparation/toolchain/images, actual bootstrap (29.612s) and actual pinned CLI guarded-fresh (63.83s). A publisher retag selected child `sha256:e85bc10ac5b141223b289e1e8dc8d448cf3df92501917149db0366b9c5aaf053`; download and separate source audit confirmed unchanged entrypoint/migration/HBA bytes before final execution. No receipt repair or substitution. All13 retained files and the final running inventory remain unchanged; owned cleanup is verified. Actual final up exits2 runtime_adapter_unqualified/runtime_ready=false. Eleven finding instances patched, one low suggestion rejected, none deferred. Enclosing ENV/P1/SERVICE acceptance remains partial; no dependent implementation is authorized by this proof. See evidence for exact commands, protected records, earlier attempts and five impact decisions.

## Spec Change Log

## Review Triage Log

Three layers completed. The verification layer reused an available independent reviewer after a new thread hit the host thread limit; it had no current implementation context. Twelve review/root finding instances are triaged individually below, before grouping.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| Blind1 | medium | Actual closed create lacks memory/CPU/PID constraints, so fixed execution/output bounds do not cap host resource consumption. Direct create flags and matching ownership checks are a patch. |
| Blind2 | medium | Actual create inherits daemon logging; subprocess capture bounds do not cover persisted Docker logs. Set and verify log driver none; patch. |
| Blind3 | low | Cleanup failure hides original execution stage/ID, but CLI UUID deterministically identifies the unique run-labelled name for manual inspection; automatic uncertain adoption/delete stays forbidden. New recovery result/persistence surface would add complexity on this rare failure path; reject under the low-finding rule. Document the existing lookup without claiming label-based deletion authority. |
| Blind4 | medium | Checking a fixed tmpfs path alone does not establish active PostgreSQL data_directory. Query and verify actual configured directory before the filesystem observation; patch. |
| Blind5 | medium | False JWT/marker/schema SQL observations are absent from existing doubles; success-only actual proof cannot detect deleted refusal checks. Add independent negative observations; patch, grouped with Verification1. |
| Blind6 | medium | Existing total-deadline test only expires before create, leaving fresh cleanup budget after mid-init expiry untested. Add deterministic mid-init expiry case; patch. |
| Blind7 | medium | rm command refusal is covered, but successful rm plus still-present observation is reachable and untested. Add this cleanup-unresolved case; patch. |
| Blind8 | medium | KeyboardInterrupt bypasses ordinary exception capture but must still traverse finally; after-create/init interruption cleanup lacks tests. Add bounded deterministic cases; patch. |
| Blind9 | low | Module descriptions incorrectly state no daemon dispatch for opt-in actual control. Direct description correction; patch. |
| Edge1 | medium | HBA exec is followed by wrong-password exec without a fresh owned check; an attached network change during the former is observed only later. Insert owned check and a late-network-change test; patch. |
| Verification1 | medium | Reviewer mutation removed all three semantic refusals while all19 focused tests passed. Trust filed verification evidence; independent false SQL result cases and cleanup assertions; patch, grouped with Blind5. |
| Root1 | medium | Injecting valid JSON `[null]` for owned container inspection after create raises AttributeError, bypassing explicit cleanup-unresolved conversion; public main emits generic startup_proof_refused while the container remains unresolved. Direct observation-shape refusal correction plus regression case; patch. |

## Verification

- `python3 -m unittest discover -s platform/deployment/tests -p test_postgres_bootstrap.py` -- observed behavioral RED, then all matrix tests GREEN.
- `python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id <fresh-qualified-uuid> --control postgres-bootstrap` -- actual selected-image SQL/key proof and verified cleanup, runtime false.
- `python3 -m unittest discover -s platform/deployment/tests` -- affected owner regressions pass after focused tests.

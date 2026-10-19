---
title: 'ENV owner post-Auth setup tail'
type: 'feature'
created: '2026-10-19'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'c4b7bfe1a0d865f2a0b4c8be4fa70d3d6a79d444'
context:
  - '{project-root}/platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md'
---

<frozen-after-approval reason="standing bounded ENV implementation and synthetic verification approval">

## Intent

Advance the existing ENV owner beyond verified API default privileges through the
selected empty/disabled setup tail and current-branch initialization. This removes
the next concrete setup/custody gate without introducing SQL or pretending the
terminated CLI resumed. Prove the owner-completed boundary through the existing
synthetic qualifier and normal owned cleanup.

## Boundaries & Constraints

Always require the existing healthy same-PG/Auth/backend/default-privilege proofs,
terminated CLI, unchanged fixed config, empty Vault, absent roles.sql, disabled
migrations/seeds and no experimental enablement. Preserve source/resource/fixture/
executable custody, original deadlines, error precedence, no replay, terminal finish
and normal cleanup. Consume a tail attempt before mutation. Initialize only the
fresh private fixture's supabase/.branches/_current_branch with exact bytes main
(no newline), file mode0644, protected owner directory. Independently verify and
retain artifact identity/content custody through cleanup before publishing the fact.
Preexisting artifacts are not adoption authority; refuse rather than overwrite.

Narrowly admit the new artifact only under explicit owner-tail custody. Ordinary
controls keep their current closed directory inventory. Reject symlinks, hardlinks,
unsafe ownership/modes, extra entries, changed/replaced bytes or directory/file
identities and configuration/roles contamination. Do not weaken other path guards.
Failures publish no success and never authorize uncertain resource deletion/retry.

Never add SQL profiles/allowlist authority, arbitrary Vault/roles/migrations, resumed
CLI execution, readiness or generic filesystem/service/generator abstractions.
Keep runtime_ready=false and fresh_setup_completed=false; name the separate fact
owner_post_auth_setup_tail_verified. No actual Docker in this increment. Keep all
receipts/state/uncertain Docker resources, concurrent work/index, TS7.0.2/mail15484.
No Leave, dependent services/KDG, production, deployment, real data or push.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Selected success | All existing proofs and fixed disabled tail inputs | Exact marker created/independently verified; separate fact after normal cleanup; no additional SQL | Existing stage/code on failure |
| Missing/order/replay | Missing prerequisite, wrong phase, repeated/failed attempt or finish | No marker mutation/qualification or replay | Safe refusal |
| Contamination | Changed config, roles.sql, preexisting branch, unsafe/extra/symlink/hardlink/replaced artifact | No adoption/overwrite; subsequent custody fails | Preserve uncertain state |
| Budget/cancellation | Expired original budget or interrupted artifact operation | No completion fact; original cancellation/deadline and cleanup authority retained | No reset/retry |
| Ordinary control | Existing default-privilege/catalog/backend control | No tail artifact/fact, original behavior | Original guards |

</frozen-after-approval>

## Code Map

- platform/deployment/resources.py: FreshGuard enable chain, api_default_privileges_sql,
  _fixture/current/check, finish_execution: consumed tail and verified custody.
- platform/deployment/startup.py: _check_workdir/check_fixture_custody must default to
  strict inventory by default; guarded_fixture_command invokes tail after defaults
  and before finish; synthetic_probe binds control/results.
- platform/deployment/tests/qualify_startup.py: existing EXECUTION_CONTROLS mapper;
  add pinned-cli-postgres-post-auth-setup-tail, not a new command/framework.
- tests/test_pinned_execution.py: ApiDefaultPrivilegesOwner fixtures plus focused
  ordering/custody/budget/replay tests. tests/test_resources.py: ExecutionSupervisor
  process acceptance using existing independent synthetic daemon, cleanup oracle.
- Pinned CLI commit753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4 primary source snapshots:
  platform/deployment/.local/post-auth-setup-tail/primary-source/sources.json records
  URLs/hashes: vault.ts34–38 empty no-op; migrate-and-seed.ts62–83 disabled/nonexperimental
  skip; seed.ts71 disabled no-op; db-setup.ts759–785 absent roles skip,679–712 main0644;
  start-database.ts231 branch after setup. dev.configuration/closed invocation govern,
  not root config. No runtime dependency on these .local source snapshots.

## Tasks & Acceptance

- [x] Add meaningful public/process acceptance RED before implementation, then focused
  TDD for every matrix row using existing owner/daemon fixtures.
- [x] Extend existing owner/startup/qualifier with guarded tail and branch custody;
  preserve ordinary controls and existing SQL/cleanup boundaries.
- [x] Root verifies affected suites/processes and records requirement-to-test mapping
  plus scaffold/UI/context/documentation/ADR decisions in evidence/runbook/KDG handoff.

Given verified default privileges on the selected synthetic owner, when its tail
completes and normal cleanup succeeds, then exact main artifact and custody are
proven, config unchanged, no new SQL exchanges, separate owner fact true and both
readiness fields false. Given any missing prerequisite or custody/budget/operation
failure, when qualification is attempted, then no success/fact or destructive replay
occurs. Existing controls still pass without silently entering the tail.

## Implementation Notes

bmad-help selects this ENV prerequisite. No intent gap/irreversible external effect;
medium footprint routes dispatch. Standing approval covers dirty-tree preservation,
implementation, synthetic verification and local commit. Root owns docs/verification/
review/commit; child owns source/tests, RED first, exact logs in .local/post-auth-setup-tail,
and review patches. Do not invoke other skills or spawn nested agents.

## Verification

Smallest failing acceptance then focused owner/branch matrix, affected owner/startup/
workspace tests and selected process positives/negatives/ordinary controls. Root
chooses affected selections after diff audit and records exact commands/results/hash
bindings. No full-suite or actual-Docker claim is required. Preserve initial failures
without changing expectations. Five impacts: existing scaffold owner only; UI/context
none; docs existing runbook/evidence/KDG resume; existing ADRs unchanged.


Root diff/task/matrix audit complete.274 exact distinct IDs PASS across five serial
selections (166 owner,40 adapter,19 lifecycle,44 resource,5 process), zero skips;
74 source/test and39 historical prerequisite hashes unchanged. All five matrix rows
have executed named tests in evidence. No actual Docker/full-suite/runtime claim.
Initial child process failures remain retained; later serial/root passes do not
explain original timing. Independent review and scoped local commit follow.


## Review Triage Log

All three layers reported before triage:9 blind findings,1 edge finding,1 verified
regression gap. Every filed finding is retained individually below.

| ID / layer | Verdict | Evidence and route |
| --- | --- | --- |
| B1 blind | medium | Root injected replacement between mkdir and open: the replacement directory received main and _tail_completed became true. Patch staged pinned artifact publication without destination overwrite; deterministic race regression. |
| B2 blind | medium | Root replaced supabase immediately before mutation reopen with an exact-config copy: tail accepted the new parent. Patch independently retained parent binding across pre-mutation validation and reject substitution. |
| B3 blind | low | Same-inode rewrite restored to main is accepted, but current identity/content remain valid and no historical no-write promise is made. No harmful semantic change is demonstrated. Reject mutation-history guards: rare private-fixture interference and additional state exceed this negligible concern. |
| B4 blind | maybe-false | Explicit fsync can block in principle; an indefinite stall on the selected local filesystem is not demonstrated. Existing deadline checks are cooperative around filesystem work. Defer unverified medium filesystem-blocking investigation; measured blocked operation/cancellation timing would settle it. |
| B5 blind | low | An owner-bit-masking umask can prevent exact0700 directory creation. Initial fixture creation/protection already refuses that environment and the owner does not change umask. Reject additional mode-repair complexity for this unsupported rare state. |
| B6 blind | low | New tests inject cancellation but omit OSError at individual filesystem boundaries. Patch direct fault-injection tests for original outcome, consumed attempt, no fact and uncertain cleanup preservation. |
| B7 blind | low | Process tests omit deadline/cancellation during tail creation. Patch existing process helper with both failures and no success/extra SQL/replay. |
| B8 blind | medium | New process tests call synthetic_probe directly; removing a public inventory entry leaves them passing. Patch real public dispatch acceptance through qualifier/startup adapters. |
| B9 blind | low | Exact commands are committed, but frozen-source/ID manifests are ignored. Patch evidence with committed source hashes and manifest digests alongside complete direct selection commands; keep runtime logs/receipts local. |
| E1 edge | medium | Same reproduced branch-publication identity substitution as B1. Group with B1 for one staged pinned publication fix. |
| G1 verification gap | medium | Pre-verified: public main/startup.qualify routing is bypassed; either inventory can regress while tests pass. Group with B8 for public acceptance patch. |
| F1 root verification | maybe-false | Child's first process group fails before tail; concurrent source/unit work prevents a stable binding and timing cause is unmeasured. Unchanged serial and root groups pass. Defer unverified medium acquisition/process timing investigation; retain original failures and capture stable source/timing to settle cause. |

Original implementation agent re-engaged for the six direct source/test corrections;
root owns committed evidence correction and append-only deferrals. Frozen intent,
existing deadlines and expectations are unchanged. Initial274-test proof is retained
as pre-review evidence, not relabeled as final patched source.


Additional patch audit finding F2 — medium, patch: pathname-based staging follows a
substituted work/tmp symlink before the subsequent directory validator refuses.
Root's isolated injection creates one empty directory outside the fixture. The
original agent is replacing staging mutation with retained tmp/source/destination
dirfds and adding a deterministic no-foreign-write regression. This corrects the
same existing scope/identity invariant; no frozen intent change or extra authority.


| Additional root audit | Verdict | Evidence/route |
| --- | --- | --- |
| F2 staging path | medium | Reproduced one foreign empty staging directory after tmp symlink substitution. Patched by retained tmp descriptor, relative mkdir/open and dirfd-to-dirfd no-replace publication; RED/GREEN regressions include mutation/publication swaps and no foreign creation. |

All source/test patches are complete. Separate final root bindings/plan/logs retain
pre-review274 results as history. Final plan selects172 owner,41 adapter,19 lifecycle,
44 resource and6 process cases (282 distinct IDs). Frozen intent is unchanged.


## Completion

Final282 distinct selected tests PASS across five serial selections, zero skips:
172 owner,41 adapter,19 lifecycle,44 resource,6 process. Root independently verifies
all verbose IDs/log hashes,74 frozen source/test bindings,39 historical prerequisite
files and frozen intent. Exact commands/timings/core hashes/manifest digests and all
five impacts are in ENV_POST_AUTH_SETUP_TAIL_EVIDENCE.md. All11 external findings
and2 root observations individually triaged; patches verified,2 negligible concerns
rejected,2 unverified-medium investigations appended to deferred work. Initial proof
and failures are preserved separately.17 concurrent files/index unchanged; no actual
Docker, full-suite, complete fresh setup or runtime/dependent readiness claim.
Scoped conventional local commit only; no push or other outside-approval action.

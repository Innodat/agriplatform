---
title: 'ENV guarded post-Auth default-privilege execution'
type: 'feature'
created: '2026-10-19'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7a0c3d741b58998553b696d58272367577fe158b'
context:
  - '{project-root}/platform/deployment/ENV_API_DEFAULT_PRIVILEGES_SEMANTICS_EVIDENCE.md'
  - '{project-root}/platform/deployment/ENV_API_DEFAULT_PRIVILEGES_REQUEST_EVIDENCE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

The pinned post-Auth SQL is source-matched and rollback-qualified, but the existing
ENV owner cannot execute it under custody. Add one opt-in disposable qualification
control, pinned-cli-postgres-api-default-privileges, that uses the retained owner
to apply the exact SQL in a bounded transaction and independently verify its direct
default-ACL result before normal cleanup. This advances the existing ENV foundation.

## Boundaries & Constraints

**Always:** Require current backend presence/departure, terminated/reaped CLI, fresh
Auth pre/job/disposal/post checks and the same healthy owned PostgreSQL instance.
Preserve one connection, source/config/resource custody, deadlines, detached output,
safe errors and consume-before-dispatch/no replay. Keep original raw-source request
refused; allow only two new exact typed envelopes for bounded apply/read-only verify.
Apply embeds the exact417-byte source SQL; transaction checks the normalized default
ACL delta against its own before snapshot, excluding only postgres/public target
privileges. Independent verification requires no remaining direct target tuples.
Publish api_default_privileges_verified only after both zero-exit proofs and final
custody. Finish requires it for the opt-in control. Existing controls retain behavior.

**Never:** Resume the CLI or mark fresh_setup_completed/runtime_ready true; claim
effective denial through global/PUBLIC/inherited authority; migrate on API startup,
repair grants automatically, reverse committed SQL after failure, access production
or real data, create accounts/services/generators, change baseline/ports or implement
Leave/Identity/Access/WRITE/KDG consumers. Preserve concurrent documents/index,
receipts/state and uncertain prior Docker resources. Only synthetic owner-verified
resources may be created/disposed by the existing lifecycle.

## I/O & Edge-Case Matrix

| Scenario | State | Expected behavior | Failure |
| --- | --- | --- | --- |
| Selected success | Fresh qualified disposable run, all prior proofs pass | Apply then independent read-only verification, cleanup, separate fact | none |
| Missing prerequisite/ordinary control | Earlier proof absent or opt-in disabled | No privilege exec | invalid_owner_handoff |
| Changed command/envelope | Altered SQL/options/types/extra keys | Reject before mutation | existing safe refusal |
| Uncertain/nonzero exec | Lost response, bad identity/state, nonzero exit | No fact/finish/retry; preserve custody rules | existing exec/transport refusal |
| Custody/deadline change | Any apply/verify boundary | No success/replay | existing custody/timeout refusal |
| Attempt repeated/finish incomplete | Prior attempt consumed or verification absent | Refuse without another SQL/start | invalid_owner_handoff |

</frozen-after-approval>

## Code Map

- platform/deployment/startup_lifecycle.py: keep raw profile refused; add bounded
  apply/read-only verify profiles with private canonical builders/typed validators.
- platform/deployment/dev.py: add only exact two bodies to _docker_persistence_route.
- platform/deployment/resources.py: FreshGuard enable/attempt/verified state and finish
  gate, auth_pg_current around exchanges. Internal exec extraction requires existing
  characterization tests first. Reject SQL after _finish_attempted, even in phase5.
- platform/deployment/startup.py: control/fixture sets, enablement, post-Auth ordering,
  result stage/fact. tests/qualify_startup.py: new control in existing dispatcher.
- platform/deployment/tests/test_pinned_execution.py:146 existing characterization
  tests; independent daemon must distinguish apply/verify from catalog post.
- platform/deployment/tests/test_resources.py: private process supervisor, stopped
  CLI/descendants, deadlines, ordering, negative exec paths and verified cleanup.

## Tasks & Acceptance

**Execution:**
- [x] Lifecycle/dev owners: closed SQL profiles and allowlist; no raw-source admission.
- [x] Resources/startup/qualifier owners: opt-in guarded execution and result only.
- [x] Existing owner/process tests: ATDD RED first, focused TDD, prior behavior and
  closed profiles, prerequisites, replay, failures, ordering and lost-custody coverage.
- [x] Root: fresh prepare/toolchain/images; actual new control plus backend/catalog
  compatibility; final affected/full regression after review. Preserve failures.
- [x] Root: ENV_API_DEFAULT_PRIVILEGES_OWNER_EVIDENCE.md, DEVELOPMENT.md and KDG
  next-session/.memlog; requirement-to-test mapping and five impact decisions.

**Acceptance Criteria:**
- Given prior proofs, when selected, then exactly one apply and one verify execute
  in order under current custody and only successful independent proof permits finish.
- Given any failed prerequisite/attempt/custody/SQL result, when retrying or finishing,
  then no additional privileged SQL or qualified fact is produced.
- Given an ordinary control or raw/altered request, when exercised, then its earlier
  behavior/refusal remains and the new fact is absent.
- Given an actual isolated qualified run, when the new control completes, then cleanup
  is verified, unrelated resources/retained receipts remain and readiness stays false.

## Implementation Notes

- bmad-help selects this bounded ENV item; medium cross-owner footprint routes to
  dispatch. No intent gaps. Standing implementation/synthetic verification approval
  and repeated next authorize proceeding without another owner acknowledgement.
- Starting canonical HEAD7a0c3d741b58998553b696d58272367577fe158b. Concurrent/index
  checkpoint under .local/api-default-privileges-owner-qualification. Root owns docs,
  actual/full verification, review and commit; implementation child changes code/tests.

Implementation coordination: control `pinned-cli-postgres-api-default-privileges`, result
stage `pinned_cli_postgres_api_default_privileges`, fact `api_default_privileges_verified`.
FreshGuard `enable_api_default_privileges()` enables backend/catalog prerequisites;
`api_default_privileges_sql()` consumes `api_default_privileges_attempted` before
`api_default_privileges_bounded_exec('apply')` then `('verify')`. Order: backend
present, CLI terminated/reaped, backend departed, Auth pre/job/disposal/post and raw
request refusal, bounded apply, independent verify, normal finish/cleanup. Query
markers distinguish delta-failed apply and verification-failed verify from catalog post.

## Verification

- python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
- Focused ExecutionSupervisor tests for new/ordinary controls using private sockets.
- Existing prepare/toolchain/images/new qualifier commands on fresh UUID; record exact
  commands/results/hashes and source/test bindings. Full deployment unittest discovery
  on final reviewed source; no root npm build/dev verification claim.

- Implementation allocation: api_owner_impl owns lifecycle/dev/resources/startup/
  qualifier and test_pinned_execution.py; api_owner_process_tests exclusively owns
  test_resources.py additions. Coordinate guard names/order via Implementation Notes
  and direct messages. Neither child runs actual Docker/full suites or commits.

- Root verification addendum: use existing qualifier-only auth-catalog post hook
  for a fixed rollback semantic matrix exercising the new production apply/verify
  DO predicates themselves. Seed a global anon EXECUTE default plus direct public
  target grants; require global preservation and per-schema removal, verify rejects
  a deliberately reintroduced direct grant, and apply delta rejects omitted/extra
  SQL. Execute predicates as postgres, snapshot/restore defaults via subtransaction,
  retain original catalog predicate and all bounds. No new public control/SQL input
  or production changes. api_owner_impl owns this qualifier/test-only follow-up.

Root checkpoint:156 focused tests pass; all672 discovered tests covered across
retained prefix/repeat/20 partitions (single discovery exits143, cause unconfirmed).
Actual owner and backend controls pass with normal cleanup. Ordinary catalog
compatibility refuses execution_cleanup_unresolved and retains exact-run resources;
separate cleanup approval pending before its repeat and actual seven-predicate matrix.
All27 source/test bindings and13 prerequisite files remain unchanged.

## Review Triage Log

All three independent layers completed before triage. Edge-case hunter returned
no findings. Blind hunter's floor arithmetic is metadata, not a defect.

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| B1 | medium | Confirmed finish checks prerequisites before consuming the attempt; calling finish with verification absent leaves SQL callable. Patch: consume at entry and characterize this demonstrated failed-finish state. |
| B2 | medium | The actual seven-predicate matrix is not yet executed; string/fake-daemon tests cannot detect a vacuous independent SQL verifier. Patch: execute the existing fixed matrix before completion; same root as V1. |
| B3 | medium | Actual ordinary catalog run refuses and retains its Auth job/database before new privilege dispatch. Auth job removal code is unchanged from baseline. Defer the pre-existing cleanup/diagnostic failure investigation; preserve failure and repeat compatibility only after separately approved exact cleanup. A later pass will not explain the refusal. |
| B4 | maybe-false | SIGTERM is recorded without a unittest failure or sender/cause. Partitioned coverage does not establish absence of accumulated-process effects. Defer medium, unverified: settle with signal provenance or a reproducible supervisor/order failure; retain exact interrupted command/log. |
| B5 | medium | Grantability is a promised preserved tuple field, but the fixed matrix has no grantability-only mutation. Patch the existing bounded synthetic matrix with a grant-option sentinel and a rejection case; no production surface change. |
| B6 | medium | Full-database tuple preservation is promised, but explicit unrelated owner/schema mutation is absent from the fixed oracle-sensitivity cases. Patch the same matrix with an unrelated-schema sentinel and mutation, retained on success and rolled back afterwards. |
| B7 | false | The extracted _auth_owned_sql has the same repeated stable/remaining checks on every poll, exercised by test_running_exec_then_success_and_deadline_preserve_one_start and test_starting_zero_pid_then_running_then_completed_qualifies through auth_catalog_sql. New-mode custody faults exercise the identical stable callback. Immediate completion in one new-mode test does not leave the shared repeated-observation path untested. |
| B8 | false | test_exec_failures_consume_pair_without_fact_finish_or_replay exercises verify create/start lost responses after successful apply, checks no fact/finish/replay. Real process transport uncertainty is covered for apply using the same unbranched _auth_owned_sql/session path. Additional SQL-mode duplication is not an uncovered behavior. |
| B9 | false | api_default_privileges_sql explicitly refuses phase != 5 before setting attempted or exchanging any request; final custody additionally enforces phase/ownership. A phase-table test is suggested but no reachable wrong-phase dispatch is demonstrated. |
| B10 | low | Evidence gives basenames without their retained directory, making local reviewer lookup ambiguous. Direct documentation patch: give artifact directory and source/receipt binding manifest paths. |
| V1 | medium | Filed verification gap accepted: fake/string tests and successful apply cannot reject an always-successful verify predicate. Execute the fixed actual reintroduced-grant rejection before completion; grouped with B2. |

Review patch outcome: finish consumption moved before phase/prerequisite checks;
focused RED/GREEN proves all three auth SQL methods stay blocked after a failed
prerequisite finish. Existing fixed rollback matrix expanded7→11 cases for preserved
grantability/unrelated-schema mutation rejection and preservation, without changing
production SQL profiles. Child12 owner +5 ordinary positive tests pass. Root final
674-test serial regression runs on post-review frozen source; actual prerequisites
will follow separately after port_unavailable was retained without mutation.

Additional final-verification triage:

| ID | Verdict | Evidence and route |
| --- | --- | --- |
| F1 | medium | Final partition37 initially sees docker_timeout instead of expected docker_response_invalid in initialized-create-malformed. Exact test passes unchanged on reviewed source10.761s and isolated baseline38.150s; eight involved initialized lifecycle methods are AST-identical to baseline and the failed create precedes finish/new SQL. Defer pre-existing nonreproducible protocol/timing investigation; original failed log retained, exact four-test partition repeated without expectation/deadline changes. Neither later pass explains the first timeout. |
| F2 | medium | Reviewed actual backend compatibility returns docker_timeout28.952s with no containers and an unused labelled volume/empty bridge retained. It does not reach a qualified result. Source27/prerequisite13 unchanged; acquisition/resource code is unchanged. Defer original timeout investigation, preserve resources, and use a separate fresh UUID for ordinary compatibility rather than adopting or replaying the uncertain run. |

Patch verification checkpoint: all674 unique discovered tests pass across48 serial
partitions, no skips; original partition37 timeout retained and exact group repeats
unchanged PASS. Actual expanded11-case matrix passes104.089s with normal cleanup,
no exact-run resources remaining and27 source/13 prerequisite hashes unchanged.
B2/V1/B5/B6 are verified. Final actual owner/backend/catalog controls follow.


## Completion

All six frozen matrix rows are covered by named owner/process tests and final actual
controls; R7 additionally executes11 canonical SQL-predicate cases. Final674 unique
IDs pass across48 partitions, no skips; initial partition37 failure remains retained
with unchanged isolated/baseline/group repeats. Actual reviewed owner76.618s and
matrix104.089s pass on2958e313-15c6-4ef6-b607-d9712333e7d7. Ordinary backend96.047s
and catalog85.329s pass on fresh9b276d1e-450c-4262-9e11-6bef12dde645. Successful runs
verify owned cleanup/readiness false; source27 and all39 prerequisite files match.
Only the failed reviewed backend's unused volume/empty bridge remain, preserved.
Three review layers completed; all patch entries verified, four operational entries
deferred, three findings refuted individually. No intent/spec loopback or public
surface expansion. Documentation and all five impact decisions complete. Concurrent
17 files/index preserved (one independent memlog advancement retained). Enclosing
ENV/scaffold and dependent gates remain open; this bounded increment alone is done.

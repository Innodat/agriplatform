---
title: 'ENV rollback-only API default-privilege semantics'
type: 'feature'
created: '2026-10-19'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

The source-matched post-Auth API default-privilege request is construction-qualified
but its SQL semantics are unproven. Add a fixed rollback-only semantic fixture to
the existing ENV startup qualifier, execute the exact source SQL on a disposable
selected PostgreSQL instance, and independently verify its precise direct-ACL delta.
Prove seeded target grants exist, unrelated defaults and existing objects survive,
new objects receive the intended direct grants, PUBLIC function access is not
mistaken for effective denial, and all synthetic changes roll back.

Use only existing test qualifier hooks and three fixed cases: apply, omitted SQL,
and an extra unintended revoke. The latter two must fail qualification. Keep all
production owners, transport allowlist, configuration, CLI-termination boundary,
dependencies and readiness gates unchanged. No persistent account/access changes,
production migrations, real data, deployment, new generator or generic SQL service.
Preserve concurrent work, receipts/state and uncertain Docker resources.

</frozen-after-approval>

## Implementation Notes

- bmad-help selects next ENV semantic prerequisite; small oneshot qualification-only
  change, no intent gap/irreversible action/public runtime API. Existing
  tests/qualify_startup.py fixed post-Auth fixture seam and test_pinned_execution.py
  own implementation/tests; root owns real isolated verification and documentation.
- Given a fresh qualified synthetic run, apply must pass independent direct-ACL and
  rollback predicates. Given omitted/extra SQL, execution must refuse with
  execution_sql_failed and return no qualified semantic fact. Observe acceptance
  failure first, focused TDD, then actual PostgreSQL controls.
- Use original auth catalog pre/post request wrapper, 5s statement/idle and1s lock
  bounds, supabase_admin over container-local socket as existing corruption fixtures.
  Execute source SQL under SET LOCAL ROLE postgres, reset role, verify new objects
  use postgres as creator. No new production route; internal fixture admitted only
  under narrowly scoped test hook. Production raw request must still refuse.
- Seed all21 direct target tuples (3 roles ×7 privileges), preserved table/sequence
  privileges and other role/schema/creator defaults. Normalize exploded default ACL
  tuples rather than ACL array ordering or catalog row IDs. Use an inner exception
  subtransaction for rollback with outer variables retaining before/after oracles;
  verify baseline/defaults and absent synthetic objects after catching only sentinel.
- PostgreSQL17 primary docs on ALTER DEFAULT PRIVILEGES and pg_default_acl confirm
  per-schema revocation cannot remove global/PUBLIC or inherited access. Fixed
  PUBLIC EXECUTE sentinel proves this limitation rather than claiming denial.
- Record requirement/test commands/results and five impact decisions in
  ENV_API_DEFAULT_PRIVILEGES_SEMANTICS_EVIDENCE.md; update existing runbook/KDG handoff.
- Starting canonical HEAD ac9907f06a6adcc6f6793686c7d38411c22be04e. Initial
  concurrent/index hashes retained in .local/api-default-privileges-qualification.
- Qualification-only helper and three focused tests implemented. Acceptance RED
  (missing helper) observed; one local Python syntax error corrected before GREEN.
  Full owner suite145 PASS3.045s. Fresh run e7643c35-6dfa-46a0-abda-9af41234dc43
  prepare/toolchain/images PASS; source/test/13 retained files frozen before actual
  apply execution. No production source or allowlist changed.
- Initial actual apply PASS73.507s with six invariants/rollback/normal cleanup;
  omitted41.092s and extra47.200s correctly refuse execution_sql_failed with zero
  verified invariants. Their source/logs remain pre-review evidence.
- Five independent oneshot review findings patched in the same owner: seed all
  object types for other role/schema/creator and a grant-option sentinel; replace
  aggregate counts with exact grantor/grantee/privilege/grantability tuple sets;
  add five rollback-only sensitivity corruptions for later oracles; bind runbook
  count to helper metadata and validate successful result fields/types.
- Review expansion initially crossed the unchanged16KiB request limit. Focused
  admission test caught it; fixed by storing fixed predicate SQL once in server-local
  variables and canonical JSON tuple ordering, not raising limits. Syntax/count
  transition failures retained in review-focused logs. Final146 tests PASS7.870s.
  Reviewed source/test bindings are separate from initial bindings; actual three
  cases repeat against the same unchanged13 prerequisites, each fresh database.

## Review Triage Log

- R1 low, patched: preservation seeds covered only table SELECT. Added sequence and
  function defaults for the other grantee/schema/creator so overbroad edits cannot
  be vacuous for those seeded types. Developer proof coverage improves.
- R2 low, patched: grantability was recorded but never true for a sentinel. Added
  authenticator function EXECUTE WITH GRANT OPTION; exact delta preserves it.
- R3 low, patched: only the delta oracle had negative controls. Five inner rollback
  corruptions now require rejection by the same existing/new/PUBLIC/default-rollback/
  object-rollback predicates. Only designated SQLSTATEs are caught; final state
  is checked again. External case choices and six invariant groups stay unchanged.
- R4 low, patched: count checks omitted full expected tuple identities. Explicit
  normalized21 target/15 retained sets now include grantor and grantability. No
  current reachable false acceptance was observed; stronger oracle precision is
  verified on the selected real PostgreSQL image.
- R5 low, patched: success annotation had a duplicated6 constant and insufficient
  result validation. Use returned helper count, check typed positive result/cleanup/
  false-readiness fields, reject false success in negative cases. A tracked-command
  regression tests count drift, missing cleanup, bool/int substitution and refusal.

## Verification

- Reviewed146-test owner suite PASS7.870s. Final actual apply PASS70.779s with six
  invariants/five sensitivity corruptions, omitted45.816s and extra51.046s correctly
  refuse execution_sql_failed and retain zero verified invariants. Exact tracked
  runbook code executed. Source SQL417-byte comparison PASS.
- All13 retained files unchanged, no unrelated running inventory delta; final
  read-only exact-run queries show no remaining containers/volume/bridge. No
  recovery removal or prior uncertain resource action. Production sources, limits,
  configuration/dependencies and public runtime refusal remain unchanged.
- All five review findings patched, none newly deferred. Five impacts and exact
  commands/results/hashes recorded in ENV_API_DEFAULT_PRIVILEGES_SEMANTICS_EVIDENCE.md.
  No full deployment suite or complete startup claim. Scoped local commit only,
  no push. Enclosing runtime/scaffold and dependent gates remain open.

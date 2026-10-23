---
title: 'Focused platform migration verification with KDG adoption'
type: 'refactor'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Apply the user-approved verification approach platform-wide: keep controlled migrations,
least privilege, application ownership and focused access tests; prefer ordinary Alembic/
PostgreSQL behavior over custom checks of their internal structures; promote proven
reusable fixtures/tests into scaffolding; add guards for concrete failure cases only.
Keep Supabase Auth/PostgreSQL, FastAPI business APIs and accepted ADR0015–0020 unchanged.

The shared inert migration helper currently permits only an empty owned schema or an
exact physical Alembic ledger. A normal future revision adding an owned table would
require changing this generic guard. Replace that inventory/ledger duplication with a
small controlled transaction wrapper. Alembic owns revision resolution and migration
execution; PostgreSQL owns permissions/transactionality. Keep exact migration login
and basic nonadministrator/schema-ownership checks, bounded owner locking/timeouts,
transaction rollback and secret-safe failures. Owners retain URL/command policy,
revision files, schema, explicit grants and real permission tests.

Given a correctly configured owner migration, when its schema contains ordinary app
objects or its Alembic history advances, then the generic helper allows execution
without a new object/revision allowlist. Given wrong migration identity or privileged
credentials, when invoked, then refuse before migration effects. Given a failed
migration, when the transaction exits, then propagate a safe failure and do not commit.
Tests must distinguish wrapper control flow from real PostgreSQL security evidence.

Update canonical scaffold helper and emitted behavioral tests in the same item,
synchronize KDG via the preservation installer, adapt KDG env wiring, and record the
platform approach in reusable guidance. Preserve relevant preexisting safety tests;
retire tests tied only to deliberately removed internal-structure assertions. Observe
an acceptance failure for normal owner-schema evolution before implementation.

This is a reversible code/scaffold verification slice only. Native KDG preparation/
acceptance remains a separate unfinished item with its previous narrow authorization;
do not run preparers, Docker lifecycle, SQL or the rejected broad historical verifier
here. Preserve the failed draft fixture and existing evidence without treating them
as qualified setup. No other app migration, shared-service rewrite, dependency/baseline
change (including TypeScript7.0.2), Leave/editor, production, real accounts/access,
provisioning, deployment/pilot, cleanup or fingerprints/HMAC.

</frozen-after-approval>

## Implementation Notes

- bmad-help [BD] selects this small shared verification correction from the user's explicit clarification. bmad-build oneshot: no intent gaps or irreversible effects, narrow canonical helper/tests + KDG adapter + guidance. No new public runtime service or lifecycle.
- Dirty tree/concurrent branch authorized by standing preservation instructions. Starting HEAD and every existing dirty/untracked file hash recorded in /tmp/platform-migration-simplification-before.json. Stage only this item's files.
- Code map: platform/builder-cli/templates/application/database-tools/{owned_migration.py,test_owned_migration.py}; sync-kdg-database.mjs owns apps/kdg-capture/database-tools copies/manifest; migrations/policy.py and env.py remain KDG-owned; migrations/tests/test_foundation.py verifies owner wiring. Builder database-pattern.test.mjs runs actual emitted tests.
- Requirements trace: AC1 ordinary schema evolution; AC2 login/least-privilege refusal; AC3 bounded serialization/rollback/safe errors; AC4 emitted test/parity/preservation; AC5 owner URL/command/history behavior. Exact commands/results will be appended.
- Impacts: scaffold helper/emitted tests updated together; shared UI unchanged; platform-wide guidance added and linked from builder + owner docs; existing agent-context rules sufficient; ADRs unchanged because this implements their guarantees with standard mechanisms. No historical evidence rewritten.

- Characterization before refactor: 10 emitted neutral and 8 owner tests PASS. Acceptance RED: new existing-owner-table/advanced-history scenario raises owned_migration_history_invalid before migration; /tmp/platform-migration-acceptance-red.log. This is explicitly test-double evidence.
- Implementation removed exhaustive catalogue/ACL/physical-ledger and fixed-revision duplication. Basic selected-login/owner checks remain; real privilege audit belongs to focused owner integration tests. Removed only expectations tied to deliberately replaced inventory behavior; native contracts remain unqualified.
- Canonical emitted tests and KDG adapter/wiring updated; sync installer updates managed copies/manifest. Alembic begin_transaction is used under the shared controlled transaction. Current owner revision file unchanged; no migration was run. Added actual unconfigured/prohibited-direction CLI refusal checks.
- Platform guidance lives at platform/docs/development/migration-verification.md and is routed from root AGENTS.md (append only; concurrent contents preserved) and builder docs/emitted README. Shared UI unchanged; no accepted ADR or dependency change. Native item remains unfinished and its failed fixture remains unchanged.

- Review exposed chained/private MigrationError diagnostics. Focused emitted regression failed before the fix (/tmp/platform-migration-safe-error-red.log); wrapper now reconstructs only known identifiers and suppresses causes, normalizing other messages. A fake callback direction refusal inside the transaction now uses that generic safe identifier; actual CLI refusal retains its owner identifier. This is an intentional, explained error-boundary change.
- Added the owner's final ledger REVOKE assertion before commit. No native privilege claim. The 11 emitted tests and 9 owner tests (including five actual CLI refusal cases) pass.
- Initial broader test invocation was interrupted (exit130) after stalling, and the bounded restricted-sandbox run exited124 after pending child-process tests. These are incomplete verification, not source-behavior REDs. Rerun uses approved Node/npm paths with an explicit overall bound outside the process sandbox; results recorded separately.

## Review Triage Log

- medium / patched: MigrationError pass-through could render private chained causes or arbitrary messages. Reproduced with a synthetic secret; normalization and emitted regression now pass.
- medium / patched: owner wiring did not assert final ledger privacy operation. Test now verifies exact PUBLIC/runtime/operator REVOKE before the engine commits.
- low / rejected: recording Alembic's nested begin_transaction would mirror an implementation detail. The existing external engine transaction already tests commit/rollback and guards the migration body; Alembic's nested context is a no-op under that external transaction. Actual PostgreSQL transaction behavior remains explicitly unqualified. No additional guard or test introduced.
- Review completed by /root/review_focused_migrations, read-only. Three substantiated findings; no new deferred defect. Earlier provisional link concerns were retracted after resolving the paths.

- Final checks PASS: 11 neutral emitted tests; 9 owner tests including five real Alembic CLI refusals; all72 builder regressions outside the restricted process sandbox (10.49s); strict TypeScript7.0.2; managed parity; scoped diff whitespace check. Fresh rendered/installed app emitted tests run inside the builder suite. No full dependency-install/browser generation run was needed or claimed for this migration-helper correction.
- Concurrent preservation: starting dirty/untracked files snapshotted. Root AGENTS preexisting content remains byte-identical; new platform section appended only. Unrelated Scribeswell/Leave/Identity planning files advanced concurrently and were not written or staged by this delivery. Failed native fixture/native spec, historical candidate evidence and accepted migration revision remain unchanged. No Docker/database operation or dependency change.

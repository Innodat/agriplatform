---
title: 'ID-B restricted current-account organization projection'
type: 'feature'
created: '2026-10-20'
status: 'done'
baseline_commit: '18c5b94566045dcca9973ce3365ea1af95e6287d'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/identity-access-execution-substrate.md'
  - '{project-root}/platform/docs/architecture/decisions/0018-transaction-scoped-tenant-context.md'
  - '{project-root}/platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md'
---

<frozen-after-approval reason="standing shared prerequisite implementation and isolated synthetic verification approval">

## Intent

Implement the selected internal identity.current_account_organization() read through
the existing Identity owner, so a verified account can resolve its current selected
organization membership and revision without person/employment setup. Include the
minimal additive membership revision needed by this read. This grants no app admission.

## Boundaries & Constraints

Return exactly account_id UUID, org_id UUID, membership_id bigint,
membership_revision bigint, actor_id UUID nullable internally. Require user context,
valid nonnil app.account_id and app.org_id; never select an account from actor assertions.
Only nondeleted profile/org/member qualify; unmapped profile keeps nullable actor.
No implicit actor/member provisioning. Use existing identity_account_projection_owner,
scoped permissive plus restrictive RLS, necessary column reads and exact access_runtime
EXECUTE. Fixed STABLE SECURITY DEFINER search_path and fully qualified objects.

Revision is positive bigint, existing/new rows start1. Server sets insert revision1;
on UPDATE compare all persisted non-revision fields: changed row advances once,
identical row preserves revision, supplied revision cannot forge/decrease it. Overflow
refuses atomically with a safe constraint error. Other fields keep legacy semantics.

Preserve UNIQUE(org_id,user_id), CASCADEs, supported seed/upsert/unretire behavior,
existing row IDs/attribution, old Access API, Auth hooks and all old migrations/references.
FORCE-RLS/lifecycle/retention/actor-backfill hardening remains a coordinated later gate;
new nonowner reader remains RLS-bound. No new roles, operator commands/outcomes, target
projections, HTTP adoption, providers/accounts/access changes, Leave/editor or deployment.
Keep exact locks/dependencies/TS7.0.2, concurrent work, receipts/state/resources.
Only isolated synthetic mutations are authorized; no new service/generator/runner.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Active account/member/selected org | Exact tuple; distinct mapped actor; no person required |
| Active unmapped account | Same tuple with nullable actor; read makes no writes |
| Invalid/missing/setup context; missing/deleted profile/org/member; other account/org | No row; actor/JWT assertions cannot broaden results |
| Revision insert/change/no-op/forgery/overflow | Starts1; change advances; no-op holds; caller cannot forge; overflow rolls back |
| Restricted caller | Exact function works; expanded raw reads/writes, owner assumption/replacement deny |
| Hostile search_path and connection reuse | Qualified data only; commit/rollback/error clear SET LOCAL scope |
| Clean/adopt/previous head/retry/failed upgrade | Old rows/hooks/queries remain; mismatch/unknown history refuse; partial DDL rolls back |

</frozen-after-approval>

## Code Map

- `services/access/identity-migrations/versions/0004_current_account_organization.py`:
  additive revision column/guard and selected read. Reuse revision3 owner/ACL pattern;
  no new preparation role or blanket grants. Preserve legacy table-level permissions.
- `identity_baseline.py`, `env.py`, `tests/qualify_identity_baseline.py`: extend the same
  verified history/final-head and independently recorded reference mechanism. Reuse
  captured-source/exclusive publication/manual-pin safeguards; avoid another recorder
  framework. New trusted reference validates all prior immutable fixtures/source pins.
- `tests/qualify_current_account_actor.py`: reusable actual-login/context/catalog
  helpers; do not change historical prior-head evidence. New organization qualifier
  and focused tests may reuse it; previous source is exact baseline18c5b945, head3.
- `scripts/seed.py:82` upserts on org_id,user_id, sets is_owner/deleted_at. Keep its
  conflict target and unretire semantics. `tools/identity_bridge.sql`, `main.py`, Auth
  profile/token hook, SQL seeds remain unchanged and need compatibility evidence.

## Tasks & Acceptance

- [x] `versions/0004_current_account_organization.py`: additive revision + read,
  exact grants/default ACL cleanup and scoped reader policies, no legacy hardening.
- [x] `identity_baseline.py`, existing qualification recorder: head4/trusted fixture;
  retain old fixed references and migration digests; verify full reader authority.
- [x] `tests/`: acceptance RED then focused TDD, actual matrix, previous-code
  upgrade/legacy writer/hook behavior, rollback and unsafe catalog/history refusal.
- [x] `IDENTITY-MIGRATIONS.md`, organization evidence, inventory and KDG navigation:
  requirement-to-test commands/results and all five impacts.

Given verified context, when the restricted login resolves its selected membership,
then only that current account/org tuple and server revision return. Given failed
migration, when activation is attempted, then no partial revision/read is committed.

## Implementation Notes

No unresolved intent gap. Standing approval covers this bounded additive item and
synthetic proof; unrelated dirty-tree documents remain untouched. Root owns actual
DB/lifecycle/reference recording/evidence/navigation/audit/commit. Implementation agent
owns migration/helper/recorder/focused tests/new actual qualifier/owner runbook; no
DB/Docker operations, generated-reference edits, commits or extra agents. Canonical
owner Python: platform/deployment/.local/identity-baseline/qualification-im60qj1l/
owner-env-djguxc78/offline-venv/bin/python. Root will record and explicitly pin the new
reference. Keep actual qualifier interfaces small and coordinate before execution.

## Spec Change Log

## Review Triage Log

All three review layers returned before triage; each finding is recorded separately.

| Finding | Verdict / route | Evidence and disposition |
| --- | --- | --- |
| G1 projected revision only checked at1 | medium / patch | All successful lookup assertions use revision1; row-only mutation tests would not catch a constant returned revision. Add committed change/no-op assertions through actual runtime lookup. |
| B1 prior actor qualifier hashes new revision as old data | medium / patch | Its legacy/head2 before/after comparisons include full org_member JSON while default upgrade now reaches4. Exclude only this known additive field in historical upgrade comparisons, with characterization; retain full failure/read-state checks. |
| B2 temporary fixture grants survive CREATE/INSERT failure | medium / patch | Restoration occurs after both fixtures without finally. Restore only newly added direct grants in finally; add injected fixture failure regression. |
| B3 org reader policy permits selected org without account | low / patch documentation | Org policy intentionally checks user context/selected org; member policy additionally checks account. Ordinary runtime cannot assume the reader and the fixed routine validates account before any query. Clarify per-table guards; no new policy needed. |
| B4 revision concurrency untested | medium / patch | Supported legacy writes can overlap, but current revision proof uses one connection. Add two bounded competing committed changes and verify final increment2. |
| B5 revision writes tested only as owner | medium / patch | Current guard executes as invoker, with no owner-only DML; ordinary legacy invocation needs proof. Add actual postgres LOGIN used by retained SQL seeds and verify change/forgery behavior; do not broaden any role. |
| B6 unlisted default function grantee not injected | low / reject | Original preflight pins all default ACLs and refuses an added unlisted default before migration. PUBLIC default removal and resulting effective function privileges already execute. Reaching this extra branch would need administrator DDL during exclusive migration; adding event-trigger/default-ACL machinery for that excluded state is disproportionate. |
| B7 own new reference missing/corrupt pin cases absent | medium / patch | Prior fixture corruption tests do not exercise new file removal/content or its fixed digest mismatch. Add direct fail-closed cases. |
| B8 multirow exhausted revision rollback untested | low / patch | Existing overflow check tests one row. Add one bounded multirow update in a savepoint and compare both rows unchanged. |
| B9 exhaustive direct-reader invalid contexts missing | low / reject | All caller context cases execute through the only granted routine; direct reader cannot be assumed by runtime. Existing raw-reader valid/spoofed-account tests establish table-local predicates. Broader direct-role fixture branches duplicate guard tests and would require distinguishing local member/org predicates from the routine join. Clarify that distinction under B3; no runtime hole demonstrated. |
| B10 joined words/counts | low / patch | New evidence/navigation contain pass.111/plus111 and adjacent identifiers; correct spacing in new passages. |
| E1 temporary grants survive fixture failure | medium / patch, group B2 | Same reached CREATE/INSERT failure path; finally restoration and injected failure characterization address both. |


## Verification

Canonical owner pytest services/access/tests and apps/pts/tests/test_release.py;
legacy and owned composer check-only. Actual PostgreSQL17 restricted-login matrix,
old owner source/head3, legacy upsert/Auth token/profile hooks, mismatch/rollback.
Exclusive new receipts; original files/references/lock and concurrent-file audit;
normal retained-data Supabase CLI stop. Scaffold remains owner-local/unpromoted;
shared UI none; agent context sufficient; docs owner/handoff; existing ADR0018/0020/
0056 and selected substrate suffice, no accepted ADR edit or new decision.

Actual acceptance RED observed before implementation: restricted access_runtime LOGIN
gets SQLSTATE42883 for the missing function; retained current-organization-t3mdjqiv.

Complete actual matrix PASS on organization-final-w4snwcju: exact prior head3,
current/read/revision/upsert/Auth-token/profile/rollback/refusal/drift scenarios all
execute.111 affected tests and both composers PASS. Fixtures preserve original direct
ACLs and their order after a focused RED1/GREEN2 regression; failed frames retained.
See [evidence](../../services/access/CURRENT_ACCOUNT_ORGANIZATION_EVIDENCE.md).


Reviewed completion: three layers, 12 individually triaged findings, 9 patch groups,
2 low rejections and no deferrals. Fresh complete reviewed actual matrix passes,
including advanced projected revision/no-op, two contending commits, observed legacy
postgres writes and multirow overflow. 119 affected tests and both composers PASS.
DDL and all trusted reference bytes remain unchanged; source-stable receipt under
organization-reviewed-final-u8insh8h. Historical failed frames remain retained.

Final audit: all 2563 unrelated prior files unchanged; original migrations 1–3,
references/pins/lock/runtime/bridge/seed source unchanged. Normal retained-data stop
passes and volume/bridge/configuration remain; no reset or explicit resource cleanup.

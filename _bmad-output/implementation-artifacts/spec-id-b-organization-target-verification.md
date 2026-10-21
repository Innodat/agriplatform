---
title: Private Identity organization verification for Access setup
type: feature
created: '2026-10-21'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: b6c8b22abbb4318cba452a308eef80d716718aa0
context:
  - AGENTS.md
  - platform/deployment/DEVELOPMENT.md
  - platform/docs/architecture/contracts/identity-access-execution-substrate.md
---

<frozen-after-approval reason="standing bounded prerequisite implementation approval">

## Intent

Stage the private account-free Identity point check needed before Access organization configuration. No suitable existing routine exists: current projections require account/member identity. Reuse the existing target projection owner and selected-org RLS, not another service or directory.

## Boundaries & Constraints

Add Identity0019, following18: identity.organization_target(p_org uuid) RETURNS TABLE(org_id uuid), STABLE SECURITY DEFINER, search_path=pg_catalog,pg_temp. Return exactly the requested existing nondeleted organization UUID or no row. Require exact nonnil selected org UUID, valid nonnil actor assertion, context_kind=setup and absent/empty account context. Missing/malformed/mixed/user context, nil/null parameter or another org returns no row without cast errors. UUID casing is accepted by typed equality. No account, membership, person, employment or grant prerequisite; expose no metadata/list.

Reuse identity_target_projection_owner's existing SELECT(id,deleted_at) and forced/restrictive org policies. EXECUTE only for access_command_owner, plus owning definer; no new roles, table/schema grants or policies. Strip inherited/unlisted routine grants atomically, preserving default ACLs. Assertions are trusted backend context, not independent authentication. Access must later verify current exact command/org/app authority before context/observation and observe before write/retry locks; this item enables no command execution, freshness token, HTTP API or admission.

Extend exact Identity history/catalog/reference verification through19 while preserving1–18 sources/references. Generate the new pinned reference through existing tests/qualify_identity_baseline.py known-source rollback-only recorder, never hand-edit generated JSON or approve an arbitrary target. Access foreign-definer whitelist may add only this exact verified function/owner/ACL identity; Access stays at8. Existing current/target reads and all command/data/receipt behavior remain. Unknown state refuses without repair; migration failure blocks activation and recovery is forward controlled upgrade, never automatic reverse/startup migration.

Preserve all concurrent files, historical data/receipts/resources, dependencies (TS7.0.2) and accepted ADRs. No real organization/account/access changes, infrastructure/deployment/pilot, grants/consumers, Leave/editor, reset/prune, push or generic generator. Synthetic verification and scoped local commit only.

## I/O & Edge-Case Matrix

| Given / when | Then |
| --- | --- |
| Valid setup and active exact org, including zero members/accounts | One exact UUID row only, no side effects |
| Other/missing/retired org; null/nil arg; invalid/mixed/user context | No row, safe refusal without scope fallback/cast errors |
| Reused connection after SET LOCAL transaction | Previous context does not leak; context remains a trusted assertion |
| Ordinary/runtime/browser/setup-target/operator call, raw reads, owner assumption | No new privilege; only staged command owner may call point check |
| Clean/history18 with populated identities / upgrade19 and repeat | Exact19, all old rows/history/attribution/receipts preserved; Access8 compatible |
| Function/owner/ACL/search_path/RLS/history drift or unlisted default function grantee | Refuse drift; new routine strips inherited grants without changing defaults |
| Held owner/DDL lock or injected failure / explicit retry | Bounded rollback, no partial routine/history; controlled recovery passes |

</frozen-after-approval>

## Code Map

Under services/access:
- New identity-migrations/versions/0019_organization_target.py; reuse0007 target role/context/RLS. Do not edit old revisions or policies.
- identity-migrations/identity_baseline.py: new history/kind/trusted reference, keeping18 behavior. Existing account_actor_catalog_snapshot supports full new fingerprints.
- tests/qualify_identity_baseline.py: append --record-organization-target-reference through existing known-source recorder, rollback clean source rehearsal1–19 with old catalog checks. New organization-target-reference.json is generated, not hand-edited. Capture routine definition hash for exact Access compatibility pin.
- migrations/access_baseline.py: add only exact new foreign routine identity to existing whitelist; no Access migration or privileges.
- New tests/qualify_identity_organization_target.py and test_identity_organization_target.py: reuse current fixture/engine/controlled migration/snapshot/custody helpers. Verify structural additions, actual context/role behavior, preserved upgrade/repeat and rollback.
- New ORGANIZATION_TARGET_VERIFICATION_EVIDENCE.md; mutable owner contracts/DEVELOPMENT/KDG handoffs: five impacts and traceability. No generated schema/client needed.

## Tasks & Acceptance

- [x] Characterize old projections, observe focused RED then implement routine/exact history; root already observed missing function on actual Identity18 before edits.
- [x] Extend existing reference recorder and generate/pin19 from trusted clean rollback fixture; preserve all old generated bytes.
- [x] Execute every matrix row via focused/native tests, actual restricted roles and previous18 source compatibility; source-bound --all and separate read-only --verify-retained, optimized Python refused before I/O.
- [x] Record exact results/custody and scaffold/UI/context/docs/ADR impacts; root final review/regression/commit.

Given verified private organization lookup, when configuration execution is attempted, then existing Access adapter/CLI/workers still refuse before effects. This is a private verification prerequisite only.

## Implementation Notes

No product intent gap. Standing approval covers dirty-tree continuation. Preservation: /tmp/org-target-preservation.json. Private reference/preparation frame: platform/deployment/.local/identity-baseline/organization-target-20261021/. Native run99b7231c-0a5b-4bdb-98e8-3329564c526a is up; root-acceptance-red.log records absent routine on18. Root owns actual bootstrap/reference recording, pin finalization and fresh reviewed qualification. Agent may adapt private bootstrap code from existing fixtures but executes no DB/Docker/resource operations, nested workflow/agents or commit. Return ready-for-reference with exact next commands, then freeze final sources after root supplies recorded identities. Bootstrap portability stays deferred. Root will prepare a separate final source-bound frame after pinning.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 runtime SELECT denial | medium / patch | Immutable bridge grants scoped org SELECT to access_runtime; current qualifier incorrectly expects42501. Preserve scoped read and test forbidden operations separately. |
| Blind2 require nonexistent target login fixtures | false / reject | Existing target/setup reader roles are NOLOGIN, actual access_runtime/identity_operator logins and explicit controlled role observations are distinguished. Requiring invented credentials would add unauthorized role provisioning. |
| Blind3 missing/other active org matrix | medium / patch | OTHER is retired, so missing and different-active cases are not independently established. Add both fixtures. |
| Blind4 absent account success | medium / patch | Empty account is covered but genuine absent setting is not; use a fresh connection and assert absent before call. |
| Blind5 external consumer preservation | medium / patch | row_fixtures creates finance/cs rows and FKs, but data_state snapshots only Identity. Capture external_state across upgrade/repeat/retained. |
| Blind6 deployment source custody | medium / patch | fixture imports dev/native_cli but these executed validators are not bound. Add concrete consumed helper/bootstrap inputs to source snapshot. |
| Blind7 controlled-route injected failure | medium / patch | Raw SQL+manual rollback does not exercise Alembic ledger advancement rollback. Reuse existing subprocess postcondition injection pattern, verify unchanged history/routine/data then forward recovery. |
| Blind8 controlled drift refusal | medium / patch | Direct catalog checks cover drift, but do not observe actual controlled command refusing without repair. Add controlled drift invocation with before/after catalog/data proof. |
| Blind9 completion evidence pending | low / patch (root) | Review snapshot contains intentional pending root verification. Replace with exact final commands/results/custody before completion. |
| Edge1 runtime SELECT denial | medium / patch | Same verified grant as Blind1; no new prohibition may replace the existing scoped read contract. |
| Gap review | no findings | Independent verification-gap reviewer returned no findings. |
| Root controlled-role observation | medium / patch | NOLOGIN denial catch spans SET ROLE, so failed assumption could be mistaken for failed point call. Assert selected current_user before the separately caught call, using existing administrator credentials. |
| Root drift owner assumption | medium / patch | Actual42501 at drift mutation: migrator must explicitly assume existing NOINHERIT projection owner to alter its routine. Restore restricted identity before checking; no privilege added. |
| Root no-op RLS mutation | medium / patch | Actual existing org flags are(true,false); NO FORCE is a no-op. DISABLE RLS changes the real protected flag and proves refusal. Preserve historical flags/policies. |

## Verification

P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python. PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 P -I -B -m pytest -p no:cacheprovider: focused RED/GREEN, then root services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q. Both tools/py/run_compose_supabase.py --check-only modes (default; --identity-authority owned --no-seeds). Root existing reference recorder, fresh --all and separate --verify-retained; known previous18 sources from baseline commit. Frozen/protected/prior-proof/scoped whitespace audit. No repository-wide lint/typecheck claim.

Root pre-review regression:1325 passed/1 failed (46.57s); old membership-join test pins18 as latest. Preserve its historical18 behavior without require_head; add explicit current19 head coverage in the new owner suite. Root first native frame clean upgrade passed, then synthetic auth.users INSERT refused42501 because table created as supabase_admin instead of existing postgres fixture owner. Correct only private fresh bootstrap ownership; failed frame preserved.

Existing-fact correction: frozen intent's reference to existing forced/restrictive org
policies must be read as preserving the actual existing RLS contract. Native catalog
shows ENABLE RLS=true, FORCE RLS=false. The projection definer is distinct from the table
owner and remains subject to selected-org policies. This item adds no FORCE flag or
policy/grant change; source/reference and runtime intent remain unchanged. The drift
test now disables actual RLS under rollback rather than asserting refusal of a no-op.

Final root verification: fresh accepted frame15 native stages plus separate read-only
retained inspection passed;1338 affected tests passed57.52s; both composition dry runs
passed. All108 source/input hashes matched, with48 protected historical sources,82 prior
proof files and64 previous18 Git files preserved. Normal native stop passed after retrying
its script without unsupported -I import isolation; failed logs retained. All confirmed
review findings fixed; no new deferral. Five impacts and exact commands/results are in
services/access/ORGANIZATION_TARGET_VERIFICATION_EVIDENCE.md. Configure execution and
all downstream gates remain closed. Scoped local commit only; no push.

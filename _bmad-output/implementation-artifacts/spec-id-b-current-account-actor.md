---
title: 'ID-B restricted current-account actor projection'
type: 'feature'
created: '2026-10-20'
status: 'done'
baseline_commit: '814bf94362a38f2687c0dc732bffac3b405b188f'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/identity-access-execution-substrate.md'
  - '{project-root}/platform/docs/architecture/decisions/0018-transaction-scoped-tenant-context.md'
  - '{project-root}/platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md'
---

<frozen-after-approval reason="standing shared prerequisite implementation and isolated synthetic verification approval">

## Intent

The actor registry has no restricted consumer. Implement the selected internal
identity.current_account_actor() projection through the existing Identity owner,
so a verified account can resolve its stable actor without person/organization setup.
This is a read, never provisioning or application admission.

## Boundaries & Constraints

Return exactly account_id UUID, actor_id UUID nullable, display_name text nullable.
Use app.context_kind=user plus verified app.account_id. Actor/org context is not needed
to resolve an actor; never select an account from app.actor_id or actor equality.
Missing/malformed/nil account or wrong/missing context yields no row. Existing active
profile without mapping yields its account with null actor/label; no implicit ensure.
Only access_runtime gains exact routine execution. Use the dedicated NOLOGIN
identity_account_projection_owner, current-account profile RLS and narrow column reads;
runtime cannot assume it or raw-read actor tables. Fixed STABLE SECURITY DEFINER,
pg_catalog/pg_temp search path, qualified objects; no public/browser RPC or API change.
GUCs are verified-backend assertions, not authentication against compromised credentials.

Preserve prior migrations, references, source pins, rows/hooks/memberships and existing
Access/PtS behavior. Existing owner lock/dependencies/TS7 remain unchanged. Synthetic
role preparation/tests only; no live account/access/provider changes, deployment,
Leave/editor, operator commands, membership redesign or readiness promotion. Preserve
concurrent files, receipts/state and Docker resources. No new service/generator/runner.

## I/O & Edge-Case Matrix

| Scenario | Expected result |
| --- | --- |
| Active mapped profile | Current account and mapped account-kind actor/label, no person/org required |
| Active unmapped profile | Current account with null actor/label, no write |
| Missing/deleted profile or invalid context | No row, no data change |
| Account A plus spoofed actor/org context | A's result only; never B or a service actor |
| Runtime access | Exact projection works; raw actor/profile reads, writes, owner-role assumption and function replacement deny |
| Connection reuse | SET LOCAL context clears after transaction; next unconfigured transaction returns no row |
| Clean/adopt/old head/retry/failure | Guarded upgrade preserves prior state; unknown preparation/catalog/history refuses, partial migration rolls back |

</frozen-after-approval>

## Code Map

- `services/access/identity-migrations/versions/`: add revision3 after0002; preserve
  0001/0002 and both existing trusted fixtures byte for byte.
- `identity_baseline.py`, `env.py`: explicit known revision verification/final head;
  add separately pinned projection reference. Old catalog comparisons may normalize
  only the single new, independently validated staged ownership membership; never
  ignore arbitrary grants, role flags or raw catalog differences.
- `services/access/tools/`: add owner-specific controlled role preparation SQL because
  the migration login is NOCREATEROLE. New empty NOLOGIN reader, no dangerous flags,
  no inherited/unlisted authority; only migrator can assume it for function ownership.
  Runtime cannot assume it. Grant reader schema CREATE only transactionally for owner
  transfer, revoke before commit. No privileged bootstrap executed outside synthetic proof.
- Existing qualification helpers and previous-code Git validation: reuse for actual
  role/query tests and reference recording. `services/access/main.py` stays unchanged;
  its legacy app.actor_id still means Auth account, not this new actor resolution.

## Tasks & Acceptance

- [x] `versions/0003_current_account_actor.py`, `tools/prepare_identity_projection_role.sql`:
  exact role/policy/column/function grants. Verify prepared role attributes/memberships
  and staged empty authority before accepting old-state normalization. New-state
  verification includes reader flags/effective privileges/ownership. No runtime schema
  CREATE/role assumption; strip new routine default/PUBLIC/browser execution.
- [x] `identity_baseline.py`, `env.py`, owner qualification recorder: explicit revision3
  trusted fixture/final-head support, clean/legacy/0002 upgrade and rollback; original
  fixture digests unchanged. No approval/export bypass or another migration owner.
- [x] `services/access/tests/`: ATDD RED, focused TDD and actual restricted-login matrix,
  nullable/no-row distinction, cross-account and pooled reuse, effective ACL/defaults,
  malicious search_path, unsafe role preparation and failure preservation. Old consumer
  query/profile hook and existing composer/coordinator regression remain covered.
- [x] `services/access/IDENTITY-MIGRATIONS.md`, new projection evidence, mutable owner
  inventory and KDG navigation: exact commands/results/traceability and five impacts.

Given valid verified context, when the restricted login resolves the current account,
then it gets only that profile's authoritative nullable actor projection. Given unsafe
preparation or unknown state, when migration executes, then no partial activation occurs.

## Implementation Notes

No unresolved intent choice. Role ownership preparation is a controlled existing owner
concern, performed only in synthetic verification here. Root owns target preparation,
private credentials/reference recording/actual qualification/evidence/navigation/audit
and scoped local commit. Implementation agent owns migration/helper/env/role SQL/unit
tests/runbook; no DB/Docker actions, extra agents or commits from its task. Use canonical
locked Python at platform/deployment/.local/identity-baseline/qualification-im60qj1l/
owner-env-djguxc78/offline-venv/bin/python. Coordinate recorder/preparation interface
before root execution. Avoid generic role registries or framework machinery.

## Spec Change Log

## Review Triage Log

All three layers completed before triage. Edge: no findings. Verification-gap: no gaps.

| Finding | Verdict / route | Verified evidence and disposition |
| --- | --- | --- |
| B1 reader effective Auth table/column privileges absent | medium / patch | Auth namespace enables resolution; PUBLIC table/column ACL creates no reader dependency. Add effective Auth table/column categories to the new fixture only. |
| B2 head3 bypasses prior actor-reference validation | medium / patch | trusted_projection_reference checks only revision3/pins; no call validates immutable actor reference/revision2. Retain explicit old-reference validation. |
| B3 old integration repairs hooks/functions before previous upgrade | false / reject | The immutable LEGACY_INTEGRATION_SQL contains only GRANT statements, no hook/function definitions. row_fixtures intentionally revokes two legacy bridge grants to represent external FKs; replay restores the exact original bridge privileges. No hook/function is reinstalled or repaired. |
| B4 incomplete prior manifest/self-reported execution | medium / patch | The loop accepts empty/incomplete sha256 sets and does not compare command/log hashes. Require exact seven-file owner set, known launcher/command and actual execution-log digests before head verification. |
| B5 direct pin write can truncate/overwrite helper | medium / patch | New recorder calls module.write_text after read/check. Remove automatic helper mutation; emit the digest and require explicit source/pin reconciliation, preserving concurrent helper edits. |
| B6 DDL bytes may change while recording | medium / patch | Imports precede final file hashing. Execute captured revision bytes and verify their identity plus source pins before exclusive publication. |
| B7 rollback snapshot omits new reader/Auth authority | medium / patch | Inherited snapshot uses old categories only. Override this qualifier's snapshot to use projection_catalog_snapshot so failure proof covers new authority. |
| B8 reuse after rollback/statement failure untested | low / patch | Existing query helper commits successful reads; no failed-transaction reuse assertion. Add same-physical-connection rollback and statement-failure checks. |
| B9 PostgreSQL15/16 preparation branches unqualified | low / patch | Actual proof is PostgreSQL17 only. State that operational qualification is limited to17; other spellings are compatibility branches, not delivered version proof. |


Additional patch triage: medium / patch — Auth privilege categories included all
false rows and would bind the Identity reference to the five-column fixture rather
than native vendor schema. Keep only effective granted table/column privileges;
empty denied sets remain invariant under unrelated vendor schema additions.
No new DDL or public surface. Focused shape/grant tests pass.

## Verification

Affected owner tests plus existing composer/coordinator; actual synthetic PostgreSQL17
matrix and prior-source compatibility, independent rollback-only source reference,
original source/reference/lock and concurrent-file preservation, normal retained-data stop.
Scaffold remains owner-local/unpromoted. UI/context unchanged. Update owner docs/evidence;
existing0018/0020/0056 and selected substrate suffice, no accepted ADR edit/new decision.


Executed: actual acceptance RED missing routine SQLSTATE42883; initial ordering/Auth
namespace failures retained and corrected; fresh complete seven-case projection matrix
PASS, including actual restricted-login/Auth-table denial and legacy JWT spoof bound.
90 focused owner/composition/coordinator tests PASS; both composer check-only commands PASS.
Exact commands, requirement matrix, private frame locations and impact decisions are in
[projection evidence](../../services/access/CURRENT_ACCOUNT_ACTOR_EVIDENCE.md).


Reviewed completion: all three layers complete, eight patch groups and one refuted
blind finding, plus the Auth denied-shape correction; no deferrals. Final generated
reference explicitly reconciled and pinned; all four upgraded targets pass final
postconditions. Actual rolled-back PUBLIC Auth table/column grants refuse, native271
vs scratch5 Auth columns leave denied categories equal. Final90 tests and both composer
checks pass. Normal Supabase CLI stop succeeds; database volume/bridge/config retained.

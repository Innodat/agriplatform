---
title: 'ID-B additive durable actor persistence foundation'
type: 'feature'
created: '2026-10-20'
status: 'done'
baseline_commit: 'e4723c5ca371df01779af3964d306d0fcd38bc0c'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/identity-access-execution-substrate.md'
  - '{project-root}/platform/docs/architecture/decisions/0056-durable-actor-registry-separate-from-login-accounts.md'
  - '{project-root}/platform/docs/architecture/decisions/0025-record-attribution-and-audit-provenance.md'
  - '{project-root}/platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md'
---

<frozen-after-approval reason="standing shared prerequisite implementation and synthetic verification approval">

## Intent

Identity needs durable attribution independent of Auth accounts before KDG can consume
stable account actors. Add the selected actor/account mapping persistence through the
existing Identity migration owner. This bounded delivery establishes structure and
restricted privileges; it does not activate actor provisioning or authorization.

## Boundaries & Constraints

Follow the substrate's exact actor/account_actor shapes and ADR0056. Preserve ID-A's
original pinned source/reference, existing rows, Auth hooks, memberships and cross-owner
references. New objects must not inherit broad legacy defaults. No Auth/person/employment
FK or synthetic organization. No new runtime service, generator or release runner.
Use the existing exact Python/uv/SQLAlchemy/Alembic/Psycopg/pytest owner lock; TS7 unchanged.
Only isolated synthetic local/CI mutations are authorized. Preserve concurrent files,
receipts/state and Docker resources. No real accounts/grants, live adoption, deployment,
Leave/editor, membership redesign, runtime projections, operator/outcome commands or
implicit actor seeds. Explicit classification/account verification belongs to later
controlled provisioning; schema fixtures are not authority to adopt a real identity.

## I/O & Edge-Case Matrix

| Scenario | Expected result |
| --- | --- |
| Clean or equivalent legacy target | Existing guarded route creates both histories in order, retains source equivalence and old behavior |
| Existing owned identity_0001 | Additive upgrade preserves all legacy rows/references; repeated current-head upgrade unchanged |
| Unknown revision/catalog or migration failure | Refuse/roll back; no activation or destructive downgrade |
| Explicit synthetic system/service actor | No Auth/person/org record required; self-attributed bootstrap permitted |
| Account mapping | One immutable stable account-to-account-kind actor mapping; service-kind/conflict/nil/invalid data rejected |
| Mutation or deletion | Stable identity/kind/assigned key and creation attribution cannot change; mapping cannot update/delete; actor deletion cannot erase history |
| Ordinary browser/runtime roles | No raw new-table/sequence/function authority, including inherited PUBLIC/default grants |

</frozen-after-approval>

## Code Map

- `services/access/identity-migrations/versions/0001_baseline.py`, original
  `reference.json`, `source-pins.json`: preserve bytes and ownership; no source replay
  on adopted targets. Add `versions/0002_actor_registry.py` in the same chain.
- `identity_baseline.py`, `env.py`: currently exact revision1/catalog only. Extend
  trusted verification for known revision1 and revision2; keep private ledger checks,
  actual login/role/mutual exclusion and final head/catalog check inside transaction.
  Keep original baseline fixture intact; add fixed pinned `actor-reference.json`.
- `services/access/tests/qualify_identity_baseline.py`: reuse private fixture URL
  validation, source execution, migration commands and preservation snapshots; add
  owner-specific actor qualification/reference recording without a migration bypass.
- `services/access/identity-migrations/uv.lock`: already qualified exact owner baseline;
  no dependency change. Existing composer/coordinator remain the only delivery route.

## Tasks & Acceptance

- [x] `versions/0002_actor_registry.py`: exact tables, nonnil UUIDs, bounded nonblank
  names/ASCII keys, unique mapping/account-kind FK, RESTRICT actor attribution;
  structural immutability/retention and server UTC attribution timestamps. Defaults
  support explicit owner-only fixture attribution, not caller-selected runtime actors.
  Keep creation actor/time immutable, update time server-maintained on allowed label
  changes; assigned key may transition null to one key once. No seeded business rows.
- [x] `identity_baseline.py`, `env.py`: recognize only exact known revision states;
  old head uses original trusted owned reference, new head uses additional fixed
  fixture. Preserve clean/adopt chaining, forbidden stamp/downgrade and rollback.
- [x] `services/access/tests/`: observe relevant acceptance RED first; focused TDD;
  actual restricted-owner migration/DDL/ACL and nonowner denial tests for every matrix
  row. Characterize previous consumers before adjusting verification. Prove legacy
  rows/history/Auth profile behavior unchanged and neither mapping nor actor creates
  authority. Root records source/lock/reference identities and exact commands/results.
- [x] `services/access/IDENTITY-MIGRATIONS.md`, new `ACTOR_FOUNDATION_EVIDENCE.md`,
  KDG next-session/shared-prerequisites and mutable ownership inventory: record scope,
  outcomes and scaffold/UI/context/documentation/ADR impacts; accepted ADRs unchanged.

Given the selected synthetic ID-A profile, when upgraded through the existing owner
route, then durable actor structures exist without requiring account/person/employment
or changing the previous supported consumers. Given invalid mappings, unauthorized
roles or unexplained catalog/history, when attempted, then constraints or guarded
migration refuse without partial change.

## Implementation Notes

No unresolved intent choice; additive owner DDL has no live irreversible action under
this approval. Implementation agent owns migration/verification helper/env/unit tests
and runbook. Root owns actual synthetic target preparation, additional reference
recording/qualification, evidence/navigation, preservation audit and scoped local commit.
Do not start Docker, touch a DB, modify original generated references, add agents or
commit from the implementation task. Coordinate required reference interfaces with root.
No operator/HTTP surface is exposed; runtime attribution derivation remains a later
consumer gate. Schema-only deployment uses existing operational release evidence.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 Unicode blank labels | low / patch | C locale class accepts NBSP/EM SPACE. A direct CHECK correction using a fixed Unicode White_Space set preserves nonblank semantics without a new API/helper. |
| Blind2 previous-source self-trust | medium / patch | The committed proof trusts its private manifest instead of checking historical Git bytes. Root originally copied exact git show bytes, but reproducible runner must verify those objects and own the launcher. |
| Blind3 interrupted fixture publication | low / patch | Safe refusal already prevents migration with no matching pin, but recovery is undocumented. Document preservation/independent regeneration after developer interruption; no automatic target approval or new recovery engine. |
| Blind4 temporary-file custody | medium / patch | Existing temporary causes open(xb) failure, then finally unlinks another invocation's file. Track whether this invocation created it; regression must leave foreign bytes intact. |
| Blind5 full committed execution | medium / patch | Required logic is already in committed runner, but only a continued execution followed the diagnostic correction. Run the entire corrected committed runner on new fixtures and record it, retaining earlier frames. |
| Blind6 concurrent mapping conflict | medium / patch | Only sequential conflicts are covered; DB uniqueness needs actual two-connection conflict/locking proof under structural integrity policy. Add bounded winner/loser preservation case. |
| Blind7 insertion/no-op attribution | medium / patch | Current valid writes cannot distinguish overrides/no-op preservation from defaults. Add conflicting metadata and no-op behavioral assertions. |
| Blind8 missing attribution actor FK | medium / patch | Existing tests never reference a nonexistent creator/updater; add failed actor/map creation and allowed-field update with absent actor and verify unchanged rows. |
| Blind9 valid/Unicode/key boundaries | low / patch | Existing oversized ASCII negative misses valid boundary and Unicode semantics. Add direct success/failure cases for 200 code points/128 ASCII key, multibyte labels, duplicate/non-ASCII keys. |
| Edge1 Unicode blank labels | low / patch | Same demonstrated C-class mismatch as Blind1; fixed set and actual examples settle it. |
| Edge2 temporary-file custody | medium / patch | Same demonstrated unconditional finally unlink as Blind4. |
| Gap1 attribution outcomes | medium / patch | Filed regression evidence establishes omitted insert override/no-op behavior; add actual owner row assertions. |

Group only shared causes: Blind1/Edge1, Blind4/Edge2 and Blind7/Gap1.
All survivors have direct internal corrections/test additions without public surface;
no intent gap, spec loopback or deferred implementation. Root executes the complete
fresh qualification and records final provenance after patches.

All nine review patch groups are completed. Fresh full committed qualification passes,
including real mapping contention and attribution/Unicode boundary tests. Final40
owner/release tests and both composer checks pass; no implementation deferred. Original
reference/revision/source pins/lock and2550 unrelated pre-existing files are unchanged.
Evidence and retained normal-stop/source audit close this bounded persistence item.

## Verification

Use the existing fresh locked owner interpreter. Run affected owner tests and existing
composer/coordinator regression; actual clean/adopt/previous-head upgrade and scoped
nonowner denials on synthetic PostgreSQL17. Verify original fixture/source bytes and
legacy snapshots. Scaffold recipe unpromoted; no UI or context change; update owner
runbook/evidence/navigation. Existing ADR0020/0025/0056 suffice; no new ADR decision.

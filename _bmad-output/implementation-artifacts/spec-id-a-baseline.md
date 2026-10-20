---
title: 'ID-A verified Identity baseline and source handover'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
baseline_commit: 'd0c543dddabb7aa9537d097a2335149fc8ddd1e9'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/identity-migration-ownership-inventory.md'
  - '{project-root}/platform/docs/architecture/contracts/identity-access-execution-substrate.md'
  - '{project-root}/platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md'
---

<frozen-after-approval reason="standing bounded foundation and isolated synthetic verification approval">

## Intent

Identity has no owned executable migration history, so current Access foundations
cannot safely depend on it. Establish its separate baseline, verified equivalent
adoption and explicit source handover through existing composition/release tooling.
This is the first bounded ID-A delivery, preserving legacy behavior and references.

## Boundaries & Constraints

Keep Identity under its existing Access maintainer: identity-migrations,
identity-alembic.ini, identity.alembic_version, identity_migrator and
IDENTITY_MIGRATION_DATABASE_URL. Never put Identity objects in Access's history.
Use pinned Python3.15/uv0.13.1, SQLAlchemy2.1.4, Alembic1.20.0, Psycopg3.3.6,
pytest9.1.1; app TS7.0.2 unchanged. Reuse source SQL and existing tools, no new
runtime service, generator, release runner or vendor interception prerequisites.

Only explicitly synthetic local/CI databases may be mutated in verification.
No production/real-account/grant/provider changes, deployment, Leave/editor or data
migration. Preserve source/history/concurrent files, receipts and Docker resources.
Legacy broad grants/helper behavior must be characterized, never silently hardened
while claiming equivalence. Actor registry, membership redesign and Access v2 remain
ID-B/ACCESS work; no readiness promotion or startup migrations/destructive downgrade.

## I/O & Edge-Case Matrix

| State/action | Required result |
| --- | --- |
| Clean synthetic target | Restricted actual Identity migration login establishes one baseline and bridge; repeat is unchanged |
| Equivalent legacy schema/adopt | Compare against trusted clean-source catalog before stamping; preserve rows, external references and original applied history |
| Unknown schema/ACL/trigger/owner/default/history | Refuse adoption without persistent changes; never self-approve from the target |
| Composition | Explicit owned mode excludes six Identity DDL sources, keeps CS/other owners; legacy default unchanged; never both histories |
| Coordinated release | Explicit Identity route runs before Access; failed Identity blocks later owners and activation; no reverse migration |
| Runtime compatibility | Actual scoped Access reads and supported Auth hook/profile creation work; foreign organization/privileged writes denied |

</frozen-after-approval>

## Code Map

- `services/access/migrations/`, `alembic.ini`: existing Access-only history stays intact.
- Six Identity SQL sources listed in ownership inventory plus
  `services/access/tools/identity_bridge.sql`: reuse pinned historical definitions;
  include public.get_user_roles and auth.users trigger. Bridge becomes owned migration
  integration in the new route; retain its old source. Handle explicit source transaction
  wrappers without breaking Alembic atomicity. No application DDL is transferred.
- `tools/py/run_compose_supabase.py`: existing discovery/manifest; add explicit
  identity authority selection, default legacy. Never edit composed generated files.
- `tools/py/deploy_pts.py`: existing lock, before/after evidence, failure stopping.
  Add opt-in Identity config/order while retaining default PtS route and tests.
- `apps/pts/tests/test_release.py`: regression and Identity-order/failure evidence.
- `platform/deployment/DEVELOPMENT.md`: existing native disposable Supabase lifecycle,
  private credentials and normal stop. Root owns actual target preparation/verification.

## Tasks & Acceptance

- [x] `services/access/identity-alembic.ini`, `identity-migrations/`: separate baseline,
  owner-local migration pyproject, source pins, safe errors, mutual exclusion and
  read-only catalog verification/adoption. Compare columns/defaults/types, constraints,
  indexes/sequences, RLS, functions/triggers including external hooks, owners, effective
  ACL/default privileges and baseline permission seeds. Ignore only qualified volatile
  identities. Trust a reference derived from known clean sources, never an arbitrary
  target-supplied approval. Guard supported bare stamp/upgrade paths on unknown schema.
- [x] `services/access/tests/`: ATDD RED then focused unit/actual PostgreSQL tests for
  every matrix row, mismatch preservation, no-op/retry and prohibited downgrade.
- [x] Composer and coordinator plus affected tests: explicit source handover/order,
  preserve legacy route, partial failure evidence and activation false.
- [x] Owner runbook/evidence and mutable shared/KDG navigation: exact commands,
  requirement-to-test traceability, actual restricted-role/Auth proof, compatibility
  limits and five impacts. Existing accepted ADRs unchanged.

Given either supported clean or equivalent legacy synthetic setup, when the controlled
Identity route executes, then one owned baseline supports existing dependencies.
Given any unexplained difference or failure, it refuses without adoption or activation.

## Implementation Notes

Executed clean/adopt/mismatch/runtime/Auth profile+hook matrix on native PG17 with
actual owner/runtime/Auth-role logins. Existing ledger/rows/finance+CS FKs survive;
concurrent lock and actual coordinator failure block activation. Native email provider
is disabled, so password sign-in is not qualified and remains a later Auth gate.
Legacy privileged self-update is characterized under RLS and rolled back, not hardened.
Removed only the redundant pinned schema-create statement from transformed legacy SQL;
actual owner schema authority stays narrow. Owned integration adds USAGE, REFERENCES(id) and exact retained seed column
privileges for postgres legacy bootstrap, without DELETE/Auth INSERT/owner membership. Compact category fingerprints replace
full catalog duplication. Initial failed receipts and reference anomaly are preserved;
independent recapture matched its exact prior digest before regeneration.

No unresolved intent choice. SQL/role changes occur only inside isolated synthetic
verification. Implementation agent owns Identity code/tests/runbook, composer/coordinator
and their tests. Root owns spec, evidence/navigation, canonical owner lock, synthetic
Supabase preparation, private credentials, actual qualification/reference recording,
review and scoped local commit. Coordinate actual DB interfaces with root; do not
start Docker or mutate a target independently. No additional agents or commits.
Use existing selected Python baseline venv for initial focused tests; final proof uses
a fresh owner lock/environment. Production's documented PUBLIC role-helper revocation
is a possible mismatch to refuse, never authority to replay older grants.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 retained seed DML | medium / patch | Retained 001_identity updates users and inserts org/member/roles as postgres; current grant covers only FKs. Extend the fixed compatibility grant only to its existing required tables/operations and execute the synthetic seed. |
| Blind2 clean role/catalog verification | high / patch | Clean path checks only migrator flags; access_runtime BYPASSRLS or memberships escape until retry. Verify the completed owned catalog before transaction commit. |
| Blind3 ledger column ACL | high / patch | Table REVOKE does not revoke column UPDATE(version_num); ledger inspection omits attacl. Reject extra column ACLs. |
| Blind4 rewrite rules | low / reject | Catalog can miss a separately added rewrite rule, but this requires owner/admin DDL outside this controlled baseline; uncommon here and adding another catalog verifier exceeds a direct correction. No arbitrary-database-equivalence claim. |
| Blind5 sequence OWNED BY | false / reject | All three source sequences are GENERATED identity dependencies. PostgreSQL forbids changing OWNED BY of an identity sequence; the described ordinary ALTER cannot remove them. |
| Blind6 concurrent uncoordinated DDL | low / reject | Advisory lock coordinates migration runners only, as documented. Privileged concurrent catalog edits outside ADR0020 controlled release are operational misuse; adding global lock machinery is unnecessary. Clarify the existing coordination requirement in the runbook. |
| Blind7 legacy history on owned retry | medium / patch | Owned branch returns before verify_legacy_history; unknown newly recorded Identity versions escape. Reuse the same read-only guard on retries. |
| Blind8 no-migrations authority | medium / patch | main skips validate_identity_output when no-migrations retains old generated files. Validate retained files on this flag combination before manifest writes. |
| Blind9 injected mid-write rollback proof | medium / patch | Existing failures occur at preflight or first source. Add controlled owner-login migration failure after writes and compare catalog/data/ledger. |
| Blind10 populated Auth claims | medium / patch | Native qualification exercises only empty claims; add synthetic active/inactive member/role cases through actual Auth role, retaining only isolated synthetic fixtures. |
| Edge1 clean elevated runtime | high / patch | Same confirmed missing post-migration catalog guard as Blind2; its transaction must roll back. |
| Edge2 upgrade base empty ledger | medium / patch | upgrade base can create an empty ledger on clean state. Require the known completed head/private ledger before commit. |
| Edge3 no-migrations authority | medium / patch | Same flag path as Blind8; retained files can contradict manifest. |
| Gap1 original legacy ledger refusal tests | medium / patch | Filed regression evidence shows only valid original ledger and independently unknown owned ledger coverage. Add partial/misnamed/unknown original-ledger and conflicting-clean cases with preservation checks. |

Survivors group only by shared cause: Blind2/Edge1 (missing postflight),
Blind8/Edge3 (retained composition output); all others remain distinct patches.
No intent/spec loopback or deferred implementation is required. Existing coordination
and identity-sequence semantics settle the rejected claims without new machinery.

Review patches completed: postflight/column ledger/legacy retry/composition guards,
exact synthetic seed column grants, actual rollback/history/runtime-role/populated-hook
regressions. Final 23 owner/release tests and both composer checks pass. Actual matrix
and final source/preservation/stop reports are linked in owner evidence. One historical
focused-check log/receipt was overwritten by its runner; observation retained, no
claim of full receipt-byte preservation. No deferred implementation.

## Verification

Affected owner pytest, composer check-only/characterization and PtS release regression.
Fresh pinned owner install plus actual native PG/Auth clean/adopt/mismatch/scoped-role
proof, retaining source/tool/lock/result hashes and normal stopped environment.
Scaffold: owner migration recipe remains unpromoted. UI: none. Context: existing rules
suffice. Docs: owner runbook/contracts/handoff. ADR:0016/0017/0020 and Identity decisions.

# Grant registry compatibility bridge

Access0011 permits registered organization capabilities while retaining exactly
`pts.poetry.read`, `pts.poetry.export` and `pts.poetry.documents` without registry
entries. Their generated nullable `registry_permission` is NULL; every other value
is its literal permission. A local composite RESTRICT FK enforces registered
organization scope, including revoked rows. Nonlegacy active rows require membership,
creation/update actors and update time; existing positive, nonnil and finite checks
remain. Revoked rows may retain unknown provenance. External IDs are not verified.

This discriminator is temporary compatibility scaffolding. Removing it and installing
final direct-FK/global active-row integrity requires coordinated legacy adoption.
Future protected assignment must exclude the three legacy PtS permissions while v1
readers ignore membership and revocation. `grant.assign` remains unsupported; storage
success proves neither current target validity nor authority nor effective access.
Reader activation and coordinated PtS/KDG adoption remain independently gated.

Controlled release uses the existing isolated owner route: explicitly configure the
protected `ACCESS_MIGRATION_DATABASE_URL`, then run the prepared owner's Python with
`-I -B -m alembic -c services/access/alembic.ini upgrade head`. Never put credentials
in command arguments or logs. There is no startup migration or automatic downgrade.
Preflight accepts only exact clean/1–11 catalogs, checks histories/RLS/ACLs, generated
expression and FK triggers; unknown state refuses without normalization. Identity19's
mutable helper selects10/11 from schema-resolved column metadata and verifies the
whole Access catalog, without Access business/history reads or new privileges.

The migration replaces one CHECK and adds one STORED generated column, one FK and
one CHECK. It performs no business-value DML, backfill or registry adoption. Adding
the STORED column can physically rewrite the table and hold locks. The existing
3-second lock timeout, 30-second statement timeout, bounded transaction settings and
owner advisory lock remain unchanged. Synthetic acceptance does not size a production
table rewrite. A real release requires explicit coordinated sizing/recovery evidence.
On failure, keep activation blocked; preserve source/log/history/data evidence,
inspect the transaction outcome, resolve contention or drift explicitly, and retry
forward through the same controlled route. Never reverse applied migrations or
normalize unexpected state automatically.

For separately authorized disposable native qualification, root prepares Identity19,
the verified service actor, protected runtime secret, five database cases
`clean/upgrade/drift/failure/locks` and the existing four credential groups. No new
fixture framework, previous-source package or runtime lifecycle is introduced.
Bootstrap custody binds consumed native configuration, driver/bootstrap/Auth inputs,
owner/client/helper sources and runtime secret; generated credentials/run inputs are
bound separately by hashes. Keep these private and never publish their values.

The retained private bootstrap also requires these existing inputs beneath
`platform/deployment/.local/identity-baseline/`:
`access-registry-reviewed-20261021/credentials.json` and
`org-storage-reviewed-20261021/credentials.json` plus its `run.json`. The latter's
`run_id` selects `platform/deployment/.local/kdg/<run_id>/supabase/config.toml`.
All are source-custody inputs. The prepared proof additionally supplies
`bootstrap*.py`, `root_qualification_driver.py`, `auth-helper-definitions.json` and
protected `runtime-credential.json`. This qualification depends on that retained
private native bootstrap and its existing credentials/configuration; it provides no
portable bootstrap or new fixture framework.

Run the prepared owner Python with `-I -B services/access/tests/qualify_grant_registry_bridge.py
--all`, with private `ACCESS_QUALIFICATION_DIR` in the environment. The aggregate is
single-use. A distinct `--verify-retained` invocation checks frozen source/bootstrap/log
custody, including the result-bound retained-state SHA256, before database inspection
and verifies exact11 in read-only transactions.
Retained results preserve original values and all five command receipts across10→11,
legacy owner writes, registry/active-field constraints, whole transaction refusals,
actual restricted runtime/operator/command-owner boundaries, drift refusals and
bounded failure/lock recovery. Normal native stop and independent evidence inspection
remain root responsibilities. Never reuse or prune historical frames.

Requirement traceability: focused tests cover exact versions, local DDL, metadata-only
selection, synthetic custody inputs, retained-state mutation refusal before database
inspection and exact safe lock-reason classification. Native `functional` proves all
three legacy permissions, permission UPDATE discriminator recomputation, each individually
missing revoked provenance field and unrevocation refusal, registered organization2
runtime fixtures, and complete-provenance dependent-CTE named-FK refusal with statement
and prefix rollback. `upgrade` proves original values/client receipts; `privileges`
proves actual restricted roles and exact organization row sets including nonlegacy
organization2 data. `drift` proves child and referenced-side FK trigger refusal,
still-STORED altered exemptions through both owner verification and actual restricted
Identity19, explicit fixture restoration, and other catalog/history/ACL refusals.
`failure_and_locks` requires the exact safe advisory-busy code or relation-lock55P03,
then proves rollback/forward retry. Its child logs contain only selected fixed code,
SQLSTATE and class; production migration sanitization and runtime busy rules are unchanged.
The still-STORED drift fixture uses pinned native18 test-only SET EXPRESSION syntax;
production0011 does not. Restoring that generated expression legitimately rebuilds
PostgreSQL internal FK trigger names. Diagnostic snapshots canonicalize only the numeric
suffix of internal `RI_ConstraintTrigger_a/c` names and the matching declaration name
inside their trigger definition, retaining every semantic field, full definition, user
trigger name and row count; rows are sorted for comparison. This is a representation
choice, with no database repair or normalization. The separate exact baseline verifier
still pins FK association, function, scope and state on both ends. Focused checks prove
name-only rebuild equality and continued inequality for disabled triggers, changed
function/event/definition and renamed user triggers. `retained` proves separate
read-only exact-head checks.

Five impacts: extend the existing owner migration/catalog scaffold and synthetic
fixtures; shared UI has no impact; agent context needs no change; owner evidence and
mutable substrate/development/KDG handoffs document the bounded result; existing ADRs
suffice without edits. No dependencies, generator, application/runtime service, actual
account/access/deployment/pilot or Leave implementation is introduced. Root records
actual commands/results, reviews, regression/composition, normal stop and local commit.

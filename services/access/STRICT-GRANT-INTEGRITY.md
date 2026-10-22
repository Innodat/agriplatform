# Strict organization grant integrity

Access0012 replaces Access0011's temporary generated `registry_permission` bridge
with validated `grants_permission_scope_fkey` on `(permission, scope_kind)` to
`access.permissions(permission, scope_kind) ON DELETE RESTRICT`. Every active row
requires membership, creation actor, update actor and update time through
`grants_active_fields`. Revoked rows may preserve partial unknown provenance, but
still require a registered organization permission. All three legacy PtS literals
follow these same rules. Existing positive/nonnil/finite constraints, original columns,
opaque IDs, values, keys, RLS and ACLs remain. No writer receives new privileges.

The migration performs local DDL only. Incompatible populated11 data refuses atomically
and remains exactly11, including history, catalog and original values. It neither
registers permissions nor adopts/backfills/deletes rows or reinterprets organization
grants as account grants. ADR-0052 permits removing unused legacy PtS compatibility;
this storage change does not complete the coordinated PtS/account/Content transition.
Protected `grant.assign` remains unsupported and effective readers remain later work.
Existing denial remains in force until coordinated replacement activation.

Use the existing controlled release route with the privately configured
`ACCESS_MIGRATION_DATABASE_URL` and prepared owner Python:
`-I -B -m alembic -c services/access/alembic.ini upgrade head`. Never place credentials
in arguments/logs. Preflight accepts exact clean/1–12, validates original histories,
full catalog/RLS/ACLs and all four FK enforcement triggers on both ends. Only11 has
the generated bridge. Twelve requires the exact native dropped `pg_attribute` slot14
left by DROP COLUMN; arbitrary dropped columns or altered tombstones refuse.
Identity19 selects12 through schema-resolved direct FK metadata before the generated11
marker, then verifies the entire catalog without Access business/history reads.
Registration metadata remains10 for both11 and12. Historical migrations/references
remain unchanged.

The dropped-slot check assumes the measured native pinned PostgreSQL image/catalog,
including default-collation OID100 and the exact slot14 tombstone metadata. A full
logical schema dump/recreate omits dropped slots and is not currently qualified or
accepted by this verifier. Recovery tested here is transaction rollback followed by
explicit controlled forward retry. No backup/restore success is claimed. Never
manually edit pg_attribute to make restored metadata pass; no new recovery tooling
or logical-restore acceptance is supplied by this delivery.

DDL acquires table locks and validates retained rows. Existing owner advisory locking,
3-second lock timeout, 30-second statement timeout and bounded transaction settings
remain. Native synthetic evidence does not size a live release. Activation stays
blocked after any failure; retain source/log/history/data evidence, establish actual
transaction outcome, resolve contention or incompatible state explicitly and retry
forward through the controlled route. No startup migration, automatic repair or
downgrade is provided. Incompatible releases require planned maintenance/recovery.

For authorized isolated native qualification root prepares the six fresh private
cases `clean/upgrade/refusal/drift/failure/locks` in the retained native run, with
Identity19, verified service actor, protected runtime credential and existing four
credential groups. Refusal intentionally remains11; other cases finish12. Preserve
all previous frames and Docker resources. Root bootstrap consumes the existing
`access-registry-reviewed-20261021/credentials.json` and
`org-storage-reviewed-20261021/{credentials.json,run.json}` beneath
`platform/deployment/.local/identity-baseline/`; the latter run selects the retained
`platform/deployment/.local/kdg/<run_id>/supabase/config.toml`. This preparation
depends on retained private credentials/configuration and is not portable CI.

The fresh proof supplies `bootstrap*.py`, `root_qualification_driver.py`,
`auth-helper-definitions.json`, `runtime-credential.json`, actor evidence and generated
`credentials.json`/`run.json`. Source custody binds all consumed owner/client/helper
sources, bootstrap/driver/Auth/runtime/config inputs and this runbook/test. Bootstrap
witness separately binds generated inputs and logs. With private
`ACCESS_QUALIFICATION_DIR`, run the prepared owner Python with
`-I -B services/access/tests/qualify_strict_grant_integrity.py --all` once, followed by
a distinct `--verify-retained`. Frozen source, generated-input, owned-log and retained
state digests are checked before database inspection. Diagnostic snapshots reuse
storage.Qualification and normalize only PostgreSQL internal RI trigger numeric name
suffixes, preserving definitions, flags, row counts and user names. Root performs
independent evidence inspection and normal native stop; no second runtime lifecycle.

Requirement traceability: `functional` tests named direct-FK23503 for unknown,
account-only and each PtS literal on active/revoked insert and permission update;
each missing active field/incomplete revival gives named CHECK23514. Successful
registered-permission update, complete revival and removal of each provenance field
from an already revoked row preserve all unrelated values. Revoked partial values
and existing structural guards are preserved. Prefix/dependent CTE/multirow failures
prove complete transaction/statement rollback. `upgrade` preserves compatible11
heterogeneous permissions and active/revoked values, partial revoked history, five command receipts/replay/lookup and repeat.
`refusal` first preserves aggregate incompatible populated11 evidence. It then records
deliberate owned synthetic registration/revocation transitions, isolating each missing
active field on a registered legacy-permission row with exact pre/post refusal
snapshots. The owned-log digest inventory binds `refusal-fixture-transitions.json`,
including the original aggregate snapshot and deliberate transitions. These fixture
transitions are not production adoption. `privileges`
uses actual restricted runtime organization reads, missing/reset context, and runtime,
operator and definer raw-write denials. `drift` rejects catalog/history/ACL, all four individually disabled FK triggers
from an asserted inventory on both ends, extra dropped slots and forged tombstone metadata, including restricted
Identity19 selection/refusal. `failure_and_locks` preserves exact sanitized lock
reasons, bounded failure/postcondition rollback and explicit forward retry. `retained`
performs separate read-only exact12/exact-refused11 verification. Focused tests cover
DDL boundaries, every retained revision, metadata-only selection and custody ordering.

Five impacts: extend existing owner migration/catalog scaffold and native fixtures;
no shared UI or agent-context change; update owner docs/evidence and mutable substrate,
DEVELOPMENT/KDG handoffs; existing ADR-0052 authority suffices without editing ADRs.
No dependency, generator, service, deployment, pilot, actual provisioning or Leave
implementation is introduced. Root records exact results, reviews, regressions,
composition checks, normal stop and scoped local commit.

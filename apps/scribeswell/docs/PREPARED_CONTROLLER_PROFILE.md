# Prepared-controller replay qualification

`prepared-controller-v1` validates an already prepared, dormant `scribeswell_0003`
for controlled native rehearsal. It performs no caller preparation, actor registration,
grant repair, enforcement activation, scripture import or state cleanup. The existing
host adapter and command line remain strict dormant-only; ambient environment hints
cannot select this profile. An active enforcement/history release profile and host
integration remain separate gates.

Use `baseline.preflight_prepared(connection, expected_actor)` on an actual restricted
migrator connection inside a caller-owned writable `READ COMMITTED` transaction.
The exact custody dictionary is:

```python
expected_actor = {
    'schema_version': 1,
    'source_id': 'tanakh',
    'executor_actor_id': '<canonical nonnil UUID>',
    'actor_kind': 'service',
    'actor_key': '<verified service key>',
    'preparation_evidence_ref': '<independent preparation evidence reference>',
}
```

These values must come from independently verified Identity-owner custody. Matching
protected local records does not verify Identity. The validator reads no Identity
records and contacts no external owner. Source/key/reference bounds match the existing
controller; unknown fields, malformed UUIDs, booleans/floats as version and overrides
fail with fixed safe identifiers.

For the native Alembic `upgrade head` rehearsal, set only these Config attributes:

```python
config.attributes['scribeswell_validation_profile'] = 'prepared-controller-v1'
config.attributes['scribeswell_prepared_actor'] = expected_actor
command.upgrade(config, 'head')
```

Use the existing explicit migration database URL and validation prerequisites in
[MIGRATIONS.md](MIGRATIONS.md). Omission means `dormant`. Unknown/`None` profiles,
custody in dormant mode and missing prepared custody fail. There is no new environment,
CLI or host selector. `scribeswell_validated_profile` appears only after successful
pre/post checks and transaction commit; it is removed before each new invocation,
including offline/unsupported attempts. Existing before/after revision observations
remain diagnostic evidence rather than a new durable ledger.

The checker requires exact existing `0003`, original pinned catalogue, actual restricted
migrator authority, and the restricted operator login. The only permitted catalogue
changes are owner-granted, nongrantable operator schema `USAGE` and `EXECUTE` on the
execute/lookup entry functions. Those three ACL cells are compared semantically,
including grantor and grantability; every other catalogue/ACL field stays exact.
Memberships, unsafe settings, ownership, other direct/default or effective business
authority, reachable PUBLIC security-definer routines and cross-owner grants without
schema usage fail. Effective foreign-data wrapper/server USAGE, tablespace CREATE,
and parameter ALTER SYSTEM or SET on settings outside the ordinary user context also
fail, including privileges inherited through PUBLIC. These are catalogue-only checks;
no foreign access, filesystem operation or ALTER SYSTEM executes. Ordinary session
settings, system reads and standard PUBLIC CONNECT/TEMP remain. Protected core
routine EXECUTE cannot exceed the PostgreSQL initdb ACL for that exact `pg_proc`
identity (`pg_init_privs`, `privtype=i`); ordinary builtins remain available. PUBLIC
default table/sequence privileges in global or currently reachable schema scopes fail,
including empty schemas. Ordinary default function EXECUTE and type USAGE remain.

Exactly one matching principal and three source-scoped begin/recover/seal authorities
are required, with positive revisions, attributed nonnil actors and finite timestamps.
Current disabled/revoked flags are preserved. Control must remain false and epoch,
attempt, outcome and write-binding tables empty. Earlier/absent ledgers cannot be
adopted or upgraded through prepared mode.

Before catalogue inspection the checker establishes local `pg_catalog, pg_temp`
search order, keeping core catalogues ahead of temporary and public shadows. A fresh
connection without a caller-owned transaction fails without starting one. Before
coordination it caps local statement timeout at five seconds and lock timeout at two
seconds, retaining any existing shorter nonzero caller bound. It reuses the migration
advisory lock, then takes `SHARE` table locks in this order: principal, authority, control, epoch, attempt, outcome, write-binding.
These prevent local configuration changes, authority insert phantoms and state writes
through the transaction; reader/importer access stays compatible. A stable owner DDL
and cluster-role window is still required. No external wait or scripture scan occurs
under these locks. Errors require rollback; no automatic repair or re-enablement occurs.
Native replay retains the existing owner-only ledger ACL guard.

The disposable PostgreSQL suite
`apps/scribeswell/tests/test_prepared_controller_profile.py` proves default-path
characterization, closed inputs, exact custody/privilege denials, disabled mappings,
lifecycle/history rejection, full catalogue/business/sequence/ledger preservation,
reordered-equivalent three-cell ACL replay, actual pending-update rollback on post-check
and native commit-boundary failure, reused Config evidence cleanup and bounded local write
blocking with compatible readers/importers. Run it with the disposable fixture described
in [MIGRATIONS.md](MIGRATIONS.md#reproduce-local-qualification), sequentially with other
database suites. The repository delivery record records actual commands and results;
skipped acceptance cases provide no qualification. Live custody, production preparation,
active release, importer transition and sealed publication/reader proof remain open.

Impact decisions: no scaffold, shared UI or agent-context promotion; app documentation
and the canonical handoff record this bounded profile. Accepted ADRs, applied revisions,
references, host selection and importer behavior are unchanged.

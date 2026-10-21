# Protected Access application registration

The current Access0005 head supports `application.register` and `permission.register`.
For permission-specific payload, exact command authority and target recovery, follow
[permission registration](PERMISSION-REGISTER.md). `application.register` creates a disabled revision1
application and atomic immutable event/outcome; matching existing applications return
unchanged with their current revision and no event. Registration does not enable an
application or grant effective access. ACCESS-A/B consumer activation remains closed.

Preparation is explicit controlled deployment work. Use
`tools/prepare_access_operator_roles.sql` under the authorized true administrator before
the current Access0005 head. It creates the restricted LOGIN operator and NOLOGIN authority owner, and
validates an already staged restricted command owner or creates it. The migrator receives
only the two exact SET-only owner edges. Set the operator password through private
preparation; this SQL contains no password, principal or authority seeds. The ordinary
controlled Alembic route requires the prepared roles and refuses unknown catalog/default
ACL/role state. Preserve historical migrations and receipts; no startup migration/reset.

Bootstrap verifies a durable Identity actor externally, then supplies only that verified
UUID to Access principal and exact command/platform/application authority mappings under
`access_migrator`. Null application explicitly means all applications for this command.
Access has no Identity-table grants or cross-owner FK. Role names, GUCs, supplied actors
and infrastructure access alone are not authority. Authority revocation and command
execution serialize using the original login's authority lock.

The existing disposable target preparer now accepts `owner='access'`. For isolated
synthetic proofs it additionally accepts an eight-character lowercase hexadecimal
`namespace`, deriving `acop_<actual_run_uuid_hex>_<namespace>` and
`access-operator-<namespace>.json` in that actual run directory. It accepts no arbitrary
database name. Config hash, actual run, owner, login and private `secrets/access.env`
remain bound and are checked again inside the isolated worker. Identity targets retain
their existing behavior. Do not use a descriptor from another run or replace an existing
secret/descriptor to rerun proof.

From `services/access`, use the locked owner environment:

```sh
python -I -B operator_cli.py execute --owner access --target /absolute/prepared/access-operator-0123abcd.json --command-file /absolute/private/command.json
python -I -B operator_cli.py outcome --owner access --target /absolute/prepared/access-operator-0123abcd.json --command application.register --app-id synthetic_app --operation-id <same-UUID>
```

The closed version1 envelope contains `schema_version`, `operation_id`,
`command="application.register"`, `scope={"kind":"platform"}`,
`payload={"app_id":"synthetic_app","expected_absent":true}`, an approved
`reason_code`, and optional bounded `evidence_ref`. No executor, timestamp or owner
payload override exists. `permission.register` has its own explicit command authority;
application authority never implies it. `entry_permission.register` remains unsupported
before target or connection access. Keep credentials and verification documents out of command files.

Only a durable committed compact receipt acknowledges completion. Its typed target is
`{app_id}`, revision is a positive decimal string, and event UUID is present only for
creation. No fingerprint or payload is returned. After a lost response, look up the same
operation and explicit app under current authority; a missing receipt is unresolved.
Retry the same operation and input. Changed input conflicts. A receipt describes the
original command outcome, not current application state or consumer readiness.

Transactions require an idle READ COMMITTED connection and bounded lock/statement/total
execution. Only retry-lock timeout returns `operation_busy`; authority/application lock
wait failures are unavailable. Failure or uncertainty must not trigger a fresh blind
operation, privilege widening or deletion of prior evidence. Investigate retained safe
operation/run references through the owning recovery route. Never automatically reverse
applied migrations.

See [executed evidence](APPLICATION_REGISTER_EVIDENCE.md) for source custody, requirement
traceability, historical Access0004 native proof and remaining activation gates. Current
Access0005 qualification is recorded in [permission evidence](PERMISSION_REGISTER_EVIDENCE.md).

## Concrete controlled synthetic preparation

These steps apply only to an approved disposable run and its synthetic databases. The
administrator, Identity migrator and Access migrator use their separate explicitly
prepared credentials. Keep each complete DSN in an owner-controlled0600 file, with an
explicit loopback host, approved port, database and login. Never put a DSN/password in
argv, a command envelope, a receipt or a diagnostic log. No runtime credential is a
provisioning credential.

1. Inspect the actual run's native marker/configuration and the selected database/login
   before connecting. The controlled route targets Access0005 and recognizes exact
   clean/1/2/3/4/5 histories; unexpected state refuses. Before migration, under the
   authorized true administrator, execute the existing
   `tools/prepare_access_operator_roles.sql` once. Its transaction refuses unexpected
   existing roles/edges; do not work around that refusal with DROP, broad grants or
   silently replacing a role. An already staged command owner is accepted only with
   the exact restricted flags and no unlisted memberships.
2. Prepare the dedicated operator password without printing it. The following example
   uses the existing owner Python environment/psycopg, a complete private administrator
   DSN, and a private secret directory in the **actual selected run**. Substitute only
   the explicitly reviewed paths. The secret file is exclusive: an existing file is
   preserved and requires investigation rather than password rotation.

```python
from pathlib import Path
import os, secrets
import psycopg
from psycopg import sql

admin_dsn = Path('/absolute/private/synthetic-admin.dsn').read_text().strip()
secret_path = Path('/absolute/actual-run/secrets/access.env')
password = secrets.token_hex(32)
fd = os.open(secret_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
with os.fdopen(fd, 'w') as secret_file:
    secret_file.write('ACCESS_OPERATOR_PASSWORD=' + password + '\n')
    secret_file.flush()
    os.fsync(secret_file.fileno())
with psycopg.connect(admin_dsn, passfile='/dev/null', sslmode='disable',
                     gssencmode='disable', connect_timeout=3,
                     options='-c statement_timeout=5000 -c lock_timeout=2000') as connection:
    connection.execute(sql.SQL('ALTER ROLE access_operator PASSWORD {}').format(sql.Literal(password)))
```

If password preparation fails after writing the file, retain it and the safe failure
reference. Verify the role/target and connection under protected owner tooling before
resuming; do not overwrite the file or infer that its value became the live password.

3. Verify the durable synthetic service actor under **Identity ownership**, before
   inserting any Access mapping. For a clean isolated Identity fixture, the controlled
   `identity_migrator` bootstrap uses this stable classified actor, with self-attribution
   only for that explicit bootstrap. For an existing fixture, first read the selected
   actor ID/kind/key and creation evidence; reuse only the exact verified identity.
   A conflict stops preparation. Do not create a new actor per operation/run or infer an
   actor from a shell username, account ID or arbitrary supplied UUID.

```sql
BEGIN;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='2s';
INSERT INTO identity.actor(id,kind,actor_key,display_name,created_by,updated_by)
VALUES ('aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','service',
        'qualification.access_operator','Synthetic Access qualification operator',
        'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa');
SELECT id,kind,actor_key,created_by,created_at FROM identity.actor
WHERE id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';
COMMIT;
```

Retain the selected actor UUID, kind/key, controlled bootstrap source/run reference and
verification result in owner-controlled synthetic preparation evidence. This is an
Identity-owned read/write; grant Access roles no Identity-table access. It creates no
Auth account, organization membership, employee or application grant.

4. Run the ordinary Access controlled migration route with the explicit Access migrator
   configuration. After exact Access0005 verification succeeds, use `access_migrator`
   to prepare the principal and narrowly app-bound command authority below. The actor
   UUID must be the externally verified one from step3; no mapping seeds are in the
   migration. The example app identifier is synthetic and grants no effective app access.

```sql
BEGIN;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='2s';
INSERT INTO access.operator_principals
(database_login,executor_actor_id,enabled,created_by,updated_by)
VALUES ('access_operator','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',true,
        'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa','aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa');
INSERT INTO access.operator_authorities
(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by)
VALUES (gen_random_uuid(),'access_operator','application.register','platform',
        'synthetic_app',true,'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
        'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa');
COMMIT;
```

For existing mappings, inspect and verify the exact login/executor/command/platform/app,
current enabled state and revision before deliberately resuming. Do not replace or
reactivate a conflicting/revoked mapping as an automatic retry. `application_id=NULL`
is a separate explicit decision granting this command authority over all apps; the
bounded example does not need it. Permission registration additionally requires its
separate `permission.register` authority for the intended app, prepared under the
[permission-specific instructions](PERMISSION-REGISTER.md); the application row above
confers none.

5. Prepare a new target descriptor through the existing
   `identity_operator_target.prepare_target(approved_environment_target, actual_run_id,
   owner='access', namespace='0123abcd')` entry point, choosing an unused bounded synthetic
   namespace. Its database must already be the explicitly prepared derived database in
   that same actual run. Execute/lookup only through the selected Access CLI above.

## Read-only investigation and controlled resume

After role preparation, migration, postcondition or response failure, preserve the
private target, secret, logs, source witness, schema and all existing outcomes. Record
only safe run/operation references and error codes. First inspect the explicitly
selected database/login and restricted role flags/memberships using catalog reads:

```sql
BEGIN READ ONLY;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='2s';
SELECT session_user,current_user,current_database();
SELECT rolname,rolcanlogin,rolsuper,rolcreatedb,rolcreaterole,rolreplication,
       rolbypassrls,rolinherit
FROM pg_roles WHERE rolname IN
('access_operator','access_operator_authority_owner','access_command_owner');
SELECT pg_get_userbyid(roleid),pg_get_userbyid(member),admin_option,
       to_jsonb(m)->>'inherit_option',to_jsonb(m)->>'set_option'
FROM pg_auth_members m
WHERE roleid IN (SELECT oid FROM pg_roles WHERE rolname IN
('access_operator','access_operator_authority_owner','access_command_owner'))
   OR member IN (SELECT oid FROM pg_roles WHERE rolname IN
('access_operator','access_operator_authority_owner','access_command_owner'));
COMMIT;
```

Under **Access migrator only**, inspect the local ledger and catalog; do not give Identity
or the operator ledger/table reads merely to investigate:

```sql
BEGIN READ ONLY;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='2s';
SELECT version_num FROM access.alembic_version;
SELECT nspname,pg_get_userbyid(nspowner),nspacl FROM pg_namespace WHERE nspname='access';
SELECT c.relname,pg_get_userbyid(c.relowner),c.relacl
FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access';
SELECT c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid)
FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname='access';
SELECT defaclobjtype,defaclacl FROM pg_default_acl
WHERE defaclrole=(SELECT oid FROM pg_roles WHERE rolname='access_migrator')
   OR defaclnamespace=(SELECT oid FROM pg_namespace WHERE nspname='access');
COMMIT;
```

An absent ledger in an exactly empty owned schema is the clean case; do not query a
missing table as if that proved migration failure. Use the existing `access_baseline`
`preflight`/`verify_postcondition` checks through the explicit Access migrator connection
inside a bounded read-only transaction for the complete fixed catalog/ACL/role check.
These checks inspect known state and do not repair it.

A known unchanged prior head after a failed transactional migration can resume through
`alembic -c services/access/alembic.ini upgrade head`, with the same protected explicit
`ACCESS_MIGRATION_DATABASE_URL` configuration, after correcting only the verified
preparation prerequisite. If the exact head already committed, a controlled head repeat
verifies it without changing business data. Unknown ledger/catalog/default/role drift
stays blocked for explicit owner disposition; never stamp, reset, prune, disable guards,
normalize unexpected grants or reverse migrations automatically.

A migration/postcondition or connection error alone does not prove which writes committed.
Verify current known ledger/catalog state before resuming. For command uncertainty,
perform authorized same-operation/app receipt lookup first. A committed receipt resolves
the original command; an unresolved lookup remains uncertain and permits only the same
operation/input retry under current authority, not a fresh duplicate or broader access.
The adapter checks its deadline after COMMIT returns; an in-process clock cannot cancel
network COMMIT. The unchanged isolated CLI process bound and durable lookup remain the
recovery mechanism for a blocked/lost/late response.

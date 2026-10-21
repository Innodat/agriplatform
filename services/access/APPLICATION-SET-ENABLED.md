# Protected Access application enablement

Access0007 implements `application.set_enabled` through the existing protected Access
operator route. It changes the global application's availability only. Organization
admission, grants and effective consumers remain separately gated; consumer activation
is not authorized by this increment.

Use the existing [controlled preparation and recovery](APPLICATION-REGISTER.md).
The roles, durable external executor verification, actual-run target/secret binding,
READ COMMITTED transaction runner and bounded isolated CLI are shared with registration.
The controlled owner route accepts only exact clean/1/2/3/4/5/6/7 catalogs. Historical
migration files and source-bound evidence remain intact. Deploy migrations before
activating any compatible command client; migration failure blocks activation. Retain
previous state and evidence, inspect, then forward-reconcile through the same controlled
route. Never stamp, normalize unknown state, disable guards, automatically reverse an
applied migration, or migrate on API/worker startup.

After verifying Access7, the Access migrator may explicitly prepare a separate enabled
`application.set_enabled` authority for the verified operator principal, platform scope,
and intended application. `application.register`, permission and entry authorities
confer no enablement authority. An application_id NULL authority explicitly covers all
apps for this command; use a narrow app when appropriate. No new login, actor, principal
or authority is seeded by the migration. Original session login and current enabled
principal/authority determine the executor; payload/GUC/assumed role cannot replace it.

Before preparing authority, verify the selected durable actor under Identity ownership
and retain that evidence; Access preparation receives its verified UUID without Identity
table reads. Under the selected Access migrator, inspect the existing principal and
application. The synthetic example below expects enabled principal revision1 bound to
actor `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa` and existing `synthetic_app`. Substitute only
explicitly verified values. If either verification SELECT or INSERT returns no row,
stop and investigate; do not create a principal, upsert, widen scope or reactivate a
revoked mapping as a retry. Retain the returned authority UUID and revision for recovery.

```sql
BEGIN;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='2s';
SELECT pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:access_operator'));
SELECT database_login,executor_actor_id,enabled,revision
FROM access.operator_principals
WHERE database_login='access_operator'
  AND executor_actor_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
  AND enabled AND revision=1;
SELECT app_id,enabled,revision FROM access.applications WHERE app_id='synthetic_app';
INSERT INTO access.operator_authorities
(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by)
SELECT gen_random_uuid(),p.database_login,'application.set_enabled','platform',
       'synthetic_app',true,'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
       'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
FROM access.operator_principals p
WHERE p.database_login='access_operator' AND p.enabled AND p.revision=1
  AND p.executor_actor_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
  AND EXISTS(SELECT 1 FROM access.applications WHERE app_id='synthetic_app')
RETURNING id,database_login,command,scope_kind,org_id,application_id,
          target_account_id,enabled,revision;
COMMIT;
```

For deliberate revocation, verify the same principal/actor/app and inspect the exact
captured authority first. The example UUID below represents the UUID returned above;
replace it with that captured identity and use its verified current revision. This
transaction disables only that exact mapping and returns the identity and new revision.
Zero updated rows means unresolved/stale preparation; inspect rather than retrying with
broader predicates. No real authority transaction is executed by this documentation.

```sql
BEGIN;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='2s';
SELECT pg_advisory_xact_lock(access.command_lock('access:operator-authority:v1:access_operator'));
SELECT database_login,executor_actor_id,enabled,revision
FROM access.operator_principals WHERE database_login='access_operator';
SELECT app_id,enabled,revision FROM access.applications WHERE app_id='synthetic_app';
SELECT id,database_login,command,scope_kind,org_id,application_id,
       target_account_id,enabled,revision
FROM access.operator_authorities
WHERE id='77777777-7777-4777-8777-777777777777';
UPDATE access.operator_authorities
SET enabled=false,updated_by='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
WHERE id='77777777-7777-4777-8777-777777777777'
  AND database_login='access_operator' AND command='application.set_enabled'
  AND scope_kind='platform' AND org_id IS NULL AND application_id='synthetic_app'
  AND target_account_id IS NULL AND enabled AND revision=1
  AND EXISTS(SELECT 1 FROM access.operator_principals p
             WHERE p.database_login='access_operator'
               AND p.executor_actor_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa')
  AND EXISTS(SELECT 1 FROM access.applications WHERE app_id='synthetic_app')
RETURNING id,database_login,command,scope_kind,org_id,application_id,
          target_account_id,enabled,revision;
COMMIT;
```

The closed version1 envelope is:

```json
{
  "schema_version": 1,
  "operation_id": "11111111-1111-4111-8111-111111111111",
  "command": "application.set_enabled",
  "scope": {"kind": "platform"},
  "payload": {"app_id": "synthetic_app", "enabled": true, "expected_revision": "1"},
  "reason_code": "access_change",
  "evidence_ref": "synthetic:availability"
}
```

`enabled` is an actual JSON boolean. `expected_revision` is a canonical positive decimal
string through signed-bigint maximum. No actor/time override is accepted. Preserve
credentials and business verification documents outside command files.

From `services/access` in the locked owner Python environment:

```sh
python -I -B operator_cli.py execute --owner access --target /absolute/prepared/access-operator-0123abcd.json --command-file /absolute/private/command.json
python -I -B operator_cli.py outcome --owner access --target /absolute/prepared/access-operator-0123abcd.json --command application.set_enabled --app-id synthetic_app --operation-id 11111111-1111-4111-8111-111111111111
```

New operations require an existing app with the exact expected revision, even if its
current enabled state already matches. A changed state increments revision exactly
once and derives update actor/time server-side. Creation attribution, app identity,
permissions, entry mappings and grants remain intact. Matching state preserves every
application field and emits no change event. Changing bigint maximum conflicts;
matching it is valid. Missing/stale state conflicts without effects.

The compact typed receipt retains target `{app_id}`, disposition `changed|unchanged`,
revision as decimal string, and UUID event_id for changed or null for unchanged.
Changed row, outcome and single `access.application_availability_changed` event commit
atomically. Event transition is exactly
`{before:{enabled,revision},after:{enabled,revision}}`, with revision strings.
Row/deferred guards prove the OLD/NEW linkage, derived actor/time and required event.
The routine compares canonical input with its typed arguments including reason and
evidence before fingerprinting; database guards do not claim SHA256 inversion.
Only the command owner receives column UPDATE(enabled); the operator receives only
exact routine EXECUTE. Identity/creation fields and managed revision/time remain guarded,
and permission/entry immutability and DELETE/TRUNCATE protection remain binding.

Retry only the same operation and input. Identical retries recover the original receipt
before current-revision checks, including after later changes. Changed input conflicts.
The four command/platform namespaces stay independent even with the same UUID.
Lookup requires current command/app authority and the explicit exact app; another app
is denied, and an absent receipt is unresolved. Revocation can deny execute/replay/lookup
of an old receipt. Retry→authority→existing application lock ordering and authority
rechecks after waits remain bounded. Only retry-lock timeout is `operation_busy`;
authority/application lock timeout is unavailable.

A lost/late COMMIT response is uncertain. Resolve the original operation/app under
current authority, then retry the same input when appropriate. A receipt proves the
original operation, not present app state or consumer readiness. Preserve private
proof targets, secrets, failed attempts and safe source/run/operation references.
See [qualification evidence](APPLICATION_SET_ENABLED_EVIDENCE.md).

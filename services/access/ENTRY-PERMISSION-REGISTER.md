# Protected entry-permission registration

Access0006 adds `entry_permission.register` to the existing protected Access operator
route. It binds an existing exact permission to its registered application as an
immutable entry permission. Both permission scopes and disabled applications are valid;
multiple explicit permissions may be entries for one application. It grants no access.

Follow the existing [owner preparation and recovery runbook](APPLICATION-REGISTER.md).
Use the same restricted roles, private prepared target and controlled `upgrade head`.
Only exact clean/1/2/3/4/5/6 histories are accepted; unknown state refuses without repair.
The migration preserves existing configuration, evidence and receipts. Identity18 checks
exact Access4/5/6 metadata without reading Access business rows or migration history.

Provision an enabled original-session principal and separate enabled
`entry_permission.register` authority for platform scope and the intended app (or an
explicit null application for all apps). Application or permission command authority
confers no entry authority. No raw operator/runtime registry privileges are added.

After the linked preparation has established the principal, use the Access migrator
for this separate entry authority. The following narrow synthetic example assumes that
Identity verification established actor `aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa`, that the
prepared original login is exactly `access_operator`, and that the intended registered
application is exactly `synthetic_app`. Substitute all three only from verified owner
preparation evidence; confirm the existing principal has that same enabled actor/login
binding. The operator and runtime must not execute this owner SQL.

```sql
BEGIN;
SET LOCAL statement_timeout='5s';
SET LOCAL lock_timeout='2s';
DO $owner$
BEGIN
 IF NOT EXISTS (SELECT 1 FROM access.operator_principals
     WHERE database_login='access_operator' AND enabled
     AND executor_actor_id='aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'::uuid)
    OR NOT EXISTS (SELECT 1 FROM access.applications WHERE app_id='synthetic_app') THEN
  RAISE EXCEPTION 'verified entry preparation binding required';
 END IF;
END
$owner$;
INSERT INTO access.operator_authorities
(id,database_login,command,scope_kind,application_id,enabled,created_by,updated_by)
VALUES (gen_random_uuid(),'access_operator','entry_permission.register','platform',
        'synthetic_app',true,'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
        'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa');
COMMIT;
```

Inspect existing exact authority rows before applying this example. An existing disabled
or conflicting row requires deliberate owner disposition; do not use an upsert or
reactivation as retry recovery. Keep `application_id` app-bound for this example.

The exact version1 envelope is:

```json
{"schema_version":1,"operation_id":"a1234567-1234-1234-1234-123456789abc","command":"entry_permission.register","scope":{"kind":"platform"},"payload":{"app_id":"synthetic_app","permission":"synthetic.read","expected_absent":true},"reason_code":"synthetic_fixture","evidence_ref":"synthetic:entry"}
```

Permissions are literal ASCII1–200 bytes, including controls and DEL; NUL is forbidden.
No trimming, normalization, wildcard expansion, scope change, permission creation or
reassignment occurs. Missing permissions and wrong application associations conflict
without writes. Identical mappings return unchanged without a creation event.

From `services/access` with the prepared interpreter:

```sh
python -I -B operator_cli.py execute --owner access --target /private/prepared/access-operator.json --command-file /private/entry-command.json
python -I -B operator_cli.py outcome --owner access --target /private/prepared/access-operator.json --command entry_permission.register --operation-id a1234567-1234-1234-1234-123456789abc --app-id synthetic_app --permission=synthetic.read
```

Always use `--permission=<literal>` for flag-like literals. Receipts contain exact
`{app_id,permission}`, created/unchanged, null revision and an event UUID for creation
only. Creation event transition is `{}`: the type and target express binding creation.
Current exact authority is required for execute, replay and explicit-target lookup,
including rechecks after waits. Wrong lookup targets deny; absent outcomes are unresolved.
The same operation UUID remains independent across all three registration commands.

The full JCS envelope is SHA256-bound. Entry/outcome/event commit atomically with
required linkage. Only retry-lock timeout reports busy; other waits/errors remain
sanitized unavailable. Retain original input/operation after uncertain completion and
recover under current authority. Do not infer rollback, repair catalogs, widen authority,
repeat migrations on process startup or automatically downgrade. Recovery follows the
existing controlled owner route. See [evidence](ENTRY_PERMISSION_REGISTER_EVIDENCE.md).

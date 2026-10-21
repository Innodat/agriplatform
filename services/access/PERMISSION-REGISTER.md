# Protected permission registration

Access0005 extends the existing Access operator route with `permission.register`.
It registers one immutable literal permission/application/scope association and grants
no access. Applications may remain disabled. Entry registration is provided by the separate [entry command](ENTRY-PERMISSION-REGISTER.md).
Application enablement is separately authorized through the
[Access0007 command](APPLICATION-SET-ENABLED.md); permission authority confers none.
Grants and consumer activation remain separately gated.

Use the existing [application operator preparation and recovery runbook](APPLICATION-REGISTER.md).
The same three restricted roles and private prepared Access target apply; no additional
credential, role or lifecycle is required. Controlled Access `upgrade head` accepts only
exact clean/1/2/3/4/5/6 histories. Populated Access4 rows and original receipts are preserved;
unknown metadata, default privileges or history refuse without normalization. Ordinary
Identity verification selects exact Access4/5/6 metadata without reading its ledger or data.

Controlled owner bootstrap must verify the external service actor and provision an enabled
`access.operator_principals` mapping for the original session login plus an enabled
`permission.register` authority with platform scope and the exact application (or explicitly
all applications via null application). `application.register` authority grants no permission
registration authority. Operator/runtime logins receive no raw registry/table access.

A version1 envelope has these exact fields (UUID is illustrative):

```json
{"schema_version":1,"operation_id":"a1234567-1234-1234-1234-123456789abc","command":"permission.register","scope":{"kind":"platform"},"payload":{"app_id":"synthetic_app","permission":"synthetic.read","scope_kind":"organization","expected_absent":true},"reason_code":"synthetic_fixture","evidence_ref":"synthetic:permission"}
```

Permission values are literal ASCII 1–200 bytes, including whitespace, controls and DEL;
NUL is forbidden. Do not trim, normalize or expand wildcards. Scope is exactly `account`
or `organization`. An identical mapping returns unchanged with no new event; reassignment
of its application or scope conflicts. Missing applications conflict without writes.

From `services/access`, use the canonical prepared interpreter/locked owner environment:

```sh
python -I -B operator_cli.py execute --owner access --target /private/prepared/access-operator.json --command-file /private/permission-command.json
python -I -B operator_cli.py outcome --owner access --target /private/prepared/access-operator.json --command permission.register --operation-id a1234567-1234-1234-1234-123456789abc --app-id synthetic_app --permission synthetic.read
```

For a permission beginning with a dash, pass its literal lookup value as
`--permission=<literal>`; this prevents option parsing from changing its meaning.

Both execution and recovery require current exact authority, rechecked after bounded waits.
The compact receipt contains target `{app_id,permission}`, created/unchanged disposition,
null revision and a creation event UUID only when created. Lookups require explicit app and
literal permission; a wrong target denies, absent outcome remains unresolved. The operation
key includes scope, executor and command, so an application operation with the same UUID
cannot supply a permission receipt. The full immutable envelope is fingerprinted with JCS
SHA256, including scope and expected absence.

On uncertain completion retain the original operation/input and use exact authorized lookup.
Do not infer rollback, manufacture a new operation, widen authority, stamp a ledger, disable
guards or automatically downgrade. Only an outcome-key lock timeout returns operation_busy;
authority/domain waits and unclassified database errors use safe unavailable responses.
The existing ten-second transaction/isolated worker bounds and late-commit recovery apply.

See [qualification evidence](PERMISSION_REGISTER_EVIDENCE.md) for commands, traceability,
source custody, retained inspection and explicit limitations.

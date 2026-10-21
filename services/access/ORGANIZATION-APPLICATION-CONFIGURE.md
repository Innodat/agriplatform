# Protected organization application configuration

`organization_application.configure` is a bounded Access owner command through the
existing isolated operator CLI. Access9 follows8; historical migrations, Identity19
and references remain unchanged. This slice does not activate admission, grants,
consumer readers or PtS/KDG. A registered globally disabled application is a valid
configuration target. Disabling preserves configuration and grants.

Use only an explicitly prepared synthetic/local target for this qualification. The
existing target descriptor binds owner, database, original login and protected secret.
Do not put credentials, actors or arbitrary SQL into command files or arguments.

## Command and recovery

The version1 envelope uses organization scope and exactly one expected state:

```json
{
  "schema_version": 1,
  "operation_id": "a1234567-1234-1234-1234-123456789abc",
  "command": "organization_application.configure",
  "scope": {"kind": "organization", "org_id": "b2345678-2345-2345-2345-23456789abcd"},
  "payload": {"app_id": "fixture_app", "enabled": true, "expected_absent": true},
  "reason_code": "synthetic_fixture",
  "evidence_ref": "setup:fixture/1"
}
```

Updates replace `expected_absent` with `expected_revision`, a positive signed-bigint
canonical decimal string. Matching state still requires a matching expected revision.
Creation yields revision1; changes increment once; unchanged leaves all attribution
and revision intact and returns null `event_id`. Create/update conflicts never overwrite.

From the existing owner environment, execute the existing CLI:

```sh
python -I -B services/access/operator_cli.py execute --owner access \
  --target "$PREPARED_TARGET" --command-file "$COMMAND_FILE"
python -I -B services/access/operator_cli.py outcome --owner access \
  --target "$PREPARED_TARGET" --command organization_application.configure \
  --org-id "$ORG_ID" --app-id fixture_app --operation-id "$OPERATION_ID"
```

Retain the exact command and operation UUID after uncertain completion. Exact replay
returns the original result under current authority; changing input with the same key
conflicts. Outcome lookup requires the exact organization and app and current authority,
without asserting current organization eligibility. New execution/replay always checks
Identity again. An unresolved lookup never proves that a command can be safely replaced
with changed input under the old operation UUID.

## Protected execution

The original `session_user` selects the enabled protected principal. Authority must
match the exact command, organization, selected app or explicit all-app value, and null
target account. Platform registration/enablement authority cannot substitute. The
command checks before calling Identity19, overwrites transaction-local setup org/actor
and empty-account context, and rechecks authority after waits. Callers cannot supply an
executor with payload or settings. No Identity business table reads, new roles or
Identity grants are added.

The Identity observation starts before the call and expires five seconds later,
including waits and replay. Missing/deleted organizations conflict; unsafe/missing
verification refuses as unavailable. Local locks and revision checks remain mandatory.
Only the retry lock maps to busy; other lock failures remain unavailable.

Organization configuration, compact outcome and `access.organization_application_changed`
event commit together. Events contain only before/after enabled and decimal revision;
before is null for creation. Deferred constraints reject omitted transition evidence.
Creation identity/history, forced organization RLS, local RESTRICT FK and delete/truncate
refusal remain. The command owner alone gains selected local DML, guarded against
unsupported raw/noop/empty statement paths.

## Controlled release and recovery

Use the existing controlled migration route, with migrations before activation and
activation blocked on failure. Exact known8 is retained; Access9 and Identity19 verify
fixed metadata, ACLs, policies, triggers, FK enforcement and private history. Identity
selects9 only from installed routine metadata and reads no Access business/history rows.
Ordinary releases preserve the four prior commands and the actual previous8 adapter.
No migrations run at application startup and no automatic downgrade is supported.

A migration failure leaves its transaction unapplied. Preserve logs and prior artifacts,
inspect without normalization, and rerun only after explicit reconciliation through the
existing route. A committed migration is recovered forward; do not delete private history,
reverse applied migrations or drop configuration to repair a release.

## Synthetic qualification

The root fixture preparation remains private and separate. It supplies exactly nine
cases (`configure`, `authority`, `retry`, `guards`, `concurrency`, `upgrade`, `rollback`,
`drift`, `cli`) using the existing four-group loopback protocol, Identity19 org verification,
verified synthetic service actor evidence, protected operator roles and the source-bound
previous8 package from the spec baseline. It is not portable CI bootstrap evidence.

```sh
ACCESS_QUALIFICATION_DIR="$PRIVATE_FRAME" python -I -B \
  services/access/tests/qualify_organization_application_configure.py --all
ACCESS_QUALIFICATION_DIR="$PRIVATE_FRAME" python -I -B \
  services/access/tests/qualify_organization_application_configure.py --verify-retained
```

`--all` is single-use. Retained verification reads current exact catalogs and compares
saved business/catalog state under read-only transactions. Source custody covers owner
sources, qualifier/helpers, private bootstrap sources, Auth helper definitions, explicit
previous8 manifest/package and log digests. Mutable native run receipts are excluded from
immutable source hashes. A failed invocation records safe frame locations without driver
exceptions, SQL or submitted values. Preserve every prior frame and log.

The [evidence record](ORGANIZATION_APPLICATION_CONFIGURE_EVIDENCE.md) holds actual commands,
results, RED/GREEN and traceability. Scaffold impact: owner-local command/parser/catalog
and qualification fixtures extend existing seams; no new generator or service. Shared UI:
none. Agent context: no new rule. Documentation: this runbook and mutable substrate/handoff
records. ADR: existing decisions suffice; no accepted decision is edited.

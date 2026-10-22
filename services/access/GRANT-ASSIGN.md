# Protected organization grant assignment

Access0013 adds `grant.assign` to the existing protected Access operator route. A
committed result proves an explicit owner-local binding; effective admission, readers,
ACCESS-B, PtS, KDG, Content and Leave activation remain separate delivery gates.

Use the existing protected target preparation, credential mapping and operator CLI.
The original database login must have an enabled principal and exact `grant.assign`
organization/app/account authority. Null app/account policy means explicitly all for
that command and organization; platform or another command authority confers nothing.
Nil target account policy is refused. The application is resolved from immutable
registered organization permission metadata, never supplied in the grant payload.

The version1 envelope is the existing closed parser contract. A synthetic create is:

```json
{
  "schema_version": 1,
  "operation_id": "a1234567-1234-4234-8234-123456789abc",
  "command": "grant.assign",
  "scope": {"kind": "organization", "org_id": "b2345678-2345-4345-8345-23456789abcd"},
  "payload": {
    "account_id": "c3456789-3456-4345-8345-3456789abcde",
    "membership_id": "7",
    "permission": "kdg_capture.read.own",
    "expected_absent": true
  },
  "reason_code": "synthetic_fixture",
  "evidence_ref": "setup:fixture/1"
}
```

Updates/regrants use a fresh operation ID and replace `expected_absent` with the
current positive decimal-string `expected_revision`. Keep the exact supplied current
membership. The Identity `organization_account_target` setup projection verifies the
account/profile, actor, active organization and exact member without requiring a grant,
person, employment or enabled admission. Identity waits precede local coordination and
write locks; the total observation budget is five seconds including waits and replay.
Every execution/retry observes again. For the supported adapter and its transaction
with constraints left deferred, the existing outcome guard rechecks observation presence,
finiteness, future time and age at commit for both changed and unchanged outcomes,
refusing expiration as verification unavailable. Arbitrary SQL that forces constraints
early with `SET CONSTRAINTS ALL IMMEDIATE` is outside that transaction guarantee.
A concurrent retirement preserves the observed
binding and gives a replacement member nothing until a new verified command rebinds it.

Run from `services/access` using the prepared private target:

```sh
python operator_cli.py execute --owner access --target "$TARGET" --command-file "$COMMAND_FILE"
python operator_cli.py outcome --owner access --target "$TARGET" --command grant.assign \
  --operation-id "$OPERATION" --org-id "$ORG" --account-id "$ACCOUNT" \
  --membership-id "$MEMBER" --permission "$PERMISSION"
```

Target flags contain identifiers only; credentials remain protected files. Outcome
selection requires exact org/account/member/permission, with no app selector. A result
target contains exactly `grant_id`, `account_id`, `permission`, `org_id`, `membership_id`.
New grants have UUID text ID and revision1; existing IDs (including opaque text) and
creation fields are retained. Expected absence/revision is checked before unchanged.
Matching active binding records only an unchanged receipt. Regrant clears revocation
and increments revision once with server executor/time and an immutable transition
event. Unknown original creation actor or changed-write revision overflow conflicts.

The protected writer receives only SELECT/INSERT and UPDATE(membership_id,revoked_at).
Statement, row and deferred guards refuse raw writers, empty/multirow writes, forged
shapes, missing or mismatched grant/outcome/event evidence. The event carries compact
before/after member/revocation/revision plus executor attribution; private outcome fields
retain verified member revision/account actor/observation start, never display text.
No Identity migration, reference or privilege changes are needed. Exact Identity19
verification selects Access13 through schema-resolved routine metadata before Access12;
the complete installed Access metadata/ACL is verified before dependency exclusions.
Historical1–12 catalogs and original sources remain independently recognized.

Use controlled migration before activation. Drift or a failed migration blocks activation
without normalization. Retain applied history and reconcile failure; retry forward through
the same route after the cause is resolved. Never migrate on startup, auto-downgrade,
reset, prune evidence or silently replace creation attribution. Ordinary releases retain
previous five-command Access12 client/receipt compatibility. For uncertain completion,
look up the same operation under current exact authority; missing is unresolved. Retry
that operation with identical stable input. Use a fresh operation only for an explicit
new action against current expected state. Receipts describe past commits, not current
membership or application access.

## Isolated native verification

Root prepares nine fresh synthetic cases: `assign`, `authority`, `retry`, `guards`,
`concurrency`, `upgrade`, `rollback`, `drift`, `cli`, with exact existing credentials/run
schema. Include private `identity-operator-credential.json`, `runtime-credential.json`,
`root_qualification_driver.py`, `auth-helper-definitions.json`, actor bootstrap evidence,
and the baseline666211d Access adapter as `previous12_access_operator.py` (SHA256
`2921c87cc7504bcaa59b1aa784991c91023378a39ddd5b5b0e724d5c62075361`).
Existing strict-storage bootstrap helpers consume retained private registry/org-storage
credentials and original run configuration; these dependencies are source-bound in
custody. No portable CI bootstrap or logical-restore claim is made.

Freeze production/test/runbook sources before root captures bootstrap custody. Use the
prepared Python (no dependency changes):

```sh
platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python -m pytest services/access/tests/test_grant_assign.py -q
ACCESS_QUALIFICATION_DIR="$PROOF" "$PYTHON" services/access/tests/qualify_grant_assign.py --all
ACCESS_QUALIFICATION_DIR="$PROOF" "$PYTHON" services/access/tests/qualify_grant_assign.py --verify-retained
```

`--all` is single-use and refuses optimized Python. Separate retained verification checks
source/input/log/state custody before database inspection, then exact metadata and state.
Owned logs exclude independent root stdout/status files. Preserve failed frames; changed
source needs a fresh prepared frame, never refreshed successful evidence. Root owns actual
native execution, retained proof, broader regressions/composers, normal stop and final
custody audit; passing unit fixtures alone do not claim native acceptance.

Requirement traceability: `test_grant_assign.py` checks history/DDL ordering/exact column
dependency scope. `qualify_grant_assign.py` stages cover first binding with disabled
admission and literal ASCII quote/backslash/control canonical agreement; typed
receipt/retry/noop and stale state; exact restricted-authority positive execution/recovery
and target denial before blocked Identity, bounded projection failure, inactive org/profile
refusal with exact fixture restoration; restricted writer, malformed private observations
and missing evidence rollback; concurrent retry, create/rebind expected-state races and
lock budgets; observation expiry including created/unchanged default-deferred delayed-commit
rollback and retirement/rejoin; populated12→13 preservation of five actual prior-command
clients/receipts plus fresh prior-client operations including real enablement/configuration
changes and lookup/replay; migration rollback/forward recovery; drift,
Identity19 metadata verification, CLI and independent retained inspection. Client/CLI
closed wire and malformed selector tests live in `test_grant_assign_adapter.py`.

Five impacts: extend existing Access owner command/evidence scaffold; no shared UI;
existing agent context applies; owner runbook/evidence and mutable delivery handoffs
record this increment; accepted ADRs remain unchanged. No new runtime framework,
generator, generic fixture engine or access consumer is introduced.

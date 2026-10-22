# Private organization check-reader Identity bridge

Identity0020 first narrows execution on six exact legacy callable routines, then grants the prepared `access_check_reader` only Identity schema USAGE and
EXECUTE on the unchanged `identity.current_account_organization()`. It stages a private
NOLOGIN owner dependency. Access14, effective check wrappers/HTTP, applications,
target discovery and PtS/KDG activation remain separately gated.

Controlled order is: verify the exact retained Identity19 catalog/history and prior
consumer state; run `tools/prepare_access_check_reader.sql` as the explicitly selected
true deployment administrator; independently rehearse the captured0020 source against
a fresh source-verified19 reference case, with rollback and source custody; record/pin
the resulting `check-reader-bridge-reference.json`; then use the existing controlled
Identity Alembic upgrade route with the private Identity migrator configuration. The
reference is developer rehearsal evidence, never target self-approval. There is no
new target export/approval/bypass CLI. Preparation refuses an existing role name;
it never repairs or reuses it. Deployment preparation portability remains an existing
limit, and this synthetic qualification makes no portable CI claim.

The prerequisite preserves these non-owner execution recipients exactly:

| Routine | Recipients |
| --- | --- |
| custom_access_token_hook(jsonb) | supabase_auth_admin |
| public.get_user_roles() | authenticated |
| create_user(text) | none |
| authorize(identity.app_permission) | authenticated, service_role, postgres, identity_account_projection_owner, identity_target_projection_owner, identity_account_verification_owner, identity_command_owner |
| membership_join_profile_allowed(uuid), membership_join_org_allowed(uuid) | identity_command_owner |

Exact19 catalog verification precedes any mutation, so unknown recipients, definitions,
owners or policies refuse rather than being normalized. The migrator uses the existing
SET-only `identity_operator_authority_owner` edge for effective join-probe revocations.
The two pure invoker JWT context helpers remain callable; trigger-only routines remain
unchanged and cannot be invoked as ordinary SQL data routines. Classification is bound
to exact routine definitions and the complete known catalog, including effective PUBLIC
privileges; no schema-wide or default-ACL change is made. Legacy `public.get_user_roles`
stays in public. Bodies, owners, schemas, policies and forced RLS stay unchanged.

The migrator grants schema usage as schema owner, assumes only its existing SET-only
`identity_account_projection_owner` edge for the function grant, then resets its role.
No migrator authority or membership is added. Preconditions reject unsafe role flags,
incoming or outgoing memberships, ownership/ACL/policy-role dependencies and excess effective
privileges, including PUBLIC privileges and both history ledgers. Postconditions verify
exact20 catalog fingerprints against the immutable19 reference chain plus the new
reference. Dependency checks cover current-database and shared catalog references,
including policy-role `r` dependencies even when no ACL privilege exists. Other databases
retain independent owner histories; this check does not certify their catalogs.
A bounded rollback-only foreign-table policy fixture proves an unlisted reader role
reference refuses, then verifies complete restoration. Nullable internal actor evidence, trusted backend context, current member
selection and existing RLS behavior are unchanged. Actor assertion alone neither
selects the account nor grants authority. Missing required account/org or wrong/setup
context fails closed; a current unmapped account retains its nullable internal actor.

Use the existing owner environment Python to run
`-m pytest services/access/tests/test_check_reader_bridge.py -q` first. The root owns
native startup, role preparation/reference custody and the inherited-hook RED witness.
With its selected private fixture in `IDENTITY_QUALIFICATION_DIR`, execute
`services/access/tests/qualify_check_reader_bridge.py --all` once, then execute
`--verify-retained` separately. The qualifier uses existing supported actor ensure and
membership join/retire commands. It proves populated Access14/Identity19 preservation,
controlled upgrade/repeat, unsafe/drift refusal, postcondition rollback, forward retry,
current/unmapped/malformed/setup/deleted/retired contexts, and actual restricted
NOLOGIN session authorization denials for raw tables/history, other projections,
writes and owner escalation. It records selected stage identifiers; SQL, URLs and
account data remain confined to protected fixture evidence. Sources are inventoried
before execution and checked again before retained inspection. The root records exact
commands/results and log/state custody in `CHECK_READER_BRIDGE_EVIDENCE.md`, including
affected regression and composition checks.

Any failed precondition or postcondition aborts the whole owner transaction, including
all six routine ACL changes, schema/function grants and applied20 history. Do not activate consumers after failure.
Inspect retained safe evidence, reconcile the exact approved defect through its owning
controlled preparation, and explicitly retry the forward upgrade. Never normalize
unknown authority, stamp over drift, reverse an applied migration automatically, or run
migrations on API/worker startup. Ordinary release compatibility and explicit recovery
remain required by platform ADR-0020. Preserve historical migrations/references and
prior native frames; normal root lifecycle stop retains data and receipts.

Impact decisions: scaffold extends the existing owner preparation, exact catalog and
qualification fixtures; no generator/framework/dependency is added. Shared UI has no
change. Agent context has no change. Documentation adds this owner runbook and root
custody evidence plus mutable delivery handoffs. Existing ADRs cover the bridge and
remain unchanged. There are no runtime application, account-reader, app grant or
consumer activation changes.


Requirement-to-test mapping:

| Requirement | Executed proof |
| --- | --- |
| true-admin preparation; exact19→20; historical/reference refusal | `test_check_reader_bridge.py` preparation, head and reference cases; native controlled upgrade |
| exact old/new foreign ACLs with fixed bodies/owners | parameterized foreign-recognition tests; native Access14 migration/clients |
| unsafe flags, memberships in both directions, dependencies, PUBLIC/raw/ledger/catalog drift | all seven unsafe role flags parameterized against the verifier; native `before_upgrade` refusal cases, foreign-policy dependency rollback and repeat20 drift |
| atomic failure and bounded locks, explicit forward retry | exact final safe error identifiers; injected postcondition, migration advisory lock, ledger relation lock, forward-retry20; lock subprocess deadline15 seconds and elapsed bound12 seconds |
| supported Auth/Expense/profile/current/target/verification/command callers | native `supported_callers` executes actual role calls, including service_role authorize with/without JWT role, policy writes rolled back; supported ensure/join/retire and Access14 execute/recovery |
| user/current/unmapped/missing/malformed/setup/wrong/deleted/retired projection contexts | native `read_matrix`, preserving read-probe snapshots and rolling back deleted fixture variants |
| actual reader denial despite schema USAGE, forged JWT/account/org claims | native `privileges`: six sensitive callable helpers, raw tables/both ledgers, other projections including the exact organization/account/member point target, writes, owner escalation |
| source/log/state retention and safe failures | source snapshot before/after; log hashes and retained read-only inspection; optimized-Python and safe-error tests |

The original pre-edit RED frame independently demonstrated inherited hook disclosure
under the temporary reader schema grant and rolled that grant back. Its original
source/input/RED receipts remain separate historical evidence; it did not execute the
final amended20 source.

The final native fixture instead prepares exact19 through the captured historical
Identity19 owner tree and `historical_identity19_driver.py`, retaining that tree's
original19 postcondition. `baseline-preparation-custody.json` binds the actual final
preparation inputs and sources. Final qualification hashes that complete historical
tree, the actual bootstrap and optional root driver, private inputs and current production
sources in `check-reader-source.json` before and after execution. Thus the final source
inventory includes every source consumed by historical19 preparation and current20
qualification, without claiming that bootstrap applied current20.

Controlled/refusal `.log` files retain outcomes. Protected refusal witnesses record
only stage/status/restoration, including unexpected probe failures. The retained record
binds these artifacts, sources, complete business/history state, catalog and stage
identifiers. Separate `--verify-retained` rechecks the binding without mutation. Root
separately binds the independent rollback-only rehearsal script/reference and exact
commands in the evidence record. Preserve failed frames and logs; never copy generated
state into a new successful receipt.

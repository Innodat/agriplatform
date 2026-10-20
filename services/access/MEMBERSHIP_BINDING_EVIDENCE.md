# Immutable membership binding evidence

Bounded Identity ID-B prerequisite, 2026-10-20. Accepted E1 membership design requires
that a retained membership ID cannot be repurposed for another organization/account.
See [Build](../../_bmad-output/implementation-artifacts/spec-id-b-membership-binding.md)
and [owner runbook](IDENTITY-MIGRATIONS.md). This binding-only increment leaves retirement,
rejoin, uniqueness/CASCADE/seed transition and owner commands as remaining delivery gates.

Revision11 replaces only identity.guard_org_member_revision() body, adding id/org_id/
user_id immutability before existing UPDATE revision calculation. It preserves owner,
invoker security, signature, ACL/search_path, trigger and every other object/function.
Unchanged binding assignments and existing mutable/seed behavior retain revision rules.
Rejected statements return23514/org_member_binding_immutable with no partial row/audit
change. Original10 revisions/references/source pins and composed SQL remain immutable.
No existing row is rewritten, new role/credential/grant/API or service introduced.

## Requirement-to-test mapping

| Requirement | Proof |
| --- | --- |
| Observe actual permissive binding before11 | Unchanged10 rollback-only valid-FK id/org/account characterization; no constraint bypass |
| Immutable instance identity at owner boundary | Actual service_role DML under restricted access_runtime login; active/retired, mixed and multirow refusal with exact row/roles/audit hashes |
| Preserve legitimate mutable writes | Noop/insert/server-revision/overflow and actual seed-shaped upsert/reference checks; existing read/Auth consumers remain unchanged |
| Coordinated migration/recovery and custody | Clean/adopt/exact10/repeat, drift/unknown and injected mid-revision failure; exact prior23 source files, only-guard function comparison and historical catalog/ACL preservation |
| Isolated bounded proof | Existing private fixture protocol, SQL/lock deadlines, durable restoration witnesses, exact temporary SET-only edges restored; root-only sequential cluster execution |

Root proof starts at platform/deployment/.local/identity-baseline/member-binding-ckpyu3za/.
Synthetic profile/org/member/role data only; direct database proof is not HTTP/provider/
JWT-signature or real-target adoption. No runtime readiness beyond this bounded item is
claimed. All previous failures/data/resources/receipts and concurrent documents remain.

## Five impacts

- Scaffold: extend existing owner migration/reference/recorder/qualifier; no generator
  or new generic lifecycle abstraction.
- Shared UI: no consuming interface or component change.
- Agent context: existing AGENTS.md safeguards suffice; exact verified commands/limits
  remain with owner documentation and KDG continuation.
- Documentation: owner runbook, evidence, ownership inventory and KDG navigation record
  the delivered boundary and remaining lifecycle/Access/WRITE/server-KDG gates.
- ADR: implements accepted structural integrity, membership binding and release safety
  contracts. No new decision and no accepted ADR modification.

## Verification

Initial actual matrix PASS25.681s, source unchanged, in the retained root frame.
Actual restricted-login unchanged10 characterization proves all three reassignment
paths. New11 rejects each field on active/retired rows and mixed/multirow statements,
retaining row/role/audit state. Noop/INSERT/mutable server revisions, overflow, exact
seed-shaped upsert/lookup and legacy role/token/current-account readers pass. Clean/
adopt/exact10/repeat, injected CREATE FUNCTION failure/atomic rollback/recovery and
profile-privilege drift refusal pass. Unknown history is tested rollback-only through
the actual owner preflight on the same connection; no subprocess migration claim for
that case. Migration fixture setup is explicit; read/characterization mutations rollback.
Seed upserts may consume PostgreSQL identity sequence values even after rollback, as
before; row/history preservation does not promise sequence-counter restoration.

Root's first direct observation attempted owner-only ledger inspection after SET ROLE
service_role and refused42501 before any mutation. The retained refusal/script documents
the correction: inspect head under admin first, with no added grants. Restricted-login
characterization then passes with exact SET-edge restoration. New reference SHA256:
43bf6d868efb7234ebd8199d884f7cafcca018a2fd274df6329187381a6827f3.

Affected regression and independent reviews follow. Both composer --check-only routes
exit0. Approved dependencies, including TypeScript7.0.2, remain unchanged. No root-wide
npm test/build claim.


## Final reviewed-source acceptance

Final retained frame: platform/deployment/.local/identity-baseline/member-binding-reviewed-zpge73fv/.
Complete actual matrix PASS29.541s, source unchanged;19 recorded stages include unchanged10
characterization bound to proof/run/fixture digest and exact transitions. Distinct member
rows and unused bigint-safe derived ID are verified before writes. NULL/two/all binding
changes reject atomically on active/retired rows. A data-dependent modifying CTE ensures
a permitted update is processed before binding rejection in the same statement; complete
member/role/audit state remains. Retired legacy-role/token/current-account readers deny.
Every matrix row executes and passes; only the guard body changes in function comparison.
Actual clean/adopt/exact10/repeat, injected failure/rollback/recovery and drift refusal
pass; unknown history remains a rollback-only same-connection owner-preflight check.
Exact role/failure-fixture restoration passes; new11 SQL/reference/pin unchanged.

Full affected suite **649 PASS29.76s, no skips**:
`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider`.
OWNER_PYTHON is the frozen interpreter at platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python.
Both `tools/py/run_compose_supabase.py --check-only` and
`--identity-authority owned --check-only` exit0; whitespace check PASS.

Three independent reviews complete: Blind10, Edge1, Verification0. Eight correction
groups (including final documentation) are verified. Two low extensions were rejected:
a privileged cross-connection max-revision fixture and concurrent live migration/writer
qualification. Existing owner-only overflow fixture is explicit; supported source branch
is unchanged and role-independent. Controlled migration-before-activation remains
binding, with no hot live-cutover claim. No new locking/recovery framework or deferral.
Five impacts remain as above.

Normal retained-data stop, preservation/private-output checks, final source manifest
and scoped local commit receipt complete the frame. All2641 protected originals remain,
seven intended existing files change, and original concurrent Scribeswell/Expense/
brainstorming/spec work is preserved. All earlier failed frames, source references,
receipts/state/data/resources remain. Full ID-B/Access/WRITE/KDG readiness is not claimed.

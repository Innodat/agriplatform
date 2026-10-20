# ID-B additive actor persistence evidence

2026-10-20; baseline e4723c5ca371df01779af3964d306d0fcd38bc0c.
This bounded increment adds the two selected durable actor tables through Identity's
existing migration history. It does not provision real identities or expose a runtime,
operator command, actor UI or authorization capability. ID-B as a whole remains open.

## Requirement to executed verification

| Requirement | Actual evidence |
| --- | --- |
| Clean owner route and unchanged retry | identity_migrator LOGIN runs both revisions to identity_0002; clean/current and populated repeats pass exact catalog verification |
| Verified equivalent legacy adoption | Pinned legacy source fixture, original six-entry Supabase ledger, Identity rows and finance/CS FK values/definitions survive adoption; scoped access_runtime reads/denials remain |
| Previous release compatibility | Exact prior committed owner code establishes identity_0001 on three fresh cases; existing row/reference fixture survives upgrade; previous scoped consumer query still works |
| Durable accountless actors/mapping | Explicit self-attributed system, service and account actors; account-kind mapping without Auth/person/org rows; no external FKs |
| Structural validation | Invalid kinds/nil IDs/blank or excessive labels/invalid ASCII keys, service-kind mapping and duplicate account/actor mapping all refuse in rolled-back transactions |
| Stable attribution and retention | Actor ID/kind/assigned key/creation actor/time mutation, mapping update/delete, actor delete and both-table/mapping TRUNCATE refuse; first key assignment/label update server-stamps updated time |
| Restricted privileges | anon/authenticated/service_role/supabase_auth_admin/access_runtime have no raw new table or guard-function privileges; actual access_runtime LOGIN SELECT/INSERT attempts deny; no synthetic organization/grant created |
| Failure and unknown state | Synthetic database-local event trigger fails account_actor CREATE after actor CREATE; whole migration rolls back with old ledger/catalog/rows unchanged; reconciled retry succeeds; unexpected ACL and unknown revision refuse unchanged |
| Source preservation | Original revision1, baseline reference, seven source pins and owner dependency lock remain byte-identical; new fixed reference separately pins revision2 bytes |

`services/access/tests/test_identity_baseline.py` first observed four expected missing
implementation failures and fifteen characterization passes. The canonical locked owner
interpreter repeated RED, then GREEN. Its final owner/composition/coordinator pytest
run passes **35 tests**; both legacy and owned composer check-only commands pass.
The original PostgreSQL format-token execution failed before a server SQLSTATE;
compiled SQL regression observed RED then GREEN and actual recording succeeds.

## Exact artifacts and commands

Private synthetic proof directory:
`platform/deployment/.local/identity-baseline/actor-foundation-6d80e9c7/`.
It uses the existing native disposable run99b7231c-0a5b-4bdb-98e8-3329564c526a,
with six fresh `actors_` scratch databases; all prior databases/resources are retained.
The native lifecycle is the ordinary existing Supabase CLI wrapper, not individual
container interception. Credentials remain private fixture input, never argv/evidence.
All prepared DB/API URLs pass the existing run/namespace/port guards before connecting.

Canonical interpreter:
`platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python`.
Its prior independent frozen offline owner environment remains the authority; unchanged
uv.lock selects Python3.15.0, SQLAlchemy2.1.4, Alembic1.20.0, Psycopg3.3.6, pytest9.1.1
with uv0.13.1. No new dependency selection, installation or TS change.

With IDENTITY_QUALIFICATION_DIR set to the proof directory:

- `OWNER_PYTHON -I -B services/access/tests/qualify_identity_baseline.py --record-actor-reference`
  independently executes known sources/integration/new DDL rollback-only, verifies the
  old catalog before new DDL and clean eligibility after rollback, and publishes exclusively.
- `OWNER_PYTHON -I -B services/access/tests/qualify_actor_foundation.py`
  runs the actor matrix. `identity-qualification.json` records exact migration argv,
  expected refusal codes, log hashes and results. `previous-source.json` binds the
  private previous-owner copy and launcher to the exact baseline commit.
- The initial proof reached an extra postgres-denial assertion. Read-only investigation
  showed the vendor administrator already inherits pg_read_all_data and migration-owner
  membership. That is outside the ordinary runtime contract; the expectation was corrected
  without changing administrator roles or weakening browser/service denials. The safe
  observation is retained. `continue-actor-proof.py` reruns structural tests with unique
  synthetic keys, then completes the remaining matrix; `additional-structural-checks.py`
  adds actual truncation/function ACL/external-FK assertions.
- `focused-checks.py` records exact owner pytest and both composer commands/results/hashes
  exclusively into this new proof directory, preserving earlier verification receipts.

The initial additional generated actor reference SHA256 was
10d6174506ff1a6b0a87ae94036da5b08397a197cacee108d041fa77e20a3109.
The reviewed replacement is recorded below; original ID-A reference remains unchanged.
The reference includes revision2's exact
migration digest and normalized category fingerprints; no target self-approval/bypass.
The first failed recorder's safe placeholder diagnosis remains in reference-failure.json;
its database transaction rolled back. Current successful checks do not erase that failure.

## Limits and impacts

Auth's legacy profile hook/source remains unchanged and creates a profile on the scratch
Auth insert path after upgrade. This is separate from prior native Auth API/hook proof;
no fresh password/provider/JWT-pipeline sign-in claim. Existing membership semantics,
old consumer roles and application references remain. Registry existence is not live
account verification; explicit classification, legacy UUID/text adoption, protected
execution binding, outcomes, membership changes, runtime projections and Access remain
later delivery gates. No real accounts/provider/access settings or deployment changed.

Scaffold: owner-local migration/fixture remains unpromoted. Shared UI: none. Agent
context: existing rules suffice, no edits. Documentation: owner runbook, this evidence,
mutable ownership inventory and KDG navigation. ADR:0020/0025/0056 govern; no accepted
ADR changes or new architecture decision. No second generator/service/release runner.

## Reviewed completion

All three review layers completed; twelve findings received individual triage rows,
with nine patch groups and no deferred implementation. The direct Unicode White_Space
CHECK correction follows a real rolled-back NBSP/EM SPACE acceptance RED. The foreign
recorder-file regression also observed RED, then GREEN. Recorder cleanup preserves
another invocation's temporary; interrupted publication recovery remains explicit
preservation/independent source regeneration, never target approval.

Fresh reviewed proof is `platform/deployment/.local/identity-baseline/actor-reviewed-0fd08827/`.
Its additional reference SHA256 is
c83985f3761cbac85666118fdbbd140d324a424a031baea69b6f174d4585cd1a.
The initial reference bytes, diagnostic frame and every earlier receipt remain retained.
One complete execution of the committed `qualify_actor_foundation.py` passes without
continuation on this new six-case frame. `complete-execution.json` records its exact
command/environment/result; the cumulative identity journal includes all migrations,
refusals and the final actor-foundation-matrix result. Previous owner code is now
independently checked against historical Git objects, including rejection of changed
or extra files; the launcher is committed in the runner, not a private supplied script.

Actual additional assertions prove server insert metadata overrides, no-op last-change
preservation, missing attribution FKs, valid 200-multibyte-code-point/128-ASCII boundaries,
invalid/duplicate keys and Unicode blank refusal. Two real owner connections demonstrate
the losing mapping insert blocks on the winner, then fails SQLSTATE23505 after winner
commit, preserving only the winning mapping. All waits are bounded.

Final **40 focused tests** and both composer check-only commands pass; exact argv,
results and log hashes are in the reviewed frame's focused-checks.json. Final source/
preservation audit confirms all2550 unrelated pre-existing files and original ID-A
migration/reference/source pins/dependency lock unchanged. The synthetic project is
normally stopped with databases and Docker resources retained. No full ID-B or KDG
readiness promotion, production migration or account/provider action occurred.

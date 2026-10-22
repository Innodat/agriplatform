# Staged organization grant lifecycle storage

Access0010 is an additive owner migration after exact9. It adds organization-only
scope, positive bigint revision (default1), nullable revocation time and nullable
external actor/update provenance. Existing rows gain organization/1/null; no actor,
time or membership is inferred. Original IDs, legacy text creation attribution,
historical creation times, permissions, membership values, indexes, forced RLS and
ACLs remain. Supplied actors must be nonnil and supplied new times finite.

This storage does not execute grant.assign, verify references or activate effective
access. No permission/Identity FK or final effective-row constraint is added. Existing
owner writers remain supported; runtime stays SELECT-only under organization RLS.
Operator and command owners receive no grant writes. ACCESS-A/B and consumers stay gated.

Use the existing controlled Access owner route, with a protected
ACCESS_MIGRATION_DATABASE_URL and the owner environment's locked Alembic dependency:

```sh
python -I -B -m alembic -c services/access/alembic.ini upgrade head
```

The route verifies exact known clean/1–10 catalogs/history before effects and exact10
before commit. Unknown history, columns, constraints, functions, ACLs or RLS refuse
without normalization. Keep current source, logs and old proof. Held owner lock or
failed postcondition rolls back the entire migration; inspect the retained state,
resolve the cause, then explicitly rerun the controlled upgrade. Never downgrade or
repair unknown state automatically. Real deployment and activation are excluded.

Synthetic qualification reuses the private four-group native owner fixture protocol
and root preparation, source custody and baseline previous-source package. It performs
no bootstrap. Root also supplies protected mode0600 `runtime-credential.json` with
exact shape `{"password": "<existing restricted runtime password>"}`. This auxiliary
input reuses the existing access_runtime credential and is read through protected file
helpers; it changes neither the four-group fixture nor roles/secrets. Its digest is
bound into preparation source custody. The previous-source package must match the
reviewed baseline7a565562 and the fixed canonical79-file inventory SHA256, as well as
each source file's digest. Use a freshly prepared private ACCESS_QUALIFICATION_DIR for
one --all:

```sh
python -I -B services/access/tests/qualify_grant_lifecycle_storage.py --all
python -I -B services/access/tests/qualify_grant_lifecycle_storage.py --verify-retained
```

The second command is separate read-only retained inspection and explicitly requires
Access0010 in every case. Before database inspection it verifies preparation source/log
custody and the final aggregate-generated log digests recorded in results.json. These
cover controlled migration logs, Identity repeat/drift evidence, previous9 compact
receipt logs, injected-postcondition output and CLI execute JSON. Missing, altered or
additional matching aggregate logs refuse; root stdout and independent inspection logs
are excluded so root can retain subsequent observations. Previous9 child failures save
only selected class/SQLSTATE/returncode; successful output is validated compact receipt
JSON. Raw child SQL, stderr and tracebacks are discarded.

Repeated --all refuses; changed sources or bound logs refuse; failures retain unique
safe frame diagnostics. Never
reuse or reset old/failed proof frames. Root owns native preparation, execution, stop
and evidence. See [delivery evidence](GRANT_LIFECYCLE_STORAGE_EVIDENCE.md).

Requirement-to-test mapping: test_grant_lifecycle_storage.py checks exact version
recognition, unchanged9 command SQL, DDL closure and Identity metadata-only9/10 selection.
The native qualifier proves fresh10, populated9 upgrade and old adapter replay/lookup,
all legacy permissions/opaque attribution, null/valid/max fields, named constraint and
whole rollback failures, runtime RLS/write denial, operator/definer denial, drift,
held advisory and grants relation locks/injected failure/forward recovery, current
command regression, committed staged-column/constraint/ACL drift refusal through actual
restricted Identity19, explicit fixture restoration, Identity19 repeat, custody, single-use execution and separate retained inspection.

Impact decisions: the owner migration/verifier and existing qualification scaffold
are extended in place; shared UI and agent context need no change; this runbook,
evidence and existing substrate/handoffs carry documentation; no new or changed ADR,
generator, dependency, runtime service or new tooling framework is required.

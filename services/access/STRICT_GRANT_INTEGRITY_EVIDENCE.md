# Strict organization grant integrity —2026-10-22

The user confirmed PtS is not used and can adopt the target infrastructure. ADR-0052
already makes legacy PtS API/org-grant compatibility a non-requirement. Access0012
removes the unnecessary0011 bridge: direct (permission,scope_kind) RESTRICT FK to the
permission registry and global active membership/actor/update completeness. All three
old PtS literals receive the same constraints. No automatic permission registration,
org-to-account grant conversion, business DML, backfill or deletion is performed.

This is the organization storage foundation. Protected assignment, typed account grants/
checks, membership-safe effective readers, ACCESS-B and coordinated PtS/Content/corpus/
KDG activation remain later existing-owner delivery. PtS corpus assets are preserved.
Current protection stays until coordinated replacement; no interim bypass is introduced.
See [ADR-0052](../../platform/docs/architecture/decisions/0052-pts-account-scoped-access-and-coordinated-adoption.md)
and the [PtS transition contract](../../apps/pts/docs/architecture/contracts/account-access-and-corpus-transition.md).

## Acceptance and preservation

Baseline311ea6d9a7b3bfd761773cdf87c11d69ca912fb6. Root snapshot
/tmp/strict-grant-preservation.json records concurrent observed bytes,76 production
sources and53 historical migration/reference files. Immutable Access0–11 and Identity
history/references stay unchanged. Only the intended mutable verifiers plus new0012
change production source. Concurrent documents may evolve and are excluded from commit.
All older synthetic frames/data/resources remain retained.

Focused acceptance RED failed4 missing-feature checks. Before production edits, root
fresh strict-grant-red-20261022 installed controlled11 and observed an unregistered,
incomplete pts.poetry.read grant accepted under the exemption. Explicit transaction
rollback preserved the complete snapshot. Expected exit1 and exact safe output are bound
in strict-grant-20261022/root-acceptance-red.json. This demonstrates the removed behavior.
A rollback-only temporary table measured PostgreSQL's dropped text-column tombstone at
slot14; exact12 verification must admit only that native shape and reject extra drops.

## Delivery impacts

Scaffold: extend existing owner migrations/verifiers/qualification, no second generator
or service. Shared UI: none. Agent context: none. Documentation: owner runbook/evidence,
mutable substrate/deployment/KDG handoff. ADR: existing0052 supplies simplification
and account-scope authority; release safety, structural integrity, attribution and safe
logging decisions stay binding. No accepted ADR change. TypeScript7.0.2/dependencies
unchanged; existing owners retain schema/client/generator/test/runbook work.

Only isolated synthetic implementation/verification is authorized. No real account/access,
production migration, infrastructure provisioning, deploy, pilot, Leave/editor, reset/prune,
historical cleanup or push. Normal stop preserves volumes/data. Controlled schema DDL
may take locks; bounded synthetic proof is not production sizing/zero-downtime evidence.
Private bootstrap still consumes dated retained credentials/run/config. This existing
preparation dependency is documented rather than represented as portable CI delivery.

## Requirement to test evidence

| Requirement | Native method / focused evidence |
| --- | --- |
| Clean12 and compatible populated11 preserving original13 values, opaque creation history and five command receipts | prepare_cases, upgrade |
| Direct registry enforcement without PtS/account exemption, INSERT/UPDATE active/revoked | functional: named grants_permission_scope_fkey/23503 |
| Each required active field, including each old PtS literal; partial revoked values and denied revival; positive/nonnil/finite safeguards | functional: named grants_active_fields/23514 plus prior constraints |
| Alternate/dependent CTE/multirow and transaction rollback | functional: valid dependent first write followed by named FK failure, exact snapshots |
| Incompatible aggregate11 retains original data/catalog/history | refusal: three unregistered PtS literals, active/revoked; no individual later-row causation claim |
| Existing restricted runtime RLS/select-only and operator/definer write denials | privileges using actual restricted logins |
| Exact schema/history/ACL/both FK ends/expected tombstone and extra-drop refusal | drift and exact verifier |
| Identity19 genuine repeat11/12 and metadata-only damaged marker/ACL refusal | upgrade, refusal, drift; focused metadata selector test |
| Bounded relation/advisory contention, injected postcondition rollback and explicit forward retry | failure_and_locks |
| Frozen source/input/log/state custody, single-use aggregate and independent read-only inspection | shared main, retained and focused custody safeguards |

Focused55 checks pass. Root affected regression passes1484 tests in53.30s; both
composition modes exit0. Pre-review native/retained PASS is recorded below; final reviewed results follow.


## Pre-review native acceptance

Fresh strict-grant-proof-20261022 passes all8 native stages. This is distinct from final
reviewed acceptance. Generated aggregate logs and retained state are frozen under that
private frame; root stdout remains in strict-grant-20261022/root-all-proof.log. An
independent read-only retained invocation follows. Production source stays frozen for
this proof. Previous failed/successful frames remain historical and are never relabeled.

Exact root commands, from repository root:

```sh
P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
F=platform/deployment/.local/identity-baseline/strict-grant-proof-20261022
D=platform/deployment/.local/identity-baseline/strict-grant-20261022
$P -I -B "$F/bootstrap_run.py" > "$D/root-bootstrap-proof.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B "$F/root_qualification_driver.py" > "$D/root-all-proof.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B services/access/tests/qualify_strict_grant_integrity.py --verify-retained > "$D/root-retained-proof.log" 2>&1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $P -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
$P -B tools/py/run_compose_supabase.py --check-only
$P -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

The bootstrap/aggregate are single-use. For changed sources use a fresh frame, not
another invocation on existing state. The root driver calls the same qualifier main
and emits only selected safe exception class/SQLSTATE/location on unexpected failure.


Independent --verify-retained exits0. Root custody inspection confirms120 source bindings,
28 owned generated-log/diagnostic bindings and retained-state digest, with53 historical
files and74 unchanged production/client sources preserved. Only2 intended mutable
verifiers change plus new0012. Frozen intent hash matches. Review lenses are sequential
under the available thread limit; all must complete before triage/final acceptance.


## Independent review

Three lenses completed sequentially due available agent capacity. Edge-case and
verification-gap lenses returned no findings. Blind review returned10 suggestions:
one rejected as already accurately scoped aggregate proof, one rejected as low-value
additional concurrent-writer machinery before a runtime writer exists, and8 direct
proof/document corrections in7 groups. These cover registered-but-incomplete legacy
upgrade refusal, a second registered capability and successful permission transition,
complete revival, revoked provenance updates, every FK enforcement trigger, and explicit
pinned-native-catalog/full logical schema restore limitations. No production DDL/verifier
change follows. The exact per-finding verdicts are in the bounded spec.

The supported recovery proven here remains transaction rollback and explicit controlled
forward retry. Full logical schema dump/recreate loses physical dropped-column slots
and does not currently satisfy this exact verifier. No backup/restore qualification,
manual catalog repair or production recovery success is claimed. Future release recovery
must obtain its own evidence before relying on an unqualified restoration arrangement.


Review corrections are implemented. Final strict-grant-final-20261022 uses the same
six fresh cases. Refusal records its aggregate unregistered snapshot before deliberate
owned synthetic transitions: explicit legacy permission registration and revocation
isolate exactly one active row missing each required field. This is adversarial test
setup, not production adoption or an automatic migration behavior. Each attempted
upgrade preserves exact11 before/after; transition snapshots are stored in
refusal-fixture-transitions.json and bound in generated-log digests. Other cases preserve
two registered organization capabilities, successful permission update/revival, revoked
field removals and every one of four FK trigger-disable probes. Production0012 and both
mutable verifier bytes remain identical to pre-review passing proof. Focused12 checks
pass after review; final native/retained/regression results follow.


## Final reviewed acceptance

Fresh final frame passes all15 recorded native stages, followed by a distinct successful
read-only --verify-retained. All120 source bindings,33 owned generated-log/selected
transition diagnostics and retained-state digest match; refusal transitions are included.
Use the earlier exact commands with F=strict-grant-final-20261022 (full parent path as
above) and root output suffix-final. No earlier proof is relabeled. All eight direct
review proof/document corrections are addressed; no new deferral. Production DDL and
both verifier hashes remain identical to the pre-review proof. Final regression,
composition, normal stop and scoped commit follow below.


Final affected regression:1484 passed in48.67s, no skips. Both composition checks exit0;
root-regression-final.log and root-compose-{default,owned}-final.log are retained in D.
Normal stop uses prepared P -B platform/deployment/dev.py stop --target
platform/deployment/environments/kdg-local.json --run-id
99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase followed by the pinned absolute
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase
binary. root-native-stop.log records the result. Final private root-final-evidence.json
binds all owned source/docs, historical/current production inventories, frozen intent,
120 source/33 generated diagnostics and state digests, supplemental RED/bootstrap/stop
proof and concurrent observed bytes; it records the scoped local commit afterward.
No reset/prune, source-history rewrite, real-target adoption or push occurs.

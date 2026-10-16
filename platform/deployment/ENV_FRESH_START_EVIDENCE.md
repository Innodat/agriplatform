# ENV fresh-start admission and branch proof

2026-10-16. Existing ENV owner item selected through bmad-help/bmad-build with
ATDD/focused TDD. [Build record](../../_bmad-output/implementation-artifacts/spec-env-fresh-start-admission.md)
and [runbook](DEVELOPMENT.md) retain scope. Runtime readiness remains false.

## Problem and bounded correction

The existing joint resource acquisition creates a database volume before constructing
CLI startup. The pinned CLI first checks whether that volume exists and uses that
observation to choose fresh setup. Pre-acquisition therefore selects existing-volume
behavior. Primary authority: pinned
[start-database.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/start-database.ts#L130)
and [container-lifecycle.ts](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/container-lifecycle.ts).

The guarded initial invocation constructor must observe absence before mutations,
leave the volume uncreated, and recheck absence before handoff. Existing or ambiguous
volume state cannot authorize reuse. Metadata acquisition remains a separate existing
adapter. The private pinned-CLI fresh fixture models an accurate absent probe, exact
synthetic volume-create acknowledgement, immutable PG request, root-key transfer and
refused first start. Expected volume profile and observed metadata are distinct.

This does not reserve a name or prove volume contents/initialization, owner bootstrap
SQL, secret provisioning, real startup or runtime readiness. No real Docker resource,
container, image layers, SQL, access/account or infrastructure change is performed.

## Required impact decisions

- Scaffold: fix the existing ENV invocation/resource ordering and extend its current
  private qualifiers; no second generator, runtime service or readiness workflow.
- Shared UI: no user-facing UI or reusable UI change is involved.
- Agent context: existing ownership, ATDD, release and sensitive-log rules suffice;
  no root/generated instruction changes.
- Documentation: existing profile/lifecycle authorities, runbook, this evidence, Build
  record and KDG handoff/memlog record verified scope and remaining gates.
- ADR: existing ownership/isolation/log/release decisions apply; no accepted ADR edit
  or new architecture decision. No production migration or activation is introduced.

## ATDD RED

Before production edits, root ran:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py' -k fresh_invocation_leaves_volume_absent
```

One test failed, exit 1 in 0.294s: volume.present was True after invocation construction,
when the required initial-start path must leave it absent. The first attempted fixture
RED instead failed on missing test bin-directory setup; that setup error is not
behavioral acceptance evidence and was corrected before production implementation.

The corrected fixture test then ran before production edits:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_startup_adapter.py' -k fresh_fixture_rejects_preacquired_volume
```

One test failed, exit 1 in 0.005s, `Refusal not raised` at line36. Both meaningful
acceptance failures were observed before implementation.

## Requirement-to-test evidence

| Requirement | Independent test or control |
| --- | --- |
| Leave volume absent, exact ordering and one connection | `test_fresh_invocation_leaves_volume_absent`; resource `fresh` exact 28-event oracle |
| Existing/foreign/error/late state refuses before handoff | `test_fresh_existing_ambiguous_and_late_refuse`; resource fresh negatives |
| Exact404 alone admits; no adoption | `test_require_absence_only_accepts_exact_missing_status_without_metadata_adoption` |
| Lost/truncated/EOF transport never reconnects | `test_fresh_transport_loss_at_every_exchange_refuses_without_reconnect` |
| Changed source/target/receipts/lock; budget and post-owner checks | `test_fresh_custody_changes_before_network_mutation_and_constructor_refuse`; `test_fresh_total_budget_and_constructor_postchecks_refuse` |
| No pre-acquired input; planned/observed states distinct | `test_fresh_fixture_rejects_preacquired_volume`; `test_public_fresh_controls_bypass_volume_acquisition_and_observation`; `test_fresh_planned_metadata_and_boolean_states_are_closed` |
| Pinned CLI fresh sequence and exact refusal boundary | `test_fresh_exact_missing_create_copy_refused_start_sequence`; public `fresh-lifecycle-positive` |
| Wrong/duplicate/reordered create/copy/start, existing/racing volume | `test_fresh_wrong_duplicate_missing_and_reordered_volume_creation_refuses`; `test_fresh_existing_and_racing_volume_refuse_without_ack_or_pg_create` |
| Negative controls require valid original baseline | `test_fresh_expected_volume_refusal_requires_complete_original_prefix`; `test_invalid_baseline_cannot_qualify_negative_controls` |

The first resource suite ran 23 tests in 84.112s and exposed three failures plus one
error: the legacy acquisition-negative loop incorrectly included fresh-invocation
controls. Its dispatch now retains the old acquisition set; the independent fresh
invocation assertions and expected refusal codes stay unchanged. The corrected legacy
matrix passes1 test in 2.419s. Volume suite passes 29 tests in 10.644s.

## Remaining gates

Absence is not reservation. The synthetic CLI create uses two CLI labels, which do
not establish the planned six-label ENV ownership profile. Guarded live creation,
execution-time continuity, initialized-volume/reuse policy, bootstrap/secret and SQL
semantics, actual health/stop/reset/recovery and generated P1/SERVICE acceptance remain
open. The fresh fixture does not claim SQL executed or contents are fresh. Dependent
Identity/Access/WRITE and KDG delivery stay gated.

Startup adapter passes 40 tests in 5.341s; complete lifecycle suite passes 18 tests in 57.979s.

The execution environment restarted during the first broad regression. Temporary logs
and process state were lost; that interrupted run supplies no passing evidence. The
repository edits and earlier focused results remained available. Final verification
is rerun after review patches. Three review lenses reported ten finding instances:
eight bounded fixes (including final evidence), two disproved; none deferred.

Review RED, before production patches:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_startup_lifecycle.py' -k fresh_planned_volume_rejects_unknown_metadata
python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py' -k fresh_invalid_workdir_refuses_before_daemon_mutation
```

The first ran 1 test in 0.019s, failed `Refusal not raised` for Mountpoint, followed by
an assertion-context setup error; the test assertion was placed inside its subtest
without changing the expected refusal. The second ran 1 test in 0.294s and failed because
a POST occurred before the invalid workdir refused. Both demonstrated behaviors precede
the corresponding production fixes. Fresh bridge replacement/image/daemon/network,
existing/conflict-winner and actual-constructor-input checks extend review coverage.

Review patches retain the original API surfaces. `startup.check_workdir` now runs
before daemon connection and again through the final constructor. Fresh fixture
validation checks the original planned object, including exact keys/types, before
metadata projection. The private resource qualifier captures real constructor
inputs and compares target/run/full bridge descriptor with its independent oracle;
it no longer derives the network proof from fabricated expected output.
The two synthetic proofs remain separate: no continuous constructor-to-live-start
execution is claimed. That future integration is an explicit runtime gate.

Final complete resource suite after review patches:28 tests PASS in 76.952s.
Command: `python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py'`.
The new matrix covers late child/config observations and each final bridge ID/name/ID
replacement, existing/conflict winner ownership, image/daemon/network refusals, invalid
workdirs and changed constructor inputs despite plausible output.

Complete post-review lifecycle suite:19 tests PASS in 63.664s.
Command: `python3 -m unittest discover -s platform/deployment/tests -p 'test_startup_lifecycle.py'`.
Fresh source-bound run: `d824e14c-5e70-408b-844d-490146e313c2`.
Preparation returns `prepared`, exit 0, runtime readiness false.

Preparation and qualification commands for the final run (all exit 0):

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id d824e14c-5e70-408b-844d-490146e313c2
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id d824e14c-5e70-408b-844d-490146e313c2
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id d824e14c-5e70-408b-844d-490146e313c2
```

They return `prepared`, `toolchain_qualified` and `base_images_qualified` respectively;
all retain `runtime_ready=false`. No image layers are pulled.

Review coverage also ran the complete fresh image/daemon/network refusal matrix,
existing/conflict bridge winners and independent exact constructor target/run/network
checks. Each final bridge ID/name/ID observation has a late-replacement case proving
`network_replaced` before construction. Root inspected the patched production and
qualifier diff; the immutable intent and existing acquisition implementation remain
unchanged. Syntax parsing, scoped whitespace and local Markdown link targets pass.

## Final public CLI qualification

All fourteen focused public checks passed on the final source-bound run. Every
result retained `runtime_ready=false`; positive startup controls reported no container
execution and unqualified SQL semantics. Safe-output canaries and the exact expected
exit/code were checked. All thirteen retained files matched their original hashes,
inodes, modes and modification times; preparation/startup source snapshots also matched.

```sh
python3 /tmp/env-fresh-start-public-proof.py d824e14c-5e70-408b-844d-490146e313c2
```

The temporary root orchestration invokes only these existing public entrypoints,
with `--target platform/deployment/environments/kdg-local.json --run-id
d824e14c-5e70-408b-844d-490146e313c2 --control <case>`. The protected JSON record retains
each exact command, result and evidence snapshot; no second delivery tool is introduced.

| Entry point / control | Exit | Expected code |
| --- | --- | --- |
| `qualify_resources.py` / `fresh` | 0 | `resources_synthetic_qualified` |
| `qualify_resources.py` / `fresh-existing` | 2 | `volume_reuse_unsupported` |
| `qualify_resources.py` / `fresh-foreign` | 2 | `volume_reuse_unsupported` |
| `qualify_resources.py` / `fresh-error` | 2 | `volume_inspection_failed` |
| `qualify_resources.py` / `fresh-late` | 2 | `volume_reuse_unsupported` |
| `qualify_resources.py` / `positive` | 0 | `resources_synthetic_qualified` |
| `qualify_startup.py` / `fresh-lifecycle-positive` | 0 | `synthetic_boundary_proven` |
| `qualify_startup.py` / `fresh-existing` | 2 | `expected_fresh_volume_rejected` |
| `qualify_startup.py` / `fresh-racing` | 2 | `expected_fresh_volume_rejected` |
| `qualify_startup.py` / `fresh-invalid-lifecycle-target` | 2 | `expected_lifecycle_rejected` |
| `qualify_startup.py` / `fresh-invalid-lifecycle-archive` | 2 | `expected_lifecycle_rejected` |
| `qualify_startup.py` / `fresh-invalid-lifecycle-order` | 2 | `expected_lifecycle_rejected` |
| `qualify_startup.py` / `positive` | 0 | `synthetic_boundary_proven` |
| `qualify_startup.py` / `lifecycle-positive` | 0 | `synthetic_boundary_proven` |

Protected local record: `.local/fresh-start-qualification/d824e14c-5e70-408b-844d-490146e313c2.json`.
SHA256: `d9a1409d4633b4c8b021cd7f675fca564fba2d1732f4532340b4abf77fecfcd2`.
The record is synthetic qualification evidence; it grants no runtime or resource
ownership authority. Fresh startup records eleven events ending at refused start;
existing refused-create records nine and existing lifecycle records eleven.

## Final regression and runtime gate

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py' > platform/deployment/.local/env-fresh-start-regression.log 2>&1
python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id d824e14c-5e70-408b-844d-490146e313c2
```

The complete deployment suite passes **416 tests in 333.443s**, exit 0. The workspace
log retains that result; its synthetic staging-run message is test-fixture output,
not evidence of an actual staging deployment. The real `up` check returns exit 2,
`docker_28_required`, `runtime_ready=false`, before runtime work. The supported-daemon
runtime-adapter gate remains closed as well. All fourteen public controls passed;
all eight review fixes are complete, two finding instances were disproved, none deferred.
No production migration, Docker resource/container, SQL, account/access change,
infrastructure provisioning, deployment or real-data pilot occurred.

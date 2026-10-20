# ID-B protected operator authority evidence

2026-10-20; baseline85b26f38dd66b5f1ac96854f82402c93f4a58700.
This bounded increment delivers principal/authority persistence and the private
original-login authorization read. It performs no provisioning, command effects,
receipt lookup, target preparation, outcomes/events, application access or deployment.
Later command/outcome routines must recheck current authority inside their short
transaction; returned metadata is never a durable authorization token.

## Requirement-to-test traceability

| Requirement / delivery matrix | Executed verification |
| --- | --- |
| Authenticated original login and exact/wildcard target | `qualify_operator_authority.py:restricted_reads`, actual identity_operator connection, exact account mapping, deterministic overlapping authority and distinct competing principal/executor |
| Closed command/platform/organization/target | Same actual matrix, unsupported/mixed/missing/nil inputs and other target/org return no row |
| Unmapped/disabled principal, disabled authority, current revisions | Same physical operator connection before and after controlled committed revocation/re-enable; no implicit authority from principal alone |
| Separate join_owner authority | Ordinary join row cannot authorize join_owner; explicit separate scoped row does |
| Spoofing resistance | GUC/JWT/temp/search_path spoof cannot change executor; SET ROLE into definer from migrator cannot impersonate operator session |
| Least privilege | Actual operator/runtime denied raw map/actor reads/writes, DDL, function replacement and definer/migrator assumption; browser/service role EXECUTE absent |
| Structural integrity and attribution | `structure`: NULLS NOT DISTINCT tuple uniqueness, invalid scope/nil/FKs, immutable tuple, forged insert revision/time/updater, changed-update attribution, server revision/time, no-op, atomic overflow, deletion/truncate retention |
| Safe owned migration | `upgrades_and_failures`: clean, legacy adoption, exact committed prior head4, repeat, unsafe role refusal, drift refusal, real external definer/sequence/PUBLIC table/staged-dependency refusal, injected write failure rollback and reconciliation |
| Source/reference custody | Rollback-only `--record-authority-reference`, captured prior/source identity and exclusive publication; manual new constant pin; prior references/revisions/locks retained |
| Preparation | Actual controlled administrator success with rollback-only probe names; nonsuperuser and existing-name refusal, unchanged role identities |
| Recorder and safe diagnostics | `test_operator_authority_qualification.py`: captured-source mutation, no auto pin/overwrite, prior reference chain, imported-helper custody, private publication, all-target validation, role guard and sensitive-error exclusion |

## Commands, targets and receipts

OWNER_PYTHON is the existing locked interpreter:
`platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python`.
Python3.15.0/uv0.13.1 and the Identity migration lock remain unchanged. The approved
TypeScript7.0.2 baseline is unchanged; no dependency or package installation.

The existing native Supabase CLI project/run99b7231c-0a5b-4bdb-98e8-3329564c526a
was resumed through `platform/deployment/dev.py up` with the explicit kdg-local target
and retained CLI2.120.0. All fixture databases are fresh, loopback/run/namespace-bound;
operator URLs are privately bound to the same database/port and exact operator login.
No credentials, command payload dumps or Auth verification documents enter logs.

Initial proof: `platform/deployment/.local/identity-baseline/operator-authority-pq17_n02/`.
Initial full-pass frame: `platform/deployment/.local/identity-baseline/operator-authority-final-gjsnxmdn/`.
Final reviewed frame: `platform/deployment/.local/identity-baseline/operator-authority-reviewed-p954m9yk/`.
All earlier frames and resources are preserved.

- Actual acceptance RED: access_runtime LOGIN on exact prior head4 receives SQLSTATE42883
  for the missing authority read; no writes (`actual-acceptance-red.json`). Exact command:
  `OWNER_PYTHON -I -B platform/deployment/.local/identity-baseline/operator-authority-pq17_n02/actual-red.py`.
- `OWNER_PYTHON -I -B services/access/tests/qualify_identity_baseline.py --record-authority-reference`
  with IDENTITY_QUALIFICATION_DIR selects the initial private frame, executes known
  sources rollback-only, verifies prior catalogs and publishes the new fixed fixture.
  New SHA256: `2f378cf2e9641bf60a84be4efda88c395a951c1032499d68c13fee878c13a81e`.
  Recording-source, rollback, exclusive publication and one-line manual pin receipts retained.
- `OWNER_PYTHON -I -B services/access/tests/qualify_operator_authority.py`
  with the final IDENTITY_QUALIFICATION_DIR executes actual role/structural/upgrade tests.
  Exact prior Git source is11 files from baseline85b26f3; unchanged code actually reaches
  head4 before new authority membership staging. Before/after staging metadata is retained.
- `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 OWNER_PYTHON -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider` covers affected owner/PtS regressions.
- Both `OWNER_PYTHON tools/py/run_compose_supabase.py --check-only` and
  `OWNER_PYTHON tools/py/run_compose_supabase.py --identity-authority owned --check-only`
  preserve their existing composition routes.

The first preparation used vendor postgres (nonsuperuser CREATEROLE), which acquired
extra automatic creator-admin memberships. Verification correctly refused. Root used
the existing qualified controlled administrator to correct only the two new synthetic
roles. Preparation SQL now refuses nonsuperusers before creating roles; the actual
success/refusal/rollback proof is retained. No verifier was relaxed.

The first actual structural frame is retained: PostgreSQL's inbound FK refuses a lone
principal-table TRUNCATE with0A000 before the retention trigger. The corrected test
characterizes that refusal and verifies23514 retention for the FK-complete two-table
TRUNCATE and standalone authority TRUNCATE. Guards and expected retention stay intact.

## Impacts and limits

Scaffold: existing owner migration/reference/qualification pattern, no generator or
shared runtime promotion before command consumers prove it. Shared UI: none. Agent
context: existing rules suffice. Documentation: owner runbook, evidence, delivery spec
and navigation/inventory. ADR: existing ownership, release safety, attribution and logging
decisions govern; no accepted ADR change or new architecture decision.

Only synthetic controlled configuration is exercised. This is not live operator adoption,
account/provider verification, effective application admission or a successful setup command.
Administrative configuration change/recovery evidence remains controlled deployment work;
this increment exposes no general authority-management API or complete audit workflow.

## Executed results

Initial full matrix:18 named PASS stages; initial affected suite272 passed. After review,
fresh full actual matrix: **24 named PASS stages**, including restricted-login, structural
and actual unsafe privilege submatrices. Final affected suite: **286 passed**, no skips. Both
composition checks and diff whitespace check: PASS. `actual-qualification-execution.json`,
`identity-qualification.json` and `focused-checks.json` retain commands/results/hashes in
the final frame. Preservation audit:2581 existing nonignored files, only eight intended
existing source/test/documentation changes, no unexpected changes. No original revision,
reference, pin, lock, runtime/seed or parser source changed.

Three independent BMAD reviews are complete. All12 findings were resolved through direct
checks/tests/documentation corrections; no deferred work. Reviewers launched as capacity
allowed, with triage after all reports. Actual rollback-only probes confirmed the two
external-privilege gaps before patching (`review-privilege-red.json` in the initial full-pass
frame). New checks refuse unapproved executable external SECURITY DEFINER routines and
non-system sequence USAGE/UPDATE. The exact canonically verified legacy public.get_user_roles()
read is retained and explicitly characterized; ordinary vendor invoker helpers remain
compatible. This does not finish the separately gated legacy membership/access hardening.

Updated recorder replay uses an ignored copy of the same owner sources (only its copied
pin set to None), current imported-helper digest/path checks and mode0600 publication.
Its generated reference is byte-identical to the repository reference; the repository
reference and trusted pin were never rewritten. See `recorder-replay.json` and retained
recording-owner-attempt2 source. First replay exposed a sequence predicate evaluation-order
error; CASE now guards has_sequence_privilege from nonsequence objects, and full actual
verification passes. Initial recording sources and unsuccessful attempts remain retained.

The native project is normally stopped with databases/data retained (`native-stop.json`,
exit0). No reset, prune or historical resource cleanup. Source-bound actual execution,
unit/composer logs and the final preservation audit are retained in the reviewed frame.

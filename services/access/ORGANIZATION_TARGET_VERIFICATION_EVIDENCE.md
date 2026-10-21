# Private Identity organization verification — 2026-10-21

Identity0019 adds `identity.organization_target(uuid)`, an account-free private point
check returning the exact existing nondeleted organization UUID or no row. It reuses
the existing target projection definer, selected-organization RLS and table privileges.
Only staged `access_command_owner` receives EXECUTE. Setup context needs valid nonnil
org/actor assertions, exact requested org and absent account context; these assertions
are trusted backend context, not independent authentication.

No organization is configured, no grant/admission is created, and no runtime API or
consumer is activated. Access remains at8 and configure execution remains closed.
Future execution must check exact current command/org/app authority before observing
Identity, outside write/retry locks; a new execution rechecks the observation.

## Verification and traceability

Actual preimplementation RED on retained exact Identity18 observed the missing routine
in `platform/deployment/.local/identity-baseline/organization-target-20261021/root-acceptance-red.log`.
Focused implementation RED:3 failed/2 passed; initial GREEN:5 passed. Later safe-failure and
review/ownership cases also observed focused RED before correction; final focused18 passed.

The existing `qualify_identity_baseline.py --record-organization-target-reference`
rehearses known historical sources and19 in a rollback transaction. Generated JSON
must never be hand edited. Historical migrations/references remain unchanged.
The first synthetic rehearsal refused `identity_target_role_unsafe` immediately after7;
rollback preserved the clean fixture. Diagnostics reported only safe codes/locations.

| Requirement | Verification |
| --- | --- |
| Exact account-free active org, invalid/mixed/missing context, pooled reset | read_matrix |
| Exact EXECUTE ACL, actual restricted logins, controlled NOLOGIN observations | privileges |
| Genuine previous18, populated identities/external FKs and protected command receipt preservation/replay | all / verify_retained |
| Routine/ACL/search_path/RLS/history drift refusal | drift |
| Injected failure, held lock, default-grantee stripping and forward recovery | rollback_and_defaults |
| Exact sources, generated reference, retained data | source_snapshot / verify_retained |
| No new table/role/policy grants; optimized interpreter refusal | test_identity_organization_target.py |

## Delivery impacts

Scaffold: extend existing controlled Identity migration/catalog/reference and owner
qualification tools; no new generator or generic service. Shared UI: none, private SQL
only. Agent context: no change. Documentation: owner contract, local runbook, this
requirement evidence and KDG handoffs. ADR: implements accepted identity/ownership,
release safety and short-transaction decisions; no new decision or accepted ADR edit.
Shared clients/schema generators remain with their existing owners. Dependencies,
including TypeScript7.0.2, remain unchanged.

Unknown history/catalog refuses without normalization. Preserve diagnostics/data,
resolve the cause and explicitly retry the controlled owner upgrade. No automatic
reverse, startup migration or activation on failure. Preparation/--all are single-use;
retained verification is read-only. No production migration, deployment, real-data pilot
or real account/access changes are authorized by this proof.

## Reference provenance and observed corrections

The known-source rollback recorder produced reference SHA256
`ac95baf560fd71eef4fa4867e45cc79fb22072c16ebb1dce80185bf524730235`,
migration SHA256 `beca1f2caacdf420cfa8d0dee8af00173beab8cc50fab02dd5bcae217d05dc9c`
and PostgreSQL routine definition SHA256
`cfeb0eda750962feb7e914e388d8c566bb9ae5f0a492395b3e73a25cd14b65b0`.
The source-bound generator receipt remains under the reference frame's
`identity-qualification.json`. Reference generation used None/empty pin placeholders;
final source-bound qualification uses the generated exact pins. These are distinct
source states, never relabeled as one proof.

The historical rehearsal rejection came from the pre10 token hook being compared with
the production Access whitelist's final hook. The recorder now permits only its exact
historical hash during known-source rollback rehearsal, authenticated by every immutable
whole-catalog reference; production whitelist checks are unchanged. It restores the
current hook immediately after10 and all process-local entries on failure/rollback.
The newly created19 function hash is admitted only inside that captured-source rehearsal
to produce its reference, then pinned for the normal controlled route.

The first full native frame passed the clean upgrade but its first synthetic Auth insert
refused42501: root created the fixture table as supabase_admin while existing helpers
use postgres. The failed frame is preserved. Fresh preparation restores synthetic database and
auth schema/table ownership to postgres; no global roles or native data change.
The first broad regression passed1325 tests with one failure in a historical test's
latest-head assertion. Historical18 verification is retained and19 gets explicit current
head coverage. No unexplained production behavior is redefined.

Independent blind and edge review both identified an incorrect qualification expectation
that runtime org SELECT should fail, despite its existing scoped bridge grant. The
correction preserves that read contract. Review also requested missing/other-active org
and absent-account cases, external-consumer preservation, actual helper source bindings,
controlled-route postcondition rollback and drift refusal evidence. All confirmed findings
are patched before final verification; the independent gap lens returned no findings.
The proposed nonexistent target-login fixtures were rejected: those roles are NOLOGIN,
and are explicitly distinguished from actual restricted-login observations.

## Reproduction commands

Run from repository root with the existing qualified interpreter. These commands
identify retained execution evidence, not permission to rerun consumed preparation.
New execution requires fresh synthetic namespaces and a new source-custody witness.
No credentials are committed; URLs stay in private fixture files.

```sh
P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
# Known-source rollback reference rehearsal, before pin finalization:
IDENTITY_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/organization-target-20261021" "$P" -I -B services/access/tests/qualify_identity_baseline.py --record-organization-target-reference
# Final independent source-bound frame:
"$P" -I -B platform/deployment/.local/identity-baseline/organization-target-accepted-20261021/bootstrap_run.py
IDENTITY_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/organization-target-accepted-20261021" "$P" -I -B services/access/tests/qualify_identity_organization_target.py --all
IDENTITY_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/organization-target-accepted-20261021" "$P" -I -B services/access/tests/qualify_identity_organization_target.py --verify-retained
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
"$P" -B tools/py/run_compose_supabase.py --check-only
"$P" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

The previous18 source package contains64 exact Git files from full baseline
`b6c8b22abbb4318cba452a308eef80d716718aa0`, independently compared with Git by root.
Its manifest and tree remain in the reference frame; the final fixture declares that
exact source directory. The qualifier runs actual old18 Alembic before populated
upgrade19 and actual Access8 compatibility checks, never relabeling current sources as18.

The next fresh frame reached context and all privilege checks, then its drift test
received42501 because the routine belongs to identity_target_projection_owner. The
qualifier now explicitly assumes that existing role only for synthetic routine mutation,
then resets and verifies identity_migrator before observing refusal. No privilege is
added. Its still-unused recovery fixtures were exercised separately as a diagnostic:
held lock, injected postcondition failure, default drift/stripping and all forward
recoveries passed. That diagnostic is not substituted for the final aggregate.

The final aggregate uses a private root diagnostic driver invoking the same main(--all),
with exception output limited to class, SQLSTATE and qualifier method/line. It is hashed
before and after execution. The normal CLI remains independently tested for safe failure.
Actual final aggregate invocation:

```sh
IDENTITY_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/organization-target-accepted-20261021" "$P" -I -B platform/deployment/.local/identity-baseline/organization-target-accepted-20261021/root_qualification_driver.py
```

The next aggregate exposed a no-op fixture mutation: identity.org already has
ENABLE RLS=true and FORCE RLS=false. NO FORCE therefore is not drift. The final
qualifier characterizes those actual flags, temporarily DISABLEs RLS and proves
refusal, then rolls back. The original policies/flags and projection-owner isolation
are preserved. No new forced-RLS requirement is invented. The frozen spec's existing-fact
wording is clarified outside its unchanged approval block.

## Final independent root results

Final frame: `platform/deployment/.local/identity-baseline/organization-target-accepted-20261021/`.
Fresh preparation custody passed; all15 recorded native stages passed, including expected
controlled refusals, followed by separate `--verify-retained` exit0. Actual previous18
rows/external references and protected receipt replay/lookup survived19 and repeat.
Actual Access8 compatibility passed both before and after19. All108 consumed source/input
bindings and the separately captured root-driver hash matched after verification.

Final affected regression: **1338 passed in57.52s**. Both composition dry runs exited0
without writes. Three review lenses completed; all confirmed findings are fixed and
verified. No new deferred issue; pre-existing bootstrap portability remains separate.
All48 protected migration/reference source bindings,82 previous-proof files and64 exact
previous18 Git files remain unchanged. The approval block hash remains
`bd6a9b0218e85529575a1da0abdb1905a4f777a086936a765dbde90327103405`.
Root's first stage-outcome audit assumed every row had status; existing command rows use
exit_code/expected_failure. The corrected audit accepts those existing receipt variants
and verifies all15 outcomes; this affected no implementation or database state.

The first stop invocation added -I to dev.py, hiding its sibling native_cli import and
failing before runtime effects. Its log remains. The corrected existing invocation exited0
with stage=stop, runtime_ready=false and retained data. Command:

```sh
"$P" -B platform/deployment/dev.py stop --target platform/deployment/environments/kdg-local.json --run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase /home/ck/repos/innodat/agriplatform/platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase
```

Final source/outcome/log/preservation identities are retained in root-final-evidence.json
inside the final private frame. Earlier reference, reviewed, final, verified and complete
frames are historical/failed evidence; none is represented as the final accepted source.
No Docker cleanup, reset or prune occurred. Concurrent source/documents were excluded
from the scoped commit rather than reverted. No push or consumer activation is included.

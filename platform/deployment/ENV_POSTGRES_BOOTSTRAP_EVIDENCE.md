# Selected PostgreSQL bootstrap qualification

Subsequent additive behavior: [bounded verified shutdown](ENV_POSTGRES_SHUTDOWN_EVIDENCE.md)
now requires clean stopped-state evidence before successful qualification and normal
removal. The original run results and scope below remain historical evidence.

Delivery: [Build specification](../../_bmad-output/implementation-artifacts/spec-env-postgres-bootstrap.md).
This is an isolated synthetic image/bootstrap proof. Full ENV/P1/SERVICE acceptance
and `up` runtime admission remain unfinished; `runtime_ready=false` throughout.

## Authority and isolation

The existing pinned CLI source profile supplies the exact 9,642-byte shell/SQL
fixture and four public synthetic environment values. The existing lifecycle owner
validates the one-member, in-memory public root-key archive before transfer.
See [profile authority](fixtures/supabase-pg17-profile.md) and
[key authority](fixtures/supabase-pg17-lifecycle.md).

The first two runs selected `public.ecr.aws/supabase/postgres:17.11.0.004`, Linux/amd64 child
`sha256:f2a84af37797675f0b27e27ea1fad2ebcd913ebf7ad60be05d7df0bcbd29e4b5`,
config `sha256:94fe95acfce6e1d41106ff2abd4c08e7932a6941d453499a56f8a620a473de1a`.
The image was downloaded by this child digest without tag substitution. Safe image
inspection confirms Linux/amd64, `docker-entrypoint.sh`, no declared volumes or
inherited labels. A format probe initially failed because the absent Volumes field
was addressed as a mandatory template member; the corrected optional lookup passed.

Two labelled, never-started disposable containers copied public image scripts for
inspection; each owned ID was checked and removal verified. Protected local public
source copies remain under `.local/postgres-source-audit/` runs
`2dbb8d67-baff-426c-8126-7221f992bfa8` and
`483ff02d-0e67-414b-9aa2-3c505c98071e`. They are diagnostic source evidence,
not generated fixture authority or credentials.

| Immutable image file | SHA256 | Observed semantics |
| --- | --- | --- |
| `/usr/local/bin/docker-entrypoint.sh` | `1a6ff568c79cb847cffc4172b22a1f501cef05001b0b09751f48323683fb64a2` | Fresh PGDATA initializes once; temporary server runs image init scripts before final server |
| `/docker-entrypoint-initdb.d/migrate.sh` | `eb6a57848a73dfbc3b8e40edbadcc7a933f1099ac62cef8c138a18115655b745` | Exports PGPASSWORD from POSTGRES_PASSWORD; runs post-init `/etc/postgresql.schema.sql` as supabase_admin with ON_ERROR_STOP |
| `/etc/postgresql/pg_hba.conf` | `a925911753f4975548eb4079177441c886aa22b6dd69f2b0cff98f779fb0b66a` | Local supabase_admin and loopback trust; other configured hosts use SCRAM |

The final bootstrap proof uses one fresh run-labelled container, network none, no ports,
no host binds, 2GiB memory with no added swap allowance, two CPUs,256 PIDs,
disabled Docker logging, and a 1GiB tmpfs database directory. These limits and the
log driver are checked in each owned observation. PostgreSQL's actual data_directory
must match the intended path and its filesystem must be tmpfs.
Copy/start/exec/removal require current ID/image/label/isolation checks.
Commands are bounded to ten seconds and 65,536 combined output bytes; initialization
has a 120-second total budget, followed by an independent ten-second cleanup budget.
Uncertain create has no replay, adoption or deletion. Failed cleanup reports unresolved
ownership/recovery rather than claiming success. Child stdout/stderr are never printed.

Image-owned initialization SQL necessarily creates PostgreSQL roles and system schemas
inside this synthetic disposable database. No repository owner migrations/seeds, app
grants/accounts, live Supabase resources or real data are used.

## ATDD and observed attempts

The first focused command was:
`python3 -m unittest discover -s platform/deployment/tests -p test_postgres_bootstrap.py`.
Root observed exit1 for missing explicit control; the implementation agent then observed
behavioral RED for missing `run_bootstrap` before implementing image-refusal behavior.
Focused TDD covers the matrix below. No existing expectation was changed to conceal an
unexplained failure.

Run `2dbb8d67-baff-426c-8126-7221f992bfa8` passed existing `dev.py prepare`,
`toolchain.py qualify`, and `images.py qualify` with explicit target
`platform/deployment/environments/kdg-local.json`. Its first sandbox preparation attempt
refused `port_unavailable`; the same command passed with authorized local socket access.
Actual `tests/qualify_startup.py ... --control postgres-bootstrap` exited2 with
`execution_failed_password_authentication` after the seven catalog verifiers matched.
Owned cleanup completed. The incorrect negative-password enforcement assumption was
investigated: immutable image HBA lines87–88 explicitly trust loopback. The test now
characterizes that source-derived behavior independently of password installation;
the exact image/bootstrap/environment remain unchanged. Earlier receipts are retained.

Fresh run `c86b126e-45a9-4254-a339-82e94f52f145` passed the same three existing
prerequisite commands. The unchanged explicit bootstrap control then exited0 in
30.603 seconds with `initialized=true`, all five SQL/key check booleans true,
`loopback_password_required=false`, `cleanup_verified=true`, `runtime_ready=false`.
All13 retained files (inventory, Supabase config, toolchain receipt and ten image
evidence JSON files) match their before hashes. Protected exact command/result/hash
record: `.local/postgres-bootstrap-qualification/c86b126e-45a9-4254-a339-82e94f52f145/result.json`,
SHA256 `1aeef80decd782e59fc5fb985b9ab7f7daad0dfc622eafd14ebda53b30ddda29`.

The entire running inventory did change: `deals-core-20261015-db` and
`deals-core-20261015-redis` appear only in the before snapshot. No command in this
qualification targets either; their concurrent stop cause was not independently
observed. All other before entries retain name/ID/image/running state. No claim
that every shared-host workload stayed running is made; preserve their current state.
This inventory is not a complete health/configuration/data comparison.

Focused command above: **19 tests PASS, 0.231 seconds** after the source-informed
authentication correction. `python3 -m unittest discover -s platform/deployment/tests`: **448 tests PASS, 278.610 seconds**, with authorized isolated local sockets/subprocesses. The emitted staging-run42 message comes from test fixtures; no staging deployment occurred.

During final post-review qualification, the publisher moved the same approved
`17.11.0.004` tag. Fresh run `46880d40-9483-4485-96c6-ca5b211d21f7` passed the
three prerequisite commands and selected child
`sha256:e85bc10ac5b141223b289e1e8dc8d448cf3df92501917149db0366b9c5aaf053`,
config `sha256:c4be96218454e68421a29c712e1a83c7a9fe186208c725d8bb2ebb474e2042f2`.
Only one of29 layers is shared with the preceding image. The bounded digest-only pull
completed. A third never-started, owned audit container confirmed all three public
files above are byte-identical to the prior image and was removed; copies are under
`.local/postgres-source-audit/46880d40-9483-4485-96c6-ca5b211d21f7/`.
No previous receipt is repaired and the earlier pass is not attributed to the replacement.

Final explicit bootstrap invocation against this run's exact child/config exited0
in29.612 seconds. All SQL/key and owned-cleanup booleans are true,
`loopback_password_required=false`, `runtime_ready=false`. All13 retained files are
unchanged; this final before/after running inventory is identical. Protected result:
`.local/postgres-bootstrap-qualification/46880d40-9483-4485-96c6-ca5b211d21f7/result.json`,
SHA256 `621582f6fe72b0b1123bc96dc24aead284e040b068d5be6991dc43b3b1fc9e05`.

Post-review focused command: **26 tests PASS,0.227 seconds**. Actual pinned
Supabase CLI2.120.0 regression control `guarded-fresh` against the final run exited0
in63.83 seconds with `synthetic_boundary_proven`, `guarded_volume_owner_proven=true`,
`runtime_ready=false`; no real daemon resource mutation occurs in this control.
Protected record beside the final bootstrap result: `guarded-cli.json`, SHA256
`25df97abab7ae389e76131ed8962f18141b15071bee89b030d4438840a53348f`.
The remaining earlier public negative controls were not repeated; affected deployment
unit/acceptance regression is the broader final check. Eleven review/root finding instances have direct
patches; one low recovery-diagnostic suggestion was rejected because existing UUID/name/
label inspection identifies the resource without adding another recovery result surface.
No finding was deferred. Individual verdicts are in the Build triage log.

The first post-review full-suite process session was unavailable after continuation;
its final output/exit status was not captured and is not counted as a pass. The final
suite is repeated with a protected durable log and JSON exit/count record under the
final qualification run, preserving the earlier448-test pass as a separate result.

Final repeated command `python3 -m unittest discover -s platform/deployment/tests`:
**455 tests PASS,270.685 seconds, exit0**. Protected records are
`.local/postgres-bootstrap-qualification/46880d40-9483-4485-96c6-ca5b211d21f7/deployment-tests-final.{log,json}`;
log SHA256 `57dc2a243d4b884142ffee018e34829ec0cafdf12df9f8c3299f29a55248f976`.
All matrix rows ran and passed, including every post-review negative case. The
staging-run42 output remains a fixture message, not an actual deployment.

Actual final `python3 platform/deployment/dev.py up --target
platform/deployment/environments/kdg-local.json --run-id
46880d40-9483-4485-96c6-ca5b211d21f7` exits2 with
`runtime_adapter_unqualified`, `runtime_ready=false`, stage `up`.
Preparation/toolchain/image bindings remain unchanged; no KDG stack starts.
Scoped whitespace checks pass. Review is closed: eleven finding instances patched,
one low suggestion rejected with reason, none deferred.

## Requirement-to-test evidence

| Requirement | Test/proof |
| --- | --- |
| Explicit opt-in; no runtime claim | `BootstrapAcceptance.test_real_bootstrap_is_an_explicit_control_and_never_runtime_ready` |
| Wrong image cannot mutate containers | `BehavioralAcceptance.test_missing_image_is_refused_before_any_container_mutation` |
| Invalid input/absent preparation/missing owner receipt refuse before execution | `PublicPrerequisites` cases through the public entrypoint |
| Changed final receipt/source cannot endorse earlier proof | `PublicPrerequisites.test_postexecution_receipt_or_source_change_prevents_success` |
| SQL/key observations and verified cleanup required | `Matrix.test_success_requires_sql_key_and_cleanup_and_closed_create`; actual selected-image proof |
| No name adoption or uncertain-create replay/delete | `Matrix.test_collision_and_uncertain_creation_never_adopt_or_delete` |
| Changed owner/image/isolation blocks use/delete | `Matrix.test_changed_ownership_refuses_execution_and_deletion`; foreign-network test |
| No success after SQL/key/password/policy/cleanup failure | `Matrix.test_failed_sql_key_auth_and_cleanup_cannot_report_success` |
| No anonymous persistent image volumes | `Matrix.test_inherited_anonymous_volumes_refuse_before_creation` |
| Exact public key and password verifiers | `Matrix.test_actual_password_verifier_and_public_archive`; actual selected-image proof |
| Bounded stdin/output without deadlock | `BoundedInput.test_input_is_streamed_while_output_is_drained` |
| Stalled input/output overflow/broken pipe remain safe | Remaining `BoundedInput` cases; no raw child error escapes |
| Initialization deadline/stopped container cannot succeed | `FailedInitialization` cases with one owned cleanup; total-budget refusal before commands |
| False semantic observations refuse | `ReviewFixes.test_configured_directory_and_independent_false_sql_checks_refuse` |
| Resource/log limits and late network continuity | `ReviewFixes` limit mutations and network attachment during HBA exec |
| Independent cleanup budget, removal observation and interruption | Remaining `ReviewFixes` deadline/still-listed/interruption cases |
| Malformed owned descriptor remains unresolved | `ReviewFixes.test_malformed_owned_descriptors_report_unresolved_cleanup` |

## Impacts and remaining acceptance

Scaffold: reuse the existing deployment/image/startup owners and qualification entrypoint;
no new generator or generated-file edits. Generator/schema/templates and generated first
consumer proof remain P1/SERVICE work. Shared UI: no UI surface or reusable UI change.
Agent context: existing AGENTS policies suffice; no new generic workflow. Documentation:
this evidence, source authorities, runbook and KDG handoff. ADR: implements existing ENV,
sensitive-log, owner and release-safety constraints; no new or modified accepted decision.

This does not prove real CLI create-to-start continuity, named-volume freshness or
reservation, durable initialized reuse, complete networking/health/stop/reset/recovery,
owner migration coordination, generator acceptance, KDG fingerprint provisioning or a
server-backed KDG slice. Loopback trust is explicitly observed in this network-none
image proof; no production/staging authentication or host exposure policy is qualified.

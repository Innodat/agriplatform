# ENV guarded post-Auth default-privilege execution

The opt-in disposable owner control is implemented and verified. It applies the
fixed post-Auth SQL, independently verifies direct default ACLs and disposes its
owned test resources. Final verification covers 674 tests across 48 serial partitions
and four actual controls below. Three independent reviews completed; all patches
are verified. Four operational investigations are deferred with original evidence.
Complete ENV/scaffold setup and runtime readiness remain open.

## Authority and execution boundary

Pinned Supabase CLI 2.120.0 commit 753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4 supplies
the exact 417-byte SQL, SHA256
438b7e8bf360f0d66c629c5ff102a9fb52584758be94be722d6cb490b216dacc.
See the [source/request proof](ENV_API_DEFAULT_PRIVILEGES_REQUEST_EVIDENCE.md) and
[earlier rollback semantics](ENV_API_DEFAULT_PRIVILEGES_SEMANTICS_EVIDENCE.md).

Order: backend presence → CLI termination/reap → backend departure → Auth
precondition → migration/job disposal → Auth postcondition/raw-request refusal →
bounded apply → independent read-only verify → normal cleanup. Both SQL profiles
use 5s statement/idle and 1s lock bounds. The full normalized default-ACL snapshot
preserves every tuple outside the exact postgres/public target, including grantor,
grantee, privilege and grantability. Direct grant removal does not establish
effective denial through PUBLIC/global/inherited authority.

Only two exact typed wrapped profiles gain admission. Raw-source/altered requests
remain refused; no arbitrary SQL parameter or generic service exists. Execution
retains one connection and the same healthy owned PostgreSQL instance. Attempts
are consumed before dispatch; every finish attempt is terminal, including missing
prerequisites. Failed/uncertain attempts cannot qualify, finish or replay SQL. The
CLI remains terminated; committed SQL is not automatically reversed. All actual
positives retain runtime_ready=false and fresh_setup_completed=false.

## Final requirement-to-test evidence

| Requirement / matrix row | Executed tests |
| --- | --- |
| R1 selected ordered success and normal cleanup | test_guarded_default_privileges_acceptance; test_api_default_privileges_process_order_and_verified_cleanup |
| R2 missing prerequisites/ordinary mode | test_missing_prerequisite_and_ordinary_control_never_dispatch; ordinary backend/catalog process positives |
| R3 altered typed SQL/envelope | test_closed_bounded_profiles_preserve_exact_source_and_all_other_tuples; test_bad_internal_builder_cannot_dispatch_or_replay |
| R4 uncertain/nonzero/bad exec state | test_exec_failures_consume_pair_without_fact_finish_or_replay; test_api_default_privileges_process_nonzero_and_identity_failures_never_qualify |
| R5 custody/deadline/no success | test_custody_change_at_each_new_exchange_cannot_publish_or_replay; test_api_default_privileges_process_lost_response_deadline_and_custody_block_success |
| R6 consumed attempt/finish boundary | test_failed_finish_blocks_all_auth_sql_even_while_phase_five; test_prerequisite_finish_is_terminal_for_each_auth_sql_method; acceptance/negative tests check no replay or finish |
| R7 SQL predicate sensitivity/global preservation | new_owner_semantic tests, test_owner_matrix_proves_grantability_and_unrelated_schema_preservation and fixed actual predicate matrix |

The reviewed test plan discovers 674 unique IDs. All pass across 48 serial partitions,
zero skips, 901.547s summed successful-partition time; 158 owner tests pass 4.235s within
that run. The original partition 37 failure is retained separately and the exact
four-test partition repeats unchanged PASS 71.816s. This is partitioned coverage,
not a successful single full-suite invocation or proof excluding accumulated-order
effects. No assertion, expected result or deadline was weakened.

Pre-extraction 146-test characterization passed before shared executor extraction.
Unit ATDD RED preceded implementation. Independently retained process ATDD RED
against an isolated baseline fails unknown_control; current process tests then
pass. Earlier missing-doc/socket-permission attempts are setup failures, not RED
evidence. Pre-review process groups: 2 tests 25.433s and 3 tests 123.314s, covering nine
positive/failure/ordinary scenarios. Final partitions rerun their affected module.
Review RED/GREEN additionally proves early failed finish blocks all three auth SQL
methods. The final SQL matrix expands 7→11 cases and exercises canonical production
predicates, including deliberately remaining direct grants, omitted/extra SQL,
grantability-only and unrelated-schema corruption, preserved global/sentinel grants
and complete rollback restoration. These are test-only fixed stimuli.

| Actual control on reviewed source | Fresh qualified run | Result |
| --- | --- | --- |
| Owner | `2958e313-15c6-4ef6-b607-d9712333e7d7` | 76.618s, exit 0, qualified; cleanup verified |
| SQL matrix | `2958e313-15c6-4ef6-b607-d9712333e7d7` | 104.089s, exit 0, qualified; cleanup verified |
| Ordinary backend | `9b276d1e-450c-4262-9e11-6bef12dde645` | 96.047s, exit 0, qualified; cleanup verified |
| Ordinary catalog | `9b276d1e-450c-4262-9e11-6bef12dde645` | 85.329s, exit 0, qualified; cleanup verified |

Owner and matrix use fresh prepare/toolchain/images 0.064s/31.594s/55.808s.
Compatibility uses a separate fresh run: 0.115s/19.243s/36.330s. Each actual positive
checks no exact-run container/volume/network remains, source 27 bindings unchanged,
and its 13 prerequisite files unchanged. Ordinary controls omit the new verified
fact. The matrix reports owner_acl_predicates_verified=11; the selected owner
reports api_default_privileges_verified=true. Current all-three-run receipt checks
confirm 39 protected files unchanged. The separately failed backend resources below
remain preserved; earlier successful cleanup is not a claim about that later run.

## Reproduction and retained artifacts

Use the [tracked runbook](DEVELOPMENT.md#guarded-owner-api-default-privilege-execution)
for fresh prepare/toolchain/images, selected control and exact fixed matrix command:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id "$KDG_RUN_ID" --control pinned-cli-postgres-api-default-privileges
python3 -m unittest discover -s platform/deployment/tests -p test_pinned_execution.py
```

Retained local directory:
`platform/deployment/.local/api-default-privileges-owner-qualification/`.
All following basenames are relative to it. They are local verification artifacts,
not committed runtime receipts. `evidence-index.json` enumerates artifact SHA256s;
its SHA256 is 617ec1a11ccd067f6d58f7492459ea9b8d936e3576943876ba962b43909205de.

- `post-review-source-bindings.json`: 27 final source/test paths and hashes;
  `source-bindings.json` retains pre-review bindings (three deliberately patched
  files differ). `verification-runner-bindings.json` retains runner hashes.
- `post-review-test-plan.json`: 674 discovered IDs and 48 groups.
  `post-review-tests-NN.log` / `post-review-tests-NN-result.json`: exact verbose IDs,
  counts, duration, hash, result and no-skip summary for every group. Root validates
  their exact union against discovery. Actual commands were
  `python3 /tmp/kdg-owner-final-tests.py N`, N=0..47; `verification-runner.py` is its
  byte-identical retained copy.
- `post-review-regression-coverage.json`: final coverage, SHA256
  5565548af842190f3a12319879eadbd9af5f461956735c1d718e1860f41bfa2e.
- `post-review-actual-owner-record.json` / `post-review-actual-matrix-record.json`:
  exact tracked command hashes, results, log hashes, duration and inventories.
  `post-review-prereqs-record.json` / `post-review-receipts-before.json` bind that run.
- `post-review-compatibility/`: separate prerequisite/source/receipt bindings,
  retained runners and ordinary backend/catalog records/logs. Records retain exact
  command hashes and result facts. No tests overlap actual Docker controls.
- `process-acceptance-red.log`: valid baseline RED, SHA256
  f3f4e75af1ac5905ff92fed48b70508986c87fbc3767effff2f8bfdfdfe035c4.
  Pre-review process logs and all original failed attempts remain indexed.
- `final-closeout-proof.json`: 39 unchanged prerequisite files, 27 final source/test
  bindings, index preservation and exact-run resources. All 17 concurrent files are
  preserved; the Scribeswell brainstorming memlog advanced independently. Running
  inventories do not claim ownership of concurrent additions.

## Retained failures and review disposition

The [Build record](../../_bmad-output/implementation-artifacts/spec-env-api-default-privileges-owner.md)
records each of 10 blind findings, one verification finding and two final-verification
observations individually. Edge-case review returned no findings. Verified patches:
terminal finish consumption, real negative predicate execution, grantability/
unrelated-schema sensitivity and concrete artifact lookup. Four investigations are
appended to [deferred work](../../_bmad-output/implementation-artifacts/deferred-work.md):

- Ordinary catalog run 4ab63792-4fc4-41f2-b837-51415a6b695b refuses
  `execution_cleanup_unresolved` after 61.766s, retaining healthy PostgreSQL and exited-zero
  Auth job. The Auth removal code is unchanged. User separately approves exact
  two-container/volume/bridge cleanup; IDs, selected image identities, labels and
  all references are rechecked before removal. `approved-cleanup-result.json`
  confirms exactly four removals and 13 unchanged prerequisites. Receipts/diagnostics
  remain; later catalog success does not explain the original failure.
- Original pre-review full discovery exits 143 after 440 passing markers, no summary
  or known signal sender/cause. Its interrupted test and remaining 231 pass in
  retained partitions covering all 672 earlier IDs. Preserve `deployment-tests.log`,
  `partition-plan.json` and `regression-coverage.json`. Possible order/supervisor
  involvement is medium, unverified; later passes are not an explanation.
- Final partition 37 initially returns docker_timeout instead of expected
  docker_response_invalid for initialized-create-malformed. Preserve
  `post-review-tests-37-first-failure/`. Exact test passes unchanged on reviewed
  source 10.761s and isolated baseline 38.150s; eight involved initialized methods are
  AST-identical to baseline, before finish/new SQL. Exact whole partition repeats
  unchanged PASS 71.816s. Original timing/protocol cause remains unconfirmed.
- Reviewed backend run 2958e313-15c6-4ef6-b607-d9712333e7d7 refuses
  `docker_timeout` after 28.952s. `post-review-retained-resource-references.json` records no
  containers, an unused labelled volume and empty bridge
  b3386f7333f0b6d5d1566be3c96f7744cc5966323ab374fd4476516acc049dc7.
  They remain preserved without adoption/removal/replay. Source 27/receipt 13 hashes
  match. Resource acquisition code is unchanged; fresh-run success does not explain
  the failure. Safe original request/phase/deadline observations are still needed.

Other retained prerequisite attempts: interrupted 579b0bb7-7a0e-40d5-98c7-cd1c96c7a8df
has partial toolchain state/lock, no receipt/live observed process; 613c54b7-b8de-4ae7-a28b-1bb48b5c782a
passes toolchain but refuses manifest_response_invalid, retaining its evidence lock.
A later read-only collector passes four images 18.460s without repairing/explaining
that failure. Fresh prepare 9b22e0a4-18c7-497c-9f2e-abed7c5582a8 refuses port_unavailable;
later selected-port observations show no listener/connection. No Docker startup
occurs in these prerequisite failures. Their causes are unconfirmed and artifacts
remain intact, including `post-review-port-refusal/`.

## Impact decisions and remaining gates

- Scaffold: extend existing deployment/lifecycle/qualification owners only; no new
  generator, template, shared schema/client ownership or generic runtime service.
- Shared UI: no browser behavior or reusable UI change.
- Agent context: current isolation/custody/owner instructions suffice; no edit.
- Documentation: this evidence, existing runbook, KDG next-session/memlog and Build
  record carry traceability and remaining gates.
- ADRs: existing release-safety, bounded-transaction and safe-diagnostic decisions
  apply; no new decision or accepted ADR edit.

Next: investigate retained operational failures and continue remaining post-Auth
setup/CLI continuation, full stack and existing scaffold proof. The running Auth/API
stack, actual provider/device proof, P1/SERVICE and dependent Identity/Access/WRITE/
KDG remain undelivered. TypeScript 7.0.2/mail 15484 and existing owners stay fixed.
No production migrations, persistent accounts/access changes, provisioning,
deployment or real-data use is authorized or performed.

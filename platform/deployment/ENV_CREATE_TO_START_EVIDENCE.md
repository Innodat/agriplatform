# ENV PostgreSQL create-to-start proof — 2026-10-16

Bounded synthetic delivery verified under the existing ENV startup owner and
[environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-create-to-start.md)
records acceptance/review. The preceding [complete-create profile](ENV_FIRST_CREATE_PROFILE_EVIDENCE.md)
validated the request through refusal; it did not reach post-create file transfer.
This increment extends synthetic proof only. Runtime readiness remains false.

## Source authority and scope

Pinned Supabase CLI2.120.0 source commit
`753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4` provides:

- [Container lifecycle](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/container-lifecycle.ts): create returns an identity, secret files transfer over stdin with `docker cp`, then start uses the same identity.
- [PostgreSQL service](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/command-internal/db-bootstrap/postgres.service.ts): the selected PG17 profile declares one pgsodium root-key file.
- [Archive construction](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/apps/cli/src/shared/functions/functions-docker.ts): strips leading path slashes and builds an in-memory Bun archive, with documented0644 file mode.
- [Local defaults](https://github.com/supabase/cli/blob/753520fa7202ed5f8b25883a4c0aa7e5e9ad1fc4/packages/stack/src/Defaults.ts): public synthetic default compared in memory, never retained as observed transfer evidence or hashed.

No archive extraction, daemon dispatch, real container create/start, SQL/bootstrap
execution or actual secret installation is authorized or claimed. Exact pinned
process behavior must agree with source authority; fixtures cannot prove real execution.

## Five impacts

- Scaffold: existing ENV startup fixture/verification owners; no parallel generator.
- Shared UI: none.
- Agent context: existing root instructions suffice; actual commands stay in runbook.
- Documentation: startup runbook/source authority/evidence, Build and KDG resume/memlog.
- ADR: existing isolation, safe logging and release constraints apply unchanged.

## Remaining runtime gates

Complete helper inventory and immutable image availability; semantic bootstrap/secret
policy; execution-session daemon/resource continuity and volume reuse/attachment policy;
guarded start/health/stop/recovery; actual deployment PostgreSQL compatibility; controlled
owner migration and fixture integration. Provider/device qualification and P1/SERVICE
generated consuming proof remain separate. Dependent Identity/Access/WRITE and KDG server
work have not started. No Leave implementation, live migration/access/account change,
infrastructure provisioning, deployment or real-data pilot is included.

## Acceptance and characterization

Initial ATDD RED: `python3 -m unittest discover -s platform/deployment/tests
-p test_startup_lifecycle.py` failed the intended create-to-start sequence because
create still returned125 instead of the required simulated acknowledgement0.

Root independently characterized the actual pinned executable from the prior qualified
payload, first checking its complete payload fingerprint against the retained tool
receipt. `python3 /tmp/env-lifecycle-characterize.py` uses only private executable
fixtures, returns a synthetic identity after full profile validation, then stops the
pinned parent at the copy boundary. It never invokes Docker or saves transfer bytes.
An initial harness ordering mistake was refused as `workdir_contaminated`; corrected
ordering constructs invocation before fixture installation, matching existing owner flow.
Two restricted-sandbox attempts reached copy with zero stdin bytes and are not accepted
as transfer evidence. The identical script outside that sandbox passed:10240 bytes,
one expected USTAR regular member, mode0644, uid/gid0, size64, expected synthetic content,
empty user/group/link/prefix, 448 zero bytes of member padding plus 9216 zero bytes after the padded block. Header mtime varies.
Only safe metadata/boolean comparisons were emitted; no archive/value/hash retained.
This resolves an environment-specific stream observation, not an upstream bug claim.
Full fresh owner/public qualification is still required; characterization alone does
not prove lifecycle success or change the approved dependency baseline.

## Focused verification and requirement traceability

Initial implementer verification before review corrections:
`python3 -m unittest discover -s platform/deployment/tests -p test_startup_lifecycle.py`
passed 8 (10.168s outside sandbox); corresponding `test_startup_adapter.py` passed 38
(5.631s outside sandbox); `test_create_profile.py` passed 10. Compilation and scoped
whitespace pass. Sandbox `test_dev.py` attempted16 tests with9 failures/2 errors from
denied socket/port access; it is not acceptance evidence. Final serial regression
must repeat those tests outside the restricted sandbox.

| Requirement | Coverage |
| --- | --- |
| Exact create, same identity transfer, refused first start | `test_exact_sequence_simulates_create_transfers_then_refuses_start`; actual pinned lifecycle-positive control |
| Complete profile remains required | Existing create-profile ten-test suite; old invalid-create controls |
| Wrong target, missing/duplicate/reordered operations | `test_missing_duplicate_reordered_and_unsupported_operations`; public target/order controls |
| Exact bounded archive, no extraction | `test_archive_adversarial_matrix`; public archive control |
| Bounded pipe/socket EOF and stalled/oversized input | `test_pipe_deadline_size_eof_and_no_regular_input`; `test_socketpair_read_and_stalled_writer` |
| Pinned parent checked before read/signal | `test_lifecycle_wrong_parent_refuses_before_read_or_signal` and existing parent identity/process cleanup tests |
| Baseline invalid input cannot qualify injected refusal | `test_invalid_baseline_cannot_qualify_negative_controls` |
| Actual wrapper sequencing and no post-start cleanup | `test_process_boundary_lifecycle_and_controls` |
| Source mutation blocks success | Existing startup source-mutation test now covers lifecycle-positive as well |
| Safe public output and unchanged owner evidence | Final public harness checks sentinel/default absence, exact codes and all thirteen retained file/source identities |

## Qualification attempts

Run `377d1480-0645-4f91-9034-9348d9a447ba`: prepare and tool qualification passed;
image qualification exited2 `registry/manifest_response_invalid`. No image receipt was
published; the protected incomplete directory contains only `.qualify.lock`. It is
preserved unchanged, not repaired or counted as acceptance. Replacement source-bound
run: `41c73d78-ebfc-4233-ac23-6ec5d8f965f4`. Final results remain pending.

Replacement run `41c73d78-ebfc-4233-ac23-6ec5d8f965f4` passed preparation, tool and image
qualification. Initial actual pinned CLI control:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 41c73d78-ebfc-4233-ac23-6ec5d8f965f4 --control lifecycle-positive
```

Exit0 `synthetic_boundary_proven`,11 events, simulated create acknowledged, transfer
validated, first start refused, `container_executed=false`, `runtime_ready=false`.
This initial positive precedes review corrections; final qualification remains pending.

## Independent review

Three review layers returned ten finding instances. Triage retained all ten for local
correction, grouped into seven causes; none deferred. Two behavior defects were verified:
original premature start could qualify an injected-order negative control, and leading
NUL numeric padding could certify mode0644 while standard tar parsing produced0000.
Root independently reproduced the numeric mismatch with a valid recomputed checksum.
Corrections also cover invalid original sequences, independent malformed-header cases,
one total read deadline under trickling input, derived event boundaries, transfer-refusal
parent termination proof and precise documentation. Final verification follows fixes.

After review fixes, the focused lifecycle suite passed 13 tests (29.074s), and the
startup suite passed 38. A source edit during an earlier test run correctly triggered
`proof_source_changed`; the stable rerun passed. The independently reproduced numeric
ambiguity now refuses with `unsafe_lifecycle`. Added traceability:

| Requirement | Additional review regression |
| --- | --- |
| Strict numeric/header interpretation with valid checksums | `test_numeric_headers_with_independent_checksums` |
| One total deadline under continuous input | `test_trickling_input_uses_one_total_deadline` |
| Invalid original sequence cannot certify injected failure | `test_original_sequence_defects_cannot_qualify_injection`; `test_duplicate_original_transfer_rejected_before_read_or_injection` |
| Transfer refusal terminates parent before cleanup | `test_cp_terminal_refusal_kills_parent_before_cleanup` |

Frozen-source run `28778358-0e4d-4742-8aac-80d8d216fcfd` passed preparation/tool
qualification but image collection exited 2 `registry/manifest_response_invalid`.
Only `.qualify.lock` exists in its image directory; no receipt was published or repaired.
Fresh replacement run: `26c17c4a-9896-4940-b712-be9d1c80be0f`.

## Final frozen-source qualification

Run `26c17c4a-9896-4940-b712-be9d1c80be0f` passed these commands serially:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 26c17c4a-9896-4940-b712-be9d1c80be0f
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 26c17c4a-9896-4940-b712-be9d1c80be0f
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 26c17c4a-9896-4940-b712-be9d1c80be0f
python3 /tmp/env-lifecycle-public-proof.py 26c17c4a-9896-4940-b712-be9d1c80be0f
```

The public harness invokes the existing `tests/qualify_startup.py --target
platform/deployment/environments/kdg-local.json --run-id <same UUID> --control <control>`
for each control below. The retained record contains every exact command/result;
the temporary orchestration script is not a new delivery entry point.

| Control | Exit | Expected code |
| --- | --- | --- |
| positive | 0 | synthetic_boundary_proven |
| invalid-network | 2 | network_not_run_owned |
| contaminated-workdir | 2 | workdir_contaminated |
| reject-command | 2 | expected_command_rejected |
| invalid-selection-plan | 2 | invalid_selection_plan |
| invalid-create-script | 2 | expected_create_profile_rejected |
| invalid-create-environment | 2 | expected_create_profile_rejected |
| invalid-create-routing | 2 | expected_create_profile_rejected |
| lifecycle-positive | 0 | synthetic_boundary_proven |
| invalid-lifecycle-target | 2 | expected_lifecycle_rejected |
| invalid-lifecycle-archive | 2 | expected_lifecycle_rejected |
| invalid-lifecycle-order | 2 | expected_lifecycle_rejected |

All 12 passed. Lifecycle positive observed 11 events, acknowledged the synthetic
create, validated the secret transfer and refused first start. Existing positive
retained its nine-event create refusal. Both independently matched the four image
observations to retained child-manifest bytes. Every result kept runtime readiness
false; neither positive executed a container. No stderr or checked sensitive markers
appeared. Thirteen evidence files retained identical hashes, inodes, modes and mtimes;
preparation/startup source snapshots also remained identical.

Protected local record:
`.local/create-to-start-qualification/26c17c4a-9896-4940-b712-be9d1c80be0f.json`
SHA-256 `74ba3cfdd418f3288a4f79e38b6657ba4a8f8298360c79ec099319a033a78aef`.
No evidence from an incomplete or pre-fix run was promoted to final proof.

## Final regression and closure

`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passed **338 tests in 131.579s**, exit 0, outside the restricted sandbox and after
public qualification. The first regression process handle was lost during a session
update, so its incomplete output is not counted; the repeated run retained output in
`/tmp/env-lifecycle-regression.log`.

`python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json
--run-id 26c17c4a-9896-4940-b712-be9d1c80be0f` exited 2 with
`docker_28_required`, `runtime_ready=false`; no container ran.

`python3 -m py_compile` passed for dev.py, startup.py, startup_lifecycle.py,
tests/qualify_startup.py, tests/test_dev.py, tests/test_startup_adapter.py and
tests/test_startup_lifecycle.py. Scoped whitespace and local Markdown links passed.
All ten independent review finding instances were fixed; none deferred. The five
impact decisions above remain applicable. Concurrent Leave/PtS changes are preserved.

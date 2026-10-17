# ENV guarded CLI volume creation integration

2026-10-16. Existing ENV owner delivery through bmad-help/bmad-build, ATDD and
focused TDD. [Build record](../../_bmad-output/implementation-artifacts/spec-env-guarded-cli-volume-creation.md).
Runtime readiness remains false.

## Purpose and limits

The pinned CLI fresh fixture previously acknowledged its two-label volume-create
command without invoking ENV's six-label volume owner. This item connects that
boundary to the retained guarded resource session, exercised against private synthetic
Docker peers. It must not precreate the volume before the CLI's truthful absent probe.
Acknowledgement requires validated owner creation, reinspection and current absence
of container references. Uncertain mutation terminates without replay, adoption or
cleanup. Existing standalone proofs and metadata acquisition remain supported.

Docker create is name-addressed and idempotent. Neither an absent probe,201 nor owner
labels prove immutable identity, exclusive reservation, empty storage or initialized
contents. This item cannot qualify bootstrap/secret/SQL semantics or actual lifecycle.
No real daemon mutation, container or SQL is executed; `up` stays gated.

## What the up refusal means

`python3 platform/deployment/dev.py up --target <target JSON> --run-id <prepared UUID>`
is the repository's intended isolated-stack start command. Its current implementation
validates preparation/ports, reads the fixed Docker socket's version and then refuses.
It does not yet start a complete stack. A selected-field read on this delivery turn
confirmed Linux Engine27.0.3, API1.46; the required engine minimum is28.0.0. Updating
the Docker client or repository packages does not upgrade that shared engine.

Docker documents that older engines may expose localhost-published ports to other
machines on the same L2 network. The gate therefore protects the selected loopback
isolation contract. [Docker publishing guidance](https://docs.docker.com/engine/network/port-publishing/).
The mismatch is technically resolvable through a host engine upgrade or a supported
isolated target. That changes infrastructure outside the standing approval. No upgrade
was attempted. Even after it, current `up` explicitly refuses
`runtime_adapter_unqualified`: the remaining runtime implementation and qualification
must also be completed. The version mismatch and unfinished adapter are distinct gates.

## ATDD and characterization

Root first ran the integrated test before the new API existed:1test ERROR in0.132s,
unexpected `_guarded_target` keyword. That established the missing seam but was not
used as the behavioral acceptance result. The test was adjusted to exercise the old
standalone fresh path and require the owner operation before production changes:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py' -k integrated_fresh_cli_creates_through_retained_volume_owner
```

**RED:**1test FAIL in0.994s, no owner POST versus one independently specified exact
six-label `/v1.48/volumes/create` request. Production implementation began only after
root observed this result. The test then targets the explicit integrated seam.

Before extracting the existing guard, root also ran:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py' -k fresh_invocation_leaves_volume_absent
```

**Characterization GREEN:**1test PASS in0.374s; existing constructor leaves the volume
absent with its exact one-connection event sequence.

## Required impact decisions

- Scaffold: extend existing ENV volume/resource/startup owners and private qualifiers;
  no second generator, runtime service or readiness engine.
- Shared UI: no user-facing or shared UI change.
- Agent context: current ATDD, ownership, sensitive logging and release rules suffice;
  no root/generated instruction change.
- Documentation: existing profile/lifecycle authority, runbook, this record, Build and
  KDG handoff/memlog must distinguish implementation, synthetic proof and live gates.
- ADR: existing isolation/ownership/log/release decisions apply; no accepted ADR edit
  or new architecture decision. No migration or release activation.

The first implemented focused integration attempt ran1test in1.965s and refused
`docker_response_invalid` at the retained-session idle check. This is recorded as an
unsuccessful check, not a pass. The existing peer's short idle lifetime is investigated;
production EOF and five-second absolute deadline guards stay binding.

After extending only the private peer's idle lifetime beyond the unchanged total
five-second production budget and adding its independent integrated oracle, the same
focused test passes1test in1.459s. It asserts the exact70-request sequence on one
connection, including owner POST/observations before acknowledgement, final joint
observation after CLI termination, and refused first start. This is the first GREEN,
not final broad qualification.

Focused integrated matrix passes4tests in35.740s; public qualifier wiring/safe-output
passes1test in7.342s. During read-through, private CLI-config custody was tightened.
Before that patch, root observed1test with2 failing inspect/create subcases in2.786s:
configuration_changed was detected eventually, but volume POST had already occurred.
After adding current workdir/config checks at the handoff/process boundaries, the same
smallest test passes1test in1.620s, proving no owner volume POST for those states.
The full affected resource suite is rerun after that patch.

The then-current full resource suite passes34tests in123.214s. A further pre-POST
subcase changed the private config while the final absence response returned, after
the outer handoff check. Root observed1test FAIL in3.636s: the new pre-post case still
saw a volume POST (the two earlier cases passed). That RED precedes binding private
fixture custody into the guard's per-request current checks. The final full regression
must run after this correction; the earlier full-resource pass is not substituted.

Final pre-review custody correction: smallest private-config test passes1test in2.368s;
all5 integrated tests pass40.069s; public wiring/safe-output passes1test in4.083s.
The guard now binds concrete private work/source/fixture/wrapper/listener custody into
its per-request check, including the check immediately before POST. The drip test
records the spawned wrapper PID privately and proves it is absent or non-running
(Z/X) afterward; this does not claim zombie reaping.

## Requirement-to-test traceability

| Requirement | Test/control |
| --- | --- |
| Retained owner POST, exact profile, observed volume, refused start | test_integrated_fresh_cli_creates_through_retained_volume_owner; guarded-fresh |
| Existing/foreign/uncertain ACK/reinspection/reference failures | test_integrated_owner_negative_matrix_never_replays_or_returns_proof; twelve guarded controls |
| Changed source/receipt/lock, budget, final owner probes | test_integrated_handoff_custody_and_total_deadline_refuse_with_cleanup |
| Forged/malformed/duplicate/repeated/wrong-args/partial handoff | test_integrated_private_handoff_adversaries_and_drip_deadline |
| Exact private config before probe/create/POST | test_integrated_private_work_configuration_change_prevents_owner_ack |
| Standalone fresh owner algorithm and no replay/adoption | test_fresh_owner_exact_request_and_current_use_before_handoff; test_fresh_owner_refuses_existing_uncertain_and_changed_without_replay |
| Public parser/wiring and selected safe output | test_guarded_public_qualifier_wiring_and_safe_output |
| Existing acquisition/constructor/CLI contracts | Complete affected resource/volume/startup/lifecycle and final deployment regression; existing public positives |

Pre-review affected suites: volume31tests PASS11.566s; lifecycle19tests PASS52.183s.
Current integrated5tests PASS40.069s and public-wiring1test PASS4.083s cover every
matrix row. Existing constructor/acquisition coverage passed34tests before the final
fixture-only custody binding; final full deployment regression covers that snapshot.
Changed Python AST and scoped whitespace checks pass.

## Independent review and corrective verification

All eleven finding instances were triaged before grouping; none was deferred.
Two verification findings duplicate the blind review's output/ancestry gaps. The
edge-case reviewer returned no findings. The executable gap required a production
fix; remaining code/test gaps and final evidence were assigned narrow patches.

Before that fix, root ran `python3 -m unittest discover -s platform/deployment/tests
-p test_resources.py -k integrated_executable_mutation_before_launch_and_post_refuses`:
one test, four FAIL subcases in7.814s. Replacing or rewriting identical executable
bytes before launch or immediately before POST incorrectly returned proof. The fix
retains a no-follow executable descriptor before existing owner byte verification,
then checks its identity/metadata and the resolved directory plus exact launch alias
before launch and each owner exchange. It adds no per-request payload/binary hashing.
The focused `-k integrated_executable_mutation` test now passes1test in6.217s.

Additional requirement-to-test evidence:

| Boundary | Focused regression |
| --- | --- |
| CLI identity/custody before launch and owner POST | test_integrated_executable_mutation_before_launch_and_post_refuses |
| Joint observations45/49/53/56/57 before ACK; source/receipt/lock/config immediately after POST42 | test_integrated_pre_ack_joint_and_post_mutation_custody_refuse |
| Removed/replaced/chmod listener and descendant cleanup | test_integrated_listener_custody_before_post_and_descendant_cleanup |
| Valid capability from real grandchild; wrong parsed kernel UID | test_integrated_handoff_rejects_real_grandchild_and_wrong_parsed_uid |
| stdout/stderr/combined overflow; malformed handoff/inherited-pipe timeout; process-group termination | test_guarded_runner_output_bounds_and_terminal_descendant_cleanup |
| Empty/2049-byte/full-without-write-EOF frames | test_integrated_private_handoff_adversaries_and_drip_deadline |

Cleanup checks accept absent or non-running Z/X processes; no zombie-reaping claim.
Output cases assert consumed bytes stop at1MiB+1. No new public controls or daemon
endpoint selector were added for these private tests.

Root ran the five review methods using repeated `-k` selectors
`integrated_pre_ack_joint`, `integrated_listener_custody`,
`integrated_handoff_rejects_real`, `guarded_runner_output_bounds`, and
`integrated_private_handoff_adversaries`:5tests PASS57.392s. The affected acceptance
matrix selected by `integrated_fresh_cli`, `integrated_owner_negative`,
`integrated_handoff_custody`, `integrated_private_work`, and `guarded_public` then
passes5tests in46.933s. These commands use the same unittest discovery prefix above.
Root inspected all review patches; all eleven finding instances are resolved.

## Final source-bound qualification

Fresh UUID: `d998c960-c37e-4ef6-807a-9fc6fe6a4f3b`. Initial sandbox preparation and
toolchain attempts returned `port_unavailable` because port probing was unavailable;
the same commands were rerun with socket-capable execution. Preparation passes with
`code=prepared`, `runtime_ready=false`. No source or retained receipt was repaired.

The first run's toolchain passes `toolchain_qualified`. Its initial sandbox image
attempt returned `images_cli/command_refused`; socket/network-capable retry reached
the registry but returned `registry/manifest_response_invalid` (exit2). That run is
preserved unchanged, with no fabricated completion or reuse of partial image evidence.
Fresh replacement UUID `5f28c799-d3e3-4a37-86c8-9aca62bd562e` prepares successfully.
Its toolchain also passes; image qualification again exits2 with
`registry/manifest_response_invalid`. Both runs remain unchanged. A separate
read-only diagnostic reported only safe operation/status/media/encoding fields:
the selected gotrue Linux/amd64 child manifest returned HTTP429; other selected
index/child probes returned200 after anonymous token exchange. No token, header,
payload or response body was printed. This identifies rate limiting as an external
qualification failure, not successful image evidence. Full synthetic regression runs
before the final fresh collection attempt; no retry/bypass is added to the owner.

Final full regression:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py' > platform/deployment/.local/env-guarded-cli-regression.log 2>&1
```

**429 tests PASS in360.909s**, exit0, after all production/test review patches. The
synthetic release-coordinator fixture also reports its successful staging run42;
this is not a deployed environment. Final replacement UUID after registry cooldown:
`05e169bc-8a00-4c7c-aca2-1ada8bd97454`, preparation PASS.
Retained regression log SHA256:
`fd0c7fb514b4175a7f8b1a4df150ed9ac39d76ed2d7d89cf70a8ae64ecd4cf45`.

The final run passes both `toolchain_qualified` and `base_images_qualified`, exit0.
Commands (all from the repository root, socket/network-capable execution):

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 05e169bc-8a00-4c7c-aca2-1ada8bd97454
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 05e169bc-8a00-4c7c-aca2-1ada8bd97454
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 05e169bc-8a00-4c7c-aca2-1ada8bd97454
```

All retained tool versions follow the approved baseline, including TypeScript7.0.2;
no shared daemon resource was mutated. Earlier registry-refused runs remain intact.

The first external harness attempt reached a successful `guarded-fresh` result but
failed its own options assertion: it expected `{}`, while the independent synthetic
volume oracle in `qualify_volumes.py` explicitly returns `Options=None` and the existing
descriptor contract preserves that representation. This is a harness failure, not a
recorded public pass. Root inspected both authorities before correcting the harness
to require exactly `None`; no product expectation or implementation changed. The
complete public batch is rerun, including that first control.

Corrected batch: actual pinned `guarded-fresh` passes (exit0,
`synthetic_boundary_proven`), with11 CLI events and70 API exchanges on one retained
connection. It proves exact six-label owner creation before ACK, selected safe volume
projection and a refused first start. No container/SQL execution or runtime readiness.

That batch then passed existing/foreign/lost/truncated/bad-ACK/bad-descriptor/changed
controls, but `guarded-use` returned `docker_timeout` instead of its expected
`volume_in_use`; a direct public repetition also returned the timeout. Neither is
counted as passing that control. A diagnostic repetition preserved the deadline and
captured only request counts/timings: all44 expected exchanges completed by2.463s,
and the public result was the required `volume/volume_in_use`. No production fix or
expectation/deadline change was made; the earlier timeouts remain recorded rather
than attributed to an unproven cause. The external harness now retains each validated
control with unchanged13-file/source snapshots, so interrupted attempts do not discard
previous evidence. The complete matrix is rerun and consolidated only after all pass.
The first retained batch passed use/fresh but then returned an unexpected deadline
for `guarded-existing`, which had passed earlier. Its subsequent repetition produced
the required `volume_reuse_unsupported`. These deadline refusals are unsuccessful
attempts, not changed expectations. Retained controls must match their original
expected exit/code and identical evidence/source snapshots; future unexpected deadline
attempts are recorded separately and prevent consolidation until each control passes.

## Final closure — 2026-10-17

All fifteen public controls now have their original expected exit/code, including
successful `guarded-fresh`, all twelve `guarded-*` refusals, existing
`fresh-lifecycle-positive` and original `positive`. The descriptor, late-volume and
late-use controls subsequently pass without source/expectation/deadline changes.
Earlier unsuccessful attempts remain evidence; this is not a first-attempt reliability
claim. The five-second fail-closed budget is unchanged.

The temporary verification harness invokes only the existing public entrypoint:

```sh
python3 platform/deployment/tests/qualify_startup.py --target platform/deployment/environments/kdg-local.json --run-id 05e169bc-8a00-4c7c-aca2-1ada8bd97454 --control CONTROL
```

Exact commands/results for every control and matching before/after SHA256, inode,
mode and mtime for all thirteen retained files plus current source snapshots are in
`platform/deployment/.local/guarded-cli-volume-qualification/05e169bc-8a00-4c7c-aca2-1ada8bd97454.json`.
Record SHA256:
`00997dff9436a55ff2867e2467991c4bb0bcda3d5e2262ac50441b2e7cabcf71`.
Root independently rechecked this record against all current files/sources after
consolidation. Per-control protected records are under
`.local/guarded-cli-volume-controls/05e169bc-8a00-4c7c-aca2-1ada8bd97454/`.

Separately retained unexpected deadline attempts under
`.local/guarded-cli-volume-attempts/05e169bc-8a00-4c7c-aca2-1ada8bd97454/`:

| Control | Attempt ID | SHA256 |
| --- | --- | --- |
| guarded-bad-descriptor | 523643e0-866f-4c2b-97f8-387504a68748 | e93862292e28175671d12b8475fb1005706d341597beaa93924b64bada6db693 |
| guarded-late-volume | faaa844f-239e-4895-869a-d17400a06341 | 5c006980de8619bad6f653d53e87d768cfc409417be6d2e2ac7e95f6b78804b6 |
| guarded-late-use | f7bed497-2f66-40e5-8041-637623c80b73 | bae00dea6f4d2dff98b68bd366206d0261a3c1aba6e9c0305b9ee11bbeee127f |

Read-only real prerequisite check:

```sh
python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json --run-id 05e169bc-8a00-4c7c-aca2-1ada8bd97454
```

Expected exit2: `docker/docker_28_required`, `runtime_ready=false`. No gate bypass,
daemon mutation, container/SQL execution, host upgrade or deployment occurred.
429 deployment tests and15 public expected results are complete. All eleven review
finding instances are resolved; none deferred. Eight changed Python files parse;
scoped whitespace and local Markdown targets pass. Required five impact decisions
are recorded above. This completes the bounded integration increment; enclosing ENV
runtime/bootstrap and P1/SERVICE scaffold acceptance remain open.

Concurrent Leave commits appeared during this delivery (including the initial Build
record). They and the latest working-tree edits are preserved; no history is rewritten.
The final commit is scoped to this ENV item's files, with unrelated current file/index
snapshots checked immediately around that commit.

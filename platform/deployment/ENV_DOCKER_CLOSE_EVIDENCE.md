# Docker close-error preservation evidence

Build: [ENV preserve failures during socket close](../../_bmad-output/implementation-artifacts/spec-env-docker-close-failure.md).
Status: bounded close-error correction complete, verified and reviewed. Runtime readiness remains false.
Baseline: `7e2ceeb66892a7be08cf578c314971c322b62c75`.

## Purpose and scope

bmad-help selects the existing ENV transport-owner close-error investigation, recorded
by the preceding diagnostics review. A socket OSError during failure handling can
replace the original transport refusal, then context exit can repeat the close.
The existing DockerSession owner now invalidates/detaches before one close attempt.
Active exchange/body failures remain authoritative when close raises OSError.
Without an active failure, explicit close and ordinary exit still raise the close
error. Non-OSError close exceptions retain propagation. Cancellation already active
is preserved. No new error fields/codes, routes, retry, resource cleanup permission,
service, generator, dependency or runtime admission are introduced.

Closed means permanently unusable, not verified kernel closure or Docker-resource
cleanup. A close error never becomes a successful exchange or lifecycle result.
Existing connection deadlines, no reconnect/replay and lost-custody preservation stay.

## Requirement-to-test ledger

| Requirement | Executed test | Result |
| --- | --- | --- |
| C1: qualifier retains transport error and safe diagnostic | DockerSessionTests.test_close_failure_acceptance_keeps_qualifier_transport_refusal | RED then GREEN |
| C2: original mapping and active cancellation | test_close_failure_preserves_active_exchange_error_and_cancellation (timeout, OSError, Refusal, KeyboardInterrupt, SystemExit) | PASS |
| C3: context body failure remains original, no invented diagnostic | test_context_close_failure_preserves_active_body_error_only | PASS |
| C4: explicit/normal-exit close error remains visible; one attempt | test_standalone_or_normal_exit_close_error_is_reported_once | PASS |
| C5: non-OSError close exceptions still propagate once | test_non_os_close_failure_propagates_and_does_not_repeat | PASS |
| C6: existing framing, session reuse and owner behavior | Session/gate/network/volume/image and selected process tests | PASS |
| C7: partial mutating send/lost response/later validation plus close error | test_close_failure_after_mutating_transmission_keeps_phase_and_no_replay (send/receive/idle_after/budget_after) | PASS |
| C8: successful exchange plus failed close never emits success | test_successful_exchange_then_close_failure_never_emits_qualifier_success | PASS |

Before implementation, the acceptance test emits startup/startup_proof_refused instead
of docker/docker_timeout plus original daemon_version/connect observation. The exact
failed output is retained; no expected result is changed. New tests also verify no
sensitive canary in JSON, no second socket/transmission, stream detachment, no close
retry, and identical exception objects where normalization does not apply.

Protected ignored records are in
`platform/deployment/.local/docker-close-failure-qualification/`. acceptance-red.log
and acceptance-green.log retain outer-loop evidence. focused-red.log/focused-green.log
include an existing private-socket test selected by the broad `-k close` filter; its
restricted-sandbox binding error is not an implementation failure or positive proof.
The authorized full session suite subsequently passes with private socket permissions.

## Acceptance command and immutable results

```sh
python3 -m unittest discover -s platform/deployment/tests -p test_docker_session.py -k close_failure_acceptance
```

Before implementation: exit1, one expected failure, acceptance-red.log SHA256
`82662d195b118385f55b0548aed19c80b433c814efa8185609575d4d9415eedf`.
After implementation: exit0, one PASS0.019s, acceptance-green.log SHA256
`774d1086a37de6d8b9e2865f12621648cb23ee1c9a1e8f5919ee23e907dcf70c`.
The final33-test session suite includes this acceptance test again. Review additionally
covers partial mutating sends/lost responses, idle/final-budget failures, successful
exchange followed by failed close at public JSON output, and non-OSError close failures
on exchange/explicit/body paths. Six focused review tests PASS0.023s, followed by full
session verification. The92-owner suite predates only the class docstring's wording
clarification and these test additions; its production behavior is identical.

## Verification

The following commands pass. The last command is one test containing four physical
private-process lost/malformed archive/start scenarios. Total126 executed tests.

| Command | Result | Log SHA256 |
| --- | --- | --- |
| `python3 -m unittest discover -s platform/deployment/tests -p test_docker_session.py` | 33 PASS0.449s | `0f0a5bce4ce1c870e66d9847af2cbbecfc2651c2f018db878e72c6251e067e4d` |
| `PYTHONPATH=platform/deployment/tests python3 -m unittest test_docker_gate test_networks test_volumes test_daemon_images` | 92 PASS44.149s | `ee6228d638cb5448030c01205d8b7aec29f6770880ef90695a9d09bd915d2b48` |
| `python3 -m unittest discover -s platform/deployment/tests -p test_resources.py -k test_execution_uncertain_archive_start_preserves_closed_peer_without_replay` | 1 PASS7.142s | `c26302da373ea3c6a2062d8def4d5f5f4c0d0b920e7427265f653186d335b851` |

This item does not repeat actual Docker runtime controls
or claim fresh source-qualified startup. Previous638-test/full runtime-control evidence
belongs to the previous source. Source-bound receipts remain untouched and require
fresh preparation/qualification before future actual execution.

## Five impact decisions

- Scaffold: correct the existing shared ENV Docker transport; no generator or new runner.
- Shared UI: no user-facing surface changes.
- Agent context: existing custody, privacy and ATDD rules suffice; no instruction edits.
- Documentation: this evidence, DEVELOPMENT.md and KDG handoff/memlog record behavior,
  commands/results, verification limits and the resolved owner investigation.
- ADR: apply ADR0023 and existing environment/lifecycle decisions; accepted ADRs unchanged.

## Preserved work and gates

Concurrent Leave/PtS/Expense/brainstorming files and index, all prior receipts/failures
and uncertain Docker resources remain. Exact TypeScript7.0.2/mail15484/approved target
are unchanged. Existing schema/client/generator/test/runbook owners retain work.
Full CLI/Auth/setup, public lifecycle/runtime, ENV/P1/SERVICE scaffold acceptance and
Identity/Access/WRITE/server KDG stay gated. No Leave/editor, accounts/grants,
production migrations, infrastructure provisioning, deployment, push or real-data pilot.

## Independent review and acceptance

The oneshot route runs one independent blind review; its added-content floor is5.
All five findings are individually triaged in the Build and fixed through test/evidence
changes, with no further production correction. No new deferred item. The preceding
transport close-OSError investigation is resolved by this increment; old deferred-work
entries remain historical and untouched. Divergent-ancestry and older investigations
remain open. No actual Docker controls or full-suite result is claimed for this source.

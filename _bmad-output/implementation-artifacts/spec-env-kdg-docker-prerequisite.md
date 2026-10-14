---
title: 'ENV: enforce the local Docker prerequisite before startup'
type: feature
created: '2026-10-14'
status: done
route: oneshot
review_loop_iteration: 0
baseline_commit: cb12db0467438ee6196ea6ae362dd4752076e57e
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Existing approval for bounded ENV implementation and isolated synthetic verification">

## Intent

Prepared ENV targets and qualified tools still lack an executable Docker prerequisite
gate. Implement the next bounded existing ENV increment in `platform/deployment/dev.py`:
`up` validates an existing unchanged protected preparation without creating/repairing it,
rechecks reserved ports, and inspects only the fixed local Docker Unix socket using a
bounded read-only GET /version. Require a stable Linux Docker Engine version >=28.0.0,
using the server version rather than the client version or ambient Docker context.
Missing, denied, malformed, oversized, truncated, slow, non-Linux or prerelease daemon
responses refuse safely, with runtime_ready=false and no raw response/error output.
Ignore Docker environment/context overrides; no remote/TCP/custom target support.
A passing prerequisite still refuses runtime_adapter_unqualified because runtime
adapters, images/DB, fixture/migration coordination and toolchain consumption are not
delivered. verify/stop/reset retain their current refusal and reset confirmation rules.

No socket command except GET /version, container/image/network/volume mutation,
daemon upgrade/configuration, schema/account/access change, infrastructure, deployment,
Leave or KDG domain implementation is permitted. All prerequisite observations are
point-in-time checks, never runtime readiness or a safe-network guarantee. Preparation
source changes deliberately invalidate old prepared runs/qualification receipts rather
than silently adopting them. Existing six-tool exact pins including TypeScript7.0.2
stay unchanged. Preserve concurrent Leave/PtS planning edits.

</frozen-after-approval>

## Implementation Notes

bmad-help selects Build for the existing ENV prerequisite, ahead of P1/SERVICE and
dependent Identity/Access/WRITE. No intent gap or irreversible action is required.
Small footprint: dev.py, its tests, a focused Docker-gate test module, owner evidence/
runbook and KDG handoff navigation/memlog. Use existing preparation tests as
characterization before extracting expected inventory construction. Observe public up
acceptance red before implementing the gate, then focused TDD for transport/version/
prepared-input safety. Verify actual host refusal using a fresh prepared run and run
the affected deployment suite. Record all five impacts and requirement-to-test mapping.

Preparation characterization passed16 tests in6.059s before refactoring. Public up
acceptance red and focused missing-function failures were observed before implementation;
the corrected initial eight-test discovery had two failures/fourteen subtest errors.
After implementation eight tests passed, then eleven with added tamper/port/output
proof. Existing lifecycle tests now leave up to its dedicated prerequisite suite;
verify/stop/reset coverage remains intact. No public startup bypass or runtime adapter
was added. Actual host prepare/up proved the Docker<28 refusal before runtime mutation.

## Review Triage Log

| Finding | Verdict and resolution |
| --- | --- |
| Mutable preparation ancestors not rechecked | medium; reproduced daemon contact after .local/kdg became0777. Patch read-only owner/write checks; regression covers both ancestors. |
| Malformed header control characters admitted | low; reproduced NUL header acceptance. Reject control bytes and invalid status reason; regressions cover NUL/LF/CR/DEL. |
| Deep JSON decoder error mapped to input validation | low; bootstrap accepts depth1500 but native json.loads at depth10000 raises RecursionError below64KiB. Normalize as docker_response_invalid; public JSON test uses depth10000. |
| Deadline test expired before receive | medium verification gap; add progressive one-byte reads, shrinking timeout assertions, and connect/send/receive timeout cases. |
| Missing fragmented-success and exact-cap proof | medium verification gap; add1/2/7/31-byte fragments and complete65536/65537-byte responses. |

All five findings were accepted and fixed; none deferred. Review regression initially
reproduced ancestor contact and malformed headers (three failures/one assertion-context
error); after fixes all15 focused tests pass. Test assertion scoping was corrected so
each malformed-header subcase reports independently.

## Verification

- `python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`:
  final173 tests pass in83.494s with isolated socket permission. Earlier pre-review
  suites passed166 and169 tests before new regression coverage.
- `python3 -m unittest discover -s platform/deployment/tests -p test_docker_gate.py -v`:
  final15 tests pass in2.369s when run alone. One prior focused run failed during
  preparation while actual preparation simultaneously probed the same fixed ports;
  serialize these checks. No test was skipped or expectation relaxed for that failure.
- Final-source actual prepare/up with run9ea3b977-f414-4414-b05e-444e6305c615:
  prepare exit0; up expected exit2, docker/docker_28_required, runtime_ready=false.
- Scoped whitespace and relative documentation links pass. The evidence/runbook and
  KDG next-session/testing/memlog record five impacts and requirement-to-test mapping.
  Concurrent Leave/PtS documents remain outside this delivery.
- `python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 9ea3b977-f414-4414-b05e-444e6305c615`:
  exit0 on final source; six actual pinned tools, compiler/GIL checks pass,
  toolchain_ready=true/runtime_ready=false. Receipt mode0600,1958bytes,13655entries,
  SHA2567152e1fb6d996ad515d1ad05729cc8cce473241b36aabc302ab7d36963f45676.

# ENV run-volume use admission evidence

2026-10-16. Existing ENV owner increment selected by bmad-help and delivered through
bmad-build with ATDD/focused TDD. [Build record](../../_bmad-output/implementation-artifacts/spec-env-volume-use-admission.md)
and [runbook](DEVELOPMENT.md) retain bounded scope. The enclosing ENV item remains open.

## Scope and authority

Run-owned volume metadata alone did not show container references. This increment
observes all containers using the exact volume-name filter on the existing guarded
Docker connection, refusing any nonempty result before standalone/joint handoff.
The joint coordinator repeats the observation after its final volume descriptor check.
No container metadata is exposed in errors or reports. There is no cleanup or replay.

The pinned [Moby28 API1.48 contract](https://raw.githubusercontent.com/moby/moby/v28.0.0/docs/api/v1.48.yaml)
ContainerList documents all=true, volume filtering and array results. The
[daemon implementation](https://raw.githubusercontent.com/moby/moby/v28.0.0/daemon/list.go)
uses exact volume-name/destination map lookups. Destination matches conservatively
refuse too. Only this closed query accepts arrays; other routes retain object responses.

An empty observation is not reservation/exclusivity or proof of fresh/empty/initialized
storage, future absence of users, immutable volume identity or execution readiness.
Matching existing volumes remain metadata-admissible. No real daemon resources,
containers, SQL, image layers, infrastructure or access/account state are changed.
TypeScript7.0.2 and the approved dependency baseline remain unchanged.

## ATDD RED

Production code was unchanged when the root ran these tests outside the socket sandbox:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_volumes.py' -k referenced_volume
python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py' -k late_volume_reference
```

Each ran one test, exit1: `AssertionError: Refusal not raised`. The standalone failure
was at test_volumes.py:121; the late joint reference failure at test_resources.py:67.
The implementer waited for these observed failures before changing production code.

## Required impact decisions

- Scaffold: extend existing ENV transport/resource adapters and their existing synthetic
  qualifiers; no parallel generator, runtime service or lifecycle. P1/SERVICE remain open.
- Shared UI: no user-facing surface or reusable UI change applies to daemon admission.
- Agent context: existing owner/ATDD/safe-log/release rules suffice; no root/generated
  instruction changes. Actual generated instructions remain with their consuming owner.
- Documentation: current runbook/status, this evidence, Build record and KDG handoff/memlog
  record tested behavior, command results and remaining gates.
- ADR: existing ownership, isolation, logging and release decisions apply; no new decision
  or accepted ADR edit. No runtime migration or activation is introduced.

## Requirement-to-test evidence

| Requirement | Executed protection |
| --- | --- |
| Admit only unused new/existing owned volume | `test_unused_new_and_existing_volume_construct_once_after_use_check`; combined exact-order/constructor test |
| Refuse running/stopped/same-owner references | standalone `test_all_private_controls` and safe public use-control test; combined negative/public control matrices |
| Recheck before final combined handoff | `test_late_volume_reference_refuses_before_constructor`; `use-late` exact terminal event oracle |
| Reject wrong JSON shape, status, malformed/oversized/truncated/EOF response | session shape/framing tests; existing qualifier use-control matrices |
| Preserve closed route and old response typing | `test_changed_use_query_refuses_before_socket_access`; `test_only_canonical_use_route_admits_array_response` |
| Preserve custody, connection, deadline/no replay | standalone query custody/deadline and every-exchange loss tests; combined every-exchange loss/final custody tests |

Initial serial focused verification passed: volume25 tests in10.033s; resources17 in
41.760s; session17 in0.370s. The final malformed control matrix reran one test in5.663s,
PASS. Before these passes, an oversized-body fixture triggered an expected receiver
close that the oracle misclassified as a transport failure; injection now sends a
bounded header-only oversized response. A preparation mutation was changed from
invalid JSON to valid changed metadata so the test specifically exercises custody.
The combined negative matrix uses the normal five-second budget except its deliberate
slow control; an inherited 0.2-second budget was insufficient for the longer path.
An initial root invocation accidentally overlapped the two focused suites; those
results were not accepted as final verification. Final focused runs were serial.

## Independent review and regression RED

Three independent review lenses ran against the39751-byte scoped code/test/runbook/
evidence diff. Edge and verification reviewers returned no findings. Blind review
filed seven findings: missing final evidence, final-query error coverage, post-create
reference coverage, safe public query-timeout coverage, unreachable type branch,
standalone handoff EOF observation and destination-match coverage. Each received an
individual verdict/evidence row before grouping in the Build record. All route to
small local patches/tests/documentation; no public runtime surface is added.

The root reproduced the standalone handoff defect before its production fix:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_volumes.py' -k observable_eof_during_final_evidence
```

One test/two subcases failed `Refusal not raised`, before and after construction,
exit1 in0.120s. EOF was synchronized to become observable during final evidence
validation, after the transport's prior idle check. The fix mirrors the existing
combined adapter's immediate idle/budget checks around its trusted constructor.

Final focused review-fix verification passed serially:

```sh
python3 -m unittest discover -s platform/deployment/tests -p 'test_volumes.py'
python3 -m unittest discover -s platform/deployment/tests -p 'test_resources.py'
```

Volume:28 tests in10.685s, exit0. Combined:18 tests in41.110s, exit0. This includes
`test_observable_eof_during_final_evidence_refuses`,
`test_reference_after_create_and_destination_match_refuse_without_cleanup`,
`test_public_use_query_timeout_is_safe_and_suppresses_constructor`, and
`test_final_use_query_invalid_outcomes_refuse_without_constructor`. All seven review
findings are addressed; none deferred. The redundant response-type branch was removed;
production response shape remains enforced in the closed-route transport parser.

## Frozen-source qualification

Run `c3173b72-8c5a-4e8b-ac3d-8132702ac262` passed preparation/toolchain but image collection
refused `registry/manifest_response_invalid`, exit2. Its incomplete empty image directory
and protected preparation/tool receipt are preserved unchanged; no qualification was
repaired or asserted. Replacement run `70727ea5-e47d-4753-8b41-33086f7ce76a` passed all
three stages with final production/qualifier sources:

```sh
python3 platform/deployment/dev.py prepare --target platform/deployment/environments/kdg-local.json --run-id 70727ea5-e47d-4753-8b41-33086f7ce76a
python3 platform/deployment/toolchain.py qualify --target platform/deployment/environments/kdg-local.json --run-id 70727ea5-e47d-4753-8b41-33086f7ce76a
python3 platform/deployment/images.py qualify --target platform/deployment/environments/kdg-local.json --run-id 70727ea5-e47d-4753-8b41-33086f7ce76a
python3 /tmp/env-volume-use-public-proof.py 70727ea5-e47d-4753-8b41-33086f7ce76a
```

The temporary public harness uses existing owner qualifiers only. It checks explicit
expected exit/code pairs, safe output, current-use query counts, thirteen retained
file hashes/inodes/modes/mtimes and preparation/startup source snapshots. The protected
result record retains every exact command and result; the harness is not a new delivery
entry point or generator.

All **54 public checks passed**, exit0 for the temporary harness:25 combined controls,
25 standalone volume controls (all except separate missing-preparation control), network
and image positives, and pinned CLI refused-create/create-to-start positives. Individual
negative commands exited2 with their exact expected code; positives exited0. Every result
kept runtime_ready=false; no stderr or checked sensitive markers appeared. Combined
positive/existing retained32/29-request sequences with two use queries; standalone
positive/existing retained5/4 requests with one. Exact independent fixture oracles enforce
one connection and no replay. Both CLI fixtures retain synthetic_boundary_proven.

All thirteen retained evidence files kept identical hashes, inodes, modes and mtimes;
preparation/startup source snapshots also remained identical. Protected result record:
`.local/volume-use-qualification/70727ea5-e47d-4753-8b41-33086f7ce76a.json`
SHA-256 `7be0366459c733c21801b7bc8d81df6c771ae549b8b81c14b5434b1c18821dc6`.

## Final regression and closure

`python3 -m unittest discover -s platform/deployment/tests -p 'test_*.py'`
passed **386 tests in186.462s**, exit0. Output is retained at
`/tmp/env-volume-use-regression.log`. The complete suite includes every matrix row and
all review-fix tests; no expectations were changed to dismiss an unexplained failure.

`python3 platform/deployment/dev.py up --target platform/deployment/environments/kdg-local.json
--run-id 70727ea5-e47d-4753-8b41-33086f7ce76a` exited2 with `docker_28_required`,
`runtime_ready=false`. The observed Docker27.0.3 remains below the >=28 prerequisite;
no host upgrade, actual container or SQL execution occurred. A supported daemon still
refuses the undelivered runtime adapter.

Affected Python syntax, scoped whitespace and local Markdown links pass. All seven
review findings are fixed; none deferred. Current concurrent epics.md and Leave
implementation-plan/planning-handoff edits remain outside the scoped commit. No
accepted ADR, dependency pin, shared UI or agent-context file changed.

ENV remains open for volume freshness/initialization/reuse, bootstrap semantic/secret
safety, execution-time image/resource enforcement, actual startup/health/bounded
stop/reset/recovery and target PostgreSQL compatibility. Existing P1/SERVICE generator,
owner migration/fixture/current-Access and provider/device gates remain undelivered.
Continue bounded ENV/scaffold work before dependent Identity/Access/WRITE/KDG delivery.

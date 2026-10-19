---
title: 'ENV owner-check timeout diagnostics'
type: 'bugfix'
created: '2026-10-19'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b37645394aa9fe71810308c0cfa0a15b23be1ca0'
context:
  - '{project-root}/platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md'
---

<frozen-after-approval reason="standing bounded ENV implementation and synthetic verification approval">

## Intent

Owner custody/deadline checks outside DockerSession.exchange can exhaust the total
budget without its request diagnostic. Add safe optional owner_failure output at
those existing timeout-detection boundaries so an operator can distinguish owner
checks from a Docker request. This resolves the diagnostic blind spot, not the
unconfirmed cause of previous actual timeouts.

## Boundaries & Constraints

Always preserve current check order, short-circuiting, original refusal/cancellation,
deadlines, source/config/resource checks, one connection and cleanup authority. The
optional diagnostic must never introduce a refusal, replace an error, reset a budget,
retry, reconnect or emit on success. Capture the existing acquisition/fresh current
checks and FreshGuard.check's outer current/idle/budget boundary. Identify where
expiry was detected, not which underlying check or Docker call caused it. Mark a
budget already exhausted at observation entry without blaming the following check.
Use exactly schema_version=1, scope, check, elapsed_ms with closed vocabularies and
bounded integer elapsed time. Keep owner_failure separate from docker_failure;
valid nested/original observations survive outer cleanup exceptions through existing
bounded exception-chain handling. Existing stage/code/runtime fields and Docker
observations retain their semantics. No values from paths, IDs, commands, fixtures,
credentials, payloads or exception text enter this optional object.

Never optimize/remove custody reads, alter existing timeout/error precedence,
automatically recover/remove/adopt retained resources or infer old failure causes.
No new public control, SQL admission, generator/service, dependency/port change,
CLI continuation or runtime readiness. Preserve all current concurrent files/index,
receipts/state and Docker resources. No Leave, Identity/Access/WRITE/KDG consumers,
production/account/access/provisioning/deployment/pilot work or push.

## I/O & Edge-Case Matrix

| Scenario | Input / state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Local timeout | Acquisition/fresh custody or guard outer budget raises existing timeout | Original refusal plus selected owner checkpoint/elapsed | Existing stage/code |
| Already expired | Budget exhausted at entry | Explicit already_expired check; original checks still execute in their existing order | No causal attribution |
| Nested cleanup | Original owner timeout followed by cleanup refusal | Original safe owner observation retained; wrapper stage/code retained | Existing cleanup behavior |
| Request timeout | Docker exchange already supplies docker_failure | Existing request diagnostic retained; no fabricated owner attribution | Existing transport refusal |
| Success/other error | Valid checks or custody refusal/cancellation | Same result/error, no fabricated owner timeout | Unchanged precedence |
| Invalid observation | Clock/attribute failure, invalid metadata, hostile exception text | Optional metadata omitted; original outcome preserved | Never stringify |

</frozen-after-approval>

## Code Map

- platform/deployment/dev.py: reuse typed diagnostic validation and refusal_result's
  bounded raw exception traversal; private owner observation helper, separate field.
- platform/deployment/resources.py: acquire.current, fresh_session.current and
  FreshGuard.check wrap exact existing callbacks; do not refactor lifecycle/ownership.
- tests/test_resources.py: owner fixtures, deadline injection, event and connection
  assertions; integrated public qualifier acceptance RED using synthetic inputs only.
- tests/test_docker_session.py: serializer privacy/type/chain/clock regressions and
  existing transport tests. No actual Docker or prerequisite qualification in child.

## Tasks & Acceptance

- [x] Add deterministic public-output ATDD RED for owner timeout without request metadata.
- [x] Implement selected owner observation/serialization and exact boundary wiring;
  focused TDD protects all matrix cases and unchanged custody/refusal behavior.
- [x] Root verifies affected owner/transport and selected process regressions, exact
  requirement mapping and five impacts.

Given an isolated synthetic owner whose custody work consumes its unchanged budget,
when the existing timeout surfaces through the qualifier, then safe owner_failure
identifies its detection boundary and no downstream handoff/mutation/success occurs.
Given unchanged ordinary controls or existing transport failures, when observed,
then behavior and Docker diagnostics remain unchanged except optional local-timeout
metadata. No fresh actual-Docker/full-suite readiness is inferred from prior receipts.

## Implementation Notes

bmad-help selects this diagnostic prerequisite before remaining ENV continuation.
No intent gap or irreversible action; medium footprint (two production modules,
two focused test owners and documentation) routes dispatch. Standing user approval
covers implementation, dirty concurrent preservation and isolated synthetic checks;
no repeated planning or owner acknowledgement. Root owns docs/verification/review.
Source baseline/checkpoint is in .local/owner-timeout-diagnostics/checkpoint.json.
Scope/check choices are internal: acquisition/custody, fresh/custody, guard/budget;
already_expired is valid for each scope. Do not add fine-grained source subcheck
profiling or a general telemetry framework in this item. Earlier failures remain
unexplained. Existing diagnostics' separate ancestry investigation is not changed.

## Verification

Run smallest failing acceptance before implementation, then affected session/owner
unit tests and selected existing process/cleanup tests with retained exact commands,
logs and results. Root will choose affected suites from the changed boundaries;
no new actual Docker setup, full674-test claim or root npm verification is required.
Record scaffold (existing owner only), UI (none), context (none), documentation and
ADR0023 (applies, no accepted edit) decisions in owner evidence/runbook/KDG handoff.

Initial root verification: baseline acceptance RED1 FAIL (missing owner_failure), focused6
PASS;328 module/class tests PASS, four selected process cases pass across original
prefix and unchanged isolated repeat.74 source/test bindings stable. Initial network
request-count and backend-positive CLI-liveness failures remain retained with
unchanged current/baseline repeats; cause/change attribution unconfirmed. No limits,
assertions or expectations changed. Full-suite/actual-Docker proof is not claimed.
All six matrix rows have named executed passing tests in the evidence; five impacts
are recorded. Workflow review and scoped local commit follow this verified artifact.


## Review Triage Log

All three independent layers completed before triage. Verification-gap review found
no gaps; its public Unix-fixture rerun was sandbox-blocked before behavior, while
root's authorized isolated run passed. Each other filed finding is retained below.

| ID / layer | Verdict | Evidence and route |
| --- | --- | --- |
| B1 blind | medium | Entry observation catches BaseException before yielding, so injected KeyboardInterrupt/SystemExit is swallowed and custody proceeds. Patch: propagate entry cancellation; preserve original failure during exit annotation. |
| B2 blind | medium | acquire's direct final idle/budget pairs and fresh_session's pre-constructor pair are outside the selected observations. This pre-existing residual blind spot is real, independent of the added boundaries. Defer broader coverage; document the limitation without claiming complete owner-timeout coverage. |
| B3 blind | low | Generic acquisition expired-entry coverage does not exercise acquire.current ordering. Patch: integrated expired-entry test; no new production branch. |
| B4 blind | low | Existing nested tests manually link exceptions; they do not exercise context-manager cleanup after the timeout. Patch: integrated owner exit refusal and preserved diagnostic/actions. |
| B5 blind | low | Fresh executable callback always succeeds in the added test. Patch consumed-budget, refusal and cancellation cases at that existing second callback. |
| B6 blind | low | Clock failures are covered but deadline callback failures/invalid results are absent. Patch direct helper outcome-preservation tests. |
| B7 blind | low | Seven commands depend on ignored local runner/plan; clean checkout lacks exact selections in committed evidence. Patch committed evidence with direct commands. |
| E1 edge | medium | Independently identifies the same entry-cancellation swallowing as B1. Group with B1 for the single propagation fix and regression test. |
| V1 root verification | maybe-false | Initial unchanged network timing assertion failed; unchanged current and baseline repeats pass and observer is not in that path. Change contribution/cause unconfirmed. Defer unverified medium timing investigation; retain original failure. |
| V2 root verification | maybe-false | Initial CLI-backend process control correctly refused after CLI departed; exact current/baseline repeats pass. Original return code/signal timing absent, so change contribution/cause unconfirmed. Defer unverified medium liveness investigation; retain original failure. |


Review patches applied by the original implementation agent: entry catches Exception
rather than BaseException; cancellation RED four subcases observed first. Added
integrated acquisition expired-entry and owner-exit cleanup tests, executable custody
expiry/refusal/cancellation, invalid deadline and entry/exit cancellation cases.
Child scoped final42 tests PASS. Root final verification follows on separate bindings.
B1/E1 and B3–B7 direct corrections are applied; B2/V1/V2 appended individually to
existing deferred work. Frozen intent and every original failure log are preserved.


## Completion

Final reviewed source: 337 distinct selected tests PASS across recorded calls;
39 session,15 gate,18 image,31 volume,158 pinned,44 resource tests and four process
cases together, plus27 network cases and its unchanged isolated failed-case repeat.
The final combined network group retains one failure; repeat PASS is not an
explanation. No complete deployment-suite/network-group PASS is claimed. All74
final source/test hashes and exact verbose passing IDs/log hashes verified; no
skips. Exact commands, timings, requirement mapping and five impacts are in
ENV_OWNER_TIMEOUT_DIAGNOSTICS_EVIDENCE.md. Three review layers complete, all eight
filed findings individually triaged; direct patches verified and three follow-ups
appended to deferred work. Existing uncertain resources/receipts and concurrent
files/index preserved. Scoped local commit only; enclosing ENV/dependent gates open.

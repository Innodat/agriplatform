---
title: 'ENV safe Docker failure diagnostics'
type: 'feature'
created: '2026-10-19'
status: 'done'
baseline_commit: '6ccd126894fa5a029c043285d068bf40103423ce'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md'
---

<frozen-after-approval reason="standing approval for bounded ENV implementation and isolated synthetic verification">

## Intent

**Problem:** Two retained backend-qualification timeouts omit the failing Docker
operation and transport phase. A passing repeat cannot diagnose either failure.
**Approach:** Add selected failure metadata to the existing DockerSession and existing
development/startup-qualification JSON errors so future failures can be investigated.

## Boundaries & Constraints

**Always:** Keep existing stage/code, exit2, runtime/setup gates, route validation,
request/response bounds, deadlines, permanent connection closure, no replay and
cleanup/lost-custody behavior. An optional `docker_failure` contains exactly
schema_version=1, operation, phase and elapsed_ms. Operation is a closed category
derived only after the existing request validator accepts it; unvalidated requests
use `unvalidated`. Categories cover only existing daemon/version, image inspection,
network/volume create/inspect/remove/use, container create/inspect/archive/start/stop/
remove and exec create/inspect/start. Phase is one of validate/connect/idle_before/
send/receive/idle_after/budget_after. elapsed_ms is a nonnegative bounded integer
derived from monotonic time, capped at2147483647; zero is valid. Capture before close.
Reusing a closed session must not replace its original failure diagnostic. Formatting
revalidates exact types/keys/enums and omits malformed metadata. A bounded cycle-safe
exception-chain walk preserves the earliest valid Docker failure through cleanup
exceptions without changing the outer failure's stage/code. Ordinary failures without
this metadata retain their exact existing JSON shape; successful output is unchanged.

**Never:** Raw routes/query strings, resource identifiers/names, socket paths, bodies,
headers, environment, SQL, hashes of secrets, response excerpts or exception text in
diagnostics. No generic logger/service/runner, retries, adopted resources, cleanup
permission, deadline extension, migrations/accounts/grants, Auth runtime/CLI continuation,
Identity/Access/WRITE/server KDG, Leave/editor, production/deployment or real-data use.
Historical failure causes remain unverified; metadata identifies observation only.

## I/O & Edge-Case Matrix

| State | Expected behavior |
| --- | --- |
| Valid request times out during connect/send/receive | Original refusal plus correct closed operation/phase/elapsed; connection closes, no replay |
| Bad framing or expiry after response processing | Distinguish receive/idle_after/budget_after; retain existing rejection |
| Invalid request or sensitive input/exception | No socket for rejected route; only unvalidated category; no sensitive values serialized |
| Cleanup wraps original error or session reused | Earliest valid diagnostic survives; outer stage/code unchanged; no new operation |
| Forged/malformed/cyclic diagnostic chain | Exact validation, bounded traversal, no payload/stringification leak |
| Ordinary refusal/success | Existing JSON shape and behavior |

</frozen-after-approval>

## Code Map

Paths relative to platform/deployment/. dev.py owns Refusal, _docker_request,
DockerSession.exchange and public error JSON; add closed categorization/validation
and one shared safe refusal formatter there. tests/qualify_startup.py uses that
formatter for Refusal only. startup.py finally can replace an original exception
with cleanup refusal: preserve attribution through exception chaining, without
changing that lifecycle behavior. tests/test_docker_session.py has Peer and existing
ScriptedSocket fixtures; tests/test_resources.py covers owner cleanup. Reuse these
fixtures, no new transport. Child owns production/no-socket/private-peer tests;
root owns actual qualification, documentation/evidence and final acceptance.

## Tasks & Acceptance

- [x] dev.py and tests/test_docker_session.py: observe acceptance RED first; focused
  TDD for exact safe metadata, framing/timeouts, malicious canaries and no replay.
- [x] tests/qualify_startup.py and existing test fixtures: prove emitted error JSON,
  original failure through cleanup, malformed metadata, ordinary shape compatibility.
- [x] DEVELOPMENT.md, ENV_DOCKER_FAILURE_DIAGNOSTICS_EVIDENCE.md, this Build and KDG
  handoff/memlog: record requirement-to-test commands/results and all five impacts.
- [x] Root verifies affected suites, fresh source-qualified actual backend control,
  prior controls/public up refusal, full deployment regression and three-layer review.

Given a private daemon failure, when the existing qualifier emits its error, then
the selected diagnostic locates the failed exchange without leaking injected secrets
or altering deadlines/custody. Given unchanged success, when actual synthetic backend
qualification completes, then existing readiness gates and retained evidence remain.

## Implementation Notes

Selection via bmad-help [BD]: diagnostic capture is the next existing ENV prerequisite;
runtime expansion would reach additional unqualified setup and privilege boundaries.
Standing implementation/preservation authorization covers the dirty concurrent tree
and this concrete bounded item; no repeated acknowledgement or permission checkpoint.

Acceptance RED for missing docker_failure precedes implementation; root independently
verifies25 transport tests0.480s,15 gate tests1.191s and the existing one-test/four-case
actual private cleanup fixture15.191s. Production changes only dev.py and the existing
startup qualifier formatter. startup.py/resources.py/lifecycle predicates unchanged.
The finite clock mock becomes a receive-driven clock with the same5s bound and
timeout expectation; no assertion is weakened. Truncated ancestry omits attribution,
and diagnostic capture failure cannot mask the transport refusal or prevent close.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1 divergent cause/context chooses later branch | maybe-false, medium-unverified / defer | A manually forged divergent graph can select cause last. Search finds only exchange's new `raise refusal from error` in this call graph; its cause/context share the original observation, while startup cleanup uses implicit context and the same closed session. A reachable owner sequence producing distinct observations on divergent branches would settle relevance. |
| Blind2 duplicate references spend32-walk budget | low / reject | Seventeen artificial double-linked nodes can omit optional attribution safely. Existing cleanup chains are short; omission preserves original refusal and privacy. Changing traversal guards for this uncommon graph adds complexity without everyday harm. |
| Blind3 initial observation clock outside try | medium / patch | New first clock read precedes try; injecting an initial error with an existing stream bypasses permanent close, unlike a budget-clock failure inside the prior implementation. Move it inside the existing handler; focused regression. |
| Blind4 close exception replaces transport error | medium / defer | close can raise before normalization; baseline has the identical close call before timeout/OSError mapping. This predates diagnostic capture. Injected close failure plus original transport failure would characterize an owner fix. |
| Blind5 category test calls helper with unvalidated routes | false / reject | Helper unit coverage does not bypass production validation: exchange invokes _docker_request before _docker_operation, and rejected-input acceptance proves no socket acquisition. Accepted mutating-route private cleanup tests exercise integration. No miscategorization or acceptance defect demonstrated. |
| Blind6 no partial-send mutating fixture | false / reject | There is no sendall progress-dependent branch: every sendall exception captures send phase then permanently closes; explicit reuse tests prove no new socket/transmission and existing lost copy/start tests prove no replay after uncertain mutation. Recording a byte prefix cannot change this path. |
| Blind7 ignored verification wrapper lacks clean-checkout reproduction | low / patch | Existing tracked qualifier/runbook exposes controls, but new ledger only gives scratch wrapper modes. Add direct tracked control mappings and retained wrapper identity so a reader can reproduce controls without that ignored file. |
| Blind8 Code Map requires startup.py edit | false / reject | Code Map explicitly says preserve attribution without changing lifecycle behavior; formatter reads existing implicit context. It does not prescribe changing startup.py. Suggested spec edit also rejected by workflow rule. |
| Edge1 initial observation clock outside try | medium / patch, grouped with Blind3 | Same new unprotected clock read and same demonstrated open-stream state; use the identical minimal fix/regression. |

Verification-gap layer: no verification gaps found. Blind floor8 arithmetic retained
in reviewer response. All8 blind findings and1 edge finding individually triaged.

## Verification

All six matrix rows map to executed passing tests D1–D6 in the
[evidence ledger](../../platform/deployment/ENV_DOCKER_FAILURE_DIAGNOSTICS_EVIDENCE.md).
Acceptance RED precedes implementation; initial-clock regression separately RED then
GREEN. Root reviewed-source26 session tests0.551s/15 gate tests1.412s PASS. Original
private-process/four-case cleanup test PASS15.191s and runs again in full regression.

Reviewed-source aa31b4ab qualifies fresh preparation/toolchain/images and actual backend
96.723s,13 receipts unchanged. Public up expected exit2/runtime_adapter_unqualified
0.052s; runtime/setup false. Pre-review A/B controls remain explicitly pre-review
compatibility evidence. Concurrent Deals deltas are selected and preserved.

Reviewed-source full638 first fails the previously retained no-eof witness assertion,
log90438f7a; the unchanged nine-case focused test PASS10.422s. One unchanged full638
rerun PASS638.108s, no skips, log4140987f. Both failures and passing results remain;
original cause/change attribution unverified. Earlier pre-review900s outer timeout
and637-test partition completion are also retained. No assertions/deadlines changed.

Three reviews complete:8 blind findings and1 edge finding individually triaged;
verification-gap none. Two minimal patch groups: protect initial observation-clock
failure and document direct tracked qualification commands. Two investigations
appended to deferred work; prior investigations untouched. Full results/digests are
in the evidence ledger and protected qualification records.

All five impacts recorded: existing scaffold transport/qualifier enhanced; shared UI
and agent context unchanged; DEVELOPMENT/evidence/handoff updated; ADR0023 applied
without changing accepted ADRs. Frozen intent, approved target, reviewed source and
concurrent index/content are preserved. TypeScript7.0.2/mail15484 unchanged. All older
uncertain resources/receipts remain; no new generator, runtime admission or dependent/
production action. This diagnostic increment is complete; enclosing ENV is not.

# Candidate own-edit request adapter — 2026-10-26

`web/src/edit.ts:editCapture` consumes the generated edit command, receipt and error
contracts. It remains unconnected to Auth, browser/editor, queue and API startup. The
caller supplies the pinned account, organization, capture target, original generated
command and its existing `{signal,isCurrent}` generation fence. The original bearer,
identity primitives and serialized nested command are captured before the first await.
Exactly one selector-free same-origin PUT sends JSON, no-store and redirect refusal.
The UTF-8 request ceiling is131072 bytes, including the exact boundary. This byte check
occurs after synchronous JSON serialization; preflight cannot be preempted or heap-bounded.
An elapsed preflight deadline prevents transport. No traversal engine is introduced.

Only a closed v1 capture.edit committed receipt matching the original operation and
capture acknowledges success. Revisions remain canonical positive signed-bigint decimal
strings through9223372036854775807. A generated409 revision conflict exposes only
`current_revision` with its exact safe status/identifier; other errors cannot carry this
field. The generated error union drives consuming TypeScript narrowing. No upstream
message, response snapshot, exception or bearer is returned or logged. Original-definition,
questionnaire and domain validation remain with the backend.

The required caller fence must represent the existing pinned session/account/organization
generation, including A→B→A. The owner must abort on replacement, logout and disposal;
predicate exceptions fail closed. Initial cancelled/stale/throwing leases are refused
before payload getters or toJSON.
Predispatch and publication checks evaluate the delegated predicate before their final
owner-signal read, suppressing synchronous predicate-triggered abort as well as stale
successes/errors. The same demonstrated race correction applies to app-owned recovery;
its characterization cases prove zero dispatch and no receipt/error publication. One
original monotonic deadline, selected at most10 seconds ahead, is checked after synchronous
preflight and across asynchronous headers/body. Transport ignoring abort cannot keep those
asynchronous waits pending indefinitely.
Responses require JSON/private/no-store, at most16384 bytes, fatal UTF-8, duplicate-key
and Unicode checks and closed DTO shapes. Late, rejected, overflow and abandoned bodies
are cancelled best effort. A cancellation or deadline after dispatch may still commit.
No result asserts rollback, absence or safe allocation of a new operation. There is no
automatic retry, recovery call, token refresh, input/store mutation or Synced feedback.

Behavioral ATDD against the explicit non-dispatching stub observed **44 failures and
one pass**. The first implementation passed45 cases and the pre-review suite reached48 edit cases;
its affected116-test and strict TypeScript/parity results remain historical checks of
that earlier tree. Post-review regressions first observed six failures covering edit and
recovery predicate-triggered aborts, rejected-lease traversal and undefined direct answers.
The final two edited test files pass **95 cases:54 edit and41 recovery**. Positive cases
retain omitted optional fields and nested `details: undefined`; direct undefined answer
entries fail without silently dropping input. HTTP201/202 cannot acknowledge, concurrent
operations cancel independently and every generated enum error identifier is checked.
Root final verification passes **124 affected edit/recovery/entry tests**, both strict
TypeScript7.0.2 configurations and all three scaffold parity checks. All three review
layers completed; nine findings were addressed, none deferred.

The original acceptance stub and first deadline mutant source were not captured at their
original execution time. Their original logs remain historical observations, without a
claim of retained original source provenance. Fresh, honestly reconstructed controls now
retain exact tested source and patches: the non-dispatching stub, `response.ok` mutant
and removed preflight deadline guard each fail their focused test. Post-review RED source
and test copies bind the six observed regressions. All post-review controls/logs/capsule
live separately under the retained `post-review/` directory; earlier capsules/logs remain
unchanged. The edit type fixture adds8 negative cases including conflict narrowing.
No dependencies were installed.

The [source-bound record](evidence/edit-adapter-20261026.json) contains exact commands,
exit codes, source/log hashes, requirement traceability and retained failed attempts.
Initial Node test child isolation was unavailable in the sandbox; direct Node execution
established behavioral RED, and final combined verification uses `--test-isolation=none`.
An optional recovery-entry test invoked directly requires its compiled Auth proof harness;
that exploratory invocation failed on the missing compiled module. The required existing
recovery/entry suites then passed through their direct-source harness. No claim is made
for rerunning the compiled recovery-entry/Auth integration proof in this slice.

Scaffold impact: existing recovery transport conventions and generated contract tooling
are reused without changing their owner or templates. The scaffold Auth lease predicate
is a pure captured-state closure; it does not invoke the delegated callback responsible
for this race, so there is no corresponding template correction. KDG write/target/error semantics
stay local; no generic SDK or lifecycle extraction. Shared UI, agent context and ADR
impact: none. Documentation: this evidence/record, appended contracts and prepended
handoff, preserving all historical bytes. Generated types/schema, Auth/entry and backend
sources stay unchanged. Recovery has only the companion predicate-before-signal race
correction and characterization tests. Backend/native suites were not rerun and no new native,
real Auth/Access, browser/editor/queue/startup or release qualification follows. Existing
release gates, retained resources, concurrent work and approved dependencies are preserved;
fingerprints/HMAC remain deferred. No Docker/native, migration, provisioning, deployment,
production/pilot, Leave/editor or cleanup action occurred.

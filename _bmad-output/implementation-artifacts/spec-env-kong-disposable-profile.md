---
title: 'ENV pinned-image disposable Kong profile'
type: 'feature'
created: '2026-10-19'
status: 'done'
route: 'dispatch'
baseline_commit: 'fb6a43029673f8e59e9f06b4e1e57a3c4c00e8f3'
review_loop_iteration: 0
---

<frozen-after-approval reason="standing bounded ENV implementation and isolated synthetic verification approval">

## Intent

Kong's source intent is deliberately unadmitted and uses restart unless-stopped.
Before any gateway execution, establish a separate closed disposable create profile
against the exact selected image defaults. Extend the existing Kong boundary control
to verify that profile and current image configuration, while still refusing creation.

## Boundaries & Constraints

Always retain source-derived Kong helpers/markers/three-file intent independently.
Read the selected pinned Kong reference through the existing Docker API1.48 session;
require current matching image Id, linux/amd64 and exact closed Config. Public fixture
authority is the independently inspected pinned config
sha256:3cefb958bcd694597b65adc00053a762b1f9a6df3c6031af528d052d75a64e1a.
Retain the public Config as a source-bound fixture with provenance and explicit
observed-versus-runtime limits. Never accept arbitrary inherited Env/Labels, volumes,
entrypoint/health/shell defaults or unknown Config fields.

Build a separately named detached disposable request from validated source intent:
restart no/MaximumRetryCount0, AutoRemove false, private cgroup namespace, privileged
false, 2GiB Memory/MemorySwap, 2 CPUs, PidsLimit256, LogConfig none/empty Config,
no mounts/binds, exact owned network/aliases and only127.0.0.1:55481->8000 publication.
Set User kong, WorkingDir /, source sh/-c command, and pinned Healthcheck/StopSignal
explicitly. Retain source ports with exact selected image port union (8000/8001/8088/
8443/8444 tcp), image Env defaults and label defaults through documented Docker merge
expectations; do not claim actual container-merge conformance. Validate the complete
request tree independently against its closed expected profile before classification.

In the existing consumed boundary attempt, check original prerequisites/custody and
healthy PG before/after image/profile validation. Require both source and disposable
create requests to remain docker_request_invalid at the classifier, without exchange.
Publish existing boundary fact only after normal cleanup. Ordinary controls remain
unchanged. Preserve errors, deadlines, no repair/replay, source/evidence/fixture/image
custody and cleanup authority; original CLI stays terminated, readiness false.

Never grant a Docker route or Kong execution/copy/start, resume CLI, add generic
service tooling or native-token minting, run additional SQL, production/data/account/
access/infra/deployment/push work. Synthetic markers do not prove Auth routing.
Actual image inspection is read-only; all delivery verification uses private synthetic
fixtures. Preserve concurrent work/index,52 prior prerequisite files, uncertain Docker
resources, existing owners, pinned baseline incl TS7.0.2/mail15484.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Failure |
| --- | --- | --- | --- |
| Valid boundary | All prior proofs, selected image Config exact | Independent safe request verifies; both creates refused; fact after cleanup | No runtime claim |
| Image change | Wrong Id/platform/Config/default field/type/extra key | No completion or mutation; consumed attempt | Existing safe refusal |
| Profile change | Altered nested host/env/script/image/port/mount/health/user/default field | Exact validation refuses | No input disclosure |
| Budget/custody/cleanup | Expired/cancelled/replaced input or failed cleanup | Existing precedence/retention/no replay; no fact | Existing contracts |
| Ordinary control | No Kong opt-in | No new image Config check or changed facts | Existing behavior |

</frozen-after-approval>

## Code Map

- `platform/deployment/create_profile.py`: keep Kong source-intent functions;
  add exact image Config validator, separate disposable request/validator, documented
  expected default merge. Reuse _exact_tree, no new generic service engine.
- `platform/deployment/fixtures/`: new small public pinned Kong API Config fixture
  and provenance; root observation at .local/kong-execution-profile/pinned-image-api-config.json.
- `platform/deployment/resources.py`: verify_kong_boundary consumes attempt, observes
  selected image and validates both requests before requiring classifier refusal.
- `platform/deployment/dev.py`: bind new fixture/provenance in SOURCES only; Docker
  transport/admission must remain unchanged.
- `platform/deployment/tests/test_create_profile.py`: independent full image/request
  oracles plus recursive key/type/nested/extra/missing/default mutation coverage.
- `platform/deployment/tests/test_pinned_execution.py`: existing KongBoundaryOwner
  and synthetic image peers; image/profile failure/order/current/cleanup coverage.
- `platform/deployment/tests/test_resources.py`: existing private-process Kong cases
  with exact selected image fixture, plus image/profile rejection/privacy checks.
- `platform/deployment/DEVELOPMENT.md`, ENV_KONG_DISPOSABLE_PROFILE_EVIDENCE.md,
  `apps/kdg-capture/docs/next-session.md` and .memlog.md: root-owned evidence/impacts.

## Tasks & Acceptance

- [x] Existing owner/process tests: observe acceptance RED for closed image/profile.
- [x] Profile/fixture/owner/test files: focused TDD, independent oracles, negatives.
- [x] Existing ordinary controls and Kong process checks: prove no admission/cleanup regressions.
- [x] Docs/evidence: exact commands/results, source bindings, five impacts and remaining gates.

**Acceptance Criteria:**
- Given the Kong boundary, when the exact selected image is observed, then source and
  safe disposable profiles validate independently and both create requests stay refused.
- Given altered image/profile/defaults, when the boundary runs, then it fails safely
  before completion, consumes the attempt and preserves custody/cleanup contracts.
- Given successful verification, when cleanup completes, then only existing boundary
  facts appear and runtime/fresh setup stay false.

## Implementation Notes

bmad-help selects Build after bounded transport qualification. Read-only delegated
investigation and root API1.48 image observation settle defaults (User kong, empty
WorkingDir, SIGQUIT, kong health10s interval/timeout/retries10). No intent gap;
footprint crosses profile/owner/test/fixture files so dispatch. Root owns spec/docs/
evidence/review/commit; delegate owns code/tests/public fixture. No Docker mutations.
Checkpoint .local/kong-execution-profile/checkpoint.json binds17 concurrent files,
52 receipts and original index. Standing authorization covers dirty-tree continuation.

## Verification

Use PYTHONPATH=platform/deployment:platform/deployment/tests python3 -m unittest -v
with smallest acceptance/focused tests first, affected profile/owner/transport suites
then selected private process controls. Record exact selectors/counts/source and log
bindings, no runtime-content hashes. No full-suite or actual-Docker execution claim.


- Implementation sequencing deviation: initial acceptance assumption required one
  image observation, but joint custody correctly repeats them. That was not relevant
  RED. The owner draft preceded the corrected assertion; only the owned resources.py
  draft was temporarily saved/restored against baseline, corrected acceptance RED
  (Config validator count0!=1,1 test0.396s) then restored GREEN recorded. No historical
  acceptance-first claim. Focused19 PASS5.925s; attempted process2 failed sandbox bind
  EPERM, excluded. Root affected161 PASS35.299s and process6 PASS202.027s, no skips.
  167 distinct IDs;44/46 source frames stable. Full matrix audited against exact
  passing selectors in ENV_KONG_DISPOSABLE_PROFILE_EVIDENCE.md. All tasks complete;
  transport/admission unchanged, current fixtures/17 concurrent/52 prior prerequisites/
  17 previous transport evidence/index preserved. Three-layer review next.

## Review Triage Log


| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| B1 validator independence claim | low | Runtime validator shares the canonical builder; independent complete test oracles are present. Correct misleading docstring directly; patch, no logic change. |
| B2 explicit image response branches lack direct negatives | medium | Earlier selected-image mutation fails before the new exchange. Add targeted response cases for status/shape/identity/platform/variant; patch existing tests only. |
| B3 disposable classifier refusal lacks distinct failure tests | medium | Existing admission mock succeeds on first source call, leaving second-call guard unproved. Add second-call accidental admission/unexpected refusal cases; patch. |
| B4 new image-exchange interruption lacks direct tests | medium | Existing cancellation/deadline injection is elsewhere. Add cancellation/timeout/transport failure at explicit new exchange and no-replay assertions; patch. |
| B5 valid-shaped constructor mutation coverage | low | None-only cases prove absence refusal but not each shaped validation obligation. Extend existing test and assert constructor not reached; patch. |
| B6 reproduction mkdir lacks parents | low | Clean checkout has no ignored .local parent, so recipe fails. Change to mkdir(parents=True, exist_ok=True); direct documentation patch. |
| B7 inherited concrete tests repeat four executions | low | KongDisposableProfile inherits four test methods under new IDs; original167 IDs include4 duplicate source executions. Reuse only fixture/oracle helpers, preserving original tests once; patch. |

All7 findings individually verified/triaged before grouping. Edge returns[];
verification-gap review finds no gaps. No intent change, loopback or deferral.
B1/B2/B3/B4/B5/B7 implementation delegate test/docstring patches; B6 root evidence
recipe correction. Runtime logic and public Config authority remain unchanged.


- All7 review findings patched, no rejections or new deferrals. Delegate focused14
  PASS; root final160 affected PASS43.884s with46 stable source bindings, no skips.
  Four inherited duplicates removed, three new owner methods added:166 final selected
  IDs across final affected and retained6 process calls. No runtime logic changes
  during review; one docstring and2 unit modules differ from process frame,43 other
  bindings identical. Exact prior production source hash restored by reversing only
  the docstring in memory; process-helper diff hunks unchanged. Original logs/frames
  retained. Final matrix and all five impacts recorded in evidence/runbook/handoff.

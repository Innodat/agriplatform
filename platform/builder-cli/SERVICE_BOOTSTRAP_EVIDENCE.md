# Disposable service bootstrap evidence

Baseline `a43f0119c054f344f999e193083cf4dc9151678a`. This increment renders the first
standalone service shell through the existing builder's internal `test:generation`
harness. Its only emitted route is health. Service authentication/current Access,
database/domain routes, normal generation and complete P1/SERVICE remain undelivered.
All catalogue entries remain candidates; output reports generation_ready:false.

## Requirement-to-test mapping

| Requirement | Test/evidence |
| --- | --- |
| Pure deterministic bounded file map and seed/generated ownership | service-renderer.test.mjs: acceptance: deterministic bounded standalone service files with explicit ownership |
| Invalid/app/extension input refused | service-renderer.test.mjs: acceptance: refuse invalid, application and extension recipes before output |
| Explicit tools/no supplied output target | generation-guards.test.mjs: bootstrap refuses missing or relative tools and supplied output target safely |
| Successful probes reject wrong tool version/implementation/free-threaded runtime before output | generation-guards.test.mjs: successful probes reject unsupported uv/Python/implementation/free-threaded values before output |
| Failed evidence write remains a safe failure with retained incomplete output | generation-guards.test.mjs: unwritable proof manifest retains failed proof and emits only safe failure JSON |
| Bounded owned child/grandchild termination with truthful failure evidence | process-runner.test.mjs: timeout terminates own synthetic child and grandchild with failure evidence |
| Valid boundary owner keeps exact identity and valid package metadata | service-renderer.test.mjs: accepted boundary owner produces valid package metadata without changing identity |
| Own lock, clean frozen offline wheel-only installations | proof.json command records, lock provenance, per-environment source/lock hashes |
| Exact selected CPython/package versions | generated tests/test_runtime.py: test_versions, in both environments |
| Actual HTTP200/404/422/500/401/503/405; challenge/retry/Allow headers; no sensitive diagnostic content | generated tests/test_runtime.py: test_real_http_safe_errors, in both environments |
| Protocol Location/Content-Range and numeric code retained on actual wire | generated tests/test_runtime.py: test_protocol_headers_and_numeric_code, in both environments |
| Background/completed and fixed-length truncated failures never expose exception text or a second status | generated tests/test_runtime.py: test_completed_and_incomplete_response_failures, in both environments |

No mocked HTTP client substitutes for actual startup. Each generated test fixture
starts a separate isolated interpreter/Uvicorn on an ephemeral127.0.0.1 socket and
stops it normally. Probe routes exist only in the fixture process, never main.py.
The independent environments use copied wheels and only the generated owner path;
no qualification/application server source is imported.

## Commands and observed results

Use pinned Node26.11.1/npm12.2.0, TypeScript7.0.2, uv0.13.1 and ordinary
CPython3.15.0. README records full invocation and explicit cache/tool paths. Scope
is the observed Linux x86_64 host; other platforms remain unqualified.

```bash
npm run test --workspace platform/builder-cli
npm run type-check --workspace platform/builder-cli
npm run schema:check --workspace platform/builder-cli
npm run test:generation --workspace platform/builder-cli
```

ATDD RED: pinned node --test tests/service-renderer.test.mjs failed exit1 before
the renderer existed. Retained at deployment/.local/scaffold-generation/renderer-red.log.
Implementation suite:12 tests pass; type-check/schema check pass. Latest implementation
bootstrap proof-O6IYGZ passes its own lock/check, two frozen offline wheel-only installs
and three generated runtime tests in each environment. Exact commands, clean child
environments, exit statuses, logs/hashes and output ownership are in each proof.json.
Its timeout handling passed both generation guard tests after that final harness change.

Preserved investigation outcomes: explicit python3 tool was initially refused because
it is a symlink; correction follows the explicitly selected executable and verifies
its version. proof-TOBK2Q retains an offline universal-resolution failure on an uncached
Windows-only colorama branch. The generated manifest now explicitly resolves Linux;
no dependency pins were changed and no historical fixture lock was copied. Intermediate
passing proofs are retained; only final source-bound evidence supports completion.

Final root verification:15 builder tests pass, zero skipped/cancelled, in7.715s;
type-check/schema:check pass. Fresh final bootstrap `proof-dkwKDY` passes own offline
lock/check and two independent frozen wheel-only installs, each running all four
generated tests (4.98s/5.81s). Root command argv/results and23 unchanged input bindings
are in `deployment/.local/scaffold-generation/root-final-verification.json`; its
root-final logs retain stdout/stderr. The proof itself records13 unchanged source
bindings and seven unchanged output/lock hashes. No Docker operations, account changes,
migrations, provisioning, deployment or real-data use occurred.

All three review layers completed:12 findings individually triaged and addressed,
none deferred. Completed responses receive no second body; failed partial responses
remain truncated. The truncation probe intentionally produces Uvicorn's generic
"ASGI callable returned without completing response" diagnostic, without traceback or
sensitive content. Operational events contain only selected event/error_id JSON.
Review runtime/renderer RED and focused GREEN logs are retained beside root evidence.
The root also corrected application rejection coverage to use a schema-valid app.

Preservation audit:2487 pre-existing files outside five intended prior-file edits
are unchanged, including concurrent documents, previous builder templates, root lock
and qualification fixtures. Historical receipts/resources were not overwritten or
removed. New failed/incomplete/successful proofs are retained separately; no whole-
repository test or full P1/SERVICE readiness claim.

## Impact decisions and limits

Scaffold: pure internal renderer and service templates/harness added to existing builder.
The historical backend templates remain untouched/unproven. Shared UI: no UI changes.
Agent context: output guidance records actual commands, ownership and authority limits;
root rules unchanged. Documentation: builder runbook/evidence, mutable contract and KDG
navigation updated. ADR:0059,0031 and0023 apply; no accepted decision changed.

main.py is a create-once owner seed; the safe error adapter and generated guidance are
template-owned. The proof manifest records classifications/hashes and uv lock ownership.
This is a fresh disposable output proof, with no public output argument or owner-root
installer. Public generation, extension import/preservation, regeneration/journal recovery,
application shell and current Access proof remain consuming work. Health is liveness,
not authorization or readiness. Generated tests prove the health shell and explicit
completed/truncated failure cases; future routes retain their own authorization,
transaction and error contracts.

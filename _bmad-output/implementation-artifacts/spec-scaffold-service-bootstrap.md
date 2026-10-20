---
title: 'Disposable service scaffold bootstrap'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
baseline_commit: 'a43f0119c054f344f999e193083cf4dc9151678a'
review_loop_iteration: 0
context:
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
  - '{project-root}/platform/docs/architecture/contracts/api-errors-and-operation-recovery.md'
---

<frozen-after-approval reason="standing approval for bounded shared foundation and next disposable output proof">

## Intent

Recipe preflight works, but no scaffold output runs. Prove the first service-only
HTTP shell through the existing builder's internal candidate-bootstrap harness.
Generate disposable output, resolve its own lock and independently install/start it.
Keep the implementation proportional; no public generator or runtime framework yet.

## Boundaries & Constraints

Always reuse recipe validation, builder ownership and approved baseline. Candidate
patterns stay unproven; health/error proof is not service authentication/current Access.
Retain synthetic outputs/logs and all prior work/resources. Output has no repository
runtime imports or hidden packages. No broad Supabase credential settings. Public
generation, application/browser output, extensions/regeneration/journal installation,
Identity/Access/WRITE, DB/auth/providers/Leave/editor/deployment are outside this proof.
No public candidate flag or generate stub; bootstrap only through test:generation.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Valid service recipe | Deterministic file map from owning templates; no filesystem writes in renderer |
| Invalid/application/extension recipe | Safe refusal before output; no candidate promotion |
| Bootstrap harness | Fresh private directory under deployment/.local/scaffold-generation; preserve every existing output |
| Missing/wrong configured tool | Safe failure; never silently use host Python/download a runtime |
| Clean output | Own uv.lock, two fresh frozen offline wheel-only installs, no source/lock drift |
| Real local HTTP | Health200; unknown404, invalid422 and unexpected500 use safe envelope; preserve protocol semantics |
| Sensitive errors | Payload/exception sentinel absent from responses and captured diagnostic output |

</frozen-after-approval>

## Code Map

- `platform/builder-cli/src/recipe.ts`: reuse validateRecipe; do not expand supported patterns.
- `platform/builder-cli/templates/backend/`: historical floating dependencies/broad secrets;
  leave intact. Add narrowly scoped service templates under existing templates owner.
- `platform/builder-cli/package.json`, `tsconfig.json`, `tests/`: existing Node26.11.1,
  npm12.2.0, TypeScript7.0.2 tools; add test:generation and renderer tests, not another CLI.
- `platform/deployment/qualification/python/README.md`: tool invocation reference only;
  never copy its all-package pyproject/lock or import its runtime tests as generator input.
- Retained tool payload `platform/deployment/.local/kdg-toolchains/0cc4bc48-505e-41c1-8876-25b2d49b5694/payload/`
  has uv/uv0.13.1 and python/bin/python3 CPython3.15.0; node tools are in
  `ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/{node/bin/node,npm/bin/npm-cli.js}`.
- Warm cache `platform/deployment/.local/python-baseline-qualification/cache`; use
  ordinary offline uv commands. Root owns final socket verification/docs/audit/commit.

## Tasks & Acceptance

- [x] `tests/`: acceptance RED before renderer implementation, focused deterministic
  service output and rejection tests. Retain exact commands/output/exit codes.
- [x] `src/`: pure internal service renderer returns bounded relative file map and
  seed/generated classifications, after existing validation. Reject application and
  nonempty extensions. Render only known owner token, never execute templates or recipe code.
- [x] `templates/service/`: main.py owner seed, safe error adapter, minimal pinned
  pyproject and runtime tests/README/AGENTS. Health only, no protected/domain routes.
  Runtime fastapi0.143.0/uvicorn0.54.0/pydantic2.14.1; pytest9.1.1/httpx0.28.1
  dev-only, requires-python==3.15.0. No copied app requirements or database packages.
- [x] Safe errors retain error:string and add error_id:string, never turn numeric
  code into text. Use resource_not_found/validation_failed/internal_error; preserve
  HTTP status and required protocol headers. Return no raw errors/input/context.
  Unexpected exceptions must not leak through Uvicorn's default traceback logging.
  Test-only probe routes are fixtures, never generated production routes.
- [x] `scripts/`, package script: test:generation requires explicit absolute
  SCAFFOLD_UV/SCAFFOLD_PYTHON tool paths and UV_CACHE_DIR. Check selected versions;
  create a fresh ENV proof/output directory, no supplied write target. Resolve its own
  uv.lock with pinned uv (offline/no-config/no-python-downloads), lock --check, then
  sync --frozen --offline --no-build --no-install-project --group test --link-mode copy
  into two absent environments. Use clean child environment/no PYTHONPATH/plugins,
  bounded processes and retain safe logs, exact commands/results/source hashes.
  Verify versions and HTTP via generated tests in both environments, no socket skip.
- [x] Proof manifest records recipe/template/source identities and generated-versus-
  seed file hashes, uv-owned lock provenance, bootstrap_only:true/generation_ready:false.
  Preserve output on failure, report truthful partial outcomes; no recovery/deletion.
- [x] README documents actual commands, output boundaries and five impact decisions.
  Root updates mutable contract/KDG handoff and requirement-to-test evidence.

**Acceptance Criteria:**
- Given valid service input, when test:generation executes with pinned tools, then
  its independently installed output serves real loopback health/safe errors in both
  environments with unchanged source/lock and no repository server imports.
- Given unsupported input or unavailable tools, when attempted, then it refuses safely
  without rewriting existing output or claiming runtime/generation readiness.

## Implementation Notes

No intent gaps or irreversible action. New renderer/test entry merits dispatch.
Agent owns builder source/templates/scripts/tests/package only; root owns other docs.
Do not rerender BMAD, commit, invoke Docker or alter previous qualification fixtures.
Synthetic subprocess/socket escalation is authorized. Keep tree stable when reporting.

Implementation:12 builder tests/type-check/schema checks pass. Renderer RED exit1 retained. Latest implementation proof-O6IYGZ passes own offline lock/check and two fresh frozen installs,3 actual runtime tests each; preceding universal offline-resolution failure is preserved. Root audited matrix coverage against these executed tests; final independent verification/review follows.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1: second body after completion/incomplete body failure | medium / patch | Adapter tracks only start and sends unguarded termination. Edge tracing confirms traceback escape after background/length errors. Track completion and contain termination failures; add runtime probes. |
| Blind2: required redirect/range headers dropped | low / patch | Allowlist lacks Location and Content-Range; HTTP status alone is insufficient. Add explicit supported cases/tests. |
| Blind3: structured logging fields absent from actual output | medium / patch | proof-O6IYGZ runtime log contains only request_failed; default logging drops extra fields. Emit bounded structured diagnostic representation and assert it. No invented correlation context. |
| Blind4: numeric compatibility asserted only on model | low / patch | response helper cannot carry code. Add optional integer and real wire fixture rather than overclaiming model evidence. |
| Blind5: wrong-version test misses comparison | medium / patch | Node Python probe fails before version check. Successful stub probes must test exact unsupported uv/Python/implementation/free-threaded refusals. |
| Blind6: process-group cleanup untested | medium / patch | Existing guards never reach a timeout/grandchild. Add bounded private runner test demonstrating descendant termination and failure evidence; do not add public controls. |
| Blind7: persistence failure escapes catch | medium / patch | Catch calls persist without protecting a second write failure. Guard failure recording and exercise own synthetic unwritable manifest. |
| Edge1: completed response background failure | medium / patch | Same second-body root cause as Blind1; completed response must not send again. |
| Edge2: incomplete fixed-length termination failure | medium / patch | Same unguarded send root cause; nested protocol failure must not expose original exception. |
| Edge3: redirect loses Location | low / patch | Same allowlist omission as Blind2. |
| Edge4: owner a_ produces invalid project name | low / patch | Recipe regex admits trailing underscore; replacement produces trailing hyphen rejected by uv. Normalize package metadata safely and test valid boundary owner. |
| Verification1: uv-version test never reaches guard | medium / patch | Filed mutation evidence shows removing comparison leaves tests green. Group with Blind5. |


Root matrix audit additionally replaced malformed application rejection with a fully valid application recipe before asserting service-renderer refusal. Focused fixes pass runtime4/4, renderer3/3 and guards/runner4/4. Review RED runtime/renderer output and focused GREEN logs retained under platform/deployment/.local/scaffold-generation/.

## Verification

Pinned npm workspace test/type-check/schema:check, then test:generation with explicit
tools/cache. Root independently verifies and records matrix coverage and preservation.
Scaffold impacted; no UI. Generated guidance adds actual commands and authority limits;
root context unchanged. Docs update; ADR0059/0031/0023 suffice, accepted ADRs immutable.

Final root checks:15 builder tests pass; type-check/schema:check and fresh test:generation pass. Proof-dkwKDY runs4 generated tests in each of2 independent frozen offline installs, with13 source/7 output bindings unchanged. Root verification binds23 code/template/test/manifest/lock files unchanged. All12 review findings addressed; no deferrals. Preservation audit2487 protected files passes; actual commands/results/hashes retained in platform/deployment/.local/scaffold-generation/root-final-verification.json.

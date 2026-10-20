---
title: 'Disposable application shell bootstrap'
type: 'feature'
created: '2026-10-20'
status: 'done'
route: 'dispatch'
baseline_commit: '6a094d0aadae0010a308be3950c39d1fe9f8fbbe'
review_loop_iteration: 1
context:
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
---

<frozen-after-approval reason="standing implementation approval and next application-shell proof">

## Intent

The builder's service shell runs, but application output is absent. Prove a minimal
presentational React/Vite shell with its owning HTTP health shell from disposable
output. Use the existing builder and delivery tooling; no real application activation.

## Boundaries & Constraints

Always preserve prior outputs/concurrent work and approved exact dependencies,
including TS7.0.2. Keep recipe validation and candidates unpromoted with
bootstrap_only:true/generation_ready:false. Reuse service templates, characterize
before refactoring. Root npm workspace/lock remains authority; no nested browser lock.
Only presentational banner/main/Welcome and keyboard skip link, responsive CSS and
Home navigation. No fake users/orgs/grants, Auth/Directory UI, editor, forms, domain
routes or product readiness/status widgets. Browser business data remains API-owned.
Never implement Identity/Access/WRITE, DB/providers, normal generation, extension
import/regeneration/journal, Leave, deployment, Docker or real-data use in this proof.

## I/O & Edge-Case Matrix

| Scenario | Expected behavior |
| --- | --- |
| Valid application input | Deterministic web/ and api/ file map; no renderer writes |
| Invalid/service/extension input | Safe refusal; no output/pattern promotion |
| Service renderer after reuse | Existing output/refusals unchanged |
| Missing/wrong tools/browser/cache | Safe failure, no runtime/browser downloads or host fallback |
| Fresh application proof | Private new ENV proof, preserve all existing output |
| Workspace install | Copied canonical root lock extended by npm only, one clean offline ci, no checkout lock change |
| Built browser/API | Semantic shell renders on desktop/mobile, keyboard skip/Home/reload work, real owner health responds; no fake admission |

</frozen-after-approval>

## Code Map

- `src/service-renderer.ts`, `templates/service/`, `scripts/process-runner.mjs` under
  builder: reuse HTTP templates and bounded child handling; service entry retains behavior.
- `src/recipe.ts`: existing app fixed-account pattern; not runtime authority.
- `templates/web/`: historical broad Auth/Directory assumptions; leave unchanged.
- `platform/env-web-qualification/package.json`: exact baseline metadata, not runtime
  generator input. `scripts/browser-smoke.mjs` there illustrates Vite preview/explicit
  Chromium teardown; do not copy its counter/demo or import its server/runtime.
- `platform/deployment/qualification/web/prove.py`: root workspace/config/install pattern.
  Existing source/caches/receipts stay intact; no historical qualifier chain prerequisite.
- Tool payloads in deployment/.local/kdg-toolchains/: node/npm from
  ad277eef-a10e-4aac-bb82-5743653fb2e0, uv/Python from0cc4bc48-505e-41c1-8876-25b2d49b5694.
  Npm cache deployment/.local/web-baseline-qualification/network-cache; Chromium executable
  browsers/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell
  there. Python cache deployment/.local/python-baseline-qualification/cache.

## Tasks & Acceptance

- [x] Builder tests: acceptance RED first, characterize service output before reuse;
  valid app/service rejection, extensions, owner token and output ownership cases.
- [x] Internal application renderer plus `templates/application/`: web shell owner seed,
  entry/styles/config/tests/guidance with explicit generated/seed ownership; api/ uses
  existing HTTP templates. Literal known tokens only. No public generation/candidate flag.
- [x] Web pins: React/DOM19.3.0, Vite8.3.4/plugin-react6.1.2, TypeScript7.0.2,
  React/DOM types19.3.0, Node types26.6.5, Playwright1.64.0 dev-only. Add only needed
  packages; no speculative Tailwind/shadcn/Auth imports. Explicit type-check/build/browser
  scripts; no hidden repo node_modules, floating versions or nested lock.
- [x] Add `test:generation:application` as a focused internal test entry in existing
  builder, reusing private process runner. Existing service test:generation stays intact.
  Require explicit selected npm/Python/uv/cache/Chromium paths; check versions and executable
  identity. Create private fresh output under deployment/.local/scaffold-application.
  Copy root manifest/lock and existing workspace manifests, preserving file-dependency
  paths. Add generated app workspace only to proof root; npm offline package-lock-only
  resolution (ignore scripts/allow-remote=all as needed), then offline ci --ignore-scripts
  from that root. Record base/extended lock and source hashes. No checkout install/edit.
- [x] App API resolves own uv lock and one fresh frozen offline wheel-only environment
  using existing pins/clean flags. Run its generated tests. Browser uses built output,
  explicit existing Chromium, real loopback preview/API health and bounded teardown.
  Assert no page/console failures, correct landmarks/skip focus/Home/reload and no external
  business/Auth requests. Retain desktop/mobile screenshots and safe logs. No socket skip.
- [x] Proof manifest records commands/results, source/output classifications/hashes,
  root lock provenance, actual browser path/hash and safe partial failures. All runs
  unique; never repair/delete old output. Bound processes and preserve sensitive logging.
- [x] Builder README/root output guidance document commands, limitations and five impacts.
  Root owns mutable contract, KDG handoff, requirement-to-test evidence and final commit.

**Acceptance Criteria:**
- Given validated app choices, when the internal proof runs with pinned tools, then
  output installs/types/builds and renders in real Chromium with a real owner HTTP shell.
- Given unsupported choices or unavailable prerequisites, when attempted, then failure
  is safe and prior output/checkout sources/locks remain unchanged.

## Implementation Notes

No intent gaps or irreversible actions; new renderer/proof merits dispatch. Standing
approval covers synthetic subprocess/socket/browser verification. Do not rerender BMAD
or commit. Agent owns builder files only; root owns other docs/audit/final review.
Avoid repeated large installs: focused tests first, root owns final full proof after review.

Implementation:21 builder tests, TS7/schema and service regression proof-bCsLRv pass. First actual app proof-jip1bf preserved TS2882 after successful35-package selective install; owning template fixed with Vite client types, strict kept. Root corrected app proof-B5FmrE passes all13 stages in13.485s, including real browser/API. Additional private dependency provenance tests3/3 pass. Matrix audited against executed renderer/guard/dependency tests and actual output; final review follows.

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
| --- | --- | --- |
| Blind1: detached API escapes outer timeout | medium / patch | Browser source sets detached:true; shared runner kills only its own group. API must inherit the group and use child-owned normal shutdown. |
| Blind2: forced shutdown is not awaited | medium / patch | Existing finally sends SIGKILL without awaiting exit; add bounded confirmation and truthful cleanup evidence. |
| Blind3: generated guidance hardcodes fixture workspace | low / patch | Renderer accepts another owner but README commands use bootstrap path; use commands relative to generated web directory. |
| Blind4: hash capture follows import/render | low / reject | Current proof assumes the explicitly frozen builder source for the run, followed by hash recheck. Concurrent hostile source replacement is not supported; immutable loading/receipt machinery would overcomplicate this isolated developer fixture. Document stable-source assumption. |
| Blind5: copied installation manifests unbound | medium / patch | Source hashes do not verify copied root/workspace manifest bytes after npm stages. Record final copied manifest hashes and compare before success. |
| Blind6: unsuccessful HTTP responses unobserved | low / patch | Requestfailed excludes HTTP errors; add >=400 response assertion. |
| Blind7: no separate failure fixture for every later stage | low / reject | All stages share the same checked run/catch, actual proof-jip1bf establishes retained post-install failure and source audit. Repeating identical error-path fixtures for install/API/browser adds test machinery without a distinct uncovered state; lifecycle failure is covered separately. |
| Blind8: live descendant timeout evidence absent | medium / patch | New API group differs from prior tested runner. Verify actual browser/API timeout pattern locally and focused forced-stop behavior, retaining ownership/exit evidence. |
| Blind9: passed browser receipt precedes cleanup | medium / patch | Result is written before finally; move final passed publication after successful cleanup and record cleanup outcome separately. |
| Edge1: detached API timeout orphan | medium / patch | Same demonstrated group mismatch as Blind1. |
| Verification1: same-origin Auth/business fetch permitted | medium / patch | Filed mutation evidence shows successful fetch('/auth/session') passes current origin filter. Reject fetch/XHR regardless of origin for this presentational shell. |


## Verification

Pinned builder test/type-check/schema:check; service proof after shared-template reuse;
application proof as above. Record exact RED/GREEN commands/results and matrix coverage.
Scaffold impacted; shell stays candidate, no shared UI promotion yet. Generated guidance
adds actual commands; root context unchanged. Docs update; existing ADR0059/0031/0023/
ownership decisions suffice, accepted ADRs immutable. Current Access and full P1 remain.


Final outcome:28 builder tests, type-check and schema:check pass. Fresh reviewed
proof-Whsv74 passes all13 stages, four generated API tests and real desktop/mobile
Chromium checks; root-final-verification.json records exact commands/results and41
unchanged source bindings. Service proof-bCsLRv retains13 matching source bindings.
All nine patch routes above are addressed; the two low rejections remain explained,
with nothing deferred. Actual timeout-ownership/result.json confirms API/Chromium
termination and closed API port. Evidence matrix includes lifecycle/request guards
and copied-manifest drift. Preservation audit confirms2500 protected prior files
unchanged. Next: safe generation/custom-code preservation; generation_ready:false.

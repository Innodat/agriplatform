---
title: 'ENV: qualify the approved frontend dependency graph'
type: feature
created: '2026-10-15'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: c37fac15698e572271cbf3a6a1817c150bc06ad7
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md'
  - '{project-root}/platform/docs/architecture/contracts/scaffold-environment-and-generation.md'
---

<frozen-after-approval reason="Standing approval for bounded ENV prerequisites and isolated synthetic verification">

## Intent

**Problem:** Selected Node/npm/TypeScript tools execute, but the approved frontend
package graph has not been clean-installed, type checked, tested or built. Existing
workspace consumers must remain protected when the canonical root lock gains it.

**Approach:** Add `platform/env-web-qualification` as an ENV-only fixture under existing
root `platform/*` workspaces. Use exact approved React19.3.0/Vite8.3.4/TypeScript7.0.2
and their approved runtime/build/test/CLI packages. Generate the root package-lock with
qualified Node26.11.1/npm12.2.0; no nested lock. Prove clean disposable root installs,
native type/build tools, synthetic component/validation/routing/auth-client boundaries
and affected consumer regression. This is package compatibility, not app generation.

## Boundaries & Constraints

**Always:** Preserve all existing tree changes and repository node_modules. Characterize
old-lock shared/Scribeswell checks in a disposable root before changing the lock. Inspect
all existing-resolution changes and minimize unrelated churn. Keep every actual root
workspace manifest and required file dependency/source path in copies. Isolate npm user/
global configs, cache and environment; explicit qualified Node/npm, integrity-locked ci,
no implicit latest/npx or lifecycle downloads. Prove compiler accepts valid and rejects
invalid types, React/DOM component interaction, Zod rejection, router rendering, local
Supabase Auth-client setup without external requests, Tailwind/native Vite build. Test
build-only CLIs at their actual declared pins; no unsupported claim of browser/device/
shadcn source-generation proof. Record source/lock provenance and five impacts.

**Never:** Add another generator, nested frontend lock, generic offline service, shared
runtime owner, KDG/Leave domain/editor or saving pattern. No app/service implementation,
database/account/grant/schema mutation, Docker upgrade/startup, infrastructure, deployment,
provider registration or real-data pilot. Do not treat root build/dev as verification,
force unsupported peers, downgrade TypeScript, add speculative TS6 compatibility or
optional React Compiler/Babel peers. Runtime readiness remains false.

## I/O & Edge-Case Matrix

| Scenario | State | Required result |
| --- | --- | --- |
| Clean graph | Qualified tools, canonical root lock, absent disposable destination | Exact fixture versions execute, integrity install/type/tests/build pass; repository install untouched |
| Invalid types/input | Deliberate TS mismatch, invalid synthetic form value | Actual TS7/type diagnostic and typed validation rejection |
| Workspace consumers | Old versus new canonical lock, same copied source/tool target | Record characterization, affected checks and explain every change/failure; no hiding regression |
| Unsafe or stale proof | Existing output, nested lock, manifest/lock drift, wrong tool/host | Refuse or fail before claiming clean compatibility; no repair/global side effects |
| Browser/runtime gates | Library/DOM/build proof only or isolated browser fixtures | Record exact executed scope; no real Auth/KDG/device/deployment readiness claim |

</frozen-after-approval>

## Code Map

- `package.json` already admits platform/*; root package-lock is canonical. Four current
  workspaces: shared, ui-business, app-directory-client, Scribeswell web. tools has no
  manifest. Add fixture without changing existing owner manifests unless a proven
  introduced incompatibility requires a separately explained compatible correction.
- `platform/env-web-qualification/`: new package/config/source/tests/runbook. No runtime
  owner imports this fixture. Existing CLI tool bins are ignored run0cc4bc48 payloads.
- Scribeswell `build` consumes actual shared launcher/client source; browser fixtures
  cover reader/lexicon/launcher. Shared has type-check; UI/client support direct local tsc.
  PtS is outside root npm workspaces and retains its own lock. Do not implement it.
- `platform/deployment/`: ENV evidence/runbook and disposable proof tooling if needed;
  preserve prepared/toolchain source bindings. KDG next-session/testing/memlog navigation.

## Tasks & Acceptance

- [x] Characterize existing lock/source checks in disposable root; record exact results.
- [x] Add fixture acceptance tests and observe relevant failure before its implementation.
- [x] Add exact manifest/config, generate canonical root lock with selected npm, inspect
  existing-resolution changes; never install in the working checkout.
- [x] Clean ci, type check/negative compiler, tests/build/tool checks; affected owner checks
  and second clean/offline proof as supported. Fix introduced failures before completion.
- [x] Record traceability, hashes/provenance, five impacts and remaining gates; preserve
  unrelated docs, complete independent review and local conventional commit only.

**Acceptance Criteria:**
- Given approved exact pins and an absent disposable root, when ci and fixture commands
  execute, then actual selected versions/type/behavior/build checks pass with no hidden
  dependency on repository node_modules and no nested canonical lock.
- Given the same existing consumer source and old/new lock, when affected checks run,
  then no unexplained regression is accepted and evidence names any preexisting gap.
- Given type/input or stale-proof failures, when qualification runs, then it fails safely
  and never reports runtime readiness or alters unrelated source/install state.

## Implementation Notes

User approval persists; dirty Leave/PtS documents are explicitly authorized for preservation.
No intent gaps or irreversible action. Full route is used because root-lock peer/hoisting
effects require affected-consumer evidence. The implementation agent owns the fixture,
disposable characterization/install execution and canonical lock update within this
scope; the root agent owns final verification and review. Do not commit before review.
Use qualified tools under platform/deployment/.local/kdg-toolchains/
0cc4bc48-505e-41c1-8876-25b2d49b5694/payload: node/bin/node, npm/bin/npm-cli.js.
The npm bundled with Node is not the selected npm. Read the latest KDG next-session
and deployment qualification evidence for current gates. Preserve unrelated dirty paths.

Actual qualification exposed and addressed npm12 bundle extraction and two historical
hashless React18 type records through scoped npm commands, never handwritten locks.
Exact pins remain unchanged. Supabase auth-js2.117.3 has one reproduced WebAuthn/TS7
DOM TS2430: strict own-source checks exclude declaration internals, and a second strict
declaration check asserts that sole upstream failure explicitly. Full declaration
coherence/WebAuthn remain unqualified. Vitest5 resolves peer Vite7.3.6 in the retained
workspace graph; the build separately executes exact Vite8.3.4. No plugin casts or
compiler downgrade. UI-business's standalone rootDir/CSS diagnostics predate this change.
See [owner evidence](../../platform/deployment/ENV_WEB_BASELINE_EVIDENCE.md).

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Verified evidence and disposition |
| --- | --- | --- |
| Blind1 resolve ignores offline | medium / patch | Both resolve commands omit the accepted offline flag; propagate it so that invocation cannot fetch unexpectedly. |
| Blind2 qualification omits lock-source validation | medium / patch | validate_lock is called only after resolution, so a later changed lock reaches ci; apply the existing validator before qualification install. |
| Blind3 preflight inherits environment | medium / patch | check_output runs before clean env construction and can execute NODE_OPTIONS preload; use isolated version probes. |
| Blind4 preflight has no deadline | medium / patch | Neither check_output has timeout; bound probes before workspace creation. Group with preflight isolation. |
| Blind5 overlapping cache/output | medium / patch | Cache below copied root is currently admitted and npm writes there; reject overlap before creating output. |
| Blind6 consumer results need automated comparison | false / reject | The runner explicitly records owner checks for manual old/new assessment; runbook says process exit0 is not acceptance. No CI consumer or automated owner-acceptance claim is added. Root actually compared source hashes and normalized diagnostics and ran both98-test suites; no unexplained regression is accepted. A new comparison protocol is not required to correct this observed delivery. |
| Blind7 qualified tools not rebound to owner receipt | medium / patch | Entry hashes/version strings alone do not detect changed supporting payload files; use the existing owner's repeat verification against the retained receipt, without installing missing tools. |
| Blind8 runner/browser provenance omitted | medium / patch | Workspace hashes exclude runner and actual browser bytes; record those identities in proof evidence. |
| Blind9 signOut result ignored | low / patch | Test checks no requests but discards returned error contract; assert local success explicitly. |
| Blind10 built fixture lacks browser execution | medium / patch | Current browser suite exercises the existing Vite7 app; add an internal bounded smoke of the exact Vite8 build entry/CSS/routing with the existing pinned browser, no runtime API or public command. |
| Edge1 NODE_OPTIONS preload and preflight hang | medium / patch | Same verified preflight defects as Blind3/4; preserve this distinct finding and fix together. |
| Edge2 interruption leaks isolated command group | medium / patch | execute handles timeout but not KeyboardInterrupt after start_new_session; interrupted parent leaves descendants. Bound cleanup and verify real interruption. |
| Gap1 fixture failure enforcement unprotected | medium / patch | Reviewer mutation changing fixture expected exits to None passed all20 tests; add per-command failure/log assertions. |

All12 patch finding instances resolved, one false finding rejected, none deferred.
Final source proof and32 focused tests pass. A process-reaping lookup race in a test
was corrected without changing its no-live-descendant requirement. Existing owner
tool receipt was actually reverified; actual Chromium headless path is recorded and
used by the built-output smoke. No loopback/runtime/declaration limit was relaxed.

## Verification

Use exact affected package commands in copied roots, not repository root wrappers.
Record initial red, final green and old/new owner outcomes, clean install provenance,
actual native/compiler/tool versions, hashes, whitespace/links and review disposition.

Executed final source proof: `python3 platform/deployment/qualification/web/prove.py
--destination <repository>/platform/deployment/.local/web-baseline-qualification/new-5
--cache <repository>/platform/deployment/.local/web-baseline-qualification/network-cache
--mode qualify --offline --browser-path <repository>/platform/deployment/.local/web-baseline-qualification/browsers`.
490 packages/18s;3 component tests,98 browser tests/1.5m, type/TS2322/native build/CLI
and built Vite8 Chromium smoke checks pass. Old-lock browser98/98,
shared/client/Scribeswell build pass; normalized
UI-business preexisting diagnostics identical; owner source hashes identical.
`python3 -m unittest discover -s platform/deployment/qualification/web -p 'test_*.py' -v`:
32 passed in2.088s. Real offline manifest drift refused before install, lock unchanged.
All five matrix rows are covered by those executed positive/negative/consumer and
guard tests. No skipped test is counted as proof. Declaration/browser/runtime limits
are explicit in the owner evidence; independent review complete, none deferred.
Local conventional commit records this bounded increment only; no push.

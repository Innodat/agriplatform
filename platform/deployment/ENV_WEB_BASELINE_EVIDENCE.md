# ENV frontend dependency qualification — 2026-10-15

This ENV-only compatibility fixture follows the
[approved dependency baseline](../docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md)
and [environment contract](../docs/architecture/contracts/scaffold-environment-and-generation.md).
The [Build record](../../_bmad-output/implementation-artifacts/spec-env-web-baseline-qualification.md)
tracks delivery and review. Compatibility checks and independent review are complete
within the stated limitations. Runtime readiness is false.

## Existing-lock characterization

Before changing the canonical root lock, selected Node26.11.1/npm12.2.0 copied all four
existing workspaces into ignored deployment evidence directory
`.local/web-baseline-qualification/old-network-1/root`. The new fixture was omitted.
No source node_modules, environment files, outputs or historical nested locks were copied.
Original owner manifests, locks and installed dependencies remained untouched.

`python3 platform/deployment/qualification/web/prove.py --destination
<repository>/platform/deployment/.local/web-baseline-qualification/old-network-1 --cache
<repository>/platform/deployment/.local/web-baseline-qualification/network-cache --mode
characterize` executed actual integrity-locked `npm ci --ignore-scripts`:155 packages,
exit0. The initial sandbox attempt failed DNS (`EAI_AGAIN`); the permitted network retry
succeeded. Exact commands/source/tool hashes and outputs remain in that proof directory.

| Existing consumer check | Old lock |
| --- | --- |
| shared `type-check` | PASS |
| Directory client local `tsc --noEmit -p` | PASS |
| UI-business local `tsc --noEmit -p` | FAIL: TS6059 sibling source outside rootDir; TS2882 CSS declaration absent |
| Scribeswell `build` | PASS: native TS7/Vite7.3.6,1591 modules; existing chunk-size warning |
| Scribeswell browser | NOT RUN: no explicit browser-cache selection |

The standalone UI-business failure predates this increment. It is not relabeled as a
passing check; new-lock comparison must preserve its diagnostic meaning. Root npm
build/dev wrappers were not used. PtS has an independent owner lock outside the root
workspace; this fixture does not qualify or change that graph.

## Resolution findings

The first disposable `--mode resolve` attempt failed safely with `EALLOWREMOTE` before
changing the checkout lock. npm12's lock-only complete-tree traversal extracts bundled
dependencies via a resolved tarball URL; selected npm's Arborist `build-ideal-tree.js`
and Pacote `fetcher.js` show the failing path. The actual refusal named the published
Tailwind4.3.3 oxide-wasm32-wasi tarball on registry.npmjs.org. npm documents the
[remote dependency policy](https://docs.npmjs.com/cli/v12/using-npm/config/#allow-remote).
Resolution requires an explicit command-scoped exception; normal installs retain the
default policy and lifecycle scripts remain disabled. Generated lock validation must
reject foreign registry URLs or missing integrity rather than trusting resolution alone.

The next attempt generated a graph but strict validation refused two preexisting
hashless records: shared's React18 and prop-types development declarations. Selected
npm's scoped `update @types/react @types/prop-types --workspace platform/shared
--package-lock-only --ignore-scripts --allow-remote=all` refreshed their metadata without
changing the shared manifest. React18 resolves18.3.31; prop-types deduplicates. The
third resolution passed validation for768 records. No generated lock was hand edited.

Canonical generated lock SHA256:
`151ca6b0926efb7478c1a153d5156e031ebf77ccb1b0b4fc6a2e81640e28a6e5`.
The old lock SHA256 was
`f8058687cd76b2b13c2151b8b321dd12820e058845ffa4c7f109dc48c1dd5507`.
The disposable `resolve-3` command/validation evidence retains both generator commands.

All57 changed/removed old paths were inspected;515 net new records are fixture/tool
dependencies. Existing source hashes are identical in the old/new proof copies.
Resolution changes follow these concrete constraints:

| Existing resolution | New resolution / reason |
| --- | --- |
| React/DOM19.2.7, scheduler0.27.0 | Exact fixture19.3.0 and scheduler0.28.0, within existing React19 owner ranges |
| React types19.2.17/DOM19.2.3, Node types26.0.1 | Exact fixture19.3.0/19.3.0/26.6.5; undici-types8.9.0 follows Node types |
| Supabase JS family2.108.2 | Exact fixture2.117.3 across auth/functions/postgrest/realtime/storage/client; phoenix0.4.5 and jose6.2.12 satisfy its dependency graph |
| Supabase CLI2.108.0 and eight platform packages | Exact fixture2.120.0; install lifecycle stays disabled |
| Tailwind Vite/node/oxide4.3.1 and12 OS variants | Exact fixture4.3.3; old nested Tailwind4.3.1 entries removed in favor of existing root4.3.3 |
| Playwright/test/core1.63.0 | Exact fixture1.64.0, compatible with existing Scribeswell declaration; binary/browser proof remains separate |
| tsx4.23.13 | Exact fixture4.23.15, compatible with root range |
| Vite7.3.6/plugin-react4.7.0, Zod3.25.76, Lucide0.400.0 | Retained for existing owners; new exact major versions coexist in the fixture graph |
| source-map-codec1.5.5, enhanced-resolve5.21.6, nanoid3.3.15, picomatch4.0.4, postcss8.5.16, source-map-js1.2.1 | Compatible shared transitives selected by added Vite/Tailwind/test tooling:1.6.0,5.26.0,3.3.20,4.0.7,8.5.30,1.2.2; three trace-mapping0.3.31 nested duplicates removed |
| shared React types18.3.26 and nested prop-types15.7.15 | Scoped publisher metadata refresh described above; React18.3.31, prop-types deduplicated |
| csstype3.2.3 | Version/integrity unchanged; development/optional classification changed through new consumers |

The first new-lock clean install (`new-1`) installed490 packages with scripts disabled.
shared/client/Scribeswell build passed; UI-business retained the same existing errors.
The fixture's strict type check exposed real Supabase/TS7 WebAuthn declaration and
mixed Vite configuration type issues plus a missing fixture CSS declaration. These
failures remain recorded while their causes are addressed; they are not green evidence.

## Acceptance and focused verification

The initial preimplementation file-presence check failed because the implementation
was absent. After dependency installation, the actual component suite was also run
with the implementation temporarily absent from its disposable copy: exit1, unresolved
`../src/Fixture`; `new-1/actual-component-red.log` retains that control. Restoring the
implementation and addressing the actual compiler failures produced three passing
component tests. Focused guard tests likewise failed before their implementations.
No expected application result was changed to dismiss a failure.

Vite build configuration now uses the fixture's actual Vite8.3.4 identity. Vitest5.0.4
resolves its retained peer Vite7.3.6 in this workspace graph and has separate configuration;
this does not claim a Vitest-on-Vite8 run. A CSS-only ambient declaration covers the
actual stylesheet import. There are no blanket module declarations or plugin casts.

Supabase auth-js2.117.3's `PublicKeyCredentialFuture.toJSON()` declaration conflicts
with TS7 DOM JSON types (`largeBlob.blob` ArrayBuffer versus string). The fixture does
not qualify WebAuthn or full upstream declaration coherence. Own-source checking keeps
`strict: true`; `skipLibCheck: true` excludes declaration internals only. Each type-check
also reruns with declaration checking enabled and asserts the sole exact upstream
TS2430, retaining the raw diagnostic. Any additional compiler error fails the command.
An independent deliberate source mismatch still must produce TS2322. No package pin,
compiler version or source type expectation was downgraded.

| Requirement | Executed proof |
| --- | --- |
| Exact runtime and24 direct package pins; actual local CLIs | scripts/tools.mjs checks each installed package and executes TS7/Vite/Vitest/tsx/npm/shadcn/Playwright versions; matching previously qualified Supabase binary runs explicitly |
| Valid source and invalid assignment | `type-check`: strict own source; known declaration conflict remains visible; negative TS2322 assertion |
| Actual React DOM, interaction and routing | baseline.test.tsx interaction/navigation test |
| Typed invalid/valid input | baseline.test.tsx Zod rejection/valid parse test |
| Auth-client setup without remote requests | baseline.test.tsx injected rejecting-fetch test, getSession/local signOut; zero requests |
| Native Vite/React/Tailwind | actual Vite8 build plus emitted p-4 CSS assertion |
| Protected copies/hosts/tools/locks |32 standard-library guard tests, including registry/hash/workspace/bundle validation and explicit browser fixture isolation |
| Bounded timeout cleanup | real parent/child/grandchild test, inherited stdout and ignored TERM, exit124 and no live descendants |
| Actual manifest/lock drift | separate `manifest-drift-1` copy changes React to19.3.999; offline npm ci exits1 before node_modules exists; lock SHA256 unchanged |
| Existing consumer compatibility | identical old/new owner-source hashes; shared/client/Scribeswell build pass; UI-business's known standalone diagnostics retained |

Focused commands in `new-1` pass all four fixture scripts, including3 component tests
and all CLI versions. Fresh `new-2` installed490 packages offline in14s; all fixture
scripts and the named owner type/build checks pass subject to the existing UI gap.
It initially selected a browser cache without required Chromium1248; no browser test
passed on that attempt. The pinned installed Playwright CLI then downloaded only its
Chromium headless1248 and FFmpeg1013 into ignored local evidence storage. No global
browser or OS packages were installed; Playwright's implicit `npx` suggestion was not used.

Actual old/new browser attempts each passed86/98 tests and failed12 because the proof
copy lacked the public tracked lexicon JSON and a parent for the synthetic privacy test.
This exposed a proof-harness defect, not an application regression. The runner now copies
exactly that public input, records its hash and creates an empty PtS/reference directory;
it never copies the private PtS library. The unchanged old-lock suite now passes all98
desktop/mobile viewport fixtures in1.5m. The pre-review fresh `new-3` proof installs490
packages offline in11s and passes all98 unchanged browser tests in1.4m, all3 component
tests, actual Vite8 native build (2066 modules), type/negative checks and CLI versions.
Shared/client/Scribeswell build pass; normalized UI-business diagnostics are byte-identical
to the old-lock failure. All prior owner source hashes and the public fixture bytes match.

Final command from repository root:

```bash
python3 platform/deployment/qualification/web/prove.py \
  --destination "$PWD/platform/deployment/.local/web-baseline-qualification/new-5" \
  --cache "$PWD/platform/deployment/.local/web-baseline-qualification/network-cache" \
  --mode qualify --offline \
  --browser-path "$PWD/platform/deployment/.local/web-baseline-qualification/browsers"
```

For repetition choose another absent destination; never reuse/delete a proof root.
Browser installation used the selected Node and locked Playwright1.64 CLI at the proof's
`node_modules/playwright/cli.js install chromium --only-shell`, explicit local browser
cache and clean environment. This is Chromium desktop/mobile-viewport fixture evidence,
not installed Android/iPhone, Firefox/WebKit, Entra or real application-service proof.

Checkout node_modules directory/hidden-lock inode and mtime match the prework snapshot.
Its hidden lock SHA256 remains
`c2d31923134bab2436a03b4837ae342770724a988a1967599efebc0875337917`.
Fixture manifest SHA256:
`3935dc154083d14bac5eeb11c22de352093cb665e2785ec0adefa2e4f4b5ffff`.
Each proof's provenance contains every copied source and selected Node/npm binary hash.

## Independent review and final proof

Three independent review lenses produced13 finding instances:12 fixed, one rejected
with evidence, none deferred. The rejected request for an automated owner-comparison
protocol did not identify an accepted regression: the documented runner requires manual
old/new assessment, which was actually completed here. No CI acceptance wrapper exists.
Every finding and its verdict remains in the Build record.

Fixes bind the proof to the existing tool owner's immutable receipt, isolate and bound
all version probes, validate the canonical lock again before qualification installation,
honor offline resolution, refuse cache/output overlap, retain every required fixture
failure, clean up interrupted process groups and record runner/browser identities.
The actual signOut success is asserted. An internal Chromium smoke now serves built
Vite8 output and proves entry/render/increment/navigation/reload/computed Tailwind16px
padding, using the exact recorded headless executable. No public command or dependency
was added. An initial full-browser-path assumption was corrected to use the actual
headless process executable; the cache intentionally contains only the headless binary.

Final reviewed `new-5`: existing six-tool receipt verification passed;490 packages
installed offline in18s; shared/client/Scribeswell builds pass;98 Scribeswell browser
tests pass in1.5m;3 component tests, all type/negative/native build/CLI checks and built
Vite8 browser smoke pass. Existing owner source hashes match and normalized UI-business
diagnostics remain identical. The interrupted `new-4` directory is incomplete evidence
and was never reused or counted as passing.

The final32 runner tests pass in2.088s. One verification run exposed a test race while
reading /proc after a process was reaped: ProcessLookupError means the process already
exited. The test now treats disappearance during lookup as exited while retaining its
assertions that no live descendant remains. No cleanup failure was dismissed.

Final runner SHA256:
`5a48df47baa3a8a604a58aa742be186a30c986809b732dbf911f4a81ed6ca1ff`.
Final guard-test SHA256:
`b6264c4fc472616fb8cceda927ef5d531c68c6ff489bc8f0848a36b8f7542f23`.
Retained tool receipt SHA256:
`4efad618046ecda6459da9680b23e9cd47375181a059b33f6838ad8acde6ecc2`.
Actual Chromium headless1248 executable SHA256:
`4fa61f0ba0b4f89b7bec242c32ca16d3bccf69dbfef0651924a9ba8fede5f9d6`.
The proof also records installed Playwright metadata/package hashes and owner command
results. Canonical/hidden install lock hashes above remain unchanged after final checks.

## Five impacts and remaining gates

- Scaffold: compatibility fixture only; existing generator/schema/template/client and
  runtime owners retain their work. No candidate pattern is promoted.
- Shared UI: no shared component or application behavior changes.
- Agent context: existing root rules suffice; actual fixture commands/bounds are in
  the [runbook](qualification/web/README.md).
- Documentation: this evidence, fixture/proof runbooks and KDG delivery navigation.
- ADR: existing ownership/scaffold/ATDD/release decisions apply; accepted ADRs unchanged.

Actual Docker>=28, isolated runtime adapter/startup, publisher image/DB target,
Identity/Access/WRITE, migration/adoption roles, generated consumers, provider/mobile
devices and pre-pilot policies remain open. No production migration, account/access,
infrastructure, deployment, Leave/KDG domain/editor or real-data action occurs here.

# Disposable frontend proof

`prove.py` copies all actual root workspace manifests and their source, preserving
relative `file:` dependencies. The new ENV fixture is excluded only for old-lock
`characterize`. Existing historical nested locks stay untouched in source and are
excluded from proof copies; the new fixture refuses a nested lock. No repository
node_modules, build output, environment files or local evidence is copied.

The runner refuses existing destinations, destination/cache parent traversal and
symlink paths, symlinked source, uncopied local dependencies, wrong Node/npm versions,
unsupported hosts and nested fixture locks. Cache and proof roots cannot overlap.
Before selected tools execute, an existing preparation and immutable receipt for
run0cc4bc48-505e-41c1-8876-25b2d49b5694 are required. The existing `toolchain.py qualify`
owner command repeats receipt/payload verification in a clean environment; a missing
receipt refuses without installing. Node/npm version preflight uses separate private
empty npm configs, removed afterward, and bounded process execution before destination
creation. Provenance retains the owner CLI result and receipt hash. `npm ci --ignore-scripts` verifies the
canonical root lock against manifests and integrity-checks artifacts. Both npm config
files and cache are explicit; execution gets a fresh selected-field environment.
A local shim ensures nested `npm` invocations use selected npm12.2.0 rather than Node's
bundled npm. Lifecycle scripts and browser downloads are never enabled. Transitive
native packages must execute through their packaged optional binaries; a missing binary
fails the relevant check. Network retries are disabled and fetch timeout is30 seconds;
commands run in a new Linux process group with a600-second execution deadline.
Timeout cleanup signals the whole group with TERM then KILL, using bounded two-second
waits; it never waits indefinitely for descendants holding stdout open. Timeout logs
retain exit124 and explicitly identify unconfirmed cleanup if pipes or the leader fail
to close within the cleanup bounds. KeyboardInterrupt performs the same bounded
group cleanup before propagating the interruption. The focused child/grandchild test includes TERM-
ignoring descendants and proves prompt return and no remaining live descendants.

From the repository root, choose unique absent destinations under ignored durable
`platform/deployment/.local/web-baseline-qualification/` and an explicit cache there.
For example, with qualified tools already present:

```bash
python3 platform/deployment/qualification/web/prove.py \
  --destination "$PWD/platform/deployment/.local/web-baseline-qualification/old-1" \
  --cache "$PWD/platform/deployment/.local/web-baseline-qualification/cache" \
  --mode characterize
```

First complete old-lock characterization, before changing the canonical lock. Then run
`--mode resolve` with another absent destination. This runs selected Node26.11.1 and
npm12.2.0 `install --package-lock-only --ignore-scripts --save-exact --allow-remote=all` in that copied root.
It then executes the same selected npm with this bounded metadata refresh in the
copied root:

```text
update @types/react @types/prop-types --workspace platform/shared --package-lock-only --ignore-scripts --allow-remote=all
```

The old lock contained two preexisting records without integrity: shared's
`@types/react18.3.26` and `@types/prop-types15.7.15`. Plain lock resolution preserved
those records, so strict validation rejected them. The scoped update regenerates
publisher metadata using npm, preserving the owner manifest and its React18 range;
qualification resolved React types18.3.31 and deduplicated the old prop-types record.
No integrity values are hand-written and validation remains strict. Inspect this
bounded refresh in the existing-resolution diff along with the new fixture graph.

The explicit remote allowance applies only to resolution: npm12.2.0's bundled-dependency
inspection calls `pacote.extract(node.resolved)` and otherwise refuses even the selected
registry's oxide-wasm32-wasi4.3.3 archive with EALLOWREMOTE. Lifecycle scripts remain
disabled. Ordinary `ci` keeps npm's default remote policy. After resolution, structural
validation accepts only HTTPS registry.npmjs.org `.tgz` artifacts with SHA512 integrity,
known workspace links, and bundled entries under pinned npm12.2.0 or
oxide-wasm32-wasi4.3.3 owners whose registry archives carry integrity. Unknown local/git/
foreign sources, missing integrity and unrecognized bundles fail. The validated lock hash
is retained in `lock-validation.json`; this does not replace npmci's integrity check.

Inspect every existing-resolution change before deliberately copying its generated
`root/package-lock.json` into the checkout. The runner never updates the checkout lock.
No owner manifests are changed to hide failures or force peer dependencies.

Run `--mode qualify` with a third absent destination after the canonical lock update.
Repeat with a fourth absent destination and `--offline`, using the same populated cache.
`--offline` also applies to both resolution npm commands. Qualification revalidates the
current lock against the strict registry/integrity policy before `ci`, even if it was
changed after the original resolution proof.
No preexisting destination is repaired, reused or deleted. Keep each run's `commands.json`,
`provenance.json` and command logs. Provenance contains copied source/lock/tool hashes,
host identity, runner hash and `runtime_ready: false`. When explicit browser binaries
are available, provenance also records the actual Chromium executable hash and installed
Playwright package/browser metadata hashes. A bounded public headless
`chromium.launchServer()` probe records `BrowserServer.process().spawnfile`, so an
existing only-shell installation is identified without requiring full Chromium. The
recorded executable is passed internally to the production smoke; missing binaries
remain unqualified. Compare old/new owner source hashes and
commands; explain every changed resolution and diagnostic before accepting the result.

The runner invokes shared's `type-check`, direct local TypeScript checks for Directory
client and UI business, Scribeswell's own `build`, and optionally its browser suite.
Owner failures are recorded without aborting subsequent characterization: process exit0
alone is **not** acceptance. Review every owner result against the old-lock source/check
baseline; preexisting failures stay visible. Fixture/install failures abort qualification.
No root build/dev wrapper is used.

Browser proof copies additionally include exactly the tracked public
`apps/scribeswell/data/hebrew-lexicon/lexicon.json`, with its SHA256 in source provenance,
and an empty `apps/pts/reference` parent where the existing reader test creates its own
synthetic temporary fixture. The lexicon file and its parent chain reject symlinks before
output creation. No PtS library, corpus, private content or existing reference contents
are copied. These inputs are included only with explicit `--browser-path`.

For actual Scribeswell browser checks, supply the same existing explicit
`--browser-path /absolute/path/to/playwright-cache` to old/new runs. The runner never
looks up a workstation cache implicitly. Without this argument, it records browser
checks as not run and leaves browser compatibility unqualified. Version commands do
not qualify browser binaries or devices. With the explicit existing browser path,
qualification additionally invokes an internal smoke after the fixture's native build.
It serves the built Vite8 output via Vite's public `preview()` API on an ephemeral
loopback port, launches the explicitly recorded Chromium executable through pinned
Playwright, and checks the heading, increment, details navigation/reload and computed
Tailwind16px padding. Browser/preview teardown has deadlines; the outer command group
provides the execution bound. This synthetic browser proof is separate from jsdom and
Scribeswell tests; it does not qualify real Auth, devices, generated apps or deployment. No `npx`, implicit latest download, global
install or real application/service/Auth/data mutation is involved.

Guard tests need only the standard library and never install anything:

```bash
python3 -m unittest discover -s platform/deployment/qualification/web -p 'test_*.py' -v
```

See [fixture scope](../../../env-web-qualification/README.md). This proof is Linux
x86_64 only. Runtime startup, owner foundations, generated apps, Docker support,
provider registration, mobile devices and production release remain unqualified.

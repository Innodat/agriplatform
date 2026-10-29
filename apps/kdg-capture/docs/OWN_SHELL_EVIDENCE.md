# Revisioned own shell candidate — 2026-10-29

Story 3.1's shell slice builds the actual `web/index.html` → `src/main.ts` production
entry with retained Vite 8.3.4. The shell plugin hashes the final emitted public HTML,
JavaScript, CSS, manifest and icon into a 24-character revision and emits an exact
precache list. Public config is validated and injected before hashing. The worker
stores the own HTML under canonical `/`; the local host continues refusing direct
`/index.html`. Only exact own root navigation receives an offline fallback. API,
Auth/provider, administrator navigation, query-bearing requests and other routes stay
network-only. The worker never caches protected HTTP responses or writes IndexedDB.

`prepareOwnShell()` confirms the active worker's complete expected cache through a
bounded MessageChannel operation. Registration alone cannot acknowledge readiness.
The caller separately verifies the atomic committed provision. Registration/activation
waits are bounded; installation uses a total 20-second fetch abort. No storage durability
or install/device qualification is inferred from a successful browser cache write.

An installed update waits. Only explicit `applyShellUpdate(currentSafety)` requests
activation; the callback reads current unsaved input and executing work before and after
waiting-cache verification and again at controller change. Input begun during activation
defers the requesting tab's reload until another explicit safe action. Other tabs do
not reload. The worker serves retained content-hashed resources from old shell revisions
and never deletes old caches. Update does not read, migrate, clear or reset queue/schema
stores and does not require successful synchronization first.

The manifest and page theme inherit neutral primary `#171717` and background `#ffffff`
from the existing shadcn lineage. The SVG is an unbranded observation document symbol;
no brand palette or lettermark is introduced. A focused assertion observed RED against
the earlier green value, then GREEN after this DESIGN.md compliance correction.

## Verification

Use selected Node26.11.1 from repository root:

```
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node --test apps/kdg-capture/web/tests/own-shell.test.mjs
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/own-shell-proof.mjs
```

The first pre-implementation command failed with `ERR_MODULE_NOT_FOUND` for the absent
own shell plugin (acceptance RED). The current focused build-contract test passes.
The actual-built proof passes eight checks, including strict TS7 checking of the shell
module, against `scripts/serve-local-shell.mjs` and its generated bounded API middleware.
Its source-bound result and retained private artifacts are:

`platform/deployment/.local/kdg-own-shell-301eeef4-9121-4073-a5f2-9dfb572f2a66/result.json`

The checks prove complete-cache readiness; offline actual own-root reopening; API,
Auth/provider and administrator exclusion; waiting update state; live typing/work and
activation-race deferral; explicit reload; retained old revision caches and offline fetching of old content-hashed resources after activation,
version4 IndexedDB pending/conflict sentinel and another tab's in-memory input; and a
failed emitted-resource install refusing shell readiness. No dependencies were installed
or upgraded. Earlier failed build attempts exposed Vite hook ordering (index not yet
emitted), TS7's required explicit rootDir, and the removed TS7 transpileModule API; each
was corrected without altering application behavior or test expectations to hide it.

A separate tested `--build-only` mode accepts the explicit external
`KDG_LOCAL_WEB_CONFIG`, emits fresh capsule production output and reports its `dist` for
the actual-provider coordinator. The immutable built host verifies its public config
against the external input and uses the same generated route declarations/proxy. The
coordinator's final stable mounted-workspace build/source binding supersedes interim
actual-index bindings made while the workspace source is still under implementation.

These are synthetic loopback Chromium shell proofs, not real Auth/current SQL, actual
history-store migration, completed mounted own-work journey, installed Android/iPhone,
physical-device or assistive-technology evidence. The version4 sentinel shows this shell
does not alter IndexedDB; storage owner tests establish actual history schema semantics.
Story 3.1 remains incomplete until its coordinator closes the other authorized gates.

Scaffold impact: application-owned KDG root/admin/public-config/build behavior, no managed
neutral file edits. Generated proxy adoption/tests are recorded by their owner. Shared
UI: update and setup presentation belongs to the mounted own workspace. Agent context:
existing app/root rules suffice. Documentation: this evidence and web README. ADR impact:
existing offline setup, saving, retention and update contracts apply; no new decision.

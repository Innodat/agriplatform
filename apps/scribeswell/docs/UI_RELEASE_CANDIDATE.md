# Accepted UI frontend release candidate — 2026-11-04

The accepted Scribeswell UI is incorporated into isolated candidate
`7293caf739390857600bafd2d9e2213fecd270ef`, on local branch
`scribeswell/ui-release-20261104`. Its parent is the actually deployed shared-release
source `59e2c8884cad24bb2f6e99fc519b2e6dc5bc9d84`. Publication is pending approval.

## Source and build

The candidate applies the approved web-subtree delta from
`e16d441ff26cee838f81fe118f980c7971c1745f` through
`8747187cf45127ab3043abaeede54a00e542b861`: 23 frontend source/test/config paths.
The only patch-context conflict was Topbar; its four newer deployed launcher/auth
changes were retained while applying the accepted presentation and signup-event
handling. No backend, migration, shared package, owner contract, dependency manifest
or lockfile changed. The isolated candidate has no tracked working-tree changes.

Both actual release builds use the deployed `build-release.mjs`, selected
Node26.11.1/npm toolchain, existing installed local dependencies and previously
published browser configuration. No private server environment file or credential
is read by this follow-up's build driver. Candidate source hashes stayed exact
through both builds. No fresh dependency installation or clean-install proof is claimed.

| Variant | Release attempt | Configuration | Result |
| --- | --- | --- | --- |
| Primary | `2026110402-1` | Existing bounded pregranted Studies on | TypeScript/Vite and independent artifact verifier pass |
| Recovery | `2026110402-2` | Studies off | TypeScript/Vite and independent artifact verifier pass |

Both contain Scribeswell at `/` and current PtS at `/pts/`. All PtS artifact bytes
equal the corresponding retained deployed build. Existing bundle-size advisories
remain. The public build fingerprints match the existing configuration; changed
asset hashes and the new source SHA identify this UI revision.

## Candidate verification

`npm exec --workspace=apps/scribeswell/web -- playwright test --config /tmp/scribeswell-ui-candidate.config.cjs study-ui-polish.spec.cjs workspace-polish.spec.cjs --workers 2`
passed **31 checks, one intentional desktop skip**, against the compiled primary
artifact served over local HTTP. Chromium uses a dead external proxy; API/Auth
responses are synthetic fixtures. The first invocation was blocked before tests by
the sandbox's localhost socket restriction; the approved rerun passed in14.9seconds.

`node /tmp/scribeswell-ui-candidate-visual.cjs` passed seven additional rendered
scenarios and captured20 screenshots. Both variants were checked on desktop/mobile
for root reading, Hebrew font and closed-selector labels, deep-query reload and
PtS entry/assets/reload. Primary Notes/actions/delete/Retry were checked at1440,
390 and320px widths with no document overflow. Static bytes are fulfilled directly
from the compiled artifacts, and unhandled external requests are blocked. These
checks establish local rendering, not live Auth, backend permissions or hosting rules.
The candidate `_redirects` and entry layout also pass the authoritative artifact verifier.

The earlier1,205-check UI workspace run retains its original source boundary; it
is not relabelled as execution against this candidate. The coordinator inspected
the actual desktop/mobile selector, phone editor and320px deletion screenshots.
Independent blind review found no supported findings in source composition or
retained verification evidence; nothing was deferred. Both final artifact inventories
were rechecked after testing and stayed exact. The sanitized checked-in receipt is
[candidate evidence](evidence/ui-release-candidate-20261104.json).

Local custody is `apps/scribeswell/.local/ui-release-evidence-20261104/`: source and
delta inventories, build driver/results/logs, primary/recovery static artifacts,
browser results and `gallery.html`. The exact candidate worktree is
`apps/scribeswell/.local/ui-release-20261104/`. These ignored local artifacts must
be retained until publication/recovery acceptance; no remote availability is claimed.

## Proposed publication and recovery

After explicit approval, publish the verified **primary static artifact only** to
the existing Scribeswell Netlify site serving `https://scribeswell.com/`. Preserve
the existing backend, owner ledgers, runtime credentials, grants, corpus and saved
Studies data. No backend deployment or maintenance window is required by this static
UI update. Before publication, recheck the candidate artifact inventory and current
site identity; stop if the target has changed since the retained handoff.

After publication verify the served source/release identity, root and deep-link
reload, CSS/Hebrew font assets, selector selection and current PtS `/pts/` entry.
If this frontend fails, restore the retained **previous primary frontend**, whose
source is `59e2c8884cad24bb2f6e99fc519b2e6dc5bc9d84` and recorded Netlify deploy is
`6aeb2e2e1d25383b65007bf1`. Verify its current availability before relying on hosted
rollback. Do not automatically use the Studies-off recovery variant as rollback for
this UI-only release; it changes the visible feature configuration. No database
restore, migration reversal or shared-adoption rerun is part of frontend recovery.

The prior complete production receipt belongs to the shared-release checkout's
`apps/scribeswell/docs/SHARED_PRODUCTION_ADOPTION_HANDOFF.md`; this follow-up neither
relabels that evidence nor changes its backend source/qualification boundary.

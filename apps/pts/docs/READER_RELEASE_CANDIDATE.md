# PtS reader release candidate — 5 November 2026

Status: deployed after explicit API/frontend and gateway approvals. Live public
boundary and desktop/mobile checks pass. Signed-in cache reuse is covered by the
compiled browser and packaged API probes; live user-session timing was not measured.
Product scope and acceptance evidence belong to the existing
[reader delivery item](../../../_bmad-output/implementation-artifacts/spec-pts-reader-cache-and-layout.md).
This is the operational release card, not a replacement specification.

## Exact candidate and target

| Item | Prepared value |
| --- | --- |
| Source | `7470628602584e3d912f624171c6889b3b79d91e` |
| Published parent | `7293caf739390857600bafd2d9e2213fecd270ef` |
| Isolated checkout | `.local/pts-reader-release-20261105`, branch `pts/reader-cache-release-20261105` |
| PtS page | `https://scribeswell.com/pts/` |
| PtS API | `https://api.scribeswell.com/pts/` |
| Local API image | `agriplatform-pts:reader-cache-20261105` |
| API image configuration ID | `sha256:9a1ceb0dba49245576da562b858df7833635580152768fab335a6a275a5c1bc7` |
| Frontend artifact | `.local/pts-reader-release-evidence-20261105/primary` |
| Manual build attempt | `2026110501-1` (no GitHub workflow executed) |
| Public configuration fingerprint | `9fcab777a06fffedf6becb7f419504543724e89247321c1be2d3199f878a78cf` |
| Existing Netlify site | `e739718f-de86-4ad4-ab84-cf6249134558` |

The isolated source contains only the reader change and its packaging/test/docs
dependencies. The published parent already contains the account-access adoption.
The candidate preserves the deployed `/pts/` Vite base. Its root Scribeswell entry,
JavaScript, CSS, fonts and routing file are byte-identical to the previous primary
artifact. Studies remains enabled with the existing public configuration.

## Verification

Executed in the isolated checkout with selected Node 26.11.1 / npm 12.2.0:

- `npm test --workspace @platform/browser-cache`: **6 passed**.
- `PYTHONPATH=/tmp/pts-reader-driver python3 -m pytest apps/pts/tests/test_reader_cache.py apps/pts/tests/test_runtime_sources.py -q`: **9 passed**.
- `npm run test:browser --prefix apps/pts/web`: **192 passed**.
- The owning `package_runtime.py` completed offline using selected Python 3.15.0
  and uv 0.13.1. The explicit runtime inventory includes `reader_cache.py`.
- `docker build --network=none -f apps/pts/deployment/Dockerfile -t agriplatform-pts:reader-cache-20261105 .` passed, including `pts_runtime_verified`.
- An offline container probe imported the packaged API under Python 3.15.0 and
  proved health, the lean response, bodyless 304 reuse and authorization denial
  before cache reuse. Synthetic repositories and authority were used.
- The owning production frontend builder and release verifier passed. All 11
  artifact files have retained SHA-256 inventory entries.
- The compiled production artifact passed at 1280×900 and 390×844 with every
  browser request intercepted locally. Each used one full lean response followed
  by authorized bodyless reuses on reload and focus. Details remained expanded,
  and neither viewport overflowed or emitted a page error.

Local custody is `.local/pts-reader-release-evidence-20261105/`: scripts, test logs,
`candidate-tests.json`, `frontend-build-result.json`, `primary-inventory.json`,
`compiled-frontend-probe.json` and screenshots. Dependencies were reused locally;
this is not a clean-install or GitHub CI claim. Existing chunk-size and installed
TestClient deprecation warnings remain. Hosted latency and real provider/session
behavior have not been measured for this candidate.

The wider main checkout remains separate and contains unrelated work. Its final
38-test API/contracts/research/collection/archive run, generated-contract check
and composition dry run are recorded in the delivery item. They are not claimed
as an isolated-candidate replay.

## Proposed production action

Use the existing host, registry and Netlify deployment credentials through their
owning release tooling, after explicit approval of this card. Publish/stage this
immutable PtS API image and activate only the PtS API service, then publish the
prepared primary frontend artifact to the existing Netlify site. Record the
registry manifest digest separately from the local image configuration ID.

No migrations, account adoption, corpus import, grant changes or changes to other
API services are included. Keep existing runtime secrets, owner ledgers, gateway,
Content/private-file behavior and Studies configuration.

Before any activation:

1. Recheck the public identity is still parent `7293caf…`, attempt `2026110402-1`.
   Verify the Netlify previous deploy is ready and remains the published deploy.
2. Read current host release state, service health, PtS image and any pending
   release markers. Capture the exact runtime configuration pointer and recovery
   commands privately. Do not replay the account-adoption coordinator or schema
   histories. If baseline, health or release ownership differs, stop activation
   and reconcile the plan.
3. Confirm artifact hashes and the exact image provenance before transfer.

Activate API first so the old frontend remains compatible. Verify health and
protected anonymous denial, then activate the frontend. Check the served release
identity and every artifact hash, `/pts/` entry/deep-link reload, root Scribeswell
reading and existing Studies presentation. Verify an authorized reader's first
response, conditional 304, changed selection, exports and source documents when
an authorized session is available; synthetic sessions do not establish live
provider behavior. Record any remaining user-session checks explicitly.

## Recovery

The recorded previous PtS image configuration ID is
`sha256:bb3ae87d37fe47d03ee186c2d493f6c7fe0cb47096d318372d076b4bc6192ddb`;
its recorded registry publication is
`ghcr.io/innodat/agriplatform/pts@sha256:0c1588c2695e2a82813ad44b4e69674f887a1ce1f3df3b61ff3dae6d26247208`.
Reconfirm both against current host state during preflight.

Restore the previous PtS image through the existing service release mechanism
and restore Netlify primary deploy `6aeb87011e4242277929c51e`, source `7293caf…`,
attempt `2026110402-1`. Keep Studies enabled. Verify the restored identity and
health; do not reverse migrations or alter data. The previous primary artifact
is retained at `apps/scribeswell/.local/ui-release-evidence-20261104/primary`.

The historical [release preparation policy](../deployment/RELEASE_PREPARATION.md)
requires: “Final approval must identify the actual target, code revision, proposed
mutations, verification evidence and recovery action before production writes or
public activation”. Its earlier bootstrap inventory and route layout are stale;
this card uses the observed published identity and actual deployed parent instead.

## Activation results and gateway correction

The user approved the API/frontend release on 5 November. PtS image publication is
`ghcr.io/innodat/agriplatform/pts@sha256:0f7cc3a06eb54455b5fbc863e9821ef71dc258331577559d94b80094508206ab`.
The host pulled that exact manifest and passed the offline API probe before activation.
Only PtS restarted; the other five container IDs stayed unchanged. API health,
anonymous denial, unchanged public books and Studies denial passed. Supervisor
evidence has no shutdown warnings, and all release/maintenance/TLS pending markers
are absent.

Frontend Netlify deploy `6aec2d0ce1915d44f8a21907` is published, release attempt
`2026110501-1`, source `7470628…`. All ten HTTP-served artifact hashes match the
prepared inventory. Independent desktop/mobile live checks pass public reading,
Hebrew font loading, existing signed-out Studies presentation, PtS sign-in/deep-link
reload and no overflow/page errors. No live private session was used.

The first complete live acceptance probe failed: the public OPTIONS response
allows only `Authorization,Content-Type,X-Org-ID`, so a browser cannot send the
reader's `If-None-Match`. This is actual gateway evidence, not an API fixture failure.
The reader remained available during preparation of the correction. The subsequent
approved correction and passing live probe are recorded below.

The correction is committed as
`7d3781317d6bd18b4ff476cb5671c5b6333db343`, parent `7470628…`, in the same isolated
release branch. It changes the owning gateway renderer's PtS JSON route only:

| CORS field | Current | Prepared |
| --- | --- | --- |
| `allow_headers` | `Authorization,Content-Type,X-Org-ID` | `Authorization,Content-Type,X-Org-ID,If-None-Match` |
| `expose_headers` | Unspecified at gateway | `ETag` |

Origins, credentials, methods, routes, upstreams, TLS certificates and all other
application/private-file policies stay byte-equivalent. These fields follow the
[APISIX CORS contract](https://apisix.apache.org/docs/apisix/plugins/cors/).
One focused regression failed before the renderer correction; all nine focused
gateway/private-file tests now pass. Independent follow-up review found no supported
issues. Two isolated image schema-harness attempts stopped on missing dependency/
configuration paths; they do not establish a gateway runtime pass. The actual live
preflight and exposed-header checks remain the acceptance gate.

The staged configuration is
`/srv/agriplatform/private/pts-reader-20261105-747062860258/gateway-cors-7d37813/compose.json`.
Its hash inventory, exact two-field diff and previous pointer are retained in
`.local/pts-reader-release-evidence-20261105/gateway-cors-preparation.json`.
The preparation was staged before gateway approval. The operator invocation is
`python3 .local/pts-reader-release-evidence-20261105/activate-gateway-cors.py activate`.
It locks the existing production release, rechecks the pointer, hashes, healthy
inventory and pending markers, and recreates gateway only with its existing pinned
image. This briefly interrupts shared API ingress while the gateway restarts.
The five API containers remain running, and no schema/data/grant change is included.

After activation, verify TLS continuity, current API denial, public books, CORS
preflight/exposed ETag, unchanged API container IDs, supervisor evidence and the full
live desktop/mobile probe. Report live authorized-session cache checks separately
when a legitimate session is available.

Recovery for this additional step is
`python3 .local/pts-reader-release-evidence-20261105/activate-gateway-cors.py rollback`:
recreate gateway from the prior composition and restore the API release pointer.
It retains the already published reader API/frontend and verifies TLS/health.
The prior composition is
`/srv/agriplatform/private/scribeswell-pts-hosted-e1-20261101/native-conninfo-02/candidate/forward-685a045a9d42432f885aa2e8362ad493/gateway/compose-pts-reader-747062860258.json`.
The broader reader rollback above remains available if needed.

## Final completion — 5 November 2026

The user explicitly approved the added gateway correction. Activated source
`7d37813…` under the existing release lock; only gateway restarted, with the same
pinned image and TLS certificate. All five API container IDs stayed unchanged.
The gateway exited normally with signal 3 / exit 0; both API and gateway supervisor
receipts contain no warnings. The backend current pointer now records gateway
source `7d37813…`; frontend release identity correctly retains reader source
`7470628…`, attempt `2026110501-1`.

The previously failing live OPTIONS check now returns 200 with `If-None-Match`
allowed. The live PtS response exposes ETag, and an anonymous conditional request
still returns 401. Public books retain their exact response digest and Studies
still denies anonymous reads. The complete live browser probe passes: ten served
artifact hashes, desktop/mobile public reader and Hebrew font, existing Studies
presentation, PtS sign-in/deep-link reload, no overflow and no page errors.
A fresh host observation confirms all six services running, all five API health
checks healthy, exact configuration hashes and no pending release/maintenance/TLS
markers.

[Sanitized publication evidence](evidence/reader-cache-publication-20261105.json)
binds the image/manifest, deployments, component sources, checks and retained local
receipts. The original failed live acceptance and two schema-harness attempts remain
retained; their results were not relabelled as passes. No live authorized user session
or private-file transfer was exercised, and no hosted cold/warm timing is claimed.
Authorized reuse was proved with the compiled production artifact and packaged API
fixtures; the actual deployed gateway boundary now passes independently.
No migrations, corpus import, grants, other API restarts or Git push occurred.

# Story 3.1 active owner HTTP integration — 2026-10-28

Status: implemented, locally qualified and independently reviewed. Story 3.1
remains incomplete. Baseline `a266f9815c74bf189b560c7e6c8c14c8c3fb47ef`.

Access now mounts the reviewed Identity display router with explicit native-reader
configuration. KDG's configured API composes existing administrator history, detail
and audit-details routes with their original engines, lifespans, authority, deadlines,
private responses and generated schemas. The context-only factory remains compatible;
administrative writes are absent. The separate producer used by qualification is the
existing own-create candidate mounted only by the qualification host.

Actual preimplementation HTTP acceptance failures were Access POST404 and configured
KDG administrator GET404, observed by the implementation agent. Its focused results
are supplemented by coordinator execution below; no saved original full RED log is
claimed. The Identity28 native prerequisite was consumed unchanged.

## Fresh resources and controlled compatibility

Proof root: `platform/deployment/.local/kdg-story31-20261028/`;
fresh frame `fresh-8f3e984596bb453a902adb8710b4860d`. All accounts, passwords, JWTs,
service keys, actor IDs, organizations and records are synthetic. Credentials live
only in private local fixture files. Existing resources and concurrent work were not
reconfigured or removed. Explicit selected pinned image digests and source bootstrap
are recorded in `resource-ready.json` and `prepare_fresh.py`.

Fresh GoTrue2.197.0 performs actual user creation, password sign-in and user-token
verification. Identity account-actor/membership setup and Access registration/grants
use their protected owner commands, with private operation journals. This is local
GoTrue evidence, not an external email/Entra/provider qualification.

The initial sandbox socket/Docker attempt failed before startup. Docker then refused
network creation because its default address pools were exhausted. A new explicitly
unused subnet was selected; no old network was removed. An internal-network attempt
started PostgreSQL but suppressed published ports; that owned container stopped
normally, and its volume/network remain. A separate fresh bridge target succeeded.

Controlled Identity migration first refused inherited PUBLIC SELECT on the image's
two `extensions.pg_stat_statements*` monitoring views. Its transaction rolled back
with no Identity ledger. Fresh-target preparation removed those PUBLIC SELECT grants;
the unchanged Identity28 chain then passed. No historical reference was regenerated.

The actual coordinated Access19 upgrade next refused `access_catalog_mismatch` and
rolled back. A rollback-only observation showed **only `discovery_functions`** differed:
its historical fingerprint included three unsafe PUBLIC trigger-helper EXECUTEs that
Identity28 removes. The consuming verifier now preserves raw observations and the
immutable reference, rejects helper regrants, and normalizes only the historical
comparison copy. Its first marker lookup required forbidden Identity schema USAGE;
actual restricted migration exposed that error. The corrected catalogue-only lookup
requires no new grant. New focused RED/GREEN and controlled retry/repeat pass.
`restricted-final-metadata.json` proves actual `access_migrator` still lacks Identity
schema USAGE, heads28/19 and zero remaining runtime sessions after HTTP shutdown.

KDG foundation plus existing storage candidate passed through controlled Alembic on
a new database, using the explicit `kdg-story31-synthetic` target/port policy. The
existing retained `kdg-local:55482` target remains unchanged. Startup runs no migration;
failed attempts block qualification and receive explicit forward retry, no downgrade.

## Actual running path and verification

`http-a16176a837e0421a9340423794b8042c` records nine passing source-bound checks:
previous own-context consumer, two actual HTTP facilitator creates, replaced keyset
history pages across owners, exact original definition and retained native name,
real-session denied role matrix, selector rejection and unchanged audit on read retry.
KDG calls the active Access/Identity owner over actual certificate-verified TLS; Access
calls actual GoTrue through an ordinary local HTTP gateway. There is no synthetic
token verifier, Access decision, SQL engine or Identity reader in this journey.
Capturer-only, membership-only, platform-admin-only, foreign-org and no-membership
accounts receive403 on all three administrator surfaces. This does not yet qualify
browser SDK invalidation, a synchronized installed-PWA journey or physical devices.

All three owned HTTP children stopped with code0, without forced termination;
source equality and zero remaining runtime database sessions pass. Earlier first
HTTP proof also passed but returned signal-derived child exit -15; it is retained
separately and is not promoted to the later code0 shutdown result.

On environment resume the fresh DB and Auth containers were found exited255, without
OOM. `resume-abnormal-resource-stop.json` preserves that observation; no graceful
stop claim is made for the interruption. Only owned resources were restarted. Docker
reassigned the ephemeral DB port, recorded in `resumed-ports.json` without altering
the historical ready receipt. Starting Auth before DB readiness failed with exit1;
the resulting503 HTTP attempt and normal child shutdown are retained. Explicit Auth
restart after DB health and subsequent qualification are recorded separately.

Coordinator commands (repository root, installed Python3.15.0):

```sh
services/access/.venv/bin/python -I -B -m pytest services/access/tests/test_actor_display_runtime.py services/access/tests/test_deployment_package.py apps/kdg-capture/tests/test_configured_admin.py apps/kdg-capture/tests/test_configured_context.py -q -p no:cacheprovider
services/access/.venv/bin/python -I -B -m pytest apps/kdg-capture/write-tests/test_admin_http.py apps/kdg-capture/write-tests/test_audit_http.py apps/kdg-capture/write-tests/test_audit_display_http.py apps/kdg-capture/write-tests/test_audit_display_contract.py -q -p no:cacheprovider
services/access/.venv/bin/python -I -B -m pytest services/access/tests/test_discovery_catalog.py services/access/tests/test_capability_catalog.py services/access/tests/test_discovery_qualification.py -q -p no:cacheprovider
services/access/.venv/bin/python -I -B apps/kdg-capture/tests/qualify_story31_http.py --proof "$FRESH_FRAME"
```

Observed results: **70**, **52 plus2 subtests**, **51** tests pass respectively. The
existing Starlette TestClient deprecation warning remains. Sandbox-only worker timeouts
are retained failures, not passes. Implementation-agent affected owner checks153 and
configuration/migration checks are supplementary reported evidence. Active/isolated
owner and configured-KDG exporters are fresh. Existing pinned Node26.11.1/client tool
regenerated Access types; no toolchain upgrade. KDG API declares matching pinned SQL
dependencies; only required dependency additions were resolved.

The existing packager built an isolated frozen Access bundle offline with retained
uv0.13.1/Python3.15.0. Its verifier passes and its packaged interpreter imports the
active actor route. The sandbox cache attempt failed; the permitted retry succeeded.
The bundle deliberately includes current concurrent owner code; scoped review/commit
generation separately excludes unrelated People changes. No production image/release
activation or real credential lifecycle is claimed.

## AC-1–AC-6 matrix after this delivery

| Criterion | Current local evidence | Still required |
| --- | --- | --- |
| AC-1 current all-read | Active API → real GoTrue/current restricted Access checks; positive cross-owner and denied role matrix | Mounted real-SDK portal; complete foreign-record/session boundary browser integration |
| AC-2 responsive review | Existing reviewed responsive portal; actual two-facilitator HTTP create→history refresh, original definition/owner | Actual mounted SDK/portal journey; phone/computer runtime and synchronized own-client integration |
| AC-3 administrator audit | Active KDG→TLS Identity→restricted retained projection; exact selected name and actual create event, unchanged retry | Mounted runtime audit and relevant edit/no-op producer attribution integration |
| AC-4 online / own PWA | Active responses remain private/no-store; no administrator persistence introduced | Actual portal host/cache separation; own capture/My observations PWA and offline integration |
| AC-5 invalidation | Fresh authority per actual request; source-bound late-publication fences already reviewed | Actual SDK/account/signout/session/access changes clear rendered data; local provider versus external provider evidence distinguished |
| AC-6 accessibility/boundaries | Actual API/runtime roles plus existing reviewed DOM/Chromium evidence | Integrated keyboard/zoom/touch checks; actual assistive technology and installed Android/iPhone extension |

Post-review verification: the combined affected command covering runtime/display/native,
packaging, catalogue/capability/discovery, configured KDG, supervision, migration policy
and administrator/audit HTTP tests passed **319 tests plus7 subtests**. The final
supervisor-only run then passed **5 tests**, including actual-child SIGTERM and SIGINT
injected between OS creation and registration. Signals now defer through registration,
prevent further launches and reap the child while retaining `passed:false`.
An actual three-owner `--hold` SIGTERM run separately proves bounded normal child
shutdown and parent exit143; interrupted qualification is never a pass.

Three independent review lenses completed. Ambient host/display credential collision,
parent interruption cleanup, missing schema-collision tests and an accidental concurrent
People test dependency were corrected; targeted independent patch review found one
additional startup-registration window, now corrected and independently cleared.
No finding was deferred. A metadata observation overlapped the held owners and refused
its zero-session assertion; after shutdown the same restricted observation passed.
The final source-bound `http-1b4ae72372c64b0489d3ab0ea44a70d3` passes all nine actual
HTTP checks with all three child exits0. The regenerated offline frozen
`access-runtime-bundle-reviewfix` verifier and packaged-import smoke pass.

Next independent ready item: mount the administrator review in the ordinary local
frontend using the real SDK, existing email form/account fence and current all-read
controller, then qualify current-access/session invalidation and business-cache absence.
The existing own frontend mounts setup status only; no mounted capture/My observations
PWA or service worker exists. Do not infer its completion from adapters or HTTP creates.

Scaffold: reuse owner/migration/runtime primitives; no speculative neutral promotion.
Shared UI: unchanged in this HTTP item. Agent context: sufficient. Documentation:
this evidence, owner runbook, API guide and readiness/handoff. ADR: existing release,
transaction/logging/errors/actor decisions apply unchanged. Selected implementation
model gpt-6.1-sol/high; actual model/usage and model-only timing unavailable.

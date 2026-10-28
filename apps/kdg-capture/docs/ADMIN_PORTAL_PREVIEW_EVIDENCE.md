# Synthetic administrator portal preview — 2026-10-28

`web/src/admin-portal-preview.tsx:mountAdminPortalPreview` explicitly mounts a responsive
administrator history/detail/audit preview. Application main/index/startup, own-entry
routing, managed Auth and existing APIs/types remain unchanged. The user's Next at the
prior integration boundary authorizes this separately bounded synthetic preview; it
does not authorize live startup, credentials, migrations, grants or deployment.

The KDG-owned controller consumes the unchanged generic Auth lifecycle with an app-owned
all-read boundary. Only returned epoch-checked current server reads admit a page; own-read
context, roles, membership alone and actor labels never authorize administrator review.
Session lookup/refresh/events/signout remain supplied Auth-port operations, synthetic in
this proof. Bearers stay inside requests/execution leases, outside published UI state.

## Visible behavior and bounds

History shows at most five records with child, observation date and original capturer.
One authorized history GET is followed by at most five audit-details GETs with limit1,
using only returned capture IDs. One original maximum ten-second executing-read budget
covers all phases; partial rows never publish. Capture/owner/creator bindings must match.
Successful empty pages require no enrichment. History and audit cursors replace pages;
no archive, export or offline grant is created.

Fresh detail and audit reads must agree on identity, revision and update attribution
before answers and latest audit render together. A concurrent mismatch yields safe
unavailable feedback and explicit Retry. Answers follow the exact original definition,
including rating meanings, Ja/Nee, text and boolean details. Optional read-only audit
preserves original creator/latest modifier, actual executor/separate initiator, committed
events, exact server times and revision strings. It starts collapsed. Resolved names
remain exact; unmapped names and valid temporary name outages have distinct fallbacks.
Retry always repeats complete current-authorized reads, with no automatic retry.

Refresh, account/org/session change, signout, offline and disposal synchronously clear
visible business state and cancel owned work. Late success/errors cannot reopen it,
even when transport ignores cancellation. Initial browser offline makes no all-read
request; reconnect verifies current all-read. Denial, expired authentication and service
unavailability remain distinct. Back freshly reads history and restores selected-row
focus/scroll; pagination focuses the new heading. Existing neutral colors,48px controls,
visible focus, wrapped layouts and safe React text are reused.

## Qualification

Final capsule: `platform/deployment/.local/kdg-admin-portal-20261028/run-8015e572-c0b4-4fac-b303-7354374ae298/`.
Strict TypeScript7.0.2 compile with immutability/API negative cases,20 controller tests
and21 named actual Chromium assertion groups pass. These are21 browser groups with
multiple assertions, counted separately from controller tests. Browser proof includes initial offline, five-row enrichment,
original question order/answers, safe HTML-like names, unmapped/outage Retry, complete
versus partial/foreign/empty pages, revision mismatch, separate history/audit paging,
focus/scroll return, delayed last enrichment, six same-call DOM invalidations, actual
held HTTP success/403 after signout and disposal with ignored abort, applied date changes/cursor reset, visible recovery from persistent record/audit404,
distinct mounted executor/initiator values, and exactly eight expected failed HTTP
responses/console events. No other page errors were accepted.

Desktop1440px, phone390px and320px/200%-font layout simulations pass with retained
screenshots. Measured text/control contrast is19.80:1/17.18:1. These checks do not
establish physical-device, actual browser zoom or assistive-technology qualification.
The isolated context has no local/session storage, IndexedDB databases, CacheStorage
entries or service-worker registrations; this does not qualify a deployed PWA worker.
Owned loopback server stopped normally with zero remaining sockets; proof artifacts
remain retained. Parent inspected the source-bound results and the phone screenshot.

Five affected source-bound proofs pass333 cases: history121, detail78, aggregate109,
presentation9 and prior audit-review state16, each with strict types. Parent separately
passed118 generated Auth lifecycle cases and managed Auth/test parity. Backend/native/
physical-device suites were not rerun because their code/contracts were unchanged.

From repository root with retained Node26.11.1 and dependencies, no installation:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/admin-portal-proof.mjs
```

`--unit-only` skips the browser; `--acceptance-only` selects the first controller case.
The [machine evidence](evidence/admin-portal-preview-20261028.json) binds exact command,
source, result/log digests, regressions, browser groups and lifecycle receipts.

ATDD history is explicit: the first RED stopped at a missing factory assertion.
The second executed an emitted inert factory and failed checking != history before
implementation; strict compile failed while UI/fixture files did not yet exist. It is
not claimed as a compile-success RED. Expanded cases followed implementation, not
individually test-first. A draft temporary-outage expectation was corrected against the
existing valid-degradation contract, not with a production workaround.

The interruption discarded the earlier `/tmp` capsules, including those initial RED
logs and the pre-review GREEN. Their machine-recorded digests/history are retained as
**unavailable historical receipts**, not independently reverified artifacts. Qualification
now stores capsules under the ignored repository-owned directory. The exact pre-review
controller was recovered from the staged index and matched its previously recorded
SHA256. A new private-capsule reproduction compiles successfully and fails all four
pending/overlapping logout regressions; current code passes them. That is a post-resume
fault reproduction, not a reconstruction of test-first history.

The first repository-local proof passed types/controller tests but Vite inherited the
stale root receipts configuration and failed its build. That failure remains retained
at `run-abf6d80a-a962-4054-a460-7e9113883e1e`. The owning browser harness now supplies
its explicit capsule TypeScript configuration, as existing Auth qualification does;
root configuration/dependencies were not changed. Final qualification passes.

## Review, impact and limits

All three review layers completed. Five findings grouped into four patches: pending
signout could reopen after reconnect; persistent404 offered no visible history exit;
applied dates and mounted actor attribution needed behavioral assertions. Parent verified
the two runtime defects. The controller now preserves explicit signout intent across
lifecycle replacements until deliberate Sign in/Retry, and late old logout results cannot
clear a newer fence. Unavailable review exposes Return to history. Browser regressions
prove changed dates replace cursor/results and show separate actual executor/initiator.
Independent patch review found zero remaining supported findings and independently
passed20 controller tests; it inspected the browser receipt without rerunning Chromium.
No new deferrals. All631 protected preexisting KDG files match baseline Git blobs.

Scaffold: generic lifecycle and transport/validation primitives reused unchanged; KDG
all-read pagination/name composition and questionnaire labels stay local. Shared UI:
existing neutral theme reused, no newly proven domain-neutral pattern to promote. Agent
context unchanged. Docs: contract/testing/readiness/handoff and evidence updated together.
ADR0022/0023/0031/0032/0056 and ADR0061 remain authority; no accepted ADR or release-tool
change. Delegated implementation selected gpt-6.1-sol/high. Coordinator model, token usage
and model-only elapsed are unavailable; logs measure test/tool waits separately.

This qualifies a browser-mounted synthetic consumer, not full Story3.1. Actual selected
Auth/provider and running Identity/Access/KDG integration, native Identity retained actor
projection/permissions, deployed own-PWA versus portal separation, installed Android/
iPhone extension, assistive technology and controlled release remain gates. Current
role loss is observed through fresh verification or supplied Auth invalidation, not a
new role-change push channel. The preview itself supplies neither live authority nor
proof of a real grant, retained actor privilege or server deployment.

No production startup/config, editor/Leave, real services/accounts/credentials, native
DB/Docker/migrations/grants, worker/queue, dependencies, deployment/production/pilot/push
or cleanup changed. Preexisting sources, concurrent work and historical resources/evidence
are preserved; the prohibited migration fixture was not accessed/run/copied/hashed.

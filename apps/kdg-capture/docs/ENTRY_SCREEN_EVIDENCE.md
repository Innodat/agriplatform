# KDG accessible entry screen — 2026-10-22

The bounded slice is complete after Blind Hunter review:15 focused presentation tests,
29 unchanged client tests, strict TypeScript7.0.2 and13 built-React/Chromium proof checks
pass. See [the durable receipt](evidence/entry-screen-20261022.json).
bmad-help selected [BD] bmad-build for Story1.1's visible current-entry presentation.
This is a React component with injected sign-in/recheck actions, not a configured
product frontend, real Auth provider, renewal/callback or safe-return implementation.
It consumes the existing typed entry boundary without changing any previous client,
API, generated DTO or historical evidence. Domain setup remains explicitly incomplete.

## Acceptance and focused tests

Story1.1 AC1/4/6 and KDG-A01.entry-allowed.presentation,
KDG-A01.entry-denied.presentation, KDG-A19.entry-accessible.fixture map to the new proof.
A conservative screen seed displayed only static sign-in text. Before implementation,
the actual built React/browser acceptance successfully called the synthetic own API
but failed waiting for the Setup not completed heading. Proof
screen-0155c439-ac37-4c5d-98de-9f7e5c26c439 retains exact source, built files and failure
receipt. D/acceptance-red.log is a concise transcript, not a full raw stdout log.
Focused static-render tests failed all14 against that same conservative behavior
in screen-88fa3b8b-62f8-4d58-98f8-7cc53c535d62/unit.log before implementation.
No expected application behavior was altered to dismiss a failure.

Earlier harness failures remain retained: CSS import declaration missing, then Vite8
searched the stale root tsconfig references despite an owner config in the source copy.
An explicit Vite8 tsconfig path and isolated build child working directory resolved
that harness issue without changing repository root files. None is behavioral RED.

D: platform/deployment/.local/kdg-entry-screen-20261022.
N: platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node.
From repository root:

- `N apps/kdg-capture/web/tests/screen-proof.mjs`: copied source capsule, strict TS7,
  Vite8 build, actual Chromium/native-fetch UI journey and15 focused static-render tests.
- Add `--unit-only` for strict TS7 plus15 focused tests; `--acceptance-only` selects
  the admitted-account/setup-state behavioral test after strict compile and Vite build.
- `N --test apps/kdg-capture/web/tests/entry.test.mjs`: unchanged affected29 client tests.
- `N node_modules/typescript/bin/tsc --project apps/kdg-capture/web/tsconfig.json`:
  unchanged client's strict types/readonly assertions.

Approved retained tools are reused, with no installation, root workspace or lock edit:
React/DOM/types19.3.0, TypeScript7.0.2, Playwright1.64.0 from scaffold proof-dI2Gy9;
Vite8.3.4/plugin-react6.1.2 from that proof's apps/bootstrap-application/web/node_modules;
Chromium1248 from the retained web-baseline-qualification cache. The source capsule
links the retained dependencies read-only in use; builds emit only in new proof roots.

## Behavior and limits

KDG Capture and Khula Development Group are static branding, never access evidence.
The component renders only selected static status text, never context IDs, tokens or
server messages. Failure families remain distinct. Sign-in/recheck is explicitly
invoked through callbacks; no automatic sign-in/retry loop. Offline state masks even
previously admitted setup and disables network actions. Reconnection alone confers no
new authority; the integrating host owns clearing/rechecking current state.

The stable native button uses aria-disabled with a guarded click handler, keeping
keyboard focus through checking and result transitions. There is a skip link, semantic
main/headings, polite atomic status, visible focus and48px minimum controls. Browser
checks cover native keyboard/DOM semantics and320/1280px layouts with200% text; the rendered contrast ratios are measured; these
are not actual screen-reader, installed Android/iPhone or device qualification. Neutral
semantic tokens are source-referenced from the existing shadcn lineage; no palette,
logo, shared app import or generic component library is introduced. Actual screen-reader/device
and provider acceptance remain consumer obligations.

Synthetic sessions drive the actual createEntryBoundary and client through native
browser fetch against an HTTP API fixture. This does not rerun the actual KDG handler,
Access/SQL or Auth provider. Protected actions still require their own current server
authority. No questionnaire/capture/admin/local-store/lease functionality is exposed.
The React screen is source-consumable; mounting, provider event ordering, session
renewal, validated return navigation and public product entrypoint remain next work.

## Delivery impacts

Scaffold: reuse semantic shell/skip/focus/client conventions, no generated template
edits. Shared UI: ui-core remains a placeholder and no proven sign-in component exists;
keep this first KDG composition local until another consumer proves a common pattern.
Agent context: root rules suffice, command guide updated in web README. Documentation:
this owner evidence, additive handoff and Build spec. ADR: adopt current access/scope,
errors/session/logging/release decisions, no new decision or accepted ADR edit.

No real sign-in/accounts/access, provisioning, Docker/resource changes, domain writes,
Leave/editor, production, deployment/pilot or cleanup. Fingerprints/HMAC stay deferred.

## Final review, proof and preservation

All six Blind Hunter findings were patched: move busy semantics from the status ancestor
to the stable button; exit1 when custody fails; check both callback counters and request
counts during blocked activation; cover longer authorized/actor/denied/unavailable/offline
states at320/1280px and200% text; protect required explanatory copy; and identify the
exact green receipt. No finding is deferred. The live-status regression first failed
in screen-b231bbf0-377f-408c-8d33-252453b6dde1 before its source fix; this is DOM-semantic
evidence, not a claim to have measured a real screen-reader announcement.

Final reviewed green: D/screen-56b1bfab-9497-477a-b9b1-6b8c8f47fac4/result.json,
with15 passing tests in unit.log and source fingerprints in that result. All13 recorded
checks pass. Measured rendered contrast: body19.80:1, button text17.18:1, control17.93:1,
focus19.80:1, exceeding the selected4.5/3 thresholds. Ten responsive-state screenshots
are retained. Every prior attempt remains intact, including the initial harness errors
and pre-review green proofs. The receipt verifies source custody and stopped HTTP server.

A separate --unit-only run with /tmp/kdg-screen-drift-injector.mjs returned exit1 with
source_unchanged:false despite all15 unit tests passing. It alters only the final
in-process custody read; source files on disk are untouched. Its receipt and
D/custody-negative.log remain retained. This proves the corrected command failure,
not an actual repository drift incident. Source and injector hashes are in the durable
receipt. Existing client strict check exits0 and client-regression.log records29 passes.

All427 protected KDG/client/API/contracts/Access/builder/root dependency baseline files
remain byte-identical to baseline7c0bac50ac8fa7de8af28d69e2694b43c7dc80c4, excluding only
the authorized additive handoff and updated web README. The complete prior handoff is
an exact suffix. Concurrent commits/changes stay excluded. No Docker, native backend
or real Auth work was performed or newly claimed.

Final visual inspection kept mobile gutters at the specified16px during text
enlargement, giving the brand more wrapping room. The final source-bound proof above
reruns every affected screen check after that CSS adjustment.

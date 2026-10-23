---
title: 'KDG local frontend startup and public configuration'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Add the actual KDG HTML/main startup entrypoint to connect explicit, inert public configuration to the existing local entry-route composition. The checked-in page has no configured target and must fail closed without Auth/storage/API work. Accept a thin, versioned, closed local/CI configuration containing fixed org and public Auth URL/key only; require loopback page/Auth origins and preserve same-origin KDG API access. Never select config/org/provider from query, hash, sessionStorage or ambient environment, nor add real credentials/default accounts/grants. Missing/malformed/oversized/duplicate/wrong-type config, unsupported routes and invalid inputs fail safely without echoing raw values. Existing route scrubbing, current admission, email method and storage/session boundaries remain binding. Cached-page restoration must recheck current access rather than restore stale admission.

Promote the bounded inert DOM JSON reader and emitted behavioral tests through the existing scaffold, keeping KDG schema, host/method/org policy and branding local. Prove the actual copied app index/main build, not only fixture entrypoints, using synthetic loopback Auth/API HTTP and browser tests. Preserve previous test journeys/evidence, concurrent work, Docker resources and approved dependencies including TypeScript7.0.2. No root workspace/lock/dependency changes, actual email/Auth provisioning, real accounts/access, production, deployment/pilot, Leave/editor, cleanup or fingerprints/HMAC.

</frozen-after-approval>

## Implementation Notes

- bmad-help [BD] Build follows ac176cb0894bac3567e964f9a7c9f8fb5e330782. Freeform local startup prerequisite, not complete Story1.1. Existing authorization requires preserving concurrent dirty-tree changes; /tmp/kdg-startup-before.json captures the baseline. No reset/stash. Small reversible oneshot; no intent gaps or external side effects required.
- Step02 read-only investigation confirms root workspaces exclude KDG; do not change baseline to add it. Reuse retained proof-capsule Node26.11.1/TS7.0.2/SDK2.117.3/React19.3/Vite8.3.4 dependencies. Existing auth-proof builds a fixture; add a second actual app build and include src/main.ts explicitly in strict tsconfig. No npm dev/build command falsely routed through root or implicit downloads.
- Code map: canonical lifecycle.ts/test-auth-lifecycle.mjs add bounded inert script reader and emitted tests, existing sync adopts two managed files. KDG local-public-config.ts owns exact schema_version/environment_kind/org_id/auth_url/auth_public_key policy and loopback restrictions; auth-public-input.ts extracts existing URL/public-key validation without importing SDK, with old characterization retained. startup.tsx reads DOM, validates root/config and observes route/connectivity before lazily delegating to LocalEntryRoute; ClosedEntry reuses the safe failure/scrub UI. main.ts owns document lifetime and cached-page restart; index.html contains null config, not a target.
- Tests: first missing reader/actual startup RED; focused parser/schema/loopback/private-key cases before implementation. Extend auth-proof source capsule, units and second Vite build rooted at actual web/index.html; serve synthetic config variants without URL selectors, actual loopback Auth/API transport, instrument storage before modules. Prove absent/invalid DOM/config, wrong host/auth target, callback refusal, cold offline, actual sign-in/reload/current denial and cached-page recheck. Keep all previous98+48 and58 checks unchanged.
- Configuration fields exactly schema_version=1, environment_kind=local_disposable|ci_disposable, org_id canonical nonnil UUID, auth_url loopback HTTP(S) origin only, auth_public_key public publishable or legacy anon. No configurable API target; current /api/v1/context is same-origin and actual local API routing remains host-owned. Inert JSON <=8192 UTF-8 bytes, exactly one script of application/json, no src. Default null fails closed. No UI exposes technical recovery details or raw configuration.
- Impacts: scaffold neutral reader/tests/guidance same item; shared UI no promotion, existing owner entry reused; agent context existing ownership sufficient; docs/evidence/receipt/handoff updated; ADRs unchanged, applies0023/0032. Root locks, native/environment/template fixtures and version baseline unchanged. Actual SMTP/server expiry/single-use/device and full environment readiness remain outside proof.

- Final implementation separates pure public-input validation from SDK imports and lazily loads LocalEntryRoute after config/route/connectivity preflight. ClosedEntry reuses the existing owner surface. Invalid root still runs a short scrub observation; no root/client is created. Pending import completion rechecks current state, suppresses disposed mounts and hands off observer ownership once.
- Behavioral RED: emitted reader proof-j0WIDn; actual-index startup auth-00328dc6-c53e-407d-afa6-fb9a34230eab; focused environment-array/newline-org rejection; missing-root callback scrub auth-475df01f-2aae-40e5-881d-12369393ecca. Earlier capsule test import-path failures are diagnostic only. auth-0ba3833d-2765-4380-add7-92096ae2ffaf exposed SDK import-time storage probing; lazy loading fixed it.
- Final owner proof auth-80debba7-f84b-4c11-b672-e9b8b0315ca5: 108 emitted + 48 owner + 14 config tests = 170; 71 compiler/SDK/React/browser checks, source unchanged, server stopped. Neutral proof-heQYzO: 108 emitted tests. Builder 68 tests and strict TypeScript 7.0.2 pass. Fresh offline generation and final receipt bind exact commands/results.
- Browser qualification boundary: CDP reports BackForwardCacheDisabledForDelegate in retained headless shell. Real Back reload checks current denial. Explicitly simulated persisted pagehide/pageshow checks synchronous root clearing, current denial and no stale admission. Actual BFCache restoration remains unqualified; no trusted restoration claim is made.

## Review Triage Log

Blind Hunter, eight original findings plus one follow-up coverage gap; all patched. Final read-only follow-up found no residual concrete issues. No separate deferred feature added.

1. medium / patch — Missing/duplicate root previously skipped URL scrub; short observer now scrubs without client work. Combined root/callback behavioral RED then GREEN.
2. low / patch — Evidence referenced a pending receipt; completed durable source/proof/command receipt before delivery.
3. low / patch — README route-only startup limitation was stale; explicitly marked historical and superseded.
4. medium / patch — Manually dispatched event was overstated as actual browser cache restoration; real Back checks and retained CDP failure establish exact boundary, simulated lifecycle labeled explicitly.
5. medium / patch — Restoration lacked revoked-access and stale-admission coverage; denial and pre-restart empty-root/no-old-admission observer checks added.
6. medium / patch — Pending lazy import disposal lacked coverage; held chunk is released after pagehide and owner calls remain zero after completed import.
7. medium / patch — Pending lazy import offline/unsafe-route state lacked coverage; completed import cannot mount, reconnect/explicit clean start recover.
8. medium / patch — Lazy chunk rejection lacked coverage; controlled 503 renders branded safe failure and disposes cleanly with zero owner calls.
9. medium / patch (follow-up) — Fixed delay did not prove pending import completed; await same module URL and subsequent task before asserting cancellation. Final follow-up confirms closure.

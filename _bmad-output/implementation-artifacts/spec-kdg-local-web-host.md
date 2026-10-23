---
title: 'KDG explicit local web host and same-origin API'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Connect the actual KDG frontend to its API through an explicit disposable local/CI web host. The existing actual-build proof supplies HTML and synthetic API responses itself; it does not yet qualify real host routing to FastAPI. Add an opt-in owner Vite configuration that requires an explicit bounded JSON configuration file outside served roots, validates existing public KDG fields and a fixed loopback API origin, safely embeds only public fields in the existing inert config script, binds loopback and retains same-origin business requests. Missing/invalid input must stop before listening, with opaque errors and no ambient authority fallback. Preserve the ordinary checked-in null startup when this opt-in host is not selected.

Share the proven neutral host helper and its behavioral tests through the existing managed scaffold adoption, keeping KDG schema, API route and provider policy owner-local. Proxy only declared read-only API paths with bounded execution/body size, safe unavailable errors, no redirects, no cookie/service-key forwarding and no URL/payload diagnostics. Unknown API routes must never fall through to HTML. The host is development-only; it does not create accounts, grant access, start shared infrastructure or activate a release.

Given valid explicit local configuration, when the actual Vite CLI serves the copied app and the browser signs in using synthetic loopback Auth, then its same-origin context request must reach the actual KDG FastAPI implementation and display its current access result. Given current denial, invalid selectors or an unavailable API, requests must fail safely without reusing admission or exposing server configuration. Given unsafe or absent host configuration, no listener/target request should start. Observe behavioral acceptance failure before implementing the host; use focused tests for neutral routing/serialization and owner validation.

Preserve concurrent changes, all historical source/evidence/resources, Docker resources and the approved dependencies including TypeScript 7.0.2. Use retained tools and fresh private proof capsules; no root workspace/lock/dependency edits. Synthetic local/CI only: no Leave/editor, production, real accounts/access/email, provisioning, deployment, pilot, cleanup or fingerprints/HMAC. Actual Auth/SMTP delivery, server expiry/reuse/device/BFCache, installed application workspace and full Story 1.1 readiness remain separate gates.

</frozen-after-approval>

## Implementation Notes

- bmad-help [BD] bmad-build selects this local runtime prerequisite after dcce7e2571684c069e0f1b49a45df8811a826c09. Freeform prerequisite, not Story 1.1 completion; no sprint key. Catalog/config/current owner contracts and prior startup/configured-context evidence grounded the selection. Existing user authorization covers preserving concurrent dirty work; /tmp/kdg-host-before.json binds the baseline. No reset/stash or unrelated edits.
- No user-visible intent gaps or irreversible actions. Small opt-in host plus tests, generated adoption and documentation; oneshot. API/domain/Auth runtime behavior is reused. No migration or dependency installation. A fresh retained capsule supplies dependency resolution and ports; no claim that root npm dev/build runs KDG.
- Code map: canonical web/local-host-tools/local-entry-host.mjs and test-local-entry-host.mjs provide neutral Vite plugin/config. The existing installer deliberately fixes inventory: a new scoped kdg-local-host-pattern.ts uses a separate managed root, preserving the Auth identity/inventory and generic installer safeguards. application-renderer/local-host-pattern tests assert emission/parity/tamper refusal. KDG local-host.config.ts owns file/public-schema/API route/CLI choice. Existing parseKdgLocalPublicConfig and index/main reused; no managed hand edits.
- Proof: new local-host proof builds a private copy and invokes retained Vite CLI with actual owner config; separate actual FastAPI process uses explicit synthetic Access transport only, no real Access SQL/DB/shared infrastructure. Loopback synthetic Auth HTTP remains fixture-only. Existing 170 owner tests/71 checks are regression, not new provider/server evidence. Focused neutral tests run against rendered/installed output as well as owner adoption; builder/full offline generation verify scaffolds.
- Impact decisions: scaffold helper/tests and parity same delivery; shared UI unchanged; agent context existing ownership rules sufficient; owner/scaffold guides, evidence/receipt and additive handoff updated; ADRs unchanged, applies 0023/0031/0032. No schema/release activation; no retained native resources touched.

- Read-only investigation used current owner/API/runtime/ENV/scaffold sources; the attempted investigation subagent never initialized, so no external answer was relied on. No unresolved intent gap. Existing installer inventory changes refused safely; do not weaken its generic ownership contract. The new separate host root is installed/refreshed by sync-kdg-local-host --write; --check validates source/manifest/classifications/inventory. Auth copies/manifest stay byte-for-byte unchanged.
- Acceptance RED: actual Vite CLI/FastAPI browser journey cannot reach Sign in with missing opt-in config. Initial root-reference module errors are part of missing default host wiring, not isolated null-config UI proof. Existing startup tests supply that behavior. Focused GET-body and malformed/truncated upstream JSON tests fail before fixes. Missing-method/typing/config-path/module-discovery attempts retained as diagnostics, not overstated behavioral RED.
- Final proof proof-ec214ec7-49c7-4171-85e5-d30600eaf409: 10 runtime/config/browser/strict-TS7 checks, source/capsule hashes match, API SIGTERM and Vite143 intentional exits, no forced kill. Actual Vite CLI -> actual KDG API; Access transport and Auth HTTP are synthetic. 11 invalid config/host variants refuse before listening. Private file/env isolation, current denial, selectors/unknown paths, outage and log canaries pass.
- Final checks: 5 neutral host tests (actual 12s deadline); builder70 and strict TS7; unchanged Auth170/71 checks; API79 with known Starlette/httpx warning; full offline generation proof-tyQXOu passed bootstrap-only, generation_ready=false. Exact commands/source/proof hashes in receipt. No dependencies/root workspaces/native fixture or Docker operations changed. Historical sources/proofs and prior handoff suffix preserved.

## Review Triage Log

Blind Hunter: seven original findings and two follow-up gaps; all patched. Final follow-up finds no remaining concrete issues. No deferral.

1. medium / patch — Lexical config-file check missed served dependency/symlink roots. Resolve real path, reject node_modules paths/inside-app placement and nonregular/oversized files; dependency/symlink CLI negatives pass.
2. medium / patch — Screenshot failure could skip shutdown/result. Guard evidence separately, attempt every owned shutdown step independently, retain failed status and final receipt.
3. medium / patch — Hashes taken after copying could misidentify executed bytes. Capture before copy, compare before execution and after; missing/unreadable input records false.
4. medium / patch — JSON MIME alone admitted malformed/truncated bytes. Bounded fatal UTF8 decode/JSON parse before relay; focused RED then GREEN.
5. medium / patch — Collected browser errors did not affect qualification. Exact expected status set and page-error refusal now gate pass.
6. medium / patch — Log safety lacked evidence. Scan captured post-shutdown API/Vite logs for private/service/refresh/bearer sentinels including exact issued JWTs.
7. medium / patch — Scaffold test exercised only KDG sync. Render/install full application and execute its emitted behavioral suite.
8. medium / patch (follow-up) — Literal bearer sentinel missed actual generated JWT. Track exact issued tokens and include all in log scan.
9. medium / patch (follow-up) — Disappearing source could prevent result emission. Catch missing/unreadable files and record source_unchanged=false.

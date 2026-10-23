---
title: 'Synthetic PKCE launch and callback controller'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

The entry lifecycle delegates interactive sign-in and cannot yet coordinate an OAuth launch with its callback. Implement a bounded, copyable controller with explicit configured Auth authorization endpoint, app callback URL, provider/scopes, PKCE-capable begin/exchange ports, synchronous owner transaction store, navigation/address-bar replacement and admission pause/check ports. KDG adapts the installed Supabase SDK and its existing private current-context API. The scaffold owns neutral code and emitted tests in the same delivery.

Given an explicit launch, invoke the SDK without automatic browser redirect; accept only the exact configured authorization endpoint/provider/callback/scopes and S256 challenge, record its explicit SDK flow ID, then invoke navigation. Given overlapping launch calls on one controller, share one operation. Given an outstanding transaction, refuse replacement until it has been consumed or explicitly invalidated. Given the exact app callback, strip code/error parameters through injected address replacement before awaiting exchange, consume the pending transaction once, enforce its configuration binding and finite ten-minute lifetime, and exchange using its explicit flow ID. A successful SDK session alone is insufficient: resume only after current owner authority verifies the returned account and fixed organization. No callback automatically submits any domain action or restores another account's context.

Given missing/expired/foreign state, malformed or duplicated parameters, provider failure, storage/SDK/admission errors, deadline, cancellation/disposal or late completion, fail safely without raw payloads, automatic redirect loops, code replay or late admission. Duplicate callbacks on one controller share its one callback operation. New attempts after failure require an explicit launch; clear history and consume state even for refused callbacks. Preserve existing return-selection boundaries; KDG currently has only root entry, so no new domain route or form restoration is introduced.

Keep storage and Auth client construction injected: no production persistence or browser storage default is selected. Real SDK tests use explicit PKCE, manual URL handling and injected synthetic storage/fetch; browser fixtures may use isolated test state. This delivery does not activate a product frontend, configure Entra, provision accounts/access or qualify provider/device readiness. Preserve concurrent work, historical evidence, Docker resources and the approved dependency baseline including TypeScript7.0.2. No Leave/editor, production, deployment/pilot, cleanup or fingerprints/HMAC.

</frozen-after-approval>

## Implementation Notes

- BMAD Help [BD] selects bmad-build from the current handoff. This is a freeform prerequisite, not complete Story1.1; no sprint/Leave epic artifact changes. User has authorized preserving concurrent changes. Step02 read-only investigation reused investigate_entry_view; source confirms explicit flow ID avoids SDK's legacy latest-verifier fallback. Automatic sb_flow_id augmentation is experimental and is not enabled here.
- No user-visible persistence choice is needed for this injected synthetic candidate, and no irreversible effects. One cohesive controller/adaptor/test increment uses the existing three managed Auth files, without ownership-inventory changes or package dependencies. Public bootstrap will still need an explicitly selected storage and lifecycle policy and actual provider qualification.
- Code map: platform/builder-cli/templates/application/web/src/auth/lifecycle.ts owns the neutral controller alongside existing lifecycle/return guards; scripts/test-auth-lifecycle.mjs owns generated acceptance and focused tests; sync-kdg-auth.mjs updates KDG via the preserving installer. KDG web/src/auth-entry.ts adapts typed SDK launch/exchange and getCurrentContext; tests/auth-entry.test.mjs proves actual SDK PKCE and owner authority; auth-fixture/main.tsx and auth-proof.mjs prove browser launch/callback address scrubbing and current context. Existing API/SQL and historical helper behavior remain unchanged.
- Controller store is synchronous and owner-isolated, with read/write/take semantics; take removes state atomically before asynchronous exchange. Records hold only version, explicit flow ID, creation time and exact public configuration binding. No session/token/verifier/form values belong there; the configured SDK remains their owner. Store implementation and trusted client construction are caller responsibilities. Transaction expiration is not a browser persistence guarantee.
- Controller deadline at most10s bounds launch and callback admission; late SDK side effects cannot be undone, so pause/dispose prevents presentation/publication and no revoked-session claim is made. An explicit invalidation aborts owner verification and settles pending work. Navigation and scrub callbacks may reenter; execution checks must survive this. Owner admission is always current, never persisted from launch state.
- ATDD: observe emitted launch/callback acceptance RED and consuming KDG/SDK RED before runtime implementation. Focused TDD covers endpoint/query/state attacks, replay, deadline, storage errors and lifecycle races. Then run generated tests, KDG strict TS7/SDK/React/Chromium proof, builder regression/parity and full offline application generation; retain failed frames and exact requirement-to-test/source/log custody. Configured Blind Hunter review and individual triage precede final scoped local commit.
- Impacts: scaffold applicable (code plus emitted tests and guidance now); shared UI unchanged (controller ports only); agent context existing same-item parity guidance sufficient; documentation new evidence/receipt and prepended handoff with history retained; ADR no new platform decision or accepted ADR edit, implements0032/0023 and Story1.1 AC5. Provider/client storage defaults remain outside this synthetic candidate.

- Acceptance RED: generated proof-16Mh3n and owner auth-d6474144-c572-4670-96cf-e230c344e1b5, with prior36/71 intact. Focused RED proof-nYjZv3 and recovery RED proof-lbHcWO preceded implementation corrections. Actual SDK PKCE proves challenge/verifier/explicit slot and current admission. Initial full application proof-txP8kE passes. Parallel builder no-output test observed that new proof directory; sequential rerun preserves expectations.
- Configured review complete:8 findings (54.728kB, floor8), all patched with focused RED proof-qluqtn and additional actual SDK/browser tests. Owner-config RED auth-db0f4e75-8e33-482d-9c7c-eca7e26ea4ea justifies snapshotting configuration. Completed callback authorization expectation amended because review proved stale authority; pending identical callbacks still share work, completed/mismatched invocations scrub/refuse. No frozen intent change or deferral.

## Review Triage Log

- high / patched: completed callbackWork could return stale authorization for a later malformed callback and skip scrubbing. Only identical pending callbacks deduplicate; later invocations scrub/refuse. Focused RED proved cached authorized vs invalid_callback, final tests verify no exchange replay.
- medium / patched: parallel controllers could both prepare then overwrite one pending record. Recheck owner storage and current execution after SDK begin and before publication; a shared-store deferred two-controller test proves one published flow/navigation survives.
- medium / patched: pause/scrub can reenter invalidation and create a newer transaction, then old finally consumes it. Snapshot public transaction before ports, compare current unchanged record and execution before take; both reentrant tests preserve replacement metadata.
- medium / patched: read can invalidate execution while returning empty. Recheck validity after read before begin; test proves no SDK preparation starts after disposal.
- medium / patched: real SDK late session writes lacked proof. Delayed synthetic token responses after deadline/disposal demonstrably save an SDK session, while callback stays failed/cancelled and owner admission is never invoked. No SDK cancellation/revocation claim.
- medium / patched: fixture owner/org replacement left old OAuth controller/state active. Invalidate/dispose and clear pending metadata; Chromium tests pending launch and delayed exchanges for both replacements, with late response unable to remount.
- low / patched: malformed callbacks lacked browser address proof. Duplicate-code, provider-error and fragment callbacks now assert actual clean history, consumed state, no exchange and paused view.
- low / patched: generic pause-error test stopped at launch. Dedicated callback test proves pause failure still scrubs/consumes its original transaction and performs no exchange.

- Final verification: generated68 in proof-2OATbt; KDG111 (68 generated +43 owner) and27 strict compiler/build/SDK/browser checks in auth-79a38360-78b0-4db3-bd43-57dc47a1d376; builder68 sequential and strict TS7 pass. Final full offline application proof-xu5dVs passes26 recorded commands with exact final source. Retained receipts bind source/log custody and unrelated concurrent exclusions. No dependencies, SDK default storage or Docker resources changed.

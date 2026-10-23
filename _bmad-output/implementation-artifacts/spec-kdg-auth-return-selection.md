---
title: 'KDG identity-safe return selection'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

KDG has session renewal and current admission, but no validated return-selection boundary for reauthentication. Implement the next bounded prerequisite from Story1.1 AC5 and platform ADR0032: remember only an approved internal destination and prior account/organization identity in memory, then select restoration only after a fresh, permitted owner observation matches both. Every other outcome selects the safe entry page without prior-user context.

The neutral scaffold owns the helper and emitted behavioral tests; KDG consumes managed copies and a thin adapter using its existing private GET /api/v1/context. Only KDG's implemented `/` entry route is approved; scaffold fixtures may prove additional explicit routes without adding KDG domain pages. Given a captured approved destination and matching fresh owner authority, restoration succeeds once; given an external, malformed, encoded, query/fragment-bearing or unapproved target, capture refuses without requesting authority. Given another account/organization, denied/unavailable/malformed authority, timeout, clearing, disposal or supersession during verification, restoration returns only the safe destination. Replaying a consumed intent cannot restore it. Verification is bounded and receives cancellation; no late outcome can select restoration after invalidation.

Keep return state minimal: approved path and identity only, no credentials, form values or opaque arbitrary URL. No navigation, storage, provider/PKCE configuration, callback exchange, real sign-in/account/access, provisioning, deployment/pilot, cleanup, Leave/editor or domain write is authorized. Preserve concurrent changes, historical evidence/Docker resources and the approved baseline including TypeScript7.0.2. Fingerprints/HMAC remain deferred. Do not claim complete Story1.1 or provider readiness.

</frozen-after-approval>

## Implementation Notes

- BMAD Help selects [BD] bmad-build from the current handoff. Step02 read-only investigation reused investigate_entry_view because the session's agent thread capacity is already occupied. Contracts settle this slice; provider storage/retry choices remain outside it. Freeform prerequisite, no epic/sprint tracking change.
- No intent gaps or irreversible effects. Small additive helper in the existing managed lifecycle module and generated test module preserves their ownership inventory. KDG adapter/test additions, proof capsule inclusion, evidence and handoff complete the footprint. Existing preserving installer regenerates managed copies; never hand-edit them.
- Code map: builder templates/application/web/src/auth/lifecycle.ts and scripts/test-auth-lifecycle.mjs own neutral behavior/tests; src/kdg-auth-pattern.ts and scripts/sync-kdg-auth.mjs enforce parity; KDG web/src/auth-entry.ts owns consuming composition; web/src/entry.ts supplies exact current authority and abortable bounded HTTP; web/tests/auth-entry.test.mjs and auth-proof.mjs run compiled owner tests plus actual generated tests and strict TS7. Existing Auth/UI behavior stays protected.
- Design: an immutable route allowlist and safe entry path are owner configuration, never derived from a return URL. Each capture/restore/clear/dispose invalidates older work. One in-memory pending intent is consumed before verification. The owner observer receives the approved path and AbortSignal and returns matching identity only when that specific destination is currently permitted. Its result is not a grant to invoke domain actions. Fixed KDG organization and context validation remain app-owned.
- ATDD outer loop: observe an emitted scaffold acceptance failure and consuming KDG return acceptance failure before implementation. Focused TDD covers route attacks, identity changes, failure and asynchronous races; retain failed frames. Then run generated, owner SDK/browser, builder parity/regression and strict TS7 checks. Record exact commands/results/source custody in new owner evidence.
- Impact decisions: scaffold applicable (neutral helper plus generated tests, same delivery); shared UI no change (selection only); agent context existing parity and owner-boundary guidance sufficient; documentation new evidence plus prepend handoff, preserve historical text; ADR no new decision, implements accepted0032 and existing Story1.1 safety.

- ATDD observed actual emitted RED in proof-kYlt0U and consuming RED in auth-aba3d8be-feb7-42f9-8823-58dbbff621b2 (existing51 still pass); focused RED proof-gVOQOb. Initial empty-log restricted subprocess frames were infrastructure failures and retained separately. Implemented bounded selector, KDG adapter,33 generated/32 owner tests, four additional actual SDK/browser checks. Strict TS7,19 proof checks, builder68, generated installer/preservation proof-KG1Qv8 and full offline application proof-e7xBj4 pass. Review pending. No managed inventory expansion or dependency change.

- Configured Blind Hunter reviewed scoped artifacts and returned six findings (29.952kB, floor6). All six patched; none deferred. Reentrancy RED proof-hmErmp has33 pass/3 fail; adapter pinning RED auth-75a3ecfd-a4bc-412a-8d42-50dac4ba5411 reproduces changed account/token. Final generated36 pass in proof-nITCE4; KDG71 (36 generated +35 owner) and21 compiler/build/SDK/browser checks pass in auth-21747209-fc18-4922-8722-b000ed6aa618. Overlapping full proof-eDb1AP correctly refused builder_source_drift after review edits, retained unchanged; final source-stable full proof recorded in receipt.

## Review Triage Log

- medium / patched: cancellation can synchronously capture newer intent and outer capture overwrites it. Epoch checks after clear preserve the nested newer capture; test reproduced true vs false before correction.
- medium / patched: finally-abort callbacks can invalidate an already evaluated restored return. Cleanup now runs before final validity selection; separate clear/dispose tests reproduced stale restored outcomes and now select safe.
- medium / patched: adapter retains mutable caller session until deferred observation. Snapshot account/bearer synchronously; consuming RED proved altered fields changed request/outcome, final test observes original bearer.
- medium / patched: fixture kept original organization after replacement. Dispose/recreate selector on replacement, verify against current fixture organization; browser proves earlier intent cannot restore.
- medium / patched: failed fixture capture leaves earlier intent. Clear before observing a new capture; browser denial then successful authority cannot replay old intent.
- low / patched: KDG transport deadline lacked direct consuming tests. Stalled headers/body now both assert5ms safe fallback, abort, cancellation and no replay. Small verification correction, no production contract expansion.

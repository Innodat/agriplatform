---
title: 'KDG local entry-route composition'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Connect the existing KDG numeric email entry to an explicitly invoked local/CI React root with configured fixed organization and Auth public inputs. Observe real browser online/offline/history/hash changes. Allow only the current root entry route and its existing skip-link anchor; scrub unexpected query/hash and callback paths before any SDK bootstrap, keep unsupported routes closed, and require explicit return to the start. Invalid org or unavailable storage/config must fail safely before SDK/session work. Create one stable SDK owner outside React rendering after valid route/config/online preflight, reuse existing EmailCodeEntry and fresh KDG API admission, preserve unfinished code entry across connectivity updates, and unmount it immediately on route refusal so late completion cannot reopen it.

Keep browser observation and emitted behavioral tests scaffold-owned; KDG route policy/branding/organization checks remain local. Explicitly mount only in the synthetic harness; do not create a public main/index, activate an environment/provider/template, create accounts/access, or change dependencies including TypeScript7.0.2. Preserve historical evidence, concurrent changes and Docker resources. No Leave/editor, production, real email/account/access, provisioning, deployment/pilot, cleanup or fingerprints/HMAC.

</frozen-after-approval>

## Implementation Notes

- bmad-help selects [BD] Build after157c606be3f040f65c09c0e9a2a9f1bbab750396 template contract. Freeform local/CI prerequisite, not a complete epic story. Existing user authorization explicitly permits concurrent preservation; snapshot /tmp/kdg-entry-route-before.json captures head and tracked hashes. No dirty-tree reset/stash.
- Step02 read-only investigation reused existing architecture AD-1 fixed env org, email-auth client, EmailCodeEntry/entry safe current-access flow. Only root is implemented; callback OAuth is historical optional capability and must not activate. Preserve legitimate #kdg-entry-content skip link.
- Small reversible oneshot, no intent gaps/irreversibles. New imperative mount accepts existing React Root and explicit org/Auth public inputs, optional injected browser/storage/Auth fetch/API request. It owns observer/root disposal and SDK refresh timer shutdown; no ambient Vite environment/default target or new config format. Browser route observer goes into existing neutral lifecycle template and tests (same managed inventory), KDG sync via owner tool. No React side-effectful SDK creation.
- Code map: templates/application/web/src/auth/lifecycle.ts and scripts/test-auth-lifecycle.mjs add neutral observer and emitted acceptance; apps/kdg-capture/web/src/LocalEntryRoute.tsx adds owner mount/CSS/failure presentation. New tests/auth-fixture/local-entry.tsx uses actual SDK with synthetic transport and real browser events; main.tsx dispatches fixture after removing its selector, auth-proof.mjs captures and exercises both old and new journeys, tsconfig.auth.json includes via fixture imports. Existing auth-entry unit suite and all legacy browser checks remain.
- ATDD: first emitted observer failure and missing local-entry mount acceptance, then focused tests for event registration/removal, scrub/refusal, skip anchor, offline stability and exceptions. Browser proves invalid org/no-storage, callback initial refusal before SDK, mounted success/current denial, reconnect pinned form/cooldown, route cancellation/late SDK result, cleanup/strict replay. Run neutral rendered tests, KDG composed proof, builder regression/strict TS and full offline generation for modified runtime template.
- Impacts: scaffold observer/tests/guidance same delivery and managed sync; shared UI no package promotion (owner branding), existing CSS reused; agent context ownership guidance sufficient; docs/evidence/receipt and prepended handoff; accepted ADRs unchanged, applies0023/0032. No DB/migration or release activation.
- Observed real browser paired popstate/hashchange reopening after initial scrub (auth-bb272f28-332d-4d50-81bd-346fe2ca42dd); focused emitted RED preserved. Fixed paired clean event suppression and separately observed/fixed a second unsafe fragment while already refused. Both generated tests and actual Back/Forward/hash browser journey pass; explicit clean Back rechecks. SafePath is pinned against caller mutation after a separate focused RED.
- Review enlarged the harness proof within the planned slice: lazy fixture dispatcher selects before any SDK construction, previous legacy journey moved to legacy-entry.tsx under all existing tests; explicit email selector beats sessionStorage fallback. Cold-offline navigator input is injected before mount; in-session connectivity uses actual browser offline/online. Invalid URL/key checked through owner mount. Held loopback context and direct pending-verification disposal proved; actual SDK public refresh methods instrumented for requested stop/start/stop order, no timer cancellation claim. Final error assertions follow the last selected ready UI.
- Final verification:98 emitted +48 owner tests =146 all pass,58 composed compiler/SDK/React/browser checks, builder68, strict builder TypeScript and managed parity pass. Fresh offline full generation proof-XxXL0y passes, bootstrap_only=true/generation_ready=false. Neutral rendered proof-h64kLg passes98. Composed auth-7c6d9210-3066-45e0-9ef1-7b6751557fb8 source unchanged/server stopped. Exact source/log/command bindings in docs/evidence/local-entry-route-20261023.json.
- Blind Hunter only, no other layers configured. Follow-up static review confirms all eight findings resolved, no residual concrete findings; reviewer did not rerun tests. No deferrals. Root dependencies/vendor profiles/native config untouched; prior handoff remains verbatim after prepend.

## Review Triage Log

1. medium — patch: old fixture main initialized a legacy SDK before selector/scrub, weakening zero-bootstrap proof. Lazy main dispatch plus legacy-entry module split retains characterized prior journey without creating its SDK in local/email modes. Final preflight cases all have zero SDK/storage/API work except deliberate storage-failure probe.
2. medium — patch: sessionStorage reload fallback overrode explicit email selection. Explicit selectors now take precedence and email clears local fallback; final browser checks emailFixture present/localEntryFixture absent.
3. medium — patch: no initial-offline coverage. Synthetic navigator observation set before mount proves zero reads/writes/Auth/API until reconnect. This is browser-input logic, not an installed offline PWA delivery claim.
4. medium — patch: public URL/key failure not exercised through mount. Both cases now show safe failure before storage or Auth I/O.
5. medium — patch: route refusal lacked pending admission proof. Actual held loopback response released after refusal cannot render admission or add context requests; explicit new start rechecks.
6. medium — patch: disposal was exercised only after refusal. Direct disposal while SDK verification held proves empty root, detached listeners and zero later context requests despite SDK completion.
7. medium — patch: refresh start/stop requests lacked evidence. Actual SDK public prototype instrumentation proves requested stop/start/stop order across rapid connectivity/disposal; completion/timer cancellation not claimed.
8. medium — patch: paired-event unit proof lacked real traversal. Browser Back emits popstate/hashchange, keeps refusal without API work, then clean Back rechecks. Subsequent unsafe fragments also scrub without reopening. All final journey errors accounted.

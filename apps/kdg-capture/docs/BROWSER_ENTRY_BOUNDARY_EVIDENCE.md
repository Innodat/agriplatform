# KDG browser current-entry boundary — 2026-10-22

The bounded slice is complete:29 focused tests, strict TypeScript7.0.2 and all seven
synthetic Chromium checks pass after Blind Hunter review. Durable custody is recorded
in [the evidence receipt](evidence/browser-entry-boundary-20261022.json).
bmad-help selected [BD] bmad-build for the next small Story1.1 browser prerequisite.
Browser entry means sign-in/current-access/landing states, not an editor. This increment
implements only the typed current-context client and session-generation boundary,
not the complete sign-in screen or provider callback. No product UI is shipped.

Generated contracts remain authoritative; existing API/Access/Identity and historical
native proofs are unchanged. Legacy scaffold AuthContext lacks current-entry/bearer
and late-session protection, so it is not copied as a purported qualified Auth flow.
The new code consumes a current session supplied by the future Auth owner integration.
No live Auth, real accounts/access, grants, provisioning, Docker, domain persistence,
Leave/editor, deployment/pilot or cleanup occurs. Fingerprints/HMAC remain deferred.

## Behavioral acceptance and focused TDD

A conservative owner seed initially stayed signed_out. Before implementation, the
actual account-change boundary acceptance expected checking and failed with signed_out:
**1 failed**. This is a behavior failure, not an import-only witness. Initial sandbox
Node test execution returned a generic subprocess failure; the confirming normal
outside-sandbox run produced the intended assertion, retained in D/behavioral-red-confirmed.log.
Focused tests then failed22 before the new getCurrentContext implementation. Most
focused failures were absent-helper TypeErrors; only the outer behavior is claimed
as an observed behavioral RED. The captured focused-red output is truncated and is
not claimed as a full raw execution log. After implementation22 tests passed; adding
newline wire edge cases already passed24 without any production correction.

D: platform/deployment/.local/kdg-browser-entry-20261022.
N: absolute platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node.
All commands use selected tools from repository root:

- `N --test apps/kdg-capture/web/tests/entry.test.mjs`: focused session/account/abort/typed error/shape/deadline coverage; final reviewed count follows below.
- `N node_modules/typescript/bin/tsc --project apps/kdg-capture/web/tsconfig.json`: strict TS7.0.2, exit0; no package or lock change.
- `N apps/kdg-capture/web/tests/browser-proof.mjs`: actual Chromium with retained Playwright1.64.0 and explicit retained Chromium1248 executable. Compiler emits only in an exclusive new proof directory.

## Browser proof and limits

Synthetic DOM/Auth sessions call the actual emitted client with native Chromium fetch
against a synthetic own-API HTTP fixture. Seven checks cover authorized entry, logout
blocking late completion, a replacement account, denial vs outage, bounded native
request and no local/session storage. Unit tests additionally prove generation guards
when the transport ignores cancellation, including same-account recheck/late denial.
No raw error text, token or service key appears in returned state. No browser cache or
storage authority is created. Header/body tests share one deadline. Every API request
uses exactly the selector-free /api/v1/context path and no browser service credential.

The initial browser proof reached all checks but falsely expected no console errors
when intentional403/503 HTTP responses were exercised. It failed and remains retained
under browser-9dfbd38e-b7c0-41c6-a0e4-d686c6638cb2. The corrected oracle verifies actual
HTTP statuses/path403+503, exactly the corresponding two resource-console events and
no page errors or unexpected console errors. No application result expectation changed.
Later proof retains executed source capsules, emitted JS/tool hashes and stopped-server
receipt. This is neither actual KDG handler/current SQL nor provider/device evidence;
those are independently bounded work and cannot be inferred from a DOM fixture.

## Impacts and remaining work

Scaffold: existing generated Context and own-fetch conventions reused; no generic
pattern promotion. Shared UI: unchanged; test markup is not product UI. Agent context:
root instructions suffice; actual commands in web/README.md. Documentation: this
owner evidence, guide, Build spec and additive handoff. ADR: existing current-access,
API error, safe session recovery/logging/release decisions; accepted bytes unchanged.
No dependency install/lock change or root build/test/CI claim. The actual sign-in page,
provider adapter/renewal, safe return navigation and UI accessibility remain next work;
full Story1.1 and persistence/queue/device/pilot readiness are not claimed.

## Review and final verification

Blind Hunter returned six findings, all patched: reject Python-incompatible year0000;
cancel a body whose headers arrive after cancellation; clear the completed controller
before publishing so a reentrant callback retains its replacement controller; expose
nested scopes as readonly types; cover in-flight disposal/external body cancellation;
and cover nested extra/missing fields and malformed UTF-8. Three new regressions
failed before correction (26 passed/3 failed, review-red.log); after correction29 pass
(review-green.log). The added cancellation/schema coverage also passes. The strict
compiler checks both nested mutation prohibitions using @ts-expect-error assertions.
The reviewer's preliminary final-newline regex suspicion was withdrawn and rejected:
the selected Node runtime and existing actor/member newline tests both reject them.
No review finding is deferred. Product/provider work remains intentionally outside.

Final Chromium proof browser-d8fa3e02-9cbb-45f0-9dcd-d7f5c8fab19c passes seven checks;
its exact source capsules include the type assertions. Earlier failed and passed proof
runs remain intact. The final strict compiler command exits0. The sandbox's generic
Node subprocess failure is retained separately in /tmp/kdg-review-red.log and is not
the behavioral RED evidence; the normal outside-sandbox29-test run supplied that.
All419 protected baseline KDG/API/contracts/Access/builder/dependency files are byte
unchanged; the complete prior handoff remains an exact suffix. Concurrent changes
are excluded. No backend/native SQL proof was rerun or newly claimed for this slice.

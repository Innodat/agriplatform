---
title: Standalone Scribeswell account entry
type: feature
created: 2026-10-22
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 7afa7f773789e7529c4891d09e5bb59797c84b13
context:
  - AGENTS.md
  - _bmad-output/specs/spec-scribeswell-studies/account-access.md
  - apps/scribeswell/docs/SHARED_SESSION.md
---

<frozen-after-approval reason="User authorized the next bounded slice and implementation in the invocation">

## Intent

Implement the standalone account-entry portion of canonical Studies ST-36 (CAP-1/CAP-9). An anonymous reader must be able to choose Create account independently of a study, or use existing Sign in, while retaining public reading. Canonical Studies requirements remain the product truth; this item records delivery scope and consumer integration details.

## Boundaries & Constraints

Always use the existing Supabase Auth project/client and `pts-auth` session key. Registration is an explicit email/password Auth request. Confirmation and session evidence belong to the provider. Public reading remains available during pending confirmation, cancellation and service failure. Preserve the existing session initialization/event race protection. Keep authentication errors safe and code-based; never display provider exception messages or log credentials/callback payloads.

Never implement Access enrollment/checks, actor preparation, app-factory tooling, study records, invitations, or private persistence. Do not change generated files, provider settings, deployment profiles, accepted ADRs or other sessions' changes. Public signup is disabled in current owner configuration; live signup activation and complete ST-36 acceptance remain gated on owner-enabled signup, required confirmation, allowed reader return URLs and real mail/callback qualification. This is consumer implementation with fixture-backed evidence, not live registration delivery.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
| --- | --- | --- | --- |
| Entry/cancel | Anonymous public reader, no study | Header Sign in and Create account open the same accessible dialog in the chosen mode; switch modes without submitting; cancellation retains public passage and analysis; fresh entry clears secrets | Escape/Close restores trigger focus; trap modal focus; short/mobile viewport scrolls |
| Confirmation pending | Signup succeeds with no session, including provider-obfuscated existing account | Clear password; show neutral check-email guidance without claiming account creation, verification or mail delivery; offer Sign in/Continue reading | No automatic repeat or enrollment; resubmission only explicit |
| Session returned | Provider returns authenticated session, or valid signup callback | Existing shared session updates; public reading remains at its passage | Session is not Studies authority; no protected side effects |
| Provider failures | Disabled signup, weak password, invalid email, rate limit, unconfirmed login, invalid credentials, unknown/provider-network failure | Safe actionable inline message; input remains editable and submit settles | Match typed codes, never English messages; thrown errors caught; explicit retry only |
| Public return | Root or nested reader, existing public book/chapter/verse and comparison query | Construct fixed same-origin app-root redirect with only validated public passage keys | Drop duplicates/malformed/oversize and all arbitrary return/private/credential fields; ignore incoming redirect targets/hash |
| Bad verification link | Error callback with expired/invalid provider error metadata | Safe dismissible notice with Sign in; public reading and any valid existing session remain usable | Scrub callback error metadata without echo/logging; no external redirect or false success |
| In-flight cancellation | Close/reopen or mode changes during signup/sign-in | One request per submit; late dialog outcome cannot overwrite a new form or show stale errors | No automatic retries; cancellation makes no rollback promise |

</frozen-after-approval>

## Code Map

- `apps/scribeswell/web/src/lib/supabase.ts`: Auth-only SDK, existing shared storage key; add bounded provider fetch and safe pre-initialization callback-error handling if needed.
- `apps/scribeswell/web/src/context/AuthContext.tsx`: current race-safe session subscription; add typed signup outcome and safe sign-in adapter without replacing session ownership.
- `apps/scribeswell/web/src/components/auth/SignInDialog.tsx`: existing password form; extend modes, pending confirmation and focus management.
- `apps/scribeswell/web/src/components/layout/Topbar.tsx`: independent auth entry, cross-tab automatic dialog closure; preserve sign-out behavior.
- `apps/scribeswell/web/tests/reader.spec.cjs`: existing public reader fixtures/geometry; preserve these expectations.
- `apps/scribeswell/web/tests/session.integration.cjs`: existing shared-origin provider fixtures and account-switch coverage.
- `apps/pts/web/src/auth.ts`: reference for safe code-based messages and bounded fetch only; do not import another app implementation.
- `supabase/config.toml`, `platform/deployment/dev.py`: owner configuration disables signup; read-only activation evidence.

## Tasks & Acceptance

**Execution:**
- [x] Add focused browser acceptance coverage in `apps/scribeswell/web/tests/account-entry.spec.cjs`; run the smallest new case and observe missing Create account before implementation. Characterize existing sign-in/public reader first.
- [x] Implement the auth consumer contract in the files above, adding an app-local `src/lib/account-entry.ts` for safe public return/error helpers as needed. Use a 15-second network bound, no automatic application retries, and no new dependency.
- [x] Verify all matrix rows, including nested return and shared-session behavior; run affected browser suites and frontend build.
- [x] Record exact red/green commands and requirement-to-test traceability in this item's Verification. Update app docs and canonical memlog with consumer-delivered versus owner-gated status. Preserve all pre-existing edits.

**Acceptance Criteria:**
- Given an anonymous reader, when standalone signup is submitted to the fixture-backed Auth owner contract, then confirmation/session/failure outcomes follow the matrix without any Studies, Access, membership or grant write.
- Given the existing shared reader session, when login/logout or account replacement occurs in either app, then existing session isolation and public reading tests continue to pass.
- Given disabled live provider signup, when delivery evidence is recorded, then it explicitly retains the activation gate and does not claim full ST-36, D-1 or Studies completion.

## Implementation Notes

The user explicitly authorized preserving the dirty working tree and implementing the next bounded slice. No worktree cleanup, deployment or provider mutation is authorized or needed. Review uses a task-specific diff without staging; any workflow-required local commit must exclude pre-existing dirty/untracked work. Scaffold: no generator change; app-factory owner session remains independent. Shared UI: assess dialog/focus patterns but do not promote an unproven auth abstraction. Agent context: no new root rule. Documentation: canonical log plus app delivery record. ADR: existing authentication/session/ownership decisions apply unchanged. No schema change or migration.

## Verification

Test-first evidence reported during implementation:

- Characterization: `npm run test:browser --workspace=apps/scribeswell/web -- --project=desktop -g 'shared launcher works'` — 1 passed (5.3s).
- Acceptance red: `npm run test:browser --workspace=apps/scribeswell/web -- --project=desktop account-entry.spec.cjs` — existing sign-in/cancellation/public-analysis case passed, standalone Create account failed because the header control was absent (1 passed, 1 failed; 7.4s).

Intermediate qualification:

- Expanded focused run: 9 passed / 7 failed (44.7s). A real confirmation-to-sign-in focus defect was fixed. Six typed-error fixture failures were corrected by matching the provider API-version header and exposing it through CORS; expectations were retained.
- Deadline test initially failed because its synthetic fetch did not retain its AbortSignal. Retaining the signal, as native fetch does, made the unchanged 15-second expectation pass: `npm run test:browser --workspace=apps/scribeswell/web -- --project=desktop -g 'fifteen second'` — 1 passed (17.4s), one request, about 15.9s to settle.
- `node_modules/.bin/playwright test --config apps/scribeswell/web/playwright.session.config.cjs` — 12 passed (1.6m), including new nested signup/session coverage. A final serial rerun follows below.
- Broad `npm run test:browser --workspace=apps/scribeswell/web` was interrupted to stop resource contention with the simultaneous session suite: 43 passed, 3 failed, 6 interrupted, 84 not run. Failures were existing reader analysis-cancel and desktop/mobile lexicon root-highlight timing failures. This is not a passed full-suite result.
- Serial `npm run test:browser --workspace=apps/scribeswell/web -- --workers=1 account-entry.spec.cjs reader.spec.cjs` — 85 passed / 1 failed (3.5m). All 46 reader checks passed. The new desktop Close/reopen case exposed Escape being missed after disabled Submit moved focus to body; a mounted fallback handler fixed it. Mobile subsequently passed the fixed case.
- Final changed-path `npm run test:browser --workspace=apps/scribeswell/web -- --workers=1 account-entry.spec.cjs -g 'closing and reopening|transport exception|confirmation pending|return helper'` — 8 passed (13.0s), including the fixed desktop case and sensitive diagnostic rejection.
- `npm run test:browser --workspace=apps/scribeswell/web -- --workers=1 lexicon.spec.cjs -g 'root highlights'` — 2 passed (13.1s), settling the two implicated lexicon failures. The unaffected remainder of the broad suite was not rerun.

Matrix traceability in `account-entry.spec.cjs`:

| Matrix row | Actual test coverage |
| --- | --- |
| Entry/cancel | existing sign-in and cancellation preserve public analysis; standalone Create account is available without a study; focus trap and short viewport |
| Confirmation pending | confirmation pending is neutral, explicit and keeps only validated public return fields |
| Session returned | session signup updates shared storage without protected requests; valid provider signup callback; nested standalone registration in session.integration.cjs |
| Provider failures | signup maps safe typed error (five variants); sign-in maps safe typed error (two variants); explicit second submission and caught thrown failure |
| Public return | confirmation-pending request redirect assertion; return helper drops duplicate malformed and oversized fields; nested shared-origin return |
| Bad verification link | invalid callback preserves existing session and scrubs metadata; signed-out callback action qualification recorded below |
| In-flight cancellation | cancel and mode switch discard late outcomes; closing and reopening during signup ignores late errors and secrets |
| Diagnostic safety/deadline | transport exception diagnostics and inline error exclude sensitive messages; fifteen second network bound without automatic retry |

Visual inspection: `/tmp/scribeswell-account-entry.png` and `/tmp/scribeswell-account-confirmation.png`, 320×375. Scroll-contained form and reachable confirmation actions; no horizontal overflow. This is Chromium viewport evidence, not physical-phone or screen-reader qualification.

Pre-review serial verification:

- `node_modules/.bin/playwright test --config apps/scribeswell/web/playwright.session.config.cjs --workers=1` — 12 passed (21.6s), final source.
- `npm run test:browser --workspace=apps/scribeswell/web -- --workers=1 account-entry.spec.cjs -g 'signed-out invalid callback'` — 2 passed (2.7s). Covers safe notice, Sign in action, Escape/focus and public reading while signed out.
- `npm run build --workspace=apps/scribeswell/web` — passed; existing bundle >500kB warning remains.
- `git diff --check -- apps/scribeswell/web` — passed.
- Canonical documentation check — passed: 19 companion paths, 11 unique CAPs, 38 unique STs, 14 resolving changed-document links. No schema changes; database composition/migration tests are not applicable or claimed.

All matrix rows are covered by tests actually run and passed, including exact reruns of the fixed case; the interrupted full-suite run remains explicitly incomplete. Before review patches, the account file had 21 cases per viewport. Independent BMAD reviews completed; verified findings fixed and scoped regressions passed (see triage below). Browser mocks prove the consumer contract only; real provider email/verification, protected return context and Studies authority remain unqualified.


## Review Triage Log

All three configured BMAD review layers completed against the task-only diff; no unrelated pre-existing changes were submitted. Each finding is classified separately before grouping.

| Finding | Verdict and evidence | Route |
| --- | --- | --- |
| Blind B1: malformed/rejected callback lacks notice/scrub | medium — installed SDK `_getSessionFromURL` returns errors before clearing the hash; existing helper only recognizes explicit error keys. Invalid-link recovery is already required. | patch, grouped callback handling |
| Blind B2: incomplete callback-parameter scrub | medium — query deletion omits provider_token, provider_refresh_token and expires_at, leaving supported credential metadata in mixed error URLs. | patch, grouped callback handling |
| Blind B3: header remains outside modal isolation | medium — AppShell contains header plus main; only main is inert. Header account/launcher controls remain exposed to assistive navigation. | patch, grouped modal isolation |
| Blind B4: narrow header with launcher may overflow | false — the new 320px populated-launcher reproduction passed before implementation changes; no overflow/occlusion was demonstrated. The test is retained, with stronger geometry assertions. | rejected; no speculative layout change |
| Blind B5: older-browser AbortSignal API support | maybe-false, potential low — API absence would break auth, but no supported failing browser/version was identified. Existing PtS uses the same APIs and current Chromium qualification supports them. A fallback would add branches without demonstrated supported-browser failure. | rejected as unverified low impact; native-device/browser-version qualification remains open |
| Blind B6: successful late-auth outcome lacks coverage | medium — delayed tests release errors only; provider-session completion after cancellation is unqualified. Cancellation never promises reversal of accepted Auth work. | patch, tests for existing session semantics |
| Blind B7: pending work has no accessible busy/status | medium — button text changes but form has no busy state/live progress outside the disabled control. | patch, accessible status |
| Edge E1: malformed/rejected tokens persist without notice | medium — same independently traced SDK early-error path as B1. | patch, grouped callback handling |
| Verification V1: reader inert restoration untested | medium — removing the main.inert assignment would leave existing tests green; current focus-wrap checks never assert background isolation or restored word interaction. | patch, grouped modal isolation |

No new product decision, provider or protected API surface is needed. Fixes complete the existing invalid-link/accessibility/cancellation contract. No finding authorizes signup activation or Access/app-factory work.


Review-patch red: `npm run test:browser --workspace=apps/scribeswell/web -- --workers=1 --project=desktop account-entry.spec.cjs -g 'callback recovery|modal isolates|populated launcher|held account|late successful'` — 5 failed / 3 passed (32.5s). Incomplete, rejected and mixed callbacks, header isolation and missing busy state failed as reported. Populated-header and successful late-session cases already passed; their coverage is retained without unnecessary production changes.


Review-patch outcome: callback recovery/complete scrubbing, startup-only rejection handling, header/reader inert restoration and busy/live status fixed. Added malformed/rejected/mixed callback, concurrent sign-out, ordinary post-callback rejection, populated-header geometry and late-success coverage. Agent scoped checks passed 18 plus 2; root then ran the complete final account suite:

- `npm run test:browser --workspace=apps/scribeswell/web -- --workers=1 account-entry.spec.cjs` — **62 passed (1.6m)**, 31 cases on desktop and mobile, final source.

The malformed-callback fix does not restore old storage or change ordinary session denial. Tests prove both guards. The suspected 320px header defect did not reproduce; labels wrap readably at 57px without a layout change. All verified review findings are resolved. B5 remains a rejected unverified low-impact compatibility suggestion, not a demonstrated supported-browser failure. Physical-device and owner activation qualification remain open.

Lint was not run: the Scribeswell manifest advertises ESLint but declares no ESLint dependency, and no Scribeswell/root ESLint configuration was found. TypeScript compilation and browser checks are the actual verification surfaces used. No backend code, database contract or schema changed; backend/migration evidence is not claimed.


## Final verification and handoff

Root verified the final patched source sequentially:

- `npm run test:browser --workspace=apps/scribeswell/web -- --workers=1 account-entry.spec.cjs` — **62 passed (1.6m)**.
- `node_modules/.bin/playwright test --config apps/scribeswell/web/playwright.session.config.cjs --workers=1` — **12 passed (19.6s)**.
- `npm run build --workspace=apps/scribeswell/web` — **passed**, Vite 2.21s; existing >500kB bundle warning.
- `git diff --check -- apps/scribeswell/web` — **passed**.
- Final canonical validation — **passed**: 19 companion paths, 11 stable unique CAPs, 38 stable unique STs and 55 existing changed-document local paths.

Three independent review layers completed. All demonstrated defects are fixed and their regression cases passed. No new product choice or accepted ADR change was required. The broader 136-test run remains interrupted/incomplete as recorded above; its implicated failures were resolved by serial reruns, and all 46 reader cases had passed. No root-wide, backend, database, real-provider or physical-device acceptance is implied.

Delivered: app-local standalone Auth consumer and closed consumer contracts. Still gated: provider signup/required confirmation/callback/mail activation, full ST-36 protected return, Access D-1 owner delivery, private storage/source publication, shared notifications and workspace/native-device D-2–D-5 qualification. Consume KDG Access and separate app-factory owner delivery rather than implementing alternatives. Existing dirty/untracked planning and other sessions' work are preserved outside any task-only commit.

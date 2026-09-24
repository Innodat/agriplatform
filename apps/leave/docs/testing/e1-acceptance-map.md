# E1 acceptance and evidence map

**Status:** Planning; no tests implemented or executed  
**Date:** 2026-09-24  
**Scope:** Approved E1 work boundaries; not a complete application requirements inventory

The [feature specification](../features.md), accepted ADRs, architecture spine and
approved UX remain authoritative. Scenario identifiers below identify test coverage,
not replacement functional requirements or approved implementation stories. Numbered
work boundaries refer to the six approved E1 capabilities in
[epics.md](../../../../_bmad-output/planning-artifacts/epics.md#e1-decomposition-discussion--2026-09-23).

## Scenario-to-source mapping

| Scenario | Given / When / Then summary | Authoritative source | E1 boundary; evidence |
| --- | --- | --- | --- |
| E1-AC-01 | Given an authenticated employee with access to organization A, when they select A, start a draft, enter details, observe Saved, close and reopen, then the same draft and acknowledged input return; no entitlement is reserved. | Features §1/7/14; spine AD-1/2/4/8; Leave ADR-0075 | 1–3; browser with real API/database, plus database assertions |
| E1-AC-02 | Given two simultaneous start actions in one employee/organization scope, when both complete, then both identify one active draft and neither overwrites the other start's values; independent scopes remain independent. | Features §7; platform ADR-0034 | 2; API/database concurrency under actual restricted runtime role |
| E1-AC-03 | Given incomplete dates, reversed dates or missing selections, when saved and reopened, then exact acknowledged input remains without invented defaults or zero calculation results. | Features §7 agreement 2026-09-24; Leave EXPERIENCE Apply for leave; platform EXPERIENCE Date inputs | 3; browser round-trip and payload/input-format contract tests |
| E1-AC-04 | Given new typing while an earlier save is pending, when its acknowledgement arrives, then newer input remains, Saved is not overstated, and the next coalesced save uses the acknowledged revision. | Features §7; Leave ADR-0118 | 3; focused UI scheduling tests plus one browser delayed-response scenario |
| E1-AC-05 | Given two tabs editing the same revision, when one commits and the other saves, then the second cannot overwrite it, pauses saving and preserves local input for authorized review. | Features §7; platform ADR-0013; Leave ADR-0118 | 3; two-page browser test and atomic revision database test |
| E1-AC-06 | Given a save commits but its response is lost, when recovery uses the original operation, then one mutation/revision advance exists, the outcome is recognized and no fresh save races the unresolved one. | Platform ADR-0012; Leave ADR-0118; shared recovery contract | 3; real commit followed by controlled response loss; API/database receipt assertions |
| E1-AC-07 | Given uncertainty persists, when the bounded automatic budget ends, then the form retains input, shows truthful unresolved feedback and offers Retry using the same operation; permanent validation/denial/conflict errors do not loop. | Shared API recovery agreement 2026-09-24; feature failure-recovery requirements | 3; controlled transport faults with contract-defined timing; focused UI and browser |
| E1-AC-08 | Given saved, saving or failed input, when Close, Escape or mobile Back is used, then each follows the same safe-close rules; discarding unsaved edits retains the last saved draft. | Features §7; Leave ADR-0075; Leave EXPERIENCE Interaction Primitives | 3; browser parameterized by close action and state, plus focus checks |
| E1-AC-09 | Given edits in A, when switching to B, then save succeeds in A before entering B; on failure Retry/Stay/Discard unsaved changes and switch behave as specified and no A values enter B. | Features §7 switching example; Leave ADR-0068 | 4; two-organization browser test with failed-save branch and API isolation |
| E1-AC-10 | Given a draft, when Discard is cancelled, then it stays editable; when confirmed, then form contents are removed and minimal lifecycle/operation evidence remains. Late saves cannot recreate it. | Features §7 retention agreement; platform ADR-0033 | 5; browser confirm/cancel and database transaction/race assertions |
| E1-AC-11 | Given discarded draft A and later draft B, when an old recorded start for A is retried, then it never returns B as its original outcome or overwrites B. An unseen delayed start must also fail its stale-start guard. | Platform ADR-0033/0034; draft recovery contract | 2/5; API/database concurrency; unseen-start case depends on final guard design |
| E1-AC-12 | Given session expiry while editing, when the same user signs in, then authorized context and supported draft recovery return. A different user, lost access or invalid return target gets safe fallback without previous-user data. | Features session recovery/§7; platform ADR-0032 | 1/6; browser auth recovery and API return/access tests |
| E1-AC-13 | Given an otherwise valid token, when membership/grants are revoked or verification is unavailable, then the next action respectively denies or returns retryable unavailability; an old operation ID grants no outcome access. | Features §1/Permissions; platform ADR-0019/0021 | 1 and every protected capability; real current-access service integration, bounded in-flight ordering tests |
| E1-AC-14 | Given future, ended or rehired employment with explicit access, when opening/editing a retained draft, then agreed preparation/read-only/resumption rules apply. Passing selected leave dates does not discard it. | Features §7 employment/past-date agreements; platform ADR-0042 | 2/3/6; API fixtures plus browser read-only/resume; clock-controlled cases |
| E1-AC-15 | Given organization-scoped users and unrelated draft/operation IDs, when direct API requests bypass the UI, then unauthorized reads/writes/recovery reveal no protected data. Nullable shared assignments do not block a valid draft. | Features Permissions/§2/7; spine AD-2/12; platform ADR-0035/0041 | All; API and pooled-connection/restricted-role database isolation tests |
| E1-AC-16 | Given keyboard, assistive technology, zoom and narrow-screen use, when entering, saving and closing a draft, then fields/status/errors are accessible, focus remains useful and required actions/input are not lost during layout transitions. | Leave EXPERIENCE Accessibility Floor/Responsive & Platform; DESIGN; feature UX requirements | 1–6; browser automation plus human keyboard/screen-reader/reflow checks |
| E1-AC-17 | Given new or legacy error responses, when handled by generated clients/shared UI, then numeric-code compatibility, known/unknown identifiers and localized message changes preserve correct behavior; sensitive input is absent from errors/logs. | Platform ADR-0023/0031; API recovery contract | Shared E1 enabling work; contract fixtures, adapter tests and safe diagnostic capture |
| E1-AC-18 | Given the reusable E1 scaffold, when generating a disposable sample and exercising its configured service boundaries, then clients/errors/revisions/attribution/migrations have executable verification without importing another owner's server or forcing Leave's draft rules on all apps. | Tracker first-slice gate; platform ADR-0003/0007/0014–0020/0025 | Shared prerequisite attached to first consumer; generator and disposable-app integration evidence |

## Automation boundaries

Use the proposed Playwright Test/TypeScript direction for browser journeys and pytest
for Python API/domain/database/service-contract tests. Use focused UI tests for
deterministic save ordering, input serialization and accessibility interactions where
they provide clearer failure localization. Do not duplicate every permutation through
the browser; security and concurrent-commit guarantees require lower-level evidence.

The primary browser journey uses real application persistence. Fault injection may
delay/drop transport responses, but a mocked successful save is not evidence of a
committed database write. Verify the actual commit for lost-response cases. Most
browser scenarios can use controlled authentication setup; separately verify actual
Entra/Supabase sign-in, callback and organization access in an isolated integration
environment. Authenticated test fixtures must not bypass application authorization.

Use synthetic users, nonprofit and for-profit organizations, bounded fixture scopes
and cleanup restricted to that run's IDs. Never reuse the old Expense tests' broad
service-role deletion pattern. Keep tokens, notes and sensitive field values out of
shared test artifacts; traces/screenshots must follow the same access/retention rules.

Human UAT evaluates wording, comprehensibility, actual assistive-technology behavior
and usefulness with representative employees. Automated passing results support that
judgment but are not the user's acceptance sign-off or proof of WCAG compliance.

## Readiness and execution records

No runnable Leave test command exists here yet; this document creates none. At story
readiness, settle the wire/persistence/auth contracts, time budgets, input bounds and
formats, browser matrix/environment, and supported migration baseline. Turn each
affected scenario into executable evidence and record the actual test identifier,
command, observed pre-implementation failure and post-implementation result in its
owning delivery item. Use ATDD first, focused TDD where needed, then affected suites.

E3 adds calculation/eligibility preview evidence, E4 adds attachment evidence including
platform ADR-0038 fixed byte identity, and E5 adds submission/revalidation/reservation
and submit-versus-save races. They are not claimed by E1. All other feature/NFR/UX
requirements still need bidirectional global coverage checking before planning closes.

Scaffold/shared-UI evidence is included above; existing agent instructions suffice.
Documentation links this map from the tracker and epics. No ADR changes are needed
for this test decomposition. No application code or test framework was installed.

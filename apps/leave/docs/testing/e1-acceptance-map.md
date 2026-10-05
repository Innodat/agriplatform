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
| E1-AC-07 | Given uncertainty persists, when the bounded automatic budget ends, then the form retains input, shows inline Changes not saved with Retry under ADR-0050 using safe original-operation recovery; permanent validation/denial/conflict errors do not loop. | Shared API recovery agreement 2026-09-24; feature failure-recovery requirements | 3; controlled transport faults with contract-defined timing; focused UI and browser |
| E1-AC-08 | Given saved, saving or failed input, when Close, Escape or mobile Back is used, then each follows platform ADR-0050 exit-only Stay / Close anyway feedback; Close anyway preserves the draft without promising rollback of an in-flight save. | Features §7; platform ADR-0050; Leave ADR-0123; Leave EXPERIENCE Interaction Primitives | 3; browser parameterized by close action and state, plus focus checks |
| E1-AC-09 | Given edits in A, when switching to B, then save succeeds in A before entering B; on failure the exit offers Stay / Switch anyway and the retained form offers inline Retry and no A values enter B. | Features §7 switching example; Leave ADR-0068 | 4; two-organization browser test with failed-save branch and API isolation |
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


## Consolidated E1 contract refinements — 2026-10-02

This consolidates discussion additions to the original 18 scenario groups. No tests
were implemented or run. Owning specifications/ADRs/contracts remain authoritative.

| Scenarios | Additional required evidence |
| --- | --- |
| E1-AC-01/12/13/15/17/18 | [Shared identity/access contract](../../../../platform/docs/architecture/contracts/identity-access-employment-e1.md): distinct account/person/actor, accountless people, explicit verified linking without combined grants, bigint decimal strings, v1/v2 compatibility and independent service/user credentials. Current grant/membership checks under restricted roles. |
| E1-AC-13/14/15/17 | Shared employment discovery/effective variants: authorized absence versus outage, no-period setup versus ended employment, future/rehire gaps, inclusive dates/nonoverlap, null optional assignments, work timezone and midnight/settings races. No automatic employee creation. |
| E1-AC-02/06/10/13/14/15 | ADR-0044 bounded draft-only employment observation: before-check/after-check/deadline/commit-uncertainty permutations. New/restarted execution rechecks; local revision/lifecycle remains guarded. No extension to consequential submission. |
| E1-AC-03/04/16/17 | [Draft input v1](../architecture/contracts/e1-draft-persistence-and-recovery.md): exact raw text/format/mode preservation, no silent defaults/truncation, 4,000/4,001-code-point notes, duplicate/unknown keys, malformed Unicode, byte/field bounds, typed date/decimal grammar and non-executable rendering. |
| E1-AC-02/06/10/11/15/17 | Local composite keys, active uniqueness, lifecycle constraints, immutable compact outcomes and restricted RLS: concurrent start/save/discard, pool reuse, missing/cross-org context, rollback and old-start guards. SHA-256/JCS canonical command reordered-key versus changed-text fixtures, restart/restore, unsupported versions. No fingerprint keyring in E1. |
| E1-AC-03/04/06/07/10/11/14/17 | Typed mutation acknowledgements: original outcome after later closure, stale acknowledgement with newer typing, decimal counters, setup reasons, safe 413/422 mapping. Full deadlines and bounded uncertainty cycle include cancellation after possible commit. |
| E1-AC-01/03/05/09/10/12/13/14/15/17 | Context/read variants: coherent scope/summary and input/revision snapshots, no implicit create, read-without-manage, setup versus unavailable, discard between context/open, removal of protected content on account/access change, no overwriting newer local edits. |
| E1-AC-01/06/09/12/13/15/17/18 | [Audit/context contract](../../../../platform/docs/architecture/contracts/e1-security-audit-ownership.md): selection deduplication, late response after Stay, independent tabs, saved-source preservation after failed target selection, mandatory local evidence failure and nonblocking remote diagnostic export. |
| E1-AC-01/03/10/15/17 | Agreed draft evidence simplification: attribution fields on draft; compact operation outcomes; minimal discard evidence. No duplicate creation/autosave audit or ordinary own-draft read event. No full form snapshots in technical evidence. |
| E1-AC-10/11 | Retain compact closed rows, clear payload on discard and later E5 submission; no automatic X-day cleanup until retry expiry/reference/audit rules are specified. No restore UI or separate archive database. |
| E1-AC-01/09/13/15/17/18 | [App admission](../../../../platform/docs/architecture/contracts/application-admission-and-discovery.md): global/org enablement plus membership and capability, direct API enforcement, suspend without deleting data, re-enable only still-valid authority, empty versus unavailable discovery. |
| E1-AC-01/12/13/15/16/17/18 | ADR-0047 launcher rule: Scribeswell omitted for anonymous/non-PtS users, included for current PtS access, removed after revocation/current refresh; unavailable/Retry has no public fallback menu links. Independently verify public reader works at scribeswell.com without login or membership. |
| E1-AC-12/13/15/17/18 | Small-cohort identity adoption: synthetic three-account rehearsal, manual mapping/recreation if selected, explicit membership/grants, historical attribution and release recovery. PtS/Scribeswell are read-only; no user-document ownership migration. No production user fixtures. |
| E1-AC-17 | Both legacy numeric-code and FastAPI detail.code error families, safe adapters, known/unknown identifiers and localization-independent handling. Existing PtS tests are characterization inputs, not evidence of a fresh test run. |
| E1-AC-18 | Approved generator/reference/Access/discovery/launcher candidates: verify freshly generated output, not template text alone; real HTTP Access and owned persistence; fixture authority separate from runtime; no PtS permission reuse for the sample. |

[Fingerprint security evolution](../../../../platform/docs/architecture/contracts/operation-fingerprint-security-evolution.md)
logs HMAC as a possible enhancement. Key rotation/lost-key fixtures apply if adopted,
not to the current SHA-256 baseline. Leave's existing pre-pilot security assessment
must disposition candidate-guessing exposure for health-related input and retained
outcomes; consistency tests alone do not demonstrate confidentiality.

## Supported browser policy — approved 2026-10-01

Support current and previous major Chrome, Edge, Firefox and Safari, including Chrome
on Android and Safari on iPhone/iPad. Record actual release/OS versions at qualification;
this is a moving window. Engine emulation does not establish actual released-browser
coverage. Cover the first journey, typed input, auth return, keyboard/focus, zoom and
safe Close/Back. Test database races at their proper layer. Exact executable projects,
binaries/device availability and human assistive-technology checks remain evidence.

## Environment and performance — agreed direction

The [environment contract](./e1-environment-and-dependencies.md) separates isolated
local/CI real-stack journeys, domain/API/database tests, actual Entra verification and
human/device qualification. User approved 500 employees as normal test data and 1,000
as largest-organization qualification, with healthy-network p95 opening/closing within
3 seconds and autosave acknowledgement within 2 seconds after dispatch. Twenty active
editors and retained-history volume remain explicit test assumptions. Report sample
counts, failures and p50/p95/p99; no benchmark or capacity result is claimed.

Exact pins and bootstrap/fixture commands remain pre-readiness work. Supported auth
return and server-saved draft reload replace the custom per-tab record/TTL. Callback
account safety and delayed-save ordering still need evidence. Candidate story boundaries are
not complete implementation authorization; global FR/NFR/UX coverage and BMAD SP
remain open. Local schema/audit/permission and generated-sample evidence accompanies
each first consuming delivery item, under the existing ATDD/TDD rules.


## Consolidated story ownership — 2026-10-04

The user approved the original 18-candidate dependency sequence and, on 2026-10-05,
the ID and D2 splits producing 20 ordered candidates. The matrix covers every existing
E1-ENTRY-01–12 and E1-DRAFT-01–20 inventory entry and every E1-AC-01–18 scenario group.
These are scoped planning references from
[epics.md](../../../../_bmad-output/planning-artifacts/epics.md#e1-entry-requirement-traceability--2026-10-02),
not a claim that all global feature/NFR/UX requirements have been extracted or tested.
Several owners contribute different evidence to one scenario. Each first consumer
promotes proven scaffolding/shared UI and records agent/docs/ADR impacts; no duplicate
cross-application runtime implementation is intended.

| Candidate in delivery order | Entry requirements | Draft requirements | Scenario groups | Owning evidence |
| --- | --- | --- | --- | --- |
| E1-ENV | E1-ENTRY-12 | E1-DRAFT-19, E1-DRAFT-20 | E1-AC-15, E1-AC-18 | Isolated bootstrap, credential separation, pins/commands and CI cleanup |
| E1-P1 | E1-ENTRY-06, E1-ENTRY-12 | E1-DRAFT-20 | E1-AC-18 | Fresh generated output, no overwrite, own migration layout |
| E1-SERVICE | E1-ENTRY-06, E1-ENTRY-12 | E1-DRAFT-20 | E1-AC-15, E1-AC-17, E1-AC-18 | Independent service output and preservation of custom extensions |
| E1-ID-A | E1-ENTRY-01, E1-ENTRY-02, E1-ENTRY-07, E1-ENTRY-10 | E1-DRAFT-16 | E1-AC-12, E1-AC-13, E1-AC-15, E1-AC-17, E1-AC-18 | Owned legacy baseline, restricted roles, clean/adopt and failure recovery; contributes foundational evidence to inherited parent mappings |
| E1-ID-B | E1-ENTRY-01, E1-ENTRY-02, E1-ENTRY-07, E1-ENTRY-10 | E1-DRAFT-16 | E1-AC-12, E1-AC-13, E1-AC-15, E1-AC-17, E1-AC-18 | Account/person/actor linking, manual adoption and attribution preservation |
| E1-ACCESS | E1-ENTRY-02, E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-07, E1-ENTRY-10 | E1-DRAFT-17 | E1-AC-13, E1-AC-15, E1-AC-17, E1-AC-18 | Current service/user authority and compatible grants |
| E1-DISCOVERY | E1-ENTRY-03, E1-ENTRY-05, E1-ENTRY-06 | E1-DRAFT-13 | E1-AC-01, E1-AC-09, E1-AC-13, E1-AC-15, E1-AC-17, E1-AC-18 | Scoped pagination, admission and empty/unavailable distinctions |
| E1-LAUNCHER | E1-ENTRY-03, E1-ENTRY-05, E1-ENTRY-11, E1-ENTRY-12 | — | E1-AC-13, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | ADR-0047 visibility and usable failure/Retry state |
| E1-WRITE | E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-10, E1-ENTRY-12 | E1-DRAFT-20 | E1-AC-15, E1-AC-17, E1-AC-18 | Atomic sample write/outcome, attribution and retry evidence |
| E1-REF | E1-ENTRY-01, E1-ENTRY-02, E1-ENTRY-03, E1-ENTRY-04, E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-20 | E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Generated real-stack browser reference; not Leave behavior evidence |
| E1-PEOPLE | E1-ENTRY-06, E1-ENTRY-07, E1-ENTRY-08 | E1-DRAFT-04, E1-DRAFT-17 | E1-AC-13, E1-AC-14, E1-AC-15, E1-AC-17, E1-AC-18 | Shared relationship/period read and null optional assignments |
| E1-A1 | E1-ENTRY-01, E1-ENTRY-02, E1-ENTRY-03, E1-ENTRY-04, E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-07, E1-ENTRY-09, E1-ENTRY-10, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-16, E1-DRAFT-18, E1-DRAFT-20 | E1-AC-01, E1-AC-09, E1-AC-12, E1-AC-13, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Real Entra entry, context selection and protected shell |
| E1-CONTEXT | E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-07, E1-ENTRY-08, E1-ENTRY-11 | E1-DRAFT-04, E1-DRAFT-17 | E1-AC-13, E1-AC-14, E1-AC-15, E1-AC-17, E1-AC-18 | Owned timezone, effective date and eligibility states |
| E1-CHOICES | E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-06, E1-DRAFT-07, E1-DRAFT-18, E1-DRAFT-20 | E1-AC-03, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Permitted modes, initial defaults and later/restored input preservation |
| E1-D1 | E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-07, E1-ENTRY-08, E1-ENTRY-10, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-01, E1-DRAFT-02, E1-DRAFT-03, E1-DRAFT-04, E1-DRAFT-05, E1-DRAFT-15, E1-DRAFT-17, E1-DRAFT-18, E1-DRAFT-19, E1-DRAFT-20 | E1-AC-01, E1-AC-02, E1-AC-06, E1-AC-11, E1-AC-13, E1-AC-14, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Atomic start/resume and coherent draft context |
| E1-D2-A | E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-08, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-02, E1-DRAFT-04, E1-DRAFT-05, E1-DRAFT-06, E1-DRAFT-07, E1-DRAFT-08, E1-DRAFT-09, E1-DRAFT-10, E1-DRAFT-11, E1-DRAFT-12, E1-DRAFT-15, E1-DRAFT-17, E1-DRAFT-18, E1-DRAFT-19, E1-DRAFT-20 | E1-AC-01, E1-AC-03, E1-AC-04, E1-AC-05, E1-AC-06, E1-AC-07, E1-AC-08, E1-AC-12, E1-AC-13, E1-AC-14, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Guarded exact-input save/read API, atomic outcomes, revision/lifecycle and delayed-save races; backend contribution to inherited parent mappings |
| E1-D2-B | E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-08, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-02, E1-DRAFT-04, E1-DRAFT-05, E1-DRAFT-06, E1-DRAFT-07, E1-DRAFT-08, E1-DRAFT-09, E1-DRAFT-10, E1-DRAFT-11, E1-DRAFT-12, E1-DRAFT-15, E1-DRAFT-17, E1-DRAFT-18, E1-DRAFT-19, E1-DRAFT-20 | E1-AC-01, E1-AC-03, E1-AC-04, E1-AC-05, E1-AC-06, E1-AC-07, E1-AC-08, E1-AC-12, E1-AC-13, E1-AC-14, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Integrated browser autosave, truthful status, safe close/reopen, accessibility and measured performance |
| E1-D3 | E1-ENTRY-03, E1-ENTRY-04, E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-09, E1-ENTRY-10, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-10, E1-DRAFT-11, E1-DRAFT-13, E1-DRAFT-16, E1-DRAFT-17, E1-DRAFT-18, E1-DRAFT-19, E1-DRAFT-20 | E1-AC-06, E1-AC-07, E1-AC-09, E1-AC-12, E1-AC-13, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Simple switch exits, target selection and late-response isolation |
| E1-D4 | E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-10, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-03, E1-DRAFT-14, E1-DRAFT-15, E1-DRAFT-17, E1-DRAFT-18, E1-DRAFT-19, E1-DRAFT-20 | E1-AC-02, E1-AC-06, E1-AC-10, E1-AC-11, E1-AC-13, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Compact closed row, payload removal and no resurrection |
| E1-D5 | E1-ENTRY-01, E1-ENTRY-05, E1-ENTRY-06, E1-ENTRY-07, E1-ENTRY-09, E1-ENTRY-11, E1-ENTRY-12 | E1-DRAFT-10, E1-DRAFT-12, E1-DRAFT-16, E1-DRAFT-17, E1-DRAFT-18, E1-DRAFT-19, E1-DRAFT-20 | E1-AC-06, E1-AC-07, E1-AC-12, E1-AC-13, E1-AC-14, E1-AC-15, E1-AC-16, E1-AC-17, E1-AC-18 | Same-account validated return and safe saved-only recovery |

Additional evidence from the latest agreed refinements:

- CHOICES/D2: new configuration initially permits all three supported modes; first type
  choice in a new form defaults to Full days only where permitted. Saved null/explicit
  selections are preserved; later type changes never silently replace a mode. No arbitrary
  fractions. Missing configuration, unavailable reads and retired choices need distinct
  contract fixtures; all configurations remain organization-scoped.
- D2-B/D3: ADR-0050 inline Changes not saved with Retry while editing; exit-only
  Stay / Close anyway, or Stay / Switch anyway for switching. Test both known failure and real commit followed
  by response loss; leaving never deletes the draft or changes another context.
- A1/D5: supported validated return, account mismatch, unsafe/missing targets and
  repeated/late callbacks. Recover current authorized saved state without a custom
  browser record/TTL, raw form contents in URLs or automatic lost-write replay.
  D2/WRITE verify delayed-save ordering; missing context does not prove rollback.
- ENV/P1/SERVICE/WRITE/REF: independently runnable checks at each layer, before downstream
  consumers. Real restricted credentials and owner-controlled setup; regenerated output
  preserves custom extensions. A passing template-text check is insufficient.

Contract closure is tracked in the
[existing delivery tracker](../implementation-plan.md#e1-technical-contract-closure--2026-10-04).
No runtime test ran during this consolidation. Exact executable test IDs/commands are
still delivery evidence, not replaced by this matrix.


### ADR-0122 draft simplicity refinement — 2026-10-04

E1-CONTEXT/CHOICES/D1/D2 and AC-03/14/17 must prove missing/invalid timezone does not
block otherwise authorized preservation; no false eligibility/calculation result is
shown. Clear only definitively obsolete selections with a notice and ordinary guarded
save; preserve independent dates/notes and all values during dependency outage. Earlier
mapping text that requires valid timezone for every draft mutation or retains every
obsolete option is superseded. Current identity/access, confirmed ended-employment and
scope/revision/lifecycle evidence remain binding. Dependent consumer schema and exact
fixtures require reconciliation before implementation; no runtime tests executed here.


Active refinement checks: context and active-draft reads carry nonblocking setup_notices;
a timezone-only defect cannot yield a draft mutation setup rejection or read-only state.
Verify both dated and undated observation evidence without fabricated dates. Resolve
obsolete selections definitively before resetting: a missing paginated-list entry or
failed catalogue read is insufficient. GET leaves stored input unchanged; subsequent
reset autosave is revision-guarded and preserves independent notes/dates. Required
People period-presence integration and exact choice schemas remain technical readiness
inputs. No runtime evidence is claimed by this mapping update.


### Undated setup and selected-choice fixtures — 2026-10-05

People discovery has_periods must reflect the relationship/revision snapshot without
claiming current employment: future-only and ended-only periods both yield true, empty
period setup yields false, and outage is an error. Test both observation evidence variants
without fabricated dates or changes to the stable command fingerprint.

CHOICES/D2 use [definitive selected-type resolution](../architecture/contracts/e1-draft-choice-resolution.md):
selected IDs outside page one still resolve; missing/foreign/retired selections expose
no foreign details; outage/malformed configuration preserves input. Ignore delayed
results after a new selection; read-only views make no reset write. Verify obsolete
type/mode clearing with notice through actual guarded autosave, retained dates/notes and
no refill of defaults. Runtime checks remain unexecuted planning evidence.


Readiness/evidence timing, 2026-10-05: use the
[consolidated existing tracker](../implementation-plan.md#remaining-e1-gates-by-timing--2026-10-05)
for pre-story contracts versus implementation evidence and later-consumer gates.
This map assigns required evidence; it does not claim tests, browser qualification,
performance measurement, clean/adopt rehearsal or generated-slice acceptance have passed.


Owner setup evidence, 2026-10-05: ENV/ID/ACCESS/PEOPLE/WRITE/REF/CHOICES must prove the [controlled provisioning contract](../../../../platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md): target guard, authenticated operator attribution, same/changed/concurrent retry, exact membership/revision binding, local change/evidence atomicity and safe resume after a later owner fails. No production fixtures or extra ordinary draft audit rows.


Saved-draft sign-in return fixtures — updated 2026-10-05: E1-AC-12/13/15/17 follow the
[simplified return contract](../architecture/contracts/e1-draft-persistence-and-recovery.md#saved-draft-sign-in-return--agreed-2026-10-05).
Cover normal renewal, real callback and validated return, different account, revoked access,
missing/malicious destination, unavailable provider and honest saved-only recovery without
automatic mutations. Remove bespoke 30-minute/4 KiB record fixtures. D2/WRITE prove both
commit orders for a delayed save versus reopened editing, revision conflict and no closed
draft resurrection. Callback integration and concurrency evidence remain unexecuted gates.


ENV/P1/SERVICE dependency evidence — 2026-10-05: follow the [owned dependency/command contract](./e1-environment-and-dependencies.md#dependency-ownership-and-command-contract--2026-10-05). Verify clean locked installs without root tooling leakage, stale-lock failure, runtime/dev separation, Access v1 compatibility after dependency separation, and custom-extension survival on regeneration. The real service browser journey, actual Entra check and released-browser/human qualification stay distinct. Planned commands are not executed evidence.


## E1 source and sizing cross-check — 2026-10-05

Scope: compare the existing entry/draft inventory and candidate criteria with features
§1/2/7/14, UX and non-functional sections; spine AD-1/2/3/4/8/12/13 and delivery gates;
tracker Phase 1; current draft, choice, employment, auth-return and environment contracts.
This is planning reconciliation, not a completed full-product requirements inventory,
formal readiness assessment or runtime test result. Source documents remain authoritative.

The existing ownership matrix contains all 12 E1-ENTRY IDs, all 20 E1-DRAFT IDs and all
18 E1-AC groups. ID presence is only an ownership check, not evidence that every source
requirement has been extracted or that an acceptance group has passed.

| Cross-check finding | Disposition / owner |
| --- | --- |
| D2 names prior proven revision/recovery/input-control foundations, but WRITE explicitly proves only create/read and REF has no editor. | Approved D2 split below makes the first mutable save owner explicit. Do not claim arbitrary update/revision support from the earlier sample. |
| ID combines legacy migration ownership/adoption, new person/account/actor behavior and cohort transition. | Approved sequential ID split below; retain all safeguards and synthetic adoption evidence. |
| ENV precedes Identity/Access, yet mentions organization fixtures and restricted-role checks. | ENV uses disposable fixture-owned scope/roles only. Actual identity memberships/grants and admission tests are added by ID/ACCESS; ENV may not require their future schema to pass. |
| Auth recovery matrix still required the removed custom record. | Reconciled active wording to supported return and saved-only recovery; historical discussion notes remain explicitly superseded. |
| UX language behavior is less explicit than generic localized-error handling. | A1/REF shell and D2 preserve shared language preference across organization changes, English fallback and translatable messages. No full Portuguese translation delivery is claimed; locale must not reinterpret stored draft input-format context or change work timezone/access. Trace to EXPERIENCE Voice and Tone, features UX and ADR-0059–0061. |
| Performance and human accessibility can disappear beneath broad scenario groups. | D2 owns measured open/save/close evidence under E1-DRAFT-19; A1/D2 own applicable keyboard/screen-reader/reflow checks under AC-16. Other stories extend evidence for their new surfaces. Existing 500/1,000 fixtures, browser policy and qualification timing remain binding. |
| Phase 1 governance work is not itself a Leave feature story. | Keep BMAD customization and platform-prompts transition as explicit tracker gates. They are not completed merely because the candidate sequence has coverage. |
| E1 must not imply later calculations, files or consequential workflows work. | Minimal My Leave/draft entry only. E2 administration, E3 calculation, E4 content including platform ADR-0038 finalized byte identity, and E5 submission/approval remain later dependent consumers. No fake balances, submission controls or placeholder success. |

### Approved sizing adjustments — 2026-10-05

Keep the approved epic order and relative position of every other candidate. Retain
original IDs as parent traceability references; assign final numeric IDs only after
remaining sizing checks. The user approved these delivery boundaries on 2026-10-05;
this does not authorize implementation or pass readiness.

| Parent | Earlier item | Following item | Traceability |
| --- | --- | --- | --- |
| E1-ID | ID-A: establish the independently owned identity migration baseline and prove clean setup/adoption using existing schema semantics, restricted roles and recovery. | ID-B: add person/account/actor linking and membership lifecycle, owner provisioning/evidence and synthetic small-cohort transition; then ACCESS may consume it. | Preserve all parent ENTRY-01/02/07/10 and AC-12/13/15/17/18 mappings; schema/role evidence belongs to ID-A, identity behavior and transition evidence to ID-B. No production cutover in either acceptance test. |
| E1-D2 | D2-A: save and read exact draft input through the real authorized API, with atomic revision/editability guards, attribution/outcome, bounded shared checks, retries and both delayed-save commit orders. Prove API/database contracts and promote proven backend helpers. | D2-B: wire the real form and autosave scheduling, truthful statuses, conflict/failure presentation, safe Close and reopen; prove browser journey, accessibility and applicable performance, promoting proven UI pieces. | Both retain parent DRAFT-05–12/15–20 and relevant AC groups. D2-A owns AC-03/05/06/13/14/15/17 backend evidence; D2-B owns integrated AC-01/03–08/12–18 where applicable. No parent requirement disappears. |

ID-A must finish and verify its baseline without ID-B's new tables or linking behavior.
D2-A must pass its real API/database acceptance without D2-B's browser. D2-B cannot ship
an unsafe happy path with conflict/recovery deferred to a later item. D1 continues to own
atomic create/resume before D2-A. D3/D4/D5 follow completed D2-B. Closed-state races before
the discard UI exists use controlled owner fixtures, not a dependency on later D4.

The approved splits produce 20 delivery candidates from the existing 18;
no extra epic or feature is introduced. P1/ACCESS/PEOPLE remain sizing watch points,
not certified single-session items. The remaining full source extraction, exact contracts,
compatibility baseline and CE/SP gates are still open.


Matrix interpretation after splitting: ID-A/ID-B and D2-A/D2-B inherit their parent
traceability IDs for continuity. Each row contributes its stated evidence; ID-A does not
claim account linking or browser recovery, and D2-A does not claim a completed browser
journey. The earlier parent story text remains the combined scope reference. Child
criteria replace its delivery boundary as they are agreed; no duplicated implementation.


ID child evidence clarification — 2026-10-05: ID-A acceptance approved; ID-B detail remains for discussion. ID-B independently tests accountless persons, verified linking, service actors, no email merge/grant union, atomic evidence/retries, join/retire/rejoin races and legacy Identity routines with synthetic accounts. ACCESS owns subsequent v1/v2 membership-bound grant checks and intended read-access/replaced-account integration. The release gate blocks activating changed membership behavior before compatible Access/writer evidence; ID-B does not depend on future ACCESS code to pass its own Identity tests.


ID-B approval clarification — 2026-10-05: add explicit old-membership removal retry after
rejoin to ID-B concurrency fixtures. PEOPLE/D1/D2 and later request-history consumers
verify that renewed membership does not replace employment or erase retained drafts/history;
ACCESS verifies fresh explicit grants, with no inherited old grants. Membership retirement
and employment termination remain separate. Three-user rehearsal uses synthetic stand-ins
for the existing PtS accounts. ID-B acceptance approved; no runtime evidence claimed.


D2-A acceptance detail — 2026-10-05: the child story owns backend round-trip and structural-bound fixtures, actual Access/People checks, atomic failure, changed-payload replay rejection, concurrent expected revisions, and delayed-save ordering before/after reopened reads. Test actual commit followed by response loss. Controlled closed-draft fixtures avoid depending on later discard UI; submitted-state integration stays E5. Existing AC-03/05/06/13/14/15/17 mappings remain, with browser/status/close evidence assigned to D2-B. No runtime result is claimed.


D2-B detail — 2026-10-05: D2-A acceptance is approved. D2-B owns focused one-second idle/five-second continuous scheduling tests, newer-input versus stale acknowledgement, actual API commit/response-loss browser recovery, two-tab conflict, Close/Escape/in-app Back and exact saved-input reopen. Parameterize simple failure exits and account/organization response isolation. Real browser/device, keyboard/screen-reader/reflow and agreed workload timings retain their separate qualification evidence. D3/D4/D5 still own complete switch/discard/interactive-return journeys. D2-B criteria await agreement; no test pass is claimed.


Draft failure presentation update — accepted 2026-10-05: platform ADR-0050 partially
supersedes ADR-0048; Leave ADR-0123 adopts it. Use inline Changes not saved with Retry
while editing; no Keep editing button. Prompt Stay / Close anyway only on exit when
bounded saving cannot be confirmed; switching uses Stay / Switch anyway. Confirmed saved
input closes immediately. Existing revision/lifecycle/retry and access protections stay
binding; no rollback or unsent-input survival promise. D2-B/D3 and shared scaffold/UI
fixtures must prove these cases. Earlier three-choice wording is superseded. This does
not decide whether a workflow needs a draft or change accepted draft scope.


Saving convention — 2026-10-05: D2-B verifies Draft saved only for acknowledged input, no Save button and no submission effects, with ADR-0050 inline Retry and exit-only confirmation. E2/E3 administration tests must prove no field writes before explicit Save and Cancel abandoning only uncommitted input. Separate preference tests prove immediate feedback and failure behavior. These are planned requirements, not executed evidence.


## Supplemental source obligations — 2026-10-05

The [E1-X01–22 source coverage](../../../../_bmad-output/planning-artifacts/epics.md#supplemental-source-coverage-permissions-ux-and-operations--2026-10-05)
assigns permissions, UX and operational requirements to first consumers and later epics.
These supplement, rather than renumber, existing ENTRY/DRAFT/AC identifiers.

Concrete E1 additions to evidence ownership: A1/D3 language-preference retention and
English fallback; CHOICES/D2 raw-format versus display tests; P1/REF/A1/D2 rendered token
and layout checks; ENV/SERVICE explicit transport/storage qualification boundaries;
SERVICE/WRITE/REF basic backend trace propagation with nonblocking exporter failure;
ENV/ID-A/REF migration/readiness and restricted-role checks. Existing scenario groups
AC-09/15/16/17/18 carry applicable fixtures. Production encryption, integrated restore,
alert routing and content/worker qualification stay at their owning delivery/release gates;
local synthetic success cannot qualify them. No tests were executed in this source pass.


Business boundary cross-reference — 2026-10-05: [BIZ-01–36](../../../../_bmad-output/planning-artifacts/epics.md#business-feature-and-ux-journey-coverage--2026-10-05)
keeps minimal E1 entry/draft evidence separate from later policy, request, content and
report evidence. E1 draft discard does not implement E5 request withdrawal. E1 must not
claim later business coverage through synthetic choices or a saved draft. This mapping
adds no E1 runtime test pass and does not change the 20-candidate delivery sequence.

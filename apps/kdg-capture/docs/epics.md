---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics, step-03-create-stories]
inputDocuments: [prd.md, DESIGN.md, EXPERIENCE.md, ARCHITECTURE-SPINE.md, contracts.md, discovery.md, testing.md]
status: coverage-validated-readiness-blocked
created: 2026-10-12
updated: 2026-10-14
---

# KDG Capture — BMAD epic planning

Requirements extraction was approved by the user with C. The installed
bmad-create-epics-and-stories step 3 is now in progress; the user approved
the five-epic structure with C. The authoritative
requirements remain in prd.md; this inventory is a delivery index, not a second feature
specification. Do not overwrite global BMAD epics.md, which owns active Leave planning.
The epic structure below is approved. Story candidates remain separate until their
individual review; approved stories are appended to this document in sequence.

## Requirements Inventory

### Functional Requirements

| ID | Extracted behavior |
| --- | --- |
| FR-1 | Platform sign-in, current fixed Khula organization, no switcher |
| FR-2 | Two explicit app roles, ownership, backend/UI authority and editor attribution |
| FR-3 | Controlled initial child/questionnaire/assignment provisioning |
| FR-4 | Mobile installed PWA, exact branding, one form, role-eligible child selection |
| FR-5 | Exact Afrikaans initial questions, required rating, Nee defaults, conditional details |
| FR-6 | Editable separate observation date, multiple same-day captures, local-known prompt |
| FR-7 | Explicit local Save, no unfinished-input recovery; safe failed/uncertain Save |
| FR-8 | Authorized local/server history, original version/author/time and revisions |
| FR-9 | Retained concurrent changes and explicit revision conflict resolution |
| FR-10 | Bounded online editor/types/reorder/retire, whole-form Save/Cancel and Publish |
| FR-11 | Immutable published versions, original historical edits, offline old-version sync |
| FR-12 | Online children/facilitator assignments through verified platform accounts |
| FR-13 | Provisioned local data, account/org isolation, normal offline reopening |
| FR-14 | Transactional create/edit queue, stable identifiers and foreground/manual sync |
| FR-15 | Local/synced/attention status and bounded safe retry |
| FR-16 | Seven-day local authority, current server checks, expiry/revocation handling |
| FR-17 | Logout/account change retains locked unsynced work without leakage |
| FR-18 | Quota/eviction, compatible updates and crash-safe local migrations |

### NonFunctional Requirements

NFR-1: Backend/runtime-role/local isolation and sensitive diagnostic minimization.
NFR-2: Atomic local/server integrity and honest acknowledgement.
NFR-3: Proposed WCAG AA/48px/320px/zoom and physical assistive-technology evidence.
NFR-4: Proposed 1-second local feedback, 30-second foreground cycle, 10-second requests.
NFR-5: Prior-version/queue release compatibility and installed Android/iPhone proof.

### Additional Requirements

AD-1–10 in ARCHITECTURE-SPINE.md bind fixed-org silo, scoped account Access, immutable
JSONB versions, local transactions, ordered commands, conflicts, seven-day local authority,
partition safety, upgrade compatibility and controlled release/promotion. Native IndexedDB
and existing React/Vite/shadcn are the proposed technical seed; there is no working starter
CLI to invoke yet. Existing shared owner work P-ID/P-ACCESS/P-SCAFFOLD/P-ENV/P-SETUP is
not duplicated; P-INVITE and P-DIRECTORY are explicitly conditional dependencies.

### UX Design Requirements

UX-DR1: Inherit/prove neutral shadcn theme with measured text/control/focus contrast.
UX-DR2: Exact names/subtitle and single scrolling mobile form with 48px targets.
UX-DR3: Accessible rating/Ja-Nee radio selection and immediate conditional details.
UX-DR4: Explicit local/synced/attention status and partial offline-history labels.
UX-DR5: Explicit capture Save and whole-form edit Save/Cancel; no observation autosave/resume.
UX-DR6: Actionable Save failures, safe retries and ordinary explicit-form exits; acknowledged save closes.
UX-DR7: Same-user sign-in return, seven-day lock states and pending-work logout choices.
UX-DR8: History/details/revision views and local-only duplicate suggestion.
UX-DR9: Explicit local/base/server conflict comparison; descendants require re-review.
UX-DR10: Online admin form/publish/reorder/retire and eligibility-load states.
UX-DR11: Storage/migration/update failures preserve data, block incompatible writes.
UX-DR12: Screen reader/keyboard/focus/language/320px/zoom/safe-area coverage.
UX-DR13: Eight surface groups each have loading/empty/denied/unavailable/recovery closure.
UX-DR14: Installed Android/iPhone setup, launch/reopen/sync/update proof.

### FR Coverage Map

The PRD remains product authority. Primary epic completes the requirement; earlier
baseline safeguards and later extension evidence are distinguished below.

| FR | Primary completion | Earlier baseline / later extension |
| --- | --- | --- |
| FR-1 | E1 | Fixed Khula/Auth/current checks apply throughout |
| FR-2 | E3 | E1 role/ownership enforcement and administrator create-all; E2 own edit; E3 all-capture administration |
| FR-3 | E1 | Initial controlled domain provisioning, shared owners retain identity/grants |
| FR-4 | E1 | Installed phone interface and exact identity; E5 additional child management |
| FR-5 | E1 | Initial questions/Nee/details; E4 editable definitions/types |
| FR-6 | E2 | E1 editable date/multiple same-day records; E2 completes locally known Edit existing / Add another with actual editing |
| FR-7 | E1 | Explicit local Save without unfinished-entry recovery; E2 whole-form existing edits |
| FR-8 | E3 | E1 local reopening/details; E2 30-day own observation history/edit and internal revision evidence; E3 permitted organization history |
| FR-9 | E2 | Full explicit revision conflict recovery for own edits; E3 adds cross-author administrator scenarios |
| FR-10 | E4 | Online bounded editor/Save/Cancel/Publish |
| FR-11 | E4 | E1 immutable seed/version pinning; E2 original-version editing; E4 actual version update/publishing compatibility |
| FR-12 | E5 | E1 controlled initial child/assignment; E5 responsive online management |
| FR-13 | E1 | E2 own historical downloads; E3 online organization history |
| FR-14 | E2 | E1 create queue, foreground/manual sync/idempotency; E2 ordered edit queue |
| FR-15 | E1 | Local/synced/attention states everywhere |
| FR-16 | E1 | Current server checks/seven-day local window; E5 changed assignment/child scenarios |
| FR-17 | E1 | Logout/account-change/pending-work isolation |
| FR-18 | E5 | E1 quota-safe saving/initial schema/update baseline; E5 full upgrade/migration/retention recovery proofs |

NFR-1 isolation and NFR-2 integrity bind every epic; establish them in E1, do not
postpone them to a hardening stage. NFR-3 accessibility binds every surface introduced.
NFR-4 bounded saves/sync starts in E1 and extends to edits/admin. NFR-5 early installed
phone proof is E1; compatible upgrades/releases remain required for each change, with
full pilot reliability evidence in E5.

| UX items | Delivery ownership |
| --- | --- |
| UX-DR1–7 | E1 baseline; extend consistent controls/session policy in all later surfaces |
| UX-DR8–9 | E2 own observations/edits/conflicts, E3 organization review |
| UX-DR10 | E4 questionnaire forms and E5 child/assignment forms |
| UX-DR11 | E1 safe initial storage/update behavior; E5 full upgrade-recovery evidence |
| UX-DR12–13 | Each epic's introduced surfaces; no deferred accessibility/error closure |
| UX-DR14 | E1 early two-phone proof; repeat affected paths with E2–E5 changes |

Acceptance groups KDG-A01–A22 are in [testing.md](testing.md). Detailed story links
remain pending the next installed step; no story readiness is claimed.

## Epic List — approved

Each epic delivers a usable outcome, builds only on earlier outcomes/shared owner
prerequisites, and does not require a later epic to function. Technical enabling work
is scoped within the consuming epic or referenced to its existing platform owner; it
is not recast as a competing platform delivery lifecycle.

### Epic 1: Record and synchronize the first observation offline

**Outcome:** Louwnique can sign in, enter fixed authorized Khula, provision Sinehgomso
and the initial immutable questionnaire, capture offline, close/reopen and view the
local observation, reconnect and synchronize, then view the server-backed record.

**FRs covered:** FR-1–7, FR-13, FR-15–17; foundational FR-2/8/11/14/18 safeguards.
**Dependency:** Only the coordinated minimum P-ID/P-ACCESS/P-SCAFFOLD/P-ENV/P-SETUP
needed by this consumer. No People, complete Leave plan, full editor, shared launcher
or normal multi-facilitator onboarding prerequisite.

The first vertical slice uses repository-approved owner-local setup, not a questionnaire
editor. It includes explicit local Save, Nee/details behavior, device-date default, repeat
same-day captures, atomic local create queue, fresh server authorization, safe retries,
truthful status and account/org isolation. Administrator create-all is enforced from
this baseline even though the initial organization contains only one active child.
Run the early physical Android/iPhone installed offline proof immediately after this
slice, before substantial history/editor work. Basic session expiry/logout/storage/update
safety cannot wait for E5. Initial history need only prove newly saved local/server records.

### Epic 2: Find and safely edit personal capture history

**Outcome:** Capturers browse their permitted last 30 days offline, fetch older history
online, and edit their own captures using the exact original questionnaire, keeping
original author/time and revision history.

**FRs covered:** FR-8 own scope, FR-9, FR-14 edit queue; extends FR-6/7/11/13/15–18.
**Dependency:** E1 only, including the shared foundations already consumed there.

Complete ordered offline edits, interrupted drainer recovery, base/local/server conflicts
and explicit resolution for the user's own multi-device edits here. No dependency on
E3 for conflict handling. Refresh/download must retain pending overlays. Capturers keep
own historical read/edit after unassignment while current KDG access remains valid.
No assertion that offline history includes records never downloaded.

### Epic 3: Review and correct captures across Khula

**Outcome:** Questionnaire administrators can view/edit all permitted Khula captures,
including facilitator observations after their devices synchronize, while preserving
original ownership and identifying the administrator editor.

**FRs covered:** Completion of FR-2/8 organization administration; strengthens FR-9/13–17.
**Dependency:** E1 and E2; initial version/children/facilitators may still be provisioned
through controlled setup, so this outcome does not require E4 or E5.

Reuse E2's revision comparison/resolution, adding facilitator-versus-administrator
concurrency and role-loss cases. Preserve conflicting branches and pause descendants
for explicit re-review. Own-only users never acquire organization-wide record access;
administrator scope never crosses Khula. Organization-wide history/edit/audit remain online in the portal; the PWA retains
own-only observation history for both application roles.

### Epic 4: Evolve questionnaires without rewriting historical captures

**Outcome:** Louwnique manages small questionnaire drafts, publishes immutable versions,
and changes wording/order/required status/types while old and offline captures continue
using their original definitions.

**FRs covered:** FR-10/11; extends FR-5/8/9 and version-compatible FR-14/18.
**Dependency:** E1–E3; no child/assignment editor required.

Deliver only rating, Ja/Nee, text and optional Ja details. Publication and draft Save/
Cancel follow approved saving conventions. New captures adopt latest downloaded version;
open in-memory entries stay pinned. Historical edits and late old-version sync remain valid.
No generic Survey runtime, branching engine or scoring/analytics expansion.

### Epic 5: Keep daily capture reliable as children and facilitators change

**Outcome:** Administrators manage active children and facilitator assignments online;
users retain their permitted history and pending work through access/assignment changes,
app upgrades and recoverable failures, with pilot-ready operating evidence.

**FRs covered:** FR-12/18; completes changed-assignment/storage/update reliability for
FR-2/8/13–17 and NFR-5.
**Dependency:** E1–E4. Normal additional-facilitator onboarding consumes the existing
Identity invitation/Access administration owners after their own readiness; no parallel
account/grant editor or automatic tenant enrollment is introduced.

Child/facilitator assignments grant no membership or app capabilities. Capturer
unassignment stops new captures but retains own historical editing; administrators
create for all active children. User-approved child deactivation/history policy A-6
preserves historical own editing under current authority. Complete old/new local-schema interruption tests,
compatible queued-work upgrades, quota/cache recovery, operational retention/device
policy and repeated physical-device validation. Already required E1–E4 correctness
is not deferred to this epic.

## Grouping and dependency rationale

Capture and synchronization share core files, so their baseline is one vertical epic,
not frontend/API/database epics. E2 and E3 share history/conflict controls intentionally:
E2 proves own multi-device editing; E3 adds a distinct authority/privacy boundary with
real cross-author edits. Questionnaire editing is a separate content/version risk
boundary. Assignment administration changes eligibility and onboarding boundaries;
its remaining recovery proof completes the pilot rather than supplying missing safety
for earlier epics. These are feedback/risk boundaries, not arbitrary technical layers.

## Story creation checkpoint

Step 1 requirements and step 2 five-epic structure: **approved**. Step 3 proceeds
sequentially by epic; all 19 stories are approved. all five epics and the step-3 final checkpoint are approved. Step-4
coverage/dependency/architecture validation and separate readiness findings follow.

### Final validation checkpoint

All five epics and 19 stories are user-approved. User C closed E5 and confirmed the
step-3 final menu. [Final validation](final-planning-validation.md) checks coverage,
quality, architecture, structure and dependency flow. Load-bearing shared design/owner
and concrete execution contracts remain unresolved; the workflow is not marked ready
for development and no final completion/PASS assertion is made.

Presentation amendment approved 2026-10-14: routine capture/history shows observation
date/answers and compact status, without audit names/timestamps or revision controls.
Earlier references to attribution/revisions in record data remain storage requirements,
not a routine capturer display requirement. Authorized administrator audit is E3.
The editor/device holding a conflicting proposal resolves it under existing own/all
permissions; first access does not grant priority. No central upload/delegation of
never-synchronized conflict proposals is introduced.

## Epic 1: Record and synchronize the first observation offline

Deliver the approved first vertical slice and early installed Android/iPhone proof,
using only the coordinated minimum shared owner dependencies; no full editor or People
integration is required. The approved story below is the first independent increment.

### Story 1.1: Sign in and enter the authorized Khula context

As a Khula capturer or questionnaire administrator,
I want to sign into KDG Capture and enter my currently authorized Khula context,
So that my identity and organization access are established before observation setup.

**Scope and size:** One KDG frontend/API integration boundary, using the existing
generator and shared Auth/Identity/Access contracts. It delivers online entry and a
clear setup-not-completed landing state. It is independently testable before child,
questionnaire, local capture or synchronization delivery. Shared platform implementations
remain their existing owners' prerequisites, not hidden work within this app story.

**Requirements:** FR-1, entry portion of FR-2/4; NFR-1/3 and the applicable NFR-4
request bound. UX-DR1/2/7/12/13; AD-1/2/8/10. This story covers online same-user return
safety; offline lease, pending-work logout and account-partition recovery remain explicit
later E1 coverage, not claims made by this entry increment.

**Acceptance Criteria:**

**AC-1 — Authorized online entry**

**Given** a verified platform account, durable account actor, current Khula membership,
global KDG availability, Khula KDG enablement and the exact KDG entry capability,
**When** that capturer or questionnaire administrator signs in using retained platform Auth,
**Then** KDG resolves the configured Khula organization through its authenticated API,
**And** displays KDG Capture and Khula Development Group with a clear setup-not-completed
landing state when domain provisioning has not yet occurred,
**And** requires neither a People/person/employment record nor organization selection.

**AC-2 — Membership and sign-in alone are insufficient**

**Given** an authenticated account with no current Khula membership, a retired membership,
no exact entry grant, disabled global KDG admission or disabled Khula KDG enablement,
**When** it opens the entry route or calls the context API directly,
**Then** entry is denied through the stable safe API error contract,
**And** no protected organization, child, questionnaire or other account information is returned,
**And** membership or a platform organization role does not substitute for an app capability.

**AC-3 — Fixed organization and trusted identity**

**Given** an account admitted to another organization, or a caller submitting a different
organization/account/actor identifier through URL/query/body/context manipulation,
**When** it attempts KDG entry,
**Then** the backend uses verified bearer identity and the environment-controlled Khula
org_id, rejects unsupported selector fields and denies unauthorized Khula admission,
**And** no organization switcher, alternative-organization fallback or identity creation occurs.

**AC-4 — Current checks and distinct failure states**

**Given** an already signed-in account or stale JWT role claims,
**When** entry authority is checked again after membership/grant/app enablement changes,
**Then** the next protected request observes current shared authority,
**And** confirmed denial is distinct from unavailable Access/Identity verification,
**And** unavailable verification fails closed with Retry rather than cached grants,
an empty successful result or an endless sign-in loop.

**AC-5 — Authentication and return navigation**

**Given** an expired authentication session or a required interactive sign-in,
**When** KDG attempts normal renewal and then supported reauthentication if needed,
**Then** only the same currently authorized account returns to a validated permitted
KDG destination; otherwise it lands safely without prior-user context,
**And** external/malformed return targets are refused,
**And** no credential/form payload enters return URLs or logs and no domain action is
automatically confirmed by completing sign-in.

**AC-6 — Accessible and honest setup state**

**Given** the entry page on a phone or computer,
**When** a user navigates by touch, keyboard or an assistive-technology test fixture,
**Then** sign-in, checking access, denied, unavailable/Retry and authorized setup states
have labeled controls, visible focus, readable status and preserved reading order,
**And** the login displays Khula Development Group and the application uses KDG Capture,
**And** offline first launch explains that online sign-in/setup is required rather than
claiming a ready offline questionnaire or completed provisioning.

**API boundary:** `GET /api/v1/context`, private/no-store, no account/org selector.
The bearer determines account; KDG backend checks the exact registered entry capability
against configured Khula using canonical Access v2 and its restricted service credential.
For the two maintained default roles, propose `kdg_capture.capture.read.own` as the
entry capability; both role definitions explicitly contain it. Entry grants no create,
all-history, edit or administrator power. Final registry/caller binding belongs to Access
contract closure before this story is ready to Build.

Success uses verified account_id, actor_id, positive decimal-string membership_id,
authorization_scope with exact Khula org_id, matching own-account resource_scope,
exact permission, decision_id and UTC checked_at. Verify the returned resource account
equals the authenticated account; absent/mismatched fields do not establish authority. Display organization name is fixed application branding, not evidence of
membership. Missing actor setup returns the owning safe setup/error outcome; no invented
actor fallback. Other action permissions are checked when needed; entry success does
not renew stronger cached capabilities or mint an offline lease. `/provision` remains
a later domain boundary, so this entry increment has no forward dependency on it.

**Dependencies and readiness gates:**

| Existing prerequisite | Concrete evidence required before Build |
| --- | --- |
| Coordination | This session/Leave handoff acknowledges existing Identity/Access/scaffold owners and KDG first-consumer boundaries; no duplicate foundation work |
| P-ENV / P-SCAFFOLD | Isolated target and verified generator/runtime layout, coherent React/Vite/shadcn pins, supported synthetic Auth callback/sign-in, typed error/client conventions |
| P-ID | Current verified account actor/membership projection and owner-controlled fixture setup under ADR-0056; no People requirement |
| P-ACCESS | KDG organization v2 variant, registry/default roles, org/app admission, caller policy and current-check fixtures including denial/unavailability |

No story numbered later in KDG Epic 1 is a prerequisite. Existing shared stories retain
their own readiness and test evidence. KDG entry can be implemented after those specific
dependencies are available, without waiting for all Leave planning.

**ATDD and traceability:**

| Scenario IDs | Acceptance | Intended public boundary |
| --- | --- | --- |
| KDG-A01.entry-allowed | AC-1 | Real KDG browser sign-in/context journey with isolated fixtures |
| KDG-A01.entry-denied | AC-2/4 | KDG API integration consuming shared Access; actual current membership/grants |
| KDG-A14.entry-scope | AC-3 | API selector/wrong-org/cross-account negative tests |
| KDG-A15.entry-return | AC-5 | Browser authentication renewal/return/malicious-target/account-change fixtures |
| KDG-A19.entry-accessible | AC-6 | Component/keyboard/accessibility plus responsive browser checks |

Platform P-AUTH/P-ACTOR/P-ACCESS/P-ERROR/P-SESSION prove their own service boundaries.
They do not replace KDG consumer tests. After implementation approval, bmad-build first
runs KDG-A01.entry-allowed and records its expected missing-behavior failure, then focused
authorization/adapter tests and the affected contract/browser suites. Exact commands
come from the verified generated package; none is invented or executed during planning.
Installed offline Android/iPhone proof belongs to the complete first vertical slice,
not a falsely passing entry-only test.

**Delivery impacts:**

| Area | Decision |
| --- | --- |
| Scaffold | Consume existing owner generator; promote proven fixed-org/current Access consumer/return fixture through that owner if not already delivered; no second generator |
| Shared UI | Consume/prove neutral sign-in/loading/error/focus composition; app branding/Khula policy remains KDG-specific |
| Agent instructions | Record actual KDG commands and fixed-org/account-author rules in app context; root changes require coordinated owner |
| Documentation | Update entry contract, test map and fixture/runbook evidence in this delivery item |
| Contract | KDG context OpenAPI and generated frontend types together; coordinated shared Access variant stays Access-owned |
| ADR | Adopt existing platform Auth/Access/API/scope/return decisions; no superseding ADR needed for this bounded consumer |

**Review checkpoint:** Scope/criteria approved by the user with C. Approval
of this story is planning approval only; applicable readiness and final implementation
review remain required before code, dependencies, migrations or deployment.

### Story 1.2: Provision and retrieve the initial published questionnaire

As an authorized KDG setup operator,
I want to provision Khula's initial immutable questionnaire through a controlled command,
So that authorized facilitators can retrieve its exact published definition before the
questionnaire editor is delivered.

**Scope and size:** One KDG domain increment: initial questionnaire/version persistence,
bounded definition validation, a targeted owner command and an authenticated version-read
API. Reuse already-proven owner-write/operator/migration scaffolding. Create only the
questionnaire/version and command outcome/change-evidence structures needed here;
child, assignment, capture and offline stores belong to their consuming stories.

**Requirements:** FR-3 questionnaire setup, FR-5 exact definition and FR-11 immutable
version identity; FR-1/2 read authority; NFR-1/2/5. AD-2/3/10. Presentation of the capture
form, active answers, conditional toggling and phone persistence remain later consuming
behavior; recording defaults here is not proof that those UI behaviors work.

**Acceptance Criteria:**

**AC-1 — Exact initial definition**

**Given** the explicitly targeted Khula organization, fixed questionnaire/version UUIDs,
four stable question UUIDs, expected absence and verified KDG operator authority,
**When** the initial questionnaire command succeeds,
**Then** it creates one published version with the four exact Afrikaans questions:

| Question | Definition |
| --- | --- |
| Hoe was haar algehele houding vandag? | Required integer rating 1–5, five choices, 1 = Goed, 5 = Nie goed nie; no default rating or invented descriptions for 2–4 |
| Het sy enige uitbarstings/gedragsprobleme gehad? | Required Ja/Nee, default Nee, optional Ja-only Besonderhede |
| Het sy sonder toestemming uit die klas geloop vandag? | Required Ja/Nee, default Nee, optional Ja-only Besonderhede |
| Het sy probeer huis toe hardloop? | Required Ja/Nee, default Nee, optional Ja-only Besonderhede |

**And** question identity is independent of wording/order and version identity is stable,
**And** the definition declares its schema version and contains no executable expression,
clinical interpretation or observation answer.

**AC-2 — Controlled owner and environment boundary**

**Given** a missing/wrong target, unsupported scope, unknown command fields, spoofed
actor, ordinary API credentials or an operator without exact KDG setup authority,
**When** it attempts the command,
**Then** validation/authority checks reject it before domain writes,
**And** it cannot create Auth accounts, memberships, application grants or People records,
**And** this command writes only KDG-owned state using restricted operator authority,
not migration credentials, API startup seeding or a universal cross-owner credential.

**AC-3 — Atomic setup and safe replay**

**Given** a valid operation ID and immutable command input,
**When** the command commits, is retried after a lost response or is attempted concurrently,
**Then** questionnaire/version state, required creation/publication attribution, compact
change evidence and operation receipt commit together at most once,
**And** identical authorized replay returns the recorded outcome without another version/event,
**And** changed input under the same operation ID conflicts,
**And** a fresh command requiring absence refuses an already-existing target rather than
overwriting it; a failed transaction creates no partially published definition.

**AC-4 — Immutable published storage**

**Given** the stored published version,
**When** an ordinary runtime write or another supported writer attempts to change its
definition, question IDs, version identity or publication attribution,
**Then** the published record cannot be mutated through that path,
**And** future changes require a new version rather than rewriting this one,
**And** the original version remains resolvable independently of later publication.

**AC-5 — Current authorized definition retrieval**

**Given** Story 1.1 entry and a caller with current Khula membership, KDG admission and
the exact questionnaire-read entry capability,
**When** it requests this exact version from the KDG API,
**Then** it receives the version/questionnaire IDs, ordered definition and original labels
through the typed private/no-store contract,
**And** cross-organization, unpublished or inaccessible versions disclose no existence,
**And** missing grants/retired membership are denied and unavailable authority fails closed,
**And** no role is inferred from questionnaire visibility or an unverified organization selector.

**AC-6 — Proof and truthful setup evidence**

**Given** an isolated synthetic setup target and a committed owner receipt,
**When** the fixture verification reads the version through the ordinary authenticated API,
**Then** it separately verifies the exact domain definition and its current authorized
consumer path, rather than treating command completion as proof of working access,
**And** command diagnostics expose only safe target/operation/outcome references,
**And** failure/retry retains committed owner state without automatically reverting another owner.

**Command contract proposal:** Owner-local `questionnaire.bootstrap_initial`, exposed
through protected operator tooling using the existing controlled-command envelope:
schema_version 1, operation_id UUID, organization scope with exact Khula org_id,
typed payload with questionnaire_id, version_id, expected absence and definition,
bounded reason_code and optional safe evidence_ref. The four question UUIDs are explicit
in the versioned payload, not allocated anew on retry or derived from labels/position.
This is a command identifier, not an installed shell invocation or a checked-in live-data seed.

Use one local transaction and the shared proven operation/evidence mechanism. The
bounded reference/configuration command follows the existing versioned SHA-256/JCS
design; receipts omit the definition/fingerprint and carry compact target/disposition/
revision/event evidence. Questionnaire content is not an observation payload, but remains
outside diagnostic dumps. No capture-answer fingerprint choice is settled by this story.

**Persistence/validation boundary:** KDG questionnaire identity plus immutable published
version with relational org/version/actor/time fields and schema-validated JSONB definition.
Tenant-aware references and unique version identity protect the structural boundary;
validated unique question IDs within each JSON definition preserve question identity. A single initial published version needs no administrative draft rows or
questionnaire editor; later publication reuses the same domain validator/immutable-write
invariant. Validate required schema, exact initial types/defaults/labels and duplicate
question IDs; return safe paths/identifiers without raw input echoing. Server times and
executing actor come from verified context. Published records and evidence are retained.

**API boundary:** `GET /api/v1/questionnaire-versions/{version_id}` under current
`kdg_capture.capture.read.own` for both maintained default roles, fixed Khula scope and
the registered KDG caller. This read reveals only a published definition, grants no
capture/edit/admin power and renews no offline capability/assignment lease. Exact
IDs/definition schema come from KDG Pydantic/OpenAPI with generated/validated TypeScript.
The later `/provision` endpoint will consume the same domain read without creating a
second source of questionnaire truth.

**Dependencies and sizing gates:**

| Dependency | Required evidence before this story's Build |
| --- | --- |
| Approved Story 1.1 | KDG bearer/current entry integration and safe shared client/errors |
| Existing P-WRITE / P-SCAFFOLD | Proven restricted KDG runtime/migration/operator separation, owned Alembic history, transaction scope/RLS, atomic operation/evidence and immutable record fixtures |
| Existing Identity operator owner | Trusted executor/actor binding, no supplied actor authority; supported restricted owner-command adapter |
| Existing release owner | KDG migration ownership registered with current coordinator; isolated target, clean/upgrade rehearsal and activation-failure evidence |
| App contract closure | Typed seed definition/envelope/receipt, explicit target IDs, privileges and exact invocation syntax validated before ready status |

No later KDG story is a dependency. If shared owner-write/operator mechanisms have not
been delivered, keep this story blocked rather than expanding it into their implementation.
Real Louwnique/Khula provisioning is an explicitly authorized later operation; delivery
acceptance uses synthetic equivalents and performs no production setup during planning.

**ATDD and traceability:**

| Scenario IDs | Acceptance | Public boundary |
| --- | --- | --- |
| KDG-A03.questionnaire-initial | AC-1/6 | Targeted operator command plus authenticated version-read integration |
| KDG-A03.questionnaire-operator-denied | AC-2 | Actual restricted operator/runtime credentials and target checks |
| KDG-A03.questionnaire-replay | AC-3 | Real PostgreSQL transaction/concurrency/lost-response fixtures |
| KDG-A12.questionnaire-immutable | AC-4 | Supported alternate writers under actual restricted DB roles |
| KDG-A01.questionnaire-read / KDG-A14.version-scope | AC-5 | KDG API/current Access and tenant-context negative tests |
| KDG-A21.questionnaire-attribution | AC-2/3/6 | Actor/time/rollback/immutable evidence and diagnostic filtering |

After final implementation approval, bmad-build first observes the missing-behavior
failure for KDG-A03.questionnaire-initial, then runs focused definition/authority/
transaction tests and affected contract/migration suites. Shared P-WRITE/P-ACTOR/
P-ACCESS/P-RELEASE proofs remain independently owned. No command/test is executed now;
exact package/test invocation is supplied by verified delivery tooling.

**Delivery impacts:**

| Area | Decision |
| --- | --- |
| Scaffold | Reuse proven owner command/immutable-write/transaction fixtures; promote a newly proven neutral extension with platform owner in this item; questionnaire schema stays in KDG |
| Shared UI | No new control in this server/setup increment; later renderer consumes the definition |
| Agent instructions | Document owner-only setup, stable IDs, immutable versions and verified invocation in KDG guidance; root/shared edits need handoff agreement |
| Documentation | Update setup recipe, API schema, synthetic fixture evidence and recovery/runbook links |
| Contract | KDG definition/OpenAPI/TypeScript and typed command/result evolve together; Identity/Access contracts unchanged here |
| ADR | Adopt platform operations, ownership, attribution and release decisions; app JSON/version decision remains linked; no superseding platform ADR required |

**Review checkpoint:** Scope/criteria approved by the user with C. Planning approval
alone does not authorize execution or remove shared/readiness gates.

### Story 1.3: Provision the initial child and facilitator assignment

As an authorized KDG setup operator,
I want to create Sinehgomso and an explicit assignment to Louwnique's verified account,
So that the first capture slice has an eligible child without requiring the administration portal.

**Scope and size:** One KDG setup/read increment: child and assignment records, a bounded
owner command and current-user eligible-child API. Reuse Story 1.2's proven owner-write/
operation/evidence mechanisms. Identity and Access retain account, membership, actor and
role ownership. Phone capture, offline leases and editable administration follow separately.

**Requirements:** Child/assignment FR-3/12, scope FR-1/2, eligible-choice FR-4;
NFR-1/2/5; AD-1/2/10. Administrator create-all and capturer assignment-only scope are
user-approved. A stored assignment is not a membership, employment fact or app grant.

**Acceptance Criteria:**

**AC-1 — Exact initial domain setup**

**Given** fixed child/assignment UUIDs, explicit expected absence, configured Khula
org_id and trusted owner evidence identifying Louwnique's exact current account/membership,
**When** an authorized KDG operator runs initial child/assignment setup,
**Then** it creates active child Sinehgomso and the explicit account-bound assignment,
**And** creation/update actor and UTC times derive from verified execution context,
**And** it creates no child Auth identity, account, membership, employment or application grant.

**AC-2 — Verified assignment target and organization**

**Given** an unknown/inactive account, wrong organization, missing current Khula
membership, missing applicable capture capability, spoofed target evidence or mismatched child,
**When** setup validates the proposed assignment,
**Then** it refuses the assignment with safe typed error information,
**And** does not infer identity from Louwnique's display name/email or copy another
owner's tables into KDG,
**And** unavailable required verification fails safely rather than treating the target as eligible.

**AC-3 — Atomic writes and safe retries**

**Given** a valid targeted command and stable operation ID,
**When** setup commits, fails partway, races another attempt or loses its response,
**Then** child, assignment, attribution, required compact change evidence and receipt
commit together once, or no local domain changes commit,
**And** identical authorized replay returns the original outcome without duplicate rows/events,
**And** changed-input reuse or a new expected-absence command against existing targets
is refused without overwriting or reactivating existing domain state.

**AC-4 — Eligible children follow current application authority**

**Given** a signed-in user admitted to KDG in Khula,
**When** that user requests capture-eligible children through the KDG API,
**Then** a capturer sees only active children currently assigned to that account,
**And** a questionnaire administrator with current create-all authority sees every
active Khula child, even without an assignment to that child,
**And** another facilitator's assignments and other organizations' children are not disclosed.

**AC-5 — No eligibility inferred from stored assignments**

**Given** an existing assignment but absent/revoked membership or applicable app authority,
**When** the account requests eligible children,
**Then** current admission/permission checks prevent unauthorized disclosure,
**And** a verified empty eligible set differs from unavailable verification,
**And** no supplied account/org selector can change whose assignments are evaluated.
Entry-only users with current own-history access but no creation permission receive
an explicit no-capture-eligibility state; assignment removal does not revoke own-history
rights. Actual historical capture reads/edits are delivered in E2, not claimed by this story.

**AC-6 — Restricted operator and consumer proof**

**Given** missing/wrong target, normal API credentials or unauthorized operator authority,
**When** setup is attempted,
**Then** it is rejected before writes without sensitive payload diagnostics,
**And** a permitted synthetic run is verified through the ordinary eligible-child API,
**And** receipt completion alone is not reported as proof of consumer eligibility.

**Command proposal:** `child.bootstrap_initial` uses the existing schema-versioned
owner envelope with Khula organization scope, operation_id, expected absence for child
and assignment, stable child/assignment/account IDs, child display name, reason/evidence
references and trusted operator context. The protected input binds actual account UUIDs;
no checked-in live credentials or automatic name/email lookup. Validation of external
identity/access occurs before short KDG write locks. Child and assignment commit in one
local transaction. No other owner's committed state is automatically rolled back.

**Target-verification gate:** Canonical Access `/v2/check` derives the target account
from the end-user bearer; an operator's bearer cannot be used to check Louwnique's
permissions by adding an account selector. Existing Identity/Access owners must declare
the narrow trusted operator target-evidence/check path before this story is ready.
Evidence binds exact account, Khula membership, applicable capture capability and its
freshness; a display name or old setup receipt is insufficient. Do not create a new
Access service, broaden a caller policy or invent a public target lookup in this story.
This is an explicit shared handoff/readiness input, not an implemented endpoint.

**Persistence:** KDG owns child and account-bound child assignment, each with non-null
org_id, server attribution and revision. Enforce same-org child references, stable IDs
and unique `(org_id, child_id, account_id)` assignment identity; retain change evidence.
No cross-owner table access/FK is introduced to validate account eligibility. Only the
initial active-state writes are delivered here; later assignment/deactivation lifecycle
and normal admin commands are E5. Membership rejoin behavior for old assignments must
be resolved with that lifecycle before its consuming story, without weakening current grants.

**Read API:** `GET /api/v1/children`, authenticated, private/no-store, fixed Khula and
bearer account only. First verify KDG entry, then the exact same-organization creation
capability: create-all permits all active children; create-assigned permits only current
assignments. Known denial of create-all may evaluate the separately registered
create-assigned alternative; never substitute account scope, cached authority or an
unverified administrator flag. Required-check outage remains an unavailable outcome.
Return typed child IDs/names plus explicit eligible/no-eligible/no-create-permission
status; client never chooses another account's scope. A sole eligible child can be
selected automatically by the later capture surface. Define Pydantic/OpenAPI and
generated/validated TypeScript together.

**Dependencies:** Approved Stories 1.1/1.2; existing P-ID/P-ACCESS current checks and
the owning target-verification path; trusted owner-command adapter and P-WRITE/runtime
RLS/migration support already required by 1.2. No later KDG story, People integration,
questionnaire editor or normal onboarding portal is required. Delivery uses synthetic
equivalents; real initial setup occurs only under later explicit target authorization.

**ATDD and traceability:**

| Scenario | Criteria | Public boundary |
| --- | --- | --- |
| KDG-A03.child-assignment-initial | AC-1/6 | Targeted operator command and current-user eligible-child API |
| KDG-A03.child-assignment-replay | AC-3 | Restricted PostgreSQL writer, concurrency/rollback/lost-response fixtures |
| KDG-A02.child-eligibility | AC-4 | Capturer/admin API fixtures; admin without assignment |
| KDG-A14.assignment-target-scope | AC-2/5 | Owner-evidence/tenant-reference/selector negative tests |
| KDG-A16.assignment-authority | AC-2/5 | Revoked membership/grant and unavailable-check contract fixtures |
| KDG-A21.assignment-attribution | AC-1/3/6 | Trusted actor/UTC provenance, atomic evidence and log minimization |

After final implementation approval, bmad-build first observes the expected missing
behavior for KDG-A03.child-assignment-initial; focused assignment/scope/transaction tests
then the affected contract/RLS suites follow. Exact commands come from verified tooling.
No setup command, migration, test or live access change is executed during planning.

**Delivery impacts:**

| Area | Decision |
| --- | --- |
| Scaffold | Reuse/prove owner command, scoped reference and attribution fixtures; child semantics remain KDG-specific |
| Shared UI | No new control here; later capture/admin consumes typed choices |
| Agent instructions | Document fixed-org/account-based assignments and non-authorizing domain associations in KDG guidance |
| Documentation | Update setup recipe, target-verification handoff, API/test map and safe recovery evidence |
| Contract | KDG child/assignment/OpenAPI contracts stay app-owned; shared target validation remains coordinated with Identity/Access |
| ADR | Adopt existing ownership/access/attribution decisions; record later lifecycle/rejoin decision before E5, no accepted ADR edited |

**Review checkpoint:** Scope/criteria approved by the user with C. Planning approval
does not authorize implementation or remove the shared readiness gate.

### Story 1.4: Install KDG Capture and provision authorized setup for offline opening

As a Khula capturer or questionnaire administrator,
I want to install KDG Capture and download my authorized child and questionnaire setup,
So that I can reopen the application and view that setup without internet.

**Scope and size:** One initial offline setup increment: manifest/app-shell caching,
current authenticated setup read, account/organization-scoped IndexedDB snapshot and
offline opening. Reuse approved entry/version/child boundaries. This delivers a read-only
setup screen, not observation saving, synchronization or downloaded capture history.
Only setup metadata, capability observations, child choices and version definitions need
local stores here; later stories add saved capture/queue stores when consumed; no unfinished-entry store.

**Requirements:** FR-4/13, setup portion of FR-16/17/18; FR-1/2 permission boundaries;
NFR-1/2/3/4/5. UX-DR1/2/4/7/11–14; AD-1–4/7–10. The seven-day window is approved
device-local policy, never a server authorization token.

**Acceptance Criteria:**

**AC-1 — Current authorized setup**

**Given** an authenticated user and the preceding published version/child setup,
**When** the user provisions this phone online,
**Then** KDG verifies current Khula admission and the exact applicable capabilities,
**And** returns the verified account/actor, eligible children and exact initial published
questionnaire definition with scoped authorization/assignment observation times,
**And** capturers receive assigned children and administrators all active Khula children,
**And** a known no-eligible/no-create state differs from unavailable verification.

**AC-2 — Local completion before readiness feedback**

**Given** valid complete setup data for the current account/Khula partition,
**When** the application persists the setup and confirms its required shell is cached,
**Then** setup data and its active-snapshot metadata commit atomically in IndexedDB,
**And** only then does the screen acknowledge that this setup is available on this phone,
**And** network interruption, invalid schema/scope, quota or storage abort never marks
partial setup as complete or replaces the last valid snapshot with incomplete data.
Shell cache and IndexedDB are separate writes; completion checks both rather than
claiming one transaction spans browser Cache Storage and IndexedDB.

**AC-3 — Installed offline cold opening**

**Given** completed setup in the installed app and a valid local-use window,
**When** the user disconnects, fully closes and reopens KDG Capture,
**Then** the cached shell opens and reads that account's stored child/version setup,
**And** the initial single eligible child is Sinehgomso without an organization selector,
**And** the setup screen makes no claim that an observation was saved or server-backed,
**And** missing initial setup explains the online requirement rather than inventing data.

**AC-4 — Scoped seven-day observations**

**Given** a successful current online observation for a specific account, Khula,
capability and applicable child/assignment scope,
**When** local access is evaluated after disconnection,
**Then** its expiry is seven days after that successful server check, bounded by the
required entry/create/child observations' earliest expiry,
**And** token expiry alone does not end a still-valid local window,
**And** an unrelated entry/read/update request cannot renew stronger cached create/admin/
assignment observations,
**And** expired local access requires online verification without deleting the stored setup.
Clock rollback/implausible time requires online verification; browser time remains a
best-effort device policy, not tamperproof authority.

**AC-5 — Account isolation and learned denial**

**Given** explicit logout, a different account, known denial or a late setup response
from a previous account/session generation,
**When** the shell evaluates or updates local setup,
**Then** it exposes only the permitted active account/Khula partition,
**And** logout or entry denial locks the prior partition while retaining data,
**And** learned creation/assignment loss invalidates the affected choices/observations,
**And** a stale response cannot unlock or renew a logged-out partition or populate the
replacement user's screen; returning to locked data requires same-account online reauthorization.
Persist invalidation before claiming a durable state change; failed local writes leave
a truthful storage error and block affected use in the active session.

**AC-6 — Cache, storage and update boundaries**

**Given** the app-shell service worker and initial local schema,
**When** it handles navigation/resources, encounters storage loss or finds an app update,
**Then** only versioned shell assets/navigation are cached; Auth/provider/protected API
responses and business payloads do not enter generic service-worker caches,
**And** denied persistent-storage permission is not presented as a backup guarantee,
**And** eviction/cleared storage produces an honest reprovision state,
**And** an update does not force a reload during setup/local writes or reset local stores;
unsupported schema blocks safely with Retry instead of delete/reset recovery.

**AC-7 — Phone identity, accessibility and evidence**

**Given** the reachable isolated HTTPS fixture and supported installation flow,
**When** Android and iPhone installed setup/opening are checked,
**Then** home-screen/app name is KDG Capture, login shows Khula Development Group,
and the setup/capture-facing subtitle is Daaglikse waarnemings,
**And** preparation/checking/available/empty/denied/unavailable/storage-error states
have accessible labels, focus, readable text and Retry where applicable,
**And** actual installed-device results identify model/OS/browser/build and remain
separate from Playwright emulation. Provision inside the installed context; browser-tab
setup is not assumed to provide its session/cache automatically.

**Provision contract increment:** `GET /api/v1/provision`, private/no-store and current
bearer/fixed Khula only. Compose existing KDG domain reads under verified current scope;
external authorization calls precede the short local read transaction. Include schema
version, account/actor/membership, exact scope, published questionnaire/version/definition,
eligible-child status/rows and observations keyed to exact permission/resource scope with
checked_at and expires_at. Assignment observations additionally identify the applicable
assignment/revision; administrator create-all requires no fabricated assignment field.
Return no credentials or replayable authority. Missing/mismatched account/scope/schema
fails validation. Only verified successful capability observations are renewed.

This increment does not require capture tables or a history endpoint. Later history
downloads use the owning paginated read; absence of history from this setup response
does not assert an empty server history. Store the exact immutable downloaded version;
future refresh changes the new-entry version pointer without mutating existing definitions
or pinned open-entry/saved-capture references. The no-create case mints no creation observation.

**PWA/local boundary:** App-specific manifest with both names KDG Capture, configured
canonical origin/start URL/scope, standalone presentation and required icons. Use the
existing Vite scaffold/build owner for verified shell precaching and deferred update
registration; exact adapter/pins are a pre-Build validation input, not installed now.
Native IndexedDB provides transaction/schema versioning with an account/org namespace.
Network/cache preparation happens outside an IndexedDB write transaction. A stored setup
generation and active session generation guard refresh/late callbacks. Request persistent
storage where supported, handle writes failing, and disclose browser deletion/eviction limits.
Private browsing is not a supported durable installation; no detection guarantee is claimed.

**Dependencies:** Approved Stories 1.1–1.3 and their shared owners; the concrete setup DTO/
capability-expiry/error variants and compatible PWA build configuration; reachable
nonproduction HTTPS/Auth callback and actual Android/iPhone fixture targets. No future
KDG capture/edit/sync story is required to complete read-only offline setup. PWA first-
consumer promotion follows coordinated platform ownership, not a second generator.

**ATDD and traceability:**

| Scenario | Criteria | Boundary |
| --- | --- | --- |
| KDG-A04.setup-offline-open | AC-1/3/7 | Browser setup/cold reopen plus installed Android/iPhone smoke |
| KDG-A07.setup-local-commit | AC-2 | Real IndexedDB transaction/abort/interrupted-download fixtures |
| KDG-A15.setup-window | AC-4/5 | Deterministic expiry/token/logout/account-return fixtures |
| KDG-A14.setup-partition | AC-1/5 | Wrong-scope/current-account and late-response negative tests |
| KDG-A16.setup-scoped-renewal | AC-4/5 | Denied/unavailable/partial capability refresh fixtures |
| KDG-A17.setup-storage-update | AC-2/6 | Quota/eviction/schema/update/cache-policy fixtures |
| KDG-A19.setup-accessible | AC-7 | Keyboard/focus/zoom/browser checks and physical assistive technology |

After implementation approval, bmad-build first observes the missing behavior at
KDG-A04.setup-offline-open, then focused provisioning/local state tests and the affected
contract/browser suites. Installed setup smoke validates this foundation early; the full
offline capture/reopen/sync physical proof follows the completed first vertical slice.
No device, installation, dependency, migration or deployment action is performed now.

**Delivery impacts:**

| Area | Decision |
| --- | --- |
| Scaffold | Prove/promote opt-in manifest/shell cache, minimal partition/transaction/schema fixtures and deferred-update hook with existing owner; no generic offline engine |
| Shared UI | Prove accessible setup/progress/retry/storage/update notices; KDG child/questionnaire rendering remains app-specific |
| Agent instructions | Record cached local setup vs current server authority, exact window and actual PWA commands in KDG guidance; coordinate root/shared edits |
| Documentation | Maintain installation/setup/privacy-limit/device evidence and generated-pattern adoption notes |
| Contract | KDG setup OpenAPI/TypeScript, exact scoped observations and local schema align; Access still owns permission decisions |
| ADR | Inherit accepted API/silo/session/scaffold rules; explicit seven-day app-local policy stays separate from server authorization; no accepted platform ADR edited |

Feasibility references: [W3C manifest](https://www.w3.org/TR/appmanifest/) and
[Apple installation guide](https://support.apple.com/guide/iphone/bookmark-a-website-iph42ab2f3a7/ios).
Exact supported phone behavior is established by physical validation, not these links.

**Review checkpoint:** Scope/criteria approved by the user with C. Readiness and
final implementation approval remain separate gates.

### Story 1.5: Explicitly save an observation on this phone

As a Khula capturer or questionnaire administrator,
I want to complete the short form and explicitly save it on my phone,
So that a completed observation can be reopened offline and synchronized later.

**Scope:** Initial Afrikaans form, explicit local Save, atomic capture/pending-create
storage and minimal local record list/details/reopen. Unfinished input stays in memory;
no observation autosave/draft recovery. Server upload is next, not a dependency.

**Requirements:** FR-4–7/13/15, local FR-8/14/16–18; NFR-1–5. UX-DR2–8/11–13;
AD-2–5/7–9 and proposed KDG ADR-0001.

**Acceptance Criteria:**

**AC-1 — Correct short form**

**Given** authorized phone setup,
**When** the user starts an observation,
**Then** the four exact Afrikaans questions use accessible large choices, rating 1–5
initially unanswered, endpoint labels Goed/Nie goed nie and Ja/Nee default Nee,
**And** Sinehgomso is automatic when sole eligible child; additional choices follow scope,
**And** date defaults to the phone date, is editable and is separate from recording times,
**And** authenticated author is not editable and the open form pins its version.

**AC-2 — Explicit validation and active answers**

**Given** entered values,
**When** Save observation is selected,
**Then** all four primary answers are required; 1 and false are valid answers; 0 is invalid for the initial scale,
**And** Ja reveals optional multiline Besonderhede; Nee hides it and excludes details
from the saved answer, while toggling Ja restores temporary text while this form is open,
**And** invalid input shows accessible correction without recording an observation.

**AC-3 — Atomic local success**

**Given** valid input and current local creation/child authority,
**When** Save completes,
**Then** the capture snapshot and stable pending create operation commit together in
IndexedDB under account/Khula scope,
**And** only then is Saved on this phone shown and the completed local record opened,
**And** no Synced/server-backed claim or unfinished-form persistence occurs.

**AC-4 — Reopen, multiplicity and repeat-click safety**

**Given** an acknowledged capture,
**When** the app closes/reopens offline within permitted local access,
**Then** details retain owner, date, version, device recording time and pending status,
**And** distinct saves may create multiple captures per child/date,
**And** repeated clicks/retries of one attempt create no extra capture/operation.
Offer Edit existing / Add another only for locally known records; no offline duplicate
detection promise. Existing-record editing is E2.

**AC-5 — Failed or uncertain Save**

**Given** quota/transaction failure or unconfirmed Save,
**When** success cannot be acknowledged,
**Then** keep values visible with plain guidance, reclaim safe disposable cache if
available, use bounded recovery and stop repeated attempts on persistent failure,
**And** resolve uncertainty using original IDs/frozen input before a changed attempt,
**And** no false saved feedback, deliberate crash, data clearing or restart advice
is offered while typing exists only in memory.

**AC-6 — No unfinished-input recovery workflow**

**Given** input not explicitly saved,
**When** the app/page closes or restarts,
**Then** no restoration promise or saved draft exists,
**And** app-controlled departure from a changed explicit-Save form uses ordinary unsaved-
changes confirmation; OS termination is not assumed to permit a dialog,
**And** no draft flush/status/list/resume/merge interface is introduced.

**AC-7 — Scope, version and updates**

**Given** permission/assignment changes, expiry, another account or new questionnaire,
**When** Save/read is evaluated,
**Then** required local scope is checked, another account cannot view/submit the capture,
and acknowledged pending captures retain owner/version,
**And** new downloads do not silently change the open form's version,
**And** updates do not force-reload unsaved typing or destroy pending operations.
Server sync independently rechecks current authority in its owning story.

**Local contract:** Capture UUID and distinct operation UUID identify one explicit
attempt. Freeze its snapshot across uncertain retries. Capture/pending command/version/
owner binding and acknowledgement commit atomically. Device time is not server audit
time; the server verifies actor/account later. Add completed capture/queue stores only.

**Dependencies:** Approved 1.1–1.4; validated capture/queue local schema/migration,
create-command version, safe quota/error handling and revised explicit-form acceptance.
Store/test typed pending commands without a server upload handler; the next sync story
consumes them. There is no forward dependency on that handler.

**ATDD:** KDG-A05.form-answers, A06.same-day-captures, A07.saved-capture-reopen,
A08.explicit-save-failure, A09.local-repeat-save, A14.capture-partition, A15.capture-window,
A17.capture-storage-update and A19.capture-accessible. First observe the expected failure
for A07.saved-capture-reopen after implementation approval, then focused validation/local
transaction tests and affected browser suites. Physical checks remain separately recorded.

**Impacts:** Scaffold/UI: prove explicit-form, atomic local capture/queue and safe status/
error patterns with existing owners; no local-draft engine. Agent/docs: update saving
scope, real commands and evidence. Contracts: version local command/storage and future
server DTO together. ADR: proposed app ADR-0001 follows platform exception rules;
no shared accepted decision changes. No implementation/tests executed during planning.

**Review checkpoint:** Revised explicit-Save scope approved when the user requested
next after the simplified plan was presented. This is planning approval only; readiness
and final implementation approval remain required.

### Story 1.6: Synchronize a saved capture and view its server-backed record

As the authenticated author of a capture saved on my phone,
I want it to synchronize safely when online,
So that the same observation is stored on the server without duplicates or lost local work.

**Scope:** Capture-create API, compact operation-outcome lookup, single-record read and
foreground create-queue delivery/status. Consume 1.5's actual saved captures; add only
needed server capture/revision persistence and operation receipts. Full history/edit,
administrator all-record views and questionnaire editor are later epics, not dependencies.

**Requirements:** FR-1/2/11/14/15/16/17; initial server FR-8; NFR-1/2/4/5.
UX-DR4/7/8/11/13; AD-2/3/5/7–10. No unfinished-form save/recovery returns in this story.

**Acceptance Criteria:**

**AC-1 — Current-authorized server creation**

**Given** an acknowledged local capture/pending create and its same authenticated account,
**When** it is submitted online,
**Then** the API checks current Khula admission, membership and exact applicable creation
authority, then current child/assignment and original published-version rules,
**And** account/actor attribution comes from verified execution, never an editable author,
**And** capture, initial immutable revision, server UTC attribution and compact operation
receipt commit together before success; creation starts at server revision 1.
Device observation/recording dates remain separate from trusted server creation time.

**AC-2 — Idempotent retry and duplicate concurrency**

**Given** the same operation/capture IDs and frozen submitted content,
**When** attempts race or the server commits but its response is lost,
**Then** one capture/revision/receipt commits and authorized replay returns that outcome,
**And** changed content under the same operation ID is rejected without overwrite,
**And** an unresolved outcome retains its original IDs and is looked up/retried safely;
no fresh observation is created merely because an earlier response was uncertain.
Distinct operations/capture IDs for the same child/date remain allowed.

**AC-3 — Foreground and manual synchronization**

**Given** permitted pending creates and network/session availability,
**When** the app opens, resumes, reconnects or the user selects Sync now,
**Then** a bounded foreground cycle attempts delivery without relying on background sync,
**And** disconnected/expired-auth/transient-failure items remain durable,
**And** multiple windows use durable claims/recovery while server uniqueness remains
the safety guarantee; interrupted attempts resolve their original outcomes.
One Needs attention item does not stop independent pending records.

**AC-4 — Truthful acknowledgement and server read**

**Given** a committed matching receipt for the current local saved snapshot,
**When** the client records it locally,
**Then** it shows Synced and stores the server identity/revision/attribution,
**And** the same authorized account can fetch the record through the normal KDG API,
**And** a stale response acknowledges only its original snapshot, never newer local content.
Local acknowledgement failure after server commit is recovered through the original receipt.
Receipt lookup is not a substitute for a fresh current-record read.

**AC-5 — Rejection and unavailable checks**

**Given** lost membership/grants, changed assignment, a fresh inactive-child request
without verified prior eligibility, invalid answers,
wrong scope or unavailable verification,
**When** queued creation is attempted,
**Then** the API applies no unauthorized capture effects and returns the safe typed outcome,
**And** the client retains the original local capture/operation, stops automatic retries
for known rejection and distinguishes it from retryable unavailability,
**And** neither administrator impersonation nor new child/owner substitution bypasses rejection.
Known entry loss locks protected local display; no inaccessible record details appear.

**AC-6 — Session/account and questionnaire compatibility**

**Given** token renewal, same-account reauthentication, a different account or a newer
published questionnaire,
**When** delivery resumes,
**Then** only the original author partition can send its saved intent after current checks,
**And** sign-in never saves unfinished typing or confirms a new unrelated action,
**And** the saved capture's original published version is accepted and retained even
when a newer version exists; no answer migration or latest-version substitution occurs.
Typed old-version fixtures prove this consumer; actual editor publication is E4.

**AC-7 — Bounded failures and sensitive-data safety**

**Given** slow Access, network failure, malformed response or unexpected server failure,
**When** the cycle reaches its deadline,
**Then** it exits with honest pending/attention state and Sync now/retry where applicable,
**And** no business lock is held through external waits,
**And** errors/diagnostics omit child notes, answers, credentials and payload dumps,
**And** supported queued command versions survive ordinary releases; unsupported versions
are retained for investigation rather than silently deleted.

**Wire/persistence:** `POST /api/v1/captures` uses capture_id, operation_id,
command_version, child_id, questionnaire_version_id, observation_date, answers and
untrusted local captured_at. Fixed Khula and author derive from service policy/bearer;
reject client audit/owner/org selectors. Validate required answers against that exact
version, including valid 1/false values and rejection of hidden false details. Tenant-aware local
references/RLS and backend ownership checks accompany restricted runtime roles.

Mutations store scoped operation identity/fingerprint and compact committed result in
the same transaction as capture/revision history. Shared setup receipts may reuse a
proven owner mechanism, but retain separate command/caller authority. Capture-answer
fingerprint algorithm/key lifecycle and canonical input must be declared before Build;
the earlier configuration-command SHA-256 choice does not silently decide private answers.

`GET /api/v1/operations/{id}` is scoped to original caller and capture-create command;
current own-read authority may retrieve a receipt even if creation permission was later
removed. This reveals no other caller's operation and grants no new create. `unresolved`
is not proof of no commit. Retrying POST still requires current creation authority.
`GET /api/v1/captures/{id}` rechecks current own-read and returns the authorized original
version/answers/owner/editor/revision. Organization-wide record reads are E3.

**Client bounds:** Proposed maximum 30-second cycle, 10-second request, at most three
write sends per item/cycle and 1/2/4-second jittered backoff within the remaining budget.
Resolve uncertainty before changed/new commands; known validation/denial does not loop.
Do not renew unrelated offline observations from Sync success. Persist claims/receipt/
status under the original account/org and guard late callbacks/session generation.
Already explicitly saved durable intent may resume under fresh same-account authority;
this is replication, not automatic confirmation of unfinished form input.

**Dependencies:** Approved 1.1–1.5 and existing owner-write/release/Access mechanisms;
concrete create/outcome/read schemas, fingerprint/retention bounds, actor/schema/RLS and
queue compatibility fixtures. No future KDG story is required for create/read sync.
Normal release compatibility/activation gates remain; no migrations or deployment now.

**ATDD:** KDG-A09.create-replay/lost-response, A20.foreground-sync, A10.create-claim-recovery,
A02.create-authority, A14.server-capture-scope, A15.sync-reauth, A16.create-rejected,
A12.create-original-version, A21.server-attribution/logs and A22.queue-release-compatibility.
First observe expected missing behavior at A09.create-lost-response after implementation
approval, then focused validation/transaction/client tests and affected contract/browser
suites. Saved-phone → server-backed record is the core endpoint proof; the next story
records full installed Android/iPhone first-slice evidence.

**Impacts:** Scaffold: prove current-authorized idempotent writes/receipts and bounded
claim/retry fixtures with existing owners; no sync service/worker engine. Shared UI:
accessible Saved on this phone/Synced/Needs attention and Sync now. Agent/docs: record
attempt/outcome semantics, actual commands and safe support evidence. Contracts:
Pydantic/OpenAPI/generated TS and versioned local queue together. ADR: inherited
authorization/operation/transaction/release rules and app explicit-Save rationale;
no shared accepted ADR edited. Planning only; no runtime/device evidence claimed.

**Review checkpoint:** Scope/criteria approved by the user with C. Planning approval
remains separate from readiness and implementation authority.

### Story 1.7: Prove the first capture slice on installed Android and iPhone PWAs

As the KDG product owner,
I want evidence that the first capture slice works on actual installed phones,
So that offline limitations are discovered before completing the wider application.

**Scope:** Reusable first-slice scenario/fixture/reporting plus physical installed-device
validation of Stories 1.1–1.6. Use actual KDG routes/shared dependencies and synthetic
nonproduction accounts/children. No duplicate reference-app workflow or new domain table.
This is the early end-to-end proof, not implementation approval or a claim of results now.

**Requirements:** UJ-1, E1 portions of FR-1–8/11/13–18; NFR-1–5; UX-DR12–14.
Offline edits, administrator all-record history and actual questionnaire publishing remain
E2–E4 tests, not requirements for completing this first-slice proof.

**Acceptance Criteria:**

**AC-1 — Actual first slice on both platforms**

**Given** a verified isolated HTTPS environment with supported real Auth/Access/KDG
integration, targeted synthetic setup and actual Android/iPhone devices,
**When** each installed PWA runs sign-in → fixed Khula setup → disconnect → explicit
Save observation → fully close/reopen → local details → reconnect/Sync now → server read,
**Then** local/server record identity, answers, author, observation date and version agree,
**And** Saved on this phone precedes Synced, with no false server-backed acknowledgement,
**And** neither platform is reported passed using browser emulation alone.

**AC-2 — Capture semantics and accessible phone behavior**

**Given** the initial question definition and eligible fixture child,
**When** the user chooses rating/Ja/Nee/details/date and saves another same-day capture,
**Then** the correct labels/defaults, hidden-detail exclusion and multiple-capture behavior
work with keyboard/touch, phone keyboard/safe-area and text scaling,
**And** installed TalkBack/VoiceOver checks can reach choices, Save, record details and Sync now.
Unfinished typing has no crash/restart recovery promise; do not reintroduce draft UX.

**AC-3 — Repeatable interruption and access boundaries**

**Given** controlled nonproduction fault/permission fixtures,
**When** response-after-commit is lost, sync is interrupted, verification is unavailable
or a pending record loses creation permission,
**Then** replay produces one server effect and saved work is retained with truthful state,
**And** wrong-account/org, revoked authority and unavailable verification remain distinct
through existing backend/contract tests and selected installed-device scenarios,
**And** no test restores access automatically or uses another account to upload the record.
Clock-driven seven-day threshold checks are automated; physical same-account reauthentication/
logout/account-isolation smoke is recorded separately. Do not pretend seven days elapsed.

**AC-4 — Pending create survives ordinary app update**

**Given** an acknowledged local capture awaiting sync,
**When** the nonproduction shell is updated through supported deferred activation,
**Then** the pending command/version and capture remain readable/retryable after reopening,
**And** updates do not force-reload an unsaved form or reset local data,
**And** changed-schema/old-version fixtures exercise the already-declared local/release
compatibility boundary; complete edit-chain/pilot hardening remains later coverage.

**AC-5 — Traceable, honest evidence**

**Given** automated checks and each physical protocol run,
**When** results are recorded,
**Then** evidence identifies exact environment, source/API/shared-service builds,
device model, OS/browser, installed mode, scenario, time and pass/fail/not-run outcome,
**And** permission/constraint tests identify actual restricted runtime roles,
**And** missing devices, skipped steps, fakes or emulation are never recorded as physical passes.
Record exact commands and initial ATDD failure/passing results from the verified packages,
not root npm build/dev or invented commands. Capture screenshots/traces only with synthetic
content and redact credentials; operational evidence contains safe identifiers, no real child notes.

**AC-6 — Findings change the owning plan before expansion**

**Given** a failed or incomplete installed-phone result,
**When** it is triaged,
**Then** the issue is attributed to its actual owning capability/story with reproducible
evidence and a clear correction or unsupported limitation,
**And** no PWA reliability/phone acceptance is claimed until required checks pass,
**And** findings affecting storage/isolation/auth/updates are resolved before broadening
the app. KDG's evidence does not authorize Leave implementation or weaken shared release gates.

**Protocol minimum:** One actual supported Android/Chrome installed PWA and one actual
iPhone/Safari home-screen PWA, both provisioned within that installed context. Use the
same maintained KDG application/scenarios with explicit target configuration. Test only
synthetic fixtures and required owner commands; no production target/reset/grant tests.
Supported exact device/OS/browser selection and fixture credentials precede execution.

**Dependencies:** Delivered/readiness-cleared 1.1–1.6, compatible nonproduction release/
callbacks, trusted isolated fixture target and physical devices. No E2 editing, E3 all-
record view, E4 editor, E5 assignment portal or hosted platform-verification app is required.
Any defect correction is a bounded fix in its owning story, not a generic new test engine.

**ATDD/traceability:** KDG-A01/02/04–09/14–17/19–22 as applicable to create/read scope;
the detailed [device plan](testing.md) separates early mandatory checks from later
editing/publication cases. Automated API/component/browser and restricted-DB checks run
at their narrow stable boundary; physical runs produce their own evidence. No independent
test is duplicated solely to claim the same behavior at another layer.

**Impacts:** Scaffold: promote proven target/disconnect/reopen/lost-response/update
utilities through existing owner. Shared UI: correct real accessibility/status issues
in owning consuming stories. Agent/docs: actual commands, device protocol and limitations.
Contract: verify implemented OpenAPI/client/queue compatibility; do not modify shared
contracts without ownership agreement. ADR: revisit a failed architectural assumption
through owning proposed/superseding decisions, never edit accepted ADRs. No code,
dependencies, migrations, deploy, accounts, device test or capture is executed now.

**Review checkpoint:** Story and E1 planning closure approved by the user with C.
Runtime completion comes only from later verified delivery; no implementation approval
is implied by this planning closure.

## Epic 2: Find and safely edit personal capture history

Deliver own downloaded history, original-version explicit editing, safe ordered delivery
and full baseline conflict recovery. E1 supplies the foundations; no future epic is a
prerequisite. The approved read-only increment precedes the proposed edit increment.

### Story 2.1: Browse my capture history online and offline

As a capturer or questionnaire administrator using my personal history,
I want to browse my own saved captures and download recent records for offline viewing,
So that I can see earlier observations with their original questions and attribution.

**Scope:** Current own-history API/list/details, default 30-day download and safe local
reconciliation. Administrators get this own-record view too; organization-wide history
is E3. Existing-record editing and full conflict/revision-history interfaces follow in
E2, not dependencies of this read-only history increment. No unfinished-form recovery.

**Requirements:** FR-2/8/11/13, history FR-15/16/17/18; NFR-1/2/3/4.
UX-DR4/7/8/11–13; AD-2/3/5/7/8/9. User-approved own historical access survives child
unassignment while applicable KDG authority remains current.

**Acceptance Criteria:**

**AC-1 — Current own history and default window**

**Given** current Khula membership/admission and exact own-read authority,
**When** the user opens history online,
**Then** the backend returns only captures whose original owner account is that user,
with observation date, child label, original version, attribution, current server revision
and permitted current answers,
**And** default download targets the phone's current observation date and previous 29
calendar dates; request bounds stay fixed through a paginated download,
**And** older history can be requested online without selecting another account or organization.
The downloaded window is a cache policy, not server retention or a capture date restriction.

**AC-2 — Original-version offline details**

**Given** locally saved or completely downloaded authorized records/definitions,
**When** the app closes/reopens offline within its valid own-read local window,
**Then** history and details use each capture's original questions/order/labels/scale,
original owner/creation facts, current editor/update facts and observation date,
**And** no latest-questionnaire substitution or definition recreation occurs,
**And** a record/version never downloaded is honestly unavailable offline, not displayed
with empty answers or a guessed current form.

**AC-3 — Atomic cache and pending-work preservation**

**Given** existing local captures, pending creates or later pending edit/conflict overlays,
**When** a permitted page and required original versions are merged into local storage,
**Then** the page snapshot/definitions/download progress commit atomically,
**And** repeated rows deduplicate by stable capture ID and older responses cannot replace
a newer server baseline,
**And** pending local content, original attempted IDs, base snapshots and referenced
versions remain intact; downloaded existence alone never acknowledges an uncertain operation.
Local completion status remains tied to matching receipts/current saved content.

**AC-4 — Partial downloads and failures**

**Given** interruption, authorization unavailability, quota/transaction failure or an
incomplete required-definition fetch,
**When** download cannot complete,
**Then** preserve earlier acknowledged local data and show partial/not-available state
with safe Retry where appropriate,
**And** do not treat failed loading as no captures or claim that the whole window is cached,
**And** resume/restart uses the same current account/filter context with fresh checks.
Pagination is not a long-held database snapshot; concurrent changes require refresh and
are never interpreted as deletion merely because a record disappears from a query window.

**AC-5 — Ownership after unassignment and account/session changes**

**Given** a removed child assignment but retained own-read authority,
**When** own history is requested,
**Then** historical captures remain readable without a new-create grant/current assignment,
**And** entry/read denial or local-window expiry locks affected local viewing without
discarding pending work,
**And** another account, forged selector or late previous-session response cannot read,
populate or unlock that account's history. Access outage is distinct from confirmed denial.

**AC-6 — Bounded caching and scoped renewal**

**Given** successful own-read verification or cache cleanup pressure,
**When** local history observations are renewed or disposable data is reclaimed,
**Then** only the exact verified own-read scope gets its seven-day observation; creation,
edit-all and other stronger rights are not extended,
**And** only acknowledged re-downloadable cache may be reclaimed, preserving pending
captures/operations/conflicts and all required original-version references,
**And** no default-window cleanup erases a just-saved local record merely because its
observation date is outside the downloaded window. MVP does not automatically prune
locally authored records; its later retention policy is an explicit E5/pilot decision.

**AC-7 — Readable accessible history**

**Given** the phone/computer history surface,
**When** users navigate records or return from details,
**Then** rows clearly identify child, observation date and local/synced/attention state,
with accessible keyboard/touch activation and restored focus/position,
**And** genuine empty, loading, partial, failed, denied and offline states remain distinct,
**And** date-only observation values do not shift when formatted in another timezone.
This is a history list/record detail, not aggregate analytics or an export interface.

**API/data increment:** `GET /api/v1/captures` derives caller/fixed Khula scope and
requires current `kdg_capture.capture.read.own` on each page. Typed date bounds and a
maximum 100-row page use opaque scope/filter-bound cursors. Use immutable server
creation time/ID for pagination rather than mutable answer/date values; UI can group
loaded rows by observation date. Cursor position is never authority. Current own filter
and tenant context apply regardless of cursor contents; reject account/org selectors.

Reuse the current own-record/version reads. Include the child label permitted by the
owned capture, even after assignment removal; do not use eligible-child choices as a
history authorization filter. Retain stable actor IDs and available permitted display
labels, never rewrite author facts. Full immutable revision-list presentation follows
its consuming E2 story; current record revision/editor metadata is available here.

Local history uses the existing capture/version partition plus bounded download progress/
server-baseline metadata. Fetch missing definitions outside IndexedDB transactions and
never overwrite an immutable cached definition with different content under its ID.
Download success includes exact scoped read observation evidence; stale generations
cannot renew authority after logout. A known locked partition never becomes active
merely because an earlier response arrives. No generic service-worker business cache.

**Dependencies:** Planning-approved E1, particularly 1.4–1.6; concrete history/cursor/
definition/read-observation DTOs and safe local schema/index migration. No edit endpoint,
all-record admin view, new publication or assignment portal is required. Test typed
older definitions/history fixtures without claiming future producer UI exists.

**ATDD:** KDG-A18.history-window/partial/reconcile, A08.history-storage-failure,
A14.history-owner-scope, A15.history-read-window, A16.history-unassignment,
A12.history-original-version and A19.history-accessible. First observe the expected
failure for A18.history-window after implementation approval; then focused API/pagination/
local reconciliation and affected contract/browser suites. Physical offline history
checks extend the installed device protocol; no test/phone activity is executed now.

**Impacts:** Scaffold: promote proven cursor/scoped read/cache merge fixtures through
existing owner, no generic offline history engine. Shared UI: accessible list/details/
partial/empty states, app child/question labels retained locally. Agent/docs: current
authority vs cached read and original-version/retention limits. Contract: own history
OpenAPI/generated TS/cache versions together. ADR: inherited scope/version/storage rules;
no shared accepted decision edited. Concrete cache retention is a later explicit gate.

**Review checkpoint:** Scope/criteria approved by the user with c. Planning approval
does not activate history access or authorize implementation.

### Story 2.2: Edit my captures offline and synchronize explicit changes safely

As the authenticated original owner of a capture,
I want to edit its date and answers using the original questionnaire with Save/Cancel,
So that corrections are preserved locally and synchronized without overwriting unseen changes.

**Scope:** Own-record edit context/form, explicit atomic local edit/queue Save, authorized
server edit/revision/history/receipt and edit-queue delivery. Normal edits work end to end;
revision conflicts are retained safely as Needs attention. Explicit conflict resolution
is the following E2 story, not a prerequisite for normal editing or safe rejection.
No unfinished-input autosave/recovery or administrator other-owner access.

**Requirements:** FR-2/6/7/8/11/14, conflict detection part of FR-9, scoped FR-13/15–18;
NFR-1–5. UX-DR5/7/8/9/11–13; AD-2–9. Role/ownership/current authority remain binding.

**Acceptance Criteria:**

**AC-1 — Original-version editable form**

**Given** an owned locally available capture/definition and valid exact own-edit scope,
**When** the user opens Edit,
**Then** its original questions/order/labels/scale and required rules are used,
**And** observation date and permitted answers/details are editable,
**And** original owner/creation, child and questionnaire version remain fixed,
**And** a missing original definition requires authorized download, never latest substitution.
Own historical editing needs no new-create grant or current child assignment. User-approved
child-deactivation policy A-6 likewise preserves historical edit authority; only current
KDG access/ownership/edit permission and record/version validation govern this edit.

**AC-2 — Whole-form Save/Cancel and no draft writes**

**Given** an open edit form,
**When** the user types, toggles Ja/Nee, cancels or explicitly saves,
**Then** unconfirmed typing stays in memory and Cancel changes no committed capture/queue,
**And** Save validates the entire original-version form, including valid 1/false values and hidden-
detail exclusion, then commits local saved changes plus pending edit atomically,
**And** Saved on this phone appears only after commit; no server/Synced claim is implied.
Closing/restarting before Save can lose typing; ordinary unsaved-form handling applies.

**AC-3 — Current authorized server update and immutable history**

**Given** fresh same-owner `kdg_capture.capture.edit.own` authority and expected revision,
**When** the edit reaches the server,
**Then** ownership/scope/original-version validation and conditional revision update are
protected atomically with new immutable revision evidence and compact operation receipt,
**And** creation/owner facts stay unchanged while actual editor/update time are server-managed,
**And** an authorized unchanged save records a compact outcome without fictitious
revision/history/update-time changes; stale expected revision still requires review.

**AC-4 — Ordered offline edits and safe replay**

**Given** a pending create or earlier edit for this record,
**When** later explicit offline edits are saved and sync resumes,
**Then** each saved action/snapshot has distinct durable operation identity and predecessor,
**And** creates precede edits; later commands freeze expected revision only after their
own predecessor's outcome is resolved, never guessing or replacing submitted content,
**And** committed duplicate replay creates no second revision/history event,
**And** a late acknowledgement marks only its saved sequence and cannot replace newer local work.

**AC-5 — Conflicts do not silently overwrite**

**Given** another device changed the record or a local editor holds stale local revision,
**When** an explicit edit cannot meet its expected revision,
**Then** no conflicting primary server update occurs,
**And** retain the acknowledged local proposal/base/operation and current authorized
baseline with Needs attention, pausing dependent unsent edits for later explicit review,
**And** never auto-advance expected revision, last-write-win or relabel conflicting work Synced.
Same-phone conflicts preserve a separate explicitly saved proposal if its storage commits;
if storage fails, retain visible memory and do not claim the proposal was saved.

**AC-6 — Permission changes, account isolation and failures**

**Given** unassignment, lost edit authority, unavailable verification, session change or
quota/write failure,
**When** local Save or server delivery is attempted,
**Then** unassignment alone does not revoke own historical editing,
**And** actual denial/expiry prevents affected edits, unavailability stays distinct,
**And** saved pending proposals remain under original account/Khula without another
account/admin being used to upload them,
**And** safe bounded recovery/guidance retains input or acknowledged work without false success.
Reads/creation-only successes cannot renew the own-edit offline observation.

**AC-7 — Accessible edit behavior and server-backed confirmation**

**Given** phone/computer Edit or a known same-day record,
**When** Save/Cancel and sync complete normally,
**Then** labeled original controls, keyboard/focus/touch behavior and status remain usable,
**And** the user can reopen saved edits offline and read the acknowledged server revision,
**And** locally known Edit existing / Add another uses a working edit action rather than
a dead control; do not claim knowledge of records unavailable offline.

**Edit context:** `GET /api/v1/captures/{id}/edit-context` rechecks current own-read/
own-edit, immutable ownership and original definition; returns current record/revision,
permitted fields and exact scoped observation evidence. Creation eligibility is unrelated.
This renews only verified read/edit scope, not create/all-record rights. Offline uses the
saved capture/definition and valid own-edit observation. No DB lock is held while filling
the form; remote checks precede the short local write transaction.

Extend `/provision` with independently verified `capture.edit.own` observation for
this consumer; create/read successes do not mint it. A locally owned pending create can
be edited under valid own-edit scope, with its edit intent waiting for the create receipt
before materializing the server revision. Edit-context applies once the server record exists.

**Update contract:** `PUT /api/v1/captures/{id}` accepts operation_id, command_version,
expected_revision (positive decimal string), observation_date and answers only. Reject
client owner/actor/audit/child/version selectors. Use exact original validation and
server revision guards. Extend own-scoped operation lookup for capture.edit; a receipt
does not re-execute the edit or substitute current-state reading. Mutation, revision
snapshot, trusted update attribution and receipt share one transaction.

**Local/queue:** Preserve server base separately from the saved overlay and each explicit
operation snapshot. A form pins the base actually reviewed; background downloads cannot
silently upgrade it. An edit following this device's own unresolved confirmed action
waits for that predecessor, but unrelated newer server state causes a conflict. Keep
frozen in-flight payloads and retained descendants on conflict. Add only required edit
metadata/queue support; no automatic unfinished edit store. Completed explicit conflict
proposals are durable saved work, not autosaved drafts.

**Dependencies:** Approved E1 and 2.1; concrete own-edit context/PUT/outcome/error DTOs,
local edit/schema migration, revision/history/fingerprint fixtures and coordinated queue
compatibility. No E3 all-record edit API, E4 producer or E5 management interface is required.
Defining and retaining conflicts here does not claim the next story's resolution UI exists.

**ATDD:** KDG-A02.own-edit, A10.edit-order/reopen, A09.edit-replay/lost-response,
A11.own-revision-conflict, A12.edit-original-version, A16.edit-after-unassignment,
A14.edit-owner-scope, A15.edit-window, A21.edit-attribution and A19.edit-accessible.
First observe the missing behavior at A10.edit-order after implementation approval;
focused validation/transaction/queue tests then affected contract/browser suites follow.
Physical offline-edit checks extend E1 proof on actual installed phones, separately
from emulation. No code, migration, dependency or device action is executed now.

**Impacts:** Scaffold: proven conditional-write/history/edit-queue fixtures with existing
owners, no generic draft/sync engine. Shared UI: explicit-form controls and conflict/attention
status, app-specific semantics retained. Agent/docs: reviewed base vs latest baseline,
original owner/version, Save-only and valid edit scope. Contracts: OpenAPI/TS/queue
versions together. ADR: inherit current auth/revision/history rules and explicit-Save
scope; user-approved A-6 preserves historical editing after child deactivation.

**Review checkpoint:** Scope/criteria approved by the user with C;
normal edit and safe conflict detection work independently of later resolution/admin UI.

### Story 2.3: Review and explicitly resolve conflicting saved changes

As the original owner of a capture with saved changes needing attention,
I want to compare my saved proposal with the current record and choose the result,
So that neither version is silently overwritten or lost.

**Scope:** Own-record local/server conflict comparison, explicit use-current or reviewed
replacement, durable resolution bookkeeping and paused-descendant review. Reuse 2.2's
read/edit-context/PUT/receipt paths. Own multi-device conflicts work without E3 admin UI.
Only explicitly saved changes are retained; edits to the review form remain in memory
until Save, with no autosaved observation draft.

**Requirements:** FR-2/8/9/11/14/15, scoped FR-13/16–18; NFR-1–4.
UX-DR4/5/7/8/9/11–13; AD-2–9. Original owner/creation/child/version stay fixed.

**Acceptance Criteria:**

**AC-1 — Understand the conflict using original questions**

**Given** a retained saved proposal, its reviewed base and a conflict outcome,
**When** the owner opens Needs attention,
**Then** comparison identifies Your saved changes and Current record with original
question labels, observation date, answers/details and permitted editor/time facts,
**And** previously viewed base values are available for context without a technical
revision-number interface or automatic merge,
**And** unchanged fields may be compact while changed values remain readable on phones.
Use actual account/resource scope; no other owner's conflict becomes readable here.

**AC-2 — Obtain the right current state**

**Given** a server conflict,
**When** the user reviews replacement,
**Then** fetch current authorized record/definition and applicable own-edit context,
**And** unavailable/missing/inaccessible current state prevents replacement without
discarding the saved proposal or guessing latest values,
**And** being offline permits viewing retained permitted snapshots but does not claim
fresh server state or authorize a blind server resolution.
A same-phone conflict may review the actual current local saved state offline under
valid local scope, with atomic local revision protection; any later server write remains checked.

**AC-3 — Explicitly keep the current record**

**Given** the reviewed current record and retained saved phone changes,
**When** the owner explicitly selects Use current record and confirms that the saved
proposal will not be applied,
**Then** adoption/decision/queue dispositions commit locally together,
**And** it produces no fake server edit or new server revision,
**And** saved conflicting proposals remain retained as protected local resolution evidence,
not silently erased or described as server-backed. Current own-read is required;
this choice grants no write authority if edit permission is gone.

**AC-4 — Save a reviewed replacement safely**

**Given** fresh permitted current state and valid own-edit authority,
**When** the owner adjusts/selects the complete intended answers/date and Save reviewed
changes is selected,
**Then** validate against the capture's original definition and atomically persist the
reviewed snapshot, new operation ID/expected revision and resolution linkage,
**And** use 2.2's normal current-authorized conditional PUT, never reuse the conflicting
operation ID with changed content or auto-advance the revision,
**And** report only local saved/pending until a matching server acknowledgement,
with original author preserved and actual committed editor/history recorded.

**AC-5 — Intervening change and unresolved outcomes**

**Given** another change after review, lost response, logout or uncertain earlier operation,
**When** resolution is attempted or retried,
**Then** another revision conflict preserves the new saved proposal and returns to review,
**And** unknown operation outcomes are resolved under their original identity before
issuing a competing replacement,
**And** Cancel/close changes no acknowledged proposal, queue or server business state;
unconfirmed review typing has no restart-recovery promise,
**And** same-account fresh authorization/late-response guards prevent cross-account effects.

**AC-6 — Descendants cannot undo resolution**

**Given** several explicit offline edits queued behind the conflicting action,
**When** the head conflict is resolved,
**Then** retained descendants remain paused for explicit review or explicit inclusion
in the reviewed complete result, rather than inheriting a new revision automatically,
**And** use-current or replacement decisions do not silently replay an older queued
snapshot over the chosen result,
**And** local resolution updates preserve every saved proposal/relationship and truthful
pending/attention state when storage or delivery fails.

**AC-7 — Accessible completion and clear failure**

**Given** touch, keyboard or assistive technology,
**When** the owner compares, chooses, validates or retries,
**Then** labeled comparison sections/actions have reachable controls and focus behavior,
**And** repeat conflict/validation/load failure preserves acknowledged proposals and
distinguishes denied access from unavailable verification,
**And** only a completed adopted-current decision or matching replacement acknowledgement
reports resolution success; no server-backup claim is made for retained local branches.

**Resolution contract:** Do not add a generic conflict service or a privileged override
endpoint. Fresh own-read supplies current snapshots; own-edit context is needed for
replacement, followed by existing revision-checked PUT with a new action identity.
User review never holds DB locks. The open review pins the revision actually shown;
subsequent refresh does not silently change the submitted expectation.

Local resolution identifies the capture, saved branch/operation, reviewed local/server
revision, explicit choice, selected complete result and descendant dispositions. Commit
that metadata plus current local representation/new pending action atomically. Retain
former proposals/base references under the same account/Khula scope until a declared
retention policy permits cleanup. They are saved conflict work, not autosaved typing or
guaranteed server history. Choosing current cannot undo a previously committed edit.

Same-phone resolution applies the same reviewed-local revision/CAS guard and current
read/edit local observations; a new server conflict still goes through normal review.
Multiple-window claims and session generations prevent duplicate resolution effects.
An uncertain replacement retains its immutable input/operation; subsequent typed changes
do not mutate it. Missing server record never authorizes deletion of local work.

**Dependencies:** Approved E1/2.1/2.2; concrete local conflict/decision/descendant schema,
authority/error/outcome compatibility and retention applicability. No administrator
all-record edit UI, new published-version producer or E5 portal is needed. A local
conflict branch's physical-storage limits remain the declared PWA limits.

**ATDD:** KDG-A11.own-conflict-use-current/replacement/intervening/descendants,
A09.resolution-lost-response, A10.resolution-local-cas, A14.resolution-owner,
A15.resolution-session, A12.resolution-original-version and A19.resolution-accessible.
First observe expected failure for A11.own-conflict-replacement after implementation
approval; then focused state/transaction/queue tests and affected browser/API suites.
Use actual same-owner multiple-device fixtures, so no E3 API is needed. Physical checks
extend the installed protocol; no runtime or device work occurs in planning.

**Impacts:** Scaffold: prove explicit revision/branch/queue-resolution fixtures through
existing owner, not a merge engine. Shared UI: comparison/review/status composition
with app-owned question/date semantics. Agent/docs: no auto-rebase, retained saved work
versus unsaved review typing and exact claims. Contracts: local resolution/queue and
generated API errors together; no new shared service API. ADR: inherited explicit
revision/current-auth/history rules and app Save-only scope; accepted ADRs unchanged.

**Review checkpoint:** Scope/criteria approved by the user with C.
Current/read selection and replacement have separate authority; no override is implied.

### Story 2.4: Prove simple offline capture history and editing

As the original owner of a capture,
I want a simple history of my observations with reliable offline editing,
So that I can find and correct saved observations without managing versions.

**Scope:** Integrated E2 acceptance/device proof and simple capture details showing
observation date and answers, with compact sync feedback when needed. Attribution
remains stored internally; administrator audit presentation belongs to E3. Reuse
2.1–2.3; no revision browser, revision-download interface or general local history table.
Local storage contains current captures, necessary original questionnaire definitions,
pending operations/reviewed bases and conflict proposals. Server attribution/immutable
business evidence remains internal, separate from this simple user interface.

**Requirements:** FR-8/9/11, verification of E2 FR-2/6/13–18; NFR-1–5.
UX-DR4/7–9/11–14; AD-2–9. No unfinished observation input persistence.

**Acceptance Criteria:**

**AC-1 — Simple observation history without routine audit metadata**

**Given** an owned saved capture and valid applicable read authority,
**When** the user opens History and record details,
**Then** show the observation date and answers using original questionnaire labels,
without routinely displaying creator/modifier names or audit timestamps,
**And** show compact pending/attention feedback where needed; a completed local Save
still clearly says Saved on this phone and is never presented as a server backup,
**And** no revision catalogue, revision download, restore or version-selection action
is presented. Authenticated authors/editors cannot be changed by the form.

**AC-2 — Offline current records, not downloaded revision archives**

**Given** locally saved or authorized downloaded observations and their definitions,
**When** the installed app reopens offline within valid read scope,
**Then** the current local saved observations remain available through ordinary history,
**And** older observations never downloaded are unavailable offline with a simple
notice when needed; no per-revision missing-history prompts are introduced,
**And** conflict comparison alone exposes retained competing saved changes as in 2.3.
Required original questionnaire definitions stay internal; users do not select versions.

**AC-3 — Minimal local state and safe refresh**

**Given** pending edits/conflicts and a server refresh or app update,
**When** records are refreshed or local schema changes are applied,
**Then** retain current saved work, required bases, frozen operation snapshots and
conflict proposals under the correct account/organization,
**And** no complete server revision archive is downloaded or added to local storage,
**And** verified read checks do not renew edit/create authority, and failed storage or
updates cannot claim success or delete unsynchronized work.

**AC-4 — Automated E2 acceptance evidence**

**Given** the delivered E1 and 2.1–2.3 behavior with synthetic accounts/records,
**When** focused contract/browser/concurrency scenarios run,
**Then** verify own/foreign scope, 30-day partial downloads, offline reopen and edits,
ordered create/edit retries, original-version rendering, local/server repeated conflicts
and paused descendants, unassignment/inactive-child history and exact session windows,
**And** server history/receipts show one committed effect per action with original author,
**And** record exact commands/results and limitations; automated emulation is not physical proof.
Use isolated immutable earlier-definition fixtures; E4 publishing is not a dependency.

**AC-5 — Installed Android and iPhone E2 proof**

**Given** synthetic data and the reachable isolated HTTPS app used for E1 proof,
**When** the E2 protocol runs on actual installed Android Chrome and iPhone Safari PWAs,
**Then** download history, disconnect, edit/Save, fully close/reopen and view the saved
edit; reconnect and verify the server revision and recorded editor,
**And** use the same account on a second device to create a concurrent edit, then review
and resolve the first device's conflict without losing saved changes or replaying an
older dependent edit over the decision,
**And** record device/OS/browser/build/test IDs, outcome and safe references separately
from controlled quota/clock/migration tests. No sensitive observation screenshots/traces.

**AC-6 — Accessible history and evidence closure**

**Given** keyboard, zoom and installed-phone assistive technology,
**When** history/record details, Edit and conflict choices are used,
**Then** labels, focus, touch targets and local/pending/synced/attention states are usable,
**And** the E2 evidence maps covered requirements to approved stories/test results and
explicitly lists any remaining issue, unsupported device or unexecuted physical check.
A failed or missing required device result prevents claiming this story's proof complete.

**Persistence boundary:** Use existing capture/history/detail, edit and conflict
contracts; withdraw the proposed revision-list API from MVP. A server revision token
is internal concurrency metadata, not a user-visible version. Retain server-side
immutable change evidence already required by the agreed scope and ADR-0025; four
attribution fields summarize the latest change and cannot replace that evidence.
Offline support alone does not require a full local or server snapshot history.

**Platform ownership:** Existing platform scaffold/UI owners provide proven bounded
IndexedDB transaction/schema-migration helpers, account/organization partitions,
queue/retry/idempotency plumbing, revision-guard/conflict primitives, sync status and
PWA update/device-test fixtures where domain-neutral. Promote with first consumers
and tests; do not create a new runtime offline service, parallel generator or generic
history engine. KDG retains questionnaires/answers, child assignment, capability checks
and comparison presentation. Shared contract changes await agreed Leave handoff.

**Dependencies:** Approved E1 and 2.1–2.3, actual installed-device environment/test access,
concrete existing record/queue/conflict fixtures. No E3 admin, E4 editor, E5 assignments
or People integration required. Execution waits for planning/implementation approval.

**ATDD:** KDG-A21.detail-attribution/immutable-evidence, A14.detail-owner-scope,
A18.current-record-cache, A12.detail-original-definition, A15.detail-read-window,
A10.E2-chain-reopen, A09.E2-lost-response, A11.E2-own-conflict,
A16.E2-historical-edit-policy, A17.E2-pending-upgrade and A19.E2-accessible.
First observe missing A18.current-record-cache after Build approval; focused read/cache tests
then the affected E2 suites. Extend the physical E1 protocol with AC-5. No executable
commands or passing results are invented during planning.

**Impacts:** Scaffold: prove/promote minimal local transaction/migration, partition,
queue/revision/conflict and update/test helpers with existing platform owners; no
universal offline/history engine. Shared UI: simple observation details and compact sync states, with
app-owned questionnaire/conflict content. Agent/docs: no offline revision archive;
original definition vs current observation vs pending/conflict state remain distinct.
Contracts: remove proposed revision-list route; preserve existing write/audit contracts.
ADR: inherit attribution, immutable consequential evidence and Save-only rules; no
accepted shared ADR changes. Record device and automated evidence separately.

**Review checkpoint:** Revised scope/criteria and conflict responsibility approved
by the user with C. E2 coverage and separate epic-completion confirmation follow.

## Epic 3: Review and correct captures across Khula

Deliver online administrator organization-wide review/edit/audit. The capture PWA
remains own-only for both roles; no offline all-record authority or download.

### Story 3.1: View authorized Khula observations and administrator audit details

As a questionnaire administrator,
I want to view organization observations and who recorded or changed them,
So that I can review facilitator captures without putting audit details in the capture form.

**Scope:** Responsive administrator history/detail and a compact online audit section;
current `capture.read.all` checks and online organization history. Reuse E2 record/history components with a distinct authority
boundary. No administrator edit action until the next story, questionnaire/assignment
management, exports, dashboards or general revision browser.

**Requirements:** Administrator read portion FR-2/8, FR-11/13/15–17; NFR-1–4.
UX-DR4/7/8/10–13; AD-2/3/4/7/8/9. Questionnaire administrator is an app role, not
platform organization administration or employment.

**Acceptance Criteria:**

**AC-1 — Current all-record authorization**

**Given** authenticated fixed-Khula membership, app admission and explicit read.all,
**When** the administrator requests history or a record,
**Then** the API checks current authority and returns only that organization's records,
**And** capturer-only, membership-only and platform-admin-only accounts cannot use this
all-record surface or enumerate another author's records by ID, query or pagination,
**And** client owner/organization selectors never supply authority. Scope follows
capability at the action boundary; no silent own-scope fallback after all-read denial.

**AC-2 — Simple responsive review**

**Given** permitted server-backed observations,
**When** the administrator opens the portal on phone or computer,
**Then** show observation date, child and original capturer with ordinary record details,
**And** render answers under the exact original questionnaire, not the latest definition,
**And** distinguish genuinely empty results from failed/partial downloads,
**And** new facilitator captures appear only after their devices synchronize and an
administrator refresh succeeds. No promise to see never-synchronized phone work.
The ordinary capture interface retains its approved simple date/answers/status display.

**AC-3 — Audit stays on the administrator surface**

**Given** fresh read.all and a permitted record,
**When** the administrator expands Audit details online,
**Then** show original creator/creation time and latest committed modifier/modification
time, with a bounded list of committed create/edit events and actual editor/server time,
**And** original author is preserved, no-op/retry does not create a fictitious event,
**And** operational logs, credentials, payload dumps and unrelated records are excluded.
No snapshot-version picker, restore, export or audit download to phones. Audit list is
read-only; answers already appear in record details and need not be duplicated in it.

**AC-4 — Online administrator / own-observation PWA split**

**Given** Louwnique holds questionnaire administrator and own-capture permissions,
**When** using the PWA or the administration portal,
**Then** the PWA offers capture and My observations under own scope, including offline,
**And** organization-wide review/audit in the responsive portal requires internet and
current read.all; no all-record download, persistent cache or offline authority is issued,
**And** losing connectivity shows unavailable/reconnect feedback without a false empty
list or deleting saved own observations. The portal does not promise offline launch.
No all-record business response is cached by the service worker or IndexedDB.

**AC-5 — Role loss, account changes and safe refresh**

**Given** revoked all-read, membership/app disable, session expiry or another
account signing in,
**When** current verification or cached rendering is attempted,
**Then** affected all-record access is locked and no prior-user or lost-role records render,
**And** unavailable verification is distinct from explicit denial; organization-wide
review never continues using a seven-day offline authorization observation,
**And** retained data does not confer rights or overwrite/delete pending/conflicting work.
Late responses and background refresh are bound to the original account/scope/session;
no own-read check authorizes organization-wide portal data.

**AC-6 — Accessible review and boundary evidence**

**Given** keyboard, zoom, phone touch or assistive technology,
**When** history, details and optional Audit details are used,
**Then** labels, focus, pagination/loading/failure feedback and responsive layout are usable,
**And** API/browser/real runtime-role tests prove foreign-owner allowed only under
current all-read, cross-org denied, original labels/owner retained and role-loss locking.
Automated scenarios and actual installed-device extension results are recorded separately.

**Contracts:** Extend existing history/detail handlers with explicit own/all authorization
modes and bounded queries, never permission inferred from a client role or actor ID.
Check read.all on every portal request; provisioning exposes no offline read.all
observation. No all-edit authority is minted here. Use existing Keyset pagination/private
no-store responses, original-definition retrieval; own-only PWA caching remains separate.
Audit events use a narrow record-owned online read such as
`GET /api/v1/captures/{id}/audit`, protected by current read.all on every bounded page.
Concrete DTO/cursor/actor-display contract and server evidence minimization gate Build.
This is an app endpoint over app-owned evidence, not a new shared audit service. No
external waits under business locks or cross-service table reads.

**Dependencies:** Approved E1/E2 and existing shared Identity/Access prerequisites;
read.all registry/caller/schema fixtures, online portal context, actor-display
mapping and bounded audit DTO. These need owner closure before Build; E4 questionnaire
editor and E5 assignments/onboarding UI are not prerequisites. Controlled setup may
supply synthetic additional facilitators and children for acceptance proof.

**ATDD:** KDG-A02.admin-read/own-denied, A14.admin-read-org/account,
A15.admin-online-session, A16.admin-read-role-loss, A18.admin-history-partial,
A12.admin-original-definition, A21.admin-audit-attribution and A19.admin-review-accessible.
First observe missing A02.admin-read after approval, then focused authorization/read/
portal/audit tests and affected API/browser/runtime-role suites. No implementation or
physical-device execution occurs during planning.

**Impacts:** Scaffold: prove scoped pagination/attribution-read and own-only persistence
patterns with existing owners. Shared UI: responsive record list, optional audit section
and scope-aware state only after proven reuse; KDG labels remain application-owned.
Agent/docs: platform roles vs app capability, own vs all, portal vs offline PWA, no
central intake of phone proposals. Contracts: exact read mode/audit DTO/errors/cache
metadata and generated types together. ADR: inherit scoped Access, actor attribution,
privacy and bounded offline policy; no accepted platform contracts/ADRs changed here.

**Review checkpoint:** Revised split/scope approved when the user confirmed the split
and requested Next.
Administrator editing/conflict handling follows as an independently reviewed increment.

### Story 3.2: Correct authorized observations online without overwriting another editor

As a questionnaire administrator,
I want to correct authorized Khula observations online with Save/Cancel and conflict review,
So that corrections preserve original ownership and other facilitators' saved work.

**Scope:** Online portal all-record edit context, whole-form Save/Cancel, conditional
update/receipt recovery and explicit administrator conflict review. Reuse E2 validation,
revision/idempotency and comparison patterns, adding distinct all-record authorization
and editor attribution. No offline organization-wide editing or local record archive.

**Requirements:** FR-2/8/9/11/15–17; NFR-1–5; UX-DR5/7/8/9/10/12/13; AD-2–10.
No questionnaire editor, assignment management, supervisor or People dependency.

**Acceptance Criteria:**

**AC-1 — Current administrator authority and original form**

**Given** current Khula membership/app admission and explicit read.all/edit.all,
**When** the administrator opens Edit for a permitted observation,
**Then** the backend returns editable date/answers under the original questionnaire,
**And** child, questionnaire version, original owner and creation attribution stay fixed,
**And** membership or organization-platform role alone grants no edit permission.
No current child assignment/new-create eligibility is required for historical correction.
The form pins the revision actually shown, not one later refreshed in the background.

**AC-2 — Explicit online Save/Cancel and trusted attribution**

**Given** a complete original-version form,
**When** Save succeeds with current edit.all and matching revision,
**Then** validate and conditionally update date/answers with actual administrator actor/
server time, immutable business evidence and operation receipt in one short transaction,
**And** preserve original capturer/creation facts and record exactly one effect per action,
**And** no-op produces no fictitious update/history; Cancel causes no committed change.
No autosave or extra administrative draft system. Offline/disconnected forms cannot
claim a server save; visible unsaved typing stays in memory with clear feedback.

**AC-3 — Facilitator-versus-administrator conflicts**

**Given** administrator and facilitator edits based on the same server revision,
**When** one commits and the other attempts Save/sync,
**Then** the stale update is rejected without overwriting the committed record,
**And** the editor holding the conflicting proposal explicitly compares and chooses
Use current record or Save reviewed changes with a new operation ID and reviewed revision,
**And** original author stays unchanged and actual successful editor appears in audit.
A fresh change during review repeats the conflict; no first-reader priority or privileged
force-overwrite. Capturer phone proposals stay in their own partition; administrators
cannot retrieve never-synchronized work or resolve it by impersonating that capturer.

**AC-4 — In-memory online conflict review**

**Given** an administrator Save rejected for a stale revision,
**When** the portal shows the current record beside the attempted answers,
**Then** retain the attempted answers and reviewed base in memory while the form stays open,
**And** let the administrator choose current or save a reviewed replacement after fresh
current access checks; another intervening change returns to review,
**And** closing/reloading may discard uncommitted input; no recovery promise is made.
No server conflict-proposal table, resolution draft, autosave or proposal-retrieval API.
No other-author record/proposal is written to IndexedDB or business-response caches.
The capturer's explicitly saved offline pending edits/conflicts remain durable under E2.
Normal operation receipts recover uncertain committed-save outcomes; they are not drafts
and never report a rejected conflict as a committed edit.

**AC-5 — Unknown outcomes, role loss and isolation**

**Given** a lost response, revoked edit.all, expired session, outage or account change,
**When** the administrator retries or reauthenticates,
**Then** resolve the original immutable action through current authorized operation lookup
before issuing a competing edit; never reuse its ID with changed answers,
**And** denial prevents edits; unavailable checks do not imply permission or lost work,
**And** no fallback uploads another user's pending edit or uses own authority on their record,
**And** late responses cannot render into another account's portal/session.
Read-only recovery can inspect its original receipt where allowed without re-executing
an edit. No authorization or external wait occurs under business write locks.

**AC-6 — Accessible end-to-end cross-author proof**

**Given** synthetic capturer/administrator accounts and original-version fixtures,
**When** API/concurrency/browser scenarios and applicable device checks run,
**Then** verify online correction, preserved ownership/audit, both conflict orderings,
repeated conflicts, lost response, own-only PWA caching and revoked/cross-org denials,
**And** responsive Save/Cancel/comparison controls work with keyboard, touch and zoom,
**And** distinguish automated results from actual installed-phone checks. A facilitator
pending edit survives administrator correction and surfaces its conflict on sync.

**Contract increment:** Extend edit context/PUT and operation lookup with current
read.all/edit.all at the action boundary, retaining typed scope, immutable target/owner
and original questionnaire validation. Use explicit portal command context, never
mint offline all-edit observations. Administrator attempted answers/reviewed base stay
in memory. Successful writes commit required audit/receipt atomically; conflict commits
no primary capture update or input snapshot. Concrete success/conflict/outcome/error
schemas must close before Build with existing platform write/error owners. No new
conflict service, server proposal schema or draft lifecycle.

**Dependencies:** Approved E1/E2 and 3.1; all-edit registration/consumer contracts,
in-memory review/unknown-outcome fixtures, actor attribution and original-operation
recovery fixtures. No E4 editor or E5 portal needed. Own-only PWA delivery remains
unchanged; domain-neutral conditional-write/conflict fixtures may be promoted through
existing platform owners after agreed shared handoff and first-consumer proof.

**ATDD:** KDG-A02.admin-edit, A11.facilitator-admin-both-orders/repeated,
A09.admin-lost-response/replay, A14.admin-edit-org/account,
A15.admin-edit-session, A16.admin-edit-role-loss, A12.admin-edit-original,
A21.admin-owner/editor, A17.no-all-record-offline-cache and A19.admin-edit-accessible.
First observe missing A02.admin-edit after Build approval; focused conditional update/
review/authorization tests then affected API/runtime-role/browser concurrency suites.
No code, migration or physical execution occurs during planning.

**Impacts:** Scaffold: bounded conditional-write/operation/conflict-review fixtures
through existing owners, no generic draft/offline engine. Shared UI: proven explicit
form, comparison and save-state patterns; KDG questions stay app-owned. Agent/docs:
online all-record correction, original owner vs editor, durable phone edits vs
in-memory online input. Contracts: all-edit/context/conflict/outcome
DTOs and generated types together. ADR: inherit short transactions/current access,
attribution/error/release rules; accepted shared decisions unchanged. No server
conflict-input retention policy/schema is introduced.

**Review checkpoint:** Revised in-memory conflict scope approved when the user said
Thanks, next after the server-preservation proposal was withdrawn. No autosave/draft
or close/reload recovery of uncommitted administrator input is promised.

## Epic 4: Evolve questionnaires without rewriting historical captures

Deliver a small online working-copy editor and explicit immutable publication.
Capture controls remain Afrikaans and exact original definitions remain usable.

### Story 4.1: Edit and save a questionnaire draft online

As a questionnaire administrator,
I want a small online editor for a saved questionnaire draft,
So that I can prepare wording and question changes without changing live or historical observations.

**Scope:** Responsive draft editor and authorized start/read/whole-form Save/Cancel.
Initial published questionnaire remains live. Draft configuration is persisted only
on explicit Save; this is the agreed questionnaire draft, not an observation autosave
or administrator conflict-recovery draft. Publish follows in 4.2 and is not required
for this editor to save/reopen prepared content.

**Requirements:** FR-10; stable-ID/draft immutability portion FR-11; editor FR-5,
FR-2/12/16/17; NFR-1–5. UX-DR5/7/10/12/13; AD-2/3/5/9/10.
Afrikaans initial content remains exact; no clinical meaning for rating values 2–4.

**Acceptance Criteria:**

**AC-1 — Current authorized draft preparation**

**Given** current fixed-Khula admission and explicit questionnaire.manage,
**When** the administrator explicitly starts or opens the questionnaire working draft,
**Then** the API checks current authority and returns a draft with stable identity/revision,
**And** starting from the current published definition copies editable content without
mutating its immutable version or historical capture references,
**And** capturers, membership-only accounts and other organizations cannot access it.
No Auth/Access grants, People facts or raw cross-owner table writes are introduced.

**AC-2 — Limited question editor**

**Given** an open working draft,
**When** questions are added, reordered, retired or edited,
**Then** support only rating integers 1–5 with endpoint labels, Ja/Nee with optional
Ja details, and plain text; wording and required/optional status are editable,
**And** wording/reorder/required-status changes retain stable question IDs,
**And** new questions or incompatible type replacement get new IDs; retired questions
leave future draft content without disappearing from old published definitions,
**And** no arbitrary branching, formulas, analytics, rich HTML or scale interpretation
is added. Retiring/replacing is explicit and clearly affects future publication only.

**AC-3 — Whole-form Save/Cancel and reopen**

**Given** local in-memory editor changes,
**When** Save or Cancel is selected,
**Then** Save validates and writes the complete draft atomically with current authority,
expected revision, actor/time, operation identity and required compact change evidence,
**And** report Draft saved only after server confirmation and reopen the saved definition,
**And** Cancel discards current unsaved changes without changing the saved draft or live version.
No selected-field autosave, offline draft queue, forced setup dependency or automatic
publication. Closing/reloading before Save can lose current typing.

**AC-4 — Safe concurrent editing and uncertain outcomes**

**Given** two administrators or two tabs editing the same draft revision,
**When** one saves and the other attempts a stale Save,
**Then** reject the stale write, keep attempted changes in memory while the form stays
open and offer review against the current draft without silent overwrite or auto-rebase,
**And** a reviewed replacement uses a new operation ID and the actually reviewed revision,
**And** normal operation receipts recover a lost Save response without a second effect.
No server conflict-proposal store or resolution autosave; session/account loss prevents
unauthorized rendering/retry. A new concurrent change requires review again.

**AC-5 — Validation and isolation without changing the live questionnaire**

**Given** a manipulated or invalid definition or unavailable server,
**When** start/read/Save is attempted,
**Then** reject unknown types/configuration, duplicate/invalid IDs and unsupported values
with safe field errors while preserving visible input as appropriate,
**And** enforce owned-organization structural references and actor attribution on every path,
**And** denial/outage is distinct from a saved or published outcome,
**And** published capture entry and old-version history continue using unchanged definitions.
Concrete limits remain contract-readiness proposals (50 questions, 500-character labels,
5000-character text/details, 128 KiB command), checked together in API/editor fixtures.

**AC-6 — Accessible administrator editor and evidence**

**Given** phone/computer touch, keyboard, zoom or assistive technology,
**When** the administrator edits/reorders questions and saves/cancels,
**Then** labeled fields, explicit move-up/down controls, focus and required/error feedback
are usable without drag-only interactions,
**And** automated API/component/browser tests prove role/org denial, stable-ID rules,
Save/Cancel, concurrent save/replay and immutable-live-version protection,
**And** actual responsive/assistive checks are recorded separately from emulation.

**Contracts:** App-owned draft start/read/update endpoints with exact questionnaire ID,
operation identity and expected revision. Current questionnaire.manage is checked on
every request; reject caller audit/org selectors. For the small MVP editor, propose one
editable working draft per questionnaire: explicit start creates/resumes atomically
without resetting existing values (opt-in ADR-0034), and distinguish an old retry from
an explicit new start (ADR-0033). No automatic start on entering another surface.
Concrete draft lifecycle/start/outcome/validation DTO and uniqueness/error fixtures gate
Build. Preserve current published version separately; create only draft persistence
needed here. No generic survey builder or second definition engine.

**Dependencies:** Approved E1–E3; questionnaire.manage registry/consumer schema, owned
write/revision/attribution helpers and concrete draft validation/outcome contracts.
No 4.2 Publish, E5 assignments or shared employment prerequisite. Existing version
fixtures prove immutability without a live publication producer.

**ATDD:** KDG-A13.editor-role/Save-Cancel/reorder-retire-types,
A12.editor-stable-IDs/published-unchanged, A09.editor-save-replay,
A11.editor-concurrent-save, A14.editor-org/account, A15.editor-session,
A21.editor-attribution and A19.editor-accessible-reorder.
First observe missing A13.editor-Save-Cancel after Build approval, then focused
validation/lifecycle/conditional-write tests and affected API/runtime/browser suites.
No dependencies, code, migration or device action is executed during planning.

**Impacts:** Scaffold: prove explicit configuration/revision/start/replay fixtures with
existing owners; no general draft runtime or generator. Shared UI: promote proven
whole-form editor/reorder/error composition; question semantics stay KDG/Survey-owned.
Agent/docs: configuration draft vs observation Save-only, stable IDs vs order/wording,
saved draft vs published live version. Contracts: schema/lifecycle/errors/generated
TS adapters together. ADR: inherit current auth/attribution, ADR-0033/0034 opt-in and
ADR-0051 configuration Save/Cancel; accepted shared ADRs unchanged. Concrete working-
draft lifecycle/limits must be closed before Build, with no universal draft mandate.

**Review checkpoint:** Scope/criteria approved when the user said Happy, next,
including explicit working-copy Save/Publish and large Ja/Nee choices in capture.
Saving prepares a questionnaire; it never changes the published version used for capture.

### Story 4.2: Publish a questionnaire without changing older observations

As a questionnaire administrator,
I want to publish my saved working copy as the next questionnaire,
So that new captures use my changes while old and offline observations remain accurate.

**Scope:** Explicit online Publish, immutable definition/current-published-pointer update,
working-draft closure and actual producer/consumer version-compatibility proof. Reuse
4.1 editor and E1–E3 capture/history/sync. No observation migration, administrator
autosave, generic survey engine or automatic creation of another working draft.

**Requirements:** FR-10/11; version-compatible FR-5/8/9/13/14/18 and scope FR-2/16/17;
NFR-1–5; UX-DR5/7/10–14; AD-2–10. Capture remains Afrikaans; the editor may label
the boolean type Yes/No, while initial capture controls remain large Ja/Nee choices.

**Acceptance Criteria:**

**AC-1 — Explicit publication of a saved working copy**

**Given** current questionnaire.manage and a saved valid working draft,
**When** the administrator reviews that saved content and explicitly selects Publish,
**Then** the backend rechecks authority, draft revision/editability and current published
state, validates the complete supported definition and publishes that exact saved content,
**And** unsaved editor typing is not silently included; save it first before publication,
**And** ordinary Save or opening the editor never publishes. Required labels/type
configuration must be valid; no invented clinical descriptions for rating values 2–4.

**AC-2 — Atomic immutable publication and guarded lifecycle**

**Given** a matching open working-draft revision and publish operation identity,
**When** publication commits,
**Then** immutable definition/identity/hash, current-published pointer, draft closure,
trusted actor/UTC attribution, required evidence and compact receipt commit together,
**And** the same operation replay returns the same version without a duplicate publication,
**And** concurrent publication/stale save cannot mutate the published version or resurrect
the closed draft; any new working copy requires an explicit new Start action.
Old retry IDs remain bound to their original draft/action. No external waits under locks.

**AC-3 — Offline devices may continue using an older version**

**Given** a phone provisioned with V1 while the administrator publishes V2 online,
**When** the phone captures offline and later synchronizes,
**Then** its V1 captures are accepted under current authority using exact V1 validation,
**And** preserve their original version/questions/answers without migration to V2,
**And** publication alone never rejects pending old-version creates/edits. Missing or
foreign-organization versions are rejected safely, not replaced by the latest version.

**AC-4 — New entries adopt downloaded content, open forms stay pinned**

**Given** an in-memory entry or saved pending observation using V1,
**When** V2 downloads successfully into the same authorized account/Khula setup,
**Then** commit the definition and applicable latest-version selection atomically,
**And** next new capture uses V2 while the open entry/pending observations remain V1,
**And** interrupted or failed download leaves the previous usable selection intact.
No version picker or silent remapping in capture. Definitions referenced by saved,
pending/conflicting captures remain retained through cache cleanup and updates.

**AC-5 — Historical editing keeps original semantics**

**Given** V2 wording/order/required status changes, retired questions or new question IDs,
**When** a V1 observation is viewed or edited by its owner or online administrator,
**Then** render and validate exact V1 wording/order/required rules/scale/details behavior,
**And** preserve stable ID semantics and existing owner/child/version attribution,
**And** ordinary revision-conflict rules still apply; publishing is not authority to
rewrite an old observation or bypass read/edit permissions.

**AC-6 — Publication and actual installed-device compatibility evidence**

**Given** isolated synthetic V1/V2 questionnaire and facilitator/admin fixtures,
**When** API/browser/concurrency/upgrade and installed Android/iPhone checks execute,
**Then** prove immutable publish/replay, stale save after publish, role/org denial,
V1 capture while offline, V2 download/new-entry selection, pinned open entry and V1 edit,
**And** verify large Afrikaans Ja/Nee controls, required/optional/new text and conditional
Ja details follow each definition with accessible labels/focus/validation,
**And** document exact automated commands/results and physical builds/devices separately.
Use the actual 4.1/4.2 publishing producer for this evidence, not merely typed fixtures.
No device or runtime work is executed in planning.

**Contracts:** Publish takes questionnaire/draft identity, operation ID/command version,
expected draft revision and reviewed current publication state; it never accepts client
publication actors/audit fields. Server allocation of version identity and immutable
content/current pointer update is structural and atomic. Draft save checks revision and
open lifecycle together; late retries cannot reopen a published working copy. Read
latest definition via existing setup/download paths, with old-version retrieval retained.
Concrete lifecycle/publish/outcome/definition compatibility DTOs and constraint/error
fixtures gate Build; generated frontend types and original validation evolve together.

**Dependencies:** Approved E1–E3 and 4.1; current manage capability/owned write/outcome
helpers, concrete publish lifecycle and supported definition/queue schemas. No E5 child
management or whole Leave completion. Review first-consumer shared patterns with their
existing retained owners under the acknowledged handoff; selected shared refinements
are linked in shared-prerequisites.md and do not authorize implementation.

**ATDD:** KDG-A13.publish-role/immutable/lifecycle,
A12.actual-publish-offline-V1/open-pinned/new-V2/historical-edit,
A09.publish-replay/lost-response, A11.publish-concurrency,
A14.publish-org/account, A15.publish-session, A17.version-retention-upgrade,
A21.publish-attribution and A19.published-controls-accessible.
First observe missing A13.publish-immutable after Build approval; focused lifecycle/
validation/transaction tests then affected API/runtime/browser/version suites. Extend
installed-device protocol with actual publication while the phone is disconnected.

**Impacts:** Scaffold: proven immutable snapshot/publication/lifecycle/operation fixtures
through existing owners; no generic form runtime. Shared UI: explicit Save/Publish and
accessible question controls only when proven reusable. Agent/docs: current published
selection vs pinned capture definition, start after publication vs stale retry, no
silent migrations. Contracts: publish/lifecycle/error/generated types and supported
local/queue definitions together. ADR: inherit immutability/attribution/current auth,
short transactions, late-save protection and queued-work/release compatibility; no
accepted platform ADR changed. Record exact version/device evidence in delivery.

**Review checkpoint:** Scope/criteria approved by the user with C.
A new publication changes future downloaded capture forms, not historical observations.

## Epic 5: Keep daily capture reliable as children and facilitators change

Complete online children/assignments and remaining pilot reliability without duplicate
Identity/Access/People infrastructure or unnecessary offline administrator features.

### Story 5.1: Manage children online without losing their observations

As a questionnaire administrator,
I want to add children, correct their display names and mark them active or inactive,
So that capture choices stay relevant while earlier observations remain intact.

**Scope:** Small responsive online child list and explicit create/edit Save/Cancel,
including active/inactive status. Reuse child ownership/UUIDs/bootstrap facts from E1.
No child deletion, full profile, clinical/employment records or facilitator assignment
editor; assignment management follows in 5.2. No offline administration queue.

**Requirements:** Child-management FR-12; child eligibility FR-2/4 and historical
FR-8/13/16; NFR-1–5. UX-DR2/7/10–13; AD-2/3/4/7/9/10.
Sinehgomso remains the initial child, not a person account or respondent identity.

**Acceptance Criteria:**

**AC-1 — Current child-management permission and fixed organization**

**Given** current Khula membership/app admission and explicit child.manage,
**When** the administrator opens the child list or creates/updates a child,
**Then** the backend checks exact action authority and returns/writes only Khula children,
**And** capturer-only and membership/platform-role-only accounts cannot manage children,
**And** organization/actor selectors cannot change scope or attribution.
Child existence grants neither facilitator access nor questionnaire administration.

**AC-2 — Minimal explicit form and stable identity**

**Given** a new child or an existing permitted child,
**When** the administrator enters a display name/status and selects Save or Cancel,
**Then** Save validates and atomically commits the complete change with stable child ID,
server actor/time, required compact evidence and operation receipt,
**And** existing child identity/org never changes when correcting the name,
**And** Cancel performs no mutation; no autosave, full child profile or offline setup.
Do not silently merge children by display name; identical names are not identity proof.
An idempotent create retry cannot create a second child.

**AC-3 — Ordinary deactivation preserves pending and historical observations**

**Given** a child with assignments and existing observations,
**When** the administrator explicitly saves inactive status,
**Then** preserve child identity, captures, original questionnaire references and attribution,
**And** exclude the child from refreshed new-capture choices,
**And** accept pending offline observations based on previously provisioned eligible-child
setup if current membership, app/capture permission and applicable assignment still pass;
ordinary inactive status alone does not reject or discard that work,
**And** current authorized own/all historical reads/edits remain valid without requiring
new-create eligibility. No cascade deletion or disguised record retirement.
Offline phones cannot learn deactivation until online refresh/sync checks current state.

**AC-4 — Reactivation and capture choices**

**Given** an inactive child restored to active by an authorized explicit Save,
**When** current eligible children are refreshed,
**Then** the administrator may create their own captures for it under create.all,
**And** capturers see it only with valid create.assigned and current active assignment,
**And** one eligible child is displayed automatically; additional eligible children
use selection, without an organization switcher or invented access grants.
Reactivation alone does not reactivate a retired assignment or revoked platform grant.

**AC-5 — Concurrent change and failure recovery**

**Given** expected child revision, immutable operation identity and current child.manage,
**When** another editor changed the child or the response is interrupted,
**Then** stale Save is rejected without silent overwrite, with attempted input retained
in memory for review while the form remains open,
**And** lost outcomes use the original authorized operation receipt/retry without duplicate
changes/evidence; reviewed changed content uses a new action identity,
**And** outage/denial/session loss is distinct from saved/empty and another account cannot
receive late responses. No server conflict-input store or restart-recovery promise.

**AC-6 — Accessible management and actual permission-change proof**

**Given** synthetic active/inactive children and own-capture/admin fixtures,
**When** contract/browser/concurrency and applicable installed-phone scenarios run,
**Then** prove add/name edit/inactivate/reactivate, role/org negatives, replay and stale save,
**And** verify refreshed choices, pending observations synchronize after ordinary
deactivation without a manual deletion task, and historical
own/admin editing after inactivation under unchanged permissions,
**And** responsive labeled Save/Cancel/status controls and focus/touch/keyboard work.
Record automated and physical evidence separately; no tests are executed in planning.

**Contracts:** App-owned online list/create/update under child.manage, using stable UUID,
operation identity/command version, expected revision for updates, display name and
active status only. Protect immutable org/ID and trusted attribution. Reuse existing
child schema/read eligibility, operation recovery and backend structural/revision rules.
Exact name bounds, status-change evidence/DTO/error fixtures gate Build; neither name
uniqueness nor generic People/person adoption is introduced. Remote Access checks stay
outside short writes; child state is protected with capture-create coordination.
Concrete offline-create eligibility evidence must distinguish previously provisioned
active-child setup from a fresh inactive-child request. Verify stored/issued scope and
child identity; a client pending flag or phone date alone proves neither eligibility nor
when Save occurred. Do not claim the server knows an offline Save predates deactivation.
Define the compatible command/provision reference before Build; this is domain evidence,
never cached authority replacing current server access. Ordinary inactivation is not a
privacy processing restriction; explicit restriction/deletion/retention has its own policy.

**Dependencies:** Approved E1–E4, child.manage registry/schema and owned write/error/
operation helpers. No 5.2 assignment editor or People service prerequisite. Existing
synthetic assignment setup supports boundary proof without normal onboarding first.

**ATDD:** KDG-A13.child-manage-role/Save-Cancel,
A02.child-admin-create-all, A16.child-inactive-pending-accepted/historical-edit/reactivate,
A09.child-replay/lost-response, A11.child-concurrent-save,
A14.child-org/account, A21.child-attribution and A19.child-admin-accessible.
First observe missing A13.child-manage-Save-Cancel after Build approval; focused
state/validation/transaction tests then affected API/runtime-role/browser suites.
Actual phone protocol extends deactivation while a device has pending new work.

**Impacts:** Scaffold: prove bounded configuration/conditional-write/receipt and scoped
reference patterns through existing owners; no generator duplication. Shared UI:
promote proven simple list/Save-Cancel/active status composition only; child semantics
stay KDG-owned. Agent/docs: inactive child vs historical access, UUID vs display name,
current server check vs unaware offline phone. Contracts: child management/error/type
fixtures with capture eligibility together. ADR: inherit scoped access, structural
integrity/attribution, release and explicit configuration saving; A-6 history policy
is already approved. No accepted shared ADR changed or new child-master service.

**Review checkpoint:** Revised deactivation policy/scope approved when the user said
Yes, next. Privacy restriction/deletion is separate from ordinary availability.
This manages availability, not accounts, employment or application grants.

Deactivation amendment approved 2026-10-14: earlier E1 rejection references to inactive
children apply to fresh ineligible requests, not previously provisioned queued offline
observations denied solely by ordinary deactivation. Story 5.1/current A-6 supersedes
that case; current membership/grant/assignment checks remain binding. Privacy
restriction/deletion is separate and not silently inferred from inactive status.

### Story 5.2: Assign children to verified facilitators online

As a questionnaire administrator,
I want to assign and unassign children for verified Khula facilitators,
So that each capturer sees the children they are authorized to observe.

**Scope:** Responsive online facilitator/child assignment list and explicit Save/Cancel.
Facilitator means an existing account with current Khula membership and capture access,
not an employee/person record. Identity onboarding and Access role approval remain with
their shared owners. No new invitation/password/grant editor or offline administration.

**Requirements:** FR-12; assignment FR-2/3/4/8/13/16/17; NFR-1–5.
UX-DR2/7/10–13; AD-2/3/4/7/8/9/10. No supervisor role or People dependency.

**Acceptance Criteria:**

**AC-1 — Authorized management and verified targets**

**Given** current Khula admission and explicit assignment.manage,
**When** the administrator opens facilitator choices or saves an assignment,
**Then** verify current target account/membership/capture eligibility through existing
Identity/Access-owned authorized HTTP evidence, not direct tables or email/name matching,
**And** only permitted minimal account display facts are returned,
**And** capturer-only, membership/platform-role-only and foreign-org requests are denied.
An operator/user bearer cannot impersonate a target by changing the account selector.
Unavailable verification is not evidence of target eligibility or confirmed ineligibility.

**AC-2 — Explicit assignment Save/Cancel and idempotency**

**Given** verified target and a permitted active child,
**When** the administrator explicitly saves assigned/unassigned status,
**Then** atomically update the scoped child/account assignment with stable identity,
expected revision, actor/time, required compact evidence and operation receipt,
**And** enforce same-org child and unique effective child/account relationship without
silently merging/resetting older values on replay,
**And** Cancel changes no assignment; name/email is never the assignment key.
Assigning does not create membership, employment or app grants; unassigning does not
revoke shared account access. Published questionnaires/captures remain unchanged.

**AC-3 — Choices and historical access**

**Given** an assignment is added or removed,
**When** a capturer refreshes eligible children or attempts new-capture sync,
**Then** choices/new creates use current applicable assignment and capability checks,
**And** unassignment stops new assigned captures but retains own historical read/edit
while the user still has those KDG permissions,
**And** one eligible child is automatic and additional children use selection,
**And** administrator create.all remains independent of child assignments.
Offline devices cannot learn assignment changes immediately; later server denial retains
already saved phone work truthfully. Unassignment is not ordinary child deactivation.

**AC-4 — Membership retirement/rejoin does not resurrect assignment authority**

**Given** a facilitator's membership is retired and later a new membership is established,
**When** old child assignments are evaluated,
**Then** user-approved MVP policy requires administrator confirmation/renewal for the new
membership instance before those assignments permit new assigned captures,
**And** grants must independently be current; an assignment cannot revive revoked access,
**And** account-linked original captures remain readable/editable only under current
own-record authority, without duplicating the account or changing original ownership.
Concrete membership lifecycle identifiers/evidence and renewal UX gate Build. This
policy is approved with this story; simple grant expiry/reauthorization within
the same continuing membership does not itself require assignment renewal.

**AC-5 — Concurrent edits, failures and shared onboarding boundary**

**Given** stale assignment revision, lost response, target verification outage or session change,
**When** Save/retry occurs,
**Then** reject stale writes and keep attempted changes in memory for explicit review,
**And** recover original operation outcomes without duplicate assignment/evidence,
**And** recheck current manager/target authority for restarted execution and prevent
late cross-account responses; no server conflict draft or offline queue.
If a target has not onboarded or lacks capture access, link the shared owner workflow
when available or explain the prerequisite. No fake Auth account, automatic grant,
arbitrary provider sync or completed-onboarding claim is created by this portal.

**AC-6 — Accessible assignments and current-access proof**

**Given** synthetic eligible/ineligible targets, children and membership generations,
**When** contract/browser/runtime-role and applicable installed-phone checks run,
**Then** prove assign/unassign, current target verification, rejoin renewal, same-org
constraints, replay/concurrent-save safety and administrator create-all independence,
**And** prove refresh/new-create denial versus historical own edit, account isolation
and preserved pending observations; unavailable evidence is distinct from an empty list,
**And** responsive labelled selectors/status/Save/Cancel are usable with touch/keyboard/zoom.
Record automated and physical results separately; none execute during planning.

**Contracts:** App-owned assignment list/create/update uses child/account/membership
instance references, operation identity, expected revision and explicit active state.
Trusted target eligibility comes from the existing shared owners' bounded authorized
contract, which remains unimplemented/unfinalized for KDG; declare caller policy,
verified target binding, exact allowed fields and outage behavior before Build. The
ordinary user `/v2/check` target cannot be changed to another account. No substitute
public endpoint/direct table queries/new Access service are specified here.

Remote verification occurs outside business locks; bounded evidence supports only the
executing assignment write. Recheck restarted execution and protected local child/
assignment structural state. A membership generation change invalidates old assignment
new-create eligibility until explicit renewal; use authoritative lifecycle evidence,
not guessed dates/profile renames. Preserve attribution/history and current grants.
Concrete lifecycle/target/list/write/outcome/error DTOs and freshness fixtures gate Build.

**Dependencies:** Approved E1–E4/5.1; Identity/Access target-discovery/eligibility and
membership-lifecycle contracts plus normal invitation/role administration where needed.
These require owner/handoff closure, not all Leave planning. Existing synthetic owner
setup supports tests. No People/shared employment, later reliability story or universal
member directory dependency.

**ATDD:** KDG-A13.assignment-manage-role/Save-Cancel,
A03.assignment-target-verification, A16.assignment-added/removed/rejoin-renewal,
A02.assignment-no-grant/admin-create-all, A09.assignment-replay/lost-response,
A11.assignment-concurrent-save, A14.assignment-org/account,
A21.assignment-attribution and A19.assignment-admin-accessible.
First observe missing A13.assignment-Save-Cancel after Build approval; focused
reference/lifecycle/freshness/transaction tests then affected API/contract/browser suites.
Installed-phone proof changes assignments while the facilitator remains offline.

**Impacts:** Scaffold: prove scoped account references/target-evidence and conditional
configuration writes with existing owners; no new runtime Access/directory. Shared UI:
verified-target selector, current status and whole-form controls only if reusable.
Agent/docs: account vs membership vs grant vs assignment, no employment, membership
renewal vs grant recovery and unavailable vs ineligible evidence. Contracts: target/
lifecycle/write/error/generated types together. ADR: inherit Identity/Access ownership,
invitation/prepared-grant safeguards, current auth and configuration saving; approved
membership-instance renewal policy applies, no accepted ADR mutation.

**Review checkpoint:** Scope/criteria and membership-rejoin renewal policy approved
by the user with C. Assignment alone never grants application access.

### Story 5.3: Protect saved observations through storage failures and app updates

As a capturer using an installed phone PWA,
I want saved observations and pending changes protected when storage or updates fail,
So that I can continue with clear guidance instead of losing acknowledged work.

**Scope:** Complete and prove E1/E2 storage/schema/update mechanisms against old/new
payloads, quota/transaction failures and interrupted migrations. Reuse preceding
implementation; no unfinished-form store, offline administrator content, universal
sync framework or guaranteed recovery from browser/user deletion. Final pilot device/
privacy/retention operating decisions follow separately, not a dependency for these tests.

**Requirements:** FR-18 and reliability FR-7/8/13–17; NFR-1–5.
UX-DR4/7/8/9/11–14; AD-4/6/7/8/9/10. App-managed saved state, not guaranteed backup.

**Acceptance Criteria:**

**AC-1 — Save failures and bounded useful recovery**

**Given** full storage or an aborted/uncertain IndexedDB Save transaction,
**When** Save cannot be confirmed,
**Then** no saved/synced claim appears until the original atomic result is known,
**And** keep visible in-memory input, reclaim only proven disposable acknowledged cache
where possible and attempt at most one bounded recovery retry,
**And** persistent failure gives plain guidance to free phone storage and try Save again
while keeping this form open; no intentional crash, database reset or misleading restart.
Never delete pending actions, saved conflict branches, locally authored observations or
required definitions to make room. Closing/restarting may lose unsaved typing.

**AC-2 — Safe local schema migration**

**Given** a prior supported local schema with saved creates/edits/unknown operations/conflicts,
**When** the app upgrades local schema or that upgrade is interrupted/fails,
**Then** preserve original account/org IDs, immutable action payloads, predecessor links,
required definitions, scoped authority observations and acknowledged captures,
**And** migration succeeds atomically or leaves recoverable prior data without destructive
reset; incompatible read/write code does not proceed on an unsupported schema,
**And** retry resumes only through verified safe migration behavior, with truthful guidance.
Use bounded versioned migration fixtures; schema metadata is not a recovery guarantee.

**AC-3 — App update activation without forced reload**

**Given** a new service-worker shell while an entry/edit or Save/request is active,
**When** an update becomes available,
**Then** default to update first, then synchronize; pending edits/conflicts are not
a prerequisite to update and no preliminary sync stage is required,
**And** defer reload while an unsaved form awaits Save/Cancel or an executing local Save/
network request must settle safely under bounded handling, preserving uncertain action
identity for later recovery rather than blocking updates indefinitely,
**And** preserve saved queue/conflict state across activation and reopening,
**And** old/new tabs cannot corrupt local data or run incompatible command interpretations.
No autosave is introduced to make update activation convenient. No private API response
or other-author administrator content enters shell caches.

**AC-4 — Queue/version compatibility and interrupted delivery**

**Given** supported older frozen operations and original questionnaire versions,
**When** app/API updates and foreground synchronization resumes,
**Then** old creates/edits/outcomes retain supported interpretation and stable identity,
**And** lost responses/expired claims recover without duplicate effects or older acknowledgements
replacing newer saved work; conflicts pause dependent edits for explicit review,
**And** unsupported payloads stay protected with Needs attention instead of deletion
or silent conversion. Do not remove old handlers solely because the ready queue is empty.
Current server authority is rechecked; compatibility never bypasses revocation.

**AC-5 — Browser limits and privacy-aware cache behavior**

**Given** permission to request persistent storage/quota estimates or unsupported browser mode,
**When** setup, cache maintenance or storage diagnostics occur,
**Then** persistent-storage support is best effort and never described as backup,
**And** only safe disposable re-downloadable cache is reclaimed; preserve protected work,
**And** explain that uninstall/clear-site-data/OS eviction can remove phone data and private
browsing is unsuitable for durable use. No promise to recover bytes already deleted.
Expose safe operation/support references, not sensitive answer/log payloads. Use the
own-only account/Khula partition and declared locked-data retention behavior.

**AC-6 — Failure/update evidence on actual supported phones**

**Given** synthetic supported schema/build pairs and pending/conflicting observations,
**When** controlled quota/transaction/migration/queue/browser tests and installed phone
upgrade/reopen/sync checks execute,
**Then** prove no false Save, safe cache reclaim, failed migration protection, deferred
shell activation and old payload/original-definition preservation,
**And** record automated fault-injection results separately from physical Android/iPhone
normal update/reopen behavior and any unsupported OS/browser combinations,
**And** scope failure stops completion claims; existing release migration/activation
failure/recovery rules remain binding. No actual device or runtime execution in planning.

**Contracts:** Minimal platform-owned local persistence/migration/claim/update fixtures
and app-owned schema/queue compatibility declarations. Coordinate local database version,
service-worker/API build and supported payload versions before delivery; do not rely on
frontend generation config as proof. Handle versionchange/blocked upgrades and tabs with
bounded safe coordination, not silent forced close or in-place frozen-payload mutation.
Server migration activation follows ADR-0020 and queued work ADR-0028. Concrete fixtures,
versions, time bounds and exact supported upgrade pairs gate Build. Require behavioral
compatibility, not a mandatory adapter architecture: unchanged schema/commands need
no adapter; add a small migration/version handler only when a concrete change needs it.

**Dependencies:** Approved E1–E4/5.1/5.2 and their delivered consumer baselines; existing
platform scaffold/UI/release owners and required test utilities. No later pilot-policy
story needed to run synthetic reliability fixtures. Pending shared pattern ownership
handoff must close before modifying shared files; domain-neutral promotion accompanies
first-consumer proof, not a second generator/runtime offline service.

**ATDD:** KDG-A08.quota-transaction-recovery, A17.failed/interrupted-local-migration/
deferred-update/pending-upgrade, A09.upgrade-lost-response, A10.upgrade-claims-order,
A12.upgrade-original-definition, A14.upgrade-partition, A15.upgrade-session,
A18.disposable-cache-only, A21.storage-log-safety and A22.release-payload-compatibility.
First observe missing A17.interrupted-local-migration after Build approval; focused
migration/claim/update tests then affected browser/contract/release suites. Expand existing
installed proof with actual nonproduction update while observations are pending.

**Impacts:** Scaffold: promote proven bounded local transaction/schema migration, claim/
queue compatibility and update fixtures to existing platform owners. Shared UI: safe
storage/update/status feedback with no recovery wizard. Agent/docs: phone Save vs server
backup, supported upgrade pair, protected work vs disposable cache and no forced reload.
Contracts: local schema/payload compatibility and generated app/update metadata together.
ADR: inherit release/queued-work/privacy/isolation and Save-only behavior; accepted ADRs
unchanged. Record exact first-consumer tests and physical limits in owning documentation.

**Review checkpoint:** Revised update-first/no-mandatory-adapter scope approved when
the user said happy, next.
No new unfinished-form recovery or universal offline/history framework is introduced.

### Story 5.4: Verify the complete workflow and prepare a controlled Khula pilot

As the Khula application owner,
I want verified device behavior and clear operating boundaries before real observations,
So that facilitators can use KDG Capture simply and sensitive child data is handled deliberately.

**Scope:** Integrated acceptance/device/release evidence, focused user guidance and
closure of outstanding pilot operating decisions. Exercise earlier delivered slices;
this story does not supply safety deliberately omitted from them or authorize deployment.
No analytics/export/notification, user-facing recovery wizard or generic compliance engine.

**Requirements:** Completion evidence for FR-1–18; operating FR-16/17/18 and NFR-1–5.
UX-DR1–14 to their approved scope. Production/real-data execution requires separately
authorized environment/release and Khula policy readiness; planning executes none.

**Acceptance Criteria:**

**AC-1 — Minimal policy decisions recorded before real child data**

**Given** the planned isolated synthetic validation and proposed real-data pilot,
**When** pilot readiness is assessed,
**Then** name Khula's responsible business/privacy owner and record approved lawful
child-data processing purpose/basis, business/audit retention, device suitability and
local acknowledged/pending/conflict/locked-data retention/disposal policy,
**And** distinguish the 30-day own download window from retention and seven-day offline
access from authorization to keep data indefinitely,
**And** distinguish ordinary child deactivation from explicit privacy processing restriction/
deletion requests. No automatic deletion merely because a child is inactive or sync fails.
Unresolved real-data policies block pilot activation, not synthetic feature development.
No numerical legal retention period or shared-phone security guarantee is invented.

**AC-2 — Session expiry, revocation and retained pending work**

**Given** saved pending observations and valid/expired exact own-scope observations,
**When** token expiry, seven-day expiry, logout/account switch or known revocation occurs,
**Then** prove allowed local use only within the exact applicable window, current checks
on server sync, and same-account reauthentication without automatic consequential action,
**And** logout/expiry locks rather than silently deletes saved pending data, with no
other account/admin uploading it; learned denial stops affected actions,
**And** define the owner-approved path for genuinely unauthorized retained phone work,
including bounded retention/disposal, without requiring the facilitator to diagnose
technical errors or promising a server copy. Outage is not proof of revocation.
The path must use permitted same-user recovery or authorized disposal, not a new public
export/impersonation/central conflict-intake feature.

**AC-3 — Actual installed-device complete workflow**

**Given** the isolated HTTPS synthetic setup with delivered capture/editor/admin features,
**When** final Android Chrome and iPhone Safari installed-PWA protocols execute,
**Then** verify sign-in/fixed Khula, capture/close-reopen/edit/sync, multiple same-day
observations, optional details, original-version history, assignments/deactivation,
admin/facilitator concurrency, new questionnaire while offline and update-first behavior,
**And** verify portal all-record work is online and PWA local content remains own-only,
**And** record exact device/OS/browser/build/test IDs and supported/unsupported results.
Physical tests do not claim to simulate all quota/clock/migration/OS-eviction cases;
controlled automated faults provide their separate named evidence.

**AC-4 — Requirement and release evidence complete**

**Given** earlier stories' ATDD and focused-test evidence,
**When** integrated readiness/release checks run,
**Then** map each requirement/story to actual failing-then-passing acceptance evidence,
affected regression/contract results and required physical outcomes,
**And** verify controlled migrations, previous-version compatibility, activation-block
on failure, recovery and queued-payload support using existing release owners,
**And** unresolved critical failures block pilot completion; planned/skipped/manual checks
are never reported as automated PASS. Root stale build/dev is not repository verification.
Operational backups/recovery and supported sign-in/callback/HTTPS targets need evidence,
not merely accepted designs or generated configuration assertions.

**AC-5 — Simple localized guidance and safe diagnostics**

**Given** the approved Afrikaans content and actual recovery behavior,
**When** facilitators install, capture, Save, sync or encounter ordinary failure,
**Then** short guidance explains Saved on this phone vs Synced, offline access expiry,
reconnection/Sync now, update handling and storage limits without technical internals,
**And** pending-work logout and privacy/disposal guidance matches approved policies,
**And** safe support references contain no child answers, credentials or payload dumps.
Khula reviews operational translations; rating values 2–4 may remain numeric without
invented clinical descriptions. Capturer history stays My observations, not audit/version UI.

**AC-6 — Ownership and handoff evidence**

**Given** KDG's shared prerequisites and first-consumer platform patterns,
**When** delivery/pilot readiness is signed off,
**Then** record coordinator and existing Identity/Access/scaffold/UI/environment/release
owners, agreed Leave handoff, delivered dependency checks and proven shared tests,
**And** document scaffold/shared-UI/agent/docs/contracts/ADR impacts in their consuming items,
**And** keep KDG rules application-owned and platform helpers domain-neutral.
Readiness does not require all Leave planning, a People service, separate PWA deployment
or complete general-purpose offline framework. Pilot activation remains a separately
reviewable release action; this story's evidence is not implicit production approval.

**Dependencies:** Approved E1–E4 and 5.1–5.3 delivered/tested to their own acceptance
boundaries; actual supported phone test access, current shared owners and controlled
synthetic environment. Real-data operating policies named in AC-1 are pilot gates.
No downstream story required; exact initial failure/test commands depend on delivered
packages and are recorded during approved Build, not invented in this plan.

**ATDD:** KDG-A01–A22 allocated across preceding stories; emphasize A15.session/
logout/expiry, A16.current-changes/pending-denial, A17.update/storage, A14.partition,
A21.safe-diagnostics and A22.release-recovery. First observe the missing integrated
A15.pending-session-recovery acceptance boundary after Build approval; focused fixes
then the affected suites, without weakening established expectations. Complete the
installed-device extensions and retention-policy fixtures under their named owners.

**Impacts:** Scaffold/shared UI: promote only actually proven first-consumer neutral
fixtures/patterns with existing owners. Agent/docs: exact support/operating/device limits,
policy owner, tested commands and release evidence. Contracts: verify synchronized
schema/types/errors/payload compatibility, not duplicate specs. ADR: inherit platform
release/privacy/attribution/session/Access decisions; accepted ADRs unchanged. Any
new material operating design is recorded in owning documentation before real-data use.
No deployment, access change, migration or physical execution occurs in initial planning.

**Review checkpoint:** Scope/criteria approved by the user with C.
Policy closure and actual execution evidence remain pending until authorized delivery.

Rating scope amendment — user-directed 2026-10-14: the initial scale is now 1–5,
with 1 = Goed and 5 = Nie goed nie; intermediate 2–4 remain numeric unless Khula
supplies descriptions. Five direct radio choices remain the recommended presentation;
no rating is selected initially. This updates seed/form/editor/test wording above and
supersedes historical 0–5 planning references. No runtime questionnaire exists to migrate.

Engineering recovery refinement — 2026-10-14: operation lookup uses required
command_type query discrimination together with authenticated org/caller/operation ID;
current stored-resource permission remains enforced. Current contracts.md specifies
compact receipt and typed command bounds; U+0000 is rejected rather than silently
removed. Prior-child eligibility metadata is created with 1.4 provisioning and carried
by 1.5/1.6; no new user-visible capture step or offline administrator scope.

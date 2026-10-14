---
stepsCompleted: [step-01-validate-prerequisites, step-02-design-epics]
inputDocuments: [prd.md, DESIGN.md, EXPERIENCE.md, ARCHITECTURE-SPINE.md, contracts.md, discovery.md, testing.md]
status: story-creation-epic-1-in-progress
created: 2026-10-12
updated: 2026-10-13
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
| FR-8 | E3 | E1 local reopening/details; E2 30-day own history/edit/revisions; E3 permitted organization history |
| FR-9 | E2 | Full explicit revision conflict recovery for own edits; E3 adds cross-author administrator scenarios |
| FR-10 | E4 | Online bounded editor/Save/Cancel/Publish |
| FR-11 | E4 | E1 immutable seed/version pinning; E2 original-version editing; E4 actual version update/publishing compatibility |
| FR-12 | E5 | E1 controlled initial child/assignment; E5 responsive online management |
| FR-13 | E1 | E2 own historical downloads; E3 permitted all-history downloads |
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
| UX-DR8–9 | E2 own history/revisions/conflicts, E3 organization review |
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
administrator scope never crosses Khula. Use the same account/org-scoped download bounds.

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
sequentially by epic; E1 is closed and E2 scope/criteria need review before formal append.

### Current review — Epic 3

E1 and E2 planning are closed with user confirmation. Epic 3 completes administrator
organization-wide read/edit and audit while preserving original owners and current
permissions. FR-2/8 and scoped FR-9/13–17, NFR-1–4 and UX-DR4/7/8/10–13 apply.

[Candidate Story 3.1](story-candidates/3-1-administrator-history.md) adds authorized
Khula history/details, compact online audit and bounded all-authorized PWA history.
Administrator editing and cross-author conflicts follow; no E4/E5 dependency.

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
| Hoe was haar algehele houding vandag? | Required integer rating 0–5, six choices, 0 = Goed, 5 = Nie goed nie; no default rating or invented descriptions for 1–4 |
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
local stores here; later stories add draft/capture/queue stores when consumed.

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
or pinned draft/capture references. The no-create case mints no creation observation.

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
**Then** the four exact Afrikaans questions use accessible large choices, rating 0–5
initially unanswered, endpoint labels Goed/Nie goed nie and Ja/Nee default Nee,
**And** Sinehgomso is automatic when sole eligible child; additional choices follow scope,
**And** date defaults to the phone date, is editable and is separate from recording times,
**And** authenticated author is not editable and the open form pins its version.

**AC-2 — Explicit validation and active answers**

**Given** entered values,
**When** Save observation is selected,
**Then** all four primary answers are required; zero and false are valid answers,
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

**Given** lost membership/grants, changed assignment, inactive child, invalid answers,
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
version, including zero/false and rejection of hidden false details. Tenant-aware local
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
**And** Save validates the entire original-version form, including zero/false and hidden-
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

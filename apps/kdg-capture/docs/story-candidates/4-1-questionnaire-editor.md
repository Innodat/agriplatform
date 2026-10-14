---
story: '4.1'
epic: 4
status: proposed-awaiting-user-review
updated: 2026-10-14
sources: [../prd.md, ../EXPERIENCE.md, ../contracts.md, ../testing.md]
---

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
Afrikaans initial content remains exact; no clinical meaning for rating values 1–4.

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
**Then** support only rating integers 0–5 with endpoint labels, Ja/Nee with optional
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

**Review checkpoint:** Proposed scope/criteria await confirmation before formal append.
Saving prepares a questionnaire; it never changes the published version used for capture.

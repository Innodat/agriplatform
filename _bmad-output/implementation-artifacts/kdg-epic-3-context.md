# Epic 3 Context: Review and correct captures across Khula

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

Enable authorized questionnaire administrators to review and correct synchronized Khula observations online, with reliable attribution and protection against concurrent edits. The installed capture PWA remains own-only for both administrators and facilitators, including offline use.

## Stories

- Story 3.1: View authorized Khula observations and administrator audit details
- Story 3.2: Correct authorized observations online without overwriting another editor

## Requirements & Constraints

- Check current fixed-organization membership, application admission and the explicit all-record capability on every relevant request. Organization or platform administration alone is insufficient. Never infer authority from client-selected owner, organization or role, or fall back to own access after all-record denial.
- The online portal displays only synchronized records from Khula, with observation date, child and original capturer. Render and validate answers against the original questionnaire version. Distinguish empty results from failed or incomplete retrieval.
- Provide a bounded, read-only audit view of original creation and latest committed modification, plus committed create/edit events with actual actor and server time. Preserve original ownership; retries and no-op changes must not invent events. Keep operational logs and sensitive payloads out of the audit view.
- All-record review, audit and correction require current online authority. Do not cache all-record responses or issue offline all-record authority. On access loss, session change or account switch, prevent prior-scope records and late responses from rendering. An unavailable check is distinct from denial.
- Corrections use whole-form Save/Cancel. Preserve the original child, questionnaire, owner and creation facts; historical corrections do not require current child assignment. Unsaved online input is held in memory and may be lost on close or reload.
- Reject stale revisions without overwriting committed work. The editor holding the proposal compares it with the current record and explicitly chooses the current record or saves reviewed changes. Repeat review after another intervening change. Capturers retain responsibility for their own saved offline proposals; administrators cannot retrieve or resolve unsynchronized proposals.
- Recover uncertain outcomes using the original immutable operation and current authorized receipt lookup before issuing a competing edit. Changed answers require a new operation identity. Never claim an unconfirmed or rejected edit was saved.
- Prove scope, access loss, original-version rendering, concurrent edits, attribution, replay and cache boundaries with affected API, browser and runtime-role tests. Record automated and physical-device evidence separately; planned checks are not passing evidence.

## Technical Decisions

- The KDG application owns its capture, history, audit and correction workflows. Shared Identity and Access supply authorized contracts over HTTP; do not read another owner's tables or create a shared audit or conflict service.
- Use bounded, private no-store history and audit reads with explicit own/all authorization modes and pagination. Obtain actor display information only for authorized records and bind results to the current account, organization, page and session. Release business locks before external calls.
- Pin the revision shown in the edit form. Conditional capture update, required immutable audit evidence and operation receipt commit together in a short transaction. Conflicts commit no primary update or input snapshot. Keep original operation identity and current authorization in recovery.
- Preserve the own-only local queue, saved conflicts and questionnaire definitions across portal activity. Online administrator conflict input has no server proposal table, draft, autosave or offline archive.
- Follow controlled migration and release compatibility, stable typed error contracts, safe structured diagnostics and server-managed attribution. Promote neutral fixtures or UI patterns only with proven first-consumer behavior and the existing shared owners; keep KDG-specific rules and labels local.

## UX & Interaction Patterns

- Provide responsive history, detail and optional audit views for phone and computer, separate from the simple capture interface. Show reconnect or unavailable feedback rather than a false empty list.
- Use labelled controls, visible focus, accessible loading and pagination feedback, and usable keyboard, touch and zoom interactions. Present Save/Cancel and conflict comparison clearly; distinguish unconfirmed server saves from successful saves.

## Cross-Story Dependencies

- Both stories depend on the approved capture and own-history foundations in Epics 1 and 2, current Identity/Access owner contracts, original questionnaire retrieval and actor attribution. Story 3.2 builds on the authorized review surface in 3.1 and adds all-edit authorization, conditional writes and outcome recovery.
- Questionnaire editing and child/assignment administration in later epics are not prerequisites. Shared contract and owner handoffs must close before their dependent work; physical-device and controlled-release evidence remain separate from synthetic verification.

# Leave authorized entry

Generated bounded web.leave-entry.v1 owner. Follow repository AGENTS.md and accepted ADRs. Business data uses Leave API; browser Supabase is Auth only, Microsoft azure provider with SDK PKCE. No password fallback. Normal sign-in never creates membership/grants. Entry needs no employment; employee actions retain setup checks. Independent tabs own their context.

Node26.11.1/npm12.2.0/Python3.15.0/uv0.13.1. Root workspace lock and independent api/uv.lock. In api/: uv sync --frozen --group test; uv run --frozen pytest; uv run --frozen python export_openapi.py. Root: npm run api:generate --workspace @scaffold/leave-web; api:check, test:entry, test:auth, type-check, build with the same workspace.

Runtime: LEAVE_DATABASE_URL must be leave_runtime; LEAVE_ACCESS_ORIGIN, LEAVE_SERVICE_KEY, LEAVE_CURRENT_SESSION_SERVICE_KEY and LEAVE_PREFERENCES_SERVICE_KEY are private. Web VITE_LEAVE_AUTH_URL/ANON_KEY are public Auth configuration. Callback is the exact current origin/auth/callback; allowlist deliberately outside generation.

Protected setup api/tools/prepare_roles.sql; separate nonlogin leave_owner, leave_migrator and leave_runtime. Controlled api/migrate.py with LEAVE_MIGRATION_DATABASE_URL before activation through platform release tooling. No startup migration, automatic downgrade or reset. Retain immutable selection events for this increment. Packaging uses api/package_production.py and explicit selected tools.

Scaffold: bounded entry composition and neutral Auth/HTTP/migration reuse. Shared UI: platform tokens/launcher; owner-specific picker. Agent context: generated guidance. Documentation: owner commands and evidence. ADR: existing accepted decisions suffice. Local synthetic proof does not establish Entra/device or hosted VERIFY; A1/E1 stay open.

Authority inputs:
- _bmad-output/planning-artifacts/epics.md
- platform/docs/architecture/contracts/e1-security-audit-ownership.md
- platform/docs/architecture/contracts/application-admission-and-discovery.md
- apps/leave/docs/architecture/contracts/e1-work-timezone-configuration.md
- apps/leave/docs/architecture/contracts/e1-draft-persistence-and-recovery.md
- platform/docs/architecture/contracts/identity-access-employment-e1.md
- apps/leave/docs/architecture/contracts/e1-draft-choice-resolution.md
- platform/docs/architecture/contracts/e1-controlled-provisioning-and-evidence.md
- apps/leave/docs/architecture/contracts/e1-editor-opening.md
- platform/docs/architecture/decisions/0066-composed-form-opening-data.md

Optional api.leave-context.v1: protected read-only preparation context uses LEAVE_PEOPLE_ORIGIN and distinct LEAVE_PEOPLE_SERVICE_KEY. Controlled btree_gist setup precedes 0003 migration. No draft persistence, start/save/submission or administration API. Context read is an observation, never future write authority. Run test:context and scripts/prove-leave-context.mjs. Actual hosted/provider/device and full E1 remain open.

Optional api.leave-choices.v1 requires Context. GET draft-choices requires current own-read, reads explicit published metadata with scoped pagination and independent selected lookup. Restricted leave_operator commands create/archive through leave_command_owner functions and current mapped actor/command/org/type authority. Runtime SELECT only. Protect bootstrap and revoke schema CREATE after migration. Controls own canonical input-v1 in memory; D1/D2 supply persistence. No saved/submission claim or public administration endpoint. Run test:choices, tests/test_draft_choices.py, tests/test_leave_operator.py and source-bound prove-leave-choices.mjs. Actual guarded save/reopen remains D2 evidence.

Optional api.leave-drafts.v1 requires Choices. D1 adds atomic explicit start/resume, private current reads and compact retained outcomes under migration0005. Request draft_context_version=1 for the extended read; unversioned context stays compatible. My Leave owns Apply and read-only opening; D2 supplies editing. No save/discard/submission API or reservations. Scoped receipt replay precedes fresh generation/editability guards, with current authority and ownership. Dated writes guard timezone source/date through the two-second transaction; undated preservation has no profile prerequisite. Run test:drafts and prove-leave-drafts.mjs. Existing ADRs suffice; domain UI remains in Leave. Hosted/provider/device/full-E1 remain separate gates.

Optional api.leave-draft-input.v1 requires D1. D2-A adds PUT complete input-v1 replacement, atomic revision/attribution/compact save receipts and command-specific client validation. Controlled compatible migration0006 closes the demonstrated alternate-write input-version gap without rewriting0005. Original ten-second preparation and two-second transaction include commit; fresh executions recheck HTTP authority/People outside locks. Preserve exact bounded text and inactive values; no choice lookup per save, editor/autosave/Close UI, discard or submission. D1-only generation retains its prior surface. Run test:draft-input, tests/test_draft_input.py and scripts/prove-leave-draft-input.mjs. Existing ADRs suffice; hosted/provider/device/full E1 remain open.

Optional web.leave-draft-editor.v1 requires D2-A. D2-B owns exact input-v1 editing, serialized one-second idle/five-second continuous autosave, immutable bounded recovery, explicit saved-state review and safe Close/reopen. First-choice defaults require a matching fresh created start and revision; direct/resumed/restored nulls never default. Neutral task/date/status/exit controls live in ui-business; Leave owns scheduling, lifecycle and authority. Adopt only with exact --adopt-leave-draft-editor, preserving owner seeds. Fresh D2-B Access/People API seeds reuse exact HTTPX verified TLS contexts captured at process start with trust_env=False, while constructing and closing a fresh client for every current protected call. Existing owner API seeds are preserved on adoption and need deliberate owner updates; no automatic patch is claimed. Restart through controlled replacement after trust configuration changes. Run test:draft-editor and prove-leave-draft-editor.mjs. No calculation, submission, discard, custom durable browser recovery or full E1/hosted/provider/device acceptance. Existing ADRs suffice.

The current draft-editor seed checks Current Session and the combined Leave read and manage decision before People. Confirm the owner client when adopting the seed. Activate the additive Access endpoint before Leave. Roll back Leave before removing the Access endpoint. Verify the HTTP contract with tests/test_draft_context.py.

Optional web.leave-editor-opening.v1 requires the existing editor. One current preparation composes read-only draft/background/options opening; options seed the exact editor generation without a mount read. Existing context/read/choices and save/Review contracts remain compatible. Adopt only with --adopt-leave-editor-opening, preserving owner seeds for deliberate owner updates. See e1-editor-opening.md and platform ADR-0066; API activates before consumer and consumer rolls back first. Run test:editor-opening and tests/test_editor_opening.py. No migration, shared-owner contract change or performance claim follows from composition.

Optional web.leave-draft-discard.v1 extends the organization-switch editor with explicit whole-draft discard. Current own-read and manage guard new commands and the committed operation UUID references immutable closure evidence. Adopt with --adopt-leave-draft-discard and deliberately update the existing owner seeds. Run tests/test_draft_discard.py and the builder discard browser and generation tests. Use the existing controlled migration state. Native, hosted and device acceptance require their own evidence.

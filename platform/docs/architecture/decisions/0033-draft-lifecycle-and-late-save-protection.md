# ADR-0033: Draft Lifecycle and Late-Save Protection

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Draft-based application workflows and shared autosave scaffolding

## Decision

Every draft save checks both the expected explicit revision and whether the target
is still editable, atomically with the write. Finalizing or discarding a draft prevents
late autosaves from modifying or recreating it. An update to a missing/closed draft
must not silently become a create/upsert. Creation of a new draft requires an explicit
user action, with its own operation identity and existing draft-count rules.

Finalization and its required local database effects commit atomically under the
owning application's transaction. Leave submission includes request creation/state,
reservation effects and draft closure alongside existing audit/outbox requirements.
Other applications define their own states and effects. Cross-service effects retain
existing outbox/recovery contracts; this does not promise a distributed transaction.

On a lifecycle conflict, stop autosaving in the affected view and preserve unsaved
local edits where practical while it stays open. After checking current authorization,
explain the current state and offer navigation to the resulting record or a safe
return page. Do not automatically convert local edits into a new request. Submitted
and discarded outcomes are distinct from an ordinary newer draft revision.

Leave examples: **This draft has already been submitted.** with **View request**;
**This draft was discarded elsewhere.** with **Back to My Leave**. A different identity
or lost permission must not receive protected record details merely because it held an
old draft reference. Do not promise persistent local recovery beyond supported drafts.

Prevent stale create retries from resurrecting a closed draft as well as stale updates.
Use the existing operation-result identity contract; the implementation must define
sufficient lifecycle/operation evidence for its permitted retry window. Physical deletion
versus retained lifecycle metadata is an implementation decision, not grounds to allow
resurrection. Repeated finalization must not repeat business effects.

## Impact and verification

- Acceptance: submit-versus-autosave and discard-versus-autosave races, repeated
  finalization, old create retry, missing-draft update, local edit preservation and
  access-checked navigation. Confirm required local effects roll back/commit together.
- Scaffold/shared UI: reusable revision/editability checks and lifecycle-conflict hooks;
  application states, resulting resources and transaction effects remain domain-owned.
  Do not introduce a generic workflow engine.
- Agent context: link no-resurrection and explicit new-draft creation requirements.
- Documentation: builder/shared experience and Leave requirements/tracker synchronized.
- ADR: complements 0012, 0013, 0022, 0031 and 0032; accepted originals unchanged.
- Planning only; no lifecycle schema, autosave or submission code implemented.

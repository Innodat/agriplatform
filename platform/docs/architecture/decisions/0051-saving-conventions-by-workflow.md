# ADR-0051: Saving Conventions by Workflow

**Status:** Accepted  
**Date:** 2026-10-05  
**Scope:** Shared application UX and first-consumer scaffolding

## Decision

Use predictable saving conventions by workflow:

- Preserve unfinished requests automatically where draft recovery is warranted. Autosave
  the whole draft, show Draft saved only for acknowledged current input, and use Close.
  A separate explicit action such as Submit request makes the request official. Draft
  preservation must not trigger that action's reservations, notifications or approvals.
- Business configuration and administration forms use explicit Save / Cancel for the
  whole form. Descriptive fields inside these forms follow the same rule, rather than
  saving individually. Preserve established Review / Confirm or specific consequential
  action labels where already required; this convention does not remove those safeguards.
- Simple independent personal preferences, such as language, apply immediately with
  clear success/failure feedback. They are separate from explicitly saved business forms.

Never mix fields that directly update committed business state with fields awaiting Save
inside the same form. Keep different saving patterns on clearly separate surfaces. Do
not add a redundant Save button to an autosaved draft: Submit is a distinct domain action,
not another way of saving the same input. No draft-management screen is implied.

Choose persistence according to consequences and recovery value, not field count alone.
This is not a universal draft requirement. Existing applications adopt proven conventions
through their consuming work, not an automatic repository-wide rewrite. Exceptions need
a documented UX rationale and applicable acceptance evidence. Direct saving still requires
current authorization, validation, appropriate revision protection and truthful feedback;
it is not authority to bypass consequential confirmation or log sensitive input.

[ADR-0050](./0050-inline-draft-save-failure-and-exit-confirmation.md) governs draft failures:
inline Retry while editing; Stay / Close anyway only on unconfirmed exit. Explicit Save
forms retain their own unsaved-edit and uncertain-command handling. Cancel abandons only
uncommitted edits; it must not imply reversal of an already committed change.

## Impacts and verification

Prove whole-form commit behavior, Cancel without hidden field writes, immediate preference
feedback, draft preservation without submission effects, and clear saved/unsaved states.
Include keyboard/assistive-technology checks: browsing choices must not accidentally confirm
business actions. Scaffold/shared UI promotes proven form/status/navigation patterns; domain
ownership and state remain application-specific. Record per-form classification in owning
UX/stories, with tests and shared impact decisions. No generic runtime form/draft engine.
Update platform/application experience, planning and agent guidance. Existing accepted ADRs
remain unchanged. Planning only; no code, migration or readiness approval.

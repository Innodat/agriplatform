# ADR-0031: Machine-Readable API Errors and Localized Presentation

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Shared API contracts, generated frontend types and error handling

## Decision

Provide stable machine-readable error identifiers and safe typed details. Frontend
behavior must use those identifiers and HTTP semantics rather than parsing displayed
English text. Examples include `attachment_not_ready`, `review_outdated`,
`operation_busy` and `access_denied`. Keep identifiers stable across localization.
Applications own domain errors; shared platform errors and handling follow one contract.

The backend enforces the action and returns safe structured context. The frontend
maps recognized errors to localized messages and appropriate behavior: preserve input,
identify an attachment, present a refreshed review, offer retry or explain denied access.
English and future Portuguese wording can differ without changing action logic. Include
existing safe operation/correlation references where appropriate; identifiers never
confer authority. Do not expose raw exceptions, SQL, credentials or sensitive details.

Preserve HTTP error semantics, distinguish authorization from availability failures,
and treat uncertain mutation outcomes through existing operation recovery rather than
blindly issuing a new action. Unknown identifiers use a safe generic fallback while
retaining recoverable form state; clients must not crash or infer success from them.

The existing scaffold has an `error` message, optional numeric `code` and untyped
`details`. Evolve that contract deliberately: settle the wire field names and supported
compatibility transition in the affected story rather than silently changing the numeric
field to a string. Align Pydantic/OpenAPI models, framework validation/exception adapters,
generated TypeScript contracts and shared handling. This ADR establishes semantics,
not a claim that the current generated template already implements them.

## Impact and verification

- Acceptance: each known error produces correct behavior; English/Portuguese text does
  not affect branching; unknown-code fallback; safe details, consistent framework errors
  and preserved operation identity for uncertain outcomes; compatibility across clients.
- Scaffold: update owning generator/templates and contract fixtures together when built;
  never hand-edit generated outputs to establish a second error format.
- Shared UI: reuse field errors, review and retry patterns; no new administration screen.
- Agent context: record stable identifiers and no message-text branching in guidance.
- Documentation: builder/shared experience and Leave requirements/tracker synchronized.
- ADR: complements platform 0001, 0012, 0014 and 0023; accepted originals unchanged.
- Planning only; no error payload wire change, generated code or runtime API modified.

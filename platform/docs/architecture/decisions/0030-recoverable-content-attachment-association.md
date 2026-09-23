# ADR-0030: Recoverable Content Attachment Association

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Applications attaching shared Content Service objects to domain records

## Decision

Distinguish a successfully uploaded/finalized content object from its confirmed
association with an application record. The Content Service owns object storage and
verification; the application owns the domain association and authorization. These
are separate service-owned writes, not one local database transaction.

Show an attachment as confirmed only after the application has saved its association.
While this is pending, show an attaching state. On a recoverable association failure,
retry using the same content identifier and duplicate-safe operation identity rather
than uploading the bytes again. For an uncertain outcome, resolve/retry through the
existing idempotency contract; do not create duplicate associations. Preserve enough
workflow state for recovery where the application supports saved drafts/reloads.

Before association, verify content ownership/scope, allowed association and finalized
content readiness under the Content Service contract. A browser-provided content ID
alone proves neither ownership nor authorization. Domain confirmation independently
checks required attachment readiness, including applicable enabled content-safety
checks. Do not accept an action requiring a document while that association remains
unconfirmed. Other workflows decide whether optional incomplete attachments must be
retried or explicitly removed; never silently drop a file the user expects to submit.

Clean up abandoned upload objects later, while protecting objects associated with
saved drafts or submitted records. Age or a locally observed absence of association
is not sufficient evidence for deleting content owned by another service. The content
lifecycle must coordinate a recoverable pending association and any confirmation or
release with cleanup, through explicit idempotent contracts. Prevent a race in which
cleanup deletes content while association is being confirmed. Define the concrete
reservation/reference mechanism and time bounds in the affected cross-service story
before implementation; no cross-owner database query or network call inside a long-held
business lock is implied. Permanent object loss/expiry returns an honest actionable
error; do not promise retry can restore missing file bytes.

Reuse platform operation identity, short-transaction, signed-transfer and privacy
rules. Internal lifecycle steps are not additional fields or technical choices for
the person attaching a file. Preserve the existing domain authorization on every read.

## Impact and verification

- Acceptance: upload succeeds/association fails and retry reuses content; uncertain
  save does not duplicate association; required-file submission blocks until ready;
  cross-NGO/unauthorized IDs rejected; saved draft/submitted attachments survive cleanup;
  delayed confirmation racing cleanup is safe; abandoned content can be reclaimed.
- Scaffold/shared UI: prove reusable attaching/retry state and client recovery patterns;
  application association semantics stay local, Content Service lifecycle stays shared.
- Agent context: reference the two-stage association and cleanup safety boundary.
- Documentation: shared builder/experience and Leave requirements/tracker updated.
- ADR: complements [0005](./0005-direct-to-storage-uploads.md),
  [0012](./0012-operation-identity-idempotency-and-tracing.md) and
  [0022](./0022-short-transactions-and-external-service-calls.md); originals unchanged.
- Planning only; no content contracts, upload code, cleanup jobs or shared UI implemented.

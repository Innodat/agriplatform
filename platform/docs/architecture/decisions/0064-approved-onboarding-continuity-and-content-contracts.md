# ADR-0064: Approved onboarding, continuity and Content contracts

**Status:** Accepted  
**Date:** 2026-10-26  
**Decision owner:** User, explicit approval of the completed consolidated Leave planning package.

## Context

The consolidated review proposed concrete owner contracts needed before Leave delivery.
The user approved that package and requested a new Codex session at implementation.
Existing accepted ADRs remain immutable; this decision records the approved refinements.

## Decision

Adopt the exact bounded contracts reviewed in the [consolidated package](../../../../_bmad-output/planning-artifacts/leave-consolidated-planning-review.md):

- [Invitations/prepared access](../contracts/organization-invitation-and-prepared-access.md):
  exact recipient/account binding, fresh signed-in mailbox verification for new recipients,
  seven-day invitation validity, rotating resend, thirty-day prepared access and honest
  separately committed admission/activation. Refines ADR-0057/0058; no email-only person
  merge, synthetic account, automatic employment or unapproved grant.
- [Organization continuity](../contracts/organization-administrator-continuity.md): retain
  one active owner and one explicit protected Organization Administrator; no ordinary
  self-removal. services/access owns both membership and grants and serializes relevant
  writers with a short owner-local guard. Owner status alone is not authority. Controlled
  existing bootstrap/adoption is recovery, not a new universal administrator.
- [Content references/reclamation](../contracts/content-association-and-reclamation.md)
  and [authenticated reads](../contracts/content-ownership-and-authenticated-read.md):
  durable owner preparation/fencing, sealed verified bytes, per-request authenticated
  application streaming, bounded resources and recoverable cleanup. Refines the existing
  ADR-0030/0038/0054/0055 boundaries without adding private bearer read URLs.
- [Assisted Entra trust](../contracts/trusted-entra-organization-enrollment.md): bounded
  operator-assisted tenant proof and explicit default-off automatic enrollment; no Graph
  synchronization or identity-broker replacement. ADR-0057's admission rules still apply.
- Existing Identity-owned own-account language and the bounded synthetic
  [verification app](../contracts/platform-verification-app.md) use their reviewed
  owner contracts. Prove generic scaffold/UI patterns with first actual consumers.

Exact selected bounds, schemas, outcomes, recovery and tests live in those contracts;
this ADR does not duplicate them or authorize live credentials/provider changes.

## Consequences and delivery boundary

The candidate approval concern is resolved. Future changes to these decisions need a
linked superseding ADR where material. Existing actor, tenant, current authorization,
transaction, audit, migration and release safeguards remain binding. Native provider,
database, browser and recovery evidence is delivered by the actual owning stories.
Approval does not assert that those implementations or tests already exist.

Finish formal planning/readiness and prepare the handoff, then stop for the new session
before implementation. No deployment, email, import, account/grant change or migration
is authorized by this record alone.

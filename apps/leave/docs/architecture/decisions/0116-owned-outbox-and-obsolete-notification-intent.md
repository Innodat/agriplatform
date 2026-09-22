# ADR-0116: Owned Outbox and Obsolete Notification Intent

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Leave notification handover and outbox ownership

## Decision

Keep the Leave outbox in the Leave-owned application schema (illustratively
`leave.outbox`), under its database/migration authority. Do not introduce a shared
cross-application `sd.outbox` or a separate Leave delivery schema for MVP. Other
applications own their respective outboxes; shared notification delivery records
belong to that service. Follow platform silo/HTTP and per-owner schema conventions.

Standardize proven outbox mechanics and scaffold structure without sharing runtime
tables or giving workers cross-application database access. Application state and
outbox intent still commit in the same transaction. If a delivery service evolves,
it receives work through its contract and owns its delivery records; the producer's
local outbox still protects reliable handover.

Before handing over an action-request notification, the Leave worker checks whether
it remains relevant. Example: submission followed by withdrawal before processing
makes an unhanded approval-request notification obsolete. Mark that outbox item
`skipped` with an explicit reason such as `request_withdrawn`, using existing current
state/claim safeguards. Preserve the original event payload and business audit;
delivery status may change without rewriting the original event.

Leave owns this business relevance decision; the shared notification capability owns
delivery mechanics. Factual notices such as approval/cancellation updates need their
own relevance rules and must not be automatically discarded merely because no action
is now required. Already-sent messages cannot reliably be recalled; request links
always resolve through current authorization and state.

Changing local outbox state after confirmed shared-service acceptance does not cancel
remote delivery. Do not label uncertain or previously accepted work as definitely
unsent. This pre-handover check reduces obsolete messages but cannot eliminate a race
with later request changes or recall messages already in delivery. Remote cancellation
would need an explicit additional contract, not an assumed local status effect.

## Impact and verification

- Acceptance: withdrawal before handover skips the action request with reason; audit
  and payload remain; factual updates handled by their rule; current claim checks;
  acceptance/uncertain-handover race cannot masquerade as confirmed cancellation.
- Scaffold: reuse proven mechanics per owner, no central SD schema or universal queue.
- Shared UI: no employee queue screen; linked requests show current permitted state.
- Agent context: existing silo and transaction rules suffice.
- Documentation: requirements/tracker and scaffold guidance synchronized.
- ADR: follows [platform silos](../../../../../platform/docs/architecture/decisions/0003-application-silo-architecture.md)
  and [owned schema histories](../../../../../platform/docs/architecture/decisions/0016-owned-migration-histories-and-coordination.md);
  complements Leave ADR-0114 and platform ADR-0024; accepted originals unchanged.
- Planning only; no tables, event processors or delivery cancellation implemented.

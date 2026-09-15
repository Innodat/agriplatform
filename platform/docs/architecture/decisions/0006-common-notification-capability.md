# ADR-0006: Common Notification Capability

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Cross-application notifications

## Context

Leave and future applications need email and in-app delivery, tenant branding,
templates, retries, deduplication, delivery state, preferences, and operational
visibility. A separately deployed microservice is premature, but duplicating
delivery logic in every application would make reliability and privacy inconsistent.

## Decision

Establish notifications as a common capability with explicit contracts and
asynchronous delivery. Domain applications own business events, recipient intent,
and permitted message context. The notification capability owns rendering, channel
adapters, delivery attempts, retries, deduplication, and status. Begin modularly and
extract/deploy independently when justified.

## Alternatives considered

- A standalone notification microservice immediately
- Leave-owned email logic
- Synchronous email calls inside business transactions

## Consequences

- Domain commits use an outbox so notification intent is not lost.
- Delivery failures do not roll back successful domain commands.
- Templates must respect tenant branding and data classification.
- Authenticated action pages are used instead of unauthenticated email approvals.

## Revisit when

Several applications require independent scaling/availability, a separate team owns
delivery, or channel complexity justifies a separately deployed service.


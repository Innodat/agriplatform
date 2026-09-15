# ADR-0004: Configurable Snapshotted Approval Workflows

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Leave approvals and lifecycle

## Context

NGOs require zero, one, or two approval levels; approvers may be supervisors,
configured people, roles, delegates, fallbacks, or the applicant when self-approval
is explicitly enabled. Organization changes must not silently alter in-flight work.

## Decision

Configure workflows per NGO/policy and resolve them to ordered step instances on
submission. Snapshot the resolved workflow. Step and application states are stored
separately with complete transition history. Self-approval is explicit and audited;
redundant consecutive decisions by the same person may collapse under configured
rules.

Leave Managers may submit or approve on behalf under a separate permission,
mandatory reason, visible attribution, and conflict checks. Approved cancellation
requires no new approval and creates audited balance reversals. Capacity warnings
are informational in MVP.

## Alternatives considered

- Hard-code Supervisor then Director
- Re-resolve approvers whenever the request is opened
- Store one mutable status and approver column

## Consequences

- Workflow history survives reporting-line and delegation changes.
- Rerouting is an explicit audited command.
- Commands require optimistic concurrency and idempotency.
- State-machine authorization and transition tests are mandatory.


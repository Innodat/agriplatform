# ADR-0002: Versioned Leave Types and Policies

**Status:** Accepted  
**Date:** 2026-09-01  
**Scope:** Leave configuration

## Context

NGOs may change entitlement, accrual, documentation, privacy, balance, eligibility,
and approval rules. Historical requests must retain the rules under which they were
calculated and submitted.

## Decision

Leave types and policies are versioned and effective-dated. Used types are archived,
not hard-deleted. A submitted application stores the applicable policy version and
calculation snapshot. Employee entitlement differences are effective-dated overrides
with reason, authorizer, preview, and explicit ledger effect.

## Alternatives considered

- Edit a single current policy row
- Copy all policy fields into every request without a policy identity
- Encode policy behavior permanently in application code

## Consequences

- Historical interpretation remains stable.
- Admin UI must distinguish draft, future, current, and archived versions.
- Retroactive changes require deliberate recalculation/adjustment workflows.
- CRUD means create, read, new-version update, archive, and restore—not destructive
  deletion of referenced records.


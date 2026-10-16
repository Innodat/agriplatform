# ADR-0135: Explicit No-Balance Tracking for MVP

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Policies without an entitlement balance

## Decision

Support an explicit No balance tracking option for MVP, completing the concept distinguished
from manual-only grants in [ADR-0090](./0090-annual-entitlement-availability-options.md).
Manual-only tracks entitlement from authorized grants; no grants legitimately means zero.
No balance tracking instead has no entitlement pot against which requests are funded.

Calculate and record leave duration and usage. Preserve current organization/access,
explicit policy assignment, employment/date/duration restrictions, document requirements,
approval rules and all other applicable request safeguards. No balance tracking bypasses
only the entitlement-balance funding requirement, not ordinary request validation or approval.
Do not create fictional infinite entitlement, automatic grants, balance reservations or
consumption against a nonexistent entitlement pot. Request lifecycle/usage evidence remains.

Present Not balance-limited instead of zero or an invented unlimited balance. Paid/unpaid
classification is independently configured: no balance tracking does not imply unpaid leave,
unlimited request duration or absence of approval. Do not offer balance-shortfall remedies
merely because an untracked request has no numerical allowance.

Keep tracked versus untracked fixed once a policy is used for MVP. Do not permit replacement
or new-type routes to migrate existing entitlement across that boundary. Independent new
types and fresh configuration are allowed; historical evidence remains against its original
type. This supplements [ADR-0134](./0134-used-policy-entitlement-source-fixed-for-mvp.md)
without changing its automatic/manual-only restriction.

## Consequences and verification

Detail bounded configuration, read/calculation and UI story scopes collaboratively before
claiming complete coverage. E5 must integrate real submission/approval/lifecycle behavior;
E6 corrections and E7 usage/reporting preserve the distinction. Bind typed balance-not-
applicable results, conditional policy fields, permitted actions, paid/unpaid presentation,
snapshot/evidence and concurrency contracts before readiness. Unsupported or failed reads
must never be interpreted as no balance tracking.

Verify automatic/manual-only/untracked distinctions, no numeric fake balance or funding
effects, actual duration/usage evidence, ordinary authorization/request gates, independent
paid/unpaid classification, no used-policy conversion/bypass and retained history. Map
requirements to actual API/database/browser/consumer tests; no runtime tests executed here.

Scaffold/shared UI reuse typed applicability/status and guarded configuration patterns;
Leave owns policy/usage meaning. Update features, spine, written UX and planning consumers.
Existing agent context suffices. Accepted predecessors unchanged. No runtime implementation,
migration, readiness PASS or implementation authorization.

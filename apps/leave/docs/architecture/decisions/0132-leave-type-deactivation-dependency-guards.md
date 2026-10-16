# ADR-0132: Leave-Type Deactivation Dependency Guards

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Leave type retirement

## Decision

Use Active/Inactive and Deactivate, retaining archive-marker storage, stable identity,
versions and historical references under [ADR-0002](./0002-versioned-leave-policies.md)
and [ADR-0086](./0086-archive-markers-and-effective-dated-versions.md).

Block deactivation while current or scheduled policy assignments depend on the type.
Link authorized affected settings; resolve assignments through their separate reviewed
change/ending flow under [ADR-0126](./0126-explicit-policy-assignment-with-employee-filters.md)
and [ADR-0128](./0128-accountable-request-impacts-of-administrative-changes.md).
Guard concurrent assignment/deactivation and alternative supported writes on the backend.

Review outstanding entitlement/request treatment explicitly. Deactivation does not erase
balances, cancel requests, change approved funding or remove otherwise authorized historical
access. Exact outstanding-entitlement/request handling remains a pre-story contract;
this guard does not invent transfer, expiry or resolution rules. Record actor/time and
required audit atomically. Inactive types are unavailable for ordinary new assignments/
request choices. Existing drafts follow accepted compatibility/lifecycle rules, preserving
useful input and explaining any cleared definitively obsolete selection.

## Consequences and verification

Prove current/scheduled dependency blocking, related-setting navigation, concurrency,
identity/version/snapshot retention, unavailable new choices, historical reads and draft
compatibility. Reuse proven availability/review/attribution scaffold and UI patterns;
Leave owns dependency semantics. Existing agent instructions suffice. Update requirements,
UX, architecture navigation and Story 3.37 traceability. Accepted predecessors unchanged.
Planning only; no implementation or readiness authorization.

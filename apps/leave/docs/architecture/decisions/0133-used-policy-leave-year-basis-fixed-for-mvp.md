# ADR-0133: Used-Policy Leave-Year Basis Fixed for MVP

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** Ordinary migration of existing entitlement between leave-year bases

## Decision

Retain calendar-year and employment-anniversary-year selection during initial policy
configuration under [ADR-0042](./0042-entitlement-period-basis.md). Once a policy is in
use, its leave-year basis is fixed for MVP. Defer ordinary migration of existing
entitlement between bases. This resolves the open basis-transition question in
[ADR-0098](./0098-availability-method-changes-at-period-boundaries.md); accepted
predecessors remain unchanged.

A new leave type may be created with either supported basis and its own entitlement
history. Creation does not migrate existing entitlement. Do not permit replacement
policy assignments or a new type to bypass the unsupported migration, replay grants,
reset/transfer balances or rewrite requests. Existing balances remain against their
original type. An authorized manual adjustment alone is not a basis-migration mechanism:
period boundaries, future grants, carry-over, expiry and request funding need explicit
transition rules before such a feature is introduced.

This restriction does not prohibit independently configured leave types using different
bases, initial assignments with no migrated entitlement, accepted daily/monthly/upfront
method changes within an unchanged basis, or necessary corrections to incorrect factual
employment history through the owning authorized correction workflow. Corrections
preserve original evidence and existing impact/acknowledgement safeguards; they are not
a disguised ordinary policy migration.

## Consequences and verification

Bind the exact definition and protected predicate of in-use state before implementation,
including concurrent first use/publication and all supported assignment/write paths.
Explain the restriction in the policy editor and affected assignment review. Prove
initial basis selection, used-policy edit rejection, no migration bypass via replacement
or a new type, unchanged historical balances/requests, independent new-type configuration,
supported method changes and factual correction separation.

Update Features §4/period rules, spine, written UX, E3 contract obligations and tracker.
Scaffold/shared UI reuse guarded configuration/typed errors/review; Leave owns the basis
and migration rules. Existing agent context suffices. No new migration engine, runtime
code, readiness PASS or implementation authorization.

# ADR-0111: Modest Calculation Snapshots and Version Evidence

**Status:** Accepted  
**Date:** 2026-09-22  
**Complements:** ADR-0106 and ADR-0107

## Decision

Use a Leave-owned table for immutable calculation evidence attached to consequential
submissions, approvals and confirmed changes. Store searchable identity/context
columns with structured JSON calculation details. Link each snapshot to its request
or other domain action and save it in the same database transaction as that action.
A snapshot is not required for routine balance viewing.

Keep the record modest: relevant calculation inputs, result and allocation, policy
version references, calculation-version identifier, actor and recorded time. Preserve
input values or references to retained immutable versions; references to mutable
current records alone do not preserve evidence. Apply existing NGO isolation and
sensitive-data permissions to snapshots and their readable explanations.

The calculation version identifies the rules/code used, separately from the policy
version. A bug fix may change the calculation without changing the policy. Retain
original results and identify affected decisions when investigating such a change.
Resulting balance corrections follow existing review, explanation and affected-request
safeguards; a code release must not silently rewrite stored decision evidence.

Do not build a generic snapshot framework, a new administration screen or an engine
that executes every historical code version. Preserve enough evidence to explain the
original result and compare it with a corrected calculation. Physical column names
and payload shape are implementation details to settle in the affected story.

## Impact and verification

- Acceptance: action and snapshot commit/rollback together; retries do not duplicate
  evidence; later source changes cannot alter the saved explanation; authorized
  readers see only permitted data; calculation and policy versions are distinct.
- Scaffold/shared UI: Leave-owned storage, existing transaction and history patterns;
  no shared snapshot service or new UI primitive.
- Agent context: existing immutability and transaction instructions suffice.
- Documentation: requirements and tracker synchronized.
- ADR: additive; no accepted predecessor modified.
- Planning only; no table migration or application implementation performed.

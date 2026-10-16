# ADR-0140: Policy In Use from Confirmed Assignment

**Status:** Accepted  
**Date:** 2026-10-15  
**Scope:** In-use predicate for MVP policy restrictions

## Decision

A policy is in use once an employee assignment is confirmed, including a future-dated
assignment. Historical use keeps this condition true: ending assignments or reaching a
zero balance does not make the policy unused again. Apply this definition to the used-
policy basis/category restrictions in ADR-0133/0134/0135 and their supported write paths.

Creating or publishing an unassigned, unused policy does not lock the restricted choices.
Selecting a leave type in an unfinished employee draft is not policy use. Confirmed
assignment establishes the boundary before earning or requests can depend on settings.
Changes to published settings still create immutable new versions; unused status is not
permission to edit a published row or discard earlier history.

## Consequences and verification

Bind identity/history representation, retained confirmed-assignment evidence, version
lineage and concurrent first-assignment/publication guards before readiness. Do not rely
only on currently active assignments or current balance. Imported/adopted consequential
history must map deliberately to this predicate; missing historical evidence is not proof
of unused state. Current authorization and all existing date/review guards remain.

Verify unused/unassigned publication, draft selection without locking, confirmed current/
future assignment locking, historical persistence after assignment ending/zero balance,
immutable version updates and concurrent first-use changes. Exact test mapping, delivery
evidence and final sizing/readiness remain open.

Update requirements, spine, written editor UX, affected E3 contract obligations and tracker.
Reuse guarded configuration/typed-status/error scaffold/UI patterns; Leave owns use/history
semantics. Existing agent context suffices. Accepted predecessors unchanged. No code,
runtime tests, readiness PASS or implementation authority.

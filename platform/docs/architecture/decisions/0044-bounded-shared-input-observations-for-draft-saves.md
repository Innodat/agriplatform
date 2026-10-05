# ADR-0044: Bounded Shared-Input Observations for Draft Saves

**Status:** Accepted

**Date:** 2026-10-01

**Scope:** Application draft saves that preserve unfinished input without consequential domain effects

## Context

Leave needs current shared employment information before saving an employee's draft.
That information can change after the shared read and before Leave's local commit.
The user approved allowing an already-checked, short draft save to finish and requested
that the principle be platform-wide. Authorization already has an in-flight boundary
under ADR-0021; this decision defines the limited equivalent for shared domain inputs
used by draft-preservation actions.

## Decision

Applications may use a freshly obtained shared-input observation for the bounded
execution of a draft-preservation action. If that shared input changes remotely after
the check, an already-executing action may complete within its declared deadline.
The next action obtains current shared facts and current authorization. Opening a
form, retaining a browser tab or possessing an earlier response does not preserve
authority or validity for a later action.

This is a reusable platform pattern, applied explicitly by the owning workflow. It
is limited to saving unfinished input without submitting, approving, reserving,
paying, consuming entitlement or producing equivalent consequential business effects.
Calling a record a draft is not sufficient if its save causes such effects. Those
actions retain their own stronger input-validity and confirmation contracts.

An adopting workflow must define:

- Which shared facts are checked and why the bounded race is acceptable for its draft.
- A total execution deadline, including dependency waits, local coordination and commit;
  per-call timeouts alone are insufficient. Leave E1 selects ten seconds. This is
  not a mandatory timeout for every application.
- Evidence identifying the source/version, observation time, effective date/context,
  authorization decision and committed action, without copying sensitive payloads.
- Fresh checks for queued, delayed, restarted or otherwise new execution. Do not
  extend a prior observation through unbounded retries or cache it across requests.
- Protected local revision, lifecycle, scope and dependency checks in the write
  transaction. Changed local context invalidates a dependent pre-read observation.
- Failure, uncertainty and retry handling under the existing operation-identity
  contract. A committed operation is replayed, not executed again, and its outcome
  still requires current authorization.

Unavailable required shared input fails safely; this rule does not permit fallback
to an old observation from another request. It does not excuse an invalid initial
check or deliberately ignore a newer invalidation already observed before mutation.
Keep external waits outside local business locks under ADR-0022. Do not claim that
this creates distributed atomicity or cancels remote changes.

For Leave, a draft save may finish after an employment change races its successful
check. A subsequent action applies current employment/read-only rules and current
membership grants. Submission, approval and entitlement changes are excluded. Leave's
work-timezone/date and local configuration checks remain protected and independent
of shared employment ownership.

## Impact and verification

- Acceptance: shared change before check affects the action; change after check may
  permit only the bounded executing draft save; subsequent and restarted execution
  rechecks. Verify deadline enforcement, unavailable input, local-context change,
  commit uncertainty and authorization loss before outcome recovery.
- Scaffold: promote observed-input/version evidence, total deadlines, fresh-execution
  boundaries and test fixtures once proven by the first adopting workflow. Applications
  own eligibility, effect classification and timeout selection; no central draft service.
- Shared UI: preserve truthful Saved/uncertain/read-only feedback. A completed draft
  save never implies eligibility for later submission; no extra confirmation UI required.
- Agent context: link the bounded draft-only scope and its distinction from consequential
  actions; no mandatory new employment dependency for unrelated applications.
- Documentation: owning application contracts declare adoption and exact bounds;
  Leave's contract, tracker and acceptance map reference this decision.
- ADR: additive clarification alongside ADR-0021/0022/0040; accepted predecessors stay
  unchanged. No runtime, schema, tests or implementation-readiness pass is created.

## References

- [Revocation and in-flight operations](./0021-revocation-and-in-flight-operations.md)
- [Short transactions and external calls](./0022-short-transactions-and-external-service-calls.md)
- [Shared employment consistency](./0040-shared-employment-core-and-application-settings.md)
- [Leave E1 shared-input contract](../contracts/identity-access-employment-e1.md)

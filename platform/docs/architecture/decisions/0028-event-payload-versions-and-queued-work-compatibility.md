# ADR-0028: Event Payload Versions and Queued-Work Compatibility

**Status:** Accepted  
**Date:** 2026-09-22  
**Scope:** Durable events and their application/shared-service consumers

## Decision

Identify durable events by an explicit event type and payload version, in addition
to the stable event identifier and originating operation links under ADR-0012. Each
owning application/service defines its event payloads and supported interpretation.
A deployment must support versions that can still arrive from active producers or
remain in queued, in-flight or failed/retryable work. Retain old-version interpretation
until such work has been resolved and those producers have moved on.

Example: a worker supporting version 2 of `leave.request.submitted` still processes
an existing version 1 item according to version 1 meaning. Do not mutate the original
recorded payload or silently fill a missing consequential value from current state
merely to satisfy a new model. Explicit adapters/defaults are permitted where they
preserve the old contract. Existing authorization, privacy and business validity
checks remain binding; version support alone is not permission to deliver.

Unsupported event types or versions remain retained and flagged for technical
investigation under ADR-0024. They are not silently discarded, guessed at, acknowledged
as completed or retried indefinitely without a change that can resolve the failure.
A deployment must not knowingly strand still-required queued work.

Use explicit payload models and compatibility tests for MVP; no schema registry or
generic schema-management service is required. Version identity describes semantics;
a new version is needed for incompatible meaning/shape, not every unrelated code release.
Document supported versions and test representative old queued payloads in affected
release checks. Coordinate consumer/producer rollout and rollback compatibility;
removing a reader requires evidence that relevant live/retryable work and producers
no longer need it, not merely that the visible ready queue is empty.

## Impact and verification

- Acceptance: old queued item after deployment, old failed item retried, mixed producers,
  unsupported version retained, compatible optional additions, and preserved event identity.
- Scaffold: prove minimal envelope fields and explicit per-version validation/dispatch
  with compatibility fixtures; domain payloads remain owner-defined. No registry required.
- Shared UI: no new administrator field or business screen.
- Agent context: link this release compatibility rule in repository guidance.
- Documentation: builder and Leave requirements/tracker synchronized.
- ADR: complements 0012, 0020 and 0024; accepted originals unchanged.
- Planning only; no payload code, queue migration or runtime consumer modified.

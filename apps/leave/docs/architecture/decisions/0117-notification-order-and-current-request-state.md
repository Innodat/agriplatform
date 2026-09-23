# ADR-0117: Notification Order and Current Request State

**Status:** Accepted  
**Date:** 2026-09-23  
**Scope:** Leave notification presentation and delivery ordering

## Decision

Notifications describe the event that occurred, with its event date/time. Distinguish
that time from delivery time; delayed delivery must not imply a past event just happened.
Opening the request always checks current authorization and shows current request state.
Notifications do not overwrite or establish the authoritative business state.

Do not guarantee email arrival order or block a newer notification behind a failed
older notification. Preserve existing pre-handover relevance checks for obsolete action
requests under ADR-0116. Factual notices may still be useful; phrase them as historical
events rather than assertions that a superseded state is still current.

Example: approval is followed by cancellation, but the cancellation message arrives
first. The delayed approval notice describes when approval occurred; its link shows
the currently cancelled request. No additional ordering mechanism is required for MVP.
Existing privacy/minimal-content rules still apply to event descriptions and timestamps.

## Impact and verification

- Acceptance: reversed/delayed delivery does not alter request state; timestamps reflect
  event occurrence; links recheck permissions/current state; failed older work does not
  block newer delivery; obsolete action-request relevance rules remain.
- Scaffold/shared UI: existing notification rendering and link patterns suffice;
  no ordering engine or new control.
- Agent context: existing business-state and notification ownership rules suffice.
- Documentation: requirements, tracker and UX synchronized.
- ADR: complements ADR-0116 and platform delivery/identity rules; originals unchanged.
- Planning only; no notification code, delivery or runtime behavior changed.

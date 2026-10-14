# ADR-0131: Discreet Unread Indicator for Other Accessible Organizations

**Status:** Accepted
**Date:** 2026-10-14
**Scope:** Leave notification bell and organization selector
**Complements:** [ADR-0055](./0055-ngo-scoped-notifications-and-badges.md),
[ADR-0056](./0056-notification-read-state.md),
[ADR-0071](./0071-concise-summary-and-header-ngo-context.md),
[platform ADR-0046](../../../../../platform/docs/architecture/decisions/0046-application-availability-and-access-scopes.md).
Accepted predecessors remain unchanged.

## Decision

The bell/panel contains only the currently selected organization's notifications and
unread count. The organization selector menu shows permitted unread-count badges
beside accessible organizations, without message previews or business-record details.

When another accessible organization has unread notifications, show a discreet dot on
the closed selector. This is count-only awareness, not a combined inbox or aggregate
bell badge. Use an accessible text equivalent; color alone cannot convey the meaning.
Recompute the indication against the current selected organization and current access.

With exactly one accessible organization, hide the selector and its dot, keep the
organization name visible in the header and show its notification bell normally.
Switching organizations loads that organization's authorized inbox and preserves
existing draft-save/switch safeguards. Revoked/disabled access removes related count/
indicator exposure; count failures are not fabricated zero/unread assertions.

Unread indicators remain separate from required approvals/employee responses. Opening
or marking notifications read does not satisfy those business actions.

## Impacts and verification

Update written shared/Leave notification UX, requirements and Story 3.26/3.27 coverage.
Test A:2/B:3 with active A bell two, selector badges two/three and other-org dot; switch
to B with its inbox/bell three and recomputed other-org indication. Test single-org hidden
selector, unread only in the active org with no other-org dot, read-state changes,
revocation, stale counts/replies, unavailable counts and keyboard/screen-reader behavior.

Scaffold/shared UI: prove reusable opt-in organization selector/count indicator integration
with first consumers; do not create synthetic organizations for account/public applications.
Leave owns its authorized destinations and business response indicators. Agent context:
existing rules suffice. Additive presentation decision; immutable predecessors unchanged.
No code/data/notifications or implementation/readiness permission.

---
title: 'Keep cancelled Identity actor-display failures out of diagnostics'
type: bugfix
created: '2026-10-27'
status: done
route: oneshot
baseline_commit: f116f05a590d7500e3b61b4a6783d441a872e3d4
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Fix the confirmed Python3.15 diagnostic disclosure when an isolated Identity actor
display HTTP request is cancelled and its injected reader fails during cleanup.
Given caller cancellation, repeated cancellation or timeout plus a cleanup exception,
the owner must await the reader, preserve cancellation/deadline semantics and prevent
raw exception/message/traceback diagnostics. Ordinary reader failure still returns
the existing safe503; successful labels and all wire contracts stay unchanged.

Use a private non-raising task outcome, following the proven KDG pattern without
importing another owner's implementation. First observe actual HTTP regression RED.
Never suppress global logging or detach work. Preserve the second cancellation at
the original deadline, cooperative cleanup and no late success. The user's “next”
authorizes this bounded repair. No KDG consumer implementation, active mount,
credentials, SQL/native/migration/grant/resource, dependency, UI/Leave, deployment,
push or cleanup work. Never access the prohibited KDG migration fixture.

</frozen-after-approval>

## Implementation Notes

Planning: no intent gaps or irreversible action; small footprint in
`services/access/actor_display_http.py` and `services/access/tests/test_actor_display.py`,
plus existing owner/KDG evidence and handoff corrections. BMAD oneshot implements
inline; independent oneshot blind review follows. Concurrent dirty work is authorized
and preserved. Current coordinator model/usage/headroom are not exposed.

Reference: [composition prerequisite](../../apps/kdg-capture/docs/audit-display-composition.md#concrete-identity-prerequisite-found-during-planning).
Existing retained Python: `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
Verify new regression first, then complete actor-display suite and affected synthetic
capability/organization/People HTTP tests. Retain exact source-bound RED/GREEN and
safe diagnostic results. Recheck isolated exporter/generated/compiler contracts;
capture protected active/dependency bytes before changes. All subprocesses bounded.

Four actual HTTP no-diagnostic regressions failed before repair, then passed after
the private outcome wrapper. The shielded task returns a redacted result for ordinary
exceptions; only uncancelled owners unwrap it. Cancelled attempts consume privately
and preserve original CancelledError, deadlines, second cancellation and awaited task
ownership. Changed runtime scope is only `services/access/actor_display_http.py`;
test scope is only `services/access/tests/test_actor_display.py`. Owner/KDG contract,
evidence and handoff documents will record the completed prerequisite.

Actual checks:85 actor-display tests,127 affected HTTP tests, isolated exporter and
generator freshness, strictTS7.0.2 all pass. Exact logs/source capsules:
`/tmp/actor-display-cleanup-fix-e_ezl9lo/`. One-shot independent review returned no
supported findings and separately passed85 tests. No new deferral. Replaying the
original actual-ASGI diagnostic confirms zero events with cancellation preserved.
All12 protected active/schema/generated/dependency files remain unchanged.

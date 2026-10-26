# Protected own-edit context — 2026-10-26

The isolated candidate GET `/api/v1/captures/{capture_id}/edit-context` returns current
original-owner detail, the exact original questionnaire, editable fields
`observation_date` and `answers`, and independent own-read/own-edit observations.
Each observation retains its actual verified account, durable actor, membership,
typed scopes, decision ID and checked_at; expiry is exactly seven days later.

Both current Access checks finish and agree before checkout. The existing PUT
authorization wrapper retains its behavior while sharing the small pair-returning
operation. The context handler has a read-only direct execute method and transaction.
It requires no create permission or current child assignment/active status. Missing
and foreign captures return the same safe404. No history receipt is manufactured and
no command, overlay, pending operation or local observation is written by this API.

One original ten-second budget covers checks, worker admission, checkout, query,
release and final serialization. Worker ownership lasts until unwind on cancellation.
The independent detail bound is512KiB and complete UTF8 envelope bound544KiB.
Responses/errors remain private/no-store with stable identifiers.

The strict transport validates the whole closed envelope, original details, exact
editable fields and agreement of both independent observations. An Auth execution
lease pins account/org and fences every result before release. Shared exact
observation validation is KDG-owned and reused by history and edit-context. It does
not infer stronger authority or establish a generic transport framework.

The owner schema/client chain is `edit_context_openapi.py`,
`export_edit_context_openapi.py`, `edit-context-openapi.json` and
`contracts/edit-context-generated`. History's stale no-renewal description is corrected
through its owner; its exact own-read behavior remains covered. Canonical observation
metadata stays aligned across both schema owners and the common runtime validator.

Use retained Node26.11.1, TypeScript7.0.2 and dependency capsules from
[offline history evidence](OFFLINE_HISTORY_EVIDENCE.md). No dependency installation is
part of this proof. Exact executed argv, working directories, results and source/log
references are recorded in [the machine record](evidence/own-edit-context-20261026.json).

Scaffold impact: reuse existing generated Auth, transaction, schema-client and IDB
primitive owners; the fixed-org original-record/edit authority contract is KDG domain
logic. Shared UI and agent-context impacts: none. Documentation appends current
contracts and prepends the handoff while retaining earlier evidence. ADR impact:
inherited accepted decisions; no accepted ADR changed.

All authority/storage is synthetic. This proof does not establish actual PostgreSQL
permissions, joins, read-only transaction effects or native-driver cancellation/drain.
That explicit activation prerequisite remains deferred. No UI/editor/Leave, local
edit Save/queue, service worker/browser/default-startup activation, real accounts or
Access, DB/Docker qualification, migrations/provisioning, deployment/production/pilot
or cleanup occurred. Fingerprints/HMAC remain deferred.


| Requirement | Executed evidence |
|---|---|
| Current independent read/edit, matching actor/member/scope before checkout | `test_edit_context` and `test_edit_context_http`; synthetic loopback current-denial/mismatch cases |
| Original questionnaire, immutable facts, inactive/unassigned child, safe foreign404 | Context handler/HTTP suites and create/edit/context loopback |
| No write effect, exclusive unwind, total deadline, safe failures | Direct read-only execute test, HTTP cancellation/error/timeout cases; existing PUT regressions |
| Closed whole response and independent byte bounds | Context transport tests:512KiB compact Unicode detail at/+1,544KiB whole envelope; generated contract error validation |
| Exact seven-day observations, fractional calendar rollover | Shared validator positive/refusal cases and both owner metadata suites |
| Session replacement and late headers/body | Context Auth consumer and loopback lease fences |
| Existing history/cache and scaffold compatibility | Isolated Chromium IndexedDB regression, strict TS7.0.2, all six contract owners and five scaffold parities |

Review triage records thirteen findings: ten addressed (including two reports of the
same detail-bound coverage gap), two rejected with evidence and one native PostgreSQL
qualification prerequisite deferred. No application architecture change was required.

The pre-review broad run exposed an older edit timeout test's40ms scheduling
assumption: its SQL phase could miss entry under load. The correction uses the
existing controllable clock to expire the original ten-second budget only after the
intended phase enters. Ownership, unwind and503 expectations stay unchanged; exact
old test bytes, the failing run and focused corrected proof are retained. The initial
restricted characterization launch stalled; a later exact baseline replay passed.
That replay is not represented as having preceded refactoring. Prior full-suite
evidence also covers the unchanged baseline authority implementation.

Final source-bound run: 313 backend tests, 16 loopback groups, 61 isolated Chromium IndexedDB checks,127 direct tests and four fixture guards pass. All six strict adapter configurations, twelve schema/client freshness checks and five scaffold parities pass. All575 compiled Auth/client tests pass.

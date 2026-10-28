# Online audit display composition contract — 2026-10-27

Status: design defined; the concrete Identity owner prerequisite below is repaired
and independently reviewed. See [repair evidence](../../../services/access/ACTOR_DISPLAY_CANCELLATION_EVIDENCE.md).
The isolated backend candidate is now implemented and reviewed; see
[backend evidence](AUDIT_DISPLAY_BACKEND_EVIDENCE.md). The inert browser request
adapter remains separate. Design baseline `f116f05a590d7500e3b61b4a6783d441a872e3d4`;
backend delivery baseline `c88c753fc46d6d5caf296ef3b2ec87370b7f8dc1`.
This is the KDG-owned contract. The later explicit `api/runtime.py` administrator
policy composes this reviewed handler with history/detail and preserves their
owned lifespans and schemas; see [configured startup](../api/README.md#configured-administrator-reads).
The earlier isolated evidence does not establish native/real-authority qualification
or portal/session integration. Story3.1 acceptance remains separately tracked.

Inherits [Story 3.1 AC-1–5](epics.md#story-31-view-authorized-khula-observations-and-administrator-audit-details),
the [unchanged audit API](contracts.md#bounded-online-audit-metadata-api-subset--2026-10-26)
and [Identity display contract](../../../services/access/HISTORICAL-ACTOR-DISPLAY.md).
Identity owns names/retention; KDG owns access, record selection and presentation.
Current retained names are not event-time snapshots. Employment, current assignment
and actor existence grant no record access or substitute historical identity.

## Closed combined response

Separate candidate route: `GET /api/v1/admin/captures/{capture_id}/audit-details`.
Accept exactly the existing audit capture identifier, optional limit (default30,
maximum100) and cursor (at most2,048 bytes). Reuse existing cursor validation and
binding unchanged. Reject unknown/duplicate query, nonempty body, organization,
actor/account selectors and browser service credentials. The current `/events`
route, its DTO, client and 64 KiB ceiling remain unchanged.

| Object | Exact fields |
|---|---|
| `AuditDetails` | `audit: AuditPage`, `actor_display: LoadedDisplays | UnavailableDisplays` |
| `LoadedDisplays` | `status: "loaded"`, `labels: Label[]` |
| `UnavailableDisplays` | `status: "temporarily_unavailable"`; labels absent |
| `Label` | Exact resolved/unavailable discriminated label from Identity's closed wire contract |

All objects are closed. `audit` is the validated original page, including original
owner, creator, latest modifier, actual event executors, nullable initiators, numeric
revision navigation and original next_cursor. Do not attach names to or mutate the
stored events. No answers, definitions, operational evidence, receipts, keys, Identity
account associations or extra authority/observation tokens enter this response.

Actual UTF-8 bounds: audit subtree64 KiB, successful Identity input256 KiB, error
input1 KiB, combined response321 KiB (`64 KiB + 256 KiB + 1 KiB` wrapper allowance).
Check actual serialized bytes before sending any response. Never trim events or names
to fit, expose a partial label batch, or change pagination because labels are large.
Label rules and request16 KiB/203-ID bounds remain Identity-owned.

## Authorized selection and execution order

1. Pin the bearer, configured organization, capture/query and one original ten-second
   monotonic Budget at entry. Validate the closed request. Verify current exact
   `kdg_capture.capture.read.all`, fixed-org admission, account, durable actor,
   membership and matching organization resource scope before checkout. No own
   fallback or offline observation. Retain existing SQL-entry freshness safeguards.
2. Execute the existing scoped audit worker with this same Budget. Await transaction
   completion, connection release and worker unwind; validate the coherent page and
   its byte bound. Never call Identity while the business read/coordination is held.
   Do not call the old HTTP route or unchanged `AuditReadHandler.execute` as a nested
   phase: both create a new Budget. Reuse app-local authorization/worker primitives
   or extract a minimal Budget-accepting seam with characterization tests first.
3. Derive the sorted distinct set of non-null `owner_actor_id`, `created_by`,
   `updated_by`, every included event's `executor_actor_id` and non-null
   `initiator_actor_id`. Do not include reader actor, owner account, cursor lookahead,
   other pages or browser-supplied IDs. There are at most203 IDs. Header provenance
   means the current audit page has a nonempty selection even on empty continuation.
4. POST that exact set and pinned org to Identity over authenticated owner HTTP.
   Current KDG access authorizes selection; Identity's dedicated display credential
   authorizes only its label projection. No application/service server imports,
   cross-owner SQL or browser call to Identity. Names remain data, never authority.
5. After lookup or safe label degradation, perform a fresh current read.all check
   using the same bearer/org and remaining Budget, with no business transaction held.
   It must match the original account, durable actor, membership, permission and org
   resource/admission scope. Known401/403 and setup errors remain owning safe outcomes;
   successful but changed binding fails503 `authorization_observation_expired`.
   Unavailable authority fails503; never publish the old page merely because labels
   failed. This check does not reload the business snapshot or make names historical.
6. Construct the closed aggregate, enforce byte/deadline bounds and return private/
   no-store JSON. No cross-request snapshot or guaranteed knowledge of a revocation
   occurring after the final check is claimed. Every new page/retry starts over.

## Dependency transport and budget

The factory receives an explicit fixed HTTPS Identity base URL and dedicated active
display service key, plus an optional synthetic transport. Validate URL/credential
configuration before execution; do not create ambient environment/database clients.
Allow no userinfo, query, fragment or browser-selected host/path. Use the exact owner
path; `trust_env=False`, no redirects, no bearer forwarding and only the server-held
display key. No new secret/provisioning or live caller configuration is created here.
Preserve distinct Access versus Identity credentials; never forward an Access key.

Let D be the original ten-second deadline. Reserve up to3 seconds for the final
Access check and250 ms for local finalization/owned unwind. Start label lookup only
when more than3.25 seconds remain; its absolute deadline is
`min(now + 3s, D - 3.25s)`. Otherwise skip lookup with temporarily_unavailable status.
The final Access phase is bounded by `min(3s, D - now - 250ms)`; when no time remains,
fail safe rather than publish. These reserves do not restart D or extend it on retry.

The label deadline includes connect, request, response headers/body, strict parse,
validation and owned cancellation/close. Reserve cleanup within it and use a
cancellation-cooperative transport. Bound streamed bytes regardless of declared
Content-Length; require JSON/private/no-store, reject public caching, redirects and
content encodings other than absent/identity. Reject duplicate JSON members, invalid
UTF-8, unknown fields, malformed scalar names and noncanonical UUIDs. All success
labels must match the exact requested set, org and order, with no duplicates/extra/
missing IDs. Validate independently of static generated types. Do not cache names.

## Failure and publication contract

| Situation | Outcome |
|---|---|
| Audit request/access/read fails | Existing KDG safe top-level error; no Identity call or old-page fallback |
| Valid Identity200, including unmapped IDs | `actor_display.status=loaded`, complete exact label list; unmapped per-ID status stays unavailable |
| Identity timeout/transport failure/503, invalid reply or service403/422 | No partial labels; temporarily_unavailable if final KDG authorization and total deadline still pass |
| Label work cancelled by caller | Await owned close/unwind and propagate cancellation; no response/publication, not a degraded success |
| Global budget exhausted or final authority fails | Existing safe error, no aggregate, no earlier labels/records disclosed |
| Valid aggregate but changed browser account/org/page/session or known role loss | Future inert client discards the whole result, including fallback/errors; never revive prior data |

Use the existing audit status/error-id pairs and KDG safe error envelope; do not leak
Identity error bodies, messages or service status as end-user authorization decisions.
All responses private/no-store, including errors. No implicit retries. An explicit
Retry repeats the complete authorized read and server selection, never just replays
an actor batch. Stable statuses drive localized “Name unavailable” versus “Names
temporarily unavailable” presentation in a later UI. Do not show UUIDs as normal names
or guess System/reader/capturer attribution. No loading UI is implemented here.

The later client pins caller, token, org, capture, query/page and session generation
before awaits. Validate aggregate/audit semantics, exact selected label set and bounds;
deep-freeze results only after validation. Recheck cancellation/current-generation and
monotonic deadline before and after stream reads and final publication. Clear page/name
memory on access invalidation; no IndexedDB, localStorage, service-worker/offline cache.
Server final authorization and client invalidation are separate responsibilities.

No raw names, batches, credentials, payloads or exceptions enter operational logs,
including asyncio diagnostics. Retain only safe operation/trace/error/timing fields.

## Concrete Identity prerequisite found during planning

Resolved — 2026-10-27: the record below describes the pre-repair baseline. Four
actual HTTP no-diagnostic cases failed before the private outcome change and now
pass; the complete owner suite passes85 and the original diagnostic reports zero
events. The owner repair and independent review are in the linked repair evidence.
This closes this prerequisite only; the KC consuming matrix remains planned.

At this baseline, `services/access/actor_display_http.py:read_owned` shields a task
that can finish with a raw reader exception during cancellation cleanup. Python3.15
`asyncio.shield` installs `_log_on_exception` after outer cancellation; retrieving
`task.exception()` later does not prevent that callback from forwarding the exception
to the loop diagnostic handler. Existing KDG `capture_create_handler._worker_outcome`
already documents and avoids this behavior with a private non-raising task outcome.

A synthetic actual-ASGI diagnostic confirmed the trigger on Python3.15.0: cancel a
valid lookup, then fail the injected reader's cooperative cleanup. The HTTP operation
remains cancelled, but one diagnostic event contains the synthetic private exception
message. Only counts/booleans were printed; raw diagnostic context was not logged.
This corrects the earlier owner's no-open-finding statement for this newly exercised
path. The existing81-test qualification did not establish this combined case.

Executed command (the no-disclosure check fails with exit1):
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python -I -B /tmp/kdg-actor-display-cancellation-diagnostic.py`.
Retained source and safe result: `/tmp/kdg-actor-composition-diagnostic-yeqc5h4s/`.
No real credentials, services or resource lifecycle operations were involved.

Required next repair: add the actual HTTP cancellation-plus-cleanup-error regression
to `services/access/tests/test_actor_display.py`, then make the owned task return a
private redacted outcome for ordinary exceptions, preserving cancellation propagation,
original deadlines, second cancellation and awaited ownership. Prove no diagnostic
message/traceback leaks on both caller cancellation and timeout cleanup failure.
Keep Access/KDG active startup, schema and generated wire bytes unchanged. Do not
silence global loop logging or merely swallow/detach the reader. Use BMAD Build with
RED/GREEN, affected checks and review. Consumer implementation waits for this repair.

## Consuming acceptance

HD-6/consumer HD-7 trace here. Backend portions execute in the linked evidence.
Update 2026-10-28: the [inert adapter](AUDIT_DISPLAY_ADAPTER_EVIDENCE.md) completes
synthetic client runtime validation and caller-predicate publication fencing for
KC-7/9. KC-5 visible presentation and actual portal/session invalidation remain
unqualified; this is not integrated browser or full Story 3.1 acceptance.

| Case | Given / When / Then |
|---|---|
| KC-1 | Given current all-read and an authorized two-owner page, when composed, then exact original metadata and selected owner/creator/modifier/executor/initiator labels survive; reader/lookahead/other-page IDs are absent |
| KC-2 | Given denial, wrong org, invalid cursor or failed audit, when requested, then no Identity I/O, checkout beyond existing guards or stored-page fallback occurs |
| KC-3 | Given slow checkout/read, when Identity begins, then transaction and connection are released and every phase uses the original Budget |
| KC-4 | Given malformed, foreign, duplicate, reordered, partial, oversized or improperly cached/encoded Identity replies, when composed, then reject all labels and expose only safe degradation after final authority succeeds |
| KC-5 | Given unmapped IDs versus service/transport outage, when displayed later, then per-ID unavailability and temporary batch unavailability stay distinct; null initiators never gain a label |
| KC-6 | Given expiry/cancellation, ignored transport abort or reader cleanup failure, when unwinding, then bounded owned cleanup completes without late success, detached work or diagnostic disclosure |
| KC-7 | Given authority loss/change during label wait, when final check runs, then no aggregate publishes; later browser switch/role loss also discards delayed success and error responses |
| KC-8 | Given maximum cursor/page/name sizes and delayed phases, when encoded, then64/256/321 KiB and original ten-second ceilings hold, with no automatic retry or pagination changes |
| KC-9 | Given owner and candidate schema/client exports, when generated and consumed, then statuses/errors/closed fields and runtime rejection match, with active existing exports unchanged |

The backend-only candidate lives in `write-candidate/audit_display.py`,
`audit_display_http.py` and `identity_actor_display.py`, with
`write-tests/test_audit_display*.py`, isolated export/generated types and fake
Access/storage plus real synthetic Identity HTTP. Missing-route HTTP404 RED was
observed first; existing audit/worker/Budget source stayed unchanged without seam
extraction. No native DB, active mount or browser integration was performed.
The separate inert web request adapter is now implemented and reviewed; its evidence
records the client part of KC-7/9 within synthetic fetch/stream scope. The
[next readiness assessment](admin-next-readiness.md#story-31-next-bounded-delivery-assessment--2026-10-28)
selects a pure audit presentation model. Neither adapter nor backend proof establishes
mounted browser/session/device behavior or current rendered-data invalidation.

Impacts: scaffold—reuse existing bounded transport/budget primitives; no new neutral
promotion before a proven consumer; shared UI—none yet; agent context—unchanged;
docs—this contract, Identity correction, BMAD and KDG handoff; ADR—existing0022/0023/
0031/0056 govern, no accepted ADR edits. Release safety remains unchanged. No Leave,
questionnaire editor, native/migration/grant/resource, dependency, real account,
deployment/production/pilot/push or cleanup work. Never access the prohibited fixture.


## Inert consuming presentation and memory state — 2026-10-28

The [presentation/state consumer evidence](AUDIT_REVIEW_CONSUMER_EVIDENCE.md) records
synthetic KC-5 label semantics and KC-7/9 caller-driven invalidation/publication/full-read
Retry over the completed adapter. Pure immutable presentation preserves exact header
and event attribution, current names, times, revisions, order and cursor. One-context
review state clears retained data on invalidation/abort/close, rejects old overlapping
results, and retries only through an explicit full authorized aggregate read.
This updates the earlier future-consumer statements only for the isolated scope.
Actual mounted UI, Auth/session/all-read admission, role-loss notifications and prior
renderer references remain outside this proof. No new owner or wire contract.


## Explicit synthetic portal consumer — 2026-10-28

The [portal preview](ADMIN_PORTAL_PREVIEW_EVIDENCE.md) now renders actual adapter/
projection outcomes with generic Auth lifecycle fences in an explicit loopback browser
host. Browser history enrichment selects only the five returned record IDs and uses
one audit-details limit1 read per row within the original executing-read deadline;
there is no browser Identity batch endpoint. Detail plus audit must match immutable
identity and latest revision/update facts before publishing. Failed/partial enrichment
withholds all rows; valid temporary name degradation remains distinct. This establishes
synthetic visible KC-5 and mounted client KC-7/9 evidence, not real owner/native/device
activation. Existing app startup and wire contracts remain unchanged.

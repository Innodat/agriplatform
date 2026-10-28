# Identity historical actor display contract — 2026-10-27

Status: contract defaults agreed by the user's subsequent “next”; credential and
projection design closed below. The isolated synthetic HTTP candidate is implemented
and its owner checks and three-layer review passed. The later cancellation-diagnostic
prerequisite is now repaired with actual RED/GREEN and independent review; see
[repair evidence](ACTOR_DISPLAY_CANCELLATION_EVIDENCE.md). The
[composition prerequisite record](../../apps/kdg-capture/docs/audit-display-composition.md#concrete-identity-prerequisite-found-during-planning)
retains the original discovery. See
[delivery evidence](HISTORICAL_ACTOR_DISPLAY_EVIDENCE.md). The later
[native prerequisite](ACTOR_DISPLAY_NATIVE_EVIDENCE.md) now has an implemented
Identity28 projection and restricted reader with reviewed synthetic ON evidence.
No active-service mount or real credential is implemented. Identity owns this contract within the existing
Access-hosted Identity boundary. KDG owns record authorization and actor selection.
Baseline: `29763767fc3bb2895fea2500283759975f826d81`.

Inherits [ADR-0056](../../platform/docs/architecture/decisions/0056-durable-actor-registry-separate-from-login-accounts.md)
and the [Identity owner contract](../../platform/docs/architecture/contracts/identity-access-employment-e1.md#read-write-and-adoption-boundaries).
Consumer: [KDG Story 3.1 AC-2/3/5](../../apps/kdg-capture/docs/epics.md#story-31-view-authorized-khula-observations-and-administrator-audit-details)
and its [existing audit API](../../apps/kdg-capture/docs/contracts.md#bounded-online-audit-metadata-api-subset--2026-10-26).
The following contract defaults are agreed; inherited ADR rules remain binding.
Later runtime deployment and native permissions require their own evidence.

## Ownership and permitted selection

Operation: `POST /v2/identity/actor-displays`, service-to-service only.
Reuse existing owner HTTP/error-generation conventions. No new Identity service,
browser resolver or general account directory is introduced.

KDG first checks current fixed-organization `capture.read.all` and obtains the
permitted record/audit page. From that exact response it selects distinct non-null
owner, creation, update, executor and initiator actor IDs. Client-supplied actor IDs,
account IDs, search text and assignment targets cannot contribute to this set.
Null initiator stays null; never substitute the reader or original capturer for an
executor. Actor IDs and stored audit facts remain unchanged by resolution.

Identity authentication uses a dedicated server-held KDG display service
key with an allowlist for this operation and the fixed organization. Deny missing,
unknown, duplicate or wrong-service credentials and unconfigured organizations
before actor lookup. No public/anonymous/end-user-only call is authorized. Do not
reuse an operator, bootstrap or universal platform credential. Browser requests
never receive this key. Exact configuration and rotation design follow below;
no real secret is created or changed during this planning work.

Identity trusts the authenticated KDG backend to enforce the above record selection;
`org_id` is a service-policy bound, not an assertion that an actor belongs to that
organization. Identity does not read KDG tables, inspect capture IDs or duplicate
KDG capabilities. Actor existence confers no authority. A compromised trusted caller
could request unrelated IDs: this is the agreed service trust boundary.
No signed record proof or application callback is required.

## Label and retention semantics

Labels are the current retained Identity actor display name at lookup time,
including for old events. They are not names snapshotted at event time. A rename may
change a subsequently displayed label; it never changes historical attribution.
Account deactivation/removal does not remove the retained actor or require current
membership, employment, person linkage or assignment eligibility. System, Migrate
and registered service actors use their owned display name without synthetic Auth.

No account IDs, email, provider subject, person, employment, active/deleted status,
membership, actor key or operator configuration is disclosed. Unknown/unmapped IDs
return only `unavailable`, without guessing from an account with the same UUID or
silently creating/repairing a mapping. A known actor with invalid stored label data
is an owner integrity failure and fails the batch safely; do not misreport it as absent.

KDG uses the application-owned localized fallback “Name unavailable” for an
unmapped actor, retaining its durable ID internally. Do not expose raw UUIDs as the
ordinary label or silently call every absent actor “System”. An owner outage produces
separate “Names temporarily unavailable” feedback and an explicit retry; it is not
evidence that actors were deleted. Audit metadata may remain visible under its own
successful current authorization. A resolver result never authorizes record access.

## Closed wire contract

All objects reject unknown fields; UUIDs are canonical nonzero lowercase strings.
No query parameters, browser actor selectors, pagination or timestamps to request
historical names. JSON only; reject malformed/duplicate JSON members and invalid
UTF-8. Bound streamed input before parsing, regardless of Content-Length.

| Direction | Exact shape and bounds |
|---|---|
| Request | `{ "org_id": UUID, "actor_ids": [UUID, ...] }`; 1–203 unique IDs, lexical ascending order; at most 16 KiB actual UTF-8 |
| Success 200 | `{ "org_id": UUID, "labels": [Label, ...] }`; exact same IDs in request order; at most 256 KiB actual UTF-8 |
| Resolved Label | `{ "actor_id": UUID, "status": "resolved", "display_name": string }` |
| Unavailable Label | `{ "actor_id": UUID, "status": "unavailable" }`; display_name absent |
| Error | `{ "error_id": enum, "error": "Request could not be completed", "details": {} }`; at most 1 KiB |

203 covers the audit page maximum of 100 distinct executor/initiator pairs plus
owner/creation/update. The initial consumer uses one page, not a union of history
pages. Empty selection is a local no-call result. Display names are nonblank plain
text, at most 256 Unicode scalar values and 1,024 UTF-8 bytes, without control
characters; render as text, never markup. Reject invalid stored names without
truncating or normalizing actor identity. JSON escaping counts toward wire limits.
There is no partial-success envelope: absent labels are explicit per-ID results,
while malformed, extra, missing, reordered or duplicate result IDs invalidate the
whole response. Consumers validate org, shape, bounds and exact ID set before use.

| HTTP | error_id | Meaning |
|---|---|---|
| 403 | `service_access_denied` | Caller or organization not permitted; no actor existence disclosure |
| 422 | `validation_failed` | Invalid closed request, count, format or byte bound |
| 503 | `identity.actor_display_unavailable` | Deadline, dependency, owner integrity or invalid response; no existence conclusion |

All success and error responses use `Cache-Control: private, no-store`.
Follow [ADR-0031](../../platform/docs/architecture/decisions/0031-machine-readable-api-errors-and-localized-presentation.md);
clients branch on `error_id`, never English text. No raw exception, input echo,
registry contents or validation payload enters error details.

## Execution and consumer behavior

Identity total execution deadline: three seconds from operation entry, including
streamed input, bounded read, serialization and owned unwind. Read only through an Identity-owned least-privilege
projection; no provisioning, mapping writes or Access/KDG direct table reads.
Projection/privilege design follows below; the [native prerequisite evidence](ACTOR_DISPLAY_NATIVE_EVIDENCE.md)
records synthetic SQL/permission proof. Active runtime activation remains unqualified.

KDG invokes resolution after releasing its business read transaction; no external
wait inside row locks or business coordination. A future aggregate consumer shares
one original ten-second monotonic budget with its record/audit read; resolution
gets at most three seconds of the remainder. No reset per phase or automatic retry.
The current audit endpoint and its 64 KiB DTO stay unchanged. A separate consuming
delivery must define its complete result shape and combined byte limit before code.

Bind each result to the original request, account, organization, record, page and
session generation. Cancellation, role/access loss or account/scope switch prevents
late publication, including failures. Display lookup cannot revive stale record
authority. No IndexedDB, service-worker cache, localStorage or offline name directory.
Optional in-memory labels live only with that authorized page and clear on invalidation.
Retry follows fresh record authorization and server selection; do not replay arbitrary IDs.

Log only safe operation/trace/error/timing fields. Never log keys, names, full actor
batches, request/response bodies or provider/business payloads, including exceptions.
No audit write is needed for this read and no receipt or run identity is returned.

## Acceptance plan and readiness

The matrix defines acceptance; executed owner-only synthetic results are recorded
in [delivery evidence](HISTORICAL_ACTOR_DISPLAY_EVIDENCE.md). The missing-operation
POST404 failure was retained before implementation, followed by focused owner and
affected HTTP/generated-client checks. Test doubles do not prove SQL privileges or
real Identity authority.

| Case | Requirement and expected proof |
|---|---|
| HD-1 | Retained account, removed-account, System/Migrate/service labels resolve; rename changes label only; IDs/executor/initiator remain original |
| HD-2 | Browser/end-user-only/wrong/duplicate key and foreign org denied before registry I/O; no actor enumeration through denial responses |
| HD-3 | Unknown mapping returns unavailable; current-account UUID equality, recreated account, absent employment/membership and assignment eligibility never substitute identity |
| HD-4 | Strict shape/UUID/order/duplicates/count/Unicode/byte bounds, streamed oversize and exact response ID/org checks; invalid owner evidence fails safely |
| HD-5 | Timeout, cancellation, malformed reply and outage remain distinct from unmapped labels; no-store on every outcome; sensitive logs/errors absent |
| HD-6 | KDG derives only authorized page IDs, excludes null initiators, releases transaction before HTTP; shared budget, switch/role-loss and late-publication protections hold |
| HD-7 | Owner OpenAPI exports and generated types match all success/error models; consuming boundary rejects incompatible replies |

The isolated synthetic owner delivery is implemented in the candidate files below,
with actual acceptance RED/GREEN recorded separately. Formal review is pending.
KDG consumer composition follows independently
with its DTO and authorization tests.

Native database/privilege changes, real accounts/services, migrations, resource
lifecycle, UI/session/startup integration, release and full Story 3.1 remain gated.
No dependency changes, deployment, push, cleanup or prohibited fixture access.

Impacts: scaffold—no promotion until first proven neutral consumer; shared UI—no
component yet, fallback text belongs to KDG; agent context—existing boundaries suffice;
documentation—this owner contract and linked KDG/BMAD handoff; ADR—implements existing
0056/0022/0023/0031, no accepted ADR edits or new architecture decision required yet.

## Exact credential policy

The isolated candidate receives an explicit configuration mapping, never an implicit
production environment or database URL. It recognizes:

| Input | Rule |
|---|---|
| `KDG_ACTOR_DISPLAY_SERVICE_KEY` | Active credential; 32–256 visible ASCII characters, no whitespace |
| `KDG_ACTOR_DISPLAY_PREVIOUS_SERVICE_KEY` | Optional distinct credential, same bounds, accepted under exactly the same policy during coordinated rotation |
| `KDG_ACTOR_DISPLAY_ORG_ID` | One canonical nonzero UUID; fixed Khula organization, supplied by the authorized environment rather than hardcoded or browser-selected |

All absent means disabled: requests return private 403 before body/provider reads.
Partial, empty-present, malformed or duplicate configuration fails construction with
only `actor_display_configuration_invalid`. Active key and org are both required
if any input is present. Reject key equality with any other supplied `*_SERVICE_KEY`
value, including the existing KDG, Access-consumer and owner/setup credentials.
Keys and configuration representations must never appear in exceptions/logs.

Require exactly one `X-Service-Key`; reject any `Authorization` header, even empty,
before body reads. Compare candidate credentials without ordinary string equality;
accept only this endpoint and configured org. No CORS/browser setup is added.
Same trusted org policy applies to active and previous keys; neither confers other
Identity/Access permission. Org mismatch is 403 before projection invocation.

Rotation procedure, not executed here: configure a new active key while retaining
the old one as previous; switch the KDG server configuration; verify new-key requests;
remove previous and verify old-key denial. If coordinated checks fail, retain the
known-working overlap while investigating. No credential is written to repository,
browser state, documentation or command output; real secret provisioning/rotation
and deployment remain outside this delivery.

## Exact read projection boundary

The synthetic implementation takes an injected async reader with the conceptual
signature `read(actor_ids: tuple[UUID, ...], deadline: float) -> rows`.
The deadline is absolute monotonic time from the original HTTP operation. The
reader returns at most one closed `{actor_id: UUID, display_name: str}` row per
found requested ID, in any order; omitted IDs mean unmapped. It returns no null
names, actor kinds, account associations or organization ownership assertions.
Reject duplicate/foreign IDs, extra fields and invalid names as batch integrity
failure. Assemble output in exact request order; never infer absence after a reader
exception or timeout. Cancellation is propagated and owned cleanup is awaited.
No process-global label cache, reader configuration, URL or connection is created.

Native design, implemented through the reviewed controlled Identity28 prerequisite:
Identity owns
`identity.actor_displays(uuid[]) RETURNS TABLE(actor_id uuid, display_name text)`.
It validates nonzero unique input IDs and 1–203 cardinality and selects only
`identity.actor.id/display_name` for those IDs in one read snapshot. It never joins
Auth, account_actor, membership, People, Access or KDG tables. The current registry
is global; HTTP service policy binds org before this call. Missing actors remain
missing, independently of any account or employment lifecycle.

Use a fixed-search-path SECURITY DEFINER function owned by the established Identity
owner and a dedicated `identity_actor_display_runtime` login. The runtime role gets
only connection/schema usage and this function's EXECUTE, no registry table reads,
writes, actor registration or operator routines. Revoke PUBLIC/other callers'
execution; inspect actual inherited privileges before qualification. Within a short
read-only transaction, the native adapter passes only the selected UUID array as
bound data and uses statement/lock timeouts bounded by the original remaining budget.
This function/role requires controlled migration before later runtime activation,
previous-version compatibility, restricted-role denial/rollback/retry evidence and
release recovery under ADR-0020. The later bounded synthetic native delivery adds
the SQL/role/migration and exact evidence without activating the current service.

The private reader requires explicit nonempty host, port, database, user and password
with exactly `identity_actor_display_runtime` as its login. Incomplete inputs never
fall back to PGHOST/PGUSER. Service selectors and nonempty ambient PGHOSTADDR,
PGSERVICE or PGSERVICEFILE fail construction/acquisition safely; the reader does not
mutate process environment. Task-local driver-log filtering preserves unrelated
task logs while removing this operation's raw dependency diagnostics.

Source check: `identity-migrations/versions/0002_actor_registry.py` retains rows
independently of live Auth and caps persisted names at 200 characters. The wire's
256-scalar defensive bound does not authorize widening that schema. Existing shared
`capability_contract.decode` permits 64 KiB; do not reuse it unchanged for this
operation's 16 KiB streamed-input limit or reset the three-second total deadline.

## Selected synthetic delivery and verification plan

Ready scope: isolated owner HTTP factory, strict models/decoder, explicit credential
policy, injected projection and candidate-only OpenAPI/generated wire types. Reuse
installed dependency versions and the existing platform client generator. Keep
`main.py`, active `openapi.json`, existing generated clients, migrations, grants and
deployment configuration unchanged. Nothing is mounted in a running service.

Suggested owned files: `actor_display_contract.py`, `actor_display_http.py`,
`export_actor_display_openapi.py`, `actor-display.openapi.json`,
`contracts/actor-display-generated/`, `tests/test_actor_display.py` and
`tests/actor_display_types.test.ts`, all beneath `services/access/`.
Generated artifacts must be produced by their owning exporter/generator.

Implement HD-1–HD-5 and the owner-generated portion of HD-7 in this slice. HD-6,
the consuming half of HD-7, native permissions, actual retained-account lifecycle
and installed portal/device proof remain explicit later qualification. Synthetic
rows simulate lifecycle cases; they cannot prove real retention or authorization.

ATDD first: a minimal synthetic ASGI owner app without the candidate route receives
POST and returns 404 where HD-1 expects 200. Retain that actual HTTP failure, then
register the candidate router in the isolated test factory and implement focused
policy/model/reader behavior. An import error is not acceptance RED.

Planned focused command: `OWNER_PYTHON -I -B -m pytest services/access/tests/test_actor_display.py -q -p no:cacheprovider`.
Use the retained owner Python described in `CURRENT_ACCOUNT_ACTOR_EVIDENCE.md`,
rechecking its executable/dependencies before testing; no installations are authorized.
Then run the affected existing capability, organization-check and People-reference
HTTP tests, candidate export freshness, generated client freshness and strict
TypeScript 7.0.2 type checks. Resolve actual selected tool paths and exact commands
in the delivery evidence; this planning pass executes none of them.

Scaffold/shared UI: record no promotion for this narrow Identity-only first consumer;
revisit only when neutral behavior is proven. Agent context stays unchanged.
Documentation and evidence must state this is isolated synthetic owner proof,
not current service activation or completed KDG named audit presentation.

# Protected KDG create/retry handler — 2026-10-25

bmad-help [BD] selected the outer current-authorized create boundary after the fresh
transaction body. `write-candidate/capture_create_handler.py` supplies an unmounted
`CreateHandler.execute(connection,raw_command,authorization)` entry point. Qualification
uses MockTransport and recorded SQL connections only. No real Access/Identity, database,
Docker lifecycle, active migration, deployment or API route was used or changed.

## Implemented consuming contract

Construct the handler with a canonical configured organization UUID, protected HTTPS
Access origin and service key. Credentials are not browser input and are never logged.
The constructor performs no network or setup I/O. The embedding API must enforce one
Authorization header, bound request streaming/body size before buffering, and provide
an exclusively owned already-open connection through its bounded acquisition policy.
Connection acquisition is outside this callable's budget; it is a mounting prerequisite,
not a qualified behavior. No active transaction/autocommit connection is accepted.
Keep the connection owned until the handler and worker have finished/unwound.

The handler creates one ten-second Budget before parsing or HTTP checks. Structural
command validation, supported version and distinct capture/operation UUIDs precede any
lookup. Distinct IDs are a cross-field wire requirement (contracts.md:336), applied to
fresh and replay requests alike, rather than fresh child/answer/eligibility semantics. A normalized Bearer token goes only to the configured protected `/v2/check`.
Check current `kdg_capture.capture.create.all` first; only explicit 403/access_denied
selects a separate create.assigned check, under one total three-second external window.
Timeout, malformed/oversized/encoded evidence, redirects, unknown service errors or
missing durable actor never select another capability. Confirmed authentication, access
and actor-setup failures preserve their safe identifiers; unavailable checks fail 503.

The closed create-evidence DTO reuses Context's canonical account/actor/decision UUIDs,
strict positive bounded membership string, organization/own-account scope and UTC
checked-at validation. Exact requested permission, configured organization, account scope
and request-window timestamp are checked. Both permissions install `own_write`; all-child
eligibility never gives all-record ownership. Complete-response observation time is
captured before response/client cleanup and retained through worker scheduling. Starting
local work over one second later fails safely; cleanup does not renew authority.

Synchronous SQL runs through the existing Starlette/AnyIO worker adapter, with admission
bounded by the original remaining Budget. A retained, shielded task is awaited through
direct/repeated cancellation before the connection can be released. Cancellation may
still leave a committed operation; it never acknowledges or promises rollback. Admission
expiry prevents later SQL. The owner
transaction installs the same verified context and original Budget; no HTTP wait occurs
under its locks. It takes the operation lock and privately looks up the exact org/account/
create/operation key. Fresh absence delegates to the unchanged protected create body,
including its reentrant lock and repeated private absence check; no bypass flag was added.

Existing outcomes select the ACTUAL stored capture, scoped by verified owner account and
organization. Missing, foreign, unsupported or inconsistent evidence fails unavailable,
never unresolved or a disclosed receipt. The handler locks the stored child. Current
assigned authority requires a currently active assignment for the exact current membership
instance; all authority does not require assignment and still stays own-author. Incoming
capture/child/version/eligibility/answers never authorize or replace the stored target.
No fresh answer, published-version, eligibility or inactive-child validation runs on an
existing receipt. The original receipt/revision returns even if the current capture is
newer. Ordinary lifecycle changes only affect it through applicable current authority.

POST retry still needs current create authority on the stored child. After losing create
or assigned authority, current own-read GET recovery is the separate intended contract;
that GET is not implemented by this handler. No automatic grant/assignment renewal or
fallback from denied organization scope occurs. This follows contracts.md:45,618,665
and the current POST/GET distinction in prior outcome storage evidence.

Only after successful transaction exit, commit and final Budget check may execute return
its compact receipt. Commit failure or a late acknowledgement returns safe failure; it
never claims absence/rollback of a possibly committed operation. The client keeps its
original operation identity. Operational errors map through an explicit identifier/status
allowlist; SQL, upstream payloads, exception text and provisional receipts are not exposed.
`HandlerError` carries safe status/error_id for the future shared HTTP error adapter.
Mounting still requires the established error envelope, private/no-store and safe middleware.

## Acceptance and focused tests

The initial missing-handler test failed at import. A behavioral freshness test then
reproduced an actual omission: two seconds of transport cleanup did not refuse stale
authority. Capturing the observation before cleanup made it fail safely before owner SQL.
One test initially patched the global time module, producing an asyncio diagnostic clock
jump; it now replaces only the write helper's time dependency. Expected behavior unchanged.

The focused suite has 23 handler tests; the complete affected write suite has 80 tests.
The focused suite exercises exact protected request binding, confirmed-denial-only
capability selection, malformed/foreign/stale evidence, current actor/membership,
changed-body original-target replay, active/current stored-child assignment, unknown
outcome formats, safe fresh validation, commit failure, acknowledgement after deadline,
slow body timeout, a combined all-denial/assigned-response deadline, cleanup freshness,
worker admission expiry, repeated direct cancellation, driver autocommit refusal and
explicit safe configuration. A synthetic late-commit receipt then retry recovers its
original capture without a second set of inserts. This models orchestration, not storage. Recorded connections
verify SQL order/commit exits; they do not simulate native durability, RLS or rollback.
A sandboxed worker run stalled and was interrupted; the same synthetic tests pass using
the existing worker adapter outside that sandbox. No external service was contacted.

P = retained `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.

- `timeout 45s P -I -B -m unittest discover -s apps/kdg-capture/write-tests -p 'test_*.py'`
- Retained Node: `platform/builder-cli/scripts/sync-kdg-write.mjs --check`

Review returned six findings: five patched and the distinct-ID classification rejected
with the existing contract/spec and an explicit existing-outcome test. The reviewer
independently reran both worker regressions (two pass) and confirmed their fixes. No
review item remains deferred. Final counts, review dispositions and source bindings are recorded in
[the delivery receipt](evidence/create-handler-20261025.json).

## Release gates and reusable impact

The existing 43-case native create-body receipt remains historical proof of that source,
not native qualification of this outer handler. Restricted-role durable commit, actual
lost-response/replay, cross-connection duplicate/concurrency and worker cancellation
behavior require consuming qualification before mounting. Current Access was exercised
only through synthetic contract responses. This does not activate schema candidate 0002.
ADR-0020 controlled coordinated migration, compatibility with previous code, activation
blocked on migration failure and explicit recovery remain required; no startup migrations
or automatic reversal. The historical native metadata-hash discrepancy stays unresolved.

Every future KDG child/assignment writer must use the existing shared child coordination
lock before mutation. No broader parent grants, privileged locking function or general
workflow engine was introduced. Shared/scaffold transaction code and its tests are unchanged;
parity is checked. Existing write scaffolds provide synchronous transaction helpers, not
an asynchronous SQL handler owning a connection. The existing jwt_optional worker decodes
a token without such a connection. Consequently the new ownership/admission cases stay
with this consuming handler; no unrelated async runtime abstraction is added to scaffolds. Domain-specific permission and stored-resource policy stay KDG-owned.
No UI or agent-context change, new ADR or dependency baseline change. TypeScript 7.0.2 and
all concurrent work/resources/old receipts remain intact. Fingerprints/HMAC remain deferred.

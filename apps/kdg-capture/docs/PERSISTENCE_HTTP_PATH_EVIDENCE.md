# Candidate create, edit and recovery HTTP path — 2026-10-26

The candidate persistence path now includes `POST /api/v1/captures`, its offline
OpenAPI/generated TypeScript contract, `createCapture` and `createCreateEntry`.
The create consumer uses the existing Auth execution lease alongside the qualified
edit/recovery consumers. These remain separately imported candidate code; default API
startup, browser/editor, queue and saved-state feedback are unchanged.

POST validates one bearer, JSON media type, selector-free strict bounded input and
distinct original capture/operation IDs. Current verified account/actor/membership and
create-all or assigned fallback precede pool acquisition. Existing create/replay business
handlers retain stored-child assignment checks, original receipt identity and transaction
ownership. One original budget spans body receipt, authority, acquisition, SQL, commit
and release. Exclusive worker ownership survives cancellation until unwind; no provisional
receipt escapes failed commit/release. Lazy bounded engine policy is reused locally from
edit without changing its defaults. Normal and exceptional lifespans dispose owned engines.

The generated-contract client pins command bytes, session and scope before awaiting,
accepts only matching v1 capture.create receipts and returns safe typed errors. Existing
strict response, size, deadline and cancellation conventions apply. Auth replacement
suppresses old receipts/errors and releases only that execution. No result triggers
retry, refresh, sign-in, new operation, store/queue mutation or Synced feedback.
Synchronous wrapper capture/serialization cannot be preempted; the adapter budget starts
after wrapper capture. Cancellation or deadline after dispatch may still commit.

## Reproduction prerequisites

Run from repository root with the already qualified Node26.11.1 executable at
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node`.
The network runner also requires the approved retained npm installation at
`platform/deployment/.local/web-baseline-qualification/new-5/root/node_modules` and Python
at `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
A fresh checkout needs these qualified tool capsules restored before executing this
proof; this delivery does not provide or qualify a fresh install/provisioning workflow.
There is no automatic package install, floating-version or system-Python fallback.

Required pins are Node26.11.1, TypeScript7.0.2, Supabase SDK2.117.3 and Python3.15.0
with FastAPI0.143.0, uvicorn0.54.0, Pydantic2.14.1, httpx0.28.1, SQLAlchemy2.1.4,
psycopg3.3.6 and AnyIO4.15.1. The existing schema test adapter additionally requires
`/usr/bin/python3` with jsonschema4.10.3. See the authoritative
[approved dependency baseline](../../../platform/docs/architecture/contracts/scaffold-dependency-baseline-2026-10-14.md).
Restore compatible approved artifacts at the paths above; creating environments is
outside this delivery. Exact executable commands and working directories are committed
in the machine record; hashed private manifests retain detailed logs/capsules.

## Executed evidence

- 21 create HTTP cases and four schema/runtime contract cases pass.
- 90 create transport/entry cases pass; the full compiled Auth/client suite passes327.
- 199 explicit synthetic business/HTTP/contract tests and124 direct-source adapter/context regressions pass.
- Strict TypeScript7.0.2 create/edit/recovery checks, four scaffold parity checks and owner schema/generated-client checks pass.
- Seven loopback requirement groups pass through actual candidate POST/PUT/GET/context routes and business handlers, using synthetic Access and shared recorded transactional storage.

The network journey proves create1, edit2, original create1/edit2 recovery, duplicate
replay, receipt-only no-op, conflict, wrong-target acknowledgement refusal and verified
unresolved. Current denial/expired/mismatched/unavailable authority blocks acquisition.
Assigned replay rechecks the stored child; recovery remains available under own-read.
Malformed headers/selectors/body/version refuse safely. Fresh acquisition/SQL/commit
failures return no acknowledgement. A fresh release failure commits in the synthetic
model, returns no acknowledgement, and recovers exactly once by the original identity.
Late headers/body after Auth replacement remain superseded while current work succeeds.
Final model: two captures, four outcomes, three history entries,24 acquisitions/releases.
Normal fixture shutdown disposes all three owned synthetic engines.

This storage model establishes control flow and wire agreement. It does not establish
PostgreSQL constraints, native permissions/rollback or driver cancellation/TCP drain.
Existing historical native evidence remains source-bound and unchanged. Real current
Identity/Access, release compatibility/recovery and activation remain separate gates.

The client acceptance stub produced80 behavioral failures/10 passes before implementation.
The loopback non-dispatching fixture produced a behavioral failure after compiling and
starting correctly. Initial backend missing-module and nested-process permission failures
are infrastructure failures, not behavioral RED. The retained API refusal control is
explicitly a later replay, failing503 versus expected200. All failed attempts, fixture
corrections and controls are retained without rewriting unexplained expectations.

Exact commands, source/log hashes, selected source capsules and qualification limits are
in [the machine record](evidence/persistence-http-path-20261026.json) and its hashed private
manifests. The broad native-qualification verifier was rejected by automatic approval
review because it imports a retained native database fixture. The explicit synthetic
business/HTTP suites passed instead; no native qualification is claimed.

Scaffold impact: reuse existing generator, Auth lifecycle and transaction patterns; no
neutral template defect found. The shared engine policy remains app-owned. Shared UI,
agent-context and ADR impacts: none. Historical contracts prefix/handoff suffix and
dependency/startup baselines are preserved, including TypeScript7.0.2. No Docker, real
accounts/Access, provisioning, migration, Leave/editor, deployment/production/pilot or
cleanup occurred. The forbidden untracked migration fixture was never read/run/copied.
Fingerprints/HMAC remain deferred.

Final independent review: ten findings addressed, one rejected against the existing
explicit timing limitation, none deferred. Schema parity covers UTC timestamps,
nonblank eligibility references and unpaired versus valid supplementary Unicode;
the sibling edit schema was aligned through its owner exporter/generator. The retained
JSON Schema tool lacks an optional RFC3339 dependency, so its FormatChecker delegates
calendar parsing to stdlib datetime.fromisoformat with an aware time component. No new
calendar rules or dependencies were introduced. Synthetic storage now refuses unknown
SQL and wrong organization/account lookups. Three named fake-child controls and two
fixture guard tests pass; final327 Auth,199 backend and124 adapter regressions pass.
Final loopback still completes normally with no forced stop. Post-review records and
current source manifests are separate from all prior evidence.

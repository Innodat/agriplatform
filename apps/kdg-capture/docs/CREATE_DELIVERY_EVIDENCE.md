# Explicit saved-create delivery and receipt recovery — 2026-10-26

The unmounted `createCreateDeliveryEntry` delivers one selected completed local create.
It recovers the original operation before at most one exact POST, consumes the matching
receipt durably and imports authorized current detail. One Auth lease and total budget
cover storage, HTTP, final publication and release. Default/maximum total budget is
30seconds; individual HTTP phases get at most10seconds and remaining time. Transactions
finish before HTTP. No sender, scheduling, claims or startup is activated.

The local store provides `lookupPreparedCreate`, `prepareCreate`, `consumeCreateReceipt`,
`attentionCreate` and `denyCreate`. Immutable original pending/serialized/content fields
remain unchanged; version1 mutable delivery metadata holds receipt, attention and
readback revision. Point lookup/recovery requires current own-read, including after
creation expiry/denial. Every POST checks current authority server-side. Known local
creation denial blocks sending until explicit newer positive verification of either
create capability. Original setup expiry/current child-list absence alone does not
reject delayed saved work. The original eligibility reference is never substituted.

A committed receipt must match original account/org/operation/type/version/capture and
initial revision1. It supplies no server answers or audit timestamps. Actual readback
must match immutable owner/child/questionnaire/definition/device facts. At the receipt
revision, answers/date must equal the frozen create; later revisions may contain later
server edits. The original receipt revision stays1 while current baseline may advance.
Only receipt-bound current detail sets the exact record's create_status to Synced.
Readback alone does not acknowledge an uncertain create; receipt persistence alone
returns operation-level acknowledgement with readback unavailable, retaining pending
readback. Original local_capture and newer saved overlays/actions remain preserved.

Known assignment/eligibility/version/validation rejection sets only the selected
record/action to Needs attention. Current creation access_denied latches both creation
capabilities before a bounded own-read context probe; an uncreated capture's404 is not
used as a read-permission probe. Verified own-read preserves display; read denial or
unavailable probe conservatively locks within the execution fence. Auth renewal and
transient errors retain retryable original work. There is no internal retry loop.
Future automatic consumers must skip attention; explicit selected invocations remain
subject to current safeguards. Unknown/contradictory durable versions are retained
and blocked. Concurrent identical invocations rely on existing server idempotency.

## Verification

Exact commands, current source hashes, RED/GREEN frames and named checks are in
[evidence](evidence/create-delivery-20261026.json). The focused proof uses real Chromium
IndexedDB and controlled transport. The HTTP proof uses actual synthetic Python
create/recovery/read/context/edit handlers, Auth and real IndexedDB, beginning with a
real atomic local Save. It verifies committed response loss, later server edit/newer
local overlay, read-only recovery after creation denial, inactive-child prior
eligibility, assignment rejection, creation-only denial and read denial. Setup uses
the strict synthetic Provision DTO; actual Provision HTTP→Auth→Save was independently
qualified in the preceding committed feature. The new host reuses the historical
storage model and seeds one explicit43-character eligibility ref; old fixture source
and behavior remain unchanged.

Both proofs use retained approved Node26.11.1, TS7.0.2, modules, Chromium and Python
listed in prior owner evidence. No install occurred. Existing Auth skipLibCheck is
limited to upstream declarations; owner sources/configurations compile strictly.
Fixtures establish no actual PostgreSQL permissions, native rollback/performance,
physical device durability or release readiness. Existing native setup issuance and
browser update/device qualification remain gates. No dependency/resource cleanup.

## Delivery impacts

- Scaffold: reuse builder-owned Auth/IndexedDB primitives unchanged. Domain command,
  scope, receipt and rejection rules stay KDG; no demonstrated neutral defect requires
  a new shared abstraction. Five existing scaffold parities remain required.
- Shared UI: unchanged; explicit consumer remains unmounted.
- Agent context: unchanged; existing owner/synthetic/preservation guidance applies.
- Documentation: this evidence and machine record, append-only contracts, README and
  prepended handoff. Historical evidence and resources remain retained.
- ADR: existing accepted scope, session, logging, attribution, lifecycle, compatibility
  and first-commit-wins decisions apply; no new or edited accepted ADR.

Final qualification:18 commands pass, including219 focused checks,40 actual synthetic
HTTP groups and127 direct entry tests. Existing Save141/setup HTTP18/setup client87,
edit delivery73/edit HTTP29/reconciliation103/local edit92/history61/Auth575 and
existing HTTP16 remain green; all five scaffold parities pass. Reused342 backend tests
only after reconfirming all85 unchanged effective sources. All13 independent review
findings addressed; nothing deferred. Review also fixed the KDG-owned own-read probe
empty-chunk deadline and added actual duplicate invocation, same-partition independent
action, retained receipt fallback, Auth lifecycle, storage-failure and final-readback
denial coverage. The probe adapter is KDG-owned; builder Auth runtime/tests remain
unchanged and parity-qualified.

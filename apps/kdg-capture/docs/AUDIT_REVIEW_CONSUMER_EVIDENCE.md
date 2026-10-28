# Inert audit presentation and review consumers — 2026-10-28

Two successive ready Story 3.1 technical subsets consume the reviewed aggregate adapter
without mounting a portal. `web/src/audit-presentation.ts:auditPresentation` maps
validated loaded outcomes into immutable audit metadata and semantic name states.
`web/src/audit-review.ts:createAuditReview` coordinates one caller-bound in-memory
page with explicit load/retry, snapshots, invalidation and close. No all-read admission
is inferred from own-read, roles or a resolver result.

Presentation preserves original capturer/creator, current latest modifier, actual
executor and separate nullable initiator, committed event order and exact decimal
revisions/UTC microseconds/cursor. Names are current retained labels, not historical
snapshots. Per-actor unavailable and batch temporarily unavailable have distinct semantic
localization keys; only the latter carries an explicit retry indication. No approved
Afrikaans translations, UUID-as-name, guessed System or synthetic events are introduced.
Nonloaded outcomes never become empty audit results.

The review coordinator captures session/request and transport inputs at construction.
Each explicit load or Retry clears prior held content and performs the entire authorized
aggregate GET under the adapter's maximum ten-second deadline. Overlapping reads abort
owned earlier work and fence both late success and late errors. Explicit invalidation,
external abort or a failed current-generation check clears retained content and makes
the instance terminal; close also releases its input binding and listener. Snapshots
recheck the caller predicate. A fresh context requires a new instance. There is no
implicit retry, persistence, offline authorization or accumulated archive.

The caller still owns actual administrator admission, scope/session/access invalidation
and rendering. A predicate cannot notify this coordinator by itself: the future owner
must call invalidate (or abort its signal) when authority changes. Reading a snapshot
also checks currentness. Previously returned immutable objects cannot be revoked; this
module does not establish that a mounted UI immediately clears them. No Auth/browser
subscriptions, startup hooks or real services are connected.

## Qualification and traceability

Actual acceptance REDs compiled successfully before implementation:

- Presentation `run-66003804-570f-4639-bcd4-cd58ad99db8b`: valid cross-owner input crossed
  the existing adapter, then the missing projection returned invalid_response instead
  of loaded. Initial wrapper `EPERM` is retained separately and is not an ATDD RED.
- State `run-009f5062-e691-48ff-abdc-544d302c4970`: the missing coordinator remained idle
  instead of exposing the loaded model, before the invalidation assertion could run.

Focused GREEN passes **9 presentation cases**, **16 state cases**, strict TypeScript
**7.0.2** compile/type/emit, **109 aggregate adapter cases** and **73 original audit
cases**, using retained Node **26.11.1**. The matrix includes consuming actual adapter
validation, unmapped/outage distinction, header-only/empty continuation, renamed service
labels, maximum page/bigint/microsecond preservation, unchanged input/deep immutability,
nonloaded reads, overlapping ignored-abort results, six caller generation switches,
external abort, close, denial/unavailable refresh and explicit retry after timeout.
These are synthetic fetch/stream/in-memory cases, not integrated browser evidence.

Traceability: A21.admin-audit-attribution and Story 3.1 AC-2/3 receive inert presentation
coverage; KC-5 semantic mapping, KC-7/9 caller-driven memory/publication fences and safe
full-read Retry are consumed. Current server read.all remains the unchanged backend's
responsibility. Story AC-1/4/5/6 are not satisfied by this isolated consumer proof.

From repository root, using the retained Node path:

```sh
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/audit-presentation-proof.mjs
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/audit-review-proof.mjs
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/audit-display-adapter-proof.mjs
platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/node/bin/node apps/kdg-capture/web/tests/audit-adapter-proof.mjs
```

The source-bound [machine record](evidence/audit-review-consumers-20261028.json) links
retained capsule hashes, exact argv/results/logs and attempts. Each proof captures its
inputs before compile/test and checks they remain unchanged. Process-sandbox `EPERM`
required running local compiler/test subprocesses through approved escalation; no
service, network or database was used. Backend/native/device tests were not rerun.

## Review, impacts and remaining gates

Presentation independent blind review reports zero supported findings and independently
passed strict types and nine cases through direct commands after wrapper EPERM.
State independent blind review also reports zero supported findings and independently
passed strict types and all16 state cases through direct capsule commands after wrapper
EPERM. Retained evidence/source digests match; no new deferrals. Both BMAD delivery
specs are done; enclosing Story 3.1 remains incomplete.

Scaffold: existing generated/immutable/transport primitives reused; new audit semantics
stay KDG-local, no proven neutral pattern requires promotion. Shared UI/agent context
unchanged. Docs: readiness/composition/test map and handoff reconciled together. ADR:
existing 0022/0023/0031/0056 and ADR-0061 apply; no accepted ADR changed. Release tooling
unchanged. Model/effort, token usage and model-only elapsed unavailable; proof logs record
test timings, not model work.

The [final Story 3.1 gate checkpoint](admin-next-readiness.md#continuous-story-31-delivery-checkpoint--2026-10-28)
explains why full completion is not plausible within retained exclusions. Mounted
portal/history/detail/audit, real all-read admission and session invalidation,
connectivity/cache separation, accessibility, installed devices, native Identity
retention/projection permissions and controlled release remain separately unqualified.

No UI/editor/Leave, Auth/session/startup/browser/worker/queue activation, real services/
accounts/credentials, native DB/Docker/migrations/grants, dependency changes, deployment/
production/pilot/push or resource lifecycle/cleanup. All preexisting runtime/generated/
schema/dependency source bytes, concurrent changes and historical evidence/resources
are preserved. The prohibited fixture was not accessed/run/copied/hashed.

Final preservation: all620 protected preexisting KDG files match the initial manifest.
The five intentionally reconciled documentation files retain their previous handoff
history. Concurrent Scribeswell edits arrived during verification and were left intact;
no non-KDG changes are included in this delivery. Document check
`python3 /tmp/kdg-audit-presentation-20261028/check_delivery.py` passes21 local links/
anchors, new-file whitespace and scoped `git diff --check`. The initial whole-workspace
unchanged-diff assertion noticed those concurrent edits; it is not reported as passing.
Verification was narrowed to owned paths and protected KDG sources, without restoring
or rewriting concurrent changes.

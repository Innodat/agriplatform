# Protected setup contract and explicit consumer — 2026-10-26

An unmounted candidate `GET /api/v1/provision` now produces current setup for a fixed
organization and explicitly configured questionnaire. `createProvisionEntry(...).load`
consumes it under an admitted Auth execution lease. This supplies the missing typed
input boundary for future pending-create local Save; it does not persist setup, save
a capture, install a PWA or activate a normal application route.

The API independently checks own-read, own-edit, create-all and create-assigned. Entry
own-read is required. Known edit/create denial yields a null positive observation,
while unavailable or mismatched verification fails the complete request. Positive
checks must agree on account, durable actor, membership and organization, retaining
each actual decision/time. Every positive observation expires exactly seven days
later. No stronger right is inferred from another capability or a local reference.

The response includes schema version1, the exact published questionnaire/version and
original definition, and a complete bounded child set. Create-all selects active
organization children without fabricated assignments; assigned creation selects
current same-account/same-membership assignments. Child/assignment revision evidence
and observed times remain separate from Access decision evidence. No account/org/
questionnaire selector is accepted from the browser.

Within a short owner transaction, deterministic child locks precede current child/
assignment rechecks and eligibility issuance. A new opaque43-character URL-safe
reference binds account, membership, child/revisions, creation permission and verified
issuer actor. It grants no authority. General historical create references remain
opaque text up to200 code points. No capture, command outcome or history is created.
A response acknowledges references only after commit, connection release and final
validation; release uncertainty may leave committed references without a successful
response. Retries may issue new references; nothing prunes old evidence.

The state precedence is `not_permitted`, `no_published_questionnaire`,
`no_eligible_children`, then `ready`. A no-create response contains no children or
creation observation; it can retain permitted questionnaire metadata. Bounds are1000
children,1MiB complete UTF-8 response and the existing128KiB/50-question definition
limit. Overflow fails safely rather than silently truncating. These are resource
bounds, not a promise that every native1000-child request finishes in ten seconds.

One original ten-second server budget spans authorization, checkout, SQL, commit,
release and serialization. External checks precede locks. Request-body validation
checks that budget after each ASGI message, including empty immediate messages.
Cancellation retains worker/connection ownership through unwind. The browser adapter
validates the complete closed DTO and relationships, safe errors, caching and body
limits. Its original request budget includes admission-lease acquisition and final
publication/release. Late, aborted or replaced-session data cannot publish success.

Backend schema/export owns generated TypeScript; generated files are not handwritten.
Existing questionnaire validation is shared with own-detail, preserving original
answer validation.108 read/history tests characterized that extraction beforehand.
Broader client runs exposed pre-existing short-deadline fixture failures under host
load. Three affected entry tests now use controlled clocks/timers for deadline checks
and one-second normal fixture budgets. Production budgets and expected results stay
unchanged. Failed logs are retained separately from setup acceptance RED and final
qualification; all575 existing client tests pass.

Scaffold impact: current authority/eligibility/definition rules are KDG-owned. No
concrete generic template defect was found; existing Auth/worker/IDB owners are reused.
There is no matching scaffold raw-ASGI setup reader to update. Shared UI and agent
context stay unchanged. Docs append contracts/prepend handoff and preserve historical
evidence. Existing ADRs apply; no accepted ADR is edited or new decision required.

Commands, requirement-to-test mapping, source hashes and exact counts are in
[the machine record](evidence/provision-contract-20261026.json). Run from repository
root using the approved retained tools listed in [web instructions](../web/README.md).
A clean checkout lacks ignored modules/browser/Python artifacts; existing toolchain/
CI owners must supply them. No dependency install or baseline update is included.
Strict own-source compilation retains the existing upstream Auth declaration exception.

The evidence is synthetic Access/storage and the actual candidate loopback HTTP API;
it does not establish actual PostgreSQL permissions, rollback or native SQL ordering.
The existing schema grants no eligibility INSERT to the runtime role. Before activation,
a controlled narrow grant/policy migration and native least-privilege issuance,
immutability, rollback, latest-version selection and load qualification are required.
This prerequisite is recorded in deferred work; no migration/grant is applied here.
Story1.4 installed-device/readiness gates remain, and this does not complete Story1.5.

Pending-create local persistence/editing and setup storage remain the next consumers.
UI/editor/Leave, active sender/queue/browser/service-worker/default-startup, real
accounts/Auth/Access, native-driver/PostgreSQL/Docker work, provisioning/migration
execution, deployment/production/pilot and cleanup remain outside this delivery.
Fingerprints/HMAC stay deferred; TypeScript7.0.2 and the approved baseline are preserved.

Final37 qualification jobs pass:87 setup-client tests,29 setup-backend tests and18
integrated setup HTTP groups;73 existing delivery and29 delivery HTTP checks,
103 reconciliation,92 Save,61 history,575 existing clients,127 direct tests, four
fixture guards and16 existing loopback groups. Eight strict adapter/delivery/setup
configurations, fourteen schema/client freshness checks and five scaffold parities pass.
Prior313 backend tests are reused only after matching all77 existing backend source
hashes. Review addressed seven findings, rejected four with evidence and grouped two
native verification findings into one pre-activation follow-up.

| Requirement | Executed evidence |
|---|---|
| Exact capability and state boundaries | Four independent checks, all/assigned/edit-denied/no-create/no-child/no-published cases; foreign identity/observation/permission/state rejection |
| Current child/assignment binding | Deterministic multi-child lock order; each own membership/assignment/revision/opaque reference; changes under lock fail safely |
| Atomic response and bounded resources | Later child/assignment/issuance failure after provisional INSERT;1000 accepted distinct rows/1001 overflow; legal UTF8 response excess before commit |
| Safe request lifetime | Duplicate bearer/selector/body refusal; immediate empty ASGI message budget; acquire/SQL/release/serialization expiry and repeated cancellation ownership |
| Browser/consumer fidelity | Closed generated DTO validation;87 unit tests including scope, safe errors, cache/UTF8/size limits, lease release and late headers/body/account replacement |
| Actual candidate consumption |18 loopback groups verify committed issuance and safe release/commit failures through explicit Auth consumer; repeated references preserve zero capture/outcome/history effects |
| Compatibility and custody | Existing validators characterized before extraction, full affected regression, owner export/generator checks, five scaffold parities and final selected-source hashes |

The source-bound records retain separate failed verification setup attempts, concrete
behavior RED and final GREEN. Coarse command snapshots predate later unused JS fixture
corrections; the final Auth proof covers those corrected fixtures, and every actual
proof-selected source matches current bytes. This avoids claiming a whole-tree atomic
snapshot while preserving concurrent work.

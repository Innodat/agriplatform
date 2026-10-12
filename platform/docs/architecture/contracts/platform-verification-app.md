# Platform verification application

**Status:** Direction and responsibility split approved — 2026-10-08; delivery sizing and readiness pending. No implementation or deployment authorization.
**Context:** User proposes a test application across development, staging and production
for release verification and support diagnosis. Extend the existing E1-REF foundation;
retain its bounded generated create/read acceptance and disposable CI generation checks.

## Approved boundary

Maintain a small internal reference application consuming the actual shared clients,
UI and HTTP services through normal authentication and authorization. Exercise supported
platform capabilities incrementally as their owning stories deliver them: account and
organization access, persistence, session handling and private Content, then applicable
later services. Do not replicate Leave policies or approvals in this application.
Application-owned acceptance journeys still run against the real Leave/PtS applications.
A reference pass does not prove app-specific configuration, routes or business behavior.

User clarification, approved 2026-10-08: the separate verification application covers
shared platform features only. Synthetic monitoring of Leave, PtS and other products
runs on those actual applications with dedicated synthetic accounts and test data,
using organization fixtures only where the tested capability requires them. For example,
Leave sign-in/create-draft/autosave/close/reopen runs in Leave; PtS individual collection
and document reads run in PtS. Do not build duplicate product workflows or a proxy for
those journeys in the verification app. Test runners and reporting may be shared while
application scenario definitions, fixtures and authorization remain owner-specific.
The production bounds below apply to both platform and application synthetic checks.

Use one maintained application across explicit environment configurations, with separate
accounts, credentials, app admission, fixture records and storage scope per environment.
Production verification uses the real production dependency path but exclusively dedicated
synthetic accounts/organizations and verification-owned resources. Account-only scenarios
remain organization-independent. A test designation never bypasses permissions or RLS.
Internal admission protects the app; normal customers do not see it in the launcher.
The browser UI is a manual exercise surface, not an arbitrary privileged test runner.

## Execution and evidence

Reuse TypeScript Playwright and owner API/contract tests. Select suites explicitly:
full regression, destructive fixtures, fault injection and load checks belong to isolated
development/CI or suitable staging. Production runs only a small bounded allowlist of
non-disruptive journeys, using pre-provisioned restricted synthetic identities. Any writes
and cleanup must verify exact test ownership and be unable to select customer records.
Do not ship disposable-environment reset commands to production. Real outbound effects
must target controlled recipients/providers and be explicitly included; a stub proves
only its named boundary. Limits, cleanup/retention and cost bounds precede activation.

Run release checks against the deployed version and permit authorized on-demand runs.
Scheduled checks are a possible later operational choice, not a schedule established by
this proposal. Record environment, app/service build versions, scenario, time, outcome
and safe operation/trace references. Scope and redact screenshots/traces; no customer
content, credentials or unrestricted logs in the app. Incomplete/skipped checks must not
appear as passes. Failed post-release checks stop further promotion and trigger the
existing recovery runbook, not automatic destructive migration rollback.

For support, reproduce a scenario with synthetic input and correlate a separately
provided safe customer error/trace reference through existing authorized diagnostics.
A passing synthetic check cannot rule out account-specific configuration or data issues.
No customer impersonation, universal support credential or cross-owner database browser.

## Delivery and authority

E1-REF remains the first bounded reference story; persistent hosted verification is an
approved E1-VERIFY scope following E1-REF and preceding E1-PEOPLE. The approved
sequence now has 24 items; concrete technical sizing/readiness remain pending. Release/deployment owners own environment
publication and the production allowlist; each capability owner adds proven scenarios
alongside its consumer. First Leave slice and all pre-story/readiness gates remain.

Scaffold: shared generated foundations/clients and reusable test fixtures; regenerate a
fresh disposable sample in CI as well as testing the maintained app to detect drift.
Shared UI: reuse proven components and simple internal scenario guidance/results only.
Agent context: existing service ownership/privacy/release rules apply; no changes yet.
Docs/ADR: proposal links existing E1-REF and ADR-0020/0023/0046/0053/0055; accepted ADRs
remain unchanged. During delivery planning, reconcile production-fixture limits explicitly without
relaxing the existing prohibition on disposable reset tooling targeting production.


## Hosted delivery increment — proposed 2026-10-08

**Placement and initial scope approved, 2026-10-08.** E1-VERIFY follows E1-REF and
precedes E1-PEOPLE, taking E1 from 23 to 24 items. Retain REF's generated local/CI proof.
VERIFY publishes that proven small application with explicit dev/staging/production
configuration, restricted internal admission, synthetic fixtures and existing test-runner
integration. Initial coverage is the already delivered organization sign-in/create/read
reference journey and known-denied access using pre-provisioned identities. No account
administration dashboard, custom test orchestrator or full platform capability catalogue.
Manual use and authorized on-demand/post-release automation share the same normal routes.

Production publication follows successful staging verification and its own resolved
hosting, credential, fixture-isolation, cleanup/retention and recovery contracts. These
are readiness/delivery gates for VERIFY, not deferred work hidden in E8 or permission to
publish during planning. Start with CI report artifacts; do not require a new results UI.
If actual deployment scope is too large for one agent-sized item, split on concrete
hosting/activation evidence before declaring the story ready.

Later owners add their platform scenarios as those capabilities are integrated with the
reference app; a shared service merely existing does not count as browser integration.
Leave's own synthetic draft journey is delivered with its consuming stories. PtS adoption
already precedes REF and retains its own release checks; it does not depend on this later
verification app to complete or activate. No backwards story dependency is introduced.


## One application, two delivery increments — approved 2026-10-08

The existing reference application IS the platform verification application; do not
build a throwaway demonstration and then recreate its features in a second application.
REF establishes the maintained scaffold-generated reference source, ordinary auth/API/UI
integration and reusable scenario definitions. WRITE remains the prior backend foundation;
REF consumes it instead of rebuilding persistence. Fresh disposable generation in CI
proves the generator still works using the same declared recipe and reusable assertions;
it is a test artifact, not a second maintained application or independent scenario suite.

VERIFY consumes that same source and existing tests. Its new work is hosted environment
configuration, restricted fixture provisioning, production-safe suite selection and
cleanup, deployment/release invocation and evidence. Run the same safe scenarios against
each target by configuration; do not copy business behavior or test assertions per
environment. Destructive CI scenarios remain excluded from production by explicit policy.
Environment-specific expectations may be parameterized where the deployment differs.
REF remains complete and testable locally/CI without VERIFY. The hosted production
lifecycle belongs to VERIFY, not both stories. Later capability additions update this
one maintained application and its tests in their owning delivery items.


## Hosted fixture boundary — proposed 2026-10-08

**Direction approved by the user, 2026-10-08; concrete limits and cleanup contract remain pending.**

Use stable synthetic accounts and organizations provisioned separately in each target
by the approved owner commands. For the first organization-scoped reference journey,
provide two test organizations, one allowed test account in each, and a third account
with no reference-app capability. Keep these identities between runs. Use their normal
sign-in and permission checks; the test runner has no grant/membership administration
credential. Actual provider sign-in feasibility remains a gate, not a reason to add a
production test-login bypass. Account-only scenarios later use independent fixtures.

Each run creates only a small declared number of non-sensitive example records, tagged
with an opaque run reference for correlation. Record the exact returned identifiers.
The protected environment fixture manifest binds the target deployment, reference app,
organization/account IDs and allowed scenarios; a display name such as 'Test' is never
proof of ownership. A run identifier alone is likewise not delete authority. Before any
write, verify the configured target and fixture scope; mismatch stops the run.

Clean up only the reference app's run-created records through an owner-controlled,
restricted operation that checks target, exact fixture ownership and recorded IDs.
Routine browser/runtime credentials gain no cross-owner or broad deletion authority.
Keep successful/failing run evidence separately according to declared artifact retention;
cleanup failure reports a distinct outcome and never erases the scenario failure.
Bound leftover fixture records and stop new write runs when that bound is exceeded.
VERIFY must select concrete bounds/retention and a scoped cleanup command before readiness.
Do not delete accounts/organizations, audit evidence or customer data after each run.

App-owned synthetic journeys define their own lifecycle: Leave discards through its
normal draft contract, Content cleanup follows association/retention protection, and
PtS read-only checks create no copies of the corpus. Do not use the reference cleanup
operation against another application's tables. Production checks use pre-established
allowed/denied accounts rather than repeatedly changing global enablement or grants;
mutation/revocation scenarios remain isolated unless explicitly designed for their own
production fixture scope. Later notifications use controlled test recipients only.

This refines VERIFY's existing fixture/cleanup acceptance and does not add a story or
new test-management UI. Reusable scaffold/runner helpers carry explicit target and
ownership checks; application cleanup stays with its owner. Existing attribution,
logging, authorization, lifecycle and release ADRs remain binding. No runtime evidence
or production provisioning is claimed.


## Initial reference capability identifiers — 2026-10-08

Concrete naming for the already approved two-capability create/read journey:

| Registry field | Selected value and meaning |
| --- | --- |
| Application ID | `reference`; display name Platform verification; no URL implied. |
| Read capability | `reference.record.read`, organization scope; read the reference example records in the currently authorized organization. |
| Create capability | `reference.record.create`, organization scope; create the bounded reference example record. This does not authorize update/delete or grant administration. |
| Initial entry capability | `reference.record.read`; organization enablement/current membership and the exact grant are required. |

Grant read and create explicitly to the hosted successful-journey accounts. Neither
implies the other; a create-only grant does not produce a launcher entry. Reference API
caller policy allows exactly these two checks and organization discovery for `reference`.
Internal launcher visibility is supplied through explicit grants, never employee status,
email domain or a fixture label. The denied test account receives neither capability.

ACCESS-A registers these identities; ACCESS-B proves checks/independence with isolated
read-only/create-only/denied fixtures; WRITE consumes the create/read contracts; REF
supplies the browser journey and VERIFY reuses it on hosted targets. The existing
mixed-scope Access fixtures remain required separately; these two organization-scoped
capabilities do not claim to prove account-scope behavior or add an account-only UI.
Exact mixed-scope fixture identifiers remain a distinct contract input.

No generic write/delete permission or public cleanup route is introduced. VERIFY's
scoped owner cleanup and setup authority remain separate from these runtime capabilities.
These names settle the initial reference registry/entry/caller identifiers only; remaining
API payload, bounds, operation retention and hosted cleanup contracts are still open.
Scaffold and typed test fixtures adopt the same names; existing UI, agent-context and ADR
rules suffice. No Access registration, credentials, runtime code or tests changed here.


## Example record and create/read wire — proposed 2026-10-08

One immutable example resource proves the existing WRITE/REF journey. Its only business
input is `label`, a non-sensitive string of 1–120 Unicode scalar values with at least
one non-whitespace character; preserve accepted text exactly, without trimming or Unicode
normalization. Reject control characters, invalid Unicode, unknown fields and duplicate
JSON keys. The decoded JSON request body is limited to 4 KiB. These are reference fixture
bounds, not universal limits for generated applications or Leave.

Persist server-generated UUID `id`, required `org_id`, `label`, UUID `run_id`, and
server-managed `created_by` actor UUID plus UTC `created_at`. The opaque run reference is
correlation, never authority. As an immutable create/read sample it needs only creation
attribution under ADR-0025; no update/revision/editor API is introduced. Fixture cleanup
is a separate owner-controlled operation, not a user edit or deletion permission.

| Route | Required input and authority | Success |
| --- | --- | --- |
| `POST /api/v1/organizations/{org_id}/examples` | JSON `{operation_id, run_id, label}`; UUID identifiers; current `reference.record.create` for the route organization | 201 with `{operation_id, status: committed, result: {record_id}}`; identical committed replay returns the same acknowledgement. No label/read data returned through create authority. |
| `GET /api/v1/organizations/{org_id}/examples/{record_id}` | Current `reference.record.read` for the route organization | 200 with `{id, org_id, label, run_id, created_by, created_at}` for that organization's record. |
| `GET /api/v1/organizations/{org_id}/example-operations/{operation_id}` | Current create authority and the original verified account's outcome scope | 200 with the original compact committed receipt or `{operation_id, status: unresolved}` if no receipt is visible in that scope. No label or arbitrary operation lookup. |

Apply the existing shared error envelope and private/no-store policy. Missing records
and another organization's record IDs use `resource_not_found` after route authorization;
failed organization access reveals no record details. Reject supplied person/actor/org
fields in the body; identity comes from verified current Access and the validated route.
A read-only account cannot create; a create-only account cannot use the read route.

The owner-local outcome is unique by verified account, organization, command/version and
operation ID. Under the existing versioned SHA-256/JCS contract, bind stable command,
organization, account, run ID and exact label; do not hash the label alone. Record the
verified executing actor as attribution, not as a browser assertion. The record and
compact outcome commit atomically. Matching concurrent retries create one record;
changed stable input returns `operation_payload_mismatch`. A missing receipt remains
unresolved, not proof of rollback. Retry the same operation/input; a deliberate new
create uses a new operation ID. External Access waits remain outside write locks.

Retain compact outcomes when synthetic example rows are cleaned up: a late retry returns
its original committed acknowledgement and never recreates a removed example. Reading
that removed record returns not found; a historic receipt does not promise current
existence. No automatic outcome pruning in this increment. Before hosted activation,
VERIFY must select storage/run bounds and owner retention/retry-expiry policy; stop new
write runs at the declared bound rather than silently deleting deduplication evidence.
No per-write duplicate business audit log or retained label payload in receipts is needed.

ATDD evidence covers exact text readback, invalid input, spoofed attribution, independent
read/create grants, other-organization IDs, concurrent retry, commit with lost response,
changed-payload rejection and replay after fixture cleanup. Database/HTTP checks belong
to WRITE; REF reuses them through the browser; VERIFY runs its safe hosted subset. No
extra product feature, reference-only draft system or generic CRUD generator is implied.

Impacts: schema/API/generated types, owner operation helper and fixtures change together
in WRITE, with REF's small UI and VERIFY's hosted configuration following. Agent context
and existing ADRs suffice; document exact commands and ownership with delivery. This
proposal settles payload/route examples for discussion, not DDL, executable tests,
retention completion or implementation readiness.


## Saving examples and demonstration role — proposed 2026-10-08

User accepted the usefulness of the initial example and asked why editor/draft coverage
was excluded. Initial create/read remains a delivery increment, not the final feature
ceiling. The user approved the same reference app serving as an internal, working
demonstration of supported platform patterns on 2026-10-08, including the distinction
between explicit Save, draft autosave and immediate preferences. Additional examples
need concrete delivery placement/sizing; the existing 24-item sequence is not expanded
or declared ready by that approval.

Keep ADR-0051's three distinct patterns clear: whole-form explicit Save/Cancel for
configuration; automatic draft preservation with a separate consequential Submit action
when that lifecycle is actually implemented; immediate application of simple independent
personal preferences. An inline editor is a presentation choice, not a fourth persistence
rule. A draft does not require clicking Save, and Submit is not a synonym for saving.
Use separate example pages/sections; do not mix immediate writes and pending Save fields
inside one form. No dummy submission may claim to verify an undelivered lifecycle.

Evolve the maintained application rather than build replacement apps. The initial
create/read tests remain regression coverage when an editor or draft example is added.
If the initially immutable example gains editing, its owning story must explicitly add
update attribution, revision/authorization and migration contracts; do not silently
reinterpret the initial create-only model. Shared mechanisms are promoted by their first
proven consumer and reused; Leave domain rules and real-app acceptance stay in Leave.

Demo examples use real shared components/services, clear sample labels and synthetic data.
Keep human demo records separate from automated run-owned records so cleanup cannot remove
an active demonstration. Internal access and production-safe operation limits apply to
manual use as well as automated tests. Realistic error/fault demonstrations belong in
isolated development/staging; no production fault-injection switches. Existing reports
and manual example pages suffice initially, not a separate showcase or test-control system.

Scaffold/shared UI additions follow the owning editor/draft/preference stories; agent
context and accepted ADRs remain unchanged. Exact scope, delivery placement and fixture
rules must be reconciled before expanding REF/VERIFY. No implementation or deployment.


## Incremental example placement — proposed 2026-10-08

**Placement approved by the user, 2026-10-08; consuming-item sizing remains binding.**

Keep REF/VERIFY's first create/read boundary and add examples with the first proven
shared mechanisms, under ADR-0051's same-item promotion requirement:

| Example increment | Delivery owner and dependency | Evidence boundary |
| --- | --- | --- |
| Create/read | Existing WRITE → REF → VERIFY | Initial shared access, attribution, persistence, safe create retry and hosted checks. |
| Draft autosave and close/reopen | E1-D2-B consumes completed D1/D2-A foundations and adds the minimal reference draft surface using proven scaffold/client/UI artifacts in the same delivery item | Generic title/note preservation and truthful status; real Leave draft tests remain separate. No submission or business configuration. |
| Organization switch and discard | E1-D3 and E1-D4 extend that same reference draft surface as their mechanisms are proven | Cross-context isolation and normal discard/late-save protection; use controlled closed fixtures until discard exists. |
| Session return | E1-D5 extends the reference journey with its proven recovery adapter | Existing saved-state recovery limits; no unsaved-input survival guarantee. |
| Whole-form Save/Cancel editor | First relevant E2 configuration writer adds a simple reference editor and updates reusable artifacts together | Update permission, attribution, revision conflict and no hidden writes before Save. Preserve application-specific review/impact checks in Leave. |
| Immediate preference | First actual independent preference consumer adds the corresponding reference example | Immediate authorized persistence and truthful failure feedback; no new product preference invented for a demo. |
| Consequential draft finalization | First E5 submission consumer, after its contracts are ready, adds only the proven generic lifecycle example | No Leave entitlements/approval engine copied into reference; an E1 demo never shows a fake successful Submit. |

These are linked acceptance/impact increments on consuming work, not newly approved
standalone story counts. Final sizing must account for the small reference-owned model,
permissions and fixtures: do not hide a second application implementation inside a
Leave story. If a consuming item becomes too large, split the completed platform
mechanism/demo increment before its consumer with explicit dependencies during story
sizing. Never make REF/VERIFY completion depend on these later additions.

Reuse tested build-time packages/templates and HTTP clients; the reference application
must not import Leave's server implementation or call Leave endpoints to impersonate a
shared-feature example. It owns its minimal example persistence and lifecycle. Its
synthetic draft domain needs an explicit scope/state contract in the consuming item;
do not assume Leave's one-active-draft rule applies universally. No generic runtime
workflow/draft engine is introduced.

The first Leave delivery remains sign in → select organization → create/resume →
autosave → close → reopen. Add only the applicable draft demonstration with that work;
editor/preferences/finalization are not prerequisites for that slice. Human demo records
remain separate from automatic run fixtures. Shared-UI/scaffold impact is proved in both
the reference and first real consumer; agent guidance and owner docs track the promotion.
Accepted ADRs and application product requirements remain authoritative.


## Minimal draft demonstration — proposed 2026-10-08

**Scope approved by the user, 2026-10-08; wire, lifecycle and sizing checks remain pending.**

The reference-owned draft is separate from the immutable create/read example. Use an
optional title (up to 120 Unicode scalar values) and optional plain-text note (up to
2,000); empty/incomplete input may be preserved. Preserve accepted text, including note
line breaks, exactly. No dates, leave types, employee settings, attachments or entitlement.
The UI identifies it as sample data and tells testers not to enter sensitive information.

Choose one active example draft per authenticated account/organization for this example
only, using ADR-0034's opt-in scoped constraint. This is not a default for all applications.
The service derives account/actor identity, verifies organization and capabilities, and
checks ownership on every route. No People/person/employment dependency is introduced.
Add `reference.draft.own.read` and `reference.draft.own.manage`, organization-scoped,
with the first consuming draft increment; neither implies the other or follows from
record read/create. Add own-read as an explicit reference entry capability when that
surface is available, not during the initial REF/VERIFY bootstrap.

Start/Resume explicitly creates an empty draft or returns the current one without
overwriting its input. Typing autosaves under the proven revision/operation contract;
Close retains acknowledged input, reopening reads it, and Discard closes the draft and
clears its input when the D4 increment arrives. States initially are active/discarded;
submission is absent until its separately designed E5 demonstration. No automatic
replacement draft after discard or after an old retry. Draft rows carry creation/update
actor/time attribution and a revision; compact closed/outcome evidence prevents stale
save/create resurrection. Retention bounds remain part of the owner lifecycle contract.

Apply the existing shared failure presentation: inline Changes not saved with Retry;
Stay / Close anyway only when leaving without confirmed saving, and Stay / Switch anyway
on an affected organization switch. No Save button or new draft-specific UX convention.
Concurrent tabs cannot silently overwrite each other or revive discarded input. Invalid
identity/access blocks disclosure; dependency outage is not permission denial.

Manual demonstration accounts are distinct from automated fixture accounts. Serialize
ordinary automated journeys per account/organization so the single-draft rule does not
make parallel checks discard one another's input; concurrency tests use deliberately
isolated fixtures. Normal cleanup uses the draft's Discard contract when available;
pre-discard test fixtures remain confined to isolated owner setup and cannot become a
production reset path. Add a production draft journey only after its cleanup and bounds
are ready, not merely because the demo page renders.

D2-B owns the first reference draft browser increment using D1/D2-A's completed shared
artifacts; D3/D4/D5 add their agreed cases. Account/organization isolation, exact input,
concurrent revision, discard/late-save and current authorization get separate reference
fixtures while Leave retains its actual domain acceptance. Shared scaffold/UI is reused,
not Leave runtime imports or a generic draft service. Exact wire/DDL/retry-retention and
story sizing remain readiness inputs. No new standalone story or implementation.

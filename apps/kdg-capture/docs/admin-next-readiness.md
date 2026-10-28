# Next administrator prerequisite assessment — 2026-10-27

Assessed at Git `29763767fc3bb2895fea2500283759975f826d81` after the
[completed request batch](admin-request-batch-checkpoint.md). No additional ready
implementation was established within the current synthetic, unmounted scope.
This assessment does not authorize a fourth batch delivery.

## Evidence and selection

- The three edit-context/edit/recovery delivery specs are done; their source files
  exist under `web/src/`. History, detail and audit request consumers also exist.
  Repeating these consumers would not advance the remaining acceptance criteria.
- [Story 3.1 AC-2/3 and its dependencies](epics.md#story-31-view-authorized-khula-observations-and-administrator-audit-details)
  require original capturer and actual modifier presentation. The
  [audit contract](contracts.md#bounded-online-audit-metadata-api-subset--2026-10-26)
  explicitly leaves historical actor-name resolution to a separate Identity HTTP
  contract; assignment-target discovery is insufficient.
- `services/access/main.py` and its included capability, preferences and People
  setup routers do not establish that historical actor lookup. The checked-in
  `services/access/openapi.json` has no historical actor lookup operation.
  Current-account SQL evidence explicitly describes an internal current-account
  projection, not a historical HTTP resolver.
- Mounted portal/session/conflict/device work, native database qualification and
  release remain outside the latest handoff's scope. Questionnaire management and
  assignment management have their own outstanding contract gates in
  [contracts.md](contracts.md#questionnaire-draft-editor-increment--approved-scope).

## Concrete next proposal

Plan the Identity-owned historical actor display contract with its KDG consumer
before implementing a resolver. Resolve caller/service authorization and permitted
actor selection without exposing a general actor directory; retention and missing,
retired, deleted, service and unmapped actor behavior; whether labels describe the
current name or a historical name; closed bounded request/response/error models;
and timeout, unavailable, no-store and sensitive-data handling. Preserve actual
executor/initiator IDs and keep all external waits outside KDG business locks.
Do not substitute current membership, employment or assignment eligibility for
historical attribution.

Then select one bounded synthetic owner delivery with acceptance failure first,
owner-generated types and consuming tests. Any database privileges, native proof,
runtime integration or activation remain separate gated work. No endpoint path,
authorization mechanism or fallback label is selected by this assessment.

## Verification and impacts

Read-only inspection of current contracts, Story 3.1, the three done specs,
checkpoint, owner routes/OpenAPI and current-account evidence. No runtime tests
were rerun and no earlier test result is promoted to current qualification.
Concurrent changes and retained resources were preserved. The prohibited migration
fixture was not accessed. No dependencies, services or resource lifecycle commands ran.

Scaffold, shared UI, agent context and ADR: unchanged; no behavior or architecture
decision implemented. Documentation: this assessment and a handoff pointer only.

## Follow-up planning — 2026-10-27

The proposal above now has an [Identity-owned candidate contract](../../../services/access/HISTORICAL-ACTOR-DISPLAY.md)
and a [BMAD spec](../../../_bmad-output/specs/spec-kdg-historical-actor-display/SPEC.md)
that adopts existing product/owner truth rather than duplicating API specifications.
The candidate proposes a restricted backend-only batch over server-selected audit IDs,
current retained names, explicit unmapped labels and separate outage feedback.
HD-1–HD-7 map future owner and consuming proof. Its ratification, exact caller
configuration and restricted projection remain prerequisites; no implementation is
established as ready. Documentation checks only; no runtime/resource changes.

## Owner readiness closure — 2026-10-27

The subsequent user “next” agrees the concrete contract defaults. The
[owner contract](../../../services/access/HISTORICAL-ACTOR-DISPLAY.md#selected-synthetic-delivery-and-verification-plan)
now fixes exact credential inputs/rotation design and the injected read projection,
with a future least-privilege native function/role design kept outside implementation.
Existing actor DDL and decoder were inspected: retention is independent of live Auth,
persisted labels remain capped at 200 characters and the shared 64 KiB decoder
cannot be reused unchanged for the selected 16 KiB operation.

One isolated synthetic Identity HTTP candidate is ready for BMAD Build: HD-1–HD-5
and owner HD-7, acceptance HTTP RED first, independent owner export/generated types.
No active Access app/export, SQL adapter, migrations, privilege changes or KDG
composition is included. Actual native retention/permissions, credential provisioning
and rotation, HD-6/consumer HD-7 and activation remain separate qualifications.
This supersedes the earlier no-ready-slice assessment only for this new owner scope.
Documentation checks only; no runtime qualification or resource action is claimed.

Verification for this closure:

- `python3 /tmp/kdg-actor-display-planning-check.py` — PASS: 12 links/companion paths including heading anchors, seven acceptance cases, stable CAP-1 and kernel/readiness sections.
- `git diff --check -- services/access/HISTORICAL-ACTOR-DISPLAY.md _bmad-output/specs/spec-kdg-historical-actor-display apps/kdg-capture/docs/next-session.md apps/kdg-capture/docs/admin-next-readiness.md apps/kdg-capture/docs/contracts.md` — PASS.
- The handoff update script asserted exact preservation of its previous bytes after prepending the new section.

These are document checks, not HTTP, generated-code or SQL qualification.

## Isolated owner delivery complete — 2026-10-27

The selected Identity candidate is implemented and reviewed; see
[owner evidence](../../../services/access/HISTORICAL_ACTOR_DISPLAY_EVIDENCE.md).
Final81 focused/127 affected tests, exporter/generator freshness and strictTS7 pass.
One verification gap was closed; no new deferral. This completes only the selected
synthetic owner scope. KDG combined DTO/budget/publication/authorization contracts
remain to close before consuming implementation; no additional ready consumer is
asserted. Native projection/real authority/activation gates remain.

## Composition planning and corrected prerequisite — 2026-10-27

The [composition contract](audit-display-composition.md) closes proposed route,
combined DTO/321 KiB bound, exact permitted selection, transaction release, original
budget, final authority check and later client invalidation, with KC-1–KC-9 mapped
to HD-6/consumer HD-7. No consuming endpoint, generated contract or runtime is added.

A targeted actual-ASGI diagnostic confirms that the existing Identity shielded reader
can disclose a synthetic private cleanup exception to Python3.15 loop diagnostics
after caller cancellation. Diagnostic command/source and boolean/count-only result
are in the composition contract; retained evidence is
`/tmp/kdg-actor-composition-diagnostic-yeqc5h4s/`. It exits1 with one diagnostic event.
This newly exercised case supersedes the earlier no-open-finding readiness only
for this specific path; no old successful test expectation/result is rewritten.

Next: BMAD owner repair with a no-disclosure cancellation/timeout regression and
private outcome wrapper before consuming implementation. Documentation changes and
one synthetic diagnostic only; no native/service/resource or runtime-code changes.

Verification: `python3 /tmp/check-kdg-audit-display-composition.py` passes22 local
link/companion targets with heading checks, stable CAP-1, nine KC cases,203-ID and
321 KiB bounds, and eight unchanged runtime/test/schema sources. Scoped
`git diff --check` passes. The targeted disclosure diagnostic exits1 as recorded,
not a passing owner qualification. Exact command, safe result and source hashes:
[planning evidence](evidence/audit-display-composition-planning-20261027.json).

## Identity prerequisite repaired — 2026-10-27

The concrete cancellation-diagnostic issue is fixed in the isolated owner candidate;
[repair evidence](../../../services/access/ACTOR_DISPLAY_CANCELLATION_EVIDENCE.md) records
four actual HTTP RED/GREEN cases,85 owner/127 affected passes, exporter/generator/TS7
checks and independent no-finding review. Original diagnostic replay has zero events.
This closes only that discovered prerequisite. The next selected scope is backend-only
synthetic composition under the [defined KDG contract](audit-display-composition.md),
with consuming acceptance RED before implementation. Native/real authority and active
mount/browser/session/UI qualification remain separate. No new deferral or resources.

## Backend composition complete — 2026-10-28

The selected [backend composition](AUDIT_DISPLAY_BACKEND_EVIDENCE.md) is implemented
and independently reviewed. Final134 tests/42 subtests, old/new export freshness,
generator/strictTS7 pass;388 prior sources unchanged. One verification gap was
closed with independent older-page/header-only and empty-continuation label tests;
no new deferral. Next select the inert browser adapter for strict aggregate/runtime
validation and publication fences. Backend proof does not establish browser/session
/device, mounted portal, native owner permissions or real authority/release readiness.
No source extraction, dependency or resource lifecycle operation was required.


## Story 3.1 next bounded delivery assessment — 2026-10-28

Baseline: `f1fd78025ad7bdad0e06db7129f5435a8d7c8fe5`. BMAD sprint-planning,
readiness-only. **PASS for one inert audit presentation model; full Story 3.1
remains incomplete and portal activation remains gated.** This assessment selects
a technical subset, not another implementation batch or completed product story.

### Completed work reconciled

The [audit-display adapter](AUDIT_DISPLAY_ADAPTER_EVIDENCE.md) is done and reviewed,
following the completed Identity owner, cancellation repair and KDG backend composition.
Its [machine record](evidence/audit-display-adapter-20261028.json) records 109 adapter
cases, strict TypeScript 7.0.2, 73 prior audit cases, 20 backend cases/two subtests,
owner/generated freshness and five adopted scaffold parities. These are the delivery's
retained results, not new runtime test executions in this assessment.

All 15 selected adapter source hashes match the current workspace. The retained final
proof digest matches the machine record and reports passing strict compile/emit and
behavior commands with sources unchanged. The adapter validates the exact actor set,
strict aggregate and byte bounds, and rejects late success/errors through the supplied
current-generation predicate. It does not own an integrated session/access lifecycle.
Repeating history/detail/edit/recovery/audit request adapters would add no missing
presentation or integration evidence. Earlier entries above remain historical.

### Remaining acceptance, without promoting synthetic proof

Authoritative criteria remain [Story 3.1](epics.md#story-31-view-authorized-khula-observations-and-administrator-audit-details).

| Criterion | Evidence already available | Remaining acceptance / selected contribution |
| --- | --- | --- |
| AC-1 current all-record authorization | Isolated authorized history/detail/audit APIs and inert request validation; bounded native history evidence has its own limits | Current authority through the mounted portal and coordinated running owners remains unproved; presentation supplies no authority |
| AC-2 responsive review | Generated history/detail/original-definition request contracts; audit owner/header labels now available | Phone/computer portal, child/date/answers under original definition, empty versus failed/partial and refresh after sync remain; selected model maps original capturer only for audit context, not every history row |
| AC-3 administrator audit | Committed bounded event/header metadata and complete validated actor displays | Selected model maps creator/latest modifier and actual event executor with preserved server times and separate initiator; visible expandable audit section remains later |
| AC-4 online portal / own PWA | Inert requests require same-origin authenticated private/no-store responses; no all-record persistence introduced | Actual connectivity feedback and browser/service-worker/IndexedDB separation remain; pure model adds no cache or offline authority |
| AC-5 role/account/session loss | Adapter fences discard delayed success/errors when caller invalidates the generation | Actual session/access owner invalidation, clearing already-rendered data and locking after denial/unavailability remain; a pure projection cannot establish these |
| AC-6 accessible/runtime evidence | Existing API/native evidence is limited to its recorded scope | DOM labels/focus/keyboard/zoom/touch/assistive technology, integrated runtime-role matrix and separately recorded installed-device extension remain; model tests establish none of these |

### Smallest ready slice

Build one **KDG-local, pure audit presentation model** consuming only the existing
validated, deeply frozen `auditDetails` loaded aggregate. It performs no request,
subscription, retry, authorization, session wiring, storage or UI mount. It projects
one bounded page, not an accumulated audit archive. This advances A21.admin-audit-
attribution and KC-5 presentation semantics without inventing another HTTP contract.

Its required behavior is already selected by the [composition contract](audit-display-composition.md)
and [Identity label semantics](../../../services/access/HISTORICAL-ACTOR-DISPLAY.md#label-and-retention-semantics):

- Map original capturer from `owner_actor_id`, creator from `created_by`, latest
  modifier from `updated_by`, and each event editor from `executor_actor_id`.
  Preserve nullable initiator separately; never substitute reader, owner account,
  latest modifier or initiator for the actual executor. Older/empty continuation
  pages still use the aggregate header for creation/latest-modification facts.
- Use exact resolved current retained names, not alleged event-time names. Emit
  distinct semantic presentation states for per-actor Name unavailable and batch
  Names temporarily unavailable; preserve the latter's explicit-retry indication.
  Do not invent approved Afrikaans translations. No UUID-as-name or guessed System.
- Preserve committed event order, command kind, exact decimal revisions, UTC server
  timestamps and opaque next cursor. Add no synthetic create/edit/no-op events,
  answer copies, version selector, restore/export or historical-name snapshots.
  Retain internal identity/provenance references distinctly from ordinary labels.
- Return an immutable projection without mutating or retaining input in module state.
  Transport failures/denial/supersession are not loaded input and must never be
  converted into an empty audit or unmapped-name result. No duplicate wire parser.

The model is a synchronous projection, not an access lease. A later caller must check
its current generation at rendering, discard references on invalidation, and make an
explicit Retry repeat the complete authorized aggregate read. Those lifecycle/network
behaviors are outside this slice; a retry indication here executes nothing.

### Build entry and verification plan

Next workflow: BMAD Build for this single subset. First observe an acceptance RED
for an authorized cross-owner aggregate with different owner/creator/modifier/
executor/initiator labels. Then cover resolved/unmapped/outage distinctions, null
initiator, exact service names, rename-on-new-input, older/header-only and empty pages,
maximum page, cursor/order/revision/time preservation, immutable output and unchanged
input. Drive loaded input through the existing adapter in synthetic consuming proof;
show its failed/superseded result cannot become a loaded presentation. Use retained
Node 26.11.1/TypeScript 7.0.2, strict types, the existing audit-display adapter proof
and affected audit checks. Record exact RED/GREEN commands and source custody in that
delivery; no RED or new runtime qualification is claimed here.

No unresolved load-bearing owner/DTO/label decision blocks this narrow projection.
DOM interaction, complete portal state coordination or native Identity projection
would each require a separately bounded assessment; combining them is unnecessary.
Keep the Story 3.1 status approved/incomplete and do not mutate global Leave tracking.

### Scope and impacts

Scaffold: reuse existing immutable/generated types; no new proven neutral pattern to
promote. Shared UI: none; KDG audit wording/provenance stays local. Agent context:
unchanged. Documentation: reconcile readiness/composition/test map and prepend handoff;
the Build item will record its own evidence. ADR: inherit 0022/0023/0031/0056; no new
or modified accepted decision. Release/migration tooling unchanged.

All prior exclusions remain: no portal/UI/editor/Leave, Auth/session/startup/browser/
worker/queue activation, real services/accounts/credentials, native DB/Docker/migrations/
grants, dependencies, deployment/production/pilot/push or resource lifecycle/cleanup.
Native Identity retention/projection permissions, real authority, installed devices and
controlled release remain separate gates. Fingerprints/HMAC remain deferred under
ADR-0061. Preserve concurrent work and retained evidence/resources. The prohibited
migration fixture must not be accessed, run, copied or hashed.

Verification for this assessment: selected source/proof digest checks and local Markdown
link/anchor checks; scoped diff whitespace and unchanged concurrent tracked diffs.
No runtime tests, dependency installation, service startup or resource command ran.


## Continuous Story 3.1 delivery checkpoint — 2026-10-28

The user requested continuing through successive ready work until Story 3.1 is done,
if plausible, without stopping after each small slice. Two inert consuming increments
are implemented: the selected pure audit presentation model and a separately assessed
single-context in-memory review coordinator. The latter derives its caller-driven
invalidation, full-read Retry, no-cache and generation rules from the existing
composition contract; it adds no authority or owner policy. See
[combined evidence](AUDIT_REVIEW_CONSUMER_EVIDENCE.md) for exact RED/GREEN and limits.
Both independent blind reviews report no supported findings; reviewers independently
passed focused cases/strict types. Full Story 3.1 remains incomplete.

Current qualification: nine presentation and16 state cases, both strict TS7.0.2 proofs,
109 aggregate and73 original audit cases pass. Prior source bytes are unchanged.
The earlier readiness assessment's projection-only stopping point is superseded by
this explicit continuation; its scope exclusions remain binding.

The next boundary is substantive, not a routine confirmation between small slices:

- **AC-1/5:** actual administrator admission/session/access integration. The mounted
  [entry context](../web/src/entry.ts) validates `own_account` and
  `kdg_capture.capture.read.own`; [local entry routing](../web/src/LocalEntryRoute.tsx)
  mounts that own-entry flow. It cannot be repurposed as current all-read authority.
  The new coordinator consumes explicit caller invalidation; it does not supply
  the missing real administrator owner integration or revoke old renderer references.
- **AC-2/3:** the phone/computer portal must actually render history, child/date,
  original-definition answers and optional audit details, with refresh/partial/error
  feedback. There is no mounted administrator surface in this delivery. Additional
  inert wrappers cannot establish those visible acceptance results.
- **AC-4:** prove actual online portal/own-PWA separation, reconnect feedback and
  absence of all-record service-worker/IndexedDB persistence in a running browser.
- **AC-6:** DOM focus/labels/pagination/loading/failure/keyboard/zoom/touch/assistive
  technology and the integrated runtime-role matrix, followed by separately recorded
  installed-device extension. Synthetic state tests cannot substitute for these.

Native Identity retained actor projection/permissions and controlled real authority/
release remain unqualified owner gates as previously recorded. No routine task choice
can supply installed Android/iPhone evidence or authorize excluded activation. Therefore
**full Story 3.1 completion is not plausible within the retained scope**. Do not mark
it done or add speculative inert layers merely to keep a batch running. The next
meaningful delivery requires a separately bounded portal/all-read integration scope
with its activation and physical-device prerequisites resolved. This records the
boundary; it does not approve any excluded action or request routine reconfirmation.

No full Story 3.2, editor, assignment management, questionnaire management, exports,
dashboards, revision browser, Leave, real account/credential, DB/grant/migration,
dependency, deployment/pilot/push or cleanup work follows. Historical evidence,
concurrent work and resources stay preserved; prohibited fixture remains untouched.

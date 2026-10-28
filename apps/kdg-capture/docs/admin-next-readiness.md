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

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

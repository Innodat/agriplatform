---
title: 'KDG controlled schema foundation and reusable migration guards'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Prepare KDG's first owner-local database foundation: separate Alembic configuration/history, exact kdg_capture schema/migrator/runtime/operator policy, and a protected version table. This first slice contains no questionnaire, child, assignment, capture or outcome tables, no business API writes and no claim that an empty schema proves row isolation. Reuse existing migration authority/transaction/security decisions. APIs never run migrations on startup, and the production deployment registry remains unchanged.

Promote neutral prepared-schema/role/ACL validation, bounded owner migration transaction and its tests through the platform builder and generated application skeleton in this same delivery. KDG consumes managed copies, with owning schema/role/history choices outside generic templates. Do not import another app's implementation or relax the installer's fixed inventory. Other apps adopt independently; do not migrate them or centralize business tables.

Given a prepared correct dedicated schema and restricted login, the controlled upgrade route must validate authority and schema boundaries before Alembic changes, serialize owner migration execution, commit only after verified ledger postconditions and report fixed safe failures. Missing/wrong/privileged identities, unsafe schema/ACL/history state, unknown revisions and unsupported migration directions refuse. No automatic stamp/downgrade, role creation, database creation, live-target fallback or destructive cleanup. Candidate tests cover refused authority before effects, transaction rollback paths, bounded SQL settings, revision resolution and generated parity/preservation.

Existing synthetic PostgreSQL target55482 is stopped and compatible KDG roles/schema have not been provisioned. Under the standing no-provisioning/resource-preservation boundary, implement and review the candidate and run all available offline/unit/scaffold checks first. Native PostgreSQL acceptance remains explicitly incomplete until an authorized compatible disposable target exists; mocked tests must never be presented as role/RLS/native migration proof. Do not use unknown target54322. Any request to change that boundary must follow a concrete reviewable candidate.

Preserve concurrent work, historical evidence, Docker resources and the approved dependency baseline including TypeScript7.0.2. No Leave/editor, production, real accounts/access, provisioning, deployment/pilot, cleanup or fingerprints/HMAC. Do not modify accepted ADRs or existing API/lock manifests. No external/schema mutation is authorized in this candidate work.

</frozen-after-approval>

## Implementation Notes

- bmad-help [BD] bmad-build selected this freeform schema prerequisite after637c485f428aa87257ab76a49021579fabaef1ac; user then explicitly requested platform/scaffold applicability. Dirty-tree preservation already authorized; /tmp/kdg-schema-before.json captures baseline. No sprint-key or product specification duplication.
- Step02 read-only subagent investigation completed. Existing WRITE examples demonstrate context/role boundaries but native preparers CREATE ROLE/DATABASE; do not run them. Existing migration authorities ADR0015/0016/0017/0018/0020 apply. No new ADR. Reuse Alembic/SQLAlchemy/psycopg at approved pins from existing Access owner environment, no installation or API lock changes.
- Code map: canonical application/database-tools/owned_migration.py and emitted test_owned_migration.py are inert neutral helpers. A scoped preservation-installer adapter adopts a separate KDG database-tools root. Owner alembic.ini, migrations/env.py and versions/0001_foundation.py select KDG policy and history; no API import. No production registry change.
- Native gap established by read-only known-port probe:55482 stopped.54322 reachable but unknown and untouched. The existing atomic fixture's DB-owning migrator would not qualify the stricter KDG role contract. Offline/unit evidence is a candidate qualification only; native schema/ACL/transaction acceptance remains required before readiness.
- Impacts: scaffold helper/emitted tests/parity same delivery; UI unchanged; existing agent context sufficient; owner/platform guides/evidence/handoff updated; ADRs immutable; no migration execution or release activation. Small reversible code candidate, no remaining intent choice in authorized work; native verification requires a later explicit scope change.

- Candidate implementation complete, native_acceptance=false. Status done refers only to the authorized inert candidate work in Intent, not schema/role/RLS/release readiness. No PostgreSQL SQL, Docker lifecycle, role/database/schema provisioning or registry activation was executed. The known endpoint remains stopped. Native completion requires an explicit exception or a compatible independently prepared target.
- Behavioral unit RED: minimal migration_transaction skeleton yielded under wrong current role; expected MigrationError missing (1 failure). Initial isolated-script sibling-import failure is diagnostic only. This is test-double ATDD/control flow, not native acceptance. Final10 emitted unit tests and8 KDG policy/revision/env wiring tests pass;5 actual CLI refusal cases fail safely before connection as expected.
- Builder72 and strict TypeScript7.0.2 pass. Full offline generation proof-IWqNGL passes bootstrap_only=true/generation_ready=false; optional database tools require the explicitly retained migration environment, not the HTTP-only API environment. Verified retained Python3.15.0/SQLAlchemy2.1.4/Alembic1.20.0/psycopg3.3.6; no install/lock/manifest change.
- Empty schema must be separately prepared under exact restricted login roles. Initial revision creates no objects itself; Alembic would create/stamp its private version table inside the guarded transaction. Unknown history/objects and private-ledger differences refuse. Schema types/functions/default authorities are not silently adopted. No tenant table exists yet and no RLS behavior is claimed.
- Unit tests are emitted/installed through actual application renderer and preservation installer, and the separate KDG database-tools root rejects manual edits. Existing Auth/host inventories remain unchanged. Production registry, accepted ADRs, native fixtures/resources, prior proofs and historical handoff suffix remain preserved. Migration tests live separately from API tests, so their optional dependencies do not enter the API baseline.

## Review Triage Log

Blind Hunter: seven findings addressed, final read-only follow-up finds no additional substantive issue. Native qualification remains a pre-existing acceptance gate, explicitly outside authorized candidate execution; no new review deferral.

1. medium / patch — Cross-owner schema ownership/CREATE was missed. CROSS_OWNER now checks both for each selected role before effects. Native effective privilege evaluation remains pending.
2. medium / patch — Empty-schema inventory missed standalone objects. Extra catalog query rejects types/domains/composites outside ledger row/array types, collations, conversions, operators/families/classes, text-search objects, extensions and extended statistics.
3. medium / patch (landed before review final) — Ledger RLS could hide unknown history. LEDGER_FEATURES rejects RLS/FORCE RLS/policies plus user triggers/rules; emitted catalog-state refusal covers the guard branch.
4. medium / patch (landed before review final) — Unlogged ledger was not durable. Ledger features require permanent nonpartitioned storage and exact expected index footprint.
5. medium / patch — Transaction timeout started after initial catalog inspection. Install it before full inspection; server-major mismatch still fails safely. Native elapsed behavior unqualified.
6. medium / patch — Privileges from different roles were combined. Use per-role CTE pairing for schema usage and relation/sequence/function access. No fake test claims SQL expression evaluation.
7. medium / patch — Incoming role memberships were omitted. Reject memberships where selected role is either member or grant target; no foreign runtime can inherit selected authority by an accepted prepared state.

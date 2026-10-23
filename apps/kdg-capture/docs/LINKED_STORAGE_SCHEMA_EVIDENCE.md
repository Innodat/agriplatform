# Linked capture storage schema candidate — 2026-10-23

bmad-help [BD] selected physical storage after the completed capture-command and
outcome boundaries. The unapplied Alembic candidate lives at
`migrations/candidates/0002_capture_storage.py`, outside active `versions` discovery.
It declares all supporting parents and linked capture/outcome/revision storage together.
No table, role, schema, data, database or Docker resource was changed by this delivery.
Active head remains0001_kdg_foundation; there is no startup/release registration.

## Implemented DDL contract

The candidate uses ordinary Alembic/SQLAlchemy PostgreSQL DDL for questionnaire,
questionnaire_version, child, child_assignment, child_eligibility, capture,
operation_outcome and capture_revision. This is storage, not an admin/setup/issuance or
protected API workflow. Parent writes remain ungranted to runtime/operator roles until
the appropriate owner commands and their current authority are delivered.

Same-organization composite foreign keys bind child/version, capture owner/history and
issued eligibility org/account/membership/child evidence. Assignment is unique per
org/child/account; explicit renewal changes current membership/revision, while immutable
eligibility records retain observed membership/revision. Old references grant no current
authority. Issued opaque references are nonblank text of at most200 codepoints; the
current command parser still treats references as opaque and proves no eligibility.
Published definitions/hash, eligibility, outcomes and revisions are immutable. KDG stores
verified external account/actor IDs without cross-owner foreign keys or another registry.
Definition hash is the publication-content digest field, not a command fingerprint;
its computation/publishing command remains consuming work.

Capture preserves original owner/child/version/creation facts and the exact accepted
untrusted device timestamp string. Observation date/answers/revision alone may update
through the restricted runtime role; trusted actor/time attribution is server stamped.
There is no child/date uniqueness. Parent actor fields remain explicit required inputs
for future protected commands; no writable parent endpoint or role grant is activated.

Outcome keeps the existing private adapter's INSERT/SELECT columns unchanged. Generated
capture_id/result_revision derive from the compact typed result; composite uniqueness
and FKs bind history to the exact org/outcome/executor/command/operation/capture/revision.
Each capture has one create outcome at revision1; edit no-op outcomes need no new history.
The current capture revision has a deferred history FK. A deferred snapshot constraint
trigger also checks every changed capture row against its matching immutable snapshot,
including exact date/answers/device time/editor. This addresses a concrete gap: a latest-
revision FK alone would allow an intermediate changed revision to omit its snapshot.
No-op updates cannot advance revision and do not invent revision evidence.

Tables enable and FORCE RLS. Explicit grants permit domain reads and capture/outcome/
revision writes under the verified transaction org/account/actor/mode. Outcome reads
remain original-executor scoped even in all modes. No delete/cleanup/DDL or parent mutation
authority is granted; missing context fails closed. These policies are candidates, not
verified current-user authorization. The HTTP consumer must obtain current Access and
recheck local child/assignment/eligibility and original definition under owner locks.

## Offline ATDD and focused verification

P is retained `platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
No dependency install or alternate database architecture was introduced.

- `P -I -B apps/kdg-capture/write-tests/test_capture_schema.py`:13 PASS.
- `P -I -B apps/kdg-capture/write-tests/test_operation_outcomes.py`:16 PASS unchanged.
- `P -I -B apps/kdg-capture/migrations/tests/test_foundation.py`:9 PASS, including
  actual CLI refusals before database access. No live fixture command runs.

Schema acceptance first failed because the linked storage DDL was absent. Focused
rendering first failed for the missing snapshot guard. A separate test incorrectly
matched the letters OR inside FOR; corrected to a word-boundary assertion, preserving
its intended no-alternative-caller policy expectation. Logs remain retained.

The tests invoke candidate.upgrade using actual Alembic MigrationContext/Operations in
PostgreSQL offline mode with no connection. They smoke-check emitted links/generated
values/privilege statements, deterministic rendering and unchanged active history.
They do not enforce constraints or execute PL/pgSQL, RLS, commits or concurrency. There
is no custom runtime schema/ledger inventory check. Production env.py still refuses
--sql; the test does not change that policy or apply/export an approved migration.
Source/log bindings are in [the receipt](evidence/linked-storage-schema-20261023.json).

## Delivery impacts and consuming gates

Scaffold: none; these tables/policies are KDG-owned. Existing controlled migration and
transaction scaffolding is reused unchanged. Shared UI: none. Agent context: current
instructions suffice. Documentation: owner contract, migration guide/current handoff and
this evidence; historical content retained. ADR: no new decision; existing structure,
attribution, first-committed outcome and ADR-0020 migration/recovery decisions apply.

Before promotion into active versions, qualify actual PostgreSQL syntax/functions,
restricted-role/RLS/immutable/scoped FK and null/alternate-writer cases. Add concrete
current-authorized create/edit transactions with capture→outcome→history ordering,
original-resource replay and lost-response recovery. Verify rollback, duplicate races,
original definitions/eligibility/member renewal and bounded waits. Ordinary release
needs previous-code compatibility, controlled migration coordination, failure-blocked
activation and explicit recovery; never auto-downgrade. Existing retained native fixture
requires verified custody/resumption and a new source-bound suite for the new head;
its historical ledger-only inspector/evidence must not be relabeled or overwritten.
No native fixture is touched here. Story1.2 bootstrap retains its separate fingerprint
contract. Fingerprints/HMAC, real accounts/access, Leave/editor, provisioning/deployment/
pilot/production and cleanup remain outside this delivery. TypeScript7.0.2 is preserved.

## Independent review and final results

All7 blind review findings are individually triaged in the
[delivery spec](../../../_bmad-output/implementation-artifacts/spec-kdg-linked-storage-schema.md).
Corrections add stored-target ownership to outcome INSERT, a deferred outcome→reported
history revision FK, history-side snapshot validation, null-safe initiator agreement,
explicit device clock bounds and Python-compatible blankness. Expanded smoke assertions
protect these declarations. Review-focused tests first reported4 failures before fixes.
No review finding is deferred. The existing private outcome adapter remains unchanged.

Final13 schema smoke checks PASS in0.148s; existing16 outcome tests and9 migration-
foundation tests PASS. Final SQL is rendered with the approved retained Python environment
into `/tmp/kdg-linked-schema-render.sql`; the receipt binds its hash. Its generation
invokes the test module's render(), which uses Alembic offline Operations without a URL,
engine or connection. This is neither a migration execution nor a native proof receipt.

Before documentation additions,227 tracked KDG/template/dependency files were byte-
identical to baseline. The final preservation check excludes only this delivery's paths;
historical native reports/inspectors, active migrations, API/validators/outcome adapter,
managed copies and dependencies remain unchanged. All150 preexisting dirty/untracked
paths remain present; concurrent work is excluded from the scoped local commit. Previous
next-session content is retained as an exact suffix. TypeScript remains7.0.2.

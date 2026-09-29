---
title: Scribeswell database access behind FastAPI
type: refactor
created: 2026-09-29
status: done
route: dispatch
baseline_commit: 7bc6b21a8f210675cf8dcf4013dc802b82c635a9
review_loop_iteration: 0
context:
  - AGENTS.md
  - platform/docs/architecture/decisions/0020-safe-schema-changes-and-release-recovery.md
  - platform/docs/architecture/decisions/0023-structured-operational-logs-and-sensitive-data.md
---

<frozen-after-approval reason="Owner accepted direct PostgreSQL recommendation and authorizes autonomous reversible implementation; production changes require concrete execution approval">

## Intent

Scribeswell runtime and corpus importer currently use Supabase PostgREST and require
its schema to be exposed separately from FastAPI. Replace that dependency with
restricted direct PostgreSQL access so the application works with only public and
graphql_public exposed. Preserve the public reader and all existing study behavior.
The app directory already uses verified Auth claims and a static catalogue, not
PostgREST: correct previous documentation instead of adding database access there.

## Boundaries & Constraints

Always preserve API shapes, canonical ordering, missing-data errors, Hebrew text,
lexicon/root matching, occurrence counts/pagination, existing IDs and importer audit.
Keep Supabase Auth and shared sign-in. Use a bounded reusable connection pool and
parameterized SQL, short transactions, explicit TLS production URLs, finite database
and pool waits, safe errors without credentials or SQL content. Runtime authority
must be read-only and confined to Scribeswell; import authority is separate and
cannot mutate identity/PtS/content. Keep privileged URLs server-side.
Never fetch new corpus material, reset production, alter reviewed source text, add
browser database queries or import another silo's server code. No schema/role/config
changes on production, import, deployment, push, or schema unexposure during local
implementation. Prepare the tested operational transition and require approval to
execute it. Retain compatibility of existing stored data/views and old runtime
until transition; no destructive revocation of unrelated consumers.

## I/O & Edge-Case Matrix

| Scenario | Input/state | Expected behavior | Error handling |
|---|---|---|---|
| Public reading | Existing complete corpus; no user | Same books, chapters, verses, morphology and lexical metadata | Existing contracts |
| Missing/incomplete data | Unknown book/word; empty words; gaps; missing morphology | Existing not-found vs integrity distinction | Safe existing HTTP errors |
| Large lookup | Long chapter; many matching lemma variants; book filter/page | No row truncation; canonical ordering and accurate word/verse totals | Parameterized filters |
| Corpus import | Valid source; repeat or interrupted import | Preserved IDs; full audit; repeat without duplicates | Reject malformed source/extra rows; no silent success |
| Restricted roles | Runtime tries writes/other owner; importer tries identity writes | Database denies | Test real PostgreSQL grants/RLS |
| Provider isolation | Data API schema unavailable | Reader/importer still work; directory uses Auth only | No REST fallback |
| Failure | DB unavailable or statement/pool timeout | Bounded safe failure; connections released | No credentials/content in response/log |

</frozen-after-approval>

## Code Map

- `backend/services/bible_service.py`: six reader queries and occurrences currently Supabase client; preserve response assembly/lexicon matching.
- `backend/config.py`, `requirements.txt`, `main.py`: configuration/dependencies/pool lifecycle and safe error handling.
- `tools/py/import_bible.py`, `scripts/seed.py`: canonical decoder, full source validation, per-chapter writes/audit; preserve verify-only/dry-run/book resume.
- `tests/test_reader_integrity.py`, `test_import_bible.py`, `test_word_inspector.py`, `test_lexicon.py`: existing characterization assertions; replace obsolete transport doubles without weakening expectations.
- `supabase/migrations/20260614000000_scribeswell_schema.sql`: inspect actual filename; existing tables, read views, RLS, sequence grants. Do not edit applied SQL.
- `deployment/manifest.json`, `runtime.env.example`, Dockerfile, `platform/deployment/registry.json`, `host-release.py`: declared role/project validation, bootstrap fingerprint, images and smoke fixtures.
- `services/app-directory/routers/apps.py`, `auth/jwt_optional.py`: static catalogue/verified claims; no database client required. Generated-marked files must not be edited directly.

## Tasks & Acceptance

- [x] Characterize existing reader/importer behaviors, then observe failing direct-database acceptance before implementation.
- [x] Add owner-local PostgreSQL access and convert runtime/importer; keep meaningful contract coverage and pool lifecycle tests.
- [x] Add idempotent explicit owner role/grant SQL under deployment bootstrap paths: scribeswell_runtime read only, scribeswell_import selective read/insert/update/sequence permissions and RLS; no passwords in SQL. Rehearse actual roles against existing schema/data, prove cross-owner denial and compatibility.
- [x] Update dependency/env/manifest/host preflight fixtures and Docker packaging; runtime requires SCRIBESWELL_DATABASE_URL with declared scribeswell_runtime role; importer uses SCRIBESWELL_IMPORT_DATABASE_URL. Reject old runtime service-key authority rather than silently retain it. Preserve optional JWT requirements appropriately.
- [x] Update owning README/release inventory and platform deployment docs: directory correction, local setup, prepare/apply/verify transition and recovery, schema removal only after affected consumers pass; record scaffold/UI/context/ADR impact.
- [x] Run focused tests, full Scribeswell suite, affected deployment suite and real PostgreSQL acceptance. Record exact commands/failures/successes and requirement traceability here.

Given schemas are unexposed, when public reading and corpus audit execute through
FastAPI/operator tools, then no Data API request or broad Supabase service key is
needed. Given existing data, when upgraded then response contents and counts are
unchanged. Given a previous version, when new grants are installed then its existing
access remains valid until explicit cutover. Given runtime credentials, when writes
or another owner's data are attempted then PostgreSQL denies access. Given a failed
role/config preflight, when release runs then activation is blocked.

## Implementation Notes

No user-visible design gaps. Footprint spans reader/importer, role preparation and
shared release contracts for one goal. Production mutations remain separate. Local
planning approval is covered by the owner's autonomous-work instruction. No UI or
scaffold behavior should change; only proven generic release validation is shared.
Existing accepted ADRs are immutable; this implements their authority/isolation
rules, not a new platform architecture decision. Implementation agent may use local
Docker/Supabase test databases but must not touch production, commit or push.

## Spec Change Log

## Review Triage Log

| Finding | Verdict and evidence | Route |
|---|---|---|
| Blind1 replication role | Medium: rolreplication is omitted from existing-role checks; can retain elevated authority. | patch |
| Blind2 column grants | Medium: has_table_privilege omits column ACLs. Existing RLS still blocks runtime UPDATE in the supplied schema, but cross-owner column grants with applicable policies can retain access. Reject conflicting explicit column authority. | patch |
| Blind3 non-table authority | Medium: direct sequence/schema-CREATE/definer grants and routine ownership are omitted. PUBLIC routine review is already a documented production gate; named-role contamination needs explicit checks. | patch |
| Blind4 NOLOGIN | Medium: existing role can pass yet fail actual login. | patch |
| Blind5 chapter metadata | Medium: chapter upsert precedes transaction, so failed/unattempted empty chapter rows survive. Earlier behavior did this too, but new chapter-atomic contract makes moving this existing write into its transaction a direct correction. | patch |
| Blind6 new error identifier | Medium: new 503 only English text; add compatible stable code under ADR0031. | patch |
| Blind7 timeout mismatch | Medium: shared preflight accepts connect_timeout values rejected by runtime. Demonstrable invalid configuration should fail before activation. | patch |
| Blind8 cluster fixture mutation | High: local host guard does not protect pre-existing cluster roles/passwords. Require fresh absent application roles and clean only fixture-created roles. | patch |
| Blind9 fixture URL replacement | Medium: non-fixture admin credentials leave wrong role URL; parse/rebuild credentials. | patch |
| Blind10 multi-chapter test | Medium: one-chapter test cannot verify earlier/later recovery boundary. | patch |
| Edge1 replication | Medium: same verified omission as Blind1. | patch |
| Edge2 chapter metadata | Medium: same verified state as Blind5. | patch |
| Edge3 cluster mutation | High: same verified unsafe fixture precondition as Blind8. | patch |
| Edge4 fixture URL | Medium: same verified URL assumption as Blind9. | patch |
| Verification1 populated bootstrap | Medium: test applies grant SQL before corpus exists; add preservation assertions over populated legacy schema. | patch |
| Verification2 effective limits | Medium: existing cancellation test installs own30ms limit, masking disabled production defaults; assert real connection settings. | patch |

All fixes are confined to demonstrated existing paths, add no public interface
except a compatible machine-readable error field required by current policy, and
need no new product decision. Preserve tested behavior and additive old-runtime
compatibility. No production role or configuration action has occurred.

## Verification

Use affected Python suites and existing container smoke conventions; actual PostgreSQL
role/contract checks must run, not merely exist or skip. Keep real integration fixtures
small but cover corpus structure, long chapters, ordering, rollback/replay and denial.
Full canonical source dry-run must still validate 39/929/23213/306785/471674 with zero
errors. Production remains paused until separately approved role/settings transition,
full import/verify and HTTP/auth/storage acceptance.


### Implementation evidence — 2026-09-29

- Reader uses an owner-local psycopg repository, parameterized values/quoted identifiers,
  base tables under role RLS, bounded pooled connections and safe 503 errors. Existing
  response assembly, ordering, Hebrew, lexicon/root matching and counts remain intact.
  Synchronous reader routes execute off the event loop. Pool opens/closes with lifespan.
- Importer uses separate authority and commits each chapter's writes plus audit together.
  Full source validation precedes writes, replay preserves IDs, malformed/extra data fails.
  Existing schema migration and legacy views/grants remain unchanged.
- Explicit idempotent role bootstrap is included in release fingerprints; role/project
  preflight and obsolete-service-key rejection precede activation. Image includes the
  importer/decoder/seed wrapper but never invokes import or SQL at startup.
- Directory correction and preparation/apply/verify/recovery are documented in the owning
  README and deployment README. No directory implementation change was needed.
- Impact: scaffold unchanged (owner-local repository; generic forbidden-env manifest
  validation only); shared UI unchanged; agent context unchanged (existing ADR policy
  already applies); documentation updated; accepted ADRs unchanged. No new architecture
  decision, browser DB calls, corpus acquisition or production action.

| Requirement | Evidence |
|---|---|
| Existing reading, Hebrew, morphology, roots, missing data | Existing reader/word-inspector/lexicon assertions retained; repository doubles replace transport doubles; PostgreSQL HTTP + missing-word exact contract |
| No row truncation; variants/filter/page totals | Actual PostgreSQL 1201-word chapter and 1002 lemma variants; canonical-order regression assertions |
| Replay, stable IDs, audit, rollback | Actual PostgreSQL import/reimport/verify and injected mid-chapter failure; extra-row rejection |
| Restricted roles/RLS/old compatibility | Actual runtime/import logins; base-table RLS active; identity/PtS/content and runtime-write denial; old service-role view read/write retained; bootstrap replay and contaminated-role failure |
| Provider isolation | Disposable PostgreSQL has no Data API at all; reader/importer succeed; directory Auth-only code inspected |
| Bounded safe failures/lifecycle | Statement and pool timeout/reuse, unavailable DB HTTP 503 and secret-log assertions, SQL parameterization, pool lifecycle |
| Release safety and packaging | Host wrong-role/service-key rejection, fingerprint inclusion, full deployment suite, non-root/no-network container smoke |

Exact verification commands and results:

- Before implementation: `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_direct_database.py -q`
  failed as expected: missing `database` module (1 failed). The original characterization
  suite started before edits but stalled in sandbox TestClient execution; reruns outside
  the sandbox completed. Assertions were preserved, not weakened to dismiss failures.
- `apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_direct_database.py apps/scribeswell/tests/test_import_bible.py apps/scribeswell/tests/test_reader_integrity.py apps/scribeswell/tests/test_word_inspector.py -q`
  — 17 passed.
- `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:55439/postgres apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests -q`
  — 34 passed in 6.49s, including actual PostgreSQL tests (no skips). Fixture-only
  credentials; database is an isolated disposable PostgreSQL 15 Docker container.
- After strengthening missing-word/RLS/safe-error/bootstrap assertions:
  `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:55439/postgres apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests/test_postgres_acceptance.py apps/scribeswell/tests/test_direct_database.py -q`
  — 10 passed in 1.84s. One pre-existing Starlette/httpx deprecation warning.
- Real PostgreSQL first exposed an invalid empty `DO UPDATE SET` for key-only chapter
  upserts. Fixed using a conflict-key self-assignment, preserving existing IDs. Initial
  sandbox DB connection failure was retried outside sandbox. Neither failure was ignored.
- `apps/scribeswell/.local/venv/bin/python apps/scribeswell/scripts/seed.py --dry-run`
  — validated 39/929/23213/306785/471674, zero errors; SHA-256
  `c2d8e9e565be4ee69f938b444e5e0dc37fdfd0d9ccb185d1a5f8d95fab91c498`.
- `apps/scribeswell/.local/venv/bin/python -m pytest platform/deployment/tests -q`
  — 106 passed, 85 subtests passed.
- `node --test platform/deployment/tests/*.test.mjs` — 13 passed outside sandbox;
  initial sandbox frontend-inputs subprocess failure resolved by the required rerun.
- `python3 tools/py/run_compose_supabase.py --check-only` — passed; no files changed.
- `docker build -f apps/scribeswell/deployment/Dockerfile -t agriplatform-scribeswell:release-check .`
  — succeeded, image `sha256:5cb67acc71d0eea7696a6f12a0cea9cf1e4ebaf582e457f9cf15c757a977efca`.
- `python3 platform/deployment/tests/container_smoke.py` — all five images healthy,
  non-root, no outbound network, required artifacts present, private env/archive absent.
- `git diff --check` — passed.

Production remains paused. Target-specific PUBLIC/default grants and executable
security-definer routines must be inventoried in the approved transition because a
PostgreSQL role cannot individually deny authority granted to PUBLIC. No production
schema/role/settings change, import, deployment, push or schema unexposure occurred.
No full production corpus audit, Auth/Storage acceptance or production-readiness claim
is made by the disposable integration rehearsal.

### Review resolution and final verification — 2026-09-29

All 16 individually triaged review findings were resolved; no review findings were
deferred. Existing-role checks now include login/replication, explicit column and
sequence ACLs, schema CREATE, routine ownership and direct security-definer grants.
Chapter metadata participates in the chapter transaction. Safe 503 responses retain
`error` and add `code=database_unavailable`; host preflight validates connection
limits. The disposable fixture refuses existing application roles before mutation,
cleans its own roles and parses credentials. Acceptance now proves populated legacy
bootstrap preservation, multi-chapter failure/retry and effective timeout settings.

Root verification after patches:

- `SCRIBESWELL_TEST_DATABASE_URL=postgresql://postgres:fixture@127.0.0.1:55439/postgres apps/scribeswell/.local/venv/bin/python -m pytest apps/scribeswell/tests -q`
  — 47 passed in 20.26s, no skips; one existing Starlette/httpx warning.
- `apps/scribeswell/.local/venv/bin/python -m pytest platform/deployment/tests -q`
  — 116 passed, 85 subtests passed in 14.52s.
- `python3 platform/deployment/tests/container_smoke.py > /tmp/scribeswell-direct-container-smoke.log 2>&1`
  — rebuilt and verified all five services: healthy, non-root, no outbound network,
  required artifacts present and private configuration/archive absent.
- `git diff --check` — passed.
- Previous unchanged Node checks, composition check and full canonical source dry-run
  remain applicable; no additional source or frontend changes were made.

Read-only production inspection found an existing PUBLIC-executable role lookup
function. The owning deployment README records the targeted correction required
before live role installation, preserving existing authenticated callers. This is
an unexecuted production gate, not a deferred local review finding. No production
role, credential, configuration, corpus, schema exposure or deployment was changed.

### Approved production transition guard correction

The approved transition stopped at the role bootstrap: Supabase grants PUBLIC
SELECT on extension statistics relations without PUBLIC USAGE on their schema.
The table guard counted this unreachable authority. New actual-PostgreSQL acceptance
reproduced the rejection (1 failed before correction). The guard now checks schema
USAGE for effective PUBLIC table access while continuing to reject every explicit
cross-owner role table grant, including grants on inaccessible schemas. The paired
acceptance grants PUBLIC schema USAGE and confirms rejection. No global PUBLIC
grants were changed to work around this issue. Role creation rolled back on failure;
the separately approved targeted role-lookup function correction had committed.

Post-correction full real-PostgreSQL Scribeswell suite: 48 passed in 12.38s.

### Production outcome after explicit owner approval

Restricted roles and protected runtime credentials installed; actual role isolation
and the targeted legacy function permission correction verified. Canonical import,
separate verify-only pass and complete repeat import all passed with zero errors:
39 books,929 chapters,23213 verses,306785 words,471674 morphemes. Full-row digests
including IDs stayed identical across all five tables. FastAPI anonymous reader,
long chapter, morphology, lexicon, occurrence filter/pagination and404 checks passed
against production with runtime authority. PtS/account/bucket counts/settings were
rechecked and preserved. Public activation and schema unexposure remain separate.

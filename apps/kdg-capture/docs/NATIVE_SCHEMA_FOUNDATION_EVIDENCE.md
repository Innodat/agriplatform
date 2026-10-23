# Native KDG schema foundation acceptance

The simplified platform migration approach now has actual PostgreSQL acceptance for
KDG's initial private Alembic ledger. The existing migration helper/env/history passed
without a runtime implementation change. Supabase PostgreSQL, Alembic, separate owner
history and restricted runtime credentials remain the agreed architecture.

bmad-help [BD] selected the unfinished native prerequisite. The user's prior explicit
exception authorized resuming retained run99b7231c-0a5b-4bdb-98e8-3329564c526a at55482,
one new template0 KDG database and exactly three restricted database roles. The new
owner adapter reads the actual private synthetic credential format, validates custody
and refuses existing roles; the earlier failed schema_fixture.py remains unchanged.
Nothing connects to unknown54322 or mutates a historical business database.

The first actual CLI `alembic upgrade head` succeeded using the new independent migrator
login. The final seven-stage native suite verifies:

- Actual distinct migrator/runtime/operator session identities and unchanged repeat upgrade.
- Sixteen SQLSTATE42501 ledger, DDL, cross-owner and role-assumption denials, plus refusal
  to yield migration connections under runtime/operator credentials.
- Successful synthetic CREATE followed by forced failure, verified absent table afterward,
  unchanged head and explicit successful forward retry.
- Unknown fixture revision refusal, unchanged failed state, conditional restoration and retry.
- A held owner advisory lock causing bounded refusal, unchanged head and retry after release.

An independent SELECT-only inspector checks final head0001_kdg_foundation, ledger-only
owned tables, foreign sentinel, restricted role flags/private ledger and unchanged
preexisting role/database metadata. Every inspector connection enforces read-only mode;
optimized Python is refused so its assertions cannot disappear. Historical data rows
were not rehashed; no historical qualification script/preparer was run.

The initial native report was preliminary. Build review identified a test false-positive:
a failed CREATE could masquerade as successful DDL rollback. Its new emitted regression
first failed with AssertionError not raised, then passed after requiring a successful-DDL
marker. The corrected complete native suite and final independent inspection passed.
Review follow-up found no remaining substantive issue. Failed/preliminary frames remain
retained and are not represented as final source-qualified acceptance.

Neutral scenarios and three offline denial/rollback-oracle tests are promoted together
into scaffold native-database-tools, adopted by KDG through the preservation installer.
The existing database-tools inventory is unchanged. Builder tests execute both emitted
suites in a fresh rendered/installed app and verify parity/tamper preservation. KDG
retains target preparation, credential custody, exact roles/schema/head and upgrade policy.
The scaffold never provisions a database or automatically executes native tests.

Final offline checks:11 emitted wrapper tests,3 oracle tests,9 owner tests (five actual
CLI refusal cases),73 builder tests, strict TypeScript7.0.2 and both managed parity checks
pass. The renderer inventory was explicitly extended for the two new emitted files;
the earlier expected-file mismatch is retained as an explained test update. No dependency,
manifest/lock or approved baseline change. Shared UI and agent context need no change;
accepted ADR0015–0020 are unchanged. API/worker startup and release registry are unchanged.

The run stopped normally with all databases, roles, credentials, data and Docker resources
retained. Exact commands, retained fixture/report paths, final lock timing, source/log
hashes, review and limits are recorded in the [receipt](evidence/native-schema-foundation-20261023.json).
No business table/RLS, capture write/API, previous-version domain compatibility, coordinated
release activation, complete Story1.1 or production readiness is proved. No real Auth/
accounts/access, Leave/editor, general provisioning, deployment/pilot, cleanup or
fingerprints/HMAC work is included. Concurrent work and historical evidence are preserved.

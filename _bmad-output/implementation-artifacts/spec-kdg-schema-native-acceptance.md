---
title: 'Native acceptance of the KDG schema foundation'
type: 'feature'
created: '2026-10-23'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

Complete native PostgreSQL acceptance of the reviewed KDG empty-schema/private-Alembic-ledger foundation. The user explicitly approved resuming the retained synthetic stack and preparing one isolated KDG test database and its three database roles as an exception to the previous no-provisioning boundary. This is not authorization for real accounts/access, Auth provider setup, other applications, business domain tables, deployment or production.

Use only the retained marked kdg-local run99b7231c-0a5b-4bdb-98e8-3329564c526a at loopback55482 through existing pinned Supabase CLI lifecycle. Verify marker/custody and use existing private synthetic administrator credentials without printing them. Create one fresh exclusive database kdg_schema_<UUIDhex>, owned by the fixture administrator, from template0, and exact restricted LOGIN roles kdg_capture_migrator/runtime/operator. Existing exact roles must refuse before alteration/adoption. Prepare only the isolated fixture's empty owned schema and a foreign denial sentinel. Retain all created resources, credentials privately and partial/failure evidence; never reset, drop, prune or modify prior fixtures. Stop the resumed stack normally with all data retained at completion.

Given this prepared target, prove actual independent migrator/runtime/operator logins, successful empty Alembic upgrade and unchanged repeat, exact ledger/catalog/ACL postconditions and runtime/operator denial of schema changes and ledger access. Exercise wrong authority, malformed/unknown schema/history/ACL states, cross-owner authority, lock waiting/refusal, postcondition rollback and explicit forward retry on this isolated target. Fault mutations must be bounded and rolled back/restored, never applied to historical databases/roles. Preserve source/proof custody and independently inspect final retained state. A database exception/timeout is not evidence that effects rolled back; verify state.

Observe the actual positive acceptance result before changing guards. If native behavior exposes a guard defect, capture its failure and add focused regression, then fix canonical platform templates and generated tests, synchronize KDG through the existing preservation installer and repeat affected proof. Reusable native scenario mechanics and appropriate scaffold tests remain platform-owned; KDG owns exact schema/history/roles. No generated hand edits, baseline dependency change or weakening expectations to dismiss unexplained failures.

Preserve concurrent work, previous candidate/historical evidence, Docker resources and TypeScript7.0.2. No Leave/editor, production, real accounts/access, business writes, general provisioning, deployment/pilot, cleanup or fingerprints/HMAC. This proves the initial empty-schema boundary only, not tenant-table RLS, questionnaire/capture persistence, full WRITE/Story1.1 or release readiness. API startup and production registry remain unchanged.

</frozen-after-approval>

## Implementation Notes

- bmad-help [BD] selected the explicit outstanding native gate from e4f4b1c5ad87452d925c8c8512b14253273490db and current evidence/contracts. Freeform prerequisite, no sprint key/product spec duplication. Existing dirty-tree preservation authorized; /tmp/kdg-schema-native-before.json binds starting sources. No reset/stash.
- User approval covers the concrete resource effects already discussed; do not reconfirm. All other prior boundaries remain. Small isolated acceptance/preparation tooling and potential canonical guard fixes; no unapproved irreversibles/intent gaps. Retain failures and resources, use oneshot.
- Read-only investigation completed. Existing atomic preparer is incompatible (DB-owning random migrator/two roles) and must not be executed. Reuse custody/retention concepts only. Use existing Access migration environment at Python3.15/SQLAlchemy2.1.4/Alembic1.20.0/psycopg3.3.6; existing Node26.11.1/TS7.0.2 and Supabase2.120.0, no install.
- Code map: platform builder test native scenario helper plus KDG migrations/tests explicit prepare/qualify/inspect scripts; canonical database-tools/owned_migration.py and test_owned_migration.py only for reproduced native fixes. Existing sync-kdg-database handles managed copies. Candidate history/ADRs immutable unless a concrete source defect requires owning adapter correction; no old proof refresh.
- First actual positive case is a gate, not a skipped/mocked native test. Native template0 fixture avoids inherited application/extension privilege pollution without revoking anything in retained DBs. Actual session_user checks preclude administrator SET ROLE from counting as a restricted login.
- Impacts: platform/scaffold neutral fixes/tests in same delivery; KDG native owner tests/history policy; UI unchanged; existing agent context sufficient; additive docs/evidence/receipt/handoff; accepted ADRs unchanged (0015–0020). Native DB/roles creation limited to this explicit approval; no production registry change or API migration startup.

- Resume2026-10-23 after explicit user clarification/approval of focused platform verification (5240fa0f5d4c0d53dd47b77ae7072c4833f8f7e6). The original frozen inventory matrix is superseded by that human direction: use ordinary Alembic revision handling and focused actual allow/deny/lock/rollback/retry checks. Resource authorization remains exact and unchanged. Preserve the original intent/history verbatim; do not restore the removed catalogue framework.
- Current route remains oneshot for this already approved native qualification. No new intent gap or resource authority required. Dirty tree preservation authorized; current snapshot /tmp/kdg-native-focused-before.json. Prior schema_fixture.py remains unchanged as failed historical draft; implement a corrected small explicit fixture adapter separately.
- Owner credential-source diagnosis settled by read-only filesystem inspection: credentials.json has databases.bridge (a loopback postgres URL) rather than admin_url. Validate target marker and private file custody, derive only the fixed postgres administration DB and supabase_admin login using the retained synthetic password. Never print private URLs/passwords.
- Scope: actual initial Alembic upgrade/repeat, actual separate restricted logins and DDL/ledger/cross-owner denials, bounded owner lock refusal/retry, rollback of synthetic transactional DDL, unknown-history refusal/restoration. Promote neutral native checks into the existing scaffold after first consuming proof. No business table/API change or release coordination claim.
- Impacts: shared neutral native-check helper/tests and managed scaffold parity where proven; owner fixture/history remains KDG-specific. UI/context/ADRs unchanged; add native evidence/receipt and current handoff. Approved dependencies and historical evidence/resources retained.

- New native_fixture.py successfully created only the authorized fresh template0 DB and three NOINHERIT/nonprivileged roles, owner schema and foreign sentinel. Old failed schema_fixture.py remains byte-identical. Initial actual CLI upgrade succeeded, followed by native suite and independent SELECT-only inspection. No runtime helper/env/history change was required.
- Shared native scenario module and three denial/rollback-oracle tests promoted to templates/application/native-database-tools and KDG's separate managed root. Existing installer refuses inventory expansion (observed scaffold_ownership_invalid); respected that preservation boundary rather than modifying manifests or installer behavior. Renderer explicitly emits the new files; fixed the explained expected-file inventory mismatch in its acceptance test.
- ATDD outer loop: actual candidate upgrade and restricted PostgreSQL behavior qualify the existing implementation. Review found a test-oracle failure, not a production migration defect. Focused inner regression observed AssertionError not raised when CREATE fails; successful-DDL marker fixes it. Final native7 stages and independent inspector rerun PASS. No mock is counted as actual SQL permission/rollback evidence.
- Final offline PASS:11 neutral wrapper,3 emitted oracle,9 KDG owner tests (five actual CLI refusals),73 builder tests, strict TS7.0.2, both managed parity checks. Native fixture/report/logs and exact commands are bound in docs/evidence/native-schema-foundation-20261023.json. Initial failed/partial proof and the original candidate evidence remain preserved.

## Review Triage Log

- medium / patched: rollback oracle could accept a CREATE failure as successful-DDL rollback. Added an observed failing emitted regression and explicit execution marker, then reran the complete native suite; no runtime code change.
- Follow-up / resolved: independent reviewer /root/review_kdg_native_focused confirmed marker fixes the false positive, canonical/managed parity holds, and no remaining substantive issue. Native requalification and read-only inspection subsequently passed. No new deferred defect.

- Final independent read-only inspection PASS after corrected native rerun; normal dev.py stop completed with all resources retained. Inspector refuses optimized Python before DB I/O (actual negative command verified). Current runtime runner/env/policy/history and all dependency/lock baselines remain unchanged. Synthetic fixture creation is the already approved narrow exception, not general provisioning.

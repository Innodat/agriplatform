# KDG schema foundation — reviewed candidate, native acceptance pending

bmad-help [BD] selected the first KDG-owned schema boundary after637c485f428aa87257ab76a49021579fabaef1ac.
The user also requested platform/scaffold applicability. bmad-build prepares separate
owner Alembic history and policy, with reusable neutral guards and unit tests emitted by
the existing builder and adopted in a separate managed KDG root. Existing Auth/host
managed inventories, API/locks and production migration registry remain unchanged.

This is an inert code candidate only. It creates no business tables, roles, databases
or schemas in this delivery. A future controlled upgrade would initialize the private
Alembic ledger in an already prepared dedicated KDG schema. Actual PostgreSQL schema,
role, privilege, lock, rollback, recovery and compatibility acceptance is unverified.
No mocked catalog response is presented as a database isolation or RLS result.

The first relevant unit acceptance RED runs the minimal candidate transaction skeleton
under a wrong role: it yields the migration connection instead of refusing, so
MigrationError was not raised. The subsequent guard implementation passes. The first
isolated-script run failed sibling-module discovery; that is diagnostic, not behavioral
RED. Exact logs/commands and final source hashes are retained in the receipt. This RED
is a test-double control-flow failure, not an executed PostgreSQL acceptance failure.

Final neutral tests cover authority flags/session/owner/CREATE/membership refusal,
prepared schema/ACL inventory, cross-owner authority rejection, exact supported ledger,
postcondition rollback paths, safe errors and transaction settings. Owner tests load
real Alembic revision metadata and actual env.py with test-double engine/context to prove
owned configuration, direction refusal, callback order, postcondition failure and disposal.
They do not parse/evaluate PostgreSQL catalog SQL. Actual CLI offline mode is refused.

Read-only reachability checks find the known disposable endpoint55482 stopped; unknown
54322 is not used. Prior atomic fixture credentials/roles/history are not adopted: its
DB-owning migrator cannot qualify this contract. Existing preparers would create roles/
databases, so no preparer, Docker lifecycle or native upgrade is run. Native acceptance
needs an explicit exception to the user's no-provisioning boundary or an independently
prepared compatible target. See ../migrations/README.md for exact required target/roles
and the future acceptance matrix. Existing data/resources/evidence are preserved.

Review patches address cross-owner CREATE/ownership, standalone schema objects, permanent
non-RLS ledger/catalog checks, transaction deadline coverage, per-role privilege pairing
and memberships in both directions. Final read-only follow-up finds no remaining
substantive code issue, while preserving the explicit native qualification gap.

Impacts: neutral application scaffold code/emitted tests and KDG managed parity in this
slice; no other app/service migration. Shared UI unchanged. Existing agent context
sufficient. Owner/scaffold guide, evidence/receipt and additive handoff updated. Accepted
ADRs unchanged; applies0015/0016/0017/0018/0020. No migration execution, deployment registry
change or release activation. Dependency baseline including TS7.0.2 is unchanged.
Fingerprint/HMAC remain deferred. No Leave/editor, production, real accounts/access,
provisioning, deployment/pilot or cleanup.

[Candidate receipt](evidence/schema-foundation-candidate-20261023.json) records offline
results, source/log hashes, preservation, review triage and native_acceptance=false.

Final offline results:10 neutral emitted unit tests,8 KDG policy/history/env wiring tests,
5 actual CLI refusal cases,72 builder tests and strict TypeScript7.0.2 pass. Full offline
generation proof-IWqNGL passes bootstrap_only=true,generation_ready=false. Retained migration
tools are Python3.15.0,SQLAlchemy2.1.4,Alembic1.20.0,psycopg3.3.6. Nothing was installed.
The candidate delivery is complete; native_acceptance remains false and no DB security,
controlled upgrade, transaction timing or recovery outcome is asserted as proven.

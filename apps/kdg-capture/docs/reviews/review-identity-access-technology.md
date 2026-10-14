# Identity/Access substrate technology and source review

2026-10-14. Required architecture technology/source gate for
platform/docs/architecture/contracts/identity-access-execution-substrate.md.
Read repository-owned source/inventory/status and official PostgreSQL documentation.
No live target inspected; no SQL, migration, privilege, install or code change run.

**Verdict: PASS for the selected planning baseline.** PostgreSQL supports the
chosen constraints, role separation, fixed projection routines and operator binding.
One small qualification should be explicit: NULLS NOT DISTINCT requires PostgreSQL
15 or newer. ENV must check that floor on its supported CLI/deployment image set;
this is no instruction to upgrade a live database or pick an unrelated latest image.

## Verified technology fit

- NULLS NOT DISTINCT uniqueness prevents duplicate authority/outcome tuples when
  nullable platform/org/app/target fields match. PostgreSQL introduced it in 15.
  Active-only membership uniqueness correctly uses a partial unique index, while
  retained retired rows keep their separate IDs. Both mechanisms exist in the
  selected PostgreSQL family. [PostgreSQL 15 release](https://www.postgresql.org/docs/15/release-15.html),
  [constraints](https://www.postgresql.org/docs/current/ddl-constraints.html).
- ENABLE plus FORCE RLS, separate non-owner/NOBYPASSRLS reader and command roles,
  and column/EXECUTE privileges form a valid design. FORCE alone does not constrain
  a superuser/BYPASSRLS role; the explicit role exclusions matter. RLS is additional
  to privileges, not their replacement. Actual inherited/default grants and all
  applicable permissive policies must be inventoried and tested as already required.
  Constraints can bypass RLS for integrity, so safe failure mapping remains necessary.
  [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html).
- SECURITY DEFINER executes as its owner; the selected NOLOGIN restricted reader
  owner is materially different from a table-owner/migrator definer. The fixed
  pg_catalog,pg_temp search path, fully qualified owner objects, no dynamic SQL and
  creation-transaction PUBLIC revocation match official security guidance. STABLE
  read routines use the calling statement's snapshot, fitting the one-statement
  candidate/admission/grant query; it does not make authority valid indefinitely.
  [CREATE FUNCTION](https://www.postgresql.org/docs/current/sql-createfunction.html),
  [volatility](https://www.postgresql.org/docs/current/xfunc-volatility.html).
- session_user preserves authenticated login across SET ROLE/definer execution.
  A non-superuser initial login cannot impersonate a different session user.
  Dedicated operator login/mapping plus denied role assumption therefore supports
  executor binding. Pool reuse still needs the stated actual-login/context-reset
  tests; a shared privileged connector with SET ROLE would not prove this design.
  [SET SESSION AUTHORIZATION](https://www.postgresql.org/docs/current/sql-set-session-authorization.html).

## Source reality and proposed transition

Repository Access migration 0001_initial.py really has org-scoped text-ID grants,
three PtS permission literals, forced RLS and runtime SELECT. identity_bridge.sql
really grants only org id/deletion and member user/org/deletion columns with the
old actor-GUC-as-account policy. Neither implements the new account/actor/membership
projections, target pool or registry model. The contract labels these extensions and
owner CLIs as planned, and correctly requires coordinated consumer/adoption evidence.

Platform multitenancy source really has unique(org_id,user_id) and CASCADE
org/profile/member-role relationships. Rejoin with a fresh ID and retained history
therefore requires the documented structural/writer handover; it cannot be achieved
only by adding new HTTP models. Retire-only guards, predecessor expected state,
explicit grants and retained account ownership distinguish membership generations
without inventing employment or reviving old grants. Partial-index seed ON CONFLICT
compatibility is explicitly called out for characterization.

Legacy public.get_user_roles source is a SECURITY DEFINER helper using JWT member_id
and search_path public,identity; it grants authenticated execution without a PUBLIC
revoke. PostgreSQL's default function EXECUTE explains the source-level concern.
platform/deployment/PRODUCTION_STATUS.md:468 separately records the 2026-09-29
PUBLIC revoke with authenticated/service_role preserved. The substrate correctly
preserves that documented difference as an adoption input and does not claim current
live ACLs from old migration text. No verified current-production exploit or clean
target equivalence is inferred here.

The planned physical owner histories/privileges align with the repository ownership
inventory. New Access external Identity IDs are not cross-owner FKs; Identity-owned
local account-kind/actor references and retained membership history stay local.
The single-statement scoped projection boundary is an owner-controlled database
integration contract for Access, not permission for KDG to read Identity tables.
Filtering effective create eligibility before public pagination prevents a misleading
short page caused by raw candidate truncation.

No frontend/tool selection changes here: newest-stable TS7.0.2 and the reviewed
Node/Python scaffold baseline remain binding. Actual DDL/ACL/pool/RLS/adoption proof
belongs to authorized delivery. This review does not imply runtime readiness PASS.

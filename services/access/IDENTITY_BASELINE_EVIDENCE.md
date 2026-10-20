# ID-A bounded Identity baseline evidence

2026-10-20; baseline d0c543dddabb7aa9537d097a2335149fc8ddd1e9.
Separate Identity history and explicit source handover are delivered under the existing
Access maintainer. This qualifies the selected synthetic owner profile; production
owner transfer, protected-column hardening, actors/membership redesign, Access v2,
password/provider sign-in and full scaffold/KDG readiness remain separate work.

## Requirement to executed test

| Requirement | Executed evidence |
| --- | --- |
| Separate owner history; exact sources | Owner tests; actual identity_migrator LOGIN clean upgrade to identity_0001; repeat unchanged; Access history untouched |
| Trusted equivalent adoption | Independently executed clean/legacy source cases; pinned compact catalog fingerprints; actual adoption/repeat preserve all Identity row hashes, original Supabase ledger and finance/CS FK values/definitions |
| Unknown state refusal | Actual ACL, trigger, schema owner, default privilege, history and column mismatch cases refuse without changing their catalog/data; source/reference tamper unit tests |
| One source authority | Legacy composition discovers 15 migrations; owned discovers 9, excluding exactly six Identity DDL files; both preserve two seeds and five function directories; duplicate no-clean output refuses |
| Dependency order/failure safety | PtS release regression and actual coordinator failure: Identity failed, Access/Content/PtS not attempted, activation_allowed false, target unchanged |
| Competing migration safety | Actual held owner advisory lock refuses second migration; release then repeat leaves data unchanged |
| Restricted current projection | Actual access_runtime LOGIN sees only selected organization/account; protected reads/writes deny; reused connection without local context returns no rows |
| Native Auth integration | Actual native migration; supported Auth admin API creates synthetic account/profile; actual supabase_auth_admin LOGIN invokes retained token hook; no person/employment required |
| Source compatibility limits | PUBLIC helper execution retained but no Auth INSERT; actual authenticated UPDATE-only self admin-field path succeeds under legacy RLS then rolls back; no hardening/readiness claim |
| No destructive recovery | CLI stamp/downgrade refuse; original histories, source files, prior proof frames and Docker resources retained |

## Exact artifacts and commands

All private artifacts are under
`platform/deployment/.local/identity-baseline/qualification-im60qj1l/`.
`run.json` records fresh native run 99b7231c-0a5b-4bdb-98e8-3329564c526a.
Native wrapper prepare/up/verify pass with CLI2.120.0. PostgreSQL major17 is observed.
No historical project or database is adopted by this verification.

- `owner-env-djguxc78/owner-environment.json`: pinned uv0.13.1 resolves/checks the
  owner lock; frozen wheel-only fetch and separate fresh offline installation pass.
  Python3.15.0, SQLAlchemy2.1.4, Alembic1.20.0, Psycopg3.3.6 and pytest9.1.1.
  Initial offline resolution lacked Windows tzdata metadata; a subsequent frozen
  install lacked pluggy1.7.0. Those failed attempts remain, followed by explicit
  public metadata/wheel fetch and successful frozen offline install. No builds.
- `second-cases/focused-checks.json` and logs: owner/release pytest and both composer
  check-only commands; exact argv, exit codes and log hashes recorded. Unit checks
  are distinct from actual database qualification.
- `second-cases/identity-qualification.json`: actual restricted migration argv,
  modes, exit codes, expected refusals and log hashes. The owner test script
  `tests/qualify_identity_baseline.py --record-reference` then `--verify` runs against
  explicit prepared synthetic mappings via IDENTITY_QUALIFICATION_DIR. Credentials
  stay in mode600 fixture files, never argv or report payloads. Every DB/API URL is
  checked against the selected local run and ports before network calls.
- The native Auth bootstrap uses the actual schema owner supabase_admin for auth
  USAGE and table owner supabase_auth_admin for SELECT(id)/REFERENCES(id)/TRIGGER.
  `native-auth-bootstrap.json` verifies those privileges and absence of Auth INSERT.
  An ordinary postgres GRANT warning was insufficient; actual privilege checks caught it.
- Native Auth admin creation/profile and direct hook invocation pass. Earlier token
  attempts returned422 email_provider_disabled because the selected fixture disables
  that provider. Provider settings stay unchanged. Password sign-in and enabling the
  hook in the vendor JWT pipeline are not claimed by ID-A.
- `scripts/coordinator_failure.py` executes the existing real coordinator against a
  known synthetic mismatch; its exclusive evidence JSON records exact failed/not-attempted
  owners and false activation. `scripts/lock_and_legacy_characterization_v2.py`
  records the real lock/retry and rolled-back legacy self-update. Its earlier
  WHERE/RETURNING probe required SELECT and failed; UPDATE-only characterization
  exposes the retained broad UPDATE path. No account changes persist from that probe.

## Reference provenance and preserved failures

Six immutable platform sources plus the existing Access bridge have exact pins.
Their transaction wrappers and redundant schema-create statement are omitted only
in the owned loader; source files remain unchanged. The schema is separately
provisioned and the migration login has no database CREATE privilege.

The first clean attempt exposed the redundant CREATE SCHEMA requirement and rolled
back completely. An always-rolled-back source probe identified SQLSTATE42501. The
legacy consumer probe then exposed missing REFERENCES authority; the owned revision
grants schema USAGE and REFERENCES(id) to the legacy postgres bootstrap. Review additionally restored the precise seed column privileges described below.
Fresh second cases prove both changes without modifying the initial proof databases.

A first full catalog fixture was observed empty despite a generation receipt. Read-only
recapture matched its recorded digest8655aaf7880986c79a57fd1c383bd2434addb25f95bed863c82b3cbd26b9819b;
the observation and restored bytes are preserved. The cause was not established.
The final fixture uses category fingerprints/row counts to avoid duplicated definitions:
The pre-review fixture was 6387 bytes, SHA2560ec607fca1bfffb3d155926fbaf0de577c72c9f729f476f0b7d881caf52f0ba3,
derived independently from fresh trusted clean/legacy source executions. Writes are
atomic and checked. Adoption never approves a target against its own exported catalog.

Exact-owner equivalence is intentional. A postgres-owned live schema or production's
documented PUBLIC role-helper revocation is a mismatch requiring separate reviewed
owner disposition; neither is silently repaired or replayed. Native owner setup is
synthetic only. No live account/provider/access changes or deployment occurred.

## Impact decisions

Scaffold: owner-local migration recipe remains unpromoted; no second generator.
Shared UI: none. Agent context: existing rules suffice. Documentation: owner runbook,
this evidence, mutable ownership inventory and KDG navigation. ADR: existing0016/0017/
0020 and Identity decisions apply; accepted ADRs unchanged. No generic runner or service.

## Review corrections and final verification

All three BMAD review layers completed; all 14 findings have individual dispositions
in the build triage. No implementation was deferred. Uncommon additional rewrite-rule
verification and global DDL locking were rejected to keep this bounded foundation lean.
An actual rolled-back ALTER confirms PostgreSQL forbids detaching these GENERATED
identity sequences (SQLSTATE0A000), refuting the sequence finding.

The migration now checks exact head/private table and column ACLs, original history
and the trusted owned catalog before commit. Clean elevated runtime, upgrade base,
column ledger grant and unknown original history on retry refuse. Actual failure when
installing the Auth trigger after the first source has written tables/types/seed tuples
rolls back completely; restoring its narrow TRIGGER privilege allows a clean retry.
Partial, misnamed and unknown original Supabase ledgers and conflicting clean history
refuse without changing their data/catalog/history.

Review fixtures and journal are in `review-cases/`; previous database frames remain.
The fixture recorder now executes known pinned sources plus the revision's fixed
integration in an always-rolled-back transaction, records the trusted catalog and
then executes the real clean migration. No migration bypass is introduced. The final
reference SHA256 is ae183b435b2659efbe1a9f2ffdf3eaf1b8d64b2f9256ea72927b6f78453beb00.
Legacy fingerprint categories remain unchanged. Owned changes are only the precise
postgres column grants needed for retained synthetic Identity seeds, with no DELETE,
Auth INSERT or owner membership. Actual nine composed sources and both retained seeds
execute; the seeded target then passes exact owned retry. A minimal external
storage.buckets fixture supports the scratch composition test; this is not vendor
Storage runtime qualification. Actual Auth-role populated claims include active
membership/role and exclude deleted memberships/roles. Native API/profile evidence
above remains applicable to unchanged Auth source; it is distinct from the new scratch
migration and populated-hook proofs. No provider sign-in is claimed.

Exact focused executions use the same fresh owner Python and private validated mappings:
`tests/qualify_identity_baseline.py --record-reference`; the retained
`scripts/run_review_regressions.py` calls the database matrix without repeating native
Auth setup, followed by review regressions. Continuation scripts complete the remaining
cases after a fixture-only multi-statement binding error (42601) and missing external
Storage fixture (42P01); both observations and earlier successful steps are retained.
The committed `--review-regressions` route runs the complete review cases on fresh
prepared mappings. No fixture error is treated as a product success.

Final focused pytest (23 passed) and both composer checks pass. Their exact commands
and hashes are in review-cases/focused-checks.json. The existing focused-check runner
accidentally reused four second-cases output paths; the earlier 16-test result remains
in the session record, but its exact old log/receipt bytes were not recovered. Current
bytes were copied to review-cases and receipt-overwrite-observation.json records the
limitation; database journals, failed command logs and prior reference backups remain.

Final source/preservation audit and normal retained-data stop
are recorded with their exact commands and hashes under review-cases. Public generation,
Auth/Access and KDG remain gated.

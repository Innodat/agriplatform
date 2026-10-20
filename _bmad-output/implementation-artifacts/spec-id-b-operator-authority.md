---
title: Protected Identity operator authority foundation
type: feature
created: '2026-10-20'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 85b26f38dd66b5f1ac96854f82402c93f4a58700
context:
  - /home/ck/repos/innodat/agriplatform/AGENTS.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/identity-access-execution-substrate.md
  - /home/ck/repos/innodat/agriplatform/platform/docs/architecture/contracts/owned-write-and-secret-execution.md
---

<frozen-after-approval reason="standing bounded implementation approval">

## Intent

Identity needs the protected database identity/authority foundation before setup commands
can safely write or retrieve outcomes. Deliver its selected authority records and a fixed
private authorization read, integrated through the existing migration/qualification owner.

## Boundaries & Constraints

Always preserve original sources, revisions1–4, trusted references/pins, locks, prior
receipts, concurrent documents and Docker resources. No dependencies or provider/accounts/
real-data changes. Root alone controls actual synthetic preparation and execution.
Never implement command effects, outcomes/events, CLI/target preparation, membership
hardening, Access/WRITE/KDG/Leave or a generic administration engine in this increment.
Input parsing remains unchanged. Authority selection is not successful provisioning.

Add identity_0005 via the existing Identity chain. Add selected `operator_principals`
and `operator_authorities` with exact columns, attribution, scope/nullability, revisions,
NULLS NOT DISTINCT tuple uniqueness and local non-cascading actor FKs from the substrate.
Only controlled migrator/bootstrap writes; ordinary/operator roles cannot raw read/write
or alter mappings. No new implicit actors, principals or grants seeded by migration.
Use safe revision guards/server timestamps for controlled edits; immutable tuple identities
must not silently change. Deployment change/recovery evidence remains controlled, not an
ordinary configuration API. Existing actor/membership behavior stays unchanged.

Prepare `identity_operator` LOGIN NOINHERIT and `identity_operator_authority_owner` NOLOGIN
NOINHERIT separately; both restricted NOSUPERUSER/NOCREATEDB/NOCREATEROLE/NOREPLICATION/
NOBYPASSRLS. Migrator has sole SET-only, non-admin membership in definer role; operator
cannot assume it. Empty/unsafe roles or unexpected effective privileges refuse migration.
Use existing preparation/verification patterns, not another lifecycle tool.

New internal `identity.current_operator_authority(command_type text, scope_kind text,
org_id uuid, target_account_id uuid)` returns executor_actor_id UUID,
principal_revision bigint, authority_id UUID, authority_revision bigint, or no row.
Supported literals are actor.register_system/account_actor.ensure (platform, latter
requires target account), membership.join/membership.retire/membership.join_owner
(organization, requires org/account). Reject nil/missing/mixed target/scope or unsupported
command. Registration has null target; account ensure exact target; no application scope.
Derive executor solely from original session_user and enabled protected principal mapping.
Match enabled exact command/scope/org, null application_id, and target either explicitly
all (null authority target) or exact requested account. Platform never implies organization
or another command. For overlapping valid rows choose authority UUID order deterministically.
Join_owner is a separate authority, never implied by ordinary join or payload flags;
future execution must check both when requested. No GUC/SET ROLE/payload chooses executor.
Return only own matching metadata, not a map listing or actor display/business content.

Use STABLE SECURITY DEFINER, fixed pg_catalog,pg_temp search_path, fully qualified objects,
no dynamic SQL/waits/writes. Revoke all inherited/default function/table privileges before
exact grants. Only identity_operator may invoke it; definer has narrow local SELECT only,
no DDL/DML/role authority. Recheck current enabled mappings on every invocation, including
a pooled connection after committed revocation. Later command/outcome wrappers must
repeat these checks inside their short transaction; this read creates no durable authority.

## I/O & Edge-Case Matrix

| Scenario | Expected |
| --- | --- |
| Actual restricted operator LOGIN, exact/wildcard target | Exact executor and current principal/authority revisions |
| Command/platform/org/target mismatch, invalid/nil/missing context | No row; no effects or existence disclosure |
| Unmapped/disabled principal or disabled authority; re-enabled fresh call | Denied immediately / current metadata only |
| Ordinary join without join_owner; independent owner row | Owner authority absent / explicitly present only |
| Spoofed GUC/JWT/SET ROLE/temp objects/search_path | Original authenticated login remains sole identity |
| Runtime/browser/service roles; operator raw maps/actor DML/DDL/role assumption | Permission denied, no state change |
| Structural invalid/duplicate/FK/revision and controlled no-op/change | Constraints enforce selected shape and server revision |
| Clean/adopt/exact prior head4 upgrade, repeat, drift and injected failure | Preserve old rows/sources; refuse unsafe state; atomic rollback |

</frozen-after-approval>

## Code Map

- `services/access/identity-migrations/identity_baseline.py`, `env.py`, revisions1–4 — reuse fixed source/canonical catalog verification; original references stay immutable.
- `services/access/tests/qualify_identity_baseline.py` — extend independent rollback-only recorder for a new authority-reference.json; capture sources before execution/publication, no automatic trusted pin.
- `services/access/tests/qualify_current_account_organization.py` — reuse qualified frames, login and previous-source patterns.
- `services/access/tools/prepare_identity_projection_role.sql` — preparation pattern; add separate owner-specific preparation SQL.
- `platform/deployment/.local/identity-baseline/operator-authority-pq17_n02/` — root-owned private proof/frame, all historical frames retained.

## Tasks & Acceptance

- [x] Owner revision/helper/new reference recorder and focused tests: observe RED before code.
- [x] Actual qualifier and preparation SQL: cover every matrix row without a new runner.
- [x] Owner runbook and root evidence/navigation: requirement/test and five impact decisions.
- [x] Root actual restricted-role/upgrade/failure checks, affected tests, review and scoped commit.

Given a verified synthetic target, when authorized scoped operator login calls the routine,
then only current matching metadata is returned. Given any forbidden authority, when read
or alternate write is attempted, then it denies and preserves state. Given old owned state,
when migrated or refused, then original rows/reference evidence are preserved atomically.

## Implementation Notes

Implementation agent owns services/access migration/helper/recorder, new qualifier/tests,
preparation SQL and IDENTITY-MIGRATIONS.md; root owns spec/evidence/navigation, actual frame,
trusted reference publication/pin and commit. Agent must not run Docker/actual DB, install,
spawn agents or commit. Report exact root execution/recording prerequisites when ready.

Root qualification: actual RED42883 on prior head4, independently executed/published
rollback-only authority reference and manually pinned2f378cf2e9641bf60a84be4efda88c395a951c1032499d68c13fee878c13a81e.
The initial nonsuperuser preparer produced forbidden creator memberships; verifier refused.
Only new synthetic memberships corrected through actual controlled admin. Preparation now
refuses nonsuperuser before CREATE; actual rollback-only success/refusal tests pass.
Initial structural test's23514 expectation was masked by PostgreSQL FK precheck0A000;
now both FK and retention-trigger refusals are verified separately, preserving expectations.
Full fresh final frame operator-authority-final-gjsnxmdn passes actual login/structural/
clean-adopt/prior-head4/repeat/unsafe/drift/rollback matrix. All272 affected tests and both
composition checks pass. Original2581 files have only eight intended existing changes.
All matrix rows map to executed checks in OPERATOR_AUTHORITY_EVIDENCE.md; no skipped rows.

Review corrections strengthened effective privilege checks, loaded-helper custody,
private publication, complete target validation, cross-principal/metadata/default-ACL
proof and PG17-only qualification wording. Updated recorder was replayed through an
ignored owner copy; generated reference remained byte-identical without touching the
repository reference/pin. Actual predicate evaluation42809 was corrected by CASE guarding
the sequence privilege call. Fresh reviewed frame operator-authority-reviewed-p954m9yk
passes24 named actual stages;286 affected tests and both composers pass. Native project
normally stopped with data retained; no cleanup/reset. No new or deferred scope.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence / route |
| --- | --- | --- |
| Blind1 external definer EXECUTE | medium | Actual rollback-only probe confirms PUBLIC executable definer outside Identity passes role checker. Patch explicit rejection; retain only already-canonically-verified legacy get_user_roles() compatibility and document it. |
| Blind2 external sequence writes | medium | Actual PUBLIC USAGE/UPDATE sequence probe passes checker. Patch non-system sequence write privilege refusal. |
| Blind3 imported helper/source capture mismatch | medium | Recorder captures disk helper while using an already imported object; import-time identity not checked. Patch loaded-helper digest check and stale-import regression. |
| Blind4 temporary file permissions | low | open(xb) honors umask, not fixed0600. Patch exclusive os.open mode and permission assertion. |
| Blind5 operator URL group partial validation | low | Only clean operator_engine call validates URLs, while docs promise each. Patch required-group validation before any writes. |
| Blind6 cross-principal fixture absent | medium | Actual proof has only one protected principal. Patch lower-ID competing principal and other-login-only permission denial. |
| Blind7 inserted server metadata unproved | medium | Successful fixtures omit spoofed metadata. Patch rollback-only insert and changed-update timestamp/updater assertions. |
| Blind8 default named ACL removal unproved | medium | Legacy source already seeds named service_role/authenticated table defaults; actual tests lack their new-map effective DML denial. Patch effective new-map privileges for all forbidden roles. Unknown extra defaults already refuse canonical preflight. |
| Blind9 actual PUBLIC/dependency refusal gaps | medium | Real role tests cover flags/memberships, mocks alone cover effective PUBLIC grants/staged dependencies. Patch actual unsafe PUBLIC read/write and direct staged-dependency cases alongside definer/sequence probes. |
| Blind10 PG15 qualification clarity | low | Runbook describes compatibility branch but runtime evidence is PG17 only. Patch explicit qualification limit; do not claim PG15/16 execution proof. |
| Edge1 sequence grant gap | medium | Same actual reproduced state as Blind2; patch together. |
| Gap1 controlled insert metadata gap | medium | Preverified missing forged insert tests, same cause as Blind7; patch together. |
| Root replay sequence predicate order | medium | Actual42809 on a nonsequence showed planner could evaluate privilege function before relkind filter. Direct CASE correction; independent replay and full actual matrix now pass. |

All entries grouped into direct implementation/test/doc patches and were resolved. No
new public API, product-intent gap or deferred work. Root retains confirmed privilege
RED probes and all prior receipts. Final286-test/full actual verification covers patches.


## Verification

Canonical Python is platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python. Use PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 and
-I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider.
Root uses existing native dev wrapper, fresh synthetic databases and actual qualifier;
then both composer --check-only routes, source-bound logs and protected-file audit.

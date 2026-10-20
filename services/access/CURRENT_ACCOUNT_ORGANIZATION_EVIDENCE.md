# ID-B selected-organization membership evidence

2026-10-20; baseline 18c5b94566045dcca9973ce3365ea1af95e6287d.
This increment adds the internal current-account organization lookup and its minimal
server-maintained membership revision through the existing Identity owner. It does
not complete ID-B lifecycle, provisioning, Access adoption or application admission.

## Requirements and executed coverage

| Requirement | Covering verification |
| --- | --- |
| Current selected identity | Actual access_runtime LOGIN returns exact account/org/member/revision/account-actor tuple; distinct account/actor IDs; no person/employment dependency |
| Nullable setup state | Active unmapped account returns current membership and null internal actor, with no provisioning or read writes |
| Missing/ineligible context | Missing/malformed/nil account/org, wrong/setup context, other account/org, deleted profile/member/org all return no row; deleted org has a real membership fixture |
| Isolation | Spoofed actor and legacy service_role JWT claim cannot change account selection; direct dedicated reader sees only current member/org |
| Revision integrity | Old rows start at 1; insert ignores supplied revision; every persisted nonrevision field change advances once; identical/revision-only updates hold; exhausted revision refuses SQLSTATE 23514 and rolls back |
| Existing writers/hooks | Actual seed_org_member function configuration characterized with fake client; matching SQL ON CONFLICT/unretire keeps ID and revisions; existing scoped Access queries, Auth profile hook and Auth-admin LOGIN token-hook remain supported |
| Restricted privileges | Runtime cannot raw-read expanded columns/write/SET ROLE/replace routine; PUBLIC/browser/service roles lack new function EXECUTE; hostile temp/search_path cannot forge result |
| Pool reuse | Same physical connection clears transaction-local context after commit, explicit rollback and statement-error rollback |
| Safe migration | Clean, equivalent adoption, exact committed head3 upgrade and current repeat; external FKs/old row fields retained; unsafe role/catalog/unknown history refuse; injected mid-write failure rolls back full catalog/rows/history |
| Trusted source | Additional rollback-only known-source fixture, captured-source checks, exclusive publication and manual pin; prior references/revisions/pins/lock preserved |

## Commands and artifacts

Canonical OWNER_PYTHON:
`platform/deployment/.local/identity-baseline/qualification-im60qj1l/owner-env-djguxc78/offline-venv/bin/python`.
Existing frozen lock retains Python 3.15.0, uv 0.13.1, SQLAlchemy 2.1.4, Alembic 1.20.0,
Psycopg 3.3.6 and pytest 9.1.1. App/compiler TypeScript 7.0.2 is unchanged.
Ordinary native Supabase CLI run 99b7231c-0a5b-4bdb-98e8-3329564c526a is reused;
all old databases, credentials/receipts and resource state are retained. New private
frame URLs pass existing run/namespace/loopback/port guards. Secrets remain private
fixture inputs, never argv/evidence. No new dependency installation or lifecycle runner.

- Actual acceptance RED before implementation: access_runtime LOGIN receives SQLSTATE 42883
  for missing identity.current_account_organization(), no writes. Retained under
  `platform/deployment/.local/identity-baseline/current-organization-t3mdjqiv/`.
- `OWNER_PYTHON -I -B services/access/tests/qualify_identity_baseline.py --record-organization-reference`
  independently executes the four exact migration sources with prior catalog checks,
  rolls back, rechecks empty eligibility and publishes only the new fixed fixture.
  Captured helper/pins/revisions/prior reference hashes are reconciled before an explicit
  one-line source pin. Generated organization reference SHA256:
  5eeed70cf624fc548e9fcbbe13f0adfb83d7e00081def9e71b69e644afd2e6ae.
- `OWNER_PYTHON -I -B services/access/tests/qualify_current_account_organization.py`
  executes actual restricted-login/current-context, revision and upgrade/failure matrices.
  Exact prior owner source is checked against baseline Git objects, exact nine-file set,
  launcher/interpreter, execution log hashes and actual head3 before upgrade.
- `OWNER_PYTHON -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider`
  with PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 covers owner/provenance/recorder/seed/composition/
  coordinator regressions. Root final results and source-bound receipts follow.
- `OWNER_PYTHON tools/py/run_compose_supabase.py --check-only` and
  `OWNER_PYTHON tools/py/run_compose_supabase.py --identity-authority owned --check-only`
  retain both composition routes.

The initial two frames retain failed previous-upgrade receipts. The exact catalog guard
correctly rejected test FK setup revoking original bridge grants, then a grant-only
replay restoring them in different ACL order. The fixture must preserve the original
schema/column grants rather than weaken catalog comparison. No old hook was replaced;
original integration SQL contains only GRANT statements. The original head3-as-final
unit expectation was also updated explicitly: head3 remains a verified prior catalog,
while head4 is now required to finish the route. No unexplained result was suppressed.

## Limits and impacts

Existing UNIQUE(org_id,user_id), CASCADEs, supported direct writers and unretire behavior
remain compatible. This revision is freshness evidence for the retained row, not delivery
of immutable membership IDs/new-ID rejoin or retained lifecycle history. FORCE RLS,
protected actor attribution, operator binding/outcomes, target projections, current
Access integration and server KDG remain later gates. The new nonowner reader obeys
RLS; no ordinary runtime raw authority is added. The Access API's legacy actor setting
still means Auth account. GUCs remain verified backend assertions, not authentication
against compromised DB credentials. Hook execution does not qualify the vendor JWT or
provider sign-in pipeline. Operational target qualification is PostgreSQL 17 only.

Scaffold: existing owner-local migration/query/reference pattern, unpromoted; no new
generator/service. Shared UI: none. Agent context: existing instructions suffice.
Documentation: owner runbook, this evidence, mutable inventory and KDG handoff.
ADR: existing ADRs 0018/0020/0056 and selected substrate suffice; accepted decisions unchanged.
No production migration, real account/access/provider changes, deployment or pilot.


## Completed pre-review verification

Fresh complete frame:
`platform/deployment/.local/identity-baseline/organization-final-w4snwcju/`.
One full execution passes every requirement row above, with no continuation. Its
complete-execution.json captures exact argv/environment, source hashes before execution,
unchanged-source reconciliation afterward, result and log digest. The cumulative
identity-qualification.json records exact migration commands/results/refusal codes.
The prior source/execution receipts identify exact committed head3 on three fresh cases.
All old membership fields and external FK definitions/values survive, with revision 1
as the sole additive row field; actual Access queries and Auth profile inserts still work.
Actual supabase_auth_admin LOGIN token-hook output preserves current member/roles and
custom/sub claims. No vendor sign-in pipeline is claimed.

Focused ACL preservation characterization first observed RED: 1 failure/1 pass against
the original helper, then GREEN: 2 passes after retaining original direct owner grants. The
complete actual matrix validates restoration against real PostgreSQL catalog ACLs;
no expected catalog fingerprint was relaxed. Initial frames remain at
current-organization-t3mdjqiv and organization-complete-8cqk5_6u under the same parent.
A scratch namespace collision guard also refused before creating any database; the
fresh namespace was corrected without touching the existing database.

Final affected pytest run: **111 passed**, with both composer check-only commands PASS.
Exact commands/results/log hashes are exclusively retained in focused-checks.json of
the fresh complete frame. All matrix rows have passing executed coverage. Initial unit
head-boundary failures and fixture failures remain evidence, alongside successful proof.
Review, final preservation and normal retained-data stop results follow.


## Reviewed completion

All three BMAD review layers completed. Twelve findings received individual triage;
nine patch groups were applied (the duplicate fixture-cleanup finding shares its fix),
two disproportionate low-risk expansions were rejected, and no implementation deferred.
The policy documentation now states each table's local predicates separately from the
routine's full current-profile/org/member join. No migration/policy/reference bytes
changed during review. Original fixed references remain immutable.

The fresh reviewed complete frame is
`platform/deployment/.local/identity-baseline/organization-reviewed-final-u8insh8h/`.
One full source-stable run passes all previous cases and new assertions:

- A committed membership change returns an advanced revision through actual
  access_runtime LOGIN; a committed no-op/forged revision leaves that result unchanged.
- Two real connections contend on the same member. The losing writer is observed
  blocked, both changes commit, and the final revision increases by two.
- Actual postgres LOGIN executes default/forged insert and changed/no-op/forged update
  cases with existing authority only. Its observed owner membership is true and owner
  inheritance false; no inheritance assumption is required. This is the privileged
  retained SQL-seed principal, not service_role or a PostgREST endpoint qualification.
- A statement including an exhausted and eligible member fails atomically, retaining
  both rows/versions. New fixture failure tests restore temporary direct grants in
  finally after CREATE/INSERT failure; only the additive member revision is normalized
  in the older actor qualifier's historical upgrade comparisons, with all other row
  fields and full default/failure snapshots still protected.
- The new reference's own missing/corrupt/wrong-pin cases refuse. Additional focused
  fixture/normalization RED observed three failures/four passes, then seven passes;
  the two relevant provenance test files pass 54 tests.

The first review-expanded run's seed principal assumption failure and its read-only
metadata probe remain retained in organization-reviewed-3bv6yczv. Its isolated corrected
seed method passes before the complete fresh repeat; no privilege was broadened.
Final **119 affected tests** and both composer check-only commands pass in the reviewed
frame's focused-checks.json. Complete-execution.json binds actual invocation, result,
log and unchanged implementation source identities. All requirement matrix rows above
have passing executed coverage. Final preservation/lifecycle audit follows.

Final preservation audit checks all 2571 prior files: only 8 intended
existing files changed; all 2563 others, including concurrent documents, remain
byte-identical. Revisions 1–3, all three prior references, source pins, owner lock, Access
runtime/bridge and actual seed source match baseline exactly. Normal Supabase stop passes;
the retained volume/owned bridge/configuration are verified separately, with no active
project containers. No reset, volume removal or explicit cleanup. Exact receipts are
preservation.json, native-stop.json and resource-retention.json in the reviewed frame.

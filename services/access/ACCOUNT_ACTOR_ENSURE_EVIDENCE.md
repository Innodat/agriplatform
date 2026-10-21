# Protected account actor setup —2026-10-21

Identity revision18 implements the accepted `account_actor.ensure` command. This is
synthetic local delivery evidence, not production or consumer activation. The existing
ACCESS-A/B membership-binding gate remains. Enclosing Build review, root regression/composition checks and preservation verification
are complete; the local project is normally stopped with data/receipts retained.

## Enclosing verification and review

Root independently ran the affected Access/PtS release suite: **1012 passed in38.63s**
(`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`, frozen Python `-I -B -m pytest services/access/tests
apps/pts/tests/test_release.py -q -p no:cacheprovider`). Both composition checks passed:
`tools/py/run_compose_supabase.py --check-only` and the owned `--identity-authority owned
--no-seeds --check-only` lane. Final `--verify-retained` passed, and independent public CLI
replay/scoped recovery returned the existing final receipt without a new operation.
`root-cli-replay-recovery.json` records that proof.143 captured executable sources match
current bytes; all35 historical migration/reference/source-pin files remain unchanged.

Three independent review lenses completed; all10 surviving finding rows were patched,
including boundary/error classification and behavioral evidence. Two low proposals for
additional cross-owner reservation/profile locks were rejected under the declared bounded
observation contract; no access is granted by mapping. The new hardcoded fixture dependency
was removed. General existing owner-bootstrap portability is deferred in the Build tracker;
portable CI provisioning is not asserted. An additional root check closed operator URL
validation before any connection. `git diff --check` passed. Normal pinned-CLI stop
completed for run99b7231c-0a5b-4bdb-98e8-3329564c526a, retaining data, receipts and prior
frames. Concurrent unrelated work stays outside the scoped local commit; no push.

## Reviewed aggregate acceptance

The reviewed revision18 reference is
`9502c7183ed38c6f81a3de6f578e04e6feb81059c56fdbbc44045b6f6054eb50`.
Only18 was regenerated through the independent rollback-only source recorder;1–17
and all earlier proof/source files remain. The reviewed fresh proof frame is
`platform/deployment/.local/identity-baseline/account-ensure-j9ial0p1`.

Before qualification, the existing root bootstrap must prepare fresh synthetic case
URLs/roles/Auth prerequisites and the existing protected CLI target. Its private
`credentials.json` must explicitly supply `cli_owner_fixture_path`: an absolute path
to a protected mode0600 JSON file in a private owner-controlled directory. The closed
shape is `{owner_url,run_id,database}`. The reader verifies exact target run/database,
postgresql scheme,127.0.0.1 host, selected port/database, identity_migrator login and no
query/fragment. No historical private frame is discovered by the qualifier. Main also
validates all operator/core URL groups before any connection and permits alternate
invocation only through the explicitly validated existing runtime URL. General bootstrap
portability predates this patch and remains deferred; no provisioning framework was added.

Actual aggregate command (repository root):

```sh
IDENTITY_QUALIFICATION_DIR=/home/ck/repos/innodat/agriplatform/platform/deployment/.local/identity-baseline/account-ensure-j9ial0p1 platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python services/access/tests/qualify_account_actor_ensure.py --all
```

Exit0;26 PASS labels in `review-all.log`, ending `ensure-all-acceptance-stages PASS`.
One unchanged-source capture covers all dependency-ordered stages. Existing stage flags
remain available. `--all` is single-use on fresh prepared cases; use `--verify-retained`
for subsequent read-only inspection. The aggregate includes the original matrix,
boundaries, review proofs, alternate executor, physical lifecycle, response-loss/migration
recovery, retained commands, exact evidence closure, CLI, populated repeat and retained
verification in that order.

Review-specific actual proofs passed:

- Disabled Auth RLS refuses both staged and head verification inside rollback-only
  transactions bounded by5s statement/2s lock limits; the disabled state is not repaired.
- Replay held behind a witnessed retry lock for5.2s returns IC004, retaining its original
  receipt. Two temporary3s observation delays with a9s raw restricted-query bound prove
  the total observation starts before both reads and expires with IC004. Exact routine
  definitions/ACLs are restored; ordinary adapter deadlines remain unchanged.
- An unexpected inherited authenticated membership plus its restrictive Auth policy
  refuses as unavailable before Auth/profile reads. Membership/policy cleanup restores
  the exact verifier catalog; no new role or login was created.
- Existing access_runtime acts temporarily as a second protected executor for one exact
  account. Separate executor retry namespaces proceed independently; each executor's
  foreign operation lookup is unresolved. Temporary exact wrapper/schema ACLs are restored,
  principals/authority are disabled afterward, and immutable history remains.
- Physical deletion of an isolated account-only profile/Auth row retains actor, mapping,
  outcome and event bytes; a new account UUID cannot appropriate that actor. A soft-deleted
  foreign Auth UUID with no actor/map independently conflicts without partial effects.
- A known fresh command's stored SHA256 equals an independently serialized canonical
  command digest; new actor creation/update actor IDs/times match mapping, event and outcome.

Before the aggregate CLI stage, the exact previous candidate source/reference/catalog
was proved, then only the three changed routines were forward-replaced in the synthetic
CLI DB. `review-cli-forward-reconciliation/` retains old/new sources, complete bounded
maintenance SQL, executed script and before/after data digests. All existing CLI data,
receipts and history were unchanged; exact final catalog required. Unknown state was
never normalized and no database was reset or recreated.

Focused tests only: baseline/new qualifier files71 passed in0.35s; edited parent command
qualification file21 passed in0.42s. Root owns broader final regression/composition/review.

The bounded Auth UUID observation does not reserve Auth's future UUID namespace.
Profile checks after waits and in the mapping trigger do not promise commit-time liveness
against every overlapping retirement. No additional global reservation or profile row
lock/write privilege was added; current application access remains independently checked.

## Earlier candidate handoff (retained)

The following narrative preserves earlier candidate evidence. The reviewed reference,
aggregate and enclosing results above govern the delivered source.

## Implementation and preparation

The existing strict command/parser/JCS/target/worker transport remains the entry point.
The adapter and CLI now support typed account/actor receipts and recovery requiring
`--command account_actor.ensure --account-id <UUID>`. No additional credential or login
hook is introduced. Required `evidence_ref` records explicit human classification;
it never substitutes for live Auth verification.

Separate administrator preparation creates `identity_account_verification_owner` as
NOLOGIN/NOINHERIT/NOBYPASSRLS with only the exact SET-only migrator edge. The separate
Auth-owner SQL grants auth schema USAGE, SELECT(id,deleted_at), and the exact SELECT
policy. Revision18 adds selected profile reads under account-targeted authority, fixed
pinned-search-path verifiers, protected mapping writes and evidence guards. Preparation
is validated before historical comparisons, including early returns, without rewriting
references1–17. The initial handoff independently recorded reference was
`98bb572d298fec7ec6825d7f2928a6830eaee31aa16fef063b61b77c7fccc595`.

The live Auth and proposed-UUID observations occur before retry/business locks. They
support at most five seconds of this executing command; restarted execution rechecks.
After waits, local profile and protected authority are rechecked. An unexpected applicable
Auth RLS policy or missing/excess selected-column rights reports unavailable, never a
false account absence. The retained profile→Auth FK permits a fixed, exact-authorized
Auth-ID collision boolean without exposing a profile directory. Deleted Auth IDs are
included in collision checks. Auth banning remains Supabase authentication policy.

The permanent actor/mapping, immutable outcome and created event commit atomically.
Verified identical mappings produce unchanged outcomes without new events. Legacy
unbound adoption requires actor UUID=verified account UUID, account kind, null key and
matching label. Existing own legacy actors cannot be bypassed with another UUID.
Foreign bindings/UUIDs, changed labels/kinds and system/keyed profiles refuse. Historical
actors/maps remain; setup creates no person/employment/member/grant.

## Actual proof frames and commands

Frozen executable (abbreviated `$P` below):
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
Native server run: `99b7231c-0a5b-4bdb-98e8-3329564c526a`.
Initial handoff retained proof directory:
`platform/deployment/.local/identity-baseline/account-ensure-00zi4tlq`.
Earlier candidate frame `account-ensure-a1f6bk90`, incomplete network-only frame
`account-ensure-f3p2wui7`, prior owner stages and Docker resources are preserved.

1. RED: `$P -m pytest services/access/tests/test_identity_operator.py -k account_actor_ensure_dispatch -q`
   failed1 with `command_unsupported` before SQL. The accepted command was still disabled.
2. Focused GREEN: `$P -m pytest services/access/tests/test_identity_operator.py services/access/tests/test_operator_cli.py services/access/tests/test_identity_baseline.py -q`
   passed119, then131 after strict receipt/context/reference-drift additions.
3. The existing head17-current-head assertion was separately observed failing after18
   became current. It now preserves optional16/17 validation and requires18 for activation.
   `$P -m pytest services/access/tests/test_identity_operator.py services/access/tests/test_operator_cli.py services/access/tests/test_identity_baseline.py services/access/tests/test_membership_join_command.py -q`
   passed152 in1.13s.
4. Independent rollback-only recorder:
   `$P /tmp/record_account_reference.py`, equivalent to
   `IDENTITY_QUALIFICATION_DIR=<candidate-frame> $P services/access/tests/qualify_identity_baseline.py --record-account-actor-ensure-reference`.
   Verified every historical catalog1–17 before18 and verified rollback to empty staged
   preparation afterward. New reference candidates were retained privately before
   regenerating through the owning recorder; historical references were never regenerated.
5. Actual qualifier invocations used `$P /tmp/run_account_matrix.py [stage]`, a private
   wrapper setting only `IDENTITY_QUALIFICATION_DIR` and calling the checked-in entrypoint.
   The repository invocation is
   `IDENTITY_QUALIFICATION_DIR=<final-frame> $P services/access/tests/qualify_account_actor_ensure.py [stage]`.
   Initial no-argument execution passed clean/exact17/repeat, new/identical/conflict,
   legacy and ineligible/lifecycle cases, then stopped at a race witness limitation.
   The subsequent named stages below completed the remaining acceptance. No successful
   whole initial-run claim is made.

| Stage / retained log | Actual result and requirement coverage |
| --- | --- |
| initial / `final-matrix.log` | Clean18 and exact17→18 across previous/failure/unsafe cases; retained system actor/data preserved; repeat; live account, same operation replay/recovery, unchanged, changed-input/label/UUID refusals; legacy absent/existing UUID retention; foreign profile/arbitrary/system/service/keyed/own-legacy bypass refusals; unauthorized target; deleted Auth/profile, system/keyed profile, missing account and new-account actor reuse refusals. |
| `--remaining` / `final-remaining.log` | Same-operation identical/conflict races; distinct-operation absent-map same/different-actor races; witnessed advisory authority/business wait chain; busy only for retry lock, other lock unavailable; event failure rollback; raw write/read/owner-role/GUC denial; exact catalog and unknown/ACL drift refusal without normalization. PASS. |
| `--additional` / `final-additional.log` | Witnessed authority/profile revocation while retry lock waits; missing/excess Auth read rights and unexpected PUBLIC restrictive policy→unavailable; actual commit followed by lost acknowledgement, original scoped recovery/retry; injected migration DDL failure with sequence witness, rollback and explicit recovery; head18 register_system/join/retire execute/replay/recovery. PASS. |
| `--cli` / `final-cli.log` | Existing prepared target, real restricted worker; execute/replay/exact-account lookup/wrong-account denial. PASS. |
| `--closure` / `final-closure.log` | Physically missing profile; exact executor/server times/mapping/event evidence; immutable mapping update/delete/truncate refusals. PASS. |
| `--populated-repeat` / `final-populated-repeat.log` | Controlled upgrade repeated after populated mappings, legacy actors and outcomes; complete Identity data/catalog and Auth fixture digest unchanged. PASS. |
| `--verify-retained` | Exact head18 in all five delivered cases plus typed stored outcome/event checks. PASS. Repeatable read-only inspection; writes only a new proof artifact. |

Mutating stages are single-use on their prepared cases. Do not replay initial,
additional or closure stages against committed fixtures. Use `--verify-retained` for
repeat inspection. Each source-capture artifact records its own actual stage and exact
before/after hashes. Final custody includes owner migrations/references/helpers/locks,
all imported qualifier sources, both preparation SQL files, bootstrap.py, deployment
Python/JSON/schema/environment sources, platform SQL, composer/seeds and dev.SOURCES.
Earlier narrower captures and refused witnesses remain historical, not final proofs.

## Retained refusals and corrections

Initial socket-restricted bootstrap refused before DB access; socket-capable local
execution succeeded on a new frame. PostgreSQL automatically gave the new role's
creator an administrative edge. The true local administrator reconciled only this
new synthetic role to the exact migrator edge before recording/executing Identity;
the preparation source now creates it through the true-admin tool. Other roles stay.

Recorder iterations caught an incorrect new revision filename, missing SET ROLE for
a grant owned by the authority owner, ordinary PUBLIC schema USAGE in staged rights,
and the required mapping SELECT grant. Each refused transaction rolled back. The
new candidate reference was regenerated only through its source recorder.

The absent-map race initially reused an oracle requiring both workers to wait directly
on one held lock. Distinct operations serialize through protected authority first,
so the second worker waits behind the first. The new oracle proves the actual advisory
holder→worker→worker chain using pg_locks/pg_blocking_pids; restricted activity wait
fields were unsuitable. Expected race outcomes were unchanged.

The prepared synthetic CLI target had an earlier known candidate18. Before replacing
only its verifier function, the rehearsal reconstructed and hashed the exact previous
candidate source and compared its entire catalog to the retained candidate reference.
A first replacement refused for missing schema CREATE and rolled back. The bounded
retry temporarily granted CREATE inside the same owner transaction, replaced the one
fixed verifier, revoked CREATE, required the exact final18 catalog and compared every
Identity table/receipt/history digest unchanged. No reset/history rewrite/unknown-catalog
normalization occurred. `cli-known-candidate-reconciliation-*` retains old/new source,
maintenance SQL, before catalog and preservation evidence. `executed-*.py` and
`executed-preparation-sources.json` retain actual administrative script identities
without credential contents. The complete executed script includes the temporary
schema grant/revoke around the routine-only SQL file.

## Release, recovery and five impacts

Coordinate separate role/Auth preparation, controlled Identity upgrade, exact catalog
verification and CLI consumer activation. Migration failure blocks activation; preserve
receipts/history and use explicit forward recovery. An unavailable operation response
is not proof of rollback: lookup with the original account/operation under current
authority, then retry only the identical command. Recovery may return a historical
receipt after account deletion; that receipt never proves present eligibility. Do not
run migrations on worker/API startup, reverse applied migrations, or reset retained data.

- Scaffold/tooling: existing owner migration/verifier/reference/CLI fixtures extended;
  reusable restricted-role/Auth preparation SQL added. No generator or service framework.
- Shared UI: no product/shared-UI change.
- Agent context: KDG next-session handoff records actual command and remaining gates.
- Documentation: development runbook, owner contract, this evidence and existing spec.
- ADR: ADR-0056 implemented under existing contracts; no accepted ADR changed.

Those enclosing Build checks are now completed as recorded above; this earlier
handoff narrative remains for provenance. No broader runtime/PtS/Access/WRITE/KDG/Leave readiness, production action,
real account/provider provisioning, deployment or push is asserted.

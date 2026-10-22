# Existing Identity pre-grant target qualification — 2026-10-22

This item qualifies the existing `identity.organization_account_target(uuid,bigint)`
projection under Identity19/Access10. Identity7 already supplied the function and
`access_command_owner` EXECUTE privilege. No production code, migration, role, privilege,
credential or dependency changes are delivered. This is a consuming proof, not a new
verification service or an effective Access grant.

The projection checks an active organization/profile/membership and an account-kind
actor mapping. It returns the exact account, membership ID/revision, actor and display
name. It does not check live Auth, permission grants, employment or application admission.
Trusted transaction context is a backend assertion, not command authorization. A later
protected grant command must independently enforce authority, bounded fresh observation,
expected state, write coordination and atomic evidence.

## Requirement to test evidence

The new native qualifier is `tests/qualify_identity_pregrant_target.py`; the focused
harness tests are `tests/test_identity_pregrant_target.py`. The owner runbook is
[IDENTITY-PREGRANT-TARGET.md](IDENTITY-PREGRANT-TARGET.md).

Synthetic setup uses existing Identity operator account-ensure and membership join/
retire commands with explicit fixture authority. Read probes use actual Access owner,
command-owner, operator and runtime logins. No temporary production grant or replacement
function is installed. Full Identity and Access state/catalog snapshots establish read
side effects independently of RLS-filtered application reads.

## Delivery impacts and limits

Scaffold: reuse the existing owner fixture loader, migration/connection/snapshot and safe
failure tools; add only this bounded qualification. Private bootstrap portability remains
an existing follow-up, not a portable CI claim. Shared UI: none. Agent context: none.
Documentation: this evidence, owner runbook, mutable substrate/local-development and KDG
handoffs. ADR: existing ownership, short transaction, structural integrity, attribution,
release and safe logging decisions apply; accepted decisions remain unchanged.
Existing schema/client/generator/test/runbook owners retain their work. TypeScript7.0.2
and the approved dependency baseline remain unchanged.

All data is isolated synthetic local data. No real account/access change, production
migration, provisioning, deployment, pilot, Leave/editor implementation, reset/prune or
push is included. Existing historical frames, receipts, data and Docker resources remain
preserved; normal native lifecycle stop retains data. Concurrent working-tree documents
are excluded from the scoped commit and may continue evolving under their owners.

| Requirement | Executed proof |
| --- | --- |
| Supported actual Identity operator ensure/join; unmapped membership; zero grants/admission | `prepare_cases` |
| Exact five values, absent/empty setup account, UUID spelling, separate user caller, wrong/null/nil/invalid targets and contexts, all LOCAL settings/roles and actual pool return/reborrow | `read_matrix`, `read_cases`, `assert_local_reset` |
| Current profile/org soft deletion and restoration | `soft_deletions` |
| Command owner point-only; raw/list refusal and actual runtime/operator denials | `privileges` |
| Active revision2, supported retire/rejoin, new ID/revision1, old ID absent, durable mapping/history retained | `advance_revision`, `lifecycle` |
| Exact current heads/catalog and no grant activation; independent read-only inspection | `retained`, separate `--verify-retained` |
| Pre-I/O optimized-Python/repeated-run/source/log refusal; protected auxiliary inputs | focused `test_identity_pregrant_target.py` safeguards |

Harness acceptance RED was six missing-module failures before implementation; focused
GREEN was six passing tests. This is qualification scaffolding: the initial failure is
not evidence that the existing production Identity function was defective.

The first fresh native preparation (`pregrant-target-proof-20261022`) passed source
custody, supported fixture commands, current-head verification and the complete point/
context matrix. Its aggregate then refused an overstrict fixture restoration assertion:
restoring a soft-deleted profile legitimately changes its update timestamp. The read
itself had passed persistent-state preservation. That frame/data and the exact failed
qualifier remain retained; they are not relabeled as final acceptance. The corrected
qualification separates intentional fixture updates from read-only side-effect checks.
No production function defect or behavior change follows from this harness correction.

The second frame (`pregrant-target-proof2-20261022`) again passed the read matrix, then
exposed another explained fixture-only effect: the existing historical
`audit_log_identity_users` trigger appends an UPDATE audit entry for the intentional
profile soft-delete. Its source is the pinned platform audit migration, not new behavior.
That failed frame is retained. The lean correction checks the selected fixture row's
restoration, while every point read still requires full state—including audit rows—to
remain exactly unchanged. Fixture writes and read effects are distinct assertions.

## Verification commands

From the repository root, use the existing owner environment and a fresh root-prepared
proof directory (`F`). Keep redirected root output in the separate diagnostic directory
(`D`), since qualifier-generated proof logs are frozen inputs to retained inspection.

```sh
P=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
F=platform/deployment/.local/identity-baseline/pregrant-target-proof3-20261022
D=platform/deployment/.local/identity-baseline/pregrant-target-20261022
$P -I -B "$F/bootstrap_run.py" > "$D/root-bootstrap3-driver.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B "$F/root_qualification_driver.py" > "$D/root-all3.log" 2>&1
ACCESS_QUALIFICATION_DIR="$F" $P -I -B services/access/tests/qualify_identity_pregrant_target.py --verify-retained > "$D/root-retained3.log" 2>&1
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 $P -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
$P -B tools/py/run_compose_supabase.py --check-only
$P -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

The root driver calls the qualifier's same `--all` main with safe exception-class,
SQLSTATE and source-location diagnostics only. Neither private credentials nor raw
exception payloads are printed. Source/log/state receipts remain private retained
artifacts. Preparation is single-use; do not rerun these bootstrap/aggregate commands
against a consumed frame. Use a new namespace after any source change or failure.

Fixture correction focused RED: one missing-helper failure with six passes; final
focused GREEN: seven passes. Exact read-state expectations were not relaxed.

Fresh `pregrant-target-proof3-20261022` preparation and all seven aggregate stages
passed. A separate `--verify-retained` passed read-only. The proof binds 122 source
inputs and 3 generated logs, plus receipt and full retained-state digests.
Actual retirement/rejoin preserved the actor mapping, kept the retired revision2 row,
returned only the new revision1 membership and left grants/admission empty.

## Independent review

Three independent lenses completed sequentially under the agent thread limit. The
verification-gap lens found none. Seven confirmed verification/custody findings are
patched in six groups: bind the actual driver; exact pre-DB log inventory and final
original-log recheck; individual LOCAL setting/role reset; actual pool return/reborrow;
active revision2 in addition to rejoin1; auxiliary file permission/symlink adversaries.
Two low-value expansions were rejected with individual evidence in the spec: auditing
all deliberate fixture-write side effects would add a separate writer qualification;
sequence state mutations are already prohibited by the asserted read-only transaction.
No production defect, intent change, new ADR or new deferral was introduced. The
pre-review successful frame/diff remains retained, distinct from final reviewed proof.

Final reviewed qualification uses fresh `pregrant-target-accepted-20261022`. Its
bootstrap/aggregate/retained root logs use the suffix `-accepted` in the separate
diagnostic directory; the earlier proof3 commands and outputs remain pre-review
evidence. The final matrix includes active revision2; retirement advances that member
to3, and explicit rejoin creates a different revision1 member. The fixture changes only
the active member timestamp before the read matrix, preserving every other member field.

Final native acceptance: all8 groups pass, followed by a separate read-only retained
invocation. All123 source bindings (including actual driver) and3 generated-log digests
match independently; exact Identity19/Access10 and retained receipt/state digests pass.
The actual connection was returned to its pool and the same backend reborrowed with
clean original roles and all four LOCAL settings cleared. Active revision2, retired3
and new rejoin1 are distinct and exact. No Access grant/admission was created.


Final regression:1459 passed in46.68s, no skips. Focused safeguards:13 passed.
Both composition modes exited0 on final sources. Root logs are
`root-regression-accepted.log`, `root-compose-default-accepted.log` and
`root-compose-owned-accepted.log` in the diagnostic directory above.
All52 protected historical files and75 production sources remain byte-identical.
The approved native run99b7231c-0a5b-4bdb-98e8-3329564c526a stopped normally using
`P -B platform/deployment/dev.py stop --target platform/deployment/environments/kdg-local.json
--run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase` followed by the pinned absolute
Supabase path under `.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase`.
The completed stop receipt is `root-native-stop.log`. No reset/prune occurred; all
current/historical databases, data, receipts and frames remain retained. Final private
`root-final-evidence.json` binds owned files, source/log receipts, supplemental bootstrap
actor evidence, protected/frozen/concurrent inventories and the scoped local commit.
Concurrent document changes are preserved and excluded; no push or activation follows.

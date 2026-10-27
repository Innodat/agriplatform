# E1-ACCESS-A: controlled account grants

2026-10-26. [Execution spec](../../../../_bmad-output/implementation-artifacts/spec-1-6-e1-access-a-account-grant-configuration.md).
[Source-bound receipt](evidence/e1-access-configuration-20261026.json) records exact source,
reference, tool-input and retained proof/log hashes. Implementation and three independent
reviews are complete; all14 findings corrected, none deferred. Effective runtime decisions remain ACCESS-B; PtS cutover remains PTS-ADOPT.

Existing registry and organization provisioning are credited and preserved. Identity24
adds a private selected-account projection; Access17 adds separate retained account grants,
closed typed operator commands, exact revision checks, current original-login authority,
server actor/UTC attribution and atomic outcomes/events. No person, employment or organization
membership is needed for an account grant. A disabled application may be configured.

| Acceptance | Actual verification |
| --- | --- |
| Closed input, typed receipt, exact command/app/account authority | Focused failing-first tests; final owner/release suite **2,036 passed in185.34s**, one existing Starlette/httpx deprecation warning. Actual original Access operator login and CLI worker execute/recover a committed revoke. Changed input and cross-command operation reuse conflict. |
| Retry, revision and concurrency | Native qualifier passes14 stages: creation/exact retry, stale/absence conflicts, unchanged without event, demonstrated overlapping exact-revision revoke, deferred commit-expiry rollback, deactivated exact retry, retained-ID regrant, delayed revoke, selected lookup, same-person independent accounts and inactive-account refusal. Supplemental concurrent absence claims retain one mapping and no losing outcome/event; identical operation retries return one receipt/event. |
| Evidence and structural safety | Actual missing-event injection rolls back both creation and revocation; exact operations succeed after explicit trigger restoration. Both account/organization permission FK directions reject23503 through alternate owner writes. Actual runtime cannot DDL/write; forced RLS reads only its asserted account and clears transaction context on commit/rollback/reuse. |
| Short bounded observation and current authority | Exact wrong-account authority denies before a blocked Identity projection. An actual local advisory-lock wait exceeding five seconds rejects the stale observation before mutation; exact retry succeeds. After Auth/profile deactivation, exact revoke succeeds and reassignment fails. Revoked exact authority denies execute and lookup with unchanged grants/outcomes/events. |
| Controlled clean, previous and failure/recovery | Independent always-rollback reference rehearsal restores exact predecessor catalog before publication. Final source bootstraps genuinely empty owner schemas and upgrades two populated prior16/23 fixtures. Both owner catalogs pass under their real migration logins across five final frames. Actual release coordinator blocks its dry activation callback on catalog failure, leaves Access16 intact, and permits the boundary after explicit reconciliation/forward retry. |
| Previous organization clients and retained rows | Captured previous adapters replay/recover all26 original operations. Old enable/disable and membership retirement/rejoin commands work; a retained grant rebinds explicitly at revision2→3. Delayed old revoke replay and a fresh stale old-membership revoke preserve the new binding. Both actual old grant IDs, creator strings/actors and creation timestamps match preupgrade committed receipts. |
| Explicit synthetic legacy adoption | A selected legacy11 PtS row produces one ordinary account command under the actual current executor. All four legacy source rows retain composite IDs, creator strings and timestamps. Unselected rows are not converted; unknown permission and missing actor mappings refuse preparation. The source stays at11. No automatic union/import or consumer activation. |
| Frozen production image | Access installs its own frozen production lock offline with selected Python3.15.0/uv0.13.1, replacing the PtS requirements dependency. Actual image starts as UID65532 with read-only root, no capabilities/network/migration configuration and health200. Existing configured Studies cold startup passes with a synthetic readiness fixture and no network/DB calls. Stale-lock, foreign-payload and reinventoried packaged-source builds fail. Image/container are normally stopped and retained. |

Historical Access migrations/references1–16 and Identity1–23 remain byte-identical to
the pre-story capture. Native source-copy tampering and an unexpected SET-only runtime
role edge are rejected. The new runtime guard preserves only the independently observed
Supabase ADMIN-only bootstrap edge, with its exact flags, grantor and bootstrap role attributes.

## Commands and custody

Prepared interpreter `P` is
`platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python`.
Private frame `.local/leave-access-a-20261026/` contains guarded fixture-only drivers,
credentials and fsynced operation journals; do not publish its private inputs.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$P" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$P" -I -B services/access/tests/qualify_account_grants.py --fixture .local/leave-access-a-20261026/account3-fixture-private.json --output .local/leave-access-a-20261026/account-native-review.json
python3 tools/py/run_compose_supabase.py --check-only
python3 tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
"$P" -I -B -c 'import sys;sys.path.insert(0,"services/access");sys.argv=["export_openapi.py","--check"];import export_openapi;raise SystemExit(export_openapi.main())'
"$P" -I -B services/access/deployment/verify_runtime.py --root services/access --bundle services/access/runtime-bundle
```

Both composers, unchanged HTTP OpenAPI and current bundle checks pass. This story adds
operator contracts, not an HTTP administration endpoint; generated API types stay current.
The actual image proof is health/packaging evidence, not database/Auth integration or
runtime account-admission evidence. The release activation callback is a recorded dry
boundary; no service or consumer cutover occurs.

Private root drivers: `prepare_previous.py`, `resume_previous.py`, `prepare_cohorts.py`,
`rehearse_identity24.py`, `rehearse_access17_02.py`, `upgrade.py`,
`prepare_replacement_frames.py`, `prepare_cohorts2.py`, `prepare_account_fixture2.py`,
`supplement_native.py`, `supplement_authority.py`, `prove_legacy_cohort.py`,
`prove_previous_clients_continue03.py`, `prove_release_failure.py`, `prepare_clean2.py`,
`prove_final_catalogs.py`, `prove_image.py`. They bind actual container/network/loopback
and explicit `aca_88a737ddad7b_<namespace>` scratch databases on Leave55582; no shared KDG
connection or credential rotation. Reuse requires fresh reviewed fixture/output paths,
not resetting or blindly rerunning accepted commands. Normal stack stop preserves volumes.

## Retained failures and corrections

Initial parser/package tests fail before implementation. Native rehearsals found a
permission-dependent cross-owner metadata probe, missing strict projection allowlist,
PL/pgSQL CASE syntax and shared-trigger record-field access. All were corrected and
rehearsed independently. The first accepted candidate reference and all installed frames
are preserved; corrected Access17 uses fresh reference/native/populated/clean frames.
The first failed account operation is reconciled with no grant/outcome/event.

A rollback-only role probe exposed missing standalone runtime membership validation;
the first stricter guard then correctly failed on the existing native bootstrap edge.
Its exact independently read ADMIN-only metadata is now preserved; unexpected outgoing
SET-only membership still fails. Cross-command operation collisions now produce the
specific safe conflict using the exact ledger uniqueness constraint, preserving other errors.

Driver corrections are retained: prior source16 initially required its declared reader
SET-only prerequisite; it was explicitly prepared before retry. A supplemental admin
attempt to update protected authority denied42501; the actual owner completed the proof.
Previous-client proof initially selected a retired replay receipt instead of the new join,
and incorrectly expected an absent/new grant rather than its historical retained revision.
The corrected continuation recovers the explicit committed operation; no source semantics
were changed. Initial unscoped owner row snapshots returned empty through RLS and do not
establish data preservation; final guarded reads compare actual rows to preupgrade receipts.
Isolated Python's direct exporter lacks its import path; the explicit owner-path launch passes.

## Impact decisions

- Scaffold: proven controlled migration, original-login operator and offline packaging
  patterns reused owner locally; no new generic importer/runtime authorization framework.
- Shared UI: none; no UI surface is introduced.
- Agent context: existing ownership, scope, attribution and release rules suffice.
- Documentation: owner account-grant runbook, this evidence and Leave tracker/handoff.
- ADR: implements accepted scope, attribution, structural integrity and release decisions;
  no accepted ADR is modified and no new decision is needed.

## Independent review corrections

All14 findings were individually triaged in the execution spec:10 blind,2 edge and2
verification findings. B9/V1 share the deferred-boundary proof; no finding was deferred.
The original reports/diff and both earlier Access17 candidate references remain retained.

Bundle verification now binds every packaged owner file to its authoritative source,
requires the expected interpreter/stdlib/dependency layout and owner execute permission,
and preserves the existing Studies readiness module. Four focused regressions failed
before correction; all7 package tests then passed. The actual rebuilt image proves normal
and synthetic opt-in Studies startup, plus rejection of a forged packaged source even
when its self-inventory is recomputed. This is contract/startup evidence, not production
Studies eligibility or provider/database qualification. The owner runbook gives the exact
selected offline package/build and archive-before-rebuild commands.

Access17 preserves schema owner/ACL and index definition/operational metadata. Actual
rollback-only schema CREATE and index-definition alterations, accepted before review,
now reject. Exact committed assignment recovery checks current operator authority before
requiring fresh account eligibility; both profile-only and Auth/profile-deactivated retry
cases now return the original receipt while changed input conflicts.

The qualifier proves both race sessions actually wait before release, asserts exact
committed/refused outcome and event sets with targets/executor/relationship, denies a
wrong revoke UUID under otherwise valid authority, and reserves command files exclusively
before guard or mutation. It proves a successful SQL result followed by expiry at COMMIT
rolls back the grant/outcome/event; the exact operation then succeeds. Source-bound native
journals retain the returned-before-commit, AC004 commit refusal and both-waiting markers.

Corrected Access17 reference:
`7bfa0b7d8057b9004fd6ffa97478b2101427caa3985e4b0c9ad5c2934058c7c3`.
Independent rollback rehearsal on fresh prior16 restores exact16 before publication.
Final frames reference3/native3/previous3/failure3/clean3 pass controlled upgrades, clean
bootstrap, explicit failure/reconciliation/forward retry and actual current catalog checks.
Previous clients pass in one corrected fresh run against actual retained rows; all26 old
operations replay/recover. Explicit legacy adoption is repeated against final source using
the original four legacy11 rows strictly read-only, with their prior hash unchanged.
Review drivers and outputs use `review`, `*3` and `previous3` names in the private frame.
The obsolete standalone review prompts were prepared during temporary agent-capacity
refusals; all three context-free reviews ultimately ran locally and those prompts are unused.

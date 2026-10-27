---
title: 'E1-ACCESS-A: Complete controlled account capability grants'
type: feature
created: '2026-10-26'
status: done
route: dispatch
baseline_commit: cd41aea6b72593c9352e3cd67845df7e2fdce70f
review_loop_iteration: 0
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/platform/docs/development/migration-verification.md'
---

<frozen-after-approval reason="user-approved Leave implementation, epic-level reviews and next ACCESS-A">

## Intent

Complete ACCESS-A's controlled provisioning using the delivered registry and organization
commands. Add general account-capability assignment/revocation, retaining independent
organization grants. Correct Access's own locked container inputs and prove the approved
synthetic adoption/recovery path. Runtime enforcement remains ACCESS-B.

## Boundaries & Constraints

Always use existing closed operator envelope, original-login exact command/app/account
authority, server attribution, positive decimal-string revisions, atomic local outcomes
and events, controlled additive migrations and actual restricted native proof. PtS
capabilities are account-scoped; Leave capabilities remain organization-scoped.

Never change historical migrations/references, mutate shared KDG/live accounts, union
legacy organization grants, invent membership/person/employment, expose a setup HTTP API,
change Studies enrollment, activate consumers, introduce generic import/authorization
frameworks, change root dependencies, commit or operate remotely. Preserve dirty work.

</frozen-after-approval>

## Code Map

- Authority: epics.md ACCESS-A3520–3617 plus later PtS amendments; accepted account
  design: `platform/docs/architecture/contracts/application-admission-and-discovery.md`
  559–637; command catalogue: `e1-controlled-provisioning-and-evidence.md`107–117.
- `services/access/migrations/versions/0003_registry_storage.py` through0014: delivered
  registry/organization commands and evidence guards; credit and preserve.0016 Studies
  grant is a separate fixed capability, not general account administration.
- `services/access/access_operator_input.py`, `access_operator.py`, `operator_cli.py`:
  extend existing typed parsing/canonical results/worker and exact outcome selectors.
- `services/access/identity-migrations/versions/0018_account_actor_ensure.py` and0019:
  private Auth/profile verification and protected setup pattern. Existing own-account
  projection is not arbitrary target setup; do not forge user context to reuse it.
- `services/access/migrations/access_baseline.py`, Identity `identity_baseline.py`:
  preserve predecessor/source/role guards; append new-head checks without weakening old
  recognition. New references require independent root rollback-only rehearsal.
- `services/access/pyproject.toml`, `uv.lock`: approved independent Python3.15 baseline.
  Dockerfile incorrectly installs PtS requirements under Python3.12. Reuse proven offline
  interpreter-carrier packaging semantics from public-service templates, owner locally;
  never hand-edit generated templates/artifacts or install dependencies into root.

## Tasks & Acceptance

- [x] `services/access/tests/test_account_grants.py` -- first observe valid planned
  commands rejected; add focused typed/receipt/context/conflict/worker protection.
- [x] `services/access/identity-migrations/versions/0024_account_grant_target.py` and
  owner catalog helper -- private `identity.account_grant_target(uuid)` returns exact
  account_id/actor_id for live Auth/profile and stable account-kind actor. Existing
  identity_account_verification_owner, Auth id/deleted_at access; add only required
  Identity column reads/policies. EXECUTE only access_command_owner; setup context has
  absent app.account_id/org_id, nonnil server executor and exact app.target_account_id.
- [x] `services/access/migrations/versions/0017_account_grants.py` and catalog support --
  separate account_grants, local scope-correct permission FK, revision/revocation and
  server UTC actor provenance; protected account_grant.assign/revoke and scoped outcome.
- [x] Existing parser/adapter/CLI -- assign create requires account_id/permission and
  expected_absent; update additionally exact grant_id/current expected_revision. Revoke
  requires exact grant_id/account_id/permission/revision. Platform scope; no actor/org/
  membership override. UUID grant IDs; same typed compact result plus event reference.
- [x] `services/access/tests/qualify_account_grants.py` -- consume root-prepared private
  explicit Leave fixture; no discovery/setup/reference recording. Real original logins,
  exact ledger/event assertions, direct permission/constraint denials and isolated CLI.
- [x] `services/access/deployment/package_runtime.py`, Dockerfile/context/tests -- root
  owns offline production-only frozen packaging and hardened image proof with source/
  lock provenance. No migration credentials/startup DDL or PtS installation dependency.
- [x] Access runbook and Leave evidence/tracker -- acceptance mapping, approved manual
  cohort adoption, release/recovery and five impact decisions; historical evidence retained.

Acceptance:
- Given exact authorized platform command, when assigning registered account capability,
  then verified account/actor observation precedes local locks, scope FK rejects organization
  capabilities, absence/revision/grant identity is checked, and one intended change commits
  atomically. Disabled apps may be configured without claiming effective admission.
- Given retries, concurrent commands, stale state or required evidence failure, when
  executing/recovering, then one outcome/event exists for a changed operation, unchanged
  has no fictitious event, changed input conflicts, and rollback leaves no partial grant.
- Given inactive account or revoked/regranted record, when revoking/retrying, then exact
  retained grant/revision controls removal; revoke needs no live account observation and
  delayed revoke cannot affect a newer regrant. No other account/person grants are unioned.
- Given absent/foreign authority or runtime credential/context spoof, when writing or
  looking up receipts, then deny before projection/evidence disclosure; runtime cannot
  DDL/write and account-scoped reads do not expose another account on reused connection.
- Given delivered organization registration/configuration/grant commands, when verifying
  current clean/previous16 upgrades and native organization transitions, then preserve
  their IDs, attribution, receipts, semantics and independent scope. Test both directions
  of scope mismatch and no cross-scope implied grants; ACCESS-B owns effective decisions.
- Given retained read-only synthetic legacy11 PtS rows, when preparing explicitly selected
  cohort account commands, then verify known permission/actor mappings and preserve old
  composite IDs/creator strings; unknown/missing mappings block preparation. New grants
  use actual executor, not guessed legacy actor. No automatic conversion or raw-schema
  takeover; incompatible legacy source remains unchanged at11. Planned consumer cutover
  and corpus migration stay gated on ACCESS-B/PTS-ADOPT.
- Given controlled migration/build failure, when reconciling, then activation stays blocked,
  previous state/data or exact rollback is proved, forward retry is explicit, and prior
  owner clients remain compatible. Actual locked production image starts nonroot read-only
  without setup credentials; type/source tests alone do not prove native permissions.

## Implementation Notes

No unresolved product choice. Native-only scratch mutations/builds are reversible and
already authorized; preserve frames. Private baseline: .local/leave-access-a-20261026/.
Root alone owns fixtures, stack lifecycle, independent reference publication and image
proof. Credit existing native records separately from fresh current-head proof. Capture
source/tool/log hashes and failed attempts. No UI/context/ADR change; document scaffold
reuse and owner-local deviations. User authorized autonomous routine implementation.

## Spec Change Log

## Review Triage Log

| ID | Verdict | Route | Verified evidence and correction |
| --- | --- | --- | --- |
| B1 | medium | patch | Bundle inventory can be recomputed independently of input hashes. Bind each packaged owner source directly to its authoritative input. |
| B2 | medium | patch | Existing verifier test accepts only payload.txt; required runtime layout is absent. Require selected interpreter/site-packages/all owner files. |
| B3 | low | patch | File hashes omit executable mode; a chmod leaves inventory unchanged. Add the direct interpreter execute-mode check alongside required layout. |
| B4 | medium | patch | Native rollback-only GRANT CREATE ON SCHEMA access TO access_runtime passes the standalone17 verifier. Include schema owner/ACL metadata. |
| B5 | medium | patch | Existing predecessor checks index definitions/operational flags;17 omits them. Native ALTER INDEX fillfactor changes its definition but passes17. Preserve the existing selected metadata check. |
| B6 | medium | patch | Actual committed replacement assignment exact retry after Auth/profile deactivation returns operation_verification_unavailable. Recover an exact retained receipt under current authority before fresh-target requirements. |
| B7 | medium | patch | Two uncoordinated tasks can run serially; returned receipts alone establish no overlap. Prove both attempts waiting on an explicit held coordination lock. |
| B8 | medium | patch | Cardinality iterates only returned rows and does not compare expected committed/refused operation sets. Assert exact sets and matching target/event relationships. |
| B9 | medium | patch | Existing expiry proof waits before mutation; no successful call followed by expired COMMIT is tested. Add native deferred-boundary rollback and exact retry. |
| B10 | medium | patch | Owner runbook omits usable package/build and occupied-bundle replacement commands. Add exact selected offline commands and retained archive procedure. |
| E1 | high | patch | Main conditionally imports studies_readiness for configured production Studies; explicit bundle/context omit it. Include the existing module and test enabled startup with a synthetic contract fixture. |
| E2 | medium | patch | Qualifier command_path.write_text follows existing siblings/symlinks after DB writes. Reserve its command output exclusively before guard or mutation. |
| V1 | medium | patch | Pre-verified gap duplicates B9: successful function return followed by expiry before commit remains uncovered. Same native correction. |
| V2 | medium | patch | Pre-verified wrong-account case denies at authority first; no authorized mismatched revoke UUID assertion reaches receipt comparison. Add wrong-grant denial plus exact lookup success at adapter boundary. |

All three independent reports received before triage. Finding-floor arithmetic is not
an additional finding. B9/V1 share the deferred-boundary correction; each finding retains
its own row. No intent change, deferral or spec amendment is required. Review capacity
initially refused parallel launches; completed reviewers released slots and all three
context-free passes ultimately ran locally. Standalone prompts remain retained but unused.

## Verification

Prepared Python: platform/deployment/.local/access-organization-check-20261022/owner-env/bin/python.
Run smallest acceptance failure first, then affected owner/release suite with
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1, -I -B -m pytest, -p no:cacheprovider. Both composers,
owned --no-seeds, must pass. Native only existing Leave run88a737dd-ad7b-429a-a83c-5d103716d659,
DB55582/Auth55581, explicitly bound scratch DB/credentials and actual container/network
check. Reuse synthetic actors/Auth inputs; never reset earlier frames or rotate credentials.

Verification complete before independent review: 2,021 owner/release tests;12 native stages;
7 supplemental native stages; five final owner catalog pairs; controlled clean/previous/
failure-forward-retry; previous26 client operations; explicit legacy11 cohort; locked image.
Both composers, OpenAPI and bundle checks pass. See
[Access evidence](../../apps/leave/docs/testing/e1-access-configuration-evidence.md).
Dirty pre-existing work is pinned by the pre-edit278-file byte capture in addition to the
canonical HEAD above; the task review diff excludes unchanged earlier deliveries/caches.

Final review correction verification: **2,036 passed, one existing warning,185.34s**;
14 native stages,7 supplemental stages, all five current catalog pairs, fresh clean/
previous/failure-forward-retry, all26 previous-client receipts, read-only legacy11 cohort,
corrected hardened image with synthetic opt-in Studies startup, both composers/OpenAPI/
bundle checks PASS. All14 findings fixed, none deferred. Sources1–16/Identity1–23 and
historical references remain byte-identical; earlier draft17 fixtures/references retained.
No commit, live/KDG mutation, consumer activation or ACCESS-B runtime decision claim.

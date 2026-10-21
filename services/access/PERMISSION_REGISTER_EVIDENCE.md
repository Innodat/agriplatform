# Protected permission registration evidence

2026-10-21. Bounded synthetic Access0005 delivery under the approved permission
registration spec. This extends the existing owner migration/operator/target route.
It creates immutable registry configuration and recovery evidence, with no effective
access, entry registration, enablement, grant, consumer activation or new lifecycle.

## Requirements and implementation

| Requirement | Implementation / proof |
| --- | --- |
| Closed platform envelope, literal ASCII 1–200 except NUL, scopes and expected absence | Existing pure `RegisterPermissionCommand`; full JCS/SHA256 envelope; focused canonical/input cases and native literals including controls/DEL/escaping, min/max, both scopes and 24 malformed SQL cases |
| Existing disabled app allowed; immutable global permission association | Access0005 `register_permission`; existing statement immutability guards; matching register unchanged, app/scope reassignment conflict; missing application conflict with no writes |
| Current exact command/app authority from original session | Separate fixed `permission_operator_authority`, existing principal/authority owners and serialization; disabled/revoked principal, application-only authority, exact-app authority, wrong original login, GUC/role attacks and after-wait checks |
| Atomic permission/outcome/event and closed linkage | Permission required-registration deferred guard; command-specific outcome/event validation, executor/time/target/scope/reason/evidence; event injection rollback, raw missing registration, authorized rollback-only forged event and missing event tests assert exact guard messages |
| Typed durable receipt, current-authorized recovery and command isolation | Null revision, exact `{app_id,permission}`, event only for created; replay/changed input, wrong target, unresolved, lost real COMMIT response and real isolated CLI; application/permission same operation UUID retain their own receipts |
| Concurrent exact retry and competing mappings | Actual witnessed retry/authority/global permission locks; same operation and changed retry; cross-app/scope races; only outcome-key timeout maps busy, domain/authority waits unavailable |
| Exact known clean/1/2/3/4/5, preservation and Identity isolation | Fixed history/catalog/ACL/function checks with pinned 0004/0005 sources; populated4/5 snapshots preserve all prior rows/receipts; unknown/default/trigger/security/foreign privilege refusal; genuine Identity18 controlled repeat validates only Access metadata |

The fixed registration routine verifies the full canonical envelope against its typed
arguments, then writes its reason/evidence values into the creation event. Row guards
validate allowed reason/evidence shape/value and command-specific target/transition and
outcome linkage; they do not recover these values from a stored SHA256 fingerprint.
No full command payload is stored in the outcome/event or returned by lookup.

Access0005 replaces the earlier outcome uniqueness with
`UNIQUE NULLS NOT DISTINCT(scope_kind,scope_id,executor_actor_id,command_type,operation_id)`.
Application wrappers now select their exact command/platform scope without changing their
call signatures or earlier data. Original migrations 0001–4 and all Identity migrations
and immutable reference files remain unchanged. The mutable Identity verifier chooses
exact Access4/5 metadata from installed routines and gains no Access data/ledger reads.

## RED and focused verification

The root's preimplementation CLI `command_unsupported` and restricted native missing
function RED are retained privately at `permission-register-red-20261021`.
The additional four focused failures were observed before implementation and retained
unchanged as `focused-red.log` in the candidate frames (original temporary capture
`/tmp/permission-register-work/focused-red.log`). They proved missing typed permission
receipts, actual-command lock isolation, permission execute/lookup dispatch and known 5.

Canonical interpreter:
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
No dependency changes or ambient pytest plugins/cache were used.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$KDG_PY" -I -B -m pytest services/access/tests/test_permission_register.py services/access/tests/test_application_register.py services/access/tests/test_operator_cli.py services/access/tests/test_access_operator_input.py services/access/tests/test_access_membership_binding.py services/access/tests/test_access_registry_storage.py -q -p no:cacheprovider
```

**238 passed in 2.83s**; final output retained as `focused-green.log` in candidate2.
Coverage includes permission receipt/dispatch/canonical closure, CLI literal values that
look like flags (`--permission=<literal>`), response target validation, new source-drift
refusal before import, fixed 4/5 catalog expectations, application compatibility, existing
CLI process bounds and Identity refusal before target dispatch. Earlier input tests were
updated only where permission execution is now intentionally supported; entry commands
and all Identity registry dispatch remain closed.

## Historical candidate2 qualification and retained inspection

Actual authorized disposable run: `99b7231c-0a5b-4bdb-98e8-3329564c526a`,
`runtime_ready=false`. Historical candidate private frame (superseded by subsequent review patches):
`platform/deployment/.local/identity-baseline/permission-register-candidate2-20261021/`.
The existing explicit bootstrap prepared 20 new isolated databases and a fresh bounded
Access CLI namespace without changing existing roles, secrets, databases or run identity.
Genuine Identity18 preparation verified the stable synthetic service actor before Access
principal mapping. Bootstrap custody records the same 72 executed source hashes before
and after both sequential scripts, including the new qualifier and migration. Source
witnesses are never refreshed to hide changes.

```sh
"$KDG_PY" -I -B platform/deployment/.local/identity-baseline/permission-register-candidate2-20261021/bootstrap_run.py
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/permission-register-candidate2-20261021" "$KDG_PY" -I -B services/access/tests/qualify_permission_register.py --all
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/permission-register-candidate2-20261021" "$KDG_PY" -I -B services/access/tests/qualify_permission_register.py --verify-retained
```

Candidate2 aggregate on its original source: **24 native groups passed**, with unchanged
72-source custody. This is historical evidence after the follow-up review patches below.
Separate retained invocation: **passed**, with identical complete catalog/data snapshots
and exact known-head inspection. Private `all.log`, `results.json`, `retained.log`,
`retained-results.json` and `retained-state.json` record these results. The genuine
Identity18 repeat is inherited from the application fixture (its historical step label
mentions Access4); in this aggregate it ran after the actual Access5 migration and
permission cases. The real permission CLI used literal `--owner` through
`--permission=--owner` and recovered the exact compact committed receipt. Forged evidence
ran under an explicitly authorized original-session migrator fixture wholly rolled back;
its exact `access_event_invalid` refusal and the missing-event
`access_required_event_missing` refusal were observed without retaining fixture authority.
Root independently reviews/verifies the source and performs the specified broad regression,
both composition checks, preservation audit, normal disposable stop and commit. Those
root results are not claimed by this candidate evidence.

## Preserved attempts and limits

- `permission-register-attempt1-20261021`: sandbox loopback refusal at the first connection;
  no database created. Failed bootstrap witness/log retained.
- `permission-register-attempt2-20261021`: fresh bootstrap passed. Initial isolated-script
  import and SQL/catalog/ACL fixture debugging remain retained; never claimed current proof.
- `permission-register-attempt3-20261021`: fresh bootstrap and initial matrix progressed
  through application checks; remaining debug stages passed after adding the copied
  adversary method's missing imports and reusing the existing CLI descriptor. Source
  changed during debug, so its original witness remains historical.
- `permission-register-candidate-20261021`: 23 native groups and separate retained
  inspection passed on its original 72-source frame. The later CLI flag-literal and root
  evidence/authority/source-pin audit fixes make that frame historical, not current proof.

All qualification operates on synthetic accounts/actors/configuration in the selected
local disposable run. No production/real account/access, deploy/provision/pilot/push,
reset/prune, Leave/editor, effective consumer checks, ACCESS-B or enablement/grant work
was performed. General bootstrap portability remains the preexisting explicit fixture
prerequisite. Existing operator process isolation handles blocked/late COMMIT uncertainty;
a client clock cannot cancel a network COMMIT. Current authority is still required to
recover any durable result. Unsupported catalog state requires owner disposition without
repair or automatic rollback.

## Five impacts

- Scaffold: extend proven owner-local command, exact migration/catalog, typed receipt,
  trusted CLI and native custody/attack fixtures; no generic framework or runtime engine.
- Shared UI: no impact; no browser/admin surface.
- Agent context: no new instructions; existing actor/owner/ATDD/release safeguards suffice.
- Documentation: permission runbook/evidence, mutable substrate and KDG handoffs updated.
- ADR: existing accepted decisions suffice; no accepted ADR changes.


## Follow-up review patches

The shared preparation runbook now points to Access0005 and the separate permission
command authority. Qualification now seeds an actual permission/outcome/event before
populated5 head repeat and recovers that original receipt afterward, proves operation
reuse in both command orders with executes/replays/lookups, and witnesses a receipt lookup
waiting while authority revocation commits before its denial. Direct canonical SQL cases
include escaped JSON NUL with exact safe AC005/no-effects; literal NUL lookup still refuses
before SQL with command_invalid. The adapter's application/permission result validation
uses explicit local branches.

Previous-version compatibility uses the actual application adapter from baseline commit
`45ab5dfaeecc836c560e3b4985defea83b1a2957`, loaded only from the private fixture
`bootstrap_previous_application_adapter.py` with fixed SHA256
`36a93ba836dbe873ca8080d5694762d05b4cd8fa49a0c3a279e7a06536a6ddcb`.
Root captures this file from git **before** bootstrap custody; the existing bootstrap*.py
source inventory includes it. Missing/modified source refuses. The native stage executes,
replays and looks up through this previous adapter on Access5 and verifies the preserved
original application receipt/data. No retained source or previous witness is rewritten.

Candidate2 and all earlier frames remain historical, source-bound results. Root performed final
fresh preparation/native/retained proof and broader verification below after these patches.
Only the tests covering the edited adapter/qualification files are run in this follow-up.

## Final root verification — 2026-10-21

Final frame: private
`platform/deployment/.local/identity-baseline/permission-register-reviewed2-20261021/`.
Root executed fresh preparation and all **25 native groups**, then a separate retained
inspection. All passed with identical before/after/aggregate/retained inventories of
**73 executed sources**, including the pinned previous application adapter. The review
extensions prove populated permission/outcome/event preservation on5 repeat, command
reuse in both orders, previous-adapter create/replay/lookup against5, receipt-lookup
revocation after a witnessed wait, and 25 malformed canonical/SQL cases including escaped
NUL. An additional root invocation of the real isolated CLI recovered exactly the saved
permission receipt for the flag-like literal `--owner` (`root-cli-verification.json`).

Canonical interpreter is `$KDG_PY` above. Root commands/results:

```sh
"$KDG_PY" -I -B platform/deployment/.local/identity-baseline/permission-register-reviewed2-20261021/bootstrap_run.py
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/permission-register-reviewed2-20261021" "$KDG_PY" -I -B services/access/tests/qualify_permission_register.py --all
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/permission-register-reviewed2-20261021" "$KDG_PY" -I -B services/access/tests/qualify_permission_register.py --verify-retained
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$KDG_PY" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
"$KDG_PY" -B tools/py/run_compose_supabase.py --check-only
"$KDG_PY" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Affected regression: **1225 passed in 33.69s**, retained in `root-regression.log`.
Both composition routes passed without changing files (`root-compose-bridge.log`,
`root-compose-owned.log`). Before broad regression, root normally stopped the actual
run using `dev.py stop --target platform/deployment/environments/kdg-local.json --run-id
99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase <existing pinned absolute CLI>`;
result was `completed`, `runtime_ready=false`, project
`agriplatform-kdg-mbcjHApbS9uY6DMpVkxSag`. Data, Docker resources and previous receipts
remain preserved; no reset/removal or activation occurred.

Three independent review lenses completed. The third launch initially hit the agent
thread limit and succeeded sequentially after a reviewer finished; no manual-session
fallback was needed. All 11 findings have separate verdicts in the spec: eight patched,
one rejected low, one refuted as unreachable, and one preexisting bootstrap-portability
prerequisite deferred to the established owner tooling. Published commands still require
explicit private fixture preparation; no fresh-checkout or hosted-CI readiness is claimed.

The earlier root frame `permission-register-reviewed-20261021` passed preparation but
refused qualification before `all-started`: a final receipt-validation cleanup overlapped
preparation and changed `access_operator.py` after custody capture. Its original witness,
logs and prepared databases remain retained. No aggregate business writes ran there, and
its witness was not refreshed. After source freeze confirmation, the final reviewed2
frame above passed without source changes. The follow-up targeted tests passed 73 cases;
root's broader regression includes them on final source.

Scoped whitespace and frozen-intent verification passed. Preservation checks confirm
all 42 historical files, 13 concurrent tracked files and 40 concurrent untracked files
remain byte-for-byte unchanged. Dependency pins, including TypeScript 7.0.2, are unchanged.

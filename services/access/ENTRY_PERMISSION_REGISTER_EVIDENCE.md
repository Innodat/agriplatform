# Protected entry-permission registration evidence

2026-10-21. Bounded synthetic Access0006 delivery under the approved entry-permission
registration spec. This adds immutable entry configuration through the existing owner
route, without access grants, enablement, ACCESS-B or consumer activation.

| Requirement | Implementation and proof |
| --- | --- |
| Closed platform envelope and literal ASCII1–200 except NUL | Existing unchanged input record, exact full-envelope JCS/SHA256 validation; focused receipt/canonical/CLI tests and native SQL malformed/literal boundary cases |
| Existing exact association, both scopes, disabled apps, multiple entries | `register_entry_permission` validates the existing app/permission association, never writes permissions; native functional cases preserve scopes/app state and reject missing/wrong association |
| Exact current original-session authority | Separate fixed `entry_permission_operator_authority`; existing authority serialization and after-wait rechecks; disabled principal/command and wrong app, inherited restricted-role/foreign privilege attacks, witnessed execute/lookup revocation |
| Atomic immutable binding/evidence/outcome | Deferred entry required-registration trigger, closed command-specific outcome/event guards; exact actor/time/target/empty transition/reason/evidence assertions; injected event failure, raw missing evidence and rollback-only forged/missing event assertions |
| Typed durable recovery and three-command UUID isolation | Null revision, exact target, event only on creation; changed envelope conflict, exact-target lookup/denial/unresolved, real lost COMMIT response, application/permission/entry shared UUID executes/replays/lookups in both orders |
| Bounded concurrent execution and truthful busy | Stable command outcome lock, exact mapping lock and retained authority lock; witnessed duplicate/distinct/changed retry races; only outcome-key wait maps busy, authority/domain waits unavailable |
| Exact known clean/1/2/3/4/5/6 and compatibility | Fixed catalogs retain historical4/5 branches, pinned0004/5/6 sources; populated5 upgrade/receipt preservation, populated6 repeat, actual previous0005 adapter create/replay/lookup, genuine Identity18 metadata-only repeat |

Entry `created_at`, event `created_at`, outcome `committed_at` and receipt timestamp are
asserted equal in native functional proof. The routine binds event reason/evidence to
canonical input. Row guards validate allowed values, exact target/transition and required
linkage; they do not recover reason/evidence from the stored digest. The existing unique
single-event registration subset is retained. No generic multi-event WRITE claim is made.

Historical Access0001–0005, all Identity migrations and immutable references are untouched.
The mutable Identity helper selects exact Access4/5/6 metadata by installed routines,
without reading Access business data/history. Only SELECT/INSERT entry privileges are
added to the existing command owner; the operator receives exact entry routines only.

## Focused RED and GREEN

Root retains its preimplementation CLI/native RED privately at
`entry-register-red-20261021`. Additional focused RED was observed before code:
**3 failed, 1 passed**, retained at `/tmp/entry-focused-red.log` and in the candidate frame.
Failures proved missing typed entry receipts, protected entry execute/lookup dispatch and
revision6 catalog support. Focused GREEN: **250 passed in 2.92s**, retained as
`focused-green.log`. Intentional historical tests now expect entry execution and HEAD6;
Identity parser/adapter/CLI still reject all Access command envelopes before dispatch.

Canonical interpreter:
`platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python`.
No dependency changes or ambient plugins/cache were used.

```sh
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$KDG_PY" -I -B -m pytest services/access/tests/test_entry_permission_register.py services/access/tests/test_permission_register.py services/access/tests/test_application_register.py services/access/tests/test_operator_cli.py services/access/tests/test_access_operator_input.py services/access/tests/test_access_registry_storage.py services/access/tests/test_access_membership_binding.py -q -p no:cacheprovider
```

## Synthetic preparation, custody and recovery

Actual disposable run: `99b7231c-0a5b-4bdb-98e8-3329564c526a`, `runtime_ready=false`.
Each frame prepares fresh isolated databases and a fresh bounded CLI namespace with the
existing private bootstrap. Existing roles, credentials, run identity and prior data remain.
Bootstrap captures executed source before/after, including the qualifier,0006 and pinned
previous adapters. Witnesses are never refreshed to conceal changes.

The actual0005 adapter is captured from baseline commit
`cdfa6f3792f7e7880ae84b13aae92a2ef8ee6ad3` before custody as
`bootstrap_previous_permission_adapter.py`; its fixed SHA256 is recorded in the qualifier.
The existing pinned previous application adapter remains included. Both execute under
restricted original-session operator credentials against the new schema.

Candidate private frame:
`platform/deployment/.local/identity-baseline/entry-register-candidate-20261021/`.
Commands (explicit private bootstrap preparation remains required):

```sh
"$KDG_PY" -I -B platform/deployment/.local/identity-baseline/entry-register-candidate-20261021/bootstrap_run.py
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/entry-register-candidate-20261021" "$KDG_PY" -I -B services/access/tests/qualify_entry_permission_register.py --all
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/entry-register-candidate-20261021" "$KDG_PY" -I -B services/access/tests/qualify_entry_permission_register.py --verify-retained
```

Candidate aggregate: **32 native groups passed**, with identical bootstrap before/after
and aggregate inventories of **76 executed sources**. Separate retained invocation:
**passed**, with complete saved catalog/data snapshots unchanged and the same76-source
inventory. `all.log`, `results.json`, `retained.log`, `retained-results.json` and
`retained-state.json` retain the proof. Inherited stage labels still mention Access4/5
and one reused recovery label says permission; the actual new entry routines and
Access6 catalog run in the entry stages. Root independently owns final
source audit/review, fresh final verification, broader regression, both composition checks,
preservation audit, normal disposable stop and scoped commit; candidate proof does not
claim those root results.

Attempts remain retained: attempt1 stopped before database creation on sandbox loopback
refusal. Attempt2 prepared successfully and exposed fixture setup issues during debug:
distinct-operation races must hold the common domain lock, lost-response entry cases
must pre-register their permission, and scoped authority identity must be added through
a new row instead of mutating an immutable tuple. Its original witness remains historical;
separate debug logs are retained privately. No failed frame is claimed as final proof.

## Five impacts and limits

- Scaffold: extend proven local registration/receipt/catalog/CLI/custody patterns; no new framework, lifecycle or generic engine.
- Shared UI: no change; no browser/admin surface.
- Agent context: existing owner/actor/ATDD/release rules suffice; shared owner preparation instructions now point to6 and exact entry authority.
- Documentation: entry runbook/evidence, current application preparation, mutable substrate/WRITE and KDG handoffs updated.
- ADR: existing accepted decisions suffice; none edited.

General bootstrap portability remains deferred. A client clock cannot cancel a network
COMMIT; late/lost completion remains uncertain and recoverable only with current exact
authority and original operation/input. No production/real account/access, infrastructure,
deploy/pilot/push/reset/prune, Leave/editor, enablement/grants or consumer activation was
performed. All results are source-bound synthetic evidence, not hosted-CI or fresh-checkout
readiness claims.


## Review qualification extensions

The candidate above remains historical source-bound proof. Follow-up qualification
changes use a fresh absent binding for distinct-operation contention and assert one
creation, one unchanged receipt, one binding/event and two recoverable outcomes.
They add app-scoped-only create/replay/lookup, rollback-only assumed/inherited operator
rights with an unregistered original session, principal revocation during witnessed
execute/lookup retry waits, direct lookup malformed/isolation cases, and lookup retry/
authority lock classification. Forged entry evidence now independently varies target,
type, executor, operation, outcome link and transition with exact row-guard rejection.
Retained verification requires aggregate source equality with the captured witness;
a focused mismatch fixture proves refusal before retained-state reads or writes without
altering any previous frame. The runbook includes separate app-bound entry-authority SQL.

Focused follow-up: **11 passed** in `test_entry_permission_register.py` using the
canonical interpreter with ambient pytest plugins/cache disabled. Final fresh
bootstrap/native/retained verification remains root-owned; no previous custody witness
or frozen specification is changed.

## Final reviewed verification

Root inspected the complete scoped diff. Three independent BMAD review layers completed;
the edge lens returned no findings. The blind and verification lenses exposed the absent
creation-race proof and the additional bounded checks listed above. Those checks and the
concrete preparation example are patched. Per-finding verdicts are retained in the Build
spec. There are no unresolved findings caused by this item. Existing fresh-checkout
bootstrap portability remains deferred.

Final fresh frame: `entry-register-reviewed-20261021` under the same private proof parent.
No credentials, receipts, state or witness were copied from a previous frame: only the
existing bootstrap scripts, pinned previous adapters and Auth helper definitions were
copied before fresh preparation. The final commands were:

```sh
"$KDG_PY" -I -B platform/deployment/.local/identity-baseline/entry-register-reviewed-20261021/bootstrap_run.py
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/entry-register-reviewed-20261021" "$KDG_PY" -I -B services/access/tests/qualify_entry_permission_register.py --all
ACCESS_QUALIFICATION_DIR="$PWD/platform/deployment/.local/identity-baseline/entry-register-reviewed-20261021" "$KDG_PY" -I -B services/access/tests/qualify_entry_permission_register.py --verify-retained
"$KDG_PY" -I -B /tmp/entry-register-root-cli.py
"$KDG_PY" -B platform/deployment/dev.py stop --target platform/deployment/environments/kdg-local.json --run-id 99b7231c-0a5b-4bdb-98e8-3329564c526a --supabase "$KDG_SUPABASE"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$KDG_PY" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py platform/deployment/tests/test_migrate_adapter.py -q -p no:cacheprovider
"$KDG_PY" -B tools/py/run_compose_supabase.py --check-only
"$KDG_PY" -B tools/py/run_compose_supabase.py --identity-authority owned --no-seeds --check-only
```

Here `KDG_SUPABASE` is the retained pinned executable at
`platform/deployment/.local/kdg-toolchains/ad277eef-a10e-4aac-bb82-5743653fb2e0/payload/supabase/supabase`
(passed as an absolute path). The independent CLI script is retained as
`root-cli-check.py` in the final frame.

Results: fresh preparation PASS; **32 native groups PASS**; separate retained inspection
PASS with identical catalog/data snapshots and **76 executed sources** matching the
bootstrap before/after and both result inventories. Independent real isolated CLI lookup
matched the original saved entry receipt. Normal stop returned `completed`,
`runtime_ready=false`; data and Docker resources remain preserved. Affected regression:
**1236 passed in42.03s**. Both composition dry runs passed and changed no files.
Scoped tracked/untracked whitespace checks passed. All43 protected historical files,
all13 preexisting tracked concurrent files and frozen intent match their starting hashes.
Concurrent untracked Scribeswell planning updates were observed and left untouched,
outside the scoped commit. `root-verification.json` retains source/log hashes and the
preservation inventory. No broader runtime, hosted-CI or activation readiness is claimed.

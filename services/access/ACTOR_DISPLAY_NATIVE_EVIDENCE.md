# Identity retained actor native implementation — 2026-10-28

Status: implemented, synthetically qualified and **reviewed**. Final verification,
review fixes, custody and normal owned-resource stop evidence are recorded below.
This implements the existing [owner contract](HISTORICAL-ACTOR-DISPLAY.md)
and KDG ON-1–ON-5 prerequisite. Story 3.1 remains incomplete.

`identity_0028` extends the actual concurrent `identity_0027` predecessor through
the existing controlled Alembic lane. The established Identity migrator owns
`identity.actor_displays(uuid[])`: fixed search path, SECURITY DEFINER, selected
retained `actor.id/display_name` only, bounded nonnull unique nonzero UUID array.
It neither joins live accounts nor infers mappings. Persisted names remain capped
at200 characters; the existing wire validation remains unchanged.

The explicit `identity_actor_display_runtime` LOGIN has no memberships, elevated
role flags, schema/database CREATE, raw table/column/sequence authority or direct
operator/projection/trigger-helper authority. All inherited EXECUTE defaults on
the new function are stripped before granting its one runtime caller. Harmless
current-JWT context helpers retain their established behavior. Catalogue additions
observe the exact new projection and three implicated old trigger helpers; an
unrelated harmless public function does not require a new Identity reference.

The actual native pre-migration probe confirmed an inherited-authority defect:
PUBLIC EXECUTE on `identity.log_audit()` plus database TEMP allowed a restricted
login to attach it to its own temporary table and write a forged audit row.
Migration28 strips direct EXECUTE on the exact legacy SECURITY DEFINER trigger
helpers `log_audit`, `set_audit_fields` and `handle_new_user`. Existing installed
Auth/profile/audit triggers still execute; native proof checks their behavior.

`actor_display_native.py` supplies explicit private, fresh unpooled Psycopg
acquisition and returns only closed actor/name rows. Acquisition, read-only
transaction, bound UUID array, statement/lock waits and owned unwind share the
caller’s absolute deadline. Interruptions finish the local libpq transport before
cancelling the owned task, avoiding Psycopg’s independent cancellation/drain
budgets and diagnostic logging. No read task is detached and repeated caller
cancellation cannot publish rows. The unchanged isolated HTTP factory receives
this reader by injection; active `main.py`, packaging and production config are
outside this delivery.

## Actual native evidence

Proof root: `platform/deployment/.local/identity-actor-native/` with private frames
`f6d496e4-d1eb-4a83-8c67-6bcfb3545fa6-attempt2`, `-attempt3` and `-attempt4`.
The earlier sandbox startup failure was tool-observed at
`/tmp/identity-actor-native-20261028/`; that temporary capsule was unavailable after
resume. Persistent attempt2/3/4 frames remain; no cleanup was performed.
Only newly named `identity-actor-native-*` PostgreSQL17 containers were used. Inputs
contain generated synthetic credentials and loopback-only ports; no retained target
or real account/provider/key was used. Native scratch Auth SQL proves fixture
FK/trigger behavior only, not GoTrue or provider lifecycle.

Attempt2’s captured27 upgrade failed transactionally at20 because the initial
synthetic bootstrap used wrong standard role flags/membership and role creation
order. The latter changed ACL-array ordering. Source-bound historical fingerprints
were preserved. Diagnosis and explicit fixture-only reconciliation attempts were
retained; a corrected fresh attempt3 then passed captured27 upgrade and repeat.
Attempt4 reused that byte-captured27 runner and added synthetic retained data and
an actual previous `access_runtime` projection consumer before upgrading.

Attempt4 seed failures (foreign-key then duplicate checkpoint) are retained. The
fixture resumes only after exact seeded actor/name evidence matches; account
removal explicitly deletes its scratch profile before its Auth row, as required
by the existing non-cascading FK. It never deletes retained actor/mapping rows.
One earlier private failure frame contains a synthetic diagnostic traceback; a
local scan found no generated fixture-password match in either failure frame.
The final qualifier records only safe phase/type/SQLSTATE failure fields. Those
earlier outcomes were preserved, not rewritten as successful attempts.

| Case | Actual evidence and boundary |
| --- | --- |
| ON-1 | Actual runtime LOGIN first received42883 for the missing function where an empty selected-ID result was expected. GREEN returns exact retained, renamed, removed-account, System/Migrate/service names and leaves unknown/current-account-equality IDs absent. Registry identities/mappings remain retained. |
| ON-2 | Actual runtime accepts valid203-ID input; seven invalid array cases fail22023.21 actual raw table/write/DDL/ledger/SET-role/operator/foreign-owner/other-projection/unauthorized-login/trigger-attachment cases fail42501. Nine rollback-only authority cases now include an executable foreign-owner SECURITY DEFINER; verifier refusal and full rollback pass. |
| ON-3 | Final locked native read ends in0.231s under a0.25s deadline; cancelled blocked read ends in0.0004s. Actual locked HTTP returns private503 in2.903s under its original3s budget. Zero runtime sessions remain. Acquisition exhaustion, repeated cancellation, malformed rows, rollback failure and finish-failure privacy also have focused reader tests. |
| ON-4 | Exact source execution records28 reference rollback-only on independently verified27; captured27 repeat verifies rollback. Controlled postcondition failure returns nonzero and rolls back function/schema ACL/helper ACL/ledger. Captured27 still verifies. Explicit current28 retry and repeat pass with seeded data and previous consumer preserved. Affected release-tooling tests verify activation/dependency blocking on migration failure; no actual release activation or downgrade runs. |
| ON-5 | Actual native reader injected into existing isolated HTTP factory returns exact selected IDs/order, resolved versus unavailable shapes, existing service/org denials and validation bounds, private no-store and closed503 envelope. Exported OpenAPI and generated clients remain fresh. |

`acceptance-red-source-binding.json` and the exact qualifier bytes retain attempt3’s
initial RED. Attempt4 `invocation-*/execution.json` binds each subsequent phase to
argv and captured owner/reader/HTTP/qualifier sources. Captured27 has its complete
source hash manifest. `reference28-source-execution.json`, `failed28-rollback.json`,
`upgrade28.json`, `native-sql*.json`, `native-guards.json` and
`native-async-http*.json` contain actual results. Earlier emitted28 candidate
reference bytes are retained as superseded artifacts when the added observation
was narrowed; no historical reference was re-recorded.

## Exact commands and current checks

From repository root, installed `services/access/.venv/bin/python` is Python3.15.0
with Psycopg3.3.6, SQLAlchemy2.1.4, Alembic1.20.0, pytest9.1.1 and HTTPX0.28.1.
No dependency was installed. `FRAME` below denotes the private attempt4 path above;
`PREVIOUS` denotes attempt3.

```sh
services/access/.venv/bin/python -I -B services/access/tests/qualify_actor_display_native.py prepare27 --proof "$FRAME" --predecessor-frame "$PREVIOUS"
services/access/.venv/bin/python -I -B services/access/tests/qualify_actor_display_native.py seed --proof "$FRAME"
services/access/.venv/bin/python -I -B services/access/tests/qualify_actor_display_native.py red --proof "$FRAME"
services/access/.venv/bin/python -I -B services/access/tests/qualify_actor_display_native.py trigger_red --proof "$FRAME"
services/access/.venv/bin/python -I -B services/access/tests/qualify_actor_display_native.py reference28 --proof "$FRAME"
services/access/.venv/bin/python -I -B services/access/tests/qualify_actor_display_native.py upgrade28 --proof "$FRAME"
services/access/.venv/bin/python -I -B services/access/tests/qualify_actor_display_native.py native --proof "$FRAME"
services/access/.venv/bin/python -I -B -m pytest services/access/tests/test_actor_display_native.py -q -p no:cacheprovider
services/access/.venv/bin/python -I -B services/access/export_actor_display_openapi.py --check
```

Native phase outputs pass. Focused reader19 pass; an initial test-double destructor
warning was corrected. The coordinator independently passed all104 reader/HTTP
cases in6.21s, with logs/argv at
`platform/deployment/.local/identity-actor-display/f6d496e4-d1eb-4a83-8c67-6bcfb3545fa6/parent-reader-http.{json,log}`.
Candidate exporter check reports `actor_display_openapi_current`; the existing
retained generator with `--check` reports `api_client_current`.

A sandbox combined regression invocation was stopped normally with exit130 after
104 cases; a bounded affected-TestClient run then timed out. The escalated rerun
was interrupted while awaiting a tool result/approval; no rejection or passing
result was returned. The coordinator owns the bounded affected Identity/HTTP,
strict TypeScript, KDG aggregate and composition checks and their final results.
There is no repository-wide root verification command. This implementation record
does not promote an interrupted command to passing evidence.

## Remaining gates and impacts

All three review lenses completed across two independent reviewers. The runtime
thread cap prevented a third fresh reviewer; the blind reviewer completed that
lens before separately running verification-gap review without claims. This is
reviewer reuse, not three context-free reviewers. Four findings were patched:
task-local suppression of raw driver diagnostics, explicit restricted-login/target
configuration, actual predecessor source/ledger verification and the missing
foreign-owner definer guard case. Independent patch review found no remaining
supported findings. No finding was deferred.

Parent final verification: **126 focused reader/qualifier/HTTP tests** pass in5.18s;
**198 affected Identity/release tests** pass in3.76s with one existing Starlette
deprecation warning. Strict TS7, the109-case KDG aggregate adapter proof, composition
check-only, owner exporter and generated freshness pass. The generator first failed
inside the sandbox; its unchanged installed checker passed outside it. No installation
ran. Parent replayed the actual updated native matrix after the four patches;
all ON cases pass. The source-bound final native invocation is retained in attempt4.

Parent checks, review reports and custody are retained under
`platform/deployment/.local/identity-actor-display/f6d496e4-d1eb-4a83-8c67-6bcfb3545fa6/`.
`parent-reader-http.json` retains the initial104-test log; `parent-affected-checks.json`
records exact affected/type/adapter/composition commands and observed results.
The final126-test output was observed directly in tool chunk2dbf1f; no full saved
test log is claimed. Final native/guard JSONs retain nine actual unsafe cases.

Normal `docker stop --time 10` completed for this delivery's three containers only.
All three report exited/code0/no OOM; all three database volumes still exist.
No container/volume or prior resource was deleted. Among992 prior selected KDG/Access
sources, this delivery edited the five planned existing files; three generated KDG
database-tool files evolved concurrently and were preserved. Original handoff suffix
is intact. Three unrelated builder tracked diffs also evolved concurrently. This
delivery did not edit those six files or claim their changes as its own qualification.

The local delivery records the existing unchanged Identity27 database migration,
catalogue/reference and role preparation as the required predecessor, so28 has a
complete checked-in history. Concurrent People API/factory/export/deployment work
and other unrelated changes remain outside this commit.

Private synthetic libpq-finish failure injection establishes safe failure/no task
leak; it does not establish an actual libpq transport malfunction in production.

Next active-owner work must separately authorize/configure/mount/package the reader
and owner route, provision/rotate real service credentials, and qualify KDG’s running
owner path with coordinated migration/release compatibility. Real Auth/provider
invalidation, synchronized producer-to-portal journey, deployed own-PWA/cache
separation, actual zoom/assistive technology and installed Android/iPhone evidence
remain separate. This is no release or full Story3.1 completion claim.

Scaffold: existing controlled owner lane reused; no neutral pattern promoted from
this Identity-specific proof. Shared UI: unchanged. Agent context: existing rules
suffice. Documentation: owner contract/runbook, this evidence, KDG readiness/handoff.
ADR: implements0020/0022/0023/0031/0056 and focused migration verification; no accepted
decision changed. Concurrent27 and unrelated dirty work remain owned by their
existing delivery items; the coordinator verifies final custody separately.

# Current-membership legacy role lookup — bounded ID-B evidence

2026-10-20. Build: `_bmad-output/implementation-artifacts/spec-id-b-legacy-role-lookup.md`.
Baseline: `f52352fc31337f5f15b1f249775e2dcebaf134b7`.

Revision9 replaces only public.get_user_roles() through the existing Identity owner.
The existing no-argument RPC returns role:string rows only for the exact token subject,
organization and membership, all active, excluding deleted member-role rows. Actor or
person mapping is not required. JWT role arrays and app context never substitute for
the exact binding. This legacy compatibility read supplies no current Access authority.

## Requirement to executed proof

| Requirement | Owner proof |
| --- | --- |
| Characterize exact old helper first | Root characterize.py/characterization.json against unchanged head8 |
| Exact active binding, stale/foreign/inactive denial, unchanged wire shape | qualify_legacy_roles.py actual restricted-login read matrix |
| Typed errors, pool reuse, fixed search path, no data writes | Same qualifier, full Identity data hashes and transaction-local context |
| Clean/adopt/head8/repeat, original rows/ACL/history, atomic failure/drift | Existing actual Alembic route, prior19 exact Git files and SQL failure fixture |
| Trusted independent reference and historical custody | Existing rollback-only recorder extension; focused source mutation/publication tests |

Root proof: `platform/deployment/.local/identity-baseline/legacy-roles-9ihk9x80/`.
Eight fresh synthetic databases use ida_99b7231c0a5b_legacyroles1_ prefix on retained
native run99b7231c-0a5b-4bdb-98e8-3329564c526a. No prior database/data/resource removed.
2624 original nonignored source files are hashed before implementation; concurrent
brainstorming, Expense, Scribeswell and specification work remain protected.

Root snapshots19 exact owner Python/JSON files from the baseline Git commit. Unchanged
head8 executes on characterization/previous/failure/unknown before new migration proof.
Old helper returns42702 for own/foreign-member/foreign-org cases because its member_id
identifier is ambiguous; this observed failure is retained rather than an invented old
success/leak. The temporary authenticated SET-only edge restores exactly. Root supplies
only synthetic Auth/profile/org/member/role fixtures, no real user/provider operation.

New legacy-role-reference.json is produced through the existing rollback-only recorder,
SHA256182564ba568ea4a2c16285aa0bdcb37dac1fe0600165f8d2ac20bc94a4c10052.
Only its new pin is set afterward. Eight prior revisions/references/source pins stay
immutable. Functions are the only changed canonical catalog category; exact function
owner/ACL/signature/type stay. Original SQL and generated composed outputs are untouched.

The source baseline's historical PUBLIC EXECUTE is preserved, not treated as evidence
of a deployed target ACL. The separately documented production PUBLIC revocation remains
an unadopted target difference. Rollback-only ACL characterization proves replacement
preserves revoked PUBLIC too; it does not authorize adoption or normalize target grants.

## Commands and scope

```sh
OWNER_PYTHON=platform/deployment/.local/identity-baseline/actor-command-zxycfmc4/owner-env/venv/bin/python
IDENTITY_QUALIFICATION_DIR=platform/deployment/.local/identity-baseline/legacy-roles-9ihk9x80 "$OWNER_PYTHON" -I -B services/access/tests/qualify_identity_baseline.py --record-legacy-role-reference
IDENTITY_QUALIFICATION_DIR=platform/deployment/.local/identity-baseline/legacy-roles-9ihk9x80 "$OWNER_PYTHON" -I -B services/access/tests/qualify_legacy_roles.py
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$OWNER_PYTHON" -I -B -m pytest services/access/tests apps/pts/tests/test_release.py -q -p no:cacheprovider
"$OWNER_PYTHON" tools/py/run_compose_supabase.py --check-only
"$OWNER_PYTHON" tools/py/run_compose_supabase.py --identity-authority owned --check-only
```

Existing frozen owner Python3.15.0/SQLAlchemy2.1.4/Alembic1.20.0/Psycopg3.3.6/rfc87850.1.4/
pytest9.1.1 and approved TypeScript7.0.2 remain. No install/lock/dependency change.
CPU ATDD RED precedes implementation: missing revision9 and head constant (two failures).
Actual old8 RED42702 is recorded independently. Root executes all DB/Docker proof;
qualifier consumes prepared credentials and creates no infrastructure/login/credential.
Temporary SET-only fixture edges, owner mutations and failure injection are synthetic;
private durable recovery witnesses, bounded SQL and exact restoration preserve custody.
Database role execution is not provider/JWT/HTTP verification or a hosted CI result.

## Five impacts and remaining gates

Scaffold: existing owner migration/reference/qualifier extension; no new generator or
runtime pattern. Shared UI: none; Expense's existing RPC rows stay compatible. Agent
context: existing ownership/release/security rules suffice. Documentation: owner runbook,
Build, this evidence, KDG navigation and ownership inventory. ADR: existing decisions
apply unchanged; none edited or superseded.

Auth token-hook behavior and invalid/stale selected-organization policy remain unchanged.
Membership lifecycle/uniqueness/CASCADEs, account verification adapter, other protected
commands, Access/WRITE and server KDG remain gates. No full Identity/shared readiness,
real account/access/provider change, production migration, provisioning/deployment,
Leave/editor, reset/prune, real-data pilot or push is claimed.


## Initial actual acceptance

Complete first matrix PASS49.34s, source unchanged, actual-execution.json;17 acceptance
stages plus trusted-reference publication are in identity-qualification.json. Actual
restricted authenticated-role exact/foreign/inactive/missing/nil/malformed/overflow,
search-path spoof and pool recheckout/different-account cases pass. Full Identity data
hashes remain unchanged. Only functions differ from prior canonical head8. Clean/adopt/
exact head8/repeat, exact ACL preservation, revoked-PUBLIC rollback characterization,
real injected CREATE FUNCTION failure/atomic old-head retention, subsequent reconciliation,
profile ACL drift refusal and unknown history all pass. All temporary edges restore.
Both composition routes exit0. Executed source bytes are retained under initial-source.
Independent review and reviewed-source final verification follow.

Initial root affected suite503 PASS13.44s, no skips (affected-suite.log). Both composer
logs exit0. Existing regression expectations deliberately retain profile8 as a supported
historical head while only9 satisfies require_head. Three independent reviews follow.


## Review corrections and Auth helper parity

Three context-free layers complete: Blind9 findings, Edge0, Verification0. Eight local
verification/recorder corrections are selected; one low directory-durability extension
is rejected with evidence in the Build log. No production SQL change or new authority.

Read-only native inspection records auth-helper-definitions.json in the initial frame:
auth.uid() prioritizes request.jwt.claim.sub before plural JSON sub; auth.jwt() prioritizes
request.jwt.claim before request.jwt.claims. Initial scratch stubs implement plural JSON
only, so that initial passing matrix does not prove legacy-context behavior. Root's fresh
reviewed frame copies exactly these two inspected helper definitions to scratch DBs only,
checks byte-identical pg_get_functiondef output and records auth-helper-parity.json.
Native Auth functions remain untouched. The helper continues to consume the existing
vendor auth.uid()/auth.jwt() authority; no new raw-plural-only authentication protocol.
Conflicting account/member contexts must deny, coherent legacy context resolves its exact
member, and pool checks clear all request claim settings. These remain trusted database
assertions and synthetic tests, not independent validation of a browser JWT or provider.

Other corrections strengthen a distinct spoof sentinel, exact old42702 characterization,
multiple active roles, valid identities without role arrays, per-function comparison,
recorder SQL deadlines and signal/failed-cleanup regression proof. All eight historical
references and revision bytes remain immutable.


The first reviewed native-parity frame legacy-roles-reviewed-7qjkit8l fails7.244s with
source unchanged at blank JSON sub. Native auth.uid casts empty JSON sub to UUID and
returns22P02; the minimal original stub normalized it to null. Safe root diagnosis
confirms the blank field and SQLSTATE without payload/credentials. Characterization,
actual per-function comparison and native parity pass before this failure; temporary
edges restore exactly. The failed source and receipts remain under failed-source.
522 affected tests still pass31.57s; that pass does not replace failed actual acceptance.
A focused RED reproduces the missing guard, followed by a small CASE guard before
native UUID conversion and focused GREEN. Nonempty malformed subjects retain typed
errors. Only new uncommitted revision9/reference will be regenerated; eight historical
revisions/references remain immutable. Fresh complete acceptance is required afterward.


## Final reviewed-source acceptance

Final retained frame:
`platform/deployment/.local/identity-baseline/legacy-roles-final-x3t9_a5_/`.
The bounded owning recorder regenerates only the new9 reference after the empty-sub
fix: SHA256983d00ac73bfc9d86188ce166cece3c246926f169b9993af0141a527d8bbd0aa.
The earlier new artifact/source/failure are retained; no generated JSON is hand edited.
Eight prior references/revisions/source pins remain unchanged.

Complete native-parity actual matrix **PASS59.688s**, source_unchanged true;20 recorded
steps include independent reference publication, unchanged8 characterization and all
17 migration/read stages (actual-execution.json, actual-qualification.log,
identity-qualification.json). Source hashes also bind reused profile/target qualifier
helpers. Root verifies exact native Auth helper definitions in every fresh scratch case,
then tests missing/empty/nil/nonpositive identity, nonempty malformed/overflow errors,
conflicting/coherent legacy claim forms, complete active-role rows without role arrays,
currentness/deletion/foreign binding, pool cleanup and a rejected distinct spoof sentinel.
Actual function-row comparison proves only public.get_user_roles body/search_path differs;
all other functions, owner/ACL/signature, profile protections and histories remain.
Clean/adopt/exact old8/repeat, full old data/external refs, revoked-PUBLIC preservation,
real injected revision failure/rollback, reconciliation and drift/unknown refusal pass.
Every temporary global role edge/fixture object/ACL restores exactly.

Final affected suite **523 PASS37.65s, no skips** (affected-suite.log); both composer
routes exit0 and diff whitespace check passes. Eight review corrections and the actual
blank-sub RED/GREEN fix are verified. One low crash-durability extension is rejected;
no deferred or unresolved finding. Signal/cleanup-failure tests retain required receipts,
restore handlers and never claim restoration after failed cleanup. Earlier actual passes
remain tied to their exact source and do not erase the native-parity failure.

Normal retained-data stop, protected-file/concurrent-work audit, credential-output
check, final source manifest and scoped local commit receipt are retained in this frame.
No real account/provider/access/production use, reset/prune, deployment or push occurred.

Final preservation-audit.json checks2624 originals: none missing, seven intended existing
changes, concurrent brainstorming memlog/Scribeswell README retained and zero unexpected
changes. Actual executed source matches current files. safe-output-check.json verifies
credential URLs/tokens/password-bearing forms absent from selected outputs, excluding
short vendor-password coincidences in legitimate role names. native-stop.json completes
normally with runtime_ready false and retained data. All prior failed frames remain.
